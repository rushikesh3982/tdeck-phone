"""Assembly diagrams for the T-Deck phone case, drawn from the actual case files.

Usage:
    python make_diagrams.py <front-earpiece-mic.stl> <back-modem-gps.stl> <output folder>

Needs: numpy, trimesh, matplotlib. Writes assembly-front-outside.png, assembly-front-inside.png,
assembly-back-inside.png and assembly-stack.png.

Front file coordinates: screen face at z = -14.7, inside toward +z, phone's LEFT side at x = -6,
RIGHT side at x = -82, top edge y = 108, bottom edge y = -2.
Back file coordinates: outside face z = -27, inside floor z = -25, rim z = -9; phone's LEFT side at
x = -4, RIGHT side at x = 72. Assembled: x_front = -x_back - 10, z_front = -4.7 - z_back.
"""
import os
import sys

import numpy as np
import trimesh
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon as MPoly, Rectangle  # noqa: E402

RES = 0.15        # mm per pixel
NAVY = "#1f3a5f"
COL = {"board": "#2f6db5", "battery": "#d9822b", "patch": "#7b4fb3", "sim": "#e0a400",
       "cap": "#c0392b", "cable": "#2e8b57", "strip": "#9fd8b0", "wire": "#555555"}


# ---------------------------------------------------------------- rendering
def render(mesh, forward, up, res=RES, depth=False):
    """Orthographic z-buffer render. Returns (shade image, extent, right, up[, depth buffer])."""
    f = np.asarray(forward, float); w = np.asarray(up, float)
    r = np.cross(f, w)
    V = mesh.vertices
    U, W, D = V @ r, V @ w, -(V @ f)
    n = mesh.face_normals
    keep = (n @ f) < 1e-9                      # cull faces turned away from the camera
    F = mesh.faces[keep]; nk = n[keep]
    light = -f + 0.45 * w + 0.35 * r
    light /= np.linalg.norm(light)
    shade = np.clip(np.nan_to_num(nk @ light), 0, 1) * 0.75 + 0.25
    umin, umax, vmin, vmax = U.min(), U.max(), W.min(), W.max()
    nx, ny = int((umax - umin) / res) + 2, int((vmax - vmin) / res) + 2
    zbuf = np.full((ny, nx), -np.inf); img = np.ones((ny, nx))
    pu, pv = (U - umin) / res, (W - vmin) / res
    for k, (a, b, c) in enumerate(F):
        xs, ys, zs = pu[[a, b, c]], pv[[a, b, c]], D[[a, b, c]]
        x0, x1 = int(np.floor(xs.min())), int(np.ceil(xs.max()))
        y0, y1 = int(np.floor(ys.min())), int(np.ceil(ys.max()))
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(den) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(max(x0, 0), min(x1, nx - 1) + 1), np.arange(max(y0, 0), min(y1, ny - 1) + 1))
        l1 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
        l2 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
        l3 = 1 - l1 - l2
        ins = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not ins.any():
            continue
        z = (l1 * zs[0] + l2 * zs[1] + l3 * zs[2])[ins]
        gx, gy = gx[ins], gy[ins]
        upd = z > zbuf[gy, gx]
        zbuf[gy[upd], gx[upd]] = z[upd]; img[gy[upd], gx[upd]] = shade[k]
    if depth:
        return img, [umin, umax, vmin, vmax], r, w, zbuf
    return img, [umin, umax, vmin, vmax], r, w


LOGO_FLOOR_Y = 108.55                      # engraved logo floor on the top-edge badge (front file)
BADGE_FACE_UV = (35.6, 52.4, -8.8, 1.7)    # badge face seen from above: u = -x, v = z


