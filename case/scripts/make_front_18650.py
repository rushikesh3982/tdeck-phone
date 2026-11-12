"""18650 version of the front, to go with make_back_18650.py. First draft: the parts that don't depend on unmeasured
parts. It starts from make_front.py's result, so the earpiece grille, mic pocket, antenna cut-outs and badge are kept.

Done here:
- left wall: the SIM slit (the board now sits at this height, in the front half) in a finger scoop, with its
  direction picture beside it;
  Alley Cat's speaker grille and switch mount filled, because the board's edge now runs along this wall;
- right wall: Alley Cat's speaker cavity and grille, an exact copy of hers moved from the left wall to below the
  T-Deck's switch (the stretch between the T-Deck's switch and the microSD slot is left alone: the notch that holds
  the T-Deck and the slot for the switch's slider piece are there). The modem switch goes on the back's right wall,
  so the front's lip is notched there for the switch's plate;
- earpiece pocket widened from 16.4 to 19.5 mm above the earpiece, and its floor lowered 0.5 mm (the face under it
  is 3.1 mm instead of 3.6), for the GPS antenna standing on its edge;
- the top-edge badge carries the owner's rushiWorks logo instead of Alley Cat's cat. Her cat and "Alley Chat TD1 S"
  are kept on the back's inside floor, and she is credited in the README and case files.

Not done yet: a new low earpiece holder, the cut-out for the battery contacts, and routes past the cell for the
earpiece wires and the GPS cable.

Usage:
    python make_front_18650.py "<Alley Chat TD1 Standard Front GPS Inserts.stl>" <output.stl>
    python make_front_18650.py --scale 1.01 "<...Front GPS Inserts.stl>" <output.stl>

Coordinates are the front's own: see make_front.py. A point in make_back_18650.py's coordinates is at
x_front = -x - 10, z_front = 0.8 - z.
"""
import os
import sys
import tempfile

import numpy as np
import trimesh
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_back_18650 as B  # noqa: E402
import make_front as F  # noqa: E402

LEFT_OUTER_X = -6.0
FILL_INNER_X = -9.0            # fills stop here (1 mm inside the board's edge line), so nothing narrows the inside

# Left wall openings to fill (y0, y1, z0, z1). The T-Deck's reset opening (y 66-71, z -7 to -4.7) is below these.
GRILLE_FILL = (31.0, 47.0, -4.3, 3.6)
SWITCH_FILL = (52.5, 74.5, -3.6, 3.7)   # includes the lead-ins and the screw countersinks
PLAIN_WALL_Y = 90.0            # the wall's plain outside profile is sampled here

# SIM slit, lined up with the card on the board.
SIM_Y = B.board_to_back(14.6, B.BOARD_H)[1]                                  # 31.57
SIM_Z = 0.8 - (B.FLOOR_Z + B.STANDOFF_H + 1.6 + 0.75)                         # -0.35
SLIT_W, SLIT_H = 15.0, 1.8     # card is 12 x 0.8 mm
SLIT_INNER_X = -9.6            # straight part, just past the wall's inside face
SLIT_FLARE = 1.0               # extra on every side at the outside face: the wall is 4 mm thick here

# Finger scoop round the slit: a shallow oval dish, 2.2 mm deep at the slit, so the card's edge (4.3 mm in from the
# wall's face) is 2.1 mm from the bottom of the dish. Alley Cat's old speaker cavity behind it (1 mm deep, inside the
# wall) is filled where it sits behind the T-Deck, so the wall left under the dish stays 1.7 mm or more.
SCOOP_DEPTH = 2.2
SCOOP_OPEN = (22.0, 7.6)       # length along the wall (y) and height (z) of the dish's rim
CAVITY_FILL = [[-9.95, 22.5, -2.6], [-8.9, 41.0, 4.25]]

