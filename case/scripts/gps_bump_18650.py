"""The 18650 version's GPS bump: the top edge's middle, where the badge was, grows into a block that houses the Eteily
GPS antenna, used by make_front_18650.py and make_back_18650.py (and make_18650_pictures.py).

Why: the antenna arrived on 15 Nov 2026 9 mm thick (a metal cap over its amplifier covers almost the whole back of its
board), and the top slot behind the badge had room for about 6 mm. Rather than make the phone 3 mm longer, the owner
chose a bump in the middle of the top edge (docs/design-18650.md, "GPS antenna"):
- the antenna stands on its edge as before, on the earpiece holder's roof, ceramic toward the top edge, its cap toward
  the T-Deck with 0.9 mm left for the earpiece wires; the room for it runs on out through the top wall into the bump;
- the bump: 22.7 mm wide (the slot plus a 1.6 mm wall each side), from 1.5 mm under the antenna's foot to flush with
  the back's outside face (21.5 mm), standing 3.5 mm out from the top edge, with 1.3 mm of plastic over the ceramic.
  Its corners seen end-on are rounded (2.5 mm) and its face has a 0.8 mm chamfer all round;
- the halves split it at their joint (front's part 14 mm, back's 7.5 mm), and it carries on the joint's groove: Alley
  Cat rounds each half's outside edge in by about 0.4 mm over the last 0.5 mm before the joint (measured at the top
  edge), so the bump's outline comes in to 0.4 mm at the joint too;
- markings, engraved 0.5 mm: the owner's logo on the front's part, "rushiworks" on the back's part, both reading with
  the phone lying screen-up, i.e. their tops toward the screen side, as Alley Cat's badge reads (the owner's choice);
- a notch for the antenna's cable in the front's slot wall on the phone's left (see cable_notch).

Everything here is in the FRONT's coordinates at 100 % (make_front.py): y along the phone (the top edge at 108), z
from the screen side (-14.7) to the back's outside face (11.8), the halves meeting at z 4.3. The back's script turns
the pieces into its own coordinates with TO_BACK (x_back = -x - 10, z_back = 0.8 - z; it is its own inverse).
"""
import os

import numpy as np
import trimesh
from shapely.affinity import affine_transform
from shapely.geometry import Polygon, box as sbox

TO_BACK = np.array([[-1, 0, 0, -10], [0, 1, 0, 0], [0, 0, -1, 0.8], [0, 0, 0, 1]], float)

# ---- where things are (front coordinates) --------------------------------------------------------------------
SLOT_X = (-53.75, -34.25)       # the antenna's slot across the phone: the back's TOPGPS_X (24.25-43.75) turned over
XC = sum(SLOT_X) / 2
TDECK_TOP = 100.0               # the T-Deck's top edge
TOP_EDGE = 108.0                # the case's top edge (outside face)
ROOF_Z = -8.2                   # the earpiece holder's roof and the steps beside it: the antenna stands here
JOINT_Z = 4.3                   # where the halves meet (the back's rim)
BACK_OUT = 11.8                 # the back's outside face
CAVITY_TOP = 10.9               # the room's ceiling: the back's 0.9 mm pocket floor, 0.9 mm under its outside face

# ---- the antenna and its room --------------------------------------------------------------------------------
ANT_T = 9.0                     # cap 4 + board 1 + ceramic 4 (measured 9 mm overall, 15 Nov 2026)
WIRES = 0.9                     # left between the T-Deck's top edge and the cap, for the earpiece wires
GAP, WALL = 0.3, 1.3            # play in front of the ceramic, and the bump's wall over it
ANT_BACK = TDECK_TOP + WIRES    # 100.9
ANT_FACE = ANT_BACK + ANT_T     # 109.9
CAVITY_Y = (100.6, ANT_FACE + GAP)   # to 110.2
BUMP_Y = CAVITY_Y[1] + WALL          # 111.5: 3.5 mm out from the top edge

# ---- the bump --------------------------------------------------------------------------------------------------
SIDE = 1.6
BX = (SLOT_X[0] - SIDE, SLOT_X[1] + SIDE)       # 22.7 mm wide
BZ = (ROOF_Z - 1.5, BACK_OUT)                   # 21.5 mm tall
R, CH = 2.5, 0.8                                # corner radius seen end-on; chamfer round the face
FRONT_FROM_Y = TOP_EDGE - 1.0                   # the front's part starts inside its top wall (inside face 107.5)
BACK_FROM_Y = 106.0                             # the back's part starts inside its top wall (106.1), so no slit is
                                                # left by the back's rounded top edge; the front's lip stops at 105.9
