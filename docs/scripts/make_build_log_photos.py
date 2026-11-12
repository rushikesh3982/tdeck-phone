"""Prepare the build-log photos (docs/build-log.md) from the original phone photos.

For each photo listed in PHOTOS below, this:
- turns it the right way up (phones store the turn separately);
- lifts the parts off the background with macOS's own "lift subject" (lift_subject.swift, macOS 14 or later), trims
  away a hand where the photo needs it, and puts the parts on a white background with a soft shadow;
- hides private details: the modem's serial number, IMEI and QR code are pixelated. Its make and model
  (SIMCom A7672S) and part number stay readable;
- crops it if a crop is given, and shrinks it to 1400 px on its long side;
- adds the labels and arrows listed for it;
- saves it as a JPEG with no hidden data (no location, date or camera details).

Usage:
    python make_build_log_photos.py <folder with the original photos> <output folder>

Positions are in percent of the photo's width and height, the photo the right way up. Circles are (x, y, radius),
the radius in percent of the width. To add a photo, add an entry to PHOTOS and run the script again.
"""
import os
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
LONG_SIDE = 1400
LIFT_SIZE = 2000                       # the size the subject is found at; the mask is then scaled up
MASK_EDGE = (120, 235)                 # mask values below the first count as background, above the second as
                                       # subject: trims the fringe of background the lifted edges carry
BACKGROUND = (255, 255, 255)
MODEM = "#2e7d32"

