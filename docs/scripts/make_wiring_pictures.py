"""Draw the two wiring pictures in docs/images:

- bench-wiring.png: the phase-A bench setup: KTRON board, CP2102 adapter, 5 V supply, earpiece (with its two 47 uF
  capacitors), mic (with its 1 kOhm resistor from M- to GND) and antennas;
- wiring-18650.png: every wire in the 18650 version: the cell, its contacts and protection board, the modem switch,
  the T-Deck's battery socket and Grove pads, earpiece, mic and both antennas.

Usage:
    python make_wiring_pictures.py <output folder>

Board positions are from KTRON's dimension drawing (component side, antenna socket at the top):
https://www.ktron.in/wp-content/uploads/2024/04/4G-module-1-scaled.jpg
C11 and the regulator are not on that drawing, so in the 18650 picture their marks only say which side they are on.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

BOARD_W, BOARD_H = 54.33, 57.23
PITCH = 2.55
LEFT = ["STA", "NET", "DTR", "RI", "VDD", "GND", "RX", "TX", "RST", "1V8"]
RIGHT = ["CLK", "CS", "MOSI", "MISO", "M-", "M+", "S-", "S+", "SCL", "SDA", "GND", "VCC"]
LEFT_U, RIGHT_U, FIRST_V = 2.45, 51.8, 13.07

COL = {"bat+": "#d62728", "gnd": "#222222", "tx": "#e6a100", "rx": "#2ca02c", "vdd": "#ff7f0e",
       "ear": "#1f77b4", "mic": "#9467bd", "rf": "#8c564b", "strip": "#9a9a9a"}


def hole(u, v):
    return u, -v                       # drawing coords (v down) -> plot coords


def wire(ax, p0, p1, col, lw=2.0, via=None, hop_at=None):
    """A wire from p0 through the via points to p1. hop_at=(x, y) draws a small bridge where this (horizontal)
    wire passes over another one without touching it."""
    pts = [p0] + (via or []) + [p1]
    if hop_at is None:
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=lw, solid_capstyle="round")
        return
    hx, hy = hop_at
    r = 1.2
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        out.append(a)
        if a[1] == b[1] == hy and min(a[0], b[0]) < hx < max(a[0], b[0]):
            s = 1 if b[0] > a[0] else -1
            out.append((hx - s * r, hy))
            ax.plot([p[0] for p in out], [p[1] for p in out], color=col, lw=lw, solid_capstyle="round")
            t = np.linspace(0, np.pi, 20)
            ax.plot(hx - s * r * np.cos(t), hy + r * np.sin(t), color=col, lw=lw)
            out = [(hx + s * r, hy)]
    out.append(pts[-1])
    ax.plot([p[0] for p in out], [p[1] for p in out], color=col, lw=lw, solid_capstyle="round")


def dot(ax, p, col):
    ax.add_patch(Circle(p, 0.75, fc=col, ec=col, zorder=5))


def draw_board(ax, used_left, used_right, sim_note="micro-SIM holder\n(on the other side)", title_xy=(BOARD_W / 2, -27)):
    """The KTRON board as on KTRON's drawing. Returns the pads' and sockets' positions."""
    ax.add_patch(FancyBboxPatch((0, -BOARD_H), BOARD_W, BOARD_H, boxstyle="round,pad=0,rounding_size=3",
                                fc="#e8f1e8", ec="#3a7a3a", lw=1.5))
    for (u, v) in ((3.215, 3.265), (51.115, 3.265), (3.215, 53.965), (51.115, 53.965)):
        ax.add_patch(Circle(hole(u, v), 1.6, fc="white", ec="#3a7a3a"))
    ax.add_patch(Rectangle((7.3, -BOARD_H + 0.5), 14.6, 16.0, fill=False, ec="#999", ls="--"))
    ax.text(14.6, -BOARD_H + 8.5, sim_note, ha="center", va="center", fontsize=7.5, color="#777")
    ax.text(*title_xy, "KTRON KSTM1548\n(A7672S)", ha="center", va="center", fontsize=12, color="#3a7a3a",
            weight="bold")
    pins = {}
    for i, name in enumerate(LEFT):
        x, y = hole(LEFT_U, FIRST_V + i * PITCH)
        used = name in used_left
        ax.add_patch(Circle((x, y), 0.85, fc="#c0392b" if used else "white", ec="#444", lw=0.8, zorder=4))
        ax.text(x + 1.6, y, name, va="center", fontsize=8, weight="bold" if used else None,
                color="#000" if used else "#999")
        pins[("L", name)] = (x, y)
    for i, name in enumerate(RIGHT):
        x, y = hole(RIGHT_U, FIRST_V + i * PITCH)
        used = name in used_right
        ax.add_patch(Circle((x, y), 0.85, fc="#c0392b" if used else "white", ec="#444", lw=0.8, zorder=4))
        ax.text(x - 1.6, y, name.replace("-", "−"), va="center", ha="right", fontsize=8,
                weight="bold" if used else None, color="#000" if used else "#999")
        pins[("R", name)] = (x, y)
    ufl1, ufl2 = hole(24.8, 3.6), hole(2.2, 41.5)
    for (x, y), lab in ((ufl1, "U.FL1 (4G)"), (ufl2, "U.FL2 (GPS)")):
        ax.add_patch(Rectangle((x - 1.5, y - 1.5), 3, 3, fc="#d9c2a6", ec="#8c564b", zorder=4))
        ax.text(x + 2.3, y + (0 if lab.startswith("U.FL1") else -2.6), lab, fontsize=7.5, va="center",
                color="#8c564b")
    pins["UFL1"], pins["UFL2"] = ufl1, ufl2
    return pins


