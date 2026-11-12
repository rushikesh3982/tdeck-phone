"""18650 version of the back (option 3 of docs/slim-layout-plan.md).

Built from Alley Cat's slim S back ("Alley Chat TD1 S Inside Cat Edition.stl"), which mates with the same front:
- 0.5 mm deeper than her S back (a slice copied from its straight walls), so the space behind the T-Deck is 12.7 mm:
  8 mm standoffs + 1.6 mm board + 1.5 mm SIM holder, with about 1.6 mm left for the wire joints on top.
- a grip ridge across the top of the outside, holding one 18650 cell (LG MJ1, 65.2 x 18.5 mm) lying across the phone;
- the KTRON modem board low down, on four 8 mm standoffs with M3 heat-set inserts, leaving the same 10.7 mm of flat
  floor below it as beside it on the right: an L-shaped band, along the bottom and up the right side, kept empty for
  a 4G antenna (the owner's choice);
- the battery contacts (the two spring contacts from an 18650 holder, their solder feet cut off) stand against the
  two end walls of the cell's channel, each between two ribs; + at the right end, - at the left, both engraved on
  the floor;
- a thin support wall along the cell's modem side, with the battery protection board (32 x 4-5 mm) glued to its
  back; the board's own nickel strips reach behind the contacts through slits, so the contacts need no soldering;
- the active GPS antenna (18 x 18 mm ceramic, its board likely about 18.5 mm) standing on its edge in the top slot, facing the phone's top edge, above the
  earpiece: the S back's gap between its two screw blocks is kept open for it, with a 0.9 mm-deep pocket in the floor
  for its top edge (0.9 mm of plastic left outside). The earpiece holder's roof is the separator below it;
- the modem's power switch (SS-12F15) on the back's right wall, just below the cell, using Alley Cat's switch slot
  and screw holes (taken from her front file);
- the network-LED light tube and window. Inside, Alley Cat's own engraved cat and "Alley Chat TD1 S" stay on the
  floor, as her credit. The outside keeps her grooves, with no logo; each now ends 2 mm
  short of the grip at the top and 2 mm short of the bottom edge's rounding at the bottom.

The front's changes are in make_front_18650.py and the low earpiece holder in make_earpiece_holder_18650.py. The design
as a whole is described in docs/design-18650.md.

Wires pass the cell's ends between the end walls and the cell, below the contacts' springs (about 3 mm of room), so
they need no grooves of their own.

Usage:
    python make_back_18650.py "<Alley Chat TD1 S Inside Cat Edition.stl>" "<...Standard Front GPS Inserts.stl>" <output.stl>
    python make_back_18650.py --scale 1.01 "<...S Inside Cat Edition.stl>" "<...Front GPS Inserts.stl>" <output.stl>
    python make_back_18650.py --scale 1.01 --stand ...   (saved standing on its top edge, as it prints)

Coordinates are the S back's own, after the 0.5 mm slice: outside face z = -11, inside floor z = -9.2, rim z = -3.5
(where the front's mating face, z = 4.3 in the front's file, meets it), the T-Deck's back at z = +3.5. As in
make_back.py: +x is the phone's RIGHT side, -x its LEFT, +y the top. Assembled: x_front = -x - 10, z_front = 0.8 - z.

--scale works as in make_back.py: everything grows with the shell except the parts that must match real parts, which
are built after scaling at their true size: the four standoffs (the board's hole spacing) and the cell's channel.
"""
import os
import sys

import numpy as np
import trimesh
from shapely.affinity import translate
from shapely.geometry import MultiPoint, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_back import prism_z, prism_x  # noqa: E402

# ---- the S back and its extra depth --------------------------------------------------------------------------
OUTER_Z, FLOOR_Z = -11.0, -9.2
Z_CUT, EXTRA = -6.5, 0.5          # slice copied from the straight walls at z = -6.5 (S back's own coordinates)
RIM_Z = -4.0 + EXTRA              # -3.5
TDECK_Z = RIM_Z + 7.0             # the T-Deck's back: 7 mm above the joint, inside the front
WALL_IN = (-2.0, 70.0)            # inside faces of the side walls (back half)

# ---- KTRON board (as make_back.py, moved: below the cell) --------------------------------------------------
BOARD_W, BOARD_H = 54.33, 57.23
HOLES_UV = [(3.215, 3.265), (51.115, 3.265), (3.215, 53.965), (51.115, 53.965)]
SIM_EDGE_X = 0.3                  # the front's left wall comes in to x = 0.0 at the board's height (it is 4 mm thick
X0 = SIM_EDGE_X + BOARD_H         # there), so the board sits 1.7 mm further right than in make_back.py
Y0 = 71.3                         # J3 (top) edge. The flat floor beside the board's right edge runs 10.7 mm, to the
                                  # wall's foot at x 68.25; the bottom wall's foot is at y 6.25, so the board's bottom
                                  # edge sits 10.7 mm above it, at y 16.97. (66.0 is as low as it could go.)