# Each label: (text, point the arrow touches, where the label sits, colour or None).
PHOTOS = [
    dict(src="20261104_135447.jpg", out="01-modem-board-as-received.jpg", font=15,
         # the board only: its outline (rounded corners), less the hand seen through its four mounting holes
         keep=[[(12.2, 14.8), (92.2, 18.9), (97.2, 77.6), (3.8, 78.0)]], keep_round=4.0,
         holes=[(15.8, 17.6, 2.1), (88.0, 21.0, 2.1), (8.3, 73.9, 2.1), (92.8, 74.8, 2.1)],
         hide=[[(57.6, 30.8), (63.6, 30.8), (63.6, 55.2), (57.6, 55.2)],          # serial number and IMEI lines
               [(43.5, 43.3), (57.0, 43.3), (57.0, 54.3), (43.5, 54.3)]],         # QR code
         labels=[
             ("C17: 100 µF 50 V,\n11 mm tall", (14.5, 64.5), (19.0, 88.0), "#c0392b"),
             ("C11: 330 µF 35 V,\n11 mm tall", (51.5, 66.5), (60.0, 92.0), "#c0392b"),
             ("Regulator (MIC29302).\nIts metal tab is GND", (17.0, 35.3), (19.0, 7.0), None),
             ("U.FL2: GPS socket", (33.5, 21.3), (42.0, 4.0), None),
             ("SIMCom A7672S: the 4G modem chip\n(serial number, IMEI and QR code hidden)", (70.0, 30.0),
              (70.0, 11.0), MODEM),
             ("U.FL1: 4G socket", (88.0, 43.2), (88.0, 25.5), None),
         ]),
    dict(src="20261104_141456.jpg", out="02-tall-capacitors-removed.jpg", font=24, crop=(8, 18, 92, 90),
         hide=[[(53.2, 41.3), (58.0, 41.3), (58.0, 59.6), (53.2, 59.6)],
               [(42.7, 51.4), (52.9, 51.4), (52.9, 59.4), (42.7, 59.4)]],
         labels=[
             ("A7672S modem\n(IMEI hidden)", (50.0, 39.5), (50.0, 23.0), MODEM),
             ("C17's pads", (25.2, 65.4), (21.0, 80.0), "#c0392b"),
             ("C11's pads", (47.6, 67.5), (62.0, 84.0), "#c0392b"),
         ]),
    dict(src="20261104_142733.jpg", out="03-capacitors-laid-flat.jpg", font=24, crop=(5, 11, 98, 98),
         hide=[[(59.0, 38.4), (64.8, 38.4), (64.8, 62.2), (59.0, 62.2)],
               [(45.4, 51.3), (58.3, 51.3), (58.3, 61.4), (45.4, 61.4)]],
         labels=[
             ("A7672S modem\n(IMEI hidden)", (56.0, 36.0), (56.0, 15.5), MODEM),
             ("100 µF", (22.5, 80.5), (16.0, 91.5), "#c0392b"),
             ("470 µF 16 V", (55.0, 77.5), (66.0, 91.5), "#c0392b"),
         ]),
    dict(src="20261104_142749.jpg", out="04-capacitors-side-view.jpg", font=16, crop=(28, 6, 92, 96),
         # the board's edge and the parts on it, without the fingers holding it
         keep=[[(43.5, 11.0), (45.4, 11.0), (45.4, 21.0), (43.5, 21.0)],          # the board, edge-on, between
               [(43.0, 21.0), (45.5, 21.0), (45.5, 91.8), (43.0, 91.8)],          # the fingers, then below them
               [(45.4, 24.5), (49.2, 24.5), (49.2, 32.3), (45.4, 32.3)],          # the 100 µF's body and legs
               [(44.8, 42.8), (52.2, 42.8), (52.2, 61.6), (44.8, 61.6)],          # the 470 µF
               [(45.4, 32.0), (46.4, 32.0), (46.4, 88.0), (45.4, 88.0)]],         # small parts along the edge
         keep_circles=[(48.3, 22.95, 2.75)],                                       # the 100 µF, end-on
         hide=[],
         labels=[
             ("100 µF on C17's pads, past the\nboard's edge, seen end-on", (49.0, 23.5), (72.0, 16.0), "#c0392b"),
             ("470 µF on C11's pads, lying flat:\nabout 7 mm high (the old one\nstood 11 mm)", (51.0, 52.0),
              (72.0, 52.0), "#c0392b"),
             ("The board, seen edge-on", (44.0, 78.0), (70.0, 84.0), None),
         ]),
    dict(src="20261112_223257.jpg", out="05-bench-setup-component-side.jpg", font=14,
         extra_lift=[(60, 8, 100, 66), (18, 70, 66, 99), (40, 60, 70, 90)],      # power wires, GPS patch, cable
         # a strip of wood the lifting kept under the antenna's cable
         remove=[[(29.0, 49.95), (30.0, 49.75), (33.0, 49.45), (36.0, 49.35), (39.0, 49.55), (42.0, 50.05),
                  (42.5, 50.25), (42.5, 50.9), (29.0, 50.9)]],
         # the antenna's white cable, traced from the photo, which the lifting only half kept
         add_lines=[([(28.7, 51.05), (29.4, 50.46), (30.0, 50.18), (30.6, 49.92), (31.2, 49.72), (31.8, 49.54),
                      (32.4, 49.41), (33.0, 49.29), (34.2, 49.14), (35.4, 49.06), (36.6, 49.06), (37.8, 49.11),
                      (39.0, 49.22), (40.2, 49.40), (41.4, 49.61), (42.6, 49.90), (43.8, 50.24), (45.0, 50.69),
                      (46.2, 51.24), (47.4, 51.91), (48.6, 52.71), (49.8, 53.68), (51.0, 54.76), (52.2, 55.94),
                      (53.4, 57.15), (54.6, 58.30), (55.8, 59.40), (57.0, 60.60), (57.6, 61.30)], 0.36)],
         # everything on the label below the part number: serial number, IMEI and QR code
         hide=[[(60.00, 67.93), (66.44, 64.42), (69.61, 67.42), (63.22, 70.67), (59.78, 68.33)]],
         labels=[
             ("CP2102 USB-serial adapter:\nplugs into the Mac", (12.5, 31.5), (24.0, 14.0), "#1f4e8c"),
             ("4 data wires: TX, RX, 3.3 V, GND", (49.5, 23.8), (52.0, 9.0), "#1f4e8c"),
             ("Full-band LTE\nsticker antenna (came\nwith the T-Deck), on U.FL1", (25.0, 58.0), (16.5, 46.0),
              "#8c564b"),
             ("GPS patch (KTRON), on U.FL2", (30.0, 89.5), (55.0, 96.0), "#8c564b"),
             ("Mic: yellow wire to M+,\ngreen wire to M−", (42.0, 54.5), (41.0, 42.0), "#7b4fb3"),
             ("SIMCom A7672S modem chip\n(serial number, IMEI and QR hidden)", (63.0, 66.0), (52.0, 77.5),
              MODEM),
             ("KTRON modem board", (72.0, 74.5), (84.0, 86.0), MODEM),
             ("Earpiece wires (S+, S−). The two\n47 µF capacitors are under\nthe black heat-shrink", (76.0, 61.5),
              (82.0, 47.5), "#1f77b4"),
             ("Bench power wires\n(red +, black −)", (88.5, 36.0), (84.0, 26.0), "#c0392b"),
         ]),
    dict(src="20261112_223337.jpg", out="06-bench-setup-sim-side.jpg", font=14,
         extra_lift=[(72, 18, 100, 62), (76, 25, 92, 58), (0, 78, 40, 92), (60, 55, 80, 80)],
         # the antenna's white cable and the earpiece's white wire, traced from the photo
         add_lines=[([(35.6, 43.2), (34.42, 43.8), (34.3, 44.4), (34.27, 45.0), (34.25, 45.6), (34.32, 46.2),
                      (34.43, 46.8), (34.85, 48.0), (35.15, 48.6), (35.5, 49.2), (35.9, 49.8), (36.37, 50.4),
                      (36.87, 51.0), (37.4, 51.6), (38.02, 52.2), (38.67, 52.8), (39.6, 53.56), (40.8, 54.42),
                      (42.0, 55.16), (43.2, 55.79), (44.4, 56.3), (45.0, 56.51), (46.8, 57.06), (48.0, 57.35),
                      (49.8, 57.69), (51.6, 57.98), (53.4, 58.21), (55.2, 58.48), (57.0, 58.78), (58.8, 59.11),
                      (60.6, 59.48), (61.8, 59.76)], 0.34),
                    ([(71.86, 75.0), (71.5, 76.8), (71.5, 78.0), (71.42, 79.2), (71.23, 80.4), (70.92, 81.6),
                      (70.55, 82.8), (69.8, 84.64), (69.2, 85.64), (68.6, 86.44), (68.0, 87.25), (66.8, 88.49),
                      (65.6, 89.14), (64.4, 89.85), (63.2, 90.29), (62.0, 90.54), (60.8, 90.72), (59.6, 90.7),
                      (58.4, 91.26), (57.2, 91.35), (56.0, 91.4), (54.8, 91.48), (53.6, 91.55), (52.4, 91.7),
                      (51.2, 91.85), (50.0, 91.94), (48.8, 92.0)], 0.42)],
         hide=[],
         labels=[
             ("CP2102 USB-serial adapter", (35.0, 21.5), (21.0, 12.0), "#1f4e8c"),
             ("Sticker antenna, back\n(3M tape still covered)", (50.0, 30.0), (60.0, 9.5), "#8c564b"),
             ("GPS patch, back", (91.0, 26.5), (87.0, 37.5), "#8c564b"),
             ("Mic", (45.5, 52.1), (31.0, 49.0), "#7b4fb3"),
             ("Micro-SIM holder", (82.0, 60.0), (85.0, 48.0), MODEM),
             ("Hot glue: holds the 4 data\nwires at their solder joints", (74.0, 55.8), (56.0, 41.0), "#555555"),
             ("1 kΩ mic resistor: M− (its long,\nbent leg) to a ground point", (74.0, 65.1), (79.0, 79.5),
              "#7b4fb3"),
             ("Hot glue: mic and\nearpiece wires", (68.9, 69.3), (48.0, 76.5), "#555555"),
             ("Bench power wires (red +,\nblack −), soldered to\nVCC and GND", (13.0, 72.5), (21.0, 62.5),
              "#c0392b"),
             ("Earpiece wires, ending in plug\nsockets for the earpiece", (47.5, 92.0), (71.0, 93.0), "#1f77b4"),
         ]),
]