GV_D, GV_H = 0.4, 0.5                           # the joint's groove: 0.4 deep, over 0.5 mm each side of the joint

# ---- the antenna's cable --------------------------------------------------------------------------------------
# It leaves the middle of one side of the board, on the cap's side. In the 19.5 mm slot a board under 19 mm leaves
# only about 0.5 mm beside it, too little for the 1.13 mm cable to come out and bend. So the antenna is pushed
# against the slot's right-hand side (the phone's right), leaving about 1 mm on the left, and a notch 1 mm into the
# left-hand wall gives the cable 2 mm: out of the board, one sharp bend, then along the notch toward the T-Deck and
# out over the T-Deck's back toward the cell's left end. The notch stops at 1 mm because the front's case-screw
# insert is beside it: 1.25 mm of plastic is left to its hole (the wall there was 2.25 mm).
BOARD_W = 18.5                  # for the cable's height: the middle of the board's side
CABLE_Z = ROOF_Z + BOARD_W / 2  # 1.05
NOTCH_D, NOTCH_H = 1.0, 2.0     # into the wall, and tall (the cable is 1.13 mm)
NOTCH_Y = (99.5, 105.2)         # from past the slot's end at the T-Deck to just past where the cable leaves

# ---- markings ----------------------------------------------------------------------------------------------------
MARK_DEPTH, MARK_MARGIN = 0.5, 0.8
LOGO_GROW = 0.05                # thin strokes widened 0.05 mm each side, as on the badge
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "rushi-logo.jpg")
NAME, NAME_FONT = "rushiworks", "DejaVu Sans"   # DejaVu Sans comes with matplotlib, so the result is reproducible


def _rounded_rect(x0, x1, z0, z1, r):
    return sbox(x0 + r, z0 + r, x1 - r, z1 - r).buffer(r, quad_segs=10)


def _slab(poly, y0, y1):
    """A prism of an (x, z) outline from y0 to y1."""
    m = trimesh.creation.extrude_polygon(poly, y1 - y0)
    m.apply_transform(np.array([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0], [0, 0, 0, 1]], float))
    if m.volume < 0:
        m.invert()
    return m


def _block(y_from):
    """The whole bump from y_from out: its outline carried out to the chamfer, then the chamfered face."""
    outline = _rounded_rect(BX[0], BX[1], BZ[0], BZ[1], R)
    inset = _rounded_rect(BX[0] + CH, BX[1] - CH, BZ[0] + CH, BZ[1] - CH, R - CH)
    face = trimesh.convex.convex_hull(np.vstack([_slab(outline, BUMP_Y - CH - 0.01, BUMP_Y - CH).vertices,
                                                 _slab(inset, BUMP_Y - 0.01, BUMP_Y).vertices]))
    return trimesh.boolean.union([_slab(outline, y_from, BUMP_Y - CH), face], engine="manifold")


def _joint_outline(y0, inset=0.0):
    """The bump's outline across the phone (x, y) at the joint, brought in by inset on its outside (sides and face)."""
    return Polygon([(BX[0] + inset, y0), (BX[1] - inset, y0), (BX[1] - inset, BUMP_Y - CH - inset * 0.4),
                    (BX[1] - CH - inset * 0.6, BUMP_Y - inset), (BX[0] + CH + inset * 0.6, BUMP_Y - inset),
                    (BX[0] + inset, BUMP_Y - CH - inset * 0.4)])


def _groove_band(y0, z_far):
    """The bump between the joint and z_far, with the groove: its full outline at z_far, GV_D in at the joint."""
    def layer(poly, z):
        return np.array([(x, y, z) for x, y in poly.exterior.coords[:-1]])
    return trimesh.convex.convex_hull(np.vstack([layer(_joint_outline(y0), z_far),
                                                 layer(_joint_outline(y0, GV_D), JOINT_Z)]))


def front_part():
    """The front's share of the bump (z up to the joint), with its half of the groove."""
    lower = trimesh.creation.box(bounds=[[-90, 90, -30], [10, 130, JOINT_Z - GV_H]])
    body = trimesh.boolean.intersection([_block(FRONT_FROM_Y), lower], engine="manifold")
    return trimesh.boolean.union([body, _groove_band(FRONT_FROM_Y, JOINT_Z - GV_H)], engine="manifold")