def show_logo(img, ext, zbuf, res=RES):
    """Darken the engraved logo in a top-edge view (its floor faces the camera, so shading can't show it)."""
    ny, nx = img.shape
    u = ext[0] + (np.arange(nx) + 0.5) * res
    v = ext[2] + (np.arange(ny) + 0.5) * res
    U, V = np.meshgrid(u, v)
    u0, u1, v0, v1 = BADGE_FACE_UV
    rad = 1.6                                          # badge face corner radius
    du = np.maximum(np.abs(U - (u0 + u1) / 2) - ((u1 - u0) / 2 - rad), 0)
    dv = np.maximum(np.abs(V - (v0 + v1) / 2) - ((v1 - v0) / 2 - rad), 0)
    inside = du ** 2 + dv ** 2 < (rad - 0.15) ** 2
    mask = (np.abs(zbuf - LOGO_FLOOR_Y) < 0.04) & inside
    img = img.copy(); img[mask] *= 0.4
    return img


def show(ax, img, ext):
    ax.imshow(img, origin="lower", extent=ext, cmap="gray", vmin=0, vmax=1.05, interpolation="bilinear")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def marker(ax, x, y, n, dx=0.0, dy=0.0, size=11):
    """Numbered callout at (x+dx, y+dy) with a leader line to (x, y)."""
    if dx or dy:
        ax.annotate("", (x, y), (x + dx, y + dy), arrowprops=dict(arrowstyle="-", color=NAVY, lw=1.0))
        ax.plot(x, y, "o", ms=3, color=NAVY)
    ax.text(x + dx, y + dy, str(n), ha="center", va="center", fontsize=size - 3, color="white", weight="bold",
            bbox=dict(boxstyle="circle,pad=0.25", fc=NAVY, ec="white", lw=1.0), zorder=10)


def key(ax, items, title=None, fontsize=8.5):
    ax.axis("off")
    h_in = ax.get_position().height * ax.figure.get_size_inches()[1]
    line = fontsize * 1.3 / 72 / h_in          # one text line, as a fraction of the key's height
    y = 1.0
    if title:
        ax.text(0, y, title, fontsize=fontsize + 1.5, weight="bold", va="top", transform=ax.transAxes)
        y -= 2.2 * line
    for n, text in items:
        if str(n):
            ax.text(0.015, y, str(n), fontsize=fontsize - 1, color="white", weight="bold", va="top", ha="center",
                    transform=ax.transAxes, bbox=dict(boxstyle="circle,pad=0.25", fc=NAVY, ec="white"))
        ax.text(0.06, y, text, fontsize=fontsize, va="top", transform=ax.transAxes)
        y -= line * (1 + text.count("\n")) + 0.9 * line


def proj(r, w, p):
    p = np.asarray(p, float)
    return float(p @ r), float(p @ w)


