"""Cut the earpiece grille, mic pocket and a second SMA antenna cut-out into the Alley Cat TD1 front,
and fill the unused slide-switch mount on its left side. The top-edge badge carries Alley Cat's cat-head logo
(from ../logo/alley-cat-head.json, taken from her TD1 files) as a visible credit to the case's designer, and
"rushiworks" is engraved on the screen side, along the right bezel beside the screen.

Usage:
    python make_front.py "<Alley Chat TD1 Standard Front GPS Inserts.stl>" <output.stl> [cat logo json]

Needs: numpy, trimesh, shapely, manifold3d, matplotlib (for the DejaVu Sans Mono Bold font it ships with).

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

# The GPS version's slide-switch mount on the left side (window, two countersunk screw holes, and the
# recess for the switch body on the inside) is not used: the modem follows the T-Deck's power switch.
# It is filled by copying the wall's normal cross-section, taken just beside the mount (y = 77, where
# the wall is untouched and the T-Deck already fits), across y = 51.0..75.6. Kept clear: the Reset
# Button opening below it and the small recess around it for the button's flange (z below -3.4).
SWITCH_WALL_SLICE_Y = 77.0
SWITCH_FILL_Y = (51.0, 75.6)
SWITCH_FILL_CLIP = (-10.6, -4.15, -5.9, 4.3)        # x0, z0, x1, z1 of the wall slice used
RESET_KEEP_OUT = [[-12.0, 65.0, -10.0], [-5.0, 72.0, -3.4]]

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

# "rushiworks" on the screen side, along the right bezel beside the screen (u = -x is left-to-right as you look
# at the screen). There the face is a 1 mm lip lying on the T-Deck's front (u 72.5-78.5, straight from y ~56 to
# 98), so the engraving is shallow and 0.7 mm of plastic stays behind it. The text runs bottom-to-top, tops of the
# letters toward the screen. Font: DejaVu Sans Mono Bold, a coding font (bundled with matplotlib, free licence).
# Engraved, because the screen side prints face-down on the bed.
FRONT_TEXT = "rushiworks"
FRONT_TEXT_HEIGHT = 4.2              # letter height incl. the h/k ascenders, measured across the bezel
FRONT_TEXT_CENTRE = (75.5, 77.0)     # u, y: middle of the bezel, beside the screen
FRONT_TEXT_ANGLE = 90.0              # degrees counter-clockwise in the screen view: reads bottom-to-top
FRONT_TEXT_DEPTH = 0.30
FACE_Z = -14.7



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


def fill_switch_mount(front):
    """Copy the wall's normal cross-section over the unused slide-switch mount."""
    from shapely.geometry import box as sbox
    from shapely.ops import polygonize, unary_union
    segs = trimesh.intersections.mesh_plane(front, [0, 1, 0], [0, SWITCH_WALL_SLICE_Y, 0])
    lines = [LineString([(round(a[0], 6), round(a[2], 6)), (round(b[0], 6), round(b[2], 6))]) for a, b in segs]
    section = unary_union(list(polygonize(unary_union(lines))))
    wall = section.intersection(sbox(*SWITCH_FILL_CLIP))
    fill = prism_y(wall, *SWITCH_FILL_Y)
    fill = trimesh.boolean.difference([fill, trimesh.creation.box(bounds=RESET_KEEP_OUT)], engine="manifold")
    return trimesh.boolean.union([front, fill], engine="manifold")


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


def engrave_front_text(front):
    from matplotlib import font_manager
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath
    from shapely.affinity import affine_transform
    from shapely.ops import unary_union
    font = font_manager.findfont(FontProperties(family="DejaVu Sans Mono", weight="bold"), fallback_to_default=False)
    path = TextPath((0, 0), FRONT_TEXT, size=10, prop=FontProperties(fname=font))
    rings = [Polygon(r).buffer(0) for r in path.to_polygons(closed_only=True) if len(r) > 3]
    text = None
    for r in sorted(rings, key=lambda q: -q.area):       # rings inside others (counters of o, etc.) are holes
        text = r if text is None else (text.difference(r) if text.contains(r) else text.union(r))
    text = unary_union(text)
    gx0, gy0, gx1, gy1 = text.bounds
    k = FRONT_TEXT_HEIGHT / (gy1 - gy0)
    a = np.radians(FRONT_TEXT_ANGLE)
    uc, yc = FRONT_TEXT_CENTRE
    gcx, gcy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    # glyph -> scaled, rotated in the screen view (u right, y up) -> model (x = -u, y)
    cu, su = k * np.cos(a), k * np.sin(a)
    u_tf = [cu, -su, su, cu, uc - (cu * gcx - su * gcy), yc - (su * gcx + cu * gcy)]
    text = affine_transform(affine_transform(text, u_tf), [-1, 0, 0, 1, 0, 0])
    cuts = [prism_z(g, FACE_Z - 1.0, FACE_Z + FRONT_TEXT_DEPTH) for g in getattr(text, "geoms", [text])]
    print(f"  text: {FRONT_TEXT!r}, {(gx1-gx0)*k:.1f} mm long, {(gy1-gy0)*k:.2f} mm tall, bounds {np.round(text.bounds, 2)}")
    return trimesh.boolean.difference([front] + cuts, engine="manifold")


def main(src, dst, cat_json=None):
    front = trimesh.load(src, force="mesh")
    assert front.is_watertight, "source mesh is not watertight"
    front = mirror_sma_cutout(front)
    front = fill_switch_mount(front)
    if cat_json is None:
        import os
        cat_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "alley-cat-head.json")
    front = replace_badge_with_cat(front, cat_json)
    front = engrave_front_text(front)

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

    cutters = trimesh.boolean.union([cut_slot, cut_pocket, cut_hole, cut_groove, cut_notch],
                                    engine="manifold")
    out = trimesh.boolean.difference([front, cutters], engine="manifold")
    assert out.is_watertight, "result is not watertight"
    out.export(dst)
    print(f"removed {front.volume - out.volume:.1f} mm^3, faces {len(out.faces)}, "
          f"watertight {out.is_watertight}, bodies {len(out.split(only_watertight=False))}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