# SIM direction picture: as on make_back.py, on the phone-top side of the scoop.
# Drawn 1.6x the size used on the current back (6.0 x 7.5 mm), so it reads easily, and centred on the flat part of
# the wall (z -10.1 to 3.9) rather than on the slit's height.
ICON_K = 1.6
ICON_W, ICON_H, ICON_GAP, ICON_CUT, ICON_DEPTH = 6.0 * ICON_K, 7.5 * ICON_K, 1.6, 2.0 * ICON_K, 0.8
ICON_Z = -3.0

# microSD direction picture (make_front.py's, on the right wall beside the microSD opening), redrawn 1.5x larger
# (8.8 x 12 mm instead of 5.87 x 8) and centred on the wall's flat part. It fills the wall between the opening's
# lead-in and the top corner (flat to y 101).
SD_K = 1.5
SD_Z = -3.05

# Speaker: the space of Alley Cat's left-wall speaker cavity and grille (cavity y 28-49.5, z -5.7 up to the mating
# face, 1 mm into the wall; grille y 32-46), mirrored to the right wall and moved down the phone, into the free
# stretch below the T-Deck's switch recess (which starts at y 38). The speaker (about 20 x 10 x 7 mm) stands in the
# cavity with its face to the grille, between the wall and the modem board's edge.
SPEAKER_REGION = [[-10.2, 27.5, -6.0], [-5.5, 50.0, 4.29]]
SPEAKER_SHIFT_Y = -12.0         # cavity y 16-37.5, grille y 20-34

# Owner's logo on the top-edge badge. The badge is built as make_front.py builds its fresh badge (rounded face,
# 1 mm proud, 45-degree edge), but larger: its face is as wide as the antenna slot behind it (x -53.3..-34.7), and
# its sloped edge spans exactly the flat part of the top edge (z -10.0, where the edge starts to curve toward the
# screen, to 4.0, where the flat ends just before the seam), so the face is z -9.0..3.0. The logo fills the face with
# 0.8 mm left round it, recessed 0.5 mm; its thinnest strokes (about 0.55 mm at this size) are widened by 0.05 mm
# each side so they print as clean grooves on this vertical face.
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "rushi-logo.jpg")
LOGO_MARGIN, LOGO_DEPTH, LOGO_GROW = 0.8, 0.5, 0.05
BADGE_FACE_18650 = (-B.TOPGPS_X[1] - 10.0, -B.TOPGPS_X[0] - 10.0, -9.0, 3.0)

# Lip notch for the modem switch's plate on the back's right wall (make_back_18650.py): the lip that reaches into
# the back (z 4.3-5.3, x -79.9..-79.0 here) is removed along the plate.
LIP_NOTCH = [[-80.3, B.SWITCH_AT[0] - B.SWITCH_PLATE[0] / 2 - 1.0, 4.2],
             [-78.6, B.SWITCH_AT[0] + B.SWITCH_PLATE[0] / 2 + 1.0, 5.6]]

# Earpiece pocket, widened above the earpiece to match the back's slot (x 24.7-43.3 there).
POCKET_NEW_X = (-B.TOPGPS_X[1] - 10.0, -B.TOPGPS_X[0] - 10.0)                # -53.75 .. -34.25
POCKET_OLD_X = (-52.2, -35.8)
POCKET_Y = (100.2, 106.4)
POCKET_Z = (-8.4, 5.4)             # from just below the holder's roof (-8.2)
# The pocket's floor (z -11.1, over the earpiece's grille slot) is lowered 0.5 mm, and the small fillet where it met
# the far wall is cleared with it, so the low earpiece holder sits 0.5 mm lower.
FLOOR_CUTS = [[[POCKET_OLD_X[0], 100.2, -11.6], [POCKET_OLD_X[1], 107.55, -11.1 + 0.01]],
              [[POCKET_OLD_X[0], 106.9, -11.2], [POCKET_OLD_X[1], 107.55, -10.5]]]