# ---------------------------------------------------------------- front, outside
def front_outside(front, path):
    views = {
        "face": ((0, 0, 1), (0, 1, 0)),     # screen side
        "top": ((0, -1, 0), (0, 0, 1)),     # top edge, back of phone up
        "bottom": ((0, 1, 0), (0, 0, -1)),  # bottom edge, screen side up
        "left": ((-1, 0, 0), (0, 1, 0)),    # phone's left side, screen side toward the face view
        "right": ((1, 0, 0), (0, 1, 0)),    # phone's right side
    }
    R = {k: render(front, *v) for k, v in views.items() if k != "top"}
    ti, te, tr, tw, tz = render(front, *views["top"], depth=True)
    R["top"] = (show_logo(ti, te, tz), te, tr, tw)
    fig = plt.figure(figsize=(15, 11.5), dpi=110)
    # unfolded layout: [left][face][right] with top above and bottom below the face
    W_face = R["face"][1][1] - R["face"][1][0]; H_face = R["face"][1][3] - R["face"][1][2]
    W_side = R["left"][1][1] - R["left"][1][0]; H_edge = R["top"][1][3] - R["top"][1][2]
    scale = 0.0058
    x0, y0 = 0.03, 0.06
    def axes_at(x, y, wmm, hmm):
        return fig.add_axes([x, y, wmm * scale * 11.5 / 15, hmm * scale])
    ax_left = axes_at(x0, y0 + H_edge * scale, W_side, H_face)
    xf = x0 + (W_side + 2) * scale * 11.5 / 15
    ax_face = axes_at(xf, y0 + H_edge * scale, W_face, H_face)
    xr = xf + (W_face + 2) * scale * 11.5 / 15
    ax_right = axes_at(xr, y0 + H_edge * scale, W_side, H_face)
    ax_top = axes_at(xf, y0 + (H_edge + H_face + 1.5) * scale, W_face, H_edge)
    ax_bot = axes_at(xf, y0 - 1.5 * scale, W_face, H_edge)
    for ax, k in ((ax_face, "face"), (ax_top, "top"), (ax_bot, "bottom"), (ax_left, "left"), (ax_right, "right")):
        show(ax, R[k][0], R[k][1])
    def P(k, p):
        return proj(R[k][2], R[k][3], p)
    ax_face.text(*P("face", (-44, 60, -14.7)), "T-Deck screen\nand keyboard\nshow through here", ha="center", va="center",
                 fontsize=9, color="0.35")
    marker(ax_face, *P("face", (-44, 103.85, -14.7)), 1, dy=-9)
    marker(ax_top, *P("top", (-19, 108, -2.85)), 2, dy=-11)
    marker(ax_top, *P("top", (-69, 108, -2.85)), 3, dy=-11)
    marker(ax_top, *P("top", (-44, 108.9, -3.5)), 4, dy=9)
    marker(ax_bot, *P("bottom", (-44, -2, -5)), 5, dy=-8)
    marker(ax_bot, *P("bottom", (-29, -1.66, -1.0)), 6, dy=-8)
    marker(ax_left, *P("left", (-6, 39, -0.5)), 7, dx=-8)
    marker(ax_left, *P("left", (-6, 68.6, -5.7)), 8, dx=-8, dy=-5)
    marker(ax_right, *P("right", (-82, 47.5, -4.75)), 9, dx=8)
    marker(ax_right, *P("right", (-82, 80.5, -5.7)), 10, dx=8)
    for ax, t in ((ax_top, "TOP EDGE"), (ax_bot, "BOTTOM EDGE"), (ax_face, "SCREEN SIDE")):
        ax.set_title(t, fontsize=8, color="0.3", pad=2)
    ax_left.set_title("LEFT SIDE", fontsize=8, color="0.3", pad=2)
    ax_right.set_title("RIGHT SIDE", fontsize=8, color="0.3", pad=2)
    kx = xr + (W_side + 6) * scale * 11.5 / 15
    ax_key = fig.add_axes([kx, 0.08, 0.98 - kx, 0.86])
    key(ax_key, [
        (1, "Earpiece grille (1 × 6 mm slot). The earpiece\nsits in the pocket right behind it."),
        (2, "SMA cut-out, top-left: the T-Deck's LoRa\nantenna (where it is now)."),
        (3, "SMA cut-out, top-right (old Grove corner):\n4G antenna, recommended. Nut and washer go\nin the round recess outside."),
        (4, "rushiWorks logo badge, engraved. The\nearpiece pocket is behind it, inside."),
        (5, "USB-C: charging and programming."),
        (6, "Mic sound hole (1.5 mm). The mic sits in a\npocket right behind it."),
        (7, "Speaker grille: the T-Deck's own speaker,\nwhich plays the ringtone."),
        (8, "Opening for the printed Reset Button part."),
        (9, "T-Deck power switch: the printed Switch\npart slides here. It turns the modem on\nand off too."),
        (10, "microSD card slot."),
        ("", "The SIM slit is on the back panel's\nleft side (see the back diagram)."),
    ], title="Front panel, outside (unfolded)")
    fig.savefig(path); plt.close(fig)


