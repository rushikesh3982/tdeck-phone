"""18650 version of the front, to go with make_back_18650.py. It starts from make_front.py's result, so the earpiece
grille, mic pocket, antenna cut-outs and badge are kept.

Done here:
- left wall: the SIM slit (the board now sits at this height, in the front half) in a finger scoop, with its
  direction picture beside it;
  the wall is rebuilt in one plain piece where Alley Cat's speaker grille and switch mount were (the board's edge now
  runs along this wall), with only her reset opening copied back;
- right wall: Alley Cat's speaker cavity and grille, an exact copy of hers moved from the left wall to below the
  T-Deck's switch (the stretch between the T-Deck's switch and the microSD slot is left alone: the notch that holds
  the T-Deck and the slot for the switch's slider piece are there). The modem switch goes on the back's right wall,
  set deep enough to clear the front's lip, so the lip is whole;
- top pocket: Alley Cat's earpiece pocket kept (16.4 mm wide, its side walls hold the holder) with its floor lowered
  0.5 mm (the face under it is 3.1 mm instead of 3.6), and above it a clean 19.5 mm slot for the GPS antenna
  standing on its edge, as wide as the back's slot;
- a notch in each side wall where the top of a battery contact stands above the back's rim;
- the top-edge badge carries the owner's rushiWorks logo instead of Alley Cat's cat. Her cat and "Alley Chat TD1 S"
  are kept on the back's inside floor, and she is credited in the README and case files.

The low earpiece holder is make_earpiece_holder_18650.py. The design as a whole is described in docs/design-18650.md.

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
from shapely.geometry import Polygon, box as shapely_box
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_back_18650 as B  # noqa: E402
import make_front as F  # noqa: E402

LEFT_OUTER_X = -6.0
# Left wall: rebuilt as one plain piece between y 27.5 and 80, where Alley Cat had her speaker recess and grille and
# the switch mount (plate recess, knob slot, screw holes, and the notch in the lip). Her wall is a straight extrusion
# there, so the piece is her own cross-section (taken at y 80, which has no features) carried along y, from z -8 up to
# the top of the lip; the wall below z -8 was never changed. Below y 27.5 her wall is left as it is: the rounded groove
# at y 21-26 runs the full height beside the T-Deck's edge (clearance she gave the T-Deck), and her wall's inside
# face changes there from upright to sloped. Only two openings are then cut into the piece: her reset opening, copied
# from her file, and the SIM slit (with its scoop and picture). Her bump beside the reset that holds the T-Deck down is
# copied back too.
LEFT_WALL_Y = (27.5, 80.0)
LEFT_WALL_X = (-10.8, -5.2)       # the box the wall is rebuilt in (her inside face is at -10 to -9.1, outside -6.0)
LEFT_WALL_Z0 = -8.0
LEFT_WALL_SECTION_Y = 80.0
# Her bump just above the reset opening (y 59-64, z -6.6 to -4.8, 0.8 mm proud) holds the T-Deck's board down: it is
# copied back from her file into the rebuilt wall.
HOLD_BUMP_REGION = [[-11.2, 58.5, -7.1], [-9.95, 64.4, -4.3]]
# Her reset opening, with its counterbore outside and the recess inside that her reset button sits in (the button is
# 5.2 x 3.4 mm; her recess reaches up into her switch recess, so it is copied up to z -3.4: 3.7 mm tall).
RESET_REGION = [[-10.6, 65.5, -7.8], [-5.4, 72.25, -3.4]]

# SIM slit, lined up with the card on the board.
SIM_Y = B.board_to_back(14.6, B.BOARD_H)[1]                                  # 31.57
SIM_Z = 0.8 - (B.FLOOR_Z + B.STANDOFF_H + 1.6 + 0.75)                         # -0.35
SLIT_W, SLIT_H = 15.0, 1.8     # card is 12 x 0.8 mm
SLIT_INNER_X = -9.6            # straight part, just past the wall's inside face
SLIT_FLARE = 1.0               # extra on every side at the outside face: the wall is 4 mm thick here

# Finger scoop round the slit: a shallow oval dish, 2.2 mm deep at the slit, so the card's edge (4.3 mm in from the
# wall's face) is 2.1 mm from the bottom of the dish. Alley Cat's old speaker recess behind it (1 mm deep, inside the
# wall) is gone with the rebuilt wall, so the wall left under the dish stays about 1.7 mm.
SCOOP_DEPTH = 2.2
SCOOP_OPEN = (22.0, 7.6)       # length along the wall (y) and height (z) of the dish's rim

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

# Speaker: the space of Alley Cat's left-wall speaker cavity and grille (cavity y 28-49.3, z -5.7 up to the mating
# face, 1 mm into the wall; grille y 32-46), mirrored to the right wall and moved down the phone, into the free
# stretch below the slot for the T-Deck switch's slider (which starts at y 37.5), leaving 1.2 mm of wall between them.
# The speaker (about 20 x 10 x 7 mm) stands in the cavity with its face to the grille, between the wall and the modem
# board's edge. The cavity's lower edge comes down to the top of the snap ridge that runs along this wall (z -6.7),
# so the two line up.
SPEAKER_REGION = [[-10.2, 27.5, -6.0], [-5.5, 50.0, 4.29]]
SPEAKER_SHIFT_Y = -13.0         # cavity y 15-36.3, grille y 19-33
SPEAKER_FLOOR_X = F.MIRROR_X + 9.0        # -79.0: her cavity's floor (x -9.0 on her left wall), mirrored
SNAP_RIDGE_TOP = -6.70          # top of the ridge along the inside of the right wall that the T-Deck snaps under

# Owner's logo on the top-edge badge. The badge is built as make_front.py builds its fresh badge (rounded face,
# 1 mm proud, 45-degree edge), but larger: its face is as wide as the antenna slot behind it (x -53.3..-34.7), and
# its sloped edge spans exactly the flat part of the top edge (z -10.0, where the edge starts to curve toward the
# screen, to 4.0, where the flat ends just before the seam), so the face is z -9.0..3.0. The logo fills the face with
# 0.8 mm left round it, recessed 0.5 mm; its thinnest strokes (about 0.55 mm at this size) are widened by 0.05 mm
# each side so they print as clean grooves on this vertical face.
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "rushi-logo.jpg")
LOGO_MARGIN, LOGO_DEPTH, LOGO_GROW = 0.8, 0.5, 0.05
BADGE_FACE_18650 = (-B.TOPGPS_X[1] - 10.0, -B.TOPGPS_X[0] - 10.0, -9.0, 3.0)


# Battery contacts (make_back_18650.py): each contact's top stands about 1.5-2.4 mm above the back's rim, where the
# front's side wall comes in to within 1.5-2.4 mm of the cell's end. So the wall is notched there out to the line of
# the plate's back (the back's wall, x -2.0 / 70.0 in the back's coordinates, plus the pad that a scaled print adds),
# up to 1 mm above the contact's highest top, leaving about 2 mm of wall; the lip that reaches into the back is
# removed across the contact's ribs too. Worked out in the back's coordinates (x, y, z) and converted.
CONTACT_NOTCH_TOP = 3.0           # 0.5 mm under the T-Deck's back


def contact_notches(scale=1.0):
    pad = B.contact_pad(scale) / scale              # the cut is made before the front is scaled
    yp = B.CELL_Y + B.CONTACT_DY / scale            # the plates' centre (true offset from the scaled cell's axis)
    out = []
    for wall, inward in ((B.WALL_IN[0], 1.0), (B.WALL_IN[1], -1.0)):
        x0, x1 = sorted((wall + (pad - 0.05) * inward, wall + 3.0 * inward))
        for (y0, y1), (z0, z1) in (((yp - B.CONTACT_W / 2 - 0.7, yp + B.CONTACT_W / 2 + 0.7),
                                    (B.RIM_Z - 0.01, CONTACT_NOTCH_TOP)),
                                   ((yp - B.RIB_GAP / 2 - B.RIB_W - 0.2, yp + B.RIB_GAP / 2 + B.RIB_W + 0.2),
                                    (B.RIM_Z - 1.2, B.RIM_Z + 0.1))):
            out.append(trimesh.creation.box(bounds=[[-x1 - 10.0, y0, 0.8 - z1], [-x0 - 10.0, y1, 0.8 - z0]]))
    return out


# Top pocket, two clean boxes stacked, both running the full depth to her far wall:
# - the earpiece's part: Alley Cat's own pocket (x -52.2..-35.8, far wall at y 107.5), whose side walls hold the
#   earpiece holder, with its floor 0.5 mm lower (z -11.1 -> -11.6) so the low holder sits lower;
# - the GPS antenna's part above it: 19.5 mm wide, as wide as the back's slot (x 24.25-43.75 there), from the low
#   holder's roof (z -8.2) straight up through the top. The step between them is level with the holder's roof, so
#   the antenna stands on one flat surface: the roof in the middle and the steps under its ends.
EAR_POCKET_X = (-52.2, -35.8)
POCKET_NEW_X = (-B.TOPGPS_X[1] - 10.0, -B.TOPGPS_X[0] - 10.0)                # -53.75 .. -34.25
POCKET_Y = (100.2, 107.5)          # her near edge (open to the T-Deck) and far wall
POCKET_FLOOR_Z, POCKET_STEP_Z, POCKET_TOP_Z = -11.6, -8.2, 7.4


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


def plain_left_wall(src):
    """The stretch of the left wall to rebuild (a box to clear) and the plain wall piece that replaces it."""
    sec = src.section(plane_origin=[0, LEFT_WALL_SECTION_Y, 0], plane_normal=[0, 1, 0])
    p2, _ = sec.to_planar(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float), check=False)
    x0, x1 = LEFT_WALL_X
    profile = unary_union(list(p2.polygons_full)).intersection(shapely_box(x0, LEFT_WALL_Z0 - 0.05, x1, 10.0))
    assert profile.geom_type == "Polygon", "the wall's cross-section should be one piece"
    y0, y1 = LEFT_WALL_Y
    clear = trimesh.creation.box(bounds=[[x0, y0, LEFT_WALL_Z0], [x1, y1, 10.0]])
    wall = F.prism_y(profile, y0 - 0.05, y1 + 0.05)          # overlaps the unchanged wall by 0.05 at each end
    return clear, wall


def hold_bump(src):
    """Alley Cat's bump that holds the T-Deck down, beside the reset opening: her front's solid in HOLD_BUMP_REGION."""
    return trimesh.boolean.intersection([trimesh.creation.box(bounds=HOLD_BUMP_REGION), src], engine="manifold")


def reset_opening(src):
    """Alley Cat's reset opening and its recesses: the empty space of her front in RESET_REGION."""
    return trimesh.boolean.difference([trimesh.creation.box(bounds=RESET_REGION), src], engine="manifold")


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
    in_wall = trimesh.creation.box(bounds=[[SPEAKER_FLOOR_X - 0.05, 0.0, -5.5], [SPEAKER_FLOOR_X + 0.9, 60.0, -3.0]])
    (_, y0, _), (_, y1, _) = trimesh.boolean.intersection([space, in_wall], engine="manifold").bounds   # the cavity
    down = trimesh.creation.box(bounds=[[SPEAKER_FLOOR_X, y0, SNAP_RIDGE_TOP], [SPEAKER_FLOOR_X + 1.1, y1, -5.6]])
    return trimesh.boolean.union([space, down], engine="manifold")


def top_pocket():
    """The earpiece's pocket (her width, lowered floor) and the GPS antenna's slot above it, both to the far wall."""
    y0, y1 = POCKET_Y
    return [trimesh.creation.box(bounds=[[EAR_POCKET_X[0], y0, POCKET_FLOOR_Z], [EAR_POCKET_X[1], y1, POCKET_STEP_Z + 0.01]]),
            trimesh.creation.box(bounds=[[POCKET_NEW_X[0], y0, POCKET_STEP_Z], [POCKET_NEW_X[1], y1, POCKET_TOP_Z]])]


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
    src_front = trimesh.load(src, force="mesh")
    speaker = moved_speaker_space(front)
    clear, wall = plain_left_wall(src_front)
    out = trimesh.boolean.union([trimesh.boolean.difference([front, clear], engine="manifold"), wall, hold_bump(src_front)],
                                engine="manifold")
    cuts = trimesh.boolean.union([speaker, sim_scoop(), reset_opening(src_front)]
                                 + sd_icon_big() + sim_slit() + sim_icon() + top_pocket() + contact_notches(scale),
                                 engine="manifold")
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