def badge_with_logo(front, _cat_json=None):
    """make_front.py's badge, with the owner's logo cut into its face instead of the cat."""
    from shapely.affinity import affine_transform
    from shapely.geometry import box as sbox
    from make_back import trace_logo
    # steps 1 and 2 of make_front.replace_badge_with_cat: restore the plain top wall, add a fresh badge
    zs = np.arange(F.BADGE_CUT_Z[0], F.BADGE_CUT_Z[1] + 1e-9, 0.1)
    origins = np.array([[F.BADGE_CUT_X[0] - 1.3, 130.0, z] for z in zs])
    loc, idx, _ = front.ray.intersects_location(origins, np.tile([0, -1, 0], (len(zs), 1)), multiple_hits=False)
    prof = np.full(len(zs), np.nan); prof[idx] = loc[:, 1]
    assert not np.isnan(prof).any(), "could not sample the top wall profile"
    ring = [(y, z) for y, z in zip(prof, zs)] + [(112.0, zs[-1]), (112.0, zs[0])]
    front = trimesh.boolean.difference([front, F.prism_x(Polygon(ring), *F.BADGE_CUT_X)], engine="manifold")
    x0, x1, z0, z1 = BADGE_FACE_18650
    r = F.BADGE_FACE_R
    face = sbox(x0 + r, z0 + r, x1 - r, z1 - r).buffer(r, quad_segs=12)
    base = face.buffer(F.BADGE_HEIGHT, quad_segs=12)
    pts = [(x, F.BADGE_FACE_Y, z) for x, z in face.exterior.coords]
    pts += [(x, F.BADGE_FACE_Y - F.BADGE_HEIGHT, z) for x, z in base.exterior.coords]
    pts += [(x, F.BADGE_FACE_Y - F.BADGE_HEIGHT - 0.4, z) for x, z in base.exterior.coords]
    front = trimesh.boolean.union([front, trimesh.convex.convex_hull(np.array(pts))], engine="manifold")
    # 3. the logo: drawing (x right, y up) -> badge face (right = +x, up = -z), as the cat was
    logo = trace_logo(LOGO_PATH)
    lx0, ly0, lx1, ly1 = logo.bounds
    s = min((x1 - x0 - 2 * LOGO_MARGIN) / (lx1 - lx0), (z1 - z0 - 2 * LOGO_MARGIN) / (ly1 - ly0))
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    art = affine_transform(logo, [s, 0, 0, -s, cx - s * (lx0 + lx1) / 2, cz + s * (ly0 + ly1) / 2])
    art = art.buffer(LOGO_GROW, join_style=1).intersection(face.buffer(-0.3))
    cuts = [F.prism_y(p, F.BADGE_FACE_Y - LOGO_DEPTH, F.BADGE_FACE_Y + 1.0) for p in getattr(art, "geoms", [art])]
    return trimesh.boolean.difference([front] + cuts, engine="manifold")


def wall_fill(front, y0, y1, z0, z1):
    """A plug for the left wall: the wall's plain outside profile, carried along y from y0 to y1."""
    zs = np.arange(z0, z1 + 1e-9, 0.1)
    origins = np.array([[10.0, PLAIN_WALL_Y, z] for z in zs])
    loc, idx, _ = front.ray.intersects_location(origins, np.tile([-1.0, 0, 0], (len(zs), 1)), multiple_hits=False)
    outer = np.full(len(zs), np.nan)
    outer[idx] = loc[:, 0]
    assert not np.isnan(outer).any(), "could not sample the plain wall"
    ring = [(x, z) for x, z in zip(outer, zs)] + [(FILL_INNER_X, zs[-1]), (FILL_INNER_X, zs[0])]
    return F.prism_y(Polygon(ring), y0, y1)


