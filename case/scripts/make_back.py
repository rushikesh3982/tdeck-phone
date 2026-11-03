"""Add KTRON modem standoffs and a GPS patch cradle to the Alley Cat TD1 X back.

Usage:
    python make_back.py "<Alley Chat TD1 X Back Inside Cat Edition.stl>" <output.stl> [layout.png]

Needs: numpy, trimesh, shapely, manifold3d (and matplotlib for the layout picture).

Coordinates are the original STL's own (mm). The back is modelled face-down: the outside
face is at z = -27, the inside floor surface at z = -25.0, and the rim at z = -9. Seen from
inside the back, +x is the phone's RIGHT side and -x its LEFT side (as you look at the
screen). +y is the top of the phone.

KTRON board (KSTM1548), from KTRON's drawing: 54.33 x 57.23 mm, four 3.2 mm holes on a
47.90 x 50.70 mm rectangle. The 4G socket (U.FL1) is on the top edge, and the SIM card slides
in from the bottom edge. The board is mounted component side toward the back cover, turned
so that its SIM edge faces the phone's LEFT side.
"""
import sys

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box

FLOOR_Z = -25.0            # inside floor surface

# ---- KTRON board ------------------------------------------------------------
BOARD_W, BOARD_H = 54.33, 57.23            # drawing: u across (J1 header at u=0), v down (U.FL1 at v=0)
HOLES_UV = [(3.215, 3.265), (51.115, 3.265), (3.215, 53.965), (51.115, 53.965)]
X0 = 56.53                 # back x of the board's U.FL1 edge (v = 0)
Y0 = 98.30                 # back y of the board's J3 edge (u = BOARD_W), just below the screw columns
STANDOFF_H = 14.0          # tallest part (330 uF cap, ~13 mm) + 1 mm
STANDOFF_D = 7.0           # the 100 uF cap is ~2 mm from one hole, so no wider than this
INSERT_D = 4.5             # M3 x 5 heat-set insert hole
INSERT_DEPTH = 6.0
FLARE_D = 10.0             # wider foot so the column stays stiff while the insert is heated in
FLARE_H = 4.0              # (the caps hang down to 1 mm above the floor, and still clear this)


def board_to_back(u, v):
    """Board drawing coords (u, v) -> back (x, y)."""
    return X0 - v, Y0 - (BOARD_W - u)


# ---- GPS patch (KTRON KSTA1417) -------------------------------------------
# Estimated from KTRON's photos until measured: 25 x 25 mm PCB, ceramic ~22.7 mm square and
# ~4 mm thick on one face, metal shield on the other, ~8 mm overall.
PATCH_CENTRE = (21.5, 26.0)
PATCH_PCB = 25.0
FIT = 0.3                  # clearance each side
FENCE_T = 1.2
CERAMIC_H = 4.0
AIR_GAP = 0.5              # keep the ceramic just off the cover
PCB_T = 1.0
FENCE_ABOVE_PCB = 1.0
GUSSET_LEG = 2.8           # corner ledges the PCB rests on; clear of the ceramic's rounded corners
CABLE_NOTCH_W = 4.0


