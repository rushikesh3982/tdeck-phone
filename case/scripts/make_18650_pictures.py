"""Pictures of the 18650 version (case/18650/images/, shown in docs/design-18650.md), drawn from the case files.

Usage:
    python make_18650_pictures.py <back.stl> <front.stl> <old back.stl> <old front.stl> <output folder>

All four files at 100 %: the 18650 back and front (case/scripts/make_back_18650.py and make_front_18650.py), and the
current back and front (make_back.py, make_front.py) for the side-by-side comparison. Needs numpy, trimesh, shapely,
manifold3d, matplotlib, and the case scripts (for sizes and the shading renderer).
"""
import os
import sys

import numpy as np
import trimesh
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon as MPoly, Rectangle  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_back_18650 as B  # noqa: E402
import make_front_18650 as FF  # noqa: E402
import make_earpiece_holder as H  # noqa: E402
import make_earpiece_holder_18650 as L  # noqa: E402
from make_diagrams import render, show, COL, NAVY  # noqa: E402

TO_FRONT = np.array([[-1, 0, 0, -10], [0, 1, 0, 0], [0, 0, -1, 0.8], [0, 0, 0, 1]], float)       # 18650 back
OLD_TO_FRONT = np.array([[-1, 0, 0, -10], [0, 1, 0, 0], [0, 0, -1, -4.7], [0, 0, 0, 1]], float)  # current back
ANTENNA = 18.5                    # the GPS antenna's board, assumed square (see design-18650.md)
GOLD = "#c9a227"                  # the battery contacts


def placed(mesh, m):
    out = mesh.copy()
    out.apply_transform(m)
    return out


def lab(ax, x, y, text, tx, ty, col=NAVY, size=9):
    ax.annotate(text, (x, y), (tx, ty), fontsize=size, color=col, weight="bold", ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=col, lw=1.0),
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=col, lw=1.0))


def ray_shade(mesh, xs, ys_or_zs, along, start, d, k=0.2):
    """Depth-shaded picture of a surface seen along one axis (rays), so shallow cuts show."""
    A, Bm = np.meshgrid(xs, ys_or_zs)
    o = np.zeros((A.size, 3))
    i, j = [n for n in range(3) if n != along]
    o[:, i], o[:, j], o[:, along] = A.ravel(), Bm.ravel(), start
    dirn = np.zeros(3); dirn[along] = d
    loc, ir, _ = mesh.ray.intersects_location(o, np.tile(dirn, (A.size, 1)), multiple_hits=False)
    D = np.full(A.size, np.nan)
    D[ir] = (loc[:, along] - start) * d
    D = D.reshape(A.shape)
    near = np.nanpercentile(D, 40)
    img = np.clip(0.86 - (D - near) * k, 0.1, 0.92)
    img[np.isnan(D)] = 1.0
    return img