def back_part():
    """The back's share of the bump (z from the joint), with its half of the groove. Front coordinates."""
    upper = trimesh.creation.box(bounds=[[-90, 90, JOINT_Z + GV_H], [10, 130, 30]])
    body = trimesh.boolean.intersection([_block(BACK_FROM_Y), upper], engine="manifold")
    return trimesh.boolean.union([body, _groove_band(BACK_FROM_Y, JOINT_Z + GV_H)], engine="manifold")


def room():
    """The antenna's room, from the T-Deck's top edge out to the bump's wall, the holder's roof up to the back's
    pocket floor. Cut from both halves."""
    return trimesh.creation.box(bounds=[[SLOT_X[0], CAVITY_Y[0], ROOF_Z], [SLOT_X[1], CAVITY_Y[1], CAVITY_TOP]])


def cable_notch():
    """The notch for the antenna's cable, in the slot's wall on the phone's left (front's +x side). Front only."""
    x = SLOT_X[1]
    return trimesh.creation.box(bounds=[[x - 0.01, NOTCH_Y[0], CABLE_Z - NOTCH_H / 2],
                                        [x + NOTCH_D, NOTCH_Y[1], CABLE_Z + NOTCH_H / 2]])


def _prism_y(poly, y0, y1):
    return _slab(poly, y0, y1)


def _fit(shape, x0, x1, z0, z1):
    """A drawing (x right, y up) fitted into a face (x0..x1, z0..z1) with MARK_MARGIN round it, read from outside the
    top edge with the screen side up: right = +x, up = -z."""
    sx0, sy0, sx1, sy1 = shape.bounds
    k = min((x1 - x0 - 2 * MARK_MARGIN) / (sx1 - sx0), (z1 - z0 - 2 * MARK_MARGIN) / (sy1 - sy0))
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    return affine_transform(shape, [k, 0, 0, -k, cx - k * (sx0 + sx1) / 2, cz + k * (sy0 + sy1) / 2])


def _cuts(shape):
    return [_prism_y(p, BUMP_Y - MARK_DEPTH, BUMP_Y + 1.0) for p in getattr(shape, "geoms", [shape]) if p.area > 1e-4]


def front_face():
    """The flat of the front's part of the face: inside the chamfer, the corners and the groove."""
    x0, x1, z0, z1 = BX[0] + CH, BX[1] - CH, BZ[0] + CH, JOINT_Z - GV_H
    rr = R - CH
    return sbox(x0 + rr, z0 + rr, x1 - rr, z1).buffer(rr, quad_segs=12).intersection(sbox(x0, z0, x1, z1))


def back_face():
    x0, x1, z0, z1 = BX[0] + CH, BX[1] - CH, JOINT_Z + GV_H, BZ[1] - CH
    rr = R - CH
    return sbox(x0 + rr, z0, x1 - rr, z1 - rr).buffer(rr, quad_segs=12).intersection(sbox(x0, z0, x1, z1))


def logo_cuts():
    """The owner's logo, engraved in the front's part (front coordinates)."""
    from make_back import trace_logo
    face = front_face()
    x0, z0, x1, z1 = face.bounds
    art = _fit(trace_logo(LOGO_PATH), x0, x1, z0, z1)
    art = art.buffer(LOGO_GROW, join_style=1).intersection(face.buffer(-0.3))
    return _cuts(art)


def name_cuts():
    """"rushiworks", engraved in the back's part (front coordinates)."""
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath
    tp = TextPath((0, 0), NAME, size=1.0, prop=FontProperties(family=NAME_FONT, weight="normal"))
    shape = Polygon()
    for ring in tp.to_polygons():                     # outlines and holes alternate, as in the font
        if len(ring) > 3:
            shape = shape.symmetric_difference(Polygon(ring).buffer(0))
    face = back_face()
    x0, z0, x1, z1 = face.bounds
    return _cuts(_fit(shape, x0, x1, z0, z1).intersection(face.buffer(-0.3)))


def to_back(mesh):
    """A piece in front coordinates, turned into the back's."""
    m = mesh.copy()
    m.apply_transform(TO_BACK)
    if m.volume < 0:
        m.invert()
    return m