STANDOFF_H = 8.0                  # 470 uF laid flat measures 7 mm above the board + 1 mm
STANDOFF_D, INSERT_D, INSERT_DEPTH = 7.0, 4.5, 6.0
FLARE_D, FLARE_H = 10.0, 2.5
TIE_TOP = -6.7                    # standoff-to-wall ties stop under the front's corner tabs (3 mm into the back, z -6.5)


def board_to_back(u, v):
    return X0 - v, Y0 - (BOARD_W - u)


# ---- 18650 cell and grip ridge --------------------------------------------------------------------------------
CELL_D, CELL_L = 18.5, 65.2       # LG MJ1 (65.15 x 18.4-18.5)
CELL_GAP = 0.25                   # all round, in the channel
CELL_Y = 88.0                     # axis, across the phone (along x)
CELL_Z = TDECK_Z - 0.5 - CELL_D / 2   # top of the cell 0.5 mm under the T-Deck: -6.25
CHANNEL_X = WALL_IN               # the channel runs wall to wall: the contacts stand against the two end walls
# The grip, seen from the side: a circle round the cell (1.5 mm of plastic under its channel) that blends into the
# flat back through concave curves, with no crease. The curves are sized so the steepest part of the grip slopes at
# 45 degrees, so the back prints standing on its top edge without supports on the outside.
GRIP_R = CELL_D / 2 + CELL_GAP + 1.5                      # 11.0
GRIP_SLOPE = np.radians(45.0)
_H = CELL_Z - OUTER_Z                                      # 4.75: cell axis above the flat face
GRIP_BLEND_R = (GRIP_R - _H / np.cos(GRIP_SLOPE)) / (1 / np.cos(GRIP_SLOPE) - 1)              # 10.34
GRIP_HALF = np.sqrt((GRIP_R + GRIP_BLEND_R) ** 2 - (_H + GRIP_BLEND_R) ** 2)                  # 15.09
GRIP_Y = (CELL_Y - GRIP_HALF, CELL_Y + GRIP_HALF)          # 72.9-103.1: where it leaves the flat back
RIDGE_DEPTH = GRIP_R - _H                                  # 6.25: 32.75 mm phone at the grip
SCREW_RECESSES = [(19.5, 102.9), (48.5, 102.9)]            # the case screws' recesses (r 2.77), re-cut through the blend
SCREW_RECESS_R = 2.77

# ---- outside grooves: Alley Cat's seven grooves (centres x 4, 14 ... 64) are 1 mm deep, 4 mm wide at the face and
# 2 mm at the flat bottom (45-degree sides), with rounded ends of the same section. They are filled from just below
# the grip and given new rounded ends there.
GROOVE_XS = [4.0 + 10.0 * k for k in range(7)]
GROOVE_END_Y = GRIP_Y[0] - 4.0      # centre of the new top end: its tip at the face is 2 mm short of the grip (y 70.9)
# Bottom ends, lengthened to match: Alley Cat's ends sat about 4 mm from where the flat face starts to round over at
# the bottom edge; these centres put each rounded end 2 mm from it (measured to the nearest point of the curved edge).
GROOVE_OLD_BOTTOM = [14.02, 7.62, 6.02, 6.02, 6.02, 7.62, 14.02]
GROOVE_NEW_BOTTOM = [10.52, 5.48, 4.0, 4.0, 4.0, 5.48, 10.52]

