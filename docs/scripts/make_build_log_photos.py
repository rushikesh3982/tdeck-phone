"""Prepare the build-log photos (docs/build-log.md) from the original phone photos.

For each photo listed in PHOTOS below, this:
- turns it the right way up (phones store the turn separately);
- hides private details: the modem's serial number, IMEI and QR code are pixelated;
- crops it if a crop is given, and shrinks it to 1400 px on its long side;
- adds the labels and arrows listed for it;
- saves it as a JPEG with no hidden data (no location, date or camera details).

Usage:
    python make_build_log_photos.py <folder with the original photos> <output folder>

Positions are in percent of the photo's width and height, the photo the right way up. To add a photo, add an entry
to PHOTOS and run the script again; photos already done are redrawn the same way.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter, ImageOps

LONG_SIDE = 1400

# (text, point the arrow touches, where the label sits); positions in percent. colour is optional.
PHOTOS = [
    dict(src="20261104_135447.jpg", out="01-modem-board-as-received.jpg", font=15,
         hide=[[(43.3, 30.0), (65.7, 30.0), (65.7, 55.4), (43.3, 55.4)]],
         labels=[
             ("C17: 100 µF 50 V,\n11 mm tall", (14.5, 64.5), (19.0, 86.5), "#c0392b"),
             ("C11: 330 µF 35 V,\n11 mm tall", (51.5, 66.5), (60.0, 91.0), "#c0392b"),
             ("Regulator (MIC29302).\nIts metal tab is GND", (17.0, 35.3), (19.0, 8.0), None),
             ("U.FL2: GPS socket", (33.5, 21.3), (45.0, 4.5), None),
             ("A7672S modem\n(serial and IMEI hidden)", (70.0, 30.0), (72.0, 12.5), None),
             ("U.FL1: 4G socket", (88.0, 43.2), (84.0, 24.5), None),
         ]),
    dict(src="20261104_141456.jpg", out="02-tall-capacitors-removed.jpg", font=24, crop=(8, 20, 92, 92),
         hide=[[(41.9, 40.5), (61.7, 40.5), (61.7, 60.3), (41.9, 60.3)]],
         labels=[
             ("C17's pads", (25.2, 65.4), (21.0, 80.0), "#c0392b"),
             ("C11's pads", (47.6, 67.5), (62.0, 84.0), "#c0392b"),
         ]),
    dict(src="20261104_142733.jpg", out="03-capacitors-laid-flat.jpg", font=24, crop=(5, 18, 98, 98),
         hide=[[(44.3, 36.6), (66.9, 36.6), (66.9, 63.4), (44.3, 63.4)]],
         labels=[
             ("100 µF", (22.5, 80.5), (16.0, 91.5), "#c0392b"),
             ("470 µF 16 V", (55.0, 77.5), (66.0, 91.5), "#c0392b"),
         ]),
    dict(src="20261104_142749.jpg", out="04-capacitors-side-view.jpg", font=16,
         hide=[],
         labels=[
             ("100 µF on C17's pads, past the\nboard's edge, seen end-on", (49.0, 23.5), (75.0, 18.0), "#c0392b"),
             ("470 µF on C11's pads, lying flat:\nabout 7 mm high (the old one stood 11 mm)", (49.5, 52.0),
              (74.0, 52.0), "#c0392b"),
             ("The board, seen edge-on", (44.5, 78.0), (72.0, 82.0), None),
         ]),
    dict(src="20261112_223257.jpg", out="05-bench-setup-component-side.jpg", font=14,
         hide=[[(57.2, 66.0), (68.0, 61.8), (70.8, 68.2), (60.0, 71.8)]],
         labels=[
             ("CP2102 USB-serial adapter:\nplugs into the Mac", (12.5, 31.5), (24.0, 14.0), "#1f4e8c"),
             ("4 data wires: TX, RX, 3.3 V, GND", (49.5, 23.8), (52.0, 9.0), "#1f4e8c"),
             ("Full-band LTE sticker antenna\n(came with the T-Deck), on U.FL1", (19.5, 67.0), (21.0, 87.0),
              "#8c564b"),
             ("GPS patch (KTRON), on U.FL2", (30.0, 89.5), (55.0, 96.0), "#8c564b"),
             ("Mic: yellow wire to M+,\ngreen wire to M−", (42.0, 54.5), (37.0, 44.0), "#7b4fb3"),
             ("KTRON modem board", (66.0, 74.0), (80.0, 87.0), "#2e7d32"),
             ("Earpiece wires (S+, S−). The two\n47 µF capacitors are under\nthe black heat-shrink", (76.0, 61.5),
              (82.0, 47.5), "#1f77b4"),
             ("Bench power wires\n(red +, black −)", (88.5, 36.0), (84.0, 26.0), "#c0392b"),
         ]),
    dict(src="20261112_223337.jpg", out="06-bench-setup-sim-side.jpg", font=14,
         hide=[],
         labels=[
             ("CP2102 USB-serial adapter", (35.0, 21.5), (21.0, 12.0), "#1f4e8c"),
             ("Sticker antenna, back\n(3M tape still covered)", (50.0, 30.0), (60.0, 9.5), "#8c564b"),
             ("GPS patch, back", (91.0, 26.5), (87.0, 37.5), "#8c564b"),
             ("Mic", (45.5, 52.1), (31.0, 49.0), "#7b4fb3"),
             ("Micro-SIM holder", (82.0, 60.0), (85.0, 48.0), "#2e7d32"),
             ("Hot glue: holds the 4 data\nwires at their solder joints", (74.0, 55.8), (56.0, 41.0), "#555555"),
             ("1 kΩ mic resistor: M− (its long,\nbent leg) to a ground point", (74.0, 65.1), (79.0, 79.5),
              "#7b4fb3"),
             ("Hot glue: mic and\nearpiece wires", (68.9, 69.3), (48.0, 76.5), "#555555"),
             ("Bench power wires (red +,\nblack −), soldered to\nVCC and GND", (13.0, 72.5), (21.0, 62.5), "#c0392b"),
             ("Earpiece wires, ending in plug\nsockets for the earpiece", (47.5, 92.0), (71.0, 93.0), "#1f77b4"),
         ]),
]


def hide(im, polys):
    """Pixelate and blur inside each polygon (percent coordinates), so the text can't be read back."""
    w, h = im.size
    for poly in polys:
        pts = [(x * w / 100, y * h / 100) for x, y in poly]
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        block = max(8, int(min(w, h) / 90))
        small = im.resize((max(1, w // block), max(1, h // block)), Image.BILINEAR)
        rough = small.resize(im.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(block * 0.8))
        im.paste(rough, (0, 0), mask)
    return im


def make(src_dir, out_dir, p):
    im = ImageOps.exif_transpose(Image.open(os.path.join(src_dir, p["src"]))).convert("RGB")
    im = hide(im, p["hide"])
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