def lift(im, box=(0, 0, 100, 100)):
    """Mask (L, the photo's size) of the subject inside box, found by macOS's Vision framework."""
    w, h = im.size
    x0, y0, x1, y1 = (int(box[0] * w / 100), int(box[1] * h / 100), int(box[2] * w / 100), int(box[3] * h / 100))
    part = im.crop((x0, y0, x1, y1))
    part.thumbnail((LIFT_SIZE, LIFT_SIZE))
    with tempfile.TemporaryDirectory() as tmp:
        src, out = os.path.join(tmp, "in.png"), os.path.join(tmp, "mask.png")
        part.save(src)
        run = subprocess.run(["swift", os.path.join(HERE, "lift_subject.swift"), src, out], capture_output=True)
        full = Image.new("L", im.size, 0)
        if run.returncode == 2:                    # nothing found in this part of the photo
            return full
        run.check_returncode()
        m = Image.open(out).convert("L").resize((x1 - x0, y1 - y0), Image.BILINEAR)
    full.paste(m, (x0, y0))
    return full


def shape_mask(size, polys, circles, round_pct=0.0):
    """Mask of polygons (corners rounded by round_pct of the width) and circles, in percent coordinates."""
    w, h = size
    mask = Image.new("L", size, 0)
    dr = ImageDraw.Draw(mask)
    r = round_pct * w / 100
    for poly in polys:
        pts = [(x * w / 100, y * h / 100) for x, y in poly]
        if r > 0:
            pts = list(Polygon(pts).buffer(-r).buffer(r, quad_segs=16).exterior.coords)
        dr.polygon(pts, fill=255)
    for x, y, rr in circles:
        cx, cy, rad = x * w / 100, y * h / 100, rr * w / 100
        dr.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=255)
    return mask


