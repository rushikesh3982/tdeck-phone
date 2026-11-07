"""Add KTRON modem standoffs, a SIM slit (with a SIM-direction picture beside it), a GPS patch cradle and a
network-LED window to the Alley Cat TD1 X back, fill the back's half of the old GPS-module slot, and replace the
cat on its outside with the rushiWorks logo.

Usage:
    python make_back.py "<Alley Chat TD1 X Back Outside Cat Edition.stl>" <output.stl> [layout.png] [logo image]
    python make_back.py --scale 1.01 "<...Outside Cat Edition.stl>" <output.stl>

--scale builds a larger cover for a tight T-Deck fit (see case/README.md, "Fit and scale"). Everything grows
with Alley Cat's shell except the four modem standoffs: they keep the KTRON board's exact 47.90 x 50.70 mm hole
spacing and their 4.5 mm insert holes, so the board still screws on. Their group sits where the larger cover puts it.

Needs: numpy, trimesh, shapely, manifold3d, pillow, matplotlib. The logo image defaults to
../logo/rushi-logo.jpg. (The Outside Cat and Inside Cat editions are identical except for the outer 1 mm of
the cover, so everything inside works the same with either.)

Coordinates are the original STL's own (mm). The back is modelled face-down: the outside
face is at z = -27, the inside floor surface at z = -25.0, and the rim at z = -9 (where the
front's top face, z = 4.3 in the front's file, meets it). Seen from inside the back, +x is the
phone's RIGHT side and -x its LEFT side (as you look at the screen). +y is the top of the phone.
The left side wall runs from x = -4 (outside) to x = -2 (inside).

KTRON board (KSTM1548), from KTRON's drawing: 54.33 x 57.23 mm, four 3.2 mm holes on a
47.90 x 50.70 mm rectangle. The 4G socket (U.FL1) is on the top edge, and the micro-SIM card
slides in from the bottom edge (push-push holder on the solder side, at the J1 header end).
The board is mounted component side toward the back cover, turned so that its SIM edge faces
the phone's LEFT side.

Depth (inside floor to T-Deck back, 23 mm with LilyGO's 11 mm T-Deck):
9 standoff + 1.6 board + 1.5 SIM holder + 1 foam + 9 battery = 22.1 mm.
The standoffs assume the stock 11 mm SMD capacitors are replaced by radial ones laid flat:
470 uF 16 V (<= 7 mm across) for C11, 100 uF 16 V (<= 5 mm) for C17.
"""
import sys

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon, box

FLOOR_Z = -25.0            # inside floor surface
WALL_IN_X, WALL_OUT_X = -2.0, -4.0   # left side wall, inside and outside faces

# ---- KTRON board ------------------------------------------------------------
BOARD_W, BOARD_H = 54.33, 57.23            # drawing: u across (J1 header at u=0), v down (U.FL1 at v=0)
HOLES_UV = [(3.215, 3.265), (51.115, 3.265), (3.215, 53.965), (51.115, 53.965)]
SIM_EDGE_X = -1.4          # board's SIM edge, 0.6 mm from the left wall
X0 = SIM_EDGE_X + BOARD_H  # back x of the board's U.FL1 edge (v = 0)
# Back y of the board's J3 edge (u = BOARD_W). First drawn at 98.30, just below the screw columns. Moved 7 mm
# down on 7 Nov 2026, after the dry fit: the earpiece wires come down from the top past the filled GPS-module slot
# (y 99-107), and the board and battery left them only about 1.5 mm. The battery moves down with the board, so the
# J3 pads stay at its top end. The GPS patch moved left and down to make room (see PATCH_CENTRE).
Y0 = 91.30
STANDOFF_H = 9.0           # tallest part on the component side: 470 uF laid flat (~7 mm) + ~1 mm under it + 1 mm
STANDOFF_D = 7.0
INSERT_D = 4.5             # M3 x 5 heat-set insert hole
INSERT_DEPTH = 6.0
FLARE_D = 10.0             # wider foot so the column stays stiff while the insert is heated in
FLARE_H = 2.5
PCB_T = 1.6