# ---------------------------------------------------------------- front, inside
def front_inside(front, path):
    img, ext, r, w = render(front, (0, 0, -1), (0, 1, 0))
    fig = plt.figure(figsize=(13, 9.5), dpi=110)
    ax = fig.add_axes([0.02, 0.03, 0.5, 0.92]); show(ax, img, ext)
    P = lambda p: proj(r, w, p)
    ax.set_title("Front panel, INSIDE (as you look into it from the back,\nso the phone's left side is on the RIGHT here)",
                 fontsize=9.5)
    ax.text(*P((-44, 55, 0)), "The T-Deck goes in\nhere, screen down", ha="center", va="center", fontsize=10, color="0.35")
    marker(ax, *P((-44, 103.8, -11)), 1, dy=-14)
    marker(ax, *P((-29, 1.5, -1)), 2, dx=8, dy=13)
    marker(ax, *P((-29, 6, 3)), 3, dx=-8, dy=13)
    marker(ax, *P((-19, 101.7, -2.85)), 4, dx=6, dy=-12)
    marker(ax, *P((-69, 101.7, -2.85)), 5, dx=-6, dy=-12)
    marker(ax, *P((-29.5, 102.9, 5)), 6, dx=4, dy=-12)
    marker(ax, *P((-58.5, 102.9, 5)), 6, dx=-4, dy=-12)
    ax.text(*P((-8, 112, 0)), "phone LEFT →", ha="right", fontsize=8, color="0.3")
    ax.text(*P((-80, 112, 0)), "← phone RIGHT", ha="left", fontsize=8, color="0.3")
    ax_key = fig.add_axes([0.56, 0.05, 0.42, 0.88])
    key(ax_key, [
        (1, "Earpiece pocket (16.4 × 7.3 mm). The Micromax\nreceiver lies on its floor, facing the slot, with\nits foam ring under it and foam behind it.\nWires leave through the open back."),
        (2, "Mic pocket, entered from inside. Push the mic\nin until it touches the 1.2 mm skin, and glue it.\nDo this BEFORE the T-Deck goes in."),
        (3, "Wire groove: the mic's two wires go up here\nand through the notch in the lip, to the back."),
        (4, "Hex pocket of the top-left SMA cut-out\n(T-Deck's LoRa connector)."),
        (5, "Hex pocket of the top-right SMA cut-out\n(4G connector's hex collar sits here)."),
        (6, "M3 × 5 heat-set inserts (2). The two M3 × 8\ncase screws come in from the back panel."),
    ], title="Front panel, inside")
    fig.savefig(path); plt.close(fig)