def inside_layout(back, path):
    img, ext, _, _ = render(back, (0, 0, -1), (0, 1, 0), res=0.12)
    fig = plt.figure(figsize=(10, 11.5), dpi=110)
    ax = fig.add_axes([0.06, 0.02, 0.88, 0.9]); show(ax, img, ext)
    X0, Y0 = B.X0, B.Y0
    free = "#e8c547"
    ax.add_patch(MPoly([(8.0, 6.3), (68.2, 6.3), (68.2, 52.6), (57.6, 52.6), (57.6, 16.9), (8.0, 16.9)], closed=True,
                       fc=free, alpha=0.45, ec="#b8941a", lw=1.5))
    ax.add_patch(Rectangle((X0 - B.BOARD_H, Y0 - B.BOARD_W), B.BOARD_H, B.BOARD_W, fill=False, ec=COL["board"], lw=2.2,
                           ls="--"))
    ax.add_patch(Rectangle((34 - B.CELL_L / 2, B.CELL_Y - B.CELL_D / 2), B.CELL_L, B.CELL_D, fc=COL["battery"],
                           alpha=0.25, ec=COL["battery"], lw=2, ls="--"))
    sy0 = B.CELL_Y - B.CELL_D / 2 - B.SUPPORT_GAP - B.SUPPORT_T
    yp = B.CELL_Y + B.CONTACT_DY
    ax.add_patch(Rectangle((34 - B.BOARD_L / 2, sy0 - 2.0), B.BOARD_L, 2.0, fc=COL["cable"], alpha=0.6,
                           ec=COL["cable"], lw=1.5))
    for xb, xw in ((34 - B.BOARD_L / 2, -1.9), (34 + B.BOARD_L / 2, 69.9)):
        ax.plot([xb, xw, xw], [sy0 - 0.1, sy0 - 0.1, yp - B.CONTACT_W / 2 + 2.0], color="#5d6d7e", lw=2.2)
    for x0 in (-2.0, 66.6):
        ax.add_patch(Rectangle((x0, yp - 3.5), 3.4, 7.0, fc=GOLD, alpha=0.8, ec="#8a6d10", lw=1.2))
    gx0, gx1 = B.TOPGPS_X
    ax.add_patch(Rectangle((34 - ANTENNA / 2, 100.0), ANTENNA, 6.0, fc=COL["patch"], alpha=0.55, ec=COL["patch"], lw=2))
    yc, _ = B.SWITCH_AT
    face = B.SWITCH_PAD_X[0]                                           # the switch: plate, body and pins
    ax.add_patch(Rectangle((face - 8.5, yc - 5.75), 8.5, 11.5, fc="#c0392b", alpha=0.3, ec="#c0392b", lw=2, ls="--"))
    lx, ly = B.board_to_back(*B.NETLIGHT_UV)
    lab(ax, 34, B.CELL_Y, "18650 cell (LG MJ1)\nin a channel in the grip", 34, B.CELL_Y, COL["battery"])
    lab(ax, 0.0, yp + 2, "\u2212 contact\n(\u2212 engraved on the floor)", 10, 104, "#8a6d10", 8)
    lab(ax, 68.3, yp + 2, "+ contact\n(+ engraved on the floor)", 58, 104, "#8a6d10", 8)
    lab(ax, 34, 103, "GPS antenna, standing on its edge\nin the top slot (over the earpiece)", 34, 113, COL["patch"])
    lab(ax, 26, sy0 - 1.0, "protection board, glued to the wall along the cell", 30, 66.5, COL["cable"], 8.5)
    lab(ax, -1.9, 81.0, "its nickel strips run to\nbehind the contacts", 14, 59, "#5d6d7e", 8)
    lab(ax, 22, 44, "modem board\non four 8 mm standoffs", 22, 44, COL["board"])
    lab(ax, (lx + B.LED_HOLE_X) / 2, ly, "network-light\ntube", 44, 58)
    lab(ax, 65.2, yc, "modem switch\n(back's right wall)", 52, 84, "#c0392b", 8.5)
    lab(ax, 38, 11.6, "free floor for the 4G antenna: 10.7 mm wide, along the bottom and up the right side", 34,
        11.6, "#8a6d10", 8)
    ax.set_ylim(-3, 117)
    ax.set_title("18650 back, inside, looking in from the T-Deck's side (the phone's left side is on the left)\n"
                 "where each part that goes into the back sits", fontsize=10)
    fig.savefig(path); plt.close(fig)


def MPolyArea(ring):
    xy = np.asarray(ring.coords)
    return 0.5 * np.sum(xy[:-1, 0] * xy[1:, 1] - xy[1:, 0] * xy[:-1, 1])


