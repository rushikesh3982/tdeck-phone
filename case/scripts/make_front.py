"""Cut the earpiece grille, mic pocket, a second SMA antenna cut-out and a microSD-direction picture into the
Alley Cat TD1 front,
and keep Alley Cat's slide-switch mount on its left side for the modem's SS-12F15 power switch. The top-edge badge carries Alley Cat's cat-head logo
(from ../logo/alley-cat-head.json, taken from her TD1 files) as a visible credit to the case's designer.

Usage:
    python make_front.py "<Alley Chat TD1 Standard Front GPS Inserts.stl>" <output.stl> [cat logo json]
    python make_front.py --scale 1.01 "<...Front GPS Inserts.stl>" <output.stl>

--scale builds a larger front for a tight T-Deck fit (see case/README.md, "Fit and scale"). The whole finished front
is scaled: nothing in it has to stay true to size within 1 % (the mic pocket goes from 6.30 to 6.36 mm).

Needs: numpy, trimesh, shapely, manifold3d.

Coordinates are the original STL's own (mm). The front is modelled face-down:
the screen face is at z = -14.7 and the inside faces +z. Looking at the screen,
"left" is +x and "right" is -x. The top edge is +y and the bottom edge is -y.
"""
import sys

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon

# Earpiece grille: a 1 x 6 mm slot through the 3.6 mm face, centred under the
# GPS pocket (pocket: x -52.2..-35.8, y 100.2..107.5, floor at z -11.1).
SLOT_CENTRE = (-44.0, 103.85)  # x, y
SLOT_LENGTH = 6.0              # along x
SLOT_WIDTH = 1.0               # along y
SLOT_Z = (-16.0, -10.5)        # through the face, out into the empty pocket

# Mic: Sunrom 6027 (6 x 2.7 mm) in the bottom wall, left of USB-C as you look at
# the screen. The pocket opens inside the case. The mic is pushed in from inside
# until it touches the 1.2 mm skin, and a 1.5 mm sound hole goes through the skin.
MIC_X = -29.0                 # 15 mm left of the USB-C centre (x -44)
MIC_Z = -1.0                  # wall is 5.4-7.7 mm thick here
OUTER_Y = -1.658              # outer surface of the bottom wall at MIC_X
SKIN = 1.2
POCKET_D = 6.3
SOUND_HOLE_D = 1.5
POCKET_END_Y = 9.0            # past the inside surface (3.8-6.0)
# Wire groove from the mic pocket up the inside wall, through the mating lip,
# so the two mic wires reach the back half without being pinched by the T-Deck.
GROOVE_W = 2.4
GROOVE_Y = (2.7, 12.0)        # starts behind the mic body, clears the outer mating face
GROOVE_Z_TOP = 4.4            # just above the mating face (z 4.3)
LIP_NOTCH_Y = (2.4, 12.0)     # through the whole lip, including its hook (outermost y 2.55)
LIP_NOTCH_Z_TOP = 8.0         # above the top of the lip (7.3)

# Second SMA antenna cut-out, top-right corner (where the Grove plug slot was; the Grove socket is
# desoldered and the modem wires are soldered on instead). It is an exact mirror of the case's own
# SMA cut-out in the top-left corner, across the case centre line x = -44: 2.8 mm deep 12 mm nut
# recess, 2 mm wall with a 6.56 mm hole, 3 mm deep 8.4 mm hex pocket, axis at z = -2.85. Copying the
# whole corner block also fills the Grove slot, so the nut has a solid wall to clamp against.
MIRROR_X = -88.0
SMA_BLOCK = [[-26.5, 99.0, -10.5], [-11.5, 109.0, 5.6]]   # around the top-left cut-out

# The GPS version's slide-switch mount on the left side is kept exactly as Alley Cat drew it. It now holds the
# modem's power switch, an SS-12F15 (the switch it was designed for): a 19.7 x 5.6 x 0.5 mm plate in the 21.6 x 8.4 mm
# recess on the inside, two M2 screws 15 mm apart through countersunk holes from outside, and the 3 x 3 mm knob
# (4 mm tall) through the 6.9 x 3.4 mm slot, so about 1 mm of it stands proud of the wall. Body centre: y = 63.4,
# z = 0.1. (It was filled in an earlier version, when the modem was to follow the T-Deck's switch.)
SWITCH_CENTRE = (63.4, 0.1)          # y, z of the mount, on the left wall (outer face x = -6.0, recess floor x = -9.0)

