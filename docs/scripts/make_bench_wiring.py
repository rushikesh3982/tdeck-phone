"""Draw the phase-A bench wiring: KTRON board, CP2102 adapter, 5 V supply, earpiece (with its two 47 uF
capacitors), mic and antennas.

Usage:
    python make_bench_wiring.py <output.png>

Board positions are from KTRON's dimension drawing (component side, antenna socket at the top):
https://www.ktron.in/wp-content/uploads/2024/04/4G-module-1-scaled.jpg
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

BOARD_W, BOARD_H = 54.33, 57.23
PITCH = 2.55
LEFT = ["STA", "NET", "DTR", "RI", "VDD", "GND", "RX", "TX", "RST", "1V8"]
RIGHT = ["CLK", "CS", "MOSI", "MISO", "M-", "M+", "S-", "S+", "SCL", "SDA", "GND", "VCC"]
LEFT_U, RIGHT_U, FIRST_V = 2.45, 51.8, 13.07
USED_LEFT = {"VDD", "GND", "RX", "TX"}
USED_RIGHT = {"M-", "M+", "S-", "S+", "GND", "VCC"}

COL = {"5v": "#d62728", "gnd": "#222222", "tx": "#e6a100", "rx": "#2ca02c", "vdd": "#ff7f0e",
       "ear": "#1f77b4", "mic": "#9467bd", "rf": "#8c564b"}


def hole(u, v):
    return u, -v                       # drawing coords (v down) -> plot coords


def main(path):
    fig, ax = plt.subplots(figsize=(17, 11), dpi=110)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-62, 128); ax.set_ylim(-88, 30)

    # ---- board
    ax.add_patch(FancyBboxPatch((0, -BOARD_H), BOARD_W, BOARD_H, boxstyle="round,pad=0,rounding_size=3",
                                fc="#e8f1e8", ec="#3a7a3a", lw=1.5))
    for (u, v) in ((3.215, 3.265), (51.115, 3.265), (3.215, 53.965), (51.115, 53.965)):
        ax.add_patch(Circle(hole(u, v), 1.6, fc="white", ec="#3a7a3a"))
    ax.add_patch(Rectangle((7.3, -BOARD_H + 0.5), 14.6, 16.0, fill=False, ec="#999", ls="--"))
    ax.text(14.6, -BOARD_H + 8.5, "micro-SIM holder\n(on the other side)", ha="center", va="center", fontsize=7.5,
            color="#777")
    ax.text(BOARD_W / 2, -27, "KTRON KSTM1548\n(A7672S)", ha="center", va="center", fontsize=12, color="#3a7a3a",
            weight="bold")
    ax.text(BOARD_W / 2, -BOARD_H - 3.5, "Board seen from the side with the modem chip and antenna sockets, as on KTRON's "
            "drawing.\nGo by the labels printed next to the holes.", ha="center", va="top", fontsize=8, color="#555")
    pins = {}
    for i, name in enumerate(LEFT):
        x, y = hole(LEFT_U, FIRST_V + i * PITCH)
        used = name in USED_LEFT
        ax.add_patch(Circle((x, y), 0.85, fc="#c0392b" if used else "white", ec="#444", lw=0.8))
        ax.text(x + 1.6, y, name, va="center", fontsize=8, weight="bold" if used else None,
                color="#000" if used else "#999")
        pins[("L", name)] = (x, y)
    for i, name in enumerate(RIGHT):
        x, y = hole(RIGHT_U, FIRST_V + i * PITCH)
        used = name in USED_RIGHT
        ax.add_patch(Circle((x, y), 0.85, fc="#c0392b" if used else "white", ec="#444", lw=0.8))
        ax.text(x - 1.6, y, name.replace("-", "−"), va="center", ha="right", fontsize=8,
                weight="bold" if used else None, color="#000" if used else "#999")
        pins[("R", name)] = (x, y)
    ufl1, ufl2 = hole(24.8, 3.6), hole(2.2, 41.5)
    for (x, y), lab in ((ufl1, "U.FL1 (4G)"), (ufl2, "U.FL2 (GPS)")):
        ax.add_patch(Rectangle((x - 1.5, y - 1.5), 3, 3, fc="#d9c2a6", ec="#8c564b"))
        ax.text(x + 2.3, y + (0 if lab.startswith("U.FL1") else -2.6), lab, fontsize=7.5, va="center",
                color="#8c564b")

    def wire(p0, p1, col, lw=2.0, via=None):
        pts = [p0] + (via or []) + [p1]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=lw, solid_capstyle="round")

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
    for i, name in enumerate(["5V", "3V3", "GND", "TXD", "RXD"]):
        x, y = cx0 + 20, cy_top - 4 - i * 5.5
        ax.add_patch(Circle((x, y), 0.9, fc="#1f4e8c" if name != "5V" else "white", ec="#1f4e8c"))
        ax.text(x - 1.8, y, name, ha="right", va="center", fontsize=9, weight="bold")
        cp[name] = (x, y)
    ax.text(cp["5V"][0] + 2.0, cp["5V"][1], "✕ leave empty", va="center", fontsize=8.5, color="#c0392b")
    for name, target, col, xt in (("3V3", "VDD", COL["vdd"], -6), ("GND", "GND", COL["gnd"], -10),
                                  ("TXD", "RX", COL["tx"], -14), ("RXD", "TX", COL["rx"], -18)):
        src, dst = cp[name], pins[("L", target)]
        wire(src, dst, col, via=[(xt, src[1]), (xt, dst[1])])
    ax.text(-31, -44, "TXD → RX and RXD → TX (crossed).\nIf AT gets no reply, swap these two.",
            fontsize=8, color="#444", va="top")

    # ---- mic (top right). The upper hole goes to the upper pin, so the wires don't cross.
    mx, my = 100, 4
    ax.add_patch(Circle((mx + 4, my), 5, fc="#bbb", ec="#555"))
    ax.text(mx + 4, my, "mic\n6027", ha="center", va="center", fontsize=8)
    for pin, yy, lab, xt in ((("R", "M-"), my + 2.5, "pin joined to the can → M−", 60),
                             (("R", "M+"), my - 2.5, "pin in the ring → M+", 63)):
        px, py = pins[pin]
        wire((px, py), (mx - 1, yy), COL["mic"], via=[(xt, py), (xt, yy)])
        ax.text(mx + 10.5, yy, lab, va="center", fontsize=8)

    # ---- earpiece with two 47 uF capacitors (right, middle)
    ex, ey = 104, -30
    ax.add_patch(FancyBboxPatch((ex - 3, ey - 6), 14, 12, boxstyle="round,pad=0,rounding_size=1.5", fc="#222",
                                ec="#222"))
    ax.text(ex + 4, ey, "earpiece\n32 Ω", ha="center", va="center", fontsize=8, color="white")
    cap_x = 88
    for pin, yy, xt in ((("R", "S-"), ey + 3, 70), (("R", "S+"), ey - 3, 72)):
        px, py = pins[pin]
        wire((px, py), (cap_x - 1.6, yy), COL["ear"], via=[(xt, py), (xt, yy)])
        ax.plot([cap_x - 1.6, cap_x - 1.6], [yy - 1.6, yy + 1.6], color="k", lw=2)
        ax.plot([cap_x + 0.4, cap_x + 0.4], [yy - 1.6, yy + 1.6], color="k", lw=2)
        ax.text(cap_x - 3.2, yy + 1.2, "+", fontsize=9, weight="bold", ha="center")
        wire((cap_x + 0.4, yy), (ex - 3, yy), COL["ear"])
    ax.text(cap_x, ey - 6.5, "2 × 47 µF, 10 V or more\n+ leg toward the board", ha="center", va="top", fontsize=8,
            weight="bold")
    ax.text(ex + 4, ey + 7.5, "either way round,\nnothing to ground", ha="center", va="bottom", fontsize=8,
            color="#444")

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
    wire(pins[("R", "GND")], sp["GND"], COL["gnd"], lw=3, via=[(63, pins[("R", "GND")][1]), (63, sp["GND"][1])])
    wire(pins[("R", "VCC")], sp["+5V"], COL["5v"], lw=3, via=[(60, pins[("R", "VCC")][1]), (60, sp["+5V"][1])])
    ax.text(65, -47, "VCC and the GND beside it:\n24 AWG, bench only (removed in phase B)", fontsize=8, color="#444")

    # ---- antennas
    ax.plot([ufl1[0], ufl1[0]], [ufl1[1] + 1.5, 16], color=COL["rf"], lw=2)
    ax.text(ufl1[0], 17.5, "IPX → SMA cable → 4G antenna (700–2700 MHz)\npress the plug straight down until it clicks",
            ha="center", va="bottom", fontsize=8.5, color=COL["rf"])
    ax.plot([ufl2[0] - 1.5, -3], [ufl2[1], ufl2[1]], color=COL["rf"], lw=2)
    ax.plot([-3, -3], [ufl2[1], -72], color=COL["rf"], lw=2)
    ax.add_patch(Rectangle((-11, -82), 16, 10, fc="#e0d2b8", ec=COL["rf"]))
    ax.text(-3, -77, "GPS patch\n(ceramic to the sky)", ha="center", va="center", fontsize=7.5)

    ax.set_title("Bench wiring for the modem tests (phase A): 10 soldered holes (red), CP2102 to the Mac, "
                 "5 V on VCC, earpiece, mic, antennas", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(path)


if __name__ == "__main__":
    main(sys.argv[1])