# ---- battery contacts: the two spring contacts from an 18650 SMD holder (Robu), measured 12 Nov 2026: a plate 7 mm
# wide and 16 mm tall whose top is folded down into a leaf spring (5 mm deep with the plate, reaching 10 mm down),
# with a 7 mm solder foot bent out at the bottom. The foot is cut off. Each contact stands upright against an end
# wall, the fold at the top as in the holder, so the cell slides in from above over the folds. Its plate stands on a
# small seat level with the channel's floor at its lower edge, which puts its top 1.5-2.4 mm above the rim (the front
# is notched there, make_front_18650.py) and the spring's pressing part over the upper half of the + cap.
# Plate to plate is 72.0 mm at any print scale (the channel grows with the case, so in the 101 % print a 0.36 mm pad
# behind each plate takes up the difference): each spring is pressed from 4.7 to 3.1 mm (2.95 with the strip).
# Holding it, as in the holder (whose end posts have a narrow groove for each edge of the plate): two ribs on each end
# wall, 7.2 mm apart, each with a lip 0.4 mm thick that reaches 0.5 mm over the plate's front edge, 0.6 mm in front of
# the wall. The plate slides down into these grooves with the strip behind it; its lower part is stepped about 0.5 mm
# toward the wall and has small tabs bent out at its sides, so in a 0.6 mm groove it presses on both faces and holds.
# The plate's lower edge rests on a seat. A thin bar joins the two lips across the front at the top of the ribs: the
# back prints standing on its top edge, where the lip on the lower rib (the one nearer the phone's bottom) would
# otherwise start in mid-air; with the bar it prints as a short bridge from the seat up to the bar. The upper rib's
# face toward the phone's top slopes at 45 degrees. The middle of the plate stays open for its spring, and wires pass
# the cell's ends in front of the lips, below the springs (2.4 mm). The strip comes in through a thin slit in the
# lower rib.
# + goes at the right end (beside the modem switch), - at the left: both are engraved on the floor.
#
# No soldering at the contacts (the owner's idea, 12 Nov 2026): a support wall runs along the cell's modem side, and
# the protection board (Robu 1S 3A 2MOS, 32 x 4-5 mm, a nickel strip welded on each end of its chip side, 91 mm in
# all) is glued chip side to it, centred, B- to the left. Each strip runs along the wall to its end, turns past it
# along the end wall, goes through a slit in the contact's lower rib and lies behind the contact's plate, which the
# cell's spring presses onto it. The strips are only about 29.5 mm long, so the contacts sit 2 mm toward the board
# from the cell's axis (still over the + cap): each strip then needs about 27.5 mm to reach 2 mm behind its plate.
CONTACT_W = 7.0
CONTACT_DY = -2.0                               # plate centre, from the cell's axis (toward the board)
CONTACT_SPAN = WALL_IN[1] - WALL_IN[0]          # 72.0: plate to plate, kept at every scale
RIB_GAP, RIB_W, RIB_D = 7.2, 1.0, 1.0
GROOVE_D, LIP_T, LIP_OVER = 0.6, 0.4, 0.5         # groove depth (strip + plate + their bend), lip thickness and overlap
TOP_BAR_H = 1.5                                   # the bar joining the lips, at the top of the ribs
SUPPORT_T, SUPPORT_GAP, SUPPORT_END_GAP = 1.2, 0.25, 0.6   # thinnest part (at the cell's axis), gap to the cell, gap at each end for the strip
SUPPORT_TOP = RIM_Z - 1.2                        # -4.7: under the front's lip, which reaches 1 mm into the back
STRIP_Z = (FLOOR_Z, FLOOR_Z + 4.8)               # the strips' height band (the board stands on the floor)
STRIP_SLOT = 0.45                                # slit width, at the plate line
BOARD_L = 32.0                                   # protection board, centred on the cell: marks on the wall's top
POLARITY = [("-", 11.0), ("+", 62.0)]           # x of each mark's centre, on the floor in front of the wall
POLARITY_Y, POLARITY_SIZE, POLARITY_STROKE, POLARITY_DEPTH = 74.6, 3.6, 0.8, 0.4


def contact_pad(scale):
    """Thickness of the pad behind each plate that keeps the plates CONTACT_SPAN apart in a scaled case."""
    return ((WALL_IN[1] - WALL_IN[0]) * scale - CONTACT_SPAN) / 2

# ---- battery protection board (Robu 1S 3A 2MOS, measured 32 x 4-5 mm, with nickel strips at both ends): no frame,
# it lies flat on double-sided tape between the board's top edge (y 71.3) and the cell (lowest at y 78.75), at about
# x 16-48, y 73.6-78.6, clear of the two upper standoffs' feet (which reach y 73.1).