# ---- SIM slit -----------------------------------------------------------------
SIM_CARD_U = 14.6          # card centre line across the board (holder spans u 7.3-21.9 on KTRON's drawing)
CARD_ABOVE_BOARD = 0.75    # card mid-plane above the solder side, standard 1.5 mm push-push holder
SLIT_W, SLIT_H = 15.0, 1.8         # inside opening (card is 12 x 0.8 mm)
SLIT_FLARE = 0.6                   # extra on every side at the outside face, as a lead-in

# ---- SIM direction picture, engraved beside the slit ------------------------------------------------------
# A micro-SIM silhouette (12 x 15 mm card, drawn 6.0 x 7.5 mm) with its cut corner and a raised arrow pointing
# up, on the flat left wall beside the slit, on the phone-top side, centred on the slit's height. (Under the slit
# the wall is flat for only 3 mm before it curves into the back's rounded edge, which spoiled a first version.)
# The picture is the card as it should look going in, with the phone screen-up: its top edge goes in first, the
# face you see is the face that is UP (the printed side; the gold contacts face down, toward the KTRON board under
# the card), and the cut corner is on the outer end, toward the phone's bottom (bottom-right as you look at the
# left side). Checked on 7 Nov 2026: KTRON's photo, and the card read only once its cut corner went in last, on
# the holder's latch side, which faces the phone's bottom here.
SIM_ICON_W, SIM_ICON_H = 6.0, 7.5  # along y (the card's 12 mm leading edge) and z (its 15 mm length)
SIM_ICON_GAP = 1.6                 # wall left between the slit's outer flare and the picture, along the wall
SIM_ICON_CUT = 2.0                 # the cut corner (exaggerated: the real one would be 1.5 mm here)
SIM_ICON_DEPTH = 0.8               # into the flat wall (2 mm thick)


# ---- Network LED window --------------------------------------------------------
# KTRON's NETLIGHT LED (0805, next to T1 and its 220 ohm resistor R1) is on the component side, so it faces the
# back cover from 9 mm up. A printed light tube runs from the floor to 1.6 mm under the board, and a 1.6 mm hole
# goes through the cover. The hole sits on the flat floor of the decorative groove (x 53-55, 1 mm thick there),
# just beside the LED; the tube is centred between the two so it covers both. Position from KTRON's photo (+-0.5 mm).
NETLIGHT_UV = (45.6, 3.58)
LED_TUBE_ID, LED_TUBE_OD = 3.6, 5.6
LED_TUBE_TOP = 7.4         # above the floor
LED_HOLE_D = 1.6
LED_HOLE_X = 53.9


# ---- Old GPS-module slot, back half ---------------------------------------------------
# The GPS version's module slot runs from the front's earpiece pocket up into the back: x 25.8-42.2,
# y 100-106.1, from the block's underside (z -10.2) to its roof (z -20.2). The earpiece holder only fills
# the front's part, so the back's part is filled solid by copying the block's cross-section from just
# beside the slot (x 24, between the slot and the left case-screw boss).
GPS_SLOT_SLICE_X = 24.0
GPS_SLOT_FILL_X = (24.8, 43.2)               # 1 mm into each side wall, past the slot's edge chamfers
GPS_SLOT_CLIP = (99.0, -21.0, 107.0, -9.0)   # y0, z0, y1, z1 of the part of the cross-section that is copied


# ---- Outside: cat head replaced by the rushiWorks logo -----------------------------------
# The Outside Cat edition has a cat-head outline engraved 1 mm deep (z -27..-26) near the top of the cover,
# above three shortened grooves. It is filled flush, keeping clear of the two screw countersinks, and the
# logo is engraved 1 mm deep in the same clear area. It reads normally from behind the phone held upright
# (right = -x, up = +y).
CAT_FILL_BOX = (17.0, 69.5, 51.0, 102.0)       # x0, y0, x1, y1: covers the cat, no grooves inside
COUNTERSINKS = ((19.5, 102.85), (48.5, 102.85))
COUNTERSINK_KEEP_R = 3.4
OUTER_Z = -27.0
BACK_LOGO_CENTRE = (34.0, 83.75)               # between the side grooves, above the shortened ones
BACK_LOGO_WIDTH = 24.0
BACK_LOGO_DEPTH = 1.0

