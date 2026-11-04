"""Make the earpiece holder: a printed block that fills the front's old GPS-module pocket and keeps the earpiece
pressed onto the pocket floor, over the 1 x 6 mm grille slot.

Usage:
    python make_earpiece_holder.py <output.stl> [picture.png front.stl back.stl]

With the optional picture and the two case files, it also checks that the holder clears both case halves
and draws how it fits. Needs: numpy, trimesh, shapely, manifold3d (and matplotlib for the picture).

Sizes are in the front file's coordinates (mm): x across the phone (u = -x seen from the screen), y up the
phone (top edge 108), z from the screen face (-14.7) toward the back. The back is placed with
x_f = -x_b - 10, z_f = -4.7 - z_b.

The front's pocket is x -52.2..-35.8, y 100.2..107.5, floor z -11.1. It is open toward the T-Deck (-y) and
toward the back (+z). Its walls end 1 mm above the mating face (z 4.3), at z 5.3, where the back's block
closes over it (z 5.5). From z 4.3 up, the back's top wall comes in to y 106.09. The back's half of the old
slot is filled solid (make_back.py), so the holder only has the front's part to fill.
"""
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon, box

# ---- Pocket and neighbours, measured from the case files ------------------------------------------
POCKET_X = (-52.2, -35.8)
POCKET_Y = (100.2, 107.5)         # -y side is open to the T-Deck's top edge
FLOOR_Z = -11.1
MATING_Z = 4.3                    # front and back meet here; the back's top wall starts at this height
BACK_WALL_Y = 106.09              # back's top wall, inside face (from MATING_Z up)
BACK_BLOCK_Z = 5.5                # underside of the back's block over the pocket
SLOT_CENTRE = (-44.0, 103.85)     # the grille slot through the floor (x, y)
TDECK_BACK_Z = -2.7               # back of the T-Deck (11 mm thick, screen side at -13.7)

# ---- Earpiece: Micromax receiver, measured by the owner ------------------------------------------
EAR_L, EAR_W, EAR_H = 13.0, 5.0, 2.0      # length (along x), width, height including the rubber gasket
CUP_SPARE = 0.4                           # added to the length and width
SQUEEZE = 0.3                             # the gasket is pressed this much onto the floor

# ---- Holder -------------------------------------------------------------------------------------
SIDE_CLEAR = 0.2
HOLDER_X = (POCKET_X[0] + SIDE_CLEAR, POCKET_X[1] - SIDE_CLEAR)   # 16.0 mm
HOLDER_Y = (POCKET_Y[0] + 0.2, POCKET_Y[1] - 0.2)                 # 6.9 mm
BODY_TOP = MATING_Z - 0.2                 # full-width part stops under the back's top wall
TONGUE_Y1 = BACK_WALL_Y - 0.25            # narrower top, beside the back's top wall
TONGUE_TOP = BACK_BLOCK_Z - 0.1           # the back holds it down when the case is closed
CHANNEL_W, CHANNEL_D = 2.5, 1.2           # wire channel in the cup's ceiling, for the solder joints
GROOVE_W = 3.0                            # wire groove up the T-Deck-side face
GROOVE_DEPTH = 2.4                        # from that face, reaching the ceiling channel


def prism_x(poly_yz, x0, x1):
    m = trimesh.creation.extrude_polygon(poly_yz, height=x1 - x0)
    m.apply_transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float))
    return m