# microSD direction picture, engraved on the right wall beside the T-Deck's microSD opening, on the phone-top side
# (the matching SIM picture is beside the SIM slit on the back's left side). Alley Cat's opening: y 72.5-89.75
# with its lead-in, centred at y 81.0, z -5.85; the wall is flat at x = -82 for y 50-101, z -10.1 to 3.9.
# The picture is the card as it should look going in, with the phone screen-up (owner's photo, 7 Nov 2026): the
# contacts end goes in first (picture's top, toward the screen side), the GOLD CONTACTS FACE UP (so they are drawn,
# as raised stripes), and the card's narrow section with its step is on the side toward the phone's bottom
# (the picture's left as you look at the right side). Card 11 x 15 mm, drawn 5.87 x 8.0 mm; step exaggerated.
SD_SLOT = (81.0, -5.85)             # y, z centre of the opening
SD_SLOT_TOP_END = 89.75             # y of the opening's lead-in edge on the phone-top side
SD_ICON_W, SD_ICON_H = 5.87, 8.0
SD_ICON_GAP = 1.6                   # wall left between the opening's lead-in and the picture
SD_ICON_STEP = 1.1                  # how far the narrow section is cut back (the real step would be 0.7 mm here)
SD_ICON_DEPTH = 0.8                 # into the 4 mm wall
SD_WALL_X = -82.0                   # outer face of the right wall

# Top-edge badge: Alley Cat's raised badge with the cat + GPS-pin art is replaced by a fresh badge of the same
# footprint carrying her cat-head logo, cut the way it is on her Alley Chat HT Pocket case: the head recessed,
# the closed eyes and nose cut deeper. The top wall under the old badge is restored from its plain profile
# (sampled beside the badge). The logo reads upright with the phone screen-up (screen side at the top of the
# view): there, right = +x and up = -z, so the ears point toward the screen side.
BADGE_CUT_X = (-55.75, -32.25)       # old badge lies within this (the wall is plain at both ends)
BADGE_CUT_Z = (-11.6, 4.2)
BADGE_FACE = (-52.4, -35.6, -8.8, 1.7)   # x0, x1, z0, z1 of the flat face (covers the earpiece pocket's width)
BADGE_FACE_R = 1.6
BADGE_FACE_Y = 109.0
BADGE_HEIGHT = 1.0                   # above the plain wall (y = 108.0)
CAT_HEIGHT = 9.4                     # cat head, ears to chin
CAT_HEAD_DEPTH = 0.35
CAT_FEATURE_DEPTH = 0.70             # eyes and nose (0.8 mm of wall stays behind them)

def prism_y(poly_xz, y0, y1):
    """Extrude a polygon drawn in (x, z) along model y, from y0 to y1."""
    mesh = trimesh.creation.extrude_polygon(poly_xz, height=y1 - y0)
    # local (X, Y, Z) -> model (x, z, -y); Z = 0 lands on y1, Z = h lands on y0
    rot = np.array([[1, 0, 0, 0],
                    [0, 0, -1, y1],
                    [0, 1, 0, 0],
                    [0, 0, 0, 1]], dtype=float)
    mesh.apply_transform(rot)
    return mesh


def prism_z(poly_xy, z0, z1):
    mesh = trimesh.creation.extrude_polygon(poly_xy, height=z1 - z0)
    mesh.apply_translation([0, 0, z0])
    return mesh


def teardrop(cx, cz, d, res=64):
    """Circle with a 45-degree roof on top (+z), so it prints without supports."""
    r = d / 2
    # arc from 135 deg round the bottom to 405 (= 45) deg, then the roof apex
    angles = np.radians(np.linspace(135, 405, res))
    pts = [(cx + r * np.cos(a), cz + r * np.sin(a)) for a in angles]
    pts.append((cx, cz + r * np.sqrt(2)))
    return Polygon(pts)