# ---------------------------------------------------------------- back, inside
def back_inside(back, path, layout):
    img, ext, r, w = render(back, (0, 0, -1), (0, 1, 0))
    fig = plt.figure(figsize=(15, 11), dpi=110)
    ax = fig.add_axes([0.02, 0.03, 0.46, 0.92]); show(ax, img, ext)
    ax.set_title("Back panel, INSIDE (as you look into it from the T-Deck side;\nphone's left on the left)", fontsize=9.5)
    btb = layout["board_to_back"]
    BW, BH = layout["BOARD_W"], layout["BOARD_H"]

    def bpoly(pts, **kw):
        ax.add_patch(MPoly([btb(u, v) for u, v in pts], closed=True, **kw))

    # free strip
    x_edge = btb(0, 0)[0]
    ax.add_patch(Rectangle((x_edge + 0.3, 45), 68.8 - x_edge - 0.3, 53, fc=COL["strip"], alpha=0.35, ec="none"))
    # board, SIM holder, caps
    bpoly([(0, 0), (BW, 0), (BW, BH), (0, BH)], fill=False, ec=COL["board"], lw=2.0)
    bpoly([(7.3, 41.0), (21.9, 41.0), (21.9, BH), (7.3, BH)], fc=COL["sim"], alpha=0.45, ec=COL["sim"])
    for u, v, rad in ((44.4, 28.8, 3.5), (42.85, 48.1, 2.5)):
        x, y = btb(u, v)
        ax.add_patch(Rectangle((x - 6, y - rad), 12, 2 * rad, fc=COL["cap"], alpha=0.35, ec=COL["cap"]))
    # header pads; the ones this project solders are highlighted and named
    j1 = ["STA", "NET", "DTR", "RI", "VDD", "GND", "RX", "TX", "RST", "1V8"]
    j3 = ["CLK", "CS", "MOSI", "MISO", "M-", "M+", "S-", "S+", "SCL", "SDA", "GND", "VCC"]
    used = {"VDD", "GND", "RX", "TX", "M-", "M+", "S-", "S+"}
    for (u, v0, names, dy) in ((2.6, 13.07, j1, -2.6), (52.0, 13.1, j3, 1.6)):
        for i, name in enumerate(names):
            x, y = btb(u, v0 + 2.55 * i)
            on = name in used and not (names is j3 and name == "GND")
            ax.add_patch(Circle((x, y), 0.85 if on else 0.6, fc="#e63946" if on else "#d4af37", ec="0.2", lw=0.5))
            if on:
                ax.text(x, y + dy, name.replace("-", "−"), ha="center", va="center", fontsize=5.6, color="#7a0010",
                        rotation=90)
    # sockets
    for (u, v) in ((24.8, 3.6), (2.2, 41.5)):
        x, y = btb(u, v)
        ax.add_patch(Rectangle((x - 1.3, y - 1.3), 2.6, 2.6, fc="#d4af37", ec="0.1"))
    # GPS patch
    cx, cy = layout["PATCH_CENTRE"]; hp = layout["PATCH_PCB"] / 2
    ax.add_patch(Rectangle((cx - hp, cy - hp), 2 * hp, 2 * hp, fc=COL["patch"], alpha=0.25, ec=COL["patch"], lw=1.5))
    # battery (dashed, over the board)
    ax.add_patch(Rectangle((0.4, 34.5), 55, 65, fill=False, ec=COL["battery"], lw=2.2, ls="--"))
    ax.text(28, 37.2, "battery 65 × 55 × 9 (lies over the board)", ha="center", fontsize=7.5, color=COL["battery"])
    # 4G cable route
    x1, y1 = btb(24.8, 3.6)
    ax.plot([x1, 61, 61, 59], [y1, y1 + 3, 98, 104], color=COL["cable"], lw=2.2)
    # network LED + light tube window, and the power LED
    lx, ly = btb(*layout["NETLIGHT_UV"])
    ax.add_patch(Circle(((lx + layout["LED_HOLE_X"]) / 2, ly), layout["LED_TUBE_OD"] / 2, fill=False, ec=COL["cable"], lw=1.4))
    ax.plot(lx, ly, "*", color="#00a651", ms=9, mec="0.2", mew=0.4)
    px, py = btb(50.58, 7.63)
    ax.add_patch(Rectangle((px - 1.0, py - 0.6), 2.0, 1.2, fc="0.75", ec="0.3", lw=0.6))
    # MOSFET board in the strip
    ax.add_patch(FancyBboxPatch((58.5, 52), 7, 9, boxstyle="round,pad=0.3", fc="0.85", ec="0.3"))
    # callouts
    marker(ax, *btb(51.115, 53.965), 1, dx=-9, dy=-6)
    for u, v in ((3.215, 3.265), (51.115, 3.265), (3.215, 53.965)):
        ax.plot(*btb(u, v), "o", ms=3, color=NAVY)
    marker(ax, *btb(30, 20), 2, dx=0, dy=0)
    marker(ax, *btb(14.6, 50), 3, dx=6, dy=3)
    marker(ax, -4.2, btb(14.6, BH)[1], 4, dx=-0.1, dy=-10)
    marker(ax, *btb(2.6, 25.8), 5, dy=-7)
    marker(ax, *btb(52.0, 25.8), 6, dy=7)
    marker(ax, *btb(24.8, 3.6), 7, dx=4, dy=-7)
    marker(ax, *btb(2.2, 41.5), 8, dx=5, dy=-6)
    marker(ax, cx, cy, 9)
    marker(ax, *btb(44.4, 28.8), 10, dy=5)
    marker(ax, *btb(42.85, 48.1), 10, dy=5)
    marker(ax, 50, 37.5, 11)
    marker(ax, 64, 82, 12)
    marker(ax, 62, 56.5, 13)
    marker(ax, 19.6, 102.85, 14, dy=6)
    marker(ax, 48.5, 102.85, 14, dy=6)
    marker(ax, 19.0, 6.5, 15, dx=-9, dy=6)
    marker(ax, lx, ly, 16, dx=-7, dy=-6)
    marker(ax, px, py, 17, dx=-6, dy=4)
    ax_key = fig.add_axes([0.51, 0.04, 0.47, 0.9])
    key(ax_key, [
        (1, "Standoffs (4) with M3 × 5 heat-set inserts. The KTRON board\nsits on them, held by 4 × M3 × 6 screws."),
        (2, "KTRON modem board (blue outline), COMPONENT SIDE DOWN,\nturned so its SIM edge faces the phone's left side."),
        (3, "Micro-SIM holder (on the board's upper side, toward the T-Deck)."),
        (4, "SIM slit through the left wall (15 × 1.8 mm, flared outside).\nPush the card in until it clicks; push again to release."),
        (5, "Header pads J1 (red = used): VDD, GND, RX, TX → T-Deck's\nGrove pads (old Grove socket, top-right corner of the T-Deck)."),
        (6, "Header pads J3 (red = used): M−, M+ → mic; S−, S+ → earpiece."),
        (7, "U.FL1 (4G) → green cable to the 4G antenna's SMA cut-out\nin the front's top-right corner."),
        (8, "U.FL2 (GPS) → GPS patch cable (95 mm; coil the extra)."),
        (9, "GPS patch cradle: patch ceramic side DOWN on the four pads,\ncable through any notch, a dab of hot glue."),
        (10, "C11: 470 µF 16 V laid flat and glued (C17: 100 µF, or left off),\nunder the board. Nothing there taller than 8 mm."),
        (11, "Battery outline (orange, dashed): lies over the board with\n1 mm foam between, connector end toward the bottom."),
        (12, "Free strip (green): 4G cable, MOSFET switch board, battery feed\nwires. The battery doesn't cover it, so the full depth is free."),
        (13, "MOSFET switch board (AO3401A + AO3400A), in the battery +\nline to the modem."),
        (14, "Case screw holes (2): M3 × 8 from outside into the front's inserts."),
        (15, "Mic wires arrive here from the front's groove; run them under\nthe board to J3."),
        (16, "Network LED (NETLIGHT) and its window: a light tube up to just\nunder the LED, and a 1.6 mm hole through the back cover."),
        (17, "Power LED (PWR): no window. Probably dark on battery power."),
    ], title="Back panel, inside")
    fig.savefig(path); plt.close(fig)