def sim_slit():
    pts = []
    for x, w, h in ((SLIT_INNER_X, SLIT_W, SLIT_H),
                    (LEFT_OUTER_X + 0.6, SLIT_W + 2 * SLIT_FLARE * 1.2, SLIT_H + 2 * SLIT_FLARE * 1.2)):
        for sy in (-1, 1):
            for sz in (-1, 1):
                pts.append([x, SIM_Y + sy * w / 2, SIM_Z + sz * h / 2])
    funnel = trimesh.convex.convex_hull(np.array(pts))
    straight = trimesh.creation.box(bounds=[[SLIT_INNER_X - 1.2, SIM_Y - SLIT_W / 2, SIM_Z - SLIT_H / 2],
                                            [SLIT_INNER_X + 0.2, SIM_Y + SLIT_W / 2, SIM_Z + SLIT_H / 2]])
    return [funnel, straight]


def sim_scoop():
    """An oval dish in the wall's outside face, centred on the slit (part of an ellipsoid)."""
    ax = 4.0                                            # how round the dish's bottom is
    k = np.sqrt(1 - ((ax - SCOOP_DEPTH) / ax) ** 2)     # rim size / ellipsoid size, at the wall's face
    dish = trimesh.creation.icosphere(subdivisions=5, radius=1.0)
    dish.apply_scale([ax, SCOOP_OPEN[0] / 2 / k, SCOOP_OPEN[1] / 2 / k])
    dish.apply_translation([LEFT_OUTER_X + ax - SCOOP_DEPTH, SIM_Y, SIM_Z])
    return dish


def sim_icon():
    """Recessed micro-SIM silhouette with a raised arrow, beside the scoop. Picture up = the screen side (-z)."""
    slit_end = SIM_Y + SCOOP_OPEN[0] / 2
    cy = slit_end + ICON_GAP + ICON_W / 2
    top, bot = ICON_Z - ICON_H / 2, ICON_Z + ICON_H / 2
    l, r = cy + ICON_W / 2, cy - ICON_W / 2             # seen from outside, +y is on the left
    c, k = ICON_CUT, ICON_K
    card = Polygon([(l, top), (r, top), (r, bot - c), (r + c, bot), (l, bot)])   # cut corner bottom-right
    card = card.buffer(-0.35 * k, join_style=1).buffer(0.35 * k, join_style=1)
    head_w, head_h, stem_w = 3.2 * k, 2.0 * k, 1.1 * k
    tip, base = top + 0.8 * k, top + 0.8 * k + head_h
    arrow = Polygon([(cy, tip), (cy + head_w / 2, base), (cy + stem_w / 2, base), (cy + stem_w / 2, bot - 0.9 * k),
                     (cy - stem_w / 2, bot - 0.9 * k), (cy - stem_w / 2, base), (cy - head_w / 2, base)])
    shape = card.difference(arrow)
    return [F.prism_x(g, LEFT_OUTER_X - ICON_DEPTH, LEFT_OUTER_X + 1.0) for g in getattr(shape, "geoms", [shape])]