def mirror_sma_cutout(front):
    """Replace the top-right corner block with a mirror image of the top-left one."""
    mirror = np.eye(4)
    mirror[0, 0], mirror[0, 3] = -1.0, MIRROR_X
    block_left = trimesh.creation.box(bounds=SMA_BLOCK)
    block_right = block_left.copy()
    block_right.apply_transform(mirror)
    piece = trimesh.boolean.intersection([front, block_left], engine="manifold")
    piece.apply_transform(mirror)
    rest = trimesh.boolean.difference([front, block_right], engine="manifold")
    return trimesh.boolean.union([rest, piece], engine="manifold")


def prism_x(poly_yz, x0, x1):
    """Extrude a polygon drawn in (y, z) along model x, from x0 to x1."""
    mesh = trimesh.creation.extrude_polygon(poly_yz, height=x1 - x0)
    rot = np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float)
    mesh.apply_transform(rot)
    return mesh


def replace_badge_with_cat(front, cat_json):
    import json
    from shapely.affinity import affine_transform
    from shapely.geometry import box as sbox, shape as sshape
    from shapely.ops import unary_union
    # 1. plain top-wall profile y(z), sampled beside the badge, and a cutter above it over the old badge
    zs = np.arange(BADGE_CUT_Z[0], BADGE_CUT_Z[1] + 1e-9, 0.1)
    origins = np.array([[BADGE_CUT_X[0] - 1.3, 130.0, z] for z in zs])
    loc, idx, _ = front.ray.intersects_location(origins, np.tile([0, -1, 0], (len(zs), 1)), multiple_hits=False)
    prof = np.full(len(zs), np.nan); prof[idx] = loc[:, 1]
    assert not np.isnan(prof).any(), "could not sample the top wall profile"
    ring = [(y, z) for y, z in zip(prof, zs)] + [(112.0, zs[-1]), (112.0, zs[0])]
    front = trimesh.boolean.difference([front, prism_x(Polygon(ring), *BADGE_CUT_X)], engine="manifold")
    # 2. fresh badge: rounded-rectangle face, 45-degree bevel down to the wall, short skirt into it
    x0, x1, z0, z1 = BADGE_FACE
    face = sbox(x0 + BADGE_FACE_R, z0 + BADGE_FACE_R, x1 - BADGE_FACE_R, z1 - BADGE_FACE_R).buffer(BADGE_FACE_R, quad_segs=12)
    base = face.buffer(BADGE_HEIGHT, quad_segs=12)
    pts = [(x, BADGE_FACE_Y, z) for x, z in face.exterior.coords]
    pts += [(x, BADGE_FACE_Y - BADGE_HEIGHT, z) for x, z in base.exterior.coords]
    pts += [(x, BADGE_FACE_Y - BADGE_HEIGHT - 0.4, z) for x, z in base.exterior.coords]
    front = trimesh.boolean.union([front, trimesh.convex.convex_hull(np.array(pts))], engine="manifold")
    # 3. cat head: drawing (x right, y up, ears up) -> badge face (right = +x, up = -z)
    art = json.load(open(cat_json))
    head = unary_union([sshape(g) for g in art["head"]])
    feats = unary_union([sshape(g) for g in art["eyes"] + art["nose"]])
    hx0, hy0, hx1, hy1 = head.bounds
    s = CAT_HEIGHT / (hy1 - hy0)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    tf = [s, 0, 0, -s, cx - s * (hx0 + hx1) / 2, cz + s * (hy0 + hy1) / 2]
    cuts = []
    for g, depth in ((head, CAT_HEAD_DEPTH), (feats, CAT_FEATURE_DEPTH)):
        g = affine_transform(g, tf)
        cuts += [prism_y(p, BADGE_FACE_Y - depth, BADGE_FACE_Y + 1.0) for p in getattr(g, "geoms", [g])]
    return trimesh.boolean.difference([front] + cuts, engine="manifold")