def front_inside(front, path):
    """The 18650 front from inside, looking in from the back (so the phone's left is on the right), with every part
    that goes into it drawn as a block, and the back's parts that reach into it dashed."""
    img, ext, _, _ = render(front, (0, 0, -1), (0, 1, 0), res=0.12)
    fig = plt.figure(figsize=(11, 12.5), dpi=110)
    ax = fig.add_axes([0.03, 0.02, 0.94, 0.9]); show(ax, img, ext)
    xf = lambda xb: -xb - 10.0                         # back x -> front x
    yp = B.CELL_Y + B.CONTACT_DY
    blk = lambda x0, y0, w, h, fc, a=0.85, **k: ax.add_patch(Rectangle((x0, y0), w, h, fc=fc, alpha=a, ec="k", lw=0.8, **k))
    dash = lambda x0, y0, w, h, ec: ax.add_patch(Rectangle((x0, y0), w, h, fill=False, ec=ec, lw=1.8, ls="--"))
    tdeck, spk, ear, gps, small, metal = "#9cc3e6", "#4d5656", "#c0392b", "#7b4fb3", "#e67e22", "#b7950b"
    # the T-Deck: in first, screen down, filling the opening (its outline is the front's inside, cut through its middle)
    to2d = np.eye(4); to2d[2, 3] = 12.5                     # below the earpiece pocket's floor
    p2, _ = front.section(plane_origin=[0, 0, -12.5], plane_normal=[0, 0, 1]).to_planar(to_2D=to2d, check=False)
    hole = max((h for poly in p2.polygons_full for h in poly.interiors), key=lambda h: abs(MPolyArea(h)))
    ax.add_patch(MPoly(np.asarray(hole.coords), closed=True, fc=tdeck, alpha=0.35, ec="#1f4e79", lw=1.2))
    ax.text(-44, 52, "T-Deck\n(goes in first, screen down;\nwe see its back)", ha="center", va="center", fontsize=12,
            color="#1f4e79", weight="bold")
    # parts that sit on it or in the front's walls
    blk(-79.0, 15.75, 10.0, 20.0, spk)                                     # T-Deck's speaker, on the T-Deck's back
    blk(-80.6, 43.7, 3.0, 8.0, small)                                      # Alley Cat's switch slider
    blk(-9.4, 65.5, 3.0, 6.0, small)                                       # Alley Cat's reset button
    blk(-50.0, 100.6, 12.0, 6.0, ear)                                      # earpiece (under the holder and antenna)
    blk(-44.0 - 9.25, 101.0, 18.5, 5.0, gps, a=0.55)                       # GPS antenna, standing on the holder
    blk(-29.0 - 3.15, -0.8, 6.3, 2.7, ear)                                 # mic, in its pocket in the bottom wall
    blk(-18.95 - 4.2, 96.0, 8.4, 11.0, metal, a=0.7)                       # LoRa SMA socket
    ax.add_patch(Rectangle((-69.05 - 4.2, 96.0), 8.4, 11.0, fc=metal, alpha=0.3, ec="k", lw=0.8, ls="--"))
    for x in (xf(19.5), xf(48.5)):
        ax.add_patch(Circle((x, 102.9), 2.3, fc=metal, ec="k", lw=0.8))   # case-screw inserts
    # parts of the back that reach into the front (dashed)
    for xb0 in (-2.0, 66.6):
        dash(xf(xb0 + 3.4), yp - 3.5, 3.4, 7.0, "#8a6d10")                 # battery contacts' tops
    yc = B.SWITCH_AT[0]
    dash(xf(B.SWITCH_PAD_X[0]), yc - B.SWITCH_PLATE[0] / 2, 0.5, B.SWITCH_PLATE[0], "#c0392b")   # modem switch plate
    # labels: phone's right side (left of the picture)
    L = lambda x, y, t, tx, ty, c, sz=8.5: lab(ax, x, y, t, tx, ty, c, sz)
    L(-74, 25.75, "T-Deck's speaker: moved onto the\nT-Deck's back here, facing the grille", -100, 22, spk)
    L(-79.1, 47.7, "switch slider (Alley Cat's)", -100, 40, small)
    L(xf(B.SWITCH_PAD_X[0]) + 0.25, 60.0, "modem switch's plate\n(on the back's wall; dashed)", -100, 57, "#c0392b")
    L(-79.0, 81.0, "microSD slot", -100, 73, NAVY)
    L(xf(68.3), yp, "+ contact's top\n(from the back; dashed)", -100, 88, "#8a6d10")
    L(-69.05, 101.5, "4G antenna socket\n(only with an SMA antenna)", -98, 108, metal)
    # labels: phone's left side (right of the picture)
    L(-7.9, 68.5, "reset button (Alley Cat's)", 13, 62, small)
    L(-10.4, 61.5, "bump that holds the T-Deck\n(Alley Cat's, kept)", 13, 49, NAVY, 8)
    L(-7.5, FF.SIM_Y, "SIM slit (the card goes\ninto the modem board)", 13, 30, "#c0392b")
    L(xf(-0.3), yp, "\u2212 contact's top\n(from the back; dashed)", 13, 88, "#8a6d10")
    L(-18.95, 101.5, "LoRa antenna socket", 13, 108, metal)
    # top and bottom
    L(-44.0, 103.5, "earpiece, low holder and GPS antenna,\nstacked in the top pocket", -44, 118, gps, 9)
    ax.annotate("", (xf(48.5), 102.9), (-44, 91), arrowprops=dict(arrowstyle="-", color=metal, lw=1.0))
    L(xf(19.5), 102.9, "case-screw inserts", -44, 91, metal)
    L(-29.0, 0.5, "mic, in its pocket in the bottom wall", -18, -9, ear, 9)
    ax.text(xf(-4) + 1.5, 52, "phone's LEFT side", rotation=90, fontsize=10, weight="bold", color="#555", va="center")
    ax.text(xf(72) - 3.2, 52, "phone's RIGHT side", rotation=90, fontsize=10, weight="bold", color="#555", va="center")
    ax.set_xlim(-114, 28); ax.set_ylim(-14, 124)
    ax.set_title("18650 front, inside, looking in from the back (so the phone's left side is on the right here)\n"
                 "solid blocks: parts that go into the front; dashed: parts of the back that reach into it",
                 fontsize=10)
    fig.savefig(path); plt.close(fig)