def prism_y(poly_xz, y0, y1):
    m = trimesh.creation.extrude_polygon(poly_xz, height=y1 - y0)
    m.apply_transform(np.array([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float))
    return m


def prism_z(poly_xy, z0, z1):
    m = trimesh.creation.extrude_polygon(poly_xy, height=z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def cuboid(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def build_holder():
    """The holder in the front's coordinates, as it sits in the pocket."""
    x0, x1 = HOLDER_X
    y0, y1 = HOLDER_Y
    z0 = FLOOR_Z
    # side profile (y, z): full width up to BODY_TOP, a narrower tongue up to TONGUE_TOP,
    # chamfers where the pocket's far wall has a small fillet at the floor and leans in near the top
    side = Polygon([(y0, z0), (y1 - 0.5, z0), (y1, z0 + 0.5), (y1, BODY_TOP - 0.4), (y1 - 0.4, BODY_TOP),
                    (TONGUE_Y1, BODY_TOP), (TONGUE_Y1, TONGUE_TOP), (y0, TONGUE_TOP)])
    body = prism_x(side, x0, x1)
    # plan (x, y): far corners chamfered for the pocket's corner radii
    plan = Polygon([(x0, y0), (x1, y0), (x1, y1 - 0.4), (x1 - 0.4, y1), (x0 + 0.4, y1), (x0, y1 - 0.4)])
    body = trimesh.boolean.intersection([body, prism_z(plan, z0 - 1, TONGUE_TOP + 1)], engine="manifold")
    # end profile (x, z): small lead-in chamfers along the bottom ends
    end = Polygon([(x0 + 0.3, z0), (x1 - 0.3, z0), (x1, z0 + 0.3), (x1, TONGUE_TOP + 1), (x0, TONGUE_TOP + 1),
                   (x0, z0 + 0.3)])
    body = trimesh.boolean.intersection([body, prism_y(end, y0 - 1, y1 + 1)], engine="manifold")

    cx, cy = SLOT_CENTRE
    cl, cw = EAR_L + CUP_SPARE, EAR_W + CUP_SPARE
    cup_top = FLOOR_Z + EAR_H - SQUEEZE
    cup = cuboid(cx - cl / 2, cx + cl / 2, cy - cw / 2, cy + cw / 2, z0 - 1, cup_top)
    channel = cuboid(cx - cl / 2, cx + cl / 2, cy - CHANNEL_W / 2, cy + CHANNEL_W / 2, z0, cup_top + CHANNEL_D)
    groove = cuboid(cx - GROOVE_W / 2, cx + GROOVE_W / 2, y0 - 1, y0 + GROOVE_DEPTH, cup_top, TONGUE_TOP + 1)
    holder = trimesh.boolean.difference([body, trimesh.boolean.union([cup, channel, groove], engine="manifold")],
                                        engine="manifold")
    assert holder.is_watertight
    return holder


def for_printing(holder):
    """Lay the holder on its T-Deck-side face (the flat face with the wire groove), centred on the origin."""
    m = holder.copy()
    m.apply_transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float))
    lo, hi = m.bounds
    m.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    return m


def back_in_front_coords(back):
    b = back.copy()
    b.apply_transform(np.array([[-1, 0, 0, -10], [0, 1, 0, 0], [0, 0, -1, -4.7], [0, 0, 0, 1]], dtype=float))
    b.fix_normals()
    return b


def check_fit(holder, front, back_f):
    lifted = holder.copy()
    lifted.apply_translation([0, 0, 0.02])      # it rests on the pocket floor: ignore that contact
    for name, part in (("front", front), ("back", back_f)):
        overlap = trimesh.boolean.intersection([lifted, part], engine="manifold")
        vol = overlap.volume if len(overlap.faces) else 0.0
        print(f"holder overlaps the {name} by {vol:.4f} mm^3")
        assert vol < 0.01, f"holder collides with the {name}"


def draw(holder, front, back_f, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from make_diagrams import render

    def view(ax, mesh, forward, up, title):
        f = np.asarray(forward, float); f /= np.linalg.norm(f)
        w = np.asarray(up, float); w = w - (w @ f) * f; w /= np.linalg.norm(w)
        img, ext, _, _, zb = render(mesh, f, w, 0.03, depth=True)
        img = np.ma.masked_where(np.isinf(zb), img)
        cmap = plt.get_cmap("Greens_r").copy(); cmap.set_bad("white")
        ax.imshow(img, origin="lower", extent=ext, cmap=cmap, vmin=0, vmax=1.35)
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=10)

    fig = plt.figure(figsize=(16, 6.8), dpi=120)
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.5])
    view(fig.add_subplot(gs[0]), holder, (0.35, 0.55, 1.0), (0, 0, 1),
         "Seen from below and from the T-Deck side:\nthe cup the earpiece sits in (wire channel\nalong its ceiling) and the wire groove")
    view(fig.add_subplot(gs[1]), for_printing(holder), (0.45, 0.6, -1.0), (0, 1, 0),
         "As printed: lying on the T-Deck-side face\n(the groove underneath), no supports")

    ax = fig.add_subplot(gs[2])
    xc = SLOT_CENTRE[0] + 2.3                  # through the slot and the cup, just beside the groove
    for mesh, col, lab in ((front, "#4a78b5", "front"), (back_f, "#d08a3a", "back (its slot now filled)"),
                           (holder, "#3a9a4a", "earpiece holder")):
        s = mesh.section(plane_origin=[xc, 0, 0], plane_normal=[1, 0, 0])
        if s is None:
            continue
        p2, _ = s.to_planar(to_2D=np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float),
                            check=False)
        for k, poly in enumerate(p2.polygons_full):
            xs, ys = poly.exterior.xy
            ax.fill(xs, ys, color=col, alpha=0.55, lw=0, label=lab if k == 0 else None)
            for hole in poly.interiors:
                hx, hy = hole.xy
                ax.fill(hx, hy, color="white", lw=0)
    cy = SLOT_CENTRE[1]
    ax.add_patch(Rectangle((cy - EAR_W / 2, FLOOR_Z), EAR_W, EAR_H, fc="#c0392b", ec="k", lw=0.6,
                           label="earpiece (5 x 2 mm)"))
    ax.add_patch(Rectangle((90.0, -13.7), POCKET_Y[0] - 90.0, 11.0, fc="#bbbbbb", ec="#777", lw=0.6,
                           label="T-Deck"))
    gy0 = HOLDER_Y[0]
    ax.add_patch(Rectangle((gy0, FLOOR_Z + EAR_H - SQUEEZE), GROOVE_DEPTH, TONGUE_TOP - (FLOOR_Z + EAR_H - SQUEEZE),
                           fill=False, ec="k", ls="--", lw=0.8, label="wire groove (middle 3 mm)"))
    ax.annotate("grille slot", (cy, -14.7), (cy + 3.5, -17.2), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate("wires: up the groove, then\nover the T-Deck to the modem", (gy0 + 1.0, 0.5), (89.6, 2.2), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.set_xlim(89, 111); ax.set_ylim(-18, 23); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_xlabel("mm, toward the top edge of the phone"); ax.set_ylabel("mm, screen face at -14.7")
    ax.set_title("Cut through the closed case, through the slot and cup", fontsize=10)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8, framealpha=0.95)
    fig.suptitle("Earpiece holder: fills the front's old GPS-module pocket and presses the earpiece onto the slot",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path)


def main(dst, picture=None, front_path=None, back_path=None):
    holder = build_holder()
    lo, hi = holder.bounds
    print(f"holder {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f} mm, {holder.volume:.0f} mm^3; "
          f"cup {EAR_L + CUP_SPARE:.1f} x {EAR_W + CUP_SPARE:.1f} x {EAR_H - SQUEEZE:.1f} mm")
    if front_path and back_path:
        front = trimesh.load(front_path, force="mesh")
        back_f = back_in_front_coords(trimesh.load(back_path, force="mesh"))
        check_fit(holder, front, back_f)
        if picture:
            draw(holder, front, back_f, picture)
    for_printing(holder).export(dst)


if __name__ == "__main__":
    main(*sys.argv[1:])
