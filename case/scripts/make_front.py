"""Cut the earpiece grille, mic pocket and a second SMA antenna cut-out into the Alley Cat TD1 front,
and fill the unused slide-switch mount on its left side.

Usage:
    python make_front.py "<Alley Chat TD1 Standard Front GPS Inserts.stl>" <output.stl>

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

# The GPS version's slide-switch mount on the left side (window, two countersunk screw holes, and the
# recess for the switch body on the inside) is not used: the modem follows the T-Deck's power switch.
# It is filled by copying the wall's normal cross-section, taken just beside the mount (y = 77, where
# the wall is untouched and the T-Deck already fits), across y = 51.0..75.6. Kept clear: the Reset
# Button opening below it and the small recess around it for the button's flange (z below -3.4).
SWITCH_WALL_SLICE_Y = 77.0
SWITCH_FILL_Y = (51.0, 75.6)
SWITCH_FILL_CLIP = (-10.6, -4.15, -5.9, 4.3)        # x0, z0, x1, z1 of the wall slice used
RESET_KEEP_OUT = [[-12.0, 65.0, -10.0], [-5.0, 72.0, -3.4]]


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


def main(src, dst):
    front = trimesh.load(src, force="mesh")
    assert front.is_watertight, "source mesh is not watertight"
    front = mirror_sma_cutout(front)
    front = fill_switch_mount(front)

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
    main(sys.argv[1], sys.argv[2])