def outside_angled(back, path):
    f = np.array([0.45, 0.55, 0.70]); f /= np.linalg.norm(f)
    up = np.array([0, 1, 0.0]); up -= (up @ f) * f; up /= np.linalg.norm(up)
    img, ext, _, _ = render(back, f, up, res=0.08)
    fig = plt.figure(figsize=(9, 9), dpi=110)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.92]); show(ax, img, ext)
    ax.set_title("18650 back, outside: the grip across the top holds the cell", fontsize=11)
    fig.savefig(path); plt.close(fig)


def side_by_side(new_phone, old_phone, path):
    fig, axs = plt.subplots(2, 1, figsize=(11, 8.5), dpi=110)
    for ax, ph, name in ((axs[0], old_phone, "today: X back over the 5000 mAh flat cell"),
                         (axs[1], new_phone, "18650 version: slim back with the grip")):
        img, ext, _, _ = render(ph, (-1, 0, 0), (0, 0, 1), res=0.1)
        show(ax, img, ext)
        ax.set_xlim(-4, 110); ax.set_ylim(-17, 24)
        thick = ph.bounds[1][2] - ph.bounds[0][2]
        ax.set_title(f"{name}: {thick:.1f} mm at the thickest point", fontsize=10)
    fig.suptitle("Side view at the same scale (screen side down, the phone's top on the right)", fontsize=11)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def side_walls(front, path):
    ys = np.arange(0, 108.01, 0.15); zs = np.arange(-14.6, 7.3, 0.15)
    Lw = ray_shade(front, ys, zs, 0, 10.0, -1.0)[:, ::-1]
    Rw = ray_shade(front, ys, zs, 0, -100.0, 1.0)
    fig, axs = plt.subplots(2, 1, figsize=(13, 7.2), dpi=110)
    h = zs[-1] - zs[0]
    zy = lambda z: zs[-1] - z
    for ax, img, t in ((axs[0], Lw, "LEFT side, from outside (screen side up; the phone's top on the left)"),
                       (axs[1], Rw, "RIGHT side, from outside (screen side up; the phone's top on the right)")):
        ax.imshow(img, cmap="gray", vmin=0, vmax=1, extent=[0, 108, 0, h], aspect="equal")
        ax.set_xticks([]); ax.set_yticks([]); ax.set_title(t, fontsize=10)
        for s in ax.spines.values():
            s.set_visible(False)
    a = axs[0]
    lab(a, 108 - FF.SIM_Y, zy(FF.SIM_Z), "SIM slit, in a finger scoop", 108 - FF.SIM_Y, zy(-10), "#c0392b")
    lab(a, 108 - 49, zy(-3.0), "SIM picture", 108 - 55, zy(-10), "#c0392b")
    lab(a, 108 - 68.7, zy(-5.8), "T-Deck reset", 108 - 75, zy(-11.5))
    a = axs[1]
    lab(a, 26, zy(0.0), "speaker grille (Alley Cat's, moved here)", 26, zy(-10.5), "#c0392b")
    lab(a, 47.7, zy(-5), "T-Deck switch", 47.7, zy(-11))
    lab(a, 66, zy(0.5), "left as it is (the notch that holds the T-Deck)", 66, zy(-10.5), "#2e8b57")
    lab(a, 80.4, zy(-5.7), "microSD", 83, zy(-11))
    lab(a, 95.8, zy(-3.0), "microSD picture", 99, zy(4.5), "#c0392b")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def right_side(phone, path):
    ys = np.arange(-2, 108.01, 0.15); zs = np.arange(-14.8, 18.3, 0.15)
    img = ray_shade(phone, ys, zs, 0, -100.0, 1.0, k=0.18)
    fig, ax = plt.subplots(figsize=(14, 5.6), dpi=110)
    ax.imshow(img, cmap="gray", vmin=0, vmax=1, extent=[ys[0], ys[-1], zs[0], zs[-1]], aspect="equal",
              origin="lower")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    yc, zc = B.SWITCH_AT
    lab(ax, 26, 0.0, "speaker grille", 22, -19)
    lab(ax, 47.7, -5, "T-Deck switch", 46, -19)
    lab(ax, 80.4, -5.7, "microSD", 86, -19)
    lab(ax, yc, 0.8 - zc, "modem switch\n(on the back's wall)", yc - 10, 21.5, "#c0392b")
    lab(ax, 34, 4.3, "front | back joint", 16, 14, "#555555")
    ax.set_ylim(25, -23)
    ax.set_title("RIGHT side, front and back together (screen side at the top; the phone's top on the right)",
                 fontsize=10)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def top_edge(phone, path):
    x0, x1, z0, z1 = FF.BADGE_FACE_18650
    fig, axs = plt.subplots(1, 2, figsize=(16, 8.5), dpi=110)
    for ax, (f, up, t) in zip(axs, (((0.30, -1.0, 0.70), (0, 0, -1), "Top edge, lying screen-up (no T-Deck drawn)"),
                                    ((0.30, -1.0, -0.70), (0, 0, 1), "Top edge, lying screen-down"))):
        f = np.asarray(f, float); f /= np.linalg.norm(f)
        w = np.asarray(up, float); w = w - (w @ f) * f; w /= np.linalg.norm(w)
        res = 0.07
        img, ext, r, w2, zb = render(phone, f, w, res, depth=True)
        ny, nx = img.shape
        U, W = np.meshgrid(ext[0] + (np.arange(nx) + .5) * res, ext[2] + (np.arange(ny) + .5) * res)
        P = U[..., None] * r + W[..., None] * w2 - zb[..., None] * f
        floor = ((np.abs(P[..., 1] - (109.0 - FF.LOGO_DEPTH)) < 0.12) & (P[..., 0] > x0) & (P[..., 0] < x1)
                 & (P[..., 2] > z0) & (P[..., 2] < z1))
        img = img.copy(); img[floor] *= 0.35
        img = np.where(np.isinf(zb), 1.0, img)
        ax.imshow(img, origin="lower", extent=ext, cmap="gray", vmin=0, vmax=1.05, interpolation="bilinear")
        ax.set_xticks([]); ax.set_yticks([]); ax.set_title(t, fontsize=11)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def top_slot_cut(front, back_f, path):
    holder = L.build_low_holder()
    X = -44.0 + 2.3
    fig, ax = plt.subplots(figsize=(11, 9.5), dpi=110)

    def cut(mesh, col, lab_):
        s = mesh.section(plane_origin=[X, 0, 0], plane_normal=[1, 0, 0])
        if s is None:
            return
        to2d = np.zeros((4, 4)); to2d[0, 1] = 1; to2d[1, 2] = 1; to2d[2, 0] = 1; to2d[3, 3] = 1
        p2, _ = s.to_planar(to_2D=to2d, check=False)
        for k, poly in enumerate(p2.polygons_full):
            xs, ys = poly.exterior.xy
            ax.fill(xs, ys, color=col, alpha=0.75, lw=0, label=lab_ if k == 0 else None)
            for hole in poly.interiors:
                hx, hy = hole.xy
                ax.fill(hx, hy, color="white", lw=0)
    cut(front, "#b9bec7", "front")
    cut(back_f, "#8d939c", "back")
    cut(holder, "#17a2b8", "low earpiece holder")
    ax.add_patch(Rectangle((74, -13.7), 26.0, 11.0, fc="#4a90c2", alpha=0.35, ec="#4a90c2", label="T-Deck"))
    ax.add_patch(Circle((B.CELL_Y, 0.8 - B.CELL_Z), B.CELL_D / 2, fc="#d9822b", alpha=0.5, ec="#a0521b",
                        label="18650 cell"))
    floor = H.FLOOR_Z - L.FLOOR_DROP
    ear_y0 = H.HOLDER_Y[0] + H.NEAR_WALL
    ax.add_patch(Rectangle((ear_y0, floor), H.EAR_W, H.EAR_BODY_H - H.SQUEEZE, fc="#c0392b", ec="k", lw=0.6,
                           label="earpiece"))
    ax.add_patch(Rectangle((102.0, L.ROOF_Z + (ANTENNA - 18) / 2), 4.0, 18, fc="#7b4fb3", alpha=0.6, ec="#7b4fb3",
                           label="GPS antenna: 18 mm ceramic"))
    ax.add_patch(Rectangle((101.0, L.ROOF_Z), 1.0, ANTENNA, fc="#3c7a3c", alpha=0.7, ec="#3c7a3c",
                           label=f"its circuit board, about {ANTENNA} mm"))
    ax.annotate("earpiece wires: up the holder's grooves,\nthen between the T-Deck's top edge\nand the antenna's "
                "board", (100.6, -5.5), (80.5, -19.5), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.annotate("0.9 mm of plastic\nover the antenna", (104.0, 11.4), (110.5, 15.5), fontsize=9,
                arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_xlim(74, 122); ax.set_ylim(-22, 20); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_xlabel("<- toward the keyboard          along the phone (mm)          top edge ->", fontsize=9)
    ax.set_ylabel("screen side (bottom) to the back of the phone (top)", fontsize=9)
    ax.set_title("Cut through the top slot: earpiece, low holder, GPS antenna, cell", fontsize=11)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def battery_contact(back, front_b, path):
    """How a battery contact sits at the cell's left end: a cut along the cell, and the end wall from inside."""
    def cut(ax, mesh, origin, normal, to2d, col):
        p2, _ = mesh.section(plane_origin=origin, plane_normal=normal).to_planar(to_2D=to2d, check=False)
        for poly in p2.polygons_full:
            xx, yy = poly.exterior.xy
            ax.fill(xx, yy, color=col, lw=0)
            for h in poly.interiors:
                hx, hy = h.xy
                ax.fill(hx, hy, color="white", lw=0)
    r = B.CELL_D / 2 + B.CELL_GAP
    yp = B.CELL_Y + B.CONTACT_DY
    bot = B.CELL_Z - np.sqrt(r ** 2 - (B.CONTACT_DY - B.CONTACT_W / 2) ** 2)      # the seat
    top = bot + 16.0
    end = 34 - B.CELL_L / 2
    sy0 = B.CELL_Y - B.CELL_D / 2 - B.SUPPORT_GAP - B.SUPPORT_T
    sz0, sz1 = B.FLOOR_Z + 0.3, B.FLOOR_Z + 4.3                                 # the strip, on a 5 mm board
    strip = "#5d6d7e"
    kw = dict(fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.8))
    fig, axs = plt.subplots(1, 2, figsize=(15, 8.5), dpi=100, gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax = axs[0]
    xz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    cut(ax, back, [0, yp, 0], [0, 1, 0], xz, "#9aa0a8")
    cut(ax, front_b, [0, yp, 0], [0, 1, 0], xz, "#c9a0dc")
    half = np.sqrt((B.CELL_D / 2) ** 2 - B.CONTACT_DY ** 2)
    ax.add_patch(Rectangle((end, B.CELL_Z - half), 12, 2 * half, fc="#e8b27a", ec="#a0521b"))
    ax.add_patch(Rectangle((-2.0, sz0), 0.15, sz1 - sz0, fc=strip, ec=strip))
    ax.plot([-1.7, -1.7], [bot, top - 1.3], color=GOLD, lw=3.5, solid_capstyle="butt")
    a = np.linspace(np.pi, 0, 30)
    ax.plot(-0.3 + 1.4 * np.cos(a), top - 1.3 + 1.4 * np.sin(a), color=GOLD, lw=3.5)
    ax.plot([1.1, end - 0.18, end - 0.18, 0.8], [top - 1.3, top - 3.0, top - 7.6, top - 9.5], color=GOLD, lw=3.5)
    ax.annotate("contact (gold): plate against the end wall,\nfolded top, spring pressed onto the cell's end",
                (end - 0.2, top - 5), (4, 9.5), **kw)
    ax.annotate("its top sits in a notch\nin the front's wall", (-0.6, top - 0.3), (-9.5, 7.5), **kw)
    ax.annotate("the protection board's nickel strip,\npressed between the plate and the wall", (-1.9, (sz0 + sz1) / 2),
                (-10.5, -19.5), **kw)
    ax.annotate("seat", (-1.2, bot - 0.4), (-6.5, -16.0), **kw)
    ax.annotate("bar across the front, joining\nthe lips at the top of the ribs", (-1.2, B.RIM_Z - 0.8), (-10.5, -7.0), **kw)
    ax.annotate("18650 cell", (8, -6), (8, -6), fontsize=10, ha="center")
    ax.annotate("back", (-3.2, -11.5), (-8, -11), **kw)
    ax.annotate("front", (-2.5, 1), (-8, 2.5), **kw)
    ax.axhline(B.RIM_Z, color="k", lw=0.6, ls=":")
    ax.text(10.5, B.RIM_Z + 0.3, "joint", fontsize=8)
    ax.axhline(B.TDECK_Z, color="b", lw=0.6, ls=":")
    ax.text(9.0, B.TDECK_Z + 0.3, "T-Deck's back", fontsize=8, color="b")
    ax.set_xlim(-11, 13); ax.set_ylim(-21, 11); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_title("Left (\u2212) end of the cell, cut along it. The right (+) end is the mirror image", fontsize=10)
    ax.set_xlabel("mm across the phone"); ax.set_ylabel("mm, screen side up")
    ax = axs[1]
    yz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    cut(ax, back, [-1.3, 0, 0], [1, 0, 0], yz, "#9aa0a8")
    cut(ax, front_b, [-1.3, 0, 0], [1, 0, 0], yz, "#c9a0dc")
    ax.add_patch(Circle((B.CELL_Y, B.CELL_Z), B.CELL_D / 2, fill=False, ec="#a0521b", lw=1.2, ls="--"))
    ax.add_patch(Rectangle((sy0 - 0.15, sz0), yp - B.CONTACT_W / 2 + 2.0 - sy0 + 0.15, sz1 - sz0, fc=strip,
                           alpha=0.45, ec=strip, lw=1.5))
    ax.add_patch(Rectangle((yp - 3.5, bot), 7.0, 16.0, fc=GOLD, alpha=0.55, ec="#8a6d10", lw=1.5))
    ax.add_patch(Rectangle((yp - 3.2, top - 9.5), 6.4, 9.3, fill=False, ec="#8a6d10", lw=1.2, ls="--"))
    ax.annotate("ribs hold the plate's edges", (yp + 4.1, -11), (97, -17.5), **kw)
    ax.annotate("", (yp - 4.1, -11), (97, -17.5), **kw)
    ax.annotate("contact plate (7 x 16 mm);\ndashed: its spring", (yp, top - 4), (97, 8.5), **kw)
    ax.annotate("lips over the plate's edges\n(the window between them is open)", (yp + 3.3, bot + 6.0), (97, -9.5), **kw)
    ax.annotate("", (yp - 3.3, bot + 6.0), (97, -9.5), **kw)
    ax.annotate("notch in the front", (yp, 2.6), (75, 9), **kw)
    ax.annotate("strip: from the board, through the\nlower rib, behind the plate", (80.5, sz1 - 0.5), (71, -18.5), **kw)
    ax.annotate("support wall\nalong the cell", (sy0 + 0.6, -6), (71.5, -1.5), **kw)
    ax.axhline(B.RIM_Z, color="k", lw=0.6, ls=":")
    ax.set_xlim(70, 108); ax.set_ylim(-21, 11); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_title("The same end wall seen from inside, cut 0.7 mm in front of it", fontsize=10)
    ax.set_xlabel("mm up the phone (top to the right)")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main(back_p, front_p, old_back_p, old_front_p, out):
    back = trimesh.load(back_p, force="mesh")
    front = trimesh.load(front_p, force="mesh")
    back_f = placed(back, TO_FRONT)
    phone = trimesh.util.concatenate([front, back_f])
    old_phone = trimesh.util.concatenate([trimesh.load(old_front_p, force="mesh"),
                                          placed(trimesh.load(old_back_p, force="mesh"), OLD_TO_FRONT)])
    os.makedirs(out, exist_ok=True)
    inside_layout(back, os.path.join(out, "18650-back-inside.png"))
    outside_angled(back, os.path.join(out, "18650-back-outside.png"))
    front_inside(front, os.path.join(out, "18650-front-inside.png"))
    side_by_side(phone, old_phone, os.path.join(out, "18650-side-view.png"))
    side_walls(front, os.path.join(out, "18650-side-walls.png"))
    right_side(phone, os.path.join(out, "18650-right-side.png"))
    top_edge(phone, os.path.join(out, "18650-top-edge.png"))
    top_slot_cut(front, back_f, os.path.join(out, "18650-top-slot.png"))
    battery_contact(back, placed(front, TO_FRONT), os.path.join(out, "18650-battery-contact.png"))
    print("pictures written to", out)


if __name__ == "__main__":
    main(*sys.argv[1:6])