def prism_z(poly, z0, z1):
    m = trimesh.creation.extrude_polygon(poly, height=z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def build_parts():
    adds, cuts = [], []
    base_z = FLOOR_Z - 0.6                     # sink into the 2 mm floor (outer grooves start at -26)
    top_z = FLOOR_Z + STANDOFF_H
    for u, v in HOLES_UV:
        x, y = board_to_back(u, v)
        adds.append(prism_z(Point(x, y).buffer(STANDOFF_D / 2, quad_segs=24), base_z, top_z))
        foot = trimesh.creation.cone(radius=FLARE_D / 2, height=2 * FLARE_H * (FLARE_D / (FLARE_D - STANDOFF_D)) / 2,
                                     sections=48)
        # cone tip above; cut it to a frustum from the floor up to FLARE_H
        foot = trimesh.boolean.intersection([foot, trimesh.creation.box(bounds=[[-6, -6, 0], [6, 6, FLARE_H]])],
                                            engine="manifold")
        foot.apply_translation([x, y, FLOOR_Z - 0.01])
        adds.append(foot)
        adds.append(prism_z(Point(x, y).buffer(FLARE_D / 2, quad_segs=24), base_z, FLOOR_Z))
        cuts.append(prism_z(Point(x, y).buffer(INSERT_D / 2, quad_segs=24), top_z - INSERT_DEPTH, top_z + 1))

    cx, cy = PATCH_CENTRE
    inner = PATCH_PCB + 2 * FIT
    outer = inner + 2 * FENCE_T
    ledge_z = FLOOR_Z + AIR_GAP + CERAMIC_H
    fence_top = ledge_z + PCB_T + FENCE_ABOVE_PCB
    ring = box(cx - outer / 2, cy - outer / 2, cx + outer / 2, cy + outer / 2).difference(
        box(cx - inner / 2, cy - inner / 2, cx + inner / 2, cy + inner / 2))
    adds.append(prism_z(ring, base_z, fence_top))
    h = inner / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner = (cx + sx * h, cy + sy * h)
            tri = Polygon([corner, (corner[0] - sx * GUSSET_LEG, corner[1]), (corner[0], corner[1] - sy * GUSSET_LEG)])
            adds.append(prism_z(tri.buffer(0.01), base_z, ledge_z))
    # cable notches in the middle of every side, down to the PCB level, so the patch can face any way
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nx, ny = cx + dx * (h + FENCE_T / 2), cy + dy * (h + FENCE_T / 2)
        w = CABLE_NOTCH_W / 2
        notch = box(nx - (FENCE_T if dx else w), ny - (FENCE_T if dy else w),
                    nx + (FENCE_T if dx else w), ny + (FENCE_T if dy else w))
        cuts.append(prism_z(notch, ledge_z, fence_top + 1))
    return adds, cuts


def main(src, dst, picture=None):
    back = trimesh.load(src, force="mesh")
    assert back.is_watertight
    adds, cuts = build_parts()
    out = trimesh.boolean.union([back] + adds, engine="manifold")
    out = trimesh.boolean.difference([out, trimesh.boolean.union(cuts, engine="manifold")], engine="manifold")
    assert out.is_watertight, "result is not watertight"
    out.export(dst)
    print(f"added {out.volume - back.volume:.1f} mm^3, watertight {out.is_watertight}, "
          f"bodies {len(out.split(only_watertight=False))}")
    if picture:
        draw_layout(out, picture)


def draw_layout(mesh, path):
    """Inside view of the back with the board, its parts and the patch drawn on top."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon as MPoly

    sec = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, -12.0])
    fig, ax = plt.subplots(figsize=(8, 11), dpi=110)
    for s in sec:
        ax.plot(s[:, 0], s[:, 1], color="0.6", lw=0.6)
    sec2 = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, FLOOR_Z + 2.0])
    for s in sec2:
        ax.plot(s[:, 0], s[:, 1], color="0.25", lw=0.8)

    def bpoly(pts, **kw):
        ax.add_patch(MPoly([board_to_back(u, v) for u, v in pts], closed=True, **kw))

    bpoly([(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)], fill=False, ec="tab:blue", lw=1.5)
    bpoly([(7.3, 41.0), (21.9, 41.0), (21.9, 57.23), (7.3, 57.23)], fc="tab:orange", alpha=0.35, ec="tab:orange")
    for (u, v, r, name) in [(44.4, 28.8, 5.4, "330 uF"), (42.85, 48.1, 4.45, "100 uF")]:
        x, y = board_to_back(u, v)
        ax.add_patch(Circle((x, y), r, fc="tab:red", alpha=0.25, ec="tab:red"))
        ax.text(x, y, name, ha="center", va="center", fontsize=7)
    for (u, v, name) in [(24.8, 3.6, "U.FL1 (4G)"), (2.2, 41.5, "U.FL2 (GPS)")]:
        x, y = board_to_back(u, v)
        ax.plot(x, y, "s", color="tab:green")
        ax.text(x, y - 2.5, name, ha="center", fontsize=7, color="tab:green")
    x, y = board_to_back(14.6, 57.23)
    ax.annotate("SIM card goes in here", (x, y), (x + 8, y - 9), fontsize=7,
                arrowprops=dict(arrowstyle="->", color="tab:orange"), color="tab:orange")
    cx, cy = PATCH_CENTRE
    ax.add_patch(MPoly([(cx - 12.5, cy - 12.5), (cx + 12.5, cy - 12.5), (cx + 12.5, cy + 12.5), (cx - 12.5, cy + 12.5)],
                       closed=True, fc="tab:purple", alpha=0.2, ec="tab:purple"))
    ax.text(cx, cy, "GPS patch\n(ceramic down)", ha="center", va="center", fontsize=7)
    for u, v in HOLES_UV:
        ax.add_patch(Circle(board_to_back(u, v), STANDOFF_D / 2, fill=False, ec="k", lw=1))
    ax.text(70, 104, "phone RIGHT side →", ha="right", fontsize=8)
    ax.text(-2, 104, "← phone LEFT side", ha="left", fontsize=8)
    ax.text(34, -1, "bottom of phone (USB-C)", ha="center", fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-6, 74); ax.set_ylim(-4, 110)
    ax.set_title("Back panel seen from inside: modem board (blue) and GPS patch (purple)", fontsize=9)
    ax.grid(True, alpha=0.2)
    fig.tight_layout(); fig.savefig(path)


if __name__ == "__main__":
    main(*sys.argv[1:4])