# ---------------------------------------------------------------- stack (section through the SIM slit)
def stack(front, back, path, layout):
    y_cut = 58.6
    b = back.copy()
    T = np.eye(4); T[0, 0] = -1; T[0, 3] = -10; T[2, 2] = -1; T[2, 3] = -4.7
    b.apply_transform(T)
    fig, ax = plt.subplots(figsize=(14, 6.3), dpi=110)
    for m, col in ((front, "0.55"), (b, "0.35")):
        sec = m.section(plane_origin=[0, y_cut, 0], plane_normal=[0, 1, 0])
        if sec is None:
            continue
        for ent in sec.discrete:
            pts = np.asarray(ent)
            ax.fill(-pts[:, 0], pts[:, 2], color=col, alpha=0.9, lw=0)
    def zf(zb):
        return -4.7 - zb
    def xf(xb):
        return -xb - 10
    X0 = layout["X0"]
    layers = [
        ("T-Deck (11 mm)", 10, 78, -13.7, -2.7, "#bbbbbb"),
        ("battery (9 mm)", -xf(0.4), -xf(55.4), zf(-11.9), zf(-2.9), COL["battery"]),
        ("foam (1 mm)", -xf(15.0), -xf(55.4), zf(-12.9), zf(-11.9), "#f3d19c"),
        ("SIM holder", -xf(-1.4), -xf(14.8), zf(-14.4), zf(-12.9), COL["sim"]),
        ("KTRON board (1.6 mm)", -xf(-1.4), -xf(X0), zf(-16.0), zf(-14.4), COL["board"]),
    ]
    for name, u0, u1, z0, z1, col in layers:
        ax.add_patch(Rectangle((min(u0, u1), min(z0, z1)), abs(u1 - u0), abs(z1 - z0), fc=col, ec="0.2", lw=0.6, alpha=0.85))
    ax.annotate("SIM card goes in here →", (-xf(-4.0), zf(-13.65)), (-xf(-4.0) - 1, zf(-13.65) + 0.2), fontsize=8,
                ha="right", va="center", color="0.15")
    ax.text(44, -8.2, "T-Deck (11 mm, screen facing down)", ha="center", va="center", fontsize=9)
    ax.text(30, zf(-7.4), "battery 9 mm", ha="center", va="center", fontsize=9)
    ax.text(40, zf(-12.4), "foam 1 mm", ha="center", va="center", fontsize=7)
    ax.text(12, zf(-13.65), "SIM holder", ha="center", va="center", fontsize=7)
    ax.text(40, zf(-15.2), "KTRON board, component side down", ha="center", va="center", fontsize=7.5, color="white")
    ax.text(40, zf(-20.5), "9 mm gap: flat capacitors, U.FL plugs, wires", ha="center", va="center", fontsize=8, color="0.25")
    ax.text(70.5, zf(-14), "free strip:\n4G cable,\nMOSFET\nboard", ha="center", va="center", fontsize=7.5, color="0.25")
    ax.annotate("", (88.5, -14.7), (88.5, zf(-27)), arrowprops=dict(arrowstyle="<->", color="0.3"))
    ax.text(89.2, (zf(-27) - 14.7) / 2, "≈37 mm overall", rotation=90, va="center", fontsize=8, color="0.3")
    ax.annotate("", (84, -2.7), (84, zf(-25)), arrowprops=dict(arrowstyle="<->", color=NAVY))
    ax.text(84.7, (zf(-25) - 2.7) / 2, "23 mm behind the T-Deck", rotation=90, va="center", fontsize=8, color=NAVY)
    ax.text(44, -16.3, "screen side", fontsize=8, color="0.3", ha="center")
    ax.text(44, zf(-27) + 0.7, "back cover", fontsize=8, color="0.3", ha="center")
    ax.text(-2, 4.3, "joint: front ↔ back", fontsize=7, color="0.4", ha="right")
    ax.axhline(4.3, color="0.6", lw=0.6, ls=":")
    ax.set_xlim(-14, 92); ax.set_ylim(-17.5, 24.5); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.text(2, -16.3, "phone LEFT", fontsize=8, color="0.3"); ax.text(86, -16.3, "phone RIGHT", fontsize=8, color="0.3", ha="right")
    ax.set_title(f"Cut through the assembled phone, {y_cut:.0f} mm up from the bottom (through the SIM slit), "
                 "seen from the top: how everything stacks", fontsize=9.5)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def top_edge(front, path):
    img, ext, r, w, z = render(front, (0, -1, 0), (0, 0, 1), 0.05, depth=True)
    img = show_logo(img, ext, z, 0.05)
    fig, ax = plt.subplots(figsize=(11, 3.8), dpi=110)
    show(ax, img, ext)
    ax.set_title("Top edge, seen from above with the screen side toward you: LoRa SMA (left), "
                 "rushiWorks logo badge, 4G SMA (right)", fontsize=9)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main(front_path, back_path, out_dir):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import make_back as mb
    layout = dict(board_to_back=mb.board_to_back, BOARD_W=mb.BOARD_W, BOARD_H=mb.BOARD_H,
                  PATCH_CENTRE=mb.PATCH_CENTRE, PATCH_PCB=mb.PATCH_PCB, X0=mb.X0,
                  NETLIGHT_UV=mb.NETLIGHT_UV, LED_HOLE_X=mb.LED_HOLE_X, LED_TUBE_OD=mb.LED_TUBE_OD)
    front = trimesh.load(front_path, force="mesh")
    back = trimesh.load(back_path, force="mesh")
    os.makedirs(out_dir, exist_ok=True)
    front_outside(front, os.path.join(out_dir, "assembly-front-outside.png"))
    front_inside(front, os.path.join(out_dir, "assembly-front-inside.png"))
    back_inside(back, os.path.join(out_dir, "assembly-back-inside.png"), layout)
    stack(front, back, os.path.join(out_dir, "assembly-stack.png"), layout)
    top_edge(front, os.path.join(out_dir, "front-top-edge.png"))
    print("done")


if __name__ == "__main__":
    main(*sys.argv[1:4])