# ---- GPS antenna in the top slot ------------------------------------------------------------------------
# Alley Cat made this slot for a GPS module (15 x 15 mm antenna, e.g. the M100 Mini). The ~200 comments on her
# Printables page (read 10 Nov 2026) report it working there, with no complaints about reception.
# Size: Eteily quotes only the ceramic (18 x 18 x 4 mm). Like the old KTRON patch (sold as 25 x 25, measured
# 26 x 26 board) and FONCON's 18 mm patch (18.5 x 18.5 x 6.5 mm unit), its board is likely about 18.5 mm square.
# Height budget (front file's z): earpiece pocket floor -11.6 (lowered 0.5 mm in the 18650 front), earpiece 2.0
# (gasket pressed 0.3) and its folded contacts 1.0 + 0.2 for solder -> -8.7; holder roof 0.5 -> -8.2; up to this
# pocket's floor -> 10.9, which is z = 0.8 - 10.9 = -10.1 here: 0.9 mm above the outside face. That is 19.1 mm for
# the antenna: 0.6 mm to spare with an 18.5 mm board, 0.1 mm with a 19 mm one. The ceramic faces the
# top wall (y 106.1); the skin is not thinned further because the back's top edge is rounded right at the antenna's
# top corner (about 0.5 mm of plastic there already).
# The S back's gap between its screw blocks (x 25.8-42.2, like the front's pocket) has a shelf up to z -7.85: the
# pocket goes 2.25 mm down through it, and the gap is widened 1.55 mm into each block (3.1 mm left to the screw holes).
TOPGPS_X = (24.25, 43.75)                   # 19.5 mm: an 18.5 mm board + 0.5 each side (a slightly crooked ceramic)
TOPGPS_Y = (98.6, 106.1)                    # ceramic 4 + board 1, then 2.4 mm for its amplifier; 1.1 mm wall to the cell
TOPGPS_FLOOR = OUTER_Z + 0.9                # -10.1
# Above the grip, three outside grooves run on to y 101.5 as short stubs: the middle one (over the antenna's pocket) and
# the two at the corners are filled, so the top above the grip is plain.
GROOVE_STUBS = [(31.0, 97.0, 37.0, 103.0), (0.0, 97.0, 8.0, 103.0), (60.0, 97.0, 68.0, 103.0)]

# ---- modem power switch -------------------------------------------------------------------------------------
# On the back's right wall, just below the grip: its top end (the upper screw's countersink) lines up with where the
# grip leaves the flat back. Alley Cat's mount on her front's left wall (a recess for the
# switch's 19.7 x 5.6 mm plate, a 6.9 x 3.4 mm slot for the knob and two countersunk M2 holes 15 mm apart, centred at
# y 63.4, z 0.1 on the wall's outside face x = -6.0, with 2.58 mm from that face to the plate) is copied: its slot and
# holes, the outer 2.58 mm. This wall is 1.95 mm thick, so a pad inside carries the plate. The pad is 1.95 mm thick,
# which puts the plate 3.9 mm in from the outside face: the 4 mm knob then stands out 0.1 mm, like Alley Cat's slider
# on the T-Deck's own switch, and the plate stays 0.9 mm clear of the front's lip, which reaches 1 mm into the back
# (so the lip is whole). The pad stops 0.1 mm below that lip; the knob slot and screw holes go on through it. The
# floor's rounded corner is cleared where the plate's lower edge sits, 0.2 mm into the floor.
SWITCH_REGION = [[-8.55, 52.5, -4.0], [-5.5, 74.5, 4.25]]     # in her front's coordinates: slot and holes only
SWITCH_SRC_Y, SWITCH_SRC_Z = 63.4, 0.1
SWITCH_AT = (GRIP_Y[0] - 10.05, -6.6)                          # y, z of the knob slot's centre: the upper screw's
                                                               # countersink ends where the grip leaves the flat
                                                               # back (y 72.9); 1.4 mm of wall above the slot
SWITCH_PLATE = (19.7, 5.6, 0.5)                                # length (y), height (z), thickness
SWITCH_PAD_X = (68.1, 70.3)                                    # 1.95 mm pad on the wall's inside face (70.05)
SWITCH_PAD_TOP = RIM_Z - 1.1                                   # -4.6: 0.1 mm under the tip of the front's lip


# ---- network LED, inside text fill ----------------------------------------------------------------------
NETLIGHT_UV = (45.6, 3.58)
LED_TUBE_ID, LED_TUBE_OD = 3.6, 5.6
LED_HOLE_D, LED_HOLE_X = 1.6, 54.0          # in the middle of the outside groove at x 52-56 (floor 0.8 mm there)


def deepen(sback):
    """Copy the slice at Z_CUT and insert EXTRA mm there: the walls and the top block grow, the rest moves up."""
    lo = trimesh.boolean.intersection([sback, trimesh.creation.box(bounds=[[-10, -10, -20], [80, 120, Z_CUT]])],
                                      engine="manifold")
    hi = trimesh.boolean.intersection([sback, trimesh.creation.box(bounds=[[-10, -10, Z_CUT], [80, 120, 5]])],
                                      engine="manifold")
    hi.apply_translation([0, 0, EXTRA])
    sec = sback.section(plane_origin=[0, 0, Z_CUT], plane_normal=[0, 0, 1])
    planar, T = sec.to_2D()
    slabs = []
    for poly in planar.polygons_full:
        m = trimesh.creation.extrude_polygon(poly, height=EXTRA)
        m.apply_transform(T)
        slabs.append(m)
    return trimesh.boolean.union([lo, hi] + slabs, engine="manifold")