def hide(im, polys):
    """Pixelate and blur inside each polygon (percent coordinates), so the text can't be read back."""
    w, h = im.size
    for poly in polys:
        mask = shape_mask(im.size, [poly], [])
        block = max(8, int(min(w, h) / 90))
        small = im.resize((max(1, w // block), max(1, h // block)), Image.BILINEAR)
        rough = small.resize(im.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(block * 0.8))
        im.paste(rough, (0, 0), mask)
    return im


def on_white(im, mask):
    """The subject on a white background, with a soft shadow down and to the right."""
    w, h = im.size
    blur = max(4, int(min(w, h) / 120))
    shadow = mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * 0.28))
    shifted = Image.new("L", im.size, 0)
    shifted.paste(shadow, (blur // 2, blur))
    out = Image.new("RGB", im.size, BACKGROUND)
    out.paste(Image.new("RGB", im.size, (60, 60, 60)), (0, 0), shifted)
    out.paste(im, (0, 0), mask)
    return out


def make(src_dir, out_dir, p):
    im = ImageOps.exif_transpose(Image.open(os.path.join(src_dir, p["src"]))).convert("RGB")
    mask = lift(im)
    for box in p.get("extra_lift", []):
        mask = ImageChops.lighter(mask, lift(im, box))
    if "keep" in p:
        keep = shape_mask(im.size, p["keep"], p.get("keep_circles", []), p.get("keep_round", 0.0))
        mask = ImageChops.darker(mask, keep)
    if "holes" in p or "remove" in p:
        mask = ImageChops.subtract(mask, shape_mask(im.size, p.get("remove", []), p.get("holes", [])))
    lo, hi = MASK_EDGE
    mask = mask.point(lambda v: max(0, min(255, (v - lo) * 255 // (hi - lo))))
    if "add_lines" in p:                       # thin parts traced by hand: lines (percent), width in % of height
        dr = ImageDraw.Draw(mask)
        w, h = mask.size
        for pts, width in p["add_lines"]:
            dr.line([(x * w / 100, y * h / 100) for x, y in pts], fill=255, width=round(width * h / 100),
                    joint="curve")
    im = on_white(hide(im, p["hide"]), mask)

    x0, y0, x1, y1 = p.get("crop", (0, 0, 100, 100))
    W, H = im.size
    im = im.crop((int(x0 * W / 100), int(y0 * H / 100), int(x1 * W / 100), int(y1 * H / 100)))
    im.thumbnail((LONG_SIDE, LONG_SIDE), Image.LANCZOS)
    w, h = im.size

    def fit(pt):                       # percent of the whole photo -> percent of the cropped one
        return ((pt[0] - x0) * 100 / (x1 - x0), (pt[1] - y0) * 100 / (y1 - y0))

    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.imshow(im, extent=(0, 100, 100, 0), aspect="auto")
    ax.set_xlim(0, 100); ax.set_ylim(100, 0)
    for text, pt, at, col in p["labels"]:
        pt, at, col = fit(pt), fit(at), col or "#222222"
        ax.annotate(text, xy=pt, xytext=at, ha="center", va="center", fontsize=p["font"], color=col,
                    weight="bold",
                    bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=col, lw=1.6, alpha=0.93),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2.2, shrinkA=2, shrinkB=1,
                                    mutation_scale=18))
        ax.plot(*pt, "o", ms=6, mfc=col, mec="white", mew=1.2)
    fig.savefig(os.path.join(out_dir, p["out"]), dpi=100, pil_kwargs={"quality": 82, "optimize": True})
    plt.close(fig)


if __name__ == "__main__":
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for p in PHOTOS:
        make(src_dir, out_dir, p)
        print("made", p["out"])