# ---- Inside floor: Alley Cat's engraved cat head and "Alley Chat TD1 X" text (0.2-0.4 mm deep, x 12-56,
# y 15-85) are filled flat. The designer is credited by the cat + GPS-pin badge kept on the front's top edge
# and in the README. The patch only fills below the flat floor (z = -25.0), inside its flat area.
INSIDE_FILL = (4.0, 10.5, 64.0, 98.5)         # x0, y0, x1, y1, within the flat floor (x 3.3-64.7, y 9.8-99.2)
INSIDE_FILL_Z = (-25.45, FLOOR_Z)


def board_to_back(u, v):
    """Board drawing coords (u, v) -> back (x, y)."""
    return X0 - v, Y0 - (BOARD_W - u)


# ---- GPS patch (KTRON KSTA1417), measured ----------------------------------
# 26 x 26 mm board, 25 x 25 x 4 mm ceramic (sits slightly crooked), no mounting holes,
# cable leaves the board from the middle of one side, 95 mm long.
# Moved from (21.5, 26.0) on 7 Nov 2026: 5 mm left and 4 mm down, the furthest it can go into the bottom-left corner
# with the ceramic still resting flat on its pads (floor rise under it <= 0.4 mm; the patch board clears the curve).
# The fence merges into the curved corner. This lets the modem board come 7 mm down, and puts about 5 mm more
# between the patch and the internal 4G sticker antenna along the right side (about 28 mm, edge to edge).
PATCH_CENTRE = (16.5, 22.0)
PATCH_PCB = 26.0
OPENING = 27.0             # room for the board and a slightly rotated ceramic
FENCE_T = 1.2
CERAMIC_H = 4.0
AIR_GAP = 0.5              # the ceramic rests on four small pads, just off the cover
PAD = 3.0                  # pad size, placed under the ceramic near its corners
PAD_OFFSET = 9.5           # pad centres from the patch centre
FENCE_H = 7.0              # above the floor: 0.5 gap + 4 ceramic + 1.6 board + ~0.9
CABLE_NOTCH_W = 4.0
CABLE_NOTCH_FROM = 4.2     # notch bottom above the floor (just under the patch board)


def prism_z(poly, z0, z1):
    m = trimesh.creation.extrude_polygon(poly, height=z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def prism_x(poly_yz, x0, x1):
    """Extrude a polygon drawn in (y, z) along x, from x0 to x1."""
    m = trimesh.creation.extrude_polygon(poly_yz, height=x1 - x0)
    m.apply_transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float))
    return m


def fill_gps_slot(back):
    """Solid block over the back's half of the old GPS-module slot, copied from the cross-section beside it."""
    from shapely.ops import polygonize, unary_union
    segs = trimesh.intersections.mesh_plane(back, [1, 0, 0], [GPS_SLOT_SLICE_X, 0, 0])
    lines = [LineString([(round(a[1], 6), round(a[2], 6)), (round(b[1], 6), round(b[2], 6))]) for a, b in segs]
    section = unary_union(list(polygonize(unary_union(lines))))
    block = section.intersection(box(*GPS_SLOT_CLIP))
    return [prism_x(g, *GPS_SLOT_FILL_X) for g in getattr(block, "geoms", [block]) if g.area > 0.01]


def standoffs(scale=1.0):
    """Standoffs at the board's true hole spacing. With scale != 1 the cover is larger: the group of four moves with
    it (its centre is scaled), and the floor, wall and heights follow the larger cover, but the spacing and the
    insert holes stay true."""
    adds, cuts = [], []
    floor_z, wall_in_x, height = FLOOR_Z * scale, WALL_IN_X * scale, STANDOFF_H * scale
    base_z = floor_z - 0.6                     # sink into the 2 mm floor (outer grooves start at -26)
    top_z = floor_z + height
    k = FLARE_D / (FLARE_D - STANDOFF_D)
    pts = [board_to_back(u, v) for u, v in HOLES_UV]
    gx, gy = np.mean(pts, axis=0)
    for x, y in pts:
        x, y = gx * scale + (x - gx), gy * scale + (y - gy)
        adds.append(prism_z(Point(x, y).buffer(STANDOFF_D / 2, quad_segs=24), base_z, top_z))
        foot = trimesh.creation.cone(radius=FLARE_D / 2, height=FLARE_H * k, sections=48)
        foot = trimesh.boolean.intersection([foot, trimesh.creation.box(bounds=[[-6, -6, 0], [6, 6, FLARE_H]])],
                                            engine="manifold")
        foot.apply_translation([x, y, floor_z - 0.01])
        adds.append(foot)
        adds.append(prism_z(Point(x, y).buffer(FLARE_D / 2, quad_segs=24), base_z, floor_z))
        if x < 10:   # columns next to the left wall: join them to it, no thin crevice
            adds.append(prism_z(box(wall_in_x - 0.5, y - STANDOFF_D / 2, x, y + STANDOFF_D / 2), base_z, top_z))
        cuts.append(prism_z(Point(x, y).buffer(INSERT_D / 2, quad_segs=24), top_z - INSERT_DEPTH, top_z + 1))
    return adds, cuts