def draw_mic(ax, pins, mx, my, steps=(60, 63)):
    """Mic to the right of the board, with the 1 kOhm resistor from M- to the right row's GND, on the board's
    component side. The resistor's legs pass between the pad labels."""
    ax.add_patch(Circle((mx + 4, my), 5, fc="#bbb", ec="#555"))
    ax.text(mx + 4, my, "mic\n6027", ha="center", va="center", fontsize=8)
    for pin, yy, lab, xt in ((("R", "M-"), my + 2.5, "pin joined to the can → M−", steps[0]),
                             (("R", "M+"), my - 2.5, "pin in the ring → M+", steps[1])):
        px, py = pins[pin]
        wire(ax, (px, py), (mx - 1, yy), COL["mic"], via=[(xt, py), (xt, yy)])
        ax.text(mx + 10.5, yy, lab, va="center", fontsize=8)

    # resistor: M- (top) to GND (bottom of the row), drawn inside the board, left of the labels
    mxp, myp = pins[("R", "M-")]
    gx, gy = pins[("R", "GND")]
    y_top, y_bot = myp - PITCH / 2, gy + PITCH / 2          # between the labels
    rx = 41.0
    leg = dict(color=COL["mic"], lw=1.4)
    ax.plot([mxp, mxp - 2.2, rx, rx], [myp, y_top, y_top, -27.0], **leg)
    ax.plot([gx, gx - 2.2, rx, rx], [gy, y_bot, y_bot, -33.0], **leg)
    ax.add_patch(Rectangle((rx - 1.1, -33.0), 2.2, 6.0, fc="#e9d8a6", ec="#7a5c00", lw=1.2, zorder=4))
    for k, c in enumerate(("#8b4513", "#000000", "#d62728")):          # brown black red = 1 kOhm
        ax.add_patch(Rectangle((rx - 1.1, -28.6 - k * 1.1), 2.2, 0.5, fc=c, ec=c, zorder=5))
    ax.text(rx - 1.8, -35.2, "1 kΩ: M− to GND", ha="right", va="center", fontsize=7.5, weight="bold",
            color="#5a3d00")


