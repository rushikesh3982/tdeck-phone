"""Make the earpiece holder: a printed block that fills the front's old GPS-module pocket and keeps the earpiece
pressed onto the pocket floor, over the 1 x 6 mm grille slot.

Usage:
    python make_earpiece_holder.py <output.stl> [picture.png front.stl back.stl]
    python make_earpiece_holder.py --scale 1.01 <output.stl> [picture.png front.stl back.stl]

--scale makes the holder for a larger case: the pocket and the parts around it grow with the case, but the earpiece,
its cup and the clearances stay true to size. Give it the front and back built at the same scale.

With the optional picture and the two case files, it also checks that the holder clears both case halves
and draws how it fits. Needs: numpy, trimesh, shapely, manifold3d (and matplotlib for the picture).

Sizes are in the front file's coordinates (mm): x across the phone (u = -x seen from the screen), y up the
phone (top edge 108), z from the screen face (-14.7) toward the back. The back is placed with
x_f = -x_b - 10, z_f = -4.7 - z_b.

The front's pocket is x -52.2..-35.8, y 100.2..107.5, floor z -11.1. It is open toward the T-Deck (-y) and
toward the back (+z). Its walls end 1 mm above the mating face (z 4.3), at z 5.3, where the back's block
closes over it (z 5.5). From z 4.3 up, the back's top wall comes in to y 106.09. The back's half of the old
slot is filled solid (make_back.py), so the holder only has the front's part to fill.

The earpiece (owner's photos, 4 Nov 2026) is 12 x 6 mm, about 2:1 in the photos. It has a rubber gasket on its
sound face and two spring contacts on its back, one at each short end. The contacts are folded over the back,
which adds 1 mm. At 6 mm wide it leaves too little room for a cup wall on both sides inside the 6.9 mm holder.
So the cup is open on the far side (+y), where the pocket's own wall holds the earpiece, and walled only on the
T-Deck side. The holder presses on the middle of the back, has deeper pockets at both ends for the folded
contacts and their solder joints, and a wire groove up the T-Deck-side face from each end pocket. Every
overhang is either a short bridge or open, so it prints on that face without supports.
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
EAR_L, EAR_W = 12.0, 6.0                  # length (along x, including the small end tabs) and width
EAR_BODY_H = 2.0                          # body with its rubber gasket
EAR_PIN_H = 1.0                           # the two spring contacts, folded over the back at the short ends
PIN_ZONE = 3.0                            # how far in from each end the folded contacts and solder joints reach
CUP_SPARE = 0.4                           # added to the length
SQUEEZE = 0.3                             # the gasket is pressed this much onto the floor
PIN_SPARE = 0.5                           # room above the folded contacts for solder and wire

# ---- Holder -------------------------------------------------------------------------------------
SIDE_CLEAR = 0.2
HOLDER_X = (POCKET_X[0] + SIDE_CLEAR, POCKET_X[1] - SIDE_CLEAR)   # 16.0 mm
HOLDER_Y = (POCKET_Y[0] + 0.2, POCKET_Y[1] - 0.2)                 # 6.9 mm
BODY_TOP = MATING_Z - 0.2                 # full-width part stops under the back's top wall
TONGUE_Y1 = BACK_WALL_Y - 0.25            # narrower top, beside the back's top wall
TONGUE_TOP = BACK_BLOCK_Z - 0.1           # the back holds it down when the case is closed
NEAR_WALL = 0.7                           # cup wall on the T-Deck side; the far side is the pocket's own wall
GROOVE_W = 2.0                            # a wire groove up the T-Deck-side face from each end pocket
GROOVE_DEPTH = 1.6                        # from that face, through the cup wall into the end pocket
ASSEMBLY = (-10.0, -4.7)                  # back -> front: x_f = -x_b - 10, z_f = -4.7 - z_b


def use_scale(s):
    """A larger case: the pocket and its neighbours grow; the earpiece, its cup and the clearances stay true."""
    global POCKET_X, POCKET_Y, FLOOR_Z, MATING_Z, BACK_WALL_Y, BACK_BLOCK_Z, SLOT_CENTRE, TDECK_BACK_Z, ASSEMBLY
    global HOLDER_X, HOLDER_Y, BODY_TOP, TONGUE_Y1, TONGUE_TOP
    POCKET_X = tuple(v * s for v in POCKET_X)
    POCKET_Y = tuple(v * s for v in POCKET_Y)
    SLOT_CENTRE = tuple(v * s for v in SLOT_CENTRE)
    ASSEMBLY = tuple(v * s for v in ASSEMBLY)
    FLOOR_Z, MATING_Z, BACK_WALL_Y, BACK_BLOCK_Z, TDECK_BACK_Z = (
        v * s for v in (FLOOR_Z, MATING_Z, BACK_WALL_Y, BACK_BLOCK_Z, TDECK_BACK_Z))
    HOLDER_X = (POCKET_X[0] + SIDE_CLEAR, POCKET_X[1] - SIDE_CLEAR)
    HOLDER_Y = (POCKET_Y[0] + 0.2, POCKET_Y[1] - 0.2)
    BODY_TOP = MATING_Z - 0.2
    TONGUE_Y1 = BACK_WALL_Y - 0.25
    TONGUE_TOP = BACK_BLOCK_Z - 0.1


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
    cl = EAR_L + CUP_SPARE
    xa, xb = cx - cl / 2, cx + cl / 2
    ya, yb = y0 + NEAR_WALL, y1 + 1                    # open on the far side, up to the pocket wall
    assert POCKET_Y[1] - ya >= EAR_W + 0.2, "earpiece too wide for the pocket"
    press_z = FLOOR_Z + EAR_BODY_H - SQUEEZE           # presses on the middle of the earpiece's back
    pin_z = FLOOR_Z + EAR_BODY_H + EAR_PIN_H + PIN_SPARE
    cuts = [cuboid(xa, xb, ya, yb, z0 - 1, press_z),                    # the earpiece body
            cuboid(xa, xa + PIN_ZONE, ya, yb, z0, pin_z),               # folded contacts, one end
            cuboid(xb - PIN_ZONE, xb, ya, yb, z0, pin_z)]               # and the other
    for gx in (xa + PIN_ZONE / 2, xb - PIN_ZONE / 2):                  # a wire groove from each end pocket
        cuts.append(cuboid(gx - GROOVE_W / 2, gx + GROOVE_W / 2, y0 - 1, y0 + GROOVE_DEPTH, press_z, TONGUE_TOP + 1))
    holder = trimesh.boolean.difference([body, trimesh.boolean.union(cuts, engine="manifold")], engine="manifold")
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
    b.apply_transform(np.array([[-1, 0, 0, ASSEMBLY[0]], [0, 1, 0, 0], [0, 0, -1, ASSEMBLY[1]], [0, 0, 0, 1]], dtype=float))
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

    def cut(ax, normal_axis, at, keep):
        normal = np.eye(3)[normal_axis]
        for mesh, col, lab in ((front, "#4a78b5", "front"), (back_f, "#d08a3a", "back (its slot now filled)"),
                               (holder, "#3a9a4a", "earpiece holder")):
            s = mesh.section(plane_origin=normal * at, plane_normal=normal)
            if s is None:
                continue
            a, b = keep
            to2d = np.zeros((4, 4)); to2d[0, a] = 1; to2d[1, b] = 1; to2d[2, normal_axis] = 1; to2d[3, 3] = 1
            p2, _ = s.to_planar(to_2D=to2d, check=False)
            for k, poly in enumerate(p2.polygons_full):
                xs, ys = poly.exterior.xy
                ax.fill(xs, ys, color=col, alpha=0.55, lw=0, label=lab if k == 0 else None)
                for hole in poly.interiors:
                    hx, hy = hole.xy
                    ax.fill(hx, hy, color="white", lw=0)

    cx, cy = SLOT_CENTRE
    body_kw = dict(fc="#c0392b", ec="k", lw=0.6)
    pin_kw = dict(fc="#e0b030", ec="k", lw=0.5)
    fig = plt.figure(figsize=(15, 12.5), dpi=110)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25])
    view(fig.add_subplot(gs[0, 0]), holder, (0.35, 0.55, 1.0), (0, 0, 1),
         "Seen from below and from the T-Deck side: the cup (open on the far\nside, where the case wall holds the "
         "earpiece), deeper pockets at both\nends for the folded contacts, and a wire groove from each end")
    view(fig.add_subplot(gs[0, 1]), for_printing(holder), (0.45, 0.6, -1.0), (0, 1, 0),
         "As printed: lying on the T-Deck-side face\n(the grooves underneath), no supports")

    ax = fig.add_subplot(gs[1, 0])
    xc = cx + 2.3                                   # through the slot and the middle of the cup, beside the groove
    cut(ax, 0, xc, (1, 2))
    ear_y0 = HOLDER_Y[0] + NEAR_WALL
    ax.add_patch(Rectangle((ear_y0, FLOOR_Z), EAR_W, EAR_BODY_H, label="earpiece body + gasket", **body_kw))
    ax.add_patch(Rectangle((90.0, -13.7), POCKET_Y[0] - 90.0, 11.0, fc="#bbbbbb", ec="#777", lw=0.6, label="T-Deck"))
    gy0 = HOLDER_Y[0]
    press_z = FLOOR_Z + EAR_BODY_H - SQUEEZE
    ax.add_patch(Rectangle((gy0, press_z), GROOVE_DEPTH, TONGUE_TOP - press_z, fill=False, ec="k", ls="--", lw=0.8,
                           label="wire grooves (one at each end)"))
    ax.annotate("grille slot", (cy, -14.7), (cy + 3.5, -17.2), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate("wires: up a groove at each\nend, then over the T-Deck\nto the modem", (gy0 + 0.8, 0.5),
                (89.4, 1.5), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.set_xlim(89, 111); ax.set_ylim(-18, 23); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_xlabel("mm, toward the top edge of the phone"); ax.set_ylabel("mm, screen face at -14.7")
    ax.set_title("Cut across, through the slot and the middle of the earpiece\n(the case wall on the right holds it)",
                 fontsize=10)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.95)

    ax = fig.add_subplot(gs[1, 1])
    cut(ax, 1, cy + 0.15, (0, 2))                   # along the earpiece, through the slot
    ax.add_patch(Rectangle((cx - EAR_L / 2, FLOOR_Z), EAR_L, EAR_BODY_H, label="earpiece body + gasket", **body_kw))
    for x_end in (cx - EAR_L / 2, cx + EAR_L / 2 - 1.5):
        ax.add_patch(Rectangle((x_end, FLOOR_Z + EAR_BODY_H), 1.5, EAR_PIN_H,
                               label="folded contacts" if x_end < cx else None, **pin_kw))
    ax.annotate("grille slot (6 mm long)", (cx, -14.7), (cx + 2.0, -17.3), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate("holder presses here\n(middle of the back)", (cx + 1.5, press_z + 0.1), (cx + 1.0, -3.0), fontsize=8,
                ha="center", arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.set_xlim(-57, -31); ax.set_ylim(-18, 9); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_xlabel("mm, across the phone"); ax.set_ylabel("mm, screen face at -14.7")
    ax.set_title("Cut along the earpiece, through the slot", fontsize=10)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.95)
    fig.suptitle("Earpiece holder: fills the front's old GPS-module pocket and presses the earpiece onto the slot",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    fig.savefig(path)


def main(dst, picture=None, front_path=None, back_path=None, scale=1.0):
    if scale != 1.0:
        use_scale(scale)
    holder = build_holder()
    lo, hi = holder.bounds
    print(f"holder {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f} mm, {holder.volume:.0f} mm^3; "
          f"cup {EAR_L + CUP_SPARE:.1f} long with {POCKET_Y[1] - HOLDER_Y[0] - NEAR_WALL:.1f} mm of width up to the pocket wall, "
          f"{EAR_BODY_H - SQUEEZE:.1f} deep in the middle, "
          f"{EAR_BODY_H + EAR_PIN_H + PIN_SPARE:.1f} deep over {PIN_ZONE:.1f} mm at each end")
    if front_path and back_path:
        front = trimesh.load(front_path, force="mesh")
        back_f = back_in_front_coords(trimesh.load(back_path, force="mesh"))
        check_fit(holder, front, back_f)
        if picture:
            draw(holder, front, back_f, picture)
    for_printing(holder).export(dst)


if __name__ == "__main__":
    args = sys.argv[1:]
    scale = 1.0
    if args and args[0] == "--scale":
        scale = float(args[1]); args = args[2:]
    main(*args, scale=scale)