def sim_slit():
    _, yc = board_to_back(SIM_CARD_U, BOARD_H)
    zc = FLOOR_Z + STANDOFF_H + PCB_T + CARD_ABOVE_BOARD
    pts = []
    for x, w, h in ((WALL_IN_X + 0.1, SLIT_W, SLIT_H),
                    (WALL_OUT_X - 0.6, SLIT_W + 2 * SLIT_FLARE * 1.3, SLIT_H + 2 * SLIT_FLARE * 1.3)):
        for sy in (-1, 1):
            for sz in (-1, 1):
                pts.append([x, yc + sy * w / 2, zc + sz * h / 2])
    funnel = trimesh.convex.convex_hull(np.array(pts))
    straight = trimesh.creation.box(bounds=[[WALL_IN_X - 0.2, yc - SLIT_W / 2, zc - SLIT_H / 2],
                                            [WALL_IN_X + 0.6, yc + SLIT_W / 2, zc + SLIT_H / 2]])
    return [funnel, straight], (yc, zc)


def sim_icon(yc, zc):
    """Recessed micro-SIM silhouette with a raised arrow, on the outside of the left wall beside the slit."""
    t = (WALL_IN_X + 0.1 - WALL_OUT_X) / (WALL_IN_X + 0.1 - (WALL_OUT_X - 0.6))   # flare at the wall face
    slit_end = yc + SLIT_W / 2 + SLIT_FLARE * 1.3 * t
    cy = slit_end + SIM_ICON_GAP + SIM_ICON_W / 2                 # +y = toward the phone's top
    top, bot = zc + SIM_ICON_H / 2, zc - SIM_ICON_H / 2
    l, r = cy + SIM_ICON_W / 2, cy - SIM_ICON_W / 2               # seen from outside, +y is on the left
    c = SIM_ICON_CUT
    card = Polygon([(l, top), (r, top), (r, bot + c), (r + c, bot), (l, bot)])   # cut corner bottom-right
    card = card.buffer(-0.35, join_style=1).buffer(0.35, join_style=1)            # slightly rounded corners
    head_w, head_h, stem_w = 3.2, 2.0, 1.1
    tip, base = top - 0.8, top - 0.8 - head_h
    arrow = Polygon([(cy, tip), (cy + head_w / 2, base), (cy + stem_w / 2, base), (cy + stem_w / 2, bot + 0.9),
                     (cy - stem_w / 2, bot + 0.9), (cy - stem_w / 2, base), (cy - head_w / 2, base)])
    shape = card.difference(arrow)
    return [prism_x(g, WALL_OUT_X - 1.0, WALL_OUT_X + SIM_ICON_DEPTH) for g in getattr(shape, "geoms", [shape])]


def led_window():
    lx, ly = board_to_back(*NETLIGHT_UV)
    cx = (lx + LED_HOLE_X) / 2
    ring = Point(cx, ly).buffer(LED_TUBE_OD / 2, quad_segs=24).difference(Point(cx, ly).buffer(LED_TUBE_ID / 2, quad_segs=24))
    adds = [prism_z(ring, FLOOR_Z - 0.6, FLOOR_Z + LED_TUBE_TOP)]
    cuts = [prism_z(Point(cx, ly).buffer(LED_TUBE_ID / 2, quad_segs=24), FLOOR_Z + 0.01, FLOOR_Z + LED_TUBE_TOP + 1),
            prism_z(Point(LED_HOLE_X, ly).buffer(LED_HOLE_D / 2, quad_segs=16), FLOOR_Z - 3.0, FLOOR_Z + 0.05)]
    return adds, cuts


