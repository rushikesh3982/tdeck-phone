"""Draw screen-layout.png: the test program's screen, with example values, at 3x the T-Deck's 320 x 240.

Usage:
    python screen_mock.py <output.png>

The layout follows src/main.cpp (TOP, ROW_H, VALUE_X, the labels and the footer). The values are examples only.
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

TOP, ROW_H, VALUE_X = 26, 17, 84
GREEN, YELLOW, RED, WHITE, DIM = "#00ff00", "#ffff00", "#ff0000", "#ffffff", "#808080"
ROWS = [
    ("Modem", "answering (A7672S-FASE)", GREEN),
    ("SIM", "ready", GREEN),
    ("Network", "registered, JIO 4G", GREEN),
    ("VoLTE", "yes: calls go over 4G", GREEN),
    ("4G signal", "-93 dBm, fair, B5", GREEN),
    ("Average", "-92.4 dBm, last 5, B5", WHITE),
    ("Battery", "3.94 V (modem 3.91 V)", WHITE),
    ("GPS", "searching (no fix yet)", YELLOW),
    ("Call", "none", DIM),
    ("SMS", "none new", DIM),
    ("Mac", "terminal idle", DIM),
]


def main(path):
    fig = plt.figure(figsize=(9.6, 7.2 + 0.5), dpi=100)
    ax = fig.add_axes([0, 0, 1, 0.94])
    ax.set_xlim(0, 320); ax.set_ylim(240, 0); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 320, 240, fc="black"))
    ax.add_patch(Rectangle((0, 0), 320, 21, fc="#000080"))
    ax.text(6, 11, "T-Deck phone: test program", color="white", fontsize=13, va="center", family="DejaVu Sans")
    for i, (label, value, col) in enumerate(ROWS):
        y = TOP + i * ROW_H + 8
        ax.text(4, y, label, color=DIM, fontsize=12, va="center")
        ax.text(VALUE_X, y, value, color=col, fontsize=12, va="center")
    ax.text(4, 222, "Mac: USB-C serial, 115200 baud. Type AT commands;", color=DIM, fontsize=8.5, va="center",
            family="DejaVu Sans Mono")
    ax.text(4, 232, "this screen pauses its questions for 20 s after.", color=DIM, fontsize=8.5, va="center",
            family="DejaVu Sans Mono")
    fig.suptitle("The test program's screen (a mock-up with example values; the real fonts are the T-Deck's own)",
                 fontsize=11, y=0.985)
    fig.savefig(path)


if __name__ == "__main__":
    main(sys.argv[1])