def draw_earpiece(ax, pins, ex, ey, cap_x, steps=(70, 72)):
    ax.add_patch(FancyBboxPatch((ex - 3, ey - 6), 14, 12, boxstyle="round,pad=0,rounding_size=1.5", fc="#222",
                                ec="#222"))
    ax.text(ex + 4, ey, "earpiece\n32 Ω", ha="center", va="center", fontsize=8, color="white")
    for pin, yy, xt in ((("R", "S-"), ey + 3, steps[0]), (("R", "S+"), ey - 3, steps[1])):
        px, py = pins[pin]
        wire(ax, (px, py), (cap_x - 1.6, yy), COL["ear"], via=[(xt, py), (xt, yy)])
        ax.plot([cap_x - 1.6, cap_x - 1.6], [yy - 1.6, yy + 1.6], color="k", lw=2)
        ax.plot([cap_x + 0.4, cap_x + 0.4], [yy - 1.6, yy + 1.6], color="k", lw=2)
        ax.text(cap_x - 3.2, yy + 1.2, "+", fontsize=9, weight="bold", ha="center")
        wire(ax, (cap_x + 0.4, yy), (ex - 3, yy), COL["ear"])
    ax.text(cap_x, ey - 6.5, "2 × 47 µF, 10 V or more\n+ leg toward the board", ha="center", va="top", fontsize=8,
            weight="bold")
    ax.text(ex + 4, ey + 7.5, "either way round,\nnothing to ground", ha="center", va="bottom", fontsize=8,
            color="#444")


def data_wires(ax, src, pins, steps):
    """src: {'3V3', 'GND', 'RX', 'TX'} -> point. Each goes right, down at its step, and right to its pad."""
    for name, target, col in (("3V3", "VDD", COL["vdd"]), ("GND", "GND", COL["gnd"]),
                              ("RX", "RX", COL["rx"]), ("TX", "TX", COL["tx"])):
        s, d = src[name], pins[("L", target)]
        xt = steps[name]
        wire(ax, s, d, col, via=[(xt, s[1]), (xt, d[1])])