def trace_logo(path):
    """Trace a black-on-white logo image into shapely polygons (image pixels, y up)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image, ImageFilter
    from shapely.ops import unary_union
    img = Image.open(path).convert("L").filter(ImageFilter.GaussianBlur(1.2))
    ink = 1.0 - np.asarray(img, float) / 255.0
    fig, ax = plt.subplots()
    cs = ax.contour(ink[::-1], levels=[0.5])
    plt.close(fig)
    rings = [Polygon(r) for p in cs.get_paths() for r in p.to_polygons() if len(r) > 3]
    shape = None
    for r in sorted(rings, key=lambda q: -q.area):       # rings inside others (the R's counter) are holes
        r = r.buffer(0)
        shape = r if shape is None else (shape.difference(r) if shape.contains(r) else shape.union(r))
    return unary_union(shape).simplify(0.25)


def back_logo(logo_path):
    from shapely.affinity import affine_transform
    x0, y0, x1, y1 = CAT_FILL_BOX
    patch = box(x0, y0, x1, y1)
    for cx, cy in COUNTERSINKS:
        patch = patch.difference(Point(cx, cy).buffer(COUNTERSINK_KEEP_R, quad_segs=24))
    adds = [prism_z(patch, OUTER_Z, OUTER_Z + 1.1),
            prism_z(box(*INSIDE_FILL), *INSIDE_FILL_Z)]
    logo = trace_logo(logo_path)
    lx0, ly0, lx1, ly1 = logo.bounds
    s = BACK_LOGO_WIDTH / (lx1 - lx0)
    cx, cy = BACK_LOGO_CENTRE
    logo_xy = affine_transform(logo, [-s, 0, 0, s, cx + s * (lx0 + lx1) / 2, cy - s * (ly0 + ly1) / 2])
    cuts = [prism_z(g, OUTER_Z - 1.0, OUTER_Z + BACK_LOGO_DEPTH) for g in getattr(logo_xy, "geoms", [logo_xy])]
    return adds, cuts


def patch_cradle():
    adds, cuts = [], []
    cx, cy = PATCH_CENTRE
    base_z = FLOOR_Z - 0.6
    inner, outer = OPENING, OPENING + 2 * FENCE_T
    ring = box(cx - outer / 2, cy - outer / 2, cx + outer / 2, cy + outer / 2).difference(
        box(cx - inner / 2, cy - inner / 2, cx + inner / 2, cy + inner / 2))
    adds.append(prism_z(ring, base_z, FLOOR_Z + FENCE_H))
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = cx + sx * PAD_OFFSET, cy + sy * PAD_OFFSET
            adds.append(prism_z(box(px - PAD / 2, py - PAD / 2, px + PAD / 2, py + PAD / 2), base_z, FLOOR_Z + AIR_GAP))
    h = inner / 2
    w = CABLE_NOTCH_W / 2
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nx, ny = cx + dx * (h + FENCE_T / 2), cy + dy * (h + FENCE_T / 2)
        notch = box(nx - (FENCE_T if dx else w), ny - (FENCE_T if dy else w),
                    nx + (FENCE_T if dx else w), ny + (FENCE_T if dy else w))
        cuts.append(prism_z(notch, FLOOR_Z + CABLE_NOTCH_FROM, FLOOR_Z + FENCE_H + 1))
    return adds, cuts


def main(src, dst, picture=None, logo_path=None, scale=1.0):
    back = trimesh.load(src, force="mesh")
    assert back.is_watertight
    if logo_path is None:
        import os
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "rushi-logo.jpg")
    a0, c0 = back_logo(logo_path)
    back = trimesh.boolean.union([back] + a0, engine="manifold")          # fill both cats first
    a1, c1 = standoffs(scale)
    a2, c2 = patch_cradle()
    c3, (slit_y, slit_z) = sim_slit()
    c3 += sim_icon(slit_y, slit_z)
    a4, c4 = led_window()
    a5 = fill_gps_slot(back)
    # Nothing added may stick out of the cover. Its outer edges are rounded, so near the floor the outside face curves in
    # (at the left wall: x = -2.9 at mid-height, -1.3 at the floor), and the left standoffs' 10 mm feet would poke through.
    # Trim every addition to the original cover's outer shape (its convex hull; the cover's outline is convex).
    # With --scale, everything except the standoffs is built at true size and then scaled about the origin with the
    # shell; the standoffs (a1, c1) are made directly in the scaled cover, at the board's true spacing.
    def grow(meshes):
        if scale == 1.0:
            return meshes
        out = []
        for m in meshes:
            m = m.copy(); m.apply_scale(scale); out.append(m)
        return out
    back, = grow([back])
    a2, a4, a5, c0, c2, c3, c4 = (grow(x) for x in (a2, a4, a5, c0, c2, c3, c4))
    envelope = back.convex_hull
    adds = [trimesh.boolean.intersection([m, envelope], engine="manifold") for m in a1 + a2 + a4 + a5]
    out = trimesh.boolean.union([back] + [m for m in adds if len(m.faces)], engine="manifold")
    out = trimesh.boolean.difference([out, trimesh.boolean.union(c0 + c1 + c2 + c3 + c4, engine="manifold")], engine="manifold")
    assert out.is_watertight, "result is not watertight"
    out.export(dst)
    print(f"added {out.volume - back.volume:.1f} mm^3, watertight {out.is_watertight}, "
          f"bodies {len(out.split(only_watertight=False))}; SIM slit centre y {slit_y:.2f}, z {slit_z:.2f} "
          f"({slit_z - FLOOR_Z:.2f} mm above the floor, {-9.0 - slit_z:.2f} mm below the rim, before scaling); scale {scale}")
    if picture and scale == 1.0:
        draw_layout(out, picture)


def draw_layout(mesh, path):
    """Inside view of the back with the board, its parts and the patch drawn on top."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon as MPoly

    fig, ax = plt.subplots(figsize=(8, 11), dpi=110)
    for z, col in ((-12.0, "0.6"), (FLOOR_Z + 2.0, "0.25")):
        for s in trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z]):
            ax.plot(s[:, 0], s[:, 1], color=col, lw=0.7)

    def bpoly(pts, **kw):
        ax.add_patch(MPoly([board_to_back(u, v) for u, v in pts], closed=True, **kw))

    bpoly([(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)], fill=False, ec="tab:blue", lw=1.5)
    bpoly([(7.3, 41.0), (21.9, 41.0), (21.9, 57.23), (7.3, 57.23)], fc="tab:orange", alpha=0.35, ec="tab:orange")
    for (u, v, r, name) in [(44.4, 28.8, 5.4, "C11\n(470 µF\nflat)"), (42.85, 48.1, 4.45, "C17")]:
        x, y = board_to_back(u, v)
        ax.add_patch(Circle((x, y), r, fc="tab:red", alpha=0.18, ec="tab:red", ls="--"))
        ax.text(x, y, name, ha="center", va="center", fontsize=6)
    for (u, v, name) in [(24.8, 3.6, "U.FL1 (4G)"), (2.2, 41.5, "U.FL2 (GPS)")]:
        x, y = board_to_back(u, v)
        ax.plot(x, y, "s", color="tab:green")
        ax.text(x, y - 2.5, name, ha="center", fontsize=7, color="tab:green")
    _, yc = board_to_back(SIM_CARD_U, BOARD_H)
    ax.plot([-4.5, -4.5], [yc - SLIT_W / 2, yc + SLIT_W / 2], color="tab:orange", lw=4)
    ax.annotate("SIM slit (in the wall)", (-4.5, yc), (8, yc - 12), fontsize=7, color="tab:orange",
                arrowprops=dict(arrowstyle="->", color="tab:orange"))
    lx, ly = board_to_back(*NETLIGHT_UV)
    ax.add_patch(Circle(((lx + LED_HOLE_X) / 2, ly), LED_TUBE_OD / 2, fill=False, ec="tab:green", lw=1.2))
    ax.plot(lx, ly, "*", color="tab:green", ms=8)
    ax.text(lx - 3, ly - 4.5, "network LED\n+ window", ha="center", fontsize=6.5, color="tab:green")
    cx, cy = PATCH_CENTRE
    hp = PATCH_PCB / 2
    ax.add_patch(MPoly([(cx - hp, cy - hp), (cx + hp, cy - hp), (cx + hp, cy + hp), (cx - hp, cy + hp)],
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
    args = sys.argv[1:]
    scale = 1.0
    if args and args[0] == "--scale":
        scale = float(args[1]); args = args[2:]
    main(*args, scale=scale)