def sd_icon():
    """Recessed microSD silhouette with raised contact stripes and a raised arrow, beside the microSD opening.
    Drawn in picture coordinates (u to the right = +y, v up = -z as seen from outside the right wall, screen up)."""
    cy = SD_SLOT_TOP_END + SD_ICON_GAP + SD_ICON_W / 2
    cz = SD_SLOT[1]
    W, H, s = SD_ICON_W, SD_ICON_H, SD_ICON_STEP
    narrow, slope = 2.77, 0.7                      # narrow section 5.2 mm of 15, then the step
    def yz(pts):
        return [(cy + u, cz - v) for u, v in pts]
    card = Polygon(yz([(W / 2, H / 2), (-W / 2 + s, H / 2), (-W / 2 + s, H / 2 - narrow),
                       (-W / 2, H / 2 - narrow - slope), (-W / 2, -H / 2), (W / 2, -H / 2)]))
    card = card.buffer(-0.35, join_style=1).buffer(0.35, join_style=1)
    keep = []
    u0 = s / 2                                     # centre of the narrow section
    for i in range(4):                             # gold contacts: 4 stripes (the card has 8; too fine to print)
        u = u0 + (i - 1.5) * 1.1
        keep.append(Polygon(yz([(u - 0.3, H / 2 - 0.55), (u + 0.3, H / 2 - 0.55),
                                (u + 0.3, H / 2 - 2.55), (u - 0.3, H / 2 - 2.55)])))
    tip = H / 2 - 3.15
    base, head_w, stem_w = tip - 1.5, 2.6, 1.0
    keep.append(Polygon(yz([(0, tip), (head_w / 2, base), (stem_w / 2, base), (stem_w / 2, -H / 2 + 0.8),
                            (-stem_w / 2, -H / 2 + 0.8), (-stem_w / 2, base), (-head_w / 2, base)])))
    shape = card
    for k in keep:
        shape = shape.difference(k)
    return [prism_x(g, SD_WALL_X - 1.0, SD_WALL_X + SD_ICON_DEPTH) for g in getattr(shape, "geoms", [shape])]


def main(src, dst, cat_json=None, scale=1.0):
    front = trimesh.load(src, force="mesh")
    assert front.is_watertight, "source mesh is not watertight"
    front = mirror_sma_cutout(front)
    if cat_json is None:
        import os
        cat_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "alley-cat-head.json")
    front = replace_badge_with_cat(front, cat_json)

    cx, cy = SLOT_CENTRE
    half = (SLOT_LENGTH - SLOT_WIDTH) / 2
    slot = LineString([(cx - half, cy), (cx + half, cy)]).buffer(SLOT_WIDTH / 2, quad_segs=16)
    cut_slot = prism_z(slot, *SLOT_Z)

    floor_y = OUTER_Y + SKIN
    cut_pocket = prism_y(teardrop(MIC_X, MIC_Z, POCKET_D), floor_y, POCKET_END_Y)
    cut_hole = prism_y(Point(MIC_X, MIC_Z).buffer(SOUND_HOLE_D / 2, quad_segs=16),
                       OUTER_Y - 3.0, floor_y + 0.1)
    def band(z0, z1):
        return Polygon([(MIC_X - GROOVE_W / 2, z0), (MIC_X + GROOVE_W / 2, z0),
                        (MIC_X + GROOVE_W / 2, z1), (MIC_X - GROOVE_W / 2, z1)])
    cut_groove = prism_y(band(MIC_Z, GROOVE_Z_TOP), *GROOVE_Y)
    cut_notch = prism_y(band(GROOVE_Z_TOP, LIP_NOTCH_Z_TOP), *LIP_NOTCH_Y)

    cutters = trimesh.boolean.union([cut_slot, cut_pocket, cut_hole, cut_groove, cut_notch] + sd_icon(),
                                    engine="manifold")
    out = trimesh.boolean.difference([front, cutters], engine="manifold")
    assert out.is_watertight, "result is not watertight"
    removed = front.volume - out.volume
    if scale != 1.0:
        out.apply_scale(scale)
    out.export(dst)
    print(f"removed {removed:.1f} mm^3 (before scaling), scale {scale}, faces {len(out.faces)}, "
          f"watertight {out.is_watertight}, bodies {len(out.split(only_watertight=False))}")


if __name__ == "__main__":
    args = sys.argv[1:]
    scale = 1.0
    if args and args[0] == "--scale":
        scale = float(args[1]); args = args[2:]
    main(*args[:3], scale=scale)