def sd_icon_big():
    """make_front.py's microSD picture, every size times SD_K: recessed card with its step, raised contact stripes
    and a raised arrow. Picture coordinates: u to the right = +y, v up = -z, seen from outside the right wall."""
    k = SD_K
    W, H, s = F.SD_ICON_W * k, F.SD_ICON_H * k, F.SD_ICON_STEP * k
    cy = F.SD_SLOT_TOP_END + F.SD_ICON_GAP + W / 2
    cz = SD_Z
    narrow, slope = 2.77 * k, 0.7 * k

    def yz(pts):
        return [(cy + u, cz - v) for u, v in pts]
    card = Polygon(yz([(W / 2, H / 2), (-W / 2 + s, H / 2), (-W / 2 + s, H / 2 - narrow),
                       (-W / 2, H / 2 - narrow - slope), (-W / 2, -H / 2), (W / 2, -H / 2)]))
    card = card.buffer(-0.35 * k, join_style=1).buffer(0.35 * k, join_style=1)
    keep = []
    u0 = s / 2
    for i in range(4):
        u = u0 + (i - 1.5) * 1.1 * k
        keep.append(Polygon(yz([(u - 0.3 * k, H / 2 - 0.55 * k), (u + 0.3 * k, H / 2 - 0.55 * k),
                                (u + 0.3 * k, H / 2 - 2.55 * k), (u - 0.3 * k, H / 2 - 2.55 * k)])))
    tip = H / 2 - 3.15 * k
    base, head_w, stem_w = tip - 1.5 * k, 2.6 * k, 1.0 * k
    keep.append(Polygon(yz([(0, tip), (head_w / 2, base), (stem_w / 2, base), (stem_w / 2, -H / 2 + 0.8 * k),
                            (-stem_w / 2, -H / 2 + 0.8 * k), (-stem_w / 2, base), (-head_w / 2, base)])))
    shape = card
    for g in keep:
        shape = shape.difference(g)
    return [F.prism_x(g, F.SD_WALL_X - 1.0, F.SD_WALL_X + F.SD_ICON_DEPTH) for g in getattr(shape, "geoms", [shape])]


def moved_speaker_space(front):
    """The empty space of Alley Cat's speaker cavity and grille, mirrored to the right wall and moved down."""
    region = trimesh.creation.box(bounds=SPEAKER_REGION)
    space = trimesh.boolean.difference([region, front], engine="manifold")
    mirror = np.eye(4)
    mirror[0, 0], mirror[0, 3] = -1.0, F.MIRROR_X
    mirror[1, 3] = SPEAKER_SHIFT_Y
    space.apply_transform(mirror)
    trimesh.repair.fix_normals(space)
    return space


def pocket_widening():
    y0, y1 = POCKET_Y
    z0, z1 = POCKET_Z
    return [trimesh.creation.box(bounds=[[POCKET_NEW_X[0], y0, z0], [POCKET_OLD_X[0] + 0.1, y1, z1]]),
            trimesh.creation.box(bounds=[[POCKET_OLD_X[1] - 0.1, y0, z0], [POCKET_NEW_X[1], y1, z1]])] + \
        [trimesh.creation.box(bounds=b) for b in FLOOR_CUTS]


def main(src, dst, scale=1.0):
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "front.stl")
        small_sd, F.sd_icon = F.sd_icon, lambda: []      # the larger microSD picture is cut below instead
        cat_badge, F.replace_badge_with_cat = F.replace_badge_with_cat, badge_with_logo
        try:
            F.main(src, base)
        finally:
            F.sd_icon, F.replace_badge_with_cat = small_sd, cat_badge
        front = trimesh.load(base, force="mesh")
    assert front.is_watertight
    speaker = moved_speaker_space(front)
    plugs = [wall_fill(front, *GRILLE_FILL), wall_fill(front, *SWITCH_FILL), trimesh.creation.box(bounds=CAVITY_FILL)]
    out = trimesh.boolean.union([front] + plugs, engine="manifold")
    cuts = trimesh.boolean.union([speaker, trimesh.creation.box(bounds=LIP_NOTCH), sim_scoop()] + sd_icon_big() + sim_slit() + sim_icon() + pocket_widening(), engine="manifold")
    out = trimesh.boolean.difference([out, cuts], engine="manifold")
    assert out.is_watertight, "result is not watertight"
    if scale != 1.0:
        out.apply_scale(scale)
    out.export(dst)
    print(f"18650 front: {out.bounds.round(2).tolist()}, watertight {out.is_watertight}, "
          f"bodies {len(out.split(only_watertight=False))}, scale {scale}; SIM slit at y {SIM_Y:.2f}, z {SIM_Z:.2f}")


if __name__ == "__main__":
    args = sys.argv[1:]
    sc = 1.0
    if args and args[0] == "--scale":
        sc = float(args[1]); args = args[2:]
    main(*args[:2], scale=sc)