def grip_z(y):
    """Height of the grip's outside surface at y (z, outward is down)."""
    d = abs(y - CELL_Y)
    if d >= GRIP_HALF:
        return OUTER_Z
    t = GRIP_R / (GRIP_R + GRIP_BLEND_R)          # where the circle hands over to the blend curve
    if d <= GRIP_HALF * t:
        return CELL_Z - np.sqrt(GRIP_R ** 2 - d ** 2)
    c = GRIP_HALF                                  # blend curve's centre, outside the part
    return (OUTER_Z - GRIP_BLEND_R) + np.sqrt(max(GRIP_BLEND_R ** 2 - (d - c) ** 2, 0.0))


def _ray_hits(poly, c, angles):
    """Where rays from c (inside the convex polygon) leave it, one point per angle."""
    xy = np.asarray(poly.exterior.coords)[:-1]
    a, b = xy, np.roll(xy, -1, axis=0)
    e = b - a                                            # edges
    d = np.c_[np.cos(angles), np.sin(angles)]            # ray directions
    w = a - c
    den = d[:, None, 0] * e[None, :, 1] - d[:, None, 1] * e[None, :, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (w[None, :, 0] * e[None, :, 1] - w[None, :, 1] * e[None, :, 0]) / den      # along the ray
        u = (w[None, :, 0] * d[:, None, 1] - w[None, :, 1] * d[:, None, 0]) / den      # along the edge
    ok = (np.abs(den) > 1e-12) & (u >= -1e-9) & (u <= 1 + 1e-9) & (t > 0)
    t = np.where(ok, t, np.inf).min(axis=1)
    return c + d * t[:, None]


def grip_ridge(back, outline):
    """Solid grip under the outside face across the top. Each slice across the phone is the cover's own cross-section
    pushed out by the grip's local height, so the rounded side edges move out with the grip and blend away with it."""
    sec = back.section(plane_origin=[0, CELL_Y, 0], plane_normal=[0, 1, 0])
    base = MultiPoint(sec.vertices[:, [0, 2]]).convex_hull.intersection(
        box(-20, OUTER_Z - 1.0, 100, OUTER_Z + 1.0))
    ys = np.linspace(GRIP_Y[0], GRIP_Y[1], 151)
    angles = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    c = np.array([34.0, OUTER_Z + 0.5])
    rings = []
    sx = 8.0      # rays are spread evenly in a space squeezed 8x across the phone, so the narrow ends get as many as the faces
    for y in ys:
        depth = OUTER_Z - grip_z(y)
        poly = unary_union([base, translate(base, 0, -depth)]).convex_hull
        squeezed = Polygon([((x - c[0]) / sx, z - c[1]) for x, z in poly.exterior.coords])
        hits = _ray_hits(squeezed, np.zeros(2), angles)
        rings.append(np.c_[hits[:, 0] * sx + c[0], hits[:, 1] + c[1]])
    n, k = len(angles), len(ys)
    verts = np.vstack([np.c_[r[:, 0], np.full(n, y), r[:, 1]] for r, y in zip(rings, ys)])
    verts = np.vstack([verts, [c[0], ys[0], c[1]], [c[0], ys[-1], c[1]]])
    faces = []
    for i in range(k - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces += [[a, b, b + n], [a, b + n, a + n]]
    c0, c1 = k * n, k * n + 1
    for j in range(n):
        faces += [[c0, (j + 1) % n, j], [c1, (k - 1) * n + j, (k - 1) * n + (j + 1) % n]]
    grip = trimesh.Trimesh(verts, np.array(faces), process=True)
    trimesh.repair.fix_normals(grip)
    assert grip.is_watertight, "grip loft is not watertight"
    foot = prism_z(outline, OUTER_Z - RIDGE_DEPTH - 1.0, OUTER_Z + 1.0)
    return trimesh.boolean.intersection([grip, foot], engine="manifold")


def cell_channel(scale=1.0):
    """The cell's channel at true size, centred where the scaled case puts it."""
    r = CELL_D / 2 + CELL_GAP
    x0, x1 = CHANNEL_X[0] * scale, CHANNEL_X[1] * scale
    cyl = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=96)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    cyl.apply_translation([(x0 + x1) / 2, CELL_Y * scale, CELL_Z * scale])
    return cyl


def contact_parts(scale=1.0):
    """The contacts' ribs with their lips, seats and pads, the support wall along the cell, and the strips' slits.
    Built at true size on the scaled case. Returns (solids to add, spaces to cut)."""
    yc, zc = CELL_Y * scale, CELL_Z * scale
    yp = yc + CONTACT_DY                                        # plate centre
    r = CELL_D / 2 + CELL_GAP
    top = RIM_Z * scale
    pad = contact_pad(scale)
    floor_at = lambda y: zc - np.sqrt(r ** 2 - (y - yc) ** 2)   # the channel's floor
    seat = floor_at(yp - CONTACT_W / 2)                          # level with the floor at the plate's lower edge
    sy0, sy1 = yc - CELL_D / 2 - SUPPORT_GAP - SUPPORT_T, yc - CELL_D / 2 - SUPPORT_GAP
    z0, z1 = STRIP_Z[0] * scale - 0.1, STRIP_Z[1] * scale + 0.3
    adds, cuts = [], []
    lines = []
    for wall, inward in ((WALL_IN[0] * scale, 1.0), (WALL_IN[1] * scale, -1.0)):
        line = wall + pad * inward                               # where the plate's back sits
        lines.append(line)
        # the two ribs with their lips (outline across the wall, extruded up the wall)
        X = lambda d: line + d * inward                                     # d mm in front of the plate's back line
        xa, xg, xf = wall - 0.3 * inward, X(GROOVE_D), X(GROOVE_D + LIP_T)  # into the wall; lip's back; lip's front
        g0, g1 = yp - RIB_GAP / 2, yp + RIB_GAP / 2                          # the groove's sides
        lower = [(xa, g0 - RIB_W), (xf, g0 - RIB_W), (xf, g0 + LIP_OVER), (xg, g0 + LIP_OVER), (xg, g0), (xa, g0)]
        upper = [(xa, g1), (xg, g1), (xg, g1 - LIP_OVER), (xf, g1 - LIP_OVER), (xf, g1 + RIB_W - 0.7),
                 (X(0.3), g1 + RIB_W), (xa, g1 + RIB_W)]                    # 45-degree face toward the phone's top
        bottom = min(floor_at(g0 - RIB_W), floor_at(g1 + RIB_W)) - 0.4      # 0.4 into the channel's floor
        for ring in (lower, upper):
            adds.append(prism_z(orient(Polygon(ring)), bottom, top))
        # the bar across the front at the top of the ribs, and the seat under the plate (to the lips' front)
        x0, x1 = sorted((xg, xf))
        adds.append(trimesh.creation.box(bounds=[[x0, g0, top - TOP_BAR_H], [x1, g1, top]]))
        x0, x1 = sorted((xa, xf))
        adds.append(trimesh.creation.box(bounds=[[x0, g0, floor_at(g1) - 0.4], [x1, g1, seat]]))
        if pad > 0.01:
            x0, x1 = sorted((wall - 0.3 * inward, line))
            adds.append(trimesh.creation.box(bounds=[[x0, yp - RIB_GAP / 2 - 0.1, seat - 0.1],
                                                     [x1, yp + RIB_GAP / 2 + 0.1, top]]))
        # the strip's path: from the support wall's back face, along the end wall, through the lower rib
        x0, x1 = sorted((line - 0.01 * inward, line + STRIP_SLOT * inward))
        cuts.append(trimesh.creation.box(bounds=[[x0, sy0 - 0.6, z0], [x1, yp - CONTACT_W / 2 + 0.1, z1]]))
    # the support wall, with a gap at each end for the strip and a mark on its top at each end of the board. Its face
    # toward the cell is the channel's own surface carried on up (the wall is cut by the channel), so the channel's
    # curve runs straight into it with no shelf, and the cell has the channel's 0.25 mm gap all the way up.
    slab = trimesh.creation.box(bounds=[[lines[0] + SUPPORT_END_GAP, sy0, FLOOR_Z * scale - 0.4],
                                        [lines[1] - SUPPORT_END_GAP, yc - r + 1.5, SUPPORT_TOP * scale]])
    adds.append(trimesh.boolean.difference([slab, cell_channel(scale)], engine="manifold"))
    for x in (34 * scale - BOARD_L / 2, 34 * scale + BOARD_L / 2):
        cuts.append(trimesh.creation.box(bounds=[[x - 0.4, sy0 - 0.1, SUPPORT_TOP * scale - 0.6],
                                                 [x + 0.4, yc - r + 0.5, SUPPORT_TOP * scale + 0.1]]))
    return adds, cuts


def polarity_marks():
    """'+' and '-' engraved on the floor beside the channel's ends, so the cell goes in the right way round."""
    s, w = POLARITY_SIZE / 2, POLARITY_STROKE / 2
    cuts = []
    for sign, x in POLARITY:
        shape = box(x - s, POLARITY_Y - w, x + s, POLARITY_Y + w)
        if sign == "+":
            shape = shape.union(box(x - w, POLARITY_Y - s, x + w, POLARITY_Y + s))
        cuts.append(prism_z(shape, FLOOR_Z - POLARITY_DEPTH, FLOOR_Z + 1.0))
    return cuts


def groove_ends():
    """Fill the grooves' last few mm below the grip and cut new rounded ends there; lengthen them at the bottom."""
    fill = prism_z(box(-10.0, GROOVE_END_Y - 1.0, 80.0, GRIP_Y[0] + 3.0), OUTER_Z, OUTER_Z + 1.1)
    cuts = []
    a = np.linspace(0, 2 * np.pi, 96, endpoint=False)

    def slot(gx, y0, y1):   # a 45-degree round-ended slot: radius 1 at the bottom, 2 at the face (2.5 just outside it)
        pts = [np.c_[gx + r * np.cos(a), yc + r * np.sin(a), np.full_like(a, z)]
               for yc in (y0, y1) for r, z in ((2.5, OUTER_Z - 0.5), (1.0, OUTER_Z + 1.0))]
        return trimesh.convex.convex_hull(np.vstack(pts))

    for gx, old, new in zip(GROOVE_XS, GROOVE_OLD_BOTTOM, GROOVE_NEW_BOTTOM):
        cuts += [slot(gx, GROOVE_END_Y - 2.0, GROOVE_END_Y), slot(gx, new, old + 1.0)]
    return [fill], cuts


def standoffs(scale=1.0):
    adds, cuts = [], []
    floor_z, wall_in_x, height = FLOOR_Z * scale, WALL_IN[0] * scale, STANDOFF_H
    base_z, top_z = floor_z - 0.6, floor_z + height
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
        if x < 10:   # tie to the left wall
            adds.append(prism_z(box(wall_in_x - 0.5, y - STANDOFF_D / 2, x, y + STANDOFF_D / 2), base_z,
                                TIE_TOP * scale))
        cuts.append(prism_z(Point(x, y).buffer(INSERT_D / 2, quad_segs=24), top_z - INSERT_DEPTH, top_z + 1))
    return adds, cuts


def led_window():
    lx, ly = board_to_back(*NETLIGHT_UV)
    cx = (lx + LED_HOLE_X) / 2
    top = FLOOR_Z + STANDOFF_H - 1.6
    ring = Point(cx, ly).buffer(LED_TUBE_OD / 2, quad_segs=24).difference(Point(cx, ly).buffer(LED_TUBE_ID / 2,
                                                                                               quad_segs=24))
    adds = [prism_z(ring, FLOOR_Z - 0.6, top)]
    cuts = [prism_z(Point(cx, ly).buffer(LED_TUBE_ID / 2, quad_segs=24), FLOOR_Z + 0.01, top + 1),
            prism_z(Point(LED_HOLE_X, ly).buffer(LED_HOLE_D / 2, quad_segs=16), OUTER_Z - 1.0, FLOOR_Z + 0.05)]
    return adds, cuts


def switch_mount(front_src):
    """Alley Cat's switch slot and screw holes, on the back's right wall. Returns (solids to add, spaces to cut)."""
    front = trimesh.load(front_src, force="mesh")
    region = trimesh.creation.box(bounds=SWITCH_REGION)
    space = trimesh.boolean.difference([region, front], engine="manifold")
    # the wall's outside face is eased into the mating edge near z 4; keep that sliver out of the copy
    space = trimesh.boolean.difference([space, trimesh.creation.box(bounds=[[-6.4, 50, 3.6], [-5.4, 77, 4.5]])],
                                       engine="manifold")
    # her left wall faces +x like this right wall, so the copy is a plain shift: outside face x -6.0 -> 72.0
    space.apply_translation([78.0, SWITCH_AT[0] - SWITCH_SRC_Y, SWITCH_AT[1] - SWITCH_SRC_Z])
    yc, zc = SWITCH_AT
    L, H, T = SWITCH_PLATE
    pad = trimesh.creation.box(bounds=[[SWITCH_PAD_X[0], yc - L / 2 - 1.0, FLOOR_Z - 0.3],
                                       [SWITCH_PAD_X[1], yc + L / 2 + 1.0, SWITCH_PAD_TOP]])
    # her slot and holes end at x 69.45 (her plate's face, 2.55 mm in); carry their outline on through the pad
    to2d = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, -69.6], [0, 0, 0, 1]], float)
    p2, _ = space.section(plane_origin=[69.6, 0, 0], plane_normal=[1, 0, 0]).to_planar(to_2D=to2d, check=False)
    through = []
    for poly in p2.polygons_full:
        m = trimesh.creation.extrude_polygon(poly, height=69.65 - (SWITCH_PAD_X[0] - 0.1))
        m.apply_transform(np.array([[0, 0, 1, SWITCH_PAD_X[0] - 0.1], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))
        through.append(m)
    corner = trimesh.creation.box(bounds=[[SWITCH_PAD_X[0] - T - 0.4, yc - L / 2 - 0.4, zc - H / 2 - 0.1],
                                          [SWITCH_PAD_X[0], yc + L / 2 + 0.4, RIM_Z + 0.2]])
    return [pad], [space, corner] + through


def main(src, front_src, dst, scale=1.0, stand=False):
    sback = trimesh.load(src, force="mesh")
    assert sback.is_watertight
    back = deepen(sback)
    outline = MultiPoint(back.vertices[:, :2]).convex_hull
    sw_adds, sw_cuts = switch_mount(front_src)
    a_gr, c_gr = groove_ends()
    a_led, c_led = led_window()
    ridge = grip_ridge(back, outline)
    stubs = [prism_z(box(*b), OUTER_Z, OUTER_Z + 1.1) for b in GROOVE_STUBS]
    top_gps = prism_z(box(TOPGPS_X[0], TOPGPS_Y[0], TOPGPS_X[1], TOPGPS_Y[1]), TOPGPS_FLOOR, RIM_Z + 5.0)
    recesses = [prism_z(Point(x, y).buffer(SCREW_RECESS_R, quad_segs=32), OUTER_Z - RIDGE_DEPTH - 1.0, OUTER_Z + 1.2)
                for x, y in SCREW_RECESSES]
    # Trim the inside additions to the cover's outer shape (its convex hull, carried straight up past the rim).
    envelope = trimesh.convex.convex_hull(np.vstack([back.vertices, back.vertices + [0, 0, 10.0]]))
    inside = [trimesh.boolean.intersection([m, envelope], engine="manifold") for m in stubs + a_gr + a_led]
    shell = trimesh.boolean.union([back, ridge] + inside + sw_adds, engine="manifold")
    shell = trimesh.boolean.difference([shell, trimesh.boolean.union(c_led + c_gr + [top_gps] + sw_cuts + recesses
                                                                     + polarity_marks(), engine="manifold")],
                                       engine="manifold")
    if scale != 1.0:
        shell.apply_scale(scale)
    a_st, c_st = standoffs(scale)
    if scale != 1.0:
        envelope.apply_scale(scale)
    a_st = [trimesh.boolean.intersection([m, envelope], engine="manifold") for m in a_st]
    out = trimesh.boolean.union([shell] + a_st, engine="manifold")
    # the network light's bore and window are cut again here: the nearest standoff's flared foot reaches into them
    c_led_scaled = [m.copy() for m in c_led]
    for m in c_led_scaled:
        m.apply_scale(scale)
    out = trimesh.boolean.difference([out, trimesh.boolean.union(c_st + [cell_channel(scale)] + c_led_scaled,
                                                                 engine="manifold")], engine="manifold")
    hull = trimesh.convex.convex_hull(out.vertices)       # includes the grip, unlike the envelope above
    a_ct, c_ct = contact_parts(scale)
    a_ct = [trimesh.boolean.intersection([m, hull], engine="manifold") for m in a_ct]
    out = trimesh.boolean.union([out] + a_ct, engine="manifold")
    out = trimesh.boolean.difference([out, trimesh.boolean.union(c_ct, engine="manifold")], engine="manifold")
    assert out.is_watertight, "result is not watertight"
    if stand:   # as it prints: standing on its top edge (the first layer is about 64 x 4 mm; use a brim)
        out = out.copy()
        out.apply_transform(np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float))
        lo, hi = out.bounds
        out.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    out.export(dst)
    print(f"18650 back: {out.bounds.round(2).tolist()}, watertight {out.is_watertight}, "
          f"bodies {len(out.split(only_watertight=False))}, scale {scale}; "
          f"rim z {RIM_Z}, T-Deck back z {TDECK_Z}, cell axis y {CELL_Y} z {CELL_Z:.2f}, board y {Y0 - BOARD_W:.2f}-{Y0}")


if __name__ == "__main__":
    args = sys.argv[1:]
    sc, st = 1.0, False
    while args and args[0].startswith("--"):
        if args[0] == "--scale":
            sc = float(args[1]); args = args[2:]
        elif args[0] == "--stand":
            st = True; args = args[1:]
        else:
            sys.exit(f"unknown option {args[0]}")
    main(*args[:3], scale=sc, stand=st)