def bench(path):
    fig, ax = plt.subplots(figsize=(17, 11), dpi=110)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-62, 128); ax.set_ylim(-88, 30)

    pins = draw_board(ax, {"VDD", "GND", "RX", "TX"}, {"M-", "M+", "S-", "S+", "GND", "VCC"})
    ax.text(BOARD_W / 2, -BOARD_H - 3.5, "Board seen from the side with the modem chip and antenna sockets, as on KTRON's "
            "drawing.\nGo by the labels printed next to the holes.", ha="center", va="top", fontsize=8, color="#555")

    # ---- CP2102 adapter (left). Pins drawn in the board's order so no wires cross; on the adapter itself
    # they may be in another order, so go by the labels.
    cx0, cy_top = -54, -4
    ax.add_patch(FancyBboxPatch((cx0, cy_top - 30), 20, 30, boxstyle="round,pad=0,rounding_size=1.5",
                                fc="#dfe8f5", ec="#1f4e8c", lw=1.3))
    ax.text(cx0 + 10, cy_top + 2.5, "CP2102 USB-serial adapter", ha="center", fontsize=9.5, weight="bold",
            color="#1f4e8c")
    ax.text(cx0 + 10, cy_top - 33, "USB → Mac (serial terminal, 115200 baud).\nIts pins may be in another order:\n"
                                   "go by the labels.", ha="center", va="top", fontsize=8, color="#1f4e8c")
    cp = {}
    for i, name in enumerate(["5V", "3V3", "GND", "RXD", "TXD"]):
        x, y = cx0 + 20, cy_top - 4 - i * 5.5
        ax.add_patch(Circle((x, y), 0.9, fc="#1f4e8c" if name != "5V" else "white", ec="#1f4e8c"))
        ax.text(x - 1.8, y, name, ha="right", va="center", fontsize=9, weight="bold")
        cp[name] = (x, y)
    ax.text(cp["5V"][0] + 2.0, cp["5V"][1], "✕ leave empty", va="center", fontsize=8.5, color="#c0392b")
    data_wires(ax, {"3V3": cp["3V3"], "GND": cp["GND"], "RX": cp["RXD"], "TX": cp["TXD"]}, pins,
               {"3V3": -6, "GND": -10, "RX": -14, "TX": -18})
    ax.text(-31, -44, "TXD → TX and RXD → RX: straight across.\nTested: crossed, the modem doesn't answer.",
            fontsize=8, color="#444", va="top")

    draw_mic(ax, pins, 100, 4)
    draw_earpiece(ax, pins, 104, -30, 88)

    # ---- 5 V supply (bottom right). VCC is the lowest hole, so it takes the inner, lower route.
    sx0, sy0 = 88, -56
    ax.add_patch(FancyBboxPatch((sx0, sy0 - 15), 30, 15, boxstyle="round,pad=0,rounding_size=1.5",
                                fc="#fbe3e3", ec="#a52a2a", lw=1.3))
    ax.text(sx0 + 15, sy0 + 2.0, "5 V supply, at least 2 A", ha="center", fontsize=9.5, weight="bold", color="#a52a2a")
    ax.text(sx0 + 15, sy0 - 17, "phone charger + USB breakout (or a cut-open\nUSB cable). Check + and − with the "
                                "multimeter first.", ha="center", va="top", fontsize=8, color="#a52a2a")
    sp = {"GND": (sx0, sy0 - 4.5), "+5V": (sx0, sy0 - 10.5)}
    for name, (x, y) in sp.items():
        ax.add_patch(Circle((x, y), 0.9, fc="#a52a2a", ec="#a52a2a"))
        ax.text(x + 1.8, y, name, va="center", fontsize=9, weight="bold")
    wire(ax, pins[("R", "GND")], sp["GND"], COL["gnd"], lw=3, via=[(63, pins[("R", "GND")][1]), (63, sp["GND"][1])])
    wire(ax, pins[("R", "VCC")], sp["+5V"], COL["bat+"], lw=3, via=[(60, pins[("R", "VCC")][1]), (60, sp["+5V"][1])])
    ax.text(65, -47, "VCC and the GND beside it:\n24 AWG, bench only (removed in phase B).\n"
                     "The mic's resistor stays in that GND hole.", fontsize=8, color="#444")

    # ---- antennas
    ufl1, ufl2 = pins["UFL1"], pins["UFL2"]
    ax.plot([ufl1[0], ufl1[0]], [ufl1[1] + 1.5, 16], color=COL["rf"], lw=2)
    ax.text(ufl1[0], 17.5, "IPX → SMA cable → 4G antenna (700–2700 MHz)\npress the plug straight down until it clicks",
            ha="center", va="bottom", fontsize=8.5, color=COL["rf"])
    ax.plot([ufl2[0] - 1.5, -3], [ufl2[1], ufl2[1]], color=COL["rf"], lw=2)
    ax.plot([-3, -3], [ufl2[1], -72], color=COL["rf"], lw=2)
    ax.add_patch(Rectangle((-11, -82), 16, 10, fc="#e0d2b8", ec=COL["rf"]))
    ax.text(-3, -77, "GPS patch\n(ceramic to the sky)", ha="center", va="center", fontsize=7.5)

    ax.set_title("Bench wiring for the modem tests (phase A): 10 soldered holes (red), CP2102 to the Mac, "
                 "5 V on VCC, earpiece, mic with its resistor, antennas", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def phone_18650(path):
    fig, ax = plt.subplots(figsize=(17, 13), dpi=110)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-80, 130); ax.set_ylim(-88, 66)

    pins = draw_board(ax, {"VDD", "GND", "RX", "TX"}, {"M-", "M+", "S-", "S+", "GND"},
                      sim_note="micro-SIM holder\n(on the other side,\nfacing the T-Deck)", title_xy=(24.0, -24.0))
    vx, vy = pins[("R", "VCC")]
    ax.text(vx + 2.0, vy, "✕ VCC: never used", va="center", fontsize=8.5, color="#c0392b", weight="bold")
    ax.text(BOARD_W / 2, -BOARD_H - 3.5,
            "Board seen from the side with the modem chip and antenna sockets, as on KTRON's drawing.\n"
            "In the phone this side faces the back's floor. Go by the labels printed next to the holes.",
            ha="center", va="top", fontsize=8, color="#555")

    # ---- battery: cell, contacts, protection board, nickel strips (top)
    cell_x, cell_y, cell_h = (-1.0, 55.0), 40.0, 11.0
    ax.add_patch(FancyBboxPatch((cell_x[0], cell_y), cell_x[1] - cell_x[0], cell_h,
                                boxstyle="round,pad=0,rounding_size=4", fc="#f0d9b5", ec="#b5803a", lw=1.5))
    ax.add_patch(Rectangle((cell_x[1] - 0.5, cell_y + 3.5), 1.6, cell_h - 7, fc="#c9c9c9", ec="#777"))
    ax.text(sum(cell_x) / 2, cell_y + cell_h / 2, "18650 cell (LG MJ1, about 3400 mAh)\n"
            "+ end to the right (marked on the floor)",
            ha="center", va="center", fontsize=9, color="#7a4a10", weight="bold")
    ax.text(cell_x[0] + 3.2, cell_y + cell_h / 2, "−", ha="center", va="center", fontsize=16, weight="bold")
    ax.text(cell_x[1] - 3.0, cell_y + cell_h / 2, "+", ha="center", va="center", fontsize=16, weight="bold")
    contact = {"-": (-4.5, cell_y - 1.5), "+": (56.6, cell_y - 1.5)}
    for sign, (x, y) in contact.items():
        ax.add_patch(Rectangle((x, y), 2.4, cell_h + 3, fc="#d4af37", ec="#8a6d00", lw=1.2))
    ax.text(contact["-"][0] - 1.0, cell_y + cell_h + 3.2, "− contact (left end wall)", ha="right", va="bottom",
            fontsize=8, color="#6b5300")
    ax.text(contact["+"][0] + 3.4, cell_y + cell_h + 3.2, "+ contact (right end wall)", ha="left", va="bottom",
            fontsize=8, color="#6b5300")

    pb_x, pb_y, pb_h = (10.0, 43.0), 26.5, 6.0
    ax.add_patch(Rectangle((pb_x[0], pb_y), pb_x[1] - pb_x[0], pb_h, fc="#3f8f55", ec="#1f5a30", lw=1.2))
    ax.text(sum(pb_x) / 2, pb_y + pb_h - 1.6, "protection board", ha="center", va="center", fontsize=8.5,
            color="white", weight="bold")
    ax.text(sum(pb_x) / 2, cell_y - 3.6, "glued to the support wall, chips toward the wall", ha="center",
            va="center", fontsize=7.5, color="#1f5a30")
    pads = {"B−": (pb_x[0] + 2.0, pb_y), "P−": (19.0, pb_y), "P+": (31.0, pb_y), "B+": (pb_x[1] - 2.0, pb_y)}
    for name, (x, y) in pads.items():
        ax.add_patch(Circle((x, y + 1.6), 0.9, fc="#e6e6e6", ec="#555", zorder=5))
        right = name != "B+"
        ax.text(x + (1.6 if right else -1.6), y + 1.6, name, ha="left" if right else "right", va="center",
                fontsize=8, color="white", weight="bold")

    # nickel strips: from each end of the board, along the wall, through the slits, behind each contact plate
    for sign, end_x, behind_x in (("-", pb_x[0], contact["-"][0] - 1.2), ("+", pb_x[1], contact["+"][0] + 3.6)):
        y0 = pb_y + 3.0
        ax.plot([end_x, behind_x, behind_x], [y0, y0, cell_y + 4.0], color=COL["strip"], lw=4.5,
                solid_capstyle="butt", solid_joinstyle="miter")
    ax.text(-8.0, 30.5, "nickel strip,\nbehind the plate", ha="right", va="center", fontsize=7.5, color="#555")
    ax.text(64.5, 33.5, "nickel strip,\nbehind the plate", ha="left", va="center", fontsize=7.5, color="#555")
    ax.text(sum(cell_x) / 2, 61.5, "No solder at the cell: each strip goes through the slits and lies behind its "
            "contact's plate, and the cell's spring presses the plate onto it.", ha="center", va="center",
            fontsize=8.5, color="#444")

    # ---- modem switch (right wall)
    sw_x, sw_y = 66.0, 5.0
    ax.add_patch(FancyBboxPatch((sw_x, sw_y), 14, 13, boxstyle="round,pad=0,rounding_size=1.0", fc="#ececec",
                                ec="#444", lw=1.2))
    ax.add_patch(Rectangle((sw_x + 14, sw_y + 4.5), 2.4, 4, fc="#666", ec="#333"))
    ax.text(sw_x + 7, sw_y + 15.2, "modem switch SS-12F15\n(back's right wall)", ha="center", va="bottom",
            fontsize=8.5, weight="bold")
    sw = {"free": (sw_x, sw_y + 10.5), "mid": (sw_x, sw_y + 6.5), "out": (sw_x, sw_y + 2.5)}
    for name, p in sw.items():
        ax.add_patch(Circle(p, 0.8, fc="#bbb" if name == "free" else "#444", ec="#333", zorder=5))
    ax.text(sw_x + 1.6, sw["free"][1], "outer: free", va="center", fontsize=7.5, color="#777")
    ax.text(sw_x + 1.6, sw["mid"][1], "middle", va="center", fontsize=7.5)
    ax.text(sw_x + 1.6, sw["out"][1], "outer", va="center", fontsize=7.5)

    # ---- C11 and the regulator's tab: the modem's battery feed (component side; places only roughly drawn)
    c11, reg = (40.0, -8.5), (19.0, -8.5)
    for p, lab in ((c11, "C11 + leg\n(470 µF)"), (reg, "regulator's\nmetal tab (GND)")):
        ax.add_patch(Circle(p, 1.1, fc="white", ec="#222", lw=1.5, zorder=5))
        ax.text(p[0], p[1] - 1.9, lab, ha="center", va="top", fontsize=7.5, weight="bold")

    # ---- T-Deck (left): battery socket and the Grove socket's pads
    tx0, tx1, ty0, ty1 = -76.0, -44.0, -40.0, 30.0
    ax.add_patch(FancyBboxPatch((tx0, ty0), tx1 - tx0, ty1 - ty0, boxstyle="round,pad=0,rounding_size=2",
                                fc="#dfe8f5", ec="#1f4e8c", lw=1.3))
    ax.text((tx0 + tx1) / 2, ty1 + 1.5, "LilyGO T-Deck", ha="center", va="bottom", fontsize=10.5, weight="bold",
            color="#1f4e8c")
    sock = {"+": (tx1, 23.0), "−": (tx1, 19.0)}
    ax.add_patch(Rectangle((tx1 - 9, 16.5), 9, 9, fc="white", ec="#1f4e8c"))
    ax.text(tx1 - 10, 21.0, "battery\nsocket\n(JST PH2.0)", ha="right", va="center", fontsize=8, color="#1f4e8c")
    for name, (x, y) in sock.items():
        ax.add_patch(Circle((x, y), 0.9, fc=COL["bat+"] if name == "+" else COL["gnd"], ec="#333", zorder=5))
        ax.text(x - 1.8, y, name, ha="right", va="center", fontsize=10, weight="bold")
    grove = {"3V3": (tx1, -6.0), "GND": (tx1, -11.5), "RX": (tx1, -17.0), "TX": (tx1, -22.5)}
    labels = {"3V3": "3.3 V (VCC)", "GND": "GND", "RX": "RX · GPIO44", "TX": "TX · GPIO43"}
    for name, (x, y) in grove.items():
        ax.add_patch(Circle((x, y), 0.9, fc="#1f4e8c", ec="#1f4e8c", zorder=5))
        ax.text(x - 1.8, y, labels[name], ha="right", va="center", fontsize=8.5, weight="bold")
    ax.text((tx0 + tx1) / 2, -1.0, "Grove socket's pads\n(socket removed)", ha="center", va="bottom", fontsize=8,
            color="#1f4e8c")
    ax.text((tx0 + tx1) / 2, -26.5, "3.3 V is switched by GPIO10:\nthe firmware keeps it on,\nalso in sleep",
            ha="center", va="top", fontsize=7.5, color="#1f4e8c")

    # ---- the wires
    W = 3.2                                                        # 24 AWG battery wires, drawn thick
    jm, jp = (pads["P−"][0], 19.0), (pads["P+"][0], 23.0)          # where each pad's wire splits
    wire(ax, pads["P−"], jm, COL["gnd"], lw=W)
    wire(ax, jm, sock["−"], COL["gnd"], lw=W)                      # JST black
    wire(ax, jm, reg, COL["gnd"], lw=W)                            # modem GND
    dot(ax, jm, COL["gnd"])
    wire(ax, pads["P+"], jp, COL["bat+"], lw=W)
    wire(ax, jp, sock["+"], COL["bat+"], lw=W, hop_at=(pads["P−"][0], 23.0))   # JST red, over the black wire
    wire(ax, jp, sw["mid"], COL["bat+"], lw=W, via=[(56.0, 23.0), (56.0, sw["mid"][1])])
    dot(ax, jp, COL["bat+"])
    wire(ax, sw["out"], c11, COL["bat+"], lw=W, via=[(c11[0], sw["out"][1])])
    ax.text(-30.0, 25.0, "JST lead: red to P+, black to P−", ha="left", va="bottom", fontsize=8, color="#444")
    ax.text(sw_x + 7, sw_y - 1.5, "on: the modem gets the cell\noff: the modem has no power", ha="center",
            va="top", fontsize=7.5, color="#444")

    data_wires(ax, grove, pins, {"3V3": -8, "GND": -12, "RX": -16, "TX": -20})
    ax.text(-42.0, -31.5, "4 thin wires, about 15 cm: up the right side, past the\ncell's right end, to the "
            "T-Deck's Grove pads.\nTX → TX and RX → RX: straight across (tested).", ha="left", va="top",
            fontsize=8, color="#444")

    draw_mic(ax, pins, 100, -8, steps=(60, 63))
    ax.text(104, -15.5, "in the front's bottom wall", ha="center", va="top", fontsize=7.5, color="#555")
    draw_earpiece(ax, pins, 104, -36, 88)
    ax.text(108, -42.8, "in the front's top pocket", ha="center", va="top", fontsize=7.5, color="#555")

    # ---- antennas
    ufl1, ufl2 = pins["UFL1"], pins["UFL2"]
    ax.plot([ufl1[0], ufl1[0]], [ufl1[1] + 1.5, 7.5], color=COL["rf"], lw=2)
    ax.plot([ufl1[0] - 2, ufl1[0], ufl1[0] + 2], [10.0, 7.5, 10.0], color=COL["rf"], lw=2)
    ax.text(ufl1[0] + 2.0, 4.0, "4G antenna\n(your choice)", ha="left", va="center", fontsize=8, color=COL["rf"],
            weight="bold")
    gx = -8.0
    ax.plot([ufl2[0] - 1.5, gx, gx], [ufl2[1], ufl2[1], -70.0], color=COL["rf"], lw=2)
    ax.add_patch(Rectangle((gx - 13, -84), 26, 14, fc="#e0d2b8", ec=COL["rf"]))
    ax.text(gx, -77, "Eteily GPS antenna (active)\nin the top slot, ceramic toward\nthe phone's top edge.\n"
            "15 cm cable; the socket gives it 3.0 V", ha="center", va="center", fontsize=7.5)

    # ---- key
    ax.text(62, -70, "Thick lines: 24 AWG battery wires. Thin lines: thin wires.\n"
            "Black: GND / battery −.   Red: battery +, after the protection board.\n"
            "C11 and the regulator are on this side of the board; their marks here only\n"
            "show which wire goes to them, not where they are. Where every wire runs:\n"
            "docs/design-18650.md, \"Wires inside\".", ha="left", va="top", fontsize=8, color="#333",
            bbox=dict(boxstyle="round,pad=0.6", fc="#f7f7f7", ec="#bbb"))

    ax.set_title("18650 version: every wire. One cell powers both boards; the modem switch is in the modem's + wire",
                 fontsize=12.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    out = sys.argv[1]
    bench(os.path.join(out, "bench-wiring.png"))
    phone_18650(os.path.join(out, "wiring-18650.png"))
