"""Low earpiece holder for the 18650 version: the GPS antenna stands on its edge on this holder's flat roof.

It is make_earpiece_holder.py's holder cut down: the same cup (open on the far side, where the pocket's own wall holds
the earpiece), the same deeper pockets at both ends for the earpiece's folded contacts, and the same wire groove up the
T-Deck-side face from each end pocket. The front's pocket floor is 0.5 mm lower in the 18650 front (z -11.6), and the
tall tongue is gone: the roof is flat at z -8.2, 0.5 mm above the contacts' pockets (which leave 0.2 mm over the
folded contacts for their solder), which is where make_back_18650.py's height budget puts the antenna's lower edge. The antenna (about 18.5 mm wide) then sits on the roof (16 mm wide) with its
ends over the widened part of the pocket (make_front_18650.py).

The two earpiece wires leave the grooves at the roof and go up between the T-Deck's top edge and the antenna's board
(about 1 mm apart there) to the space behind the T-Deck.

Usage:
    python make_earpiece_holder_18650.py <output.stl>
    python make_earpiece_holder_18650.py --scale 1.01 <output.stl>

--scale works as in make_earpiece_holder.py: the pocket grows with the case, the earpiece and its cup stay true.
Coordinates are the front's (see make_earpiece_holder.py); the printed file is laid on the T-Deck-side face.
"""
import os
import sys

import trimesh
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_earpiece_holder as H  # noqa: E402

FLOOR_DROP = 0.5                  # the 18650 front's pocket floor is this much lower (make_front_18650.py)
PIN_SPARE = 0.2                   # over the folded contacts, for their solder (the current holder leaves 0.5)
ROOF_T = 0.5
ROOF_Z = H.FLOOR_Z - FLOOR_DROP + H.EAR_BODY_H - H.SQUEEZE + H.EAR_PIN_H + PIN_SPARE + ROOF_T     # -8.2: antenna's lower edge


def build_low_holder(roof_z=ROOF_Z, floor_z=None):
    x0, x1 = H.HOLDER_X
    y0, y1 = H.HOLDER_Y
    z0 = H.FLOOR_Z - FLOOR_DROP if floor_z is None else floor_z
    # side profile (y, z): the far wall's small fillet at the floor; flat roof
    side = Polygon([(y0, z0), (y1 - 0.5, z0), (y1, z0 + 0.5), (y1, roof_z), (y0, roof_z)])
    body = H.prism_x(side, x0, x1)
    plan = Polygon([(x0, y0), (x1, y0), (x1, y1 - 0.4), (x1 - 0.4, y1), (x0 + 0.4, y1), (x0, y1 - 0.4)])
    body = trimesh.boolean.intersection([body, H.prism_z(plan, z0 - 1, roof_z + 1)], engine="manifold")
    end = Polygon([(x0 + 0.3, z0), (x1 - 0.3, z0), (x1, z0 + 0.3), (x1, roof_z + 1), (x0, roof_z + 1), (x0, z0 + 0.3)])
    body = trimesh.boolean.intersection([body, H.prism_y(end, y0 - 1, y1 + 1)], engine="manifold")

    cx, _ = H.SLOT_CENTRE
    cl = H.EAR_L + H.CUP_SPARE
    xa, xb = cx - cl / 2, cx + cl / 2
    ya, yb = y0 + H.NEAR_WALL, y1 + 1
    press_z = z0 + H.EAR_BODY_H - H.SQUEEZE            # presses on the middle of the earpiece's back
    pin_z = press_z + H.EAR_PIN_H + PIN_SPARE          # folded contacts on the pressed earpiece, plus room for solder
    assert roof_z - pin_z >= ROOF_T - 0.01, "roof too thin over the contacts"
    cuts = [H.cuboid(xa, xb, ya, yb, z0 - 1, press_z),
            H.cuboid(xa, xa + H.PIN_ZONE, ya, yb, z0, pin_z),
            H.cuboid(xb - H.PIN_ZONE, xb, ya, yb, z0, pin_z)]
    for gx in (xa + H.PIN_ZONE / 2, xb - H.PIN_ZONE / 2):
        cuts.append(H.cuboid(gx - H.GROOVE_W / 2, gx + H.GROOVE_W / 2, y0 - 1, y0 + H.GROOVE_DEPTH, press_z, roof_z + 1))
    holder = trimesh.boolean.difference([body, trimesh.boolean.union(cuts, engine="manifold")], engine="manifold")
    assert holder.is_watertight
    return holder


def main(dst, scale=1.0):
    if scale != 1.0:
        H.use_scale(scale)
    floor_z = H.FLOOR_Z - FLOOR_DROP * scale            # the pocket (and its lowered floor) grows with the case;
    roof_z = floor_z + H.EAR_BODY_H - H.SQUEEZE + H.EAR_PIN_H + PIN_SPARE + ROOF_T    # the earpiece stack doesn't
    holder = build_low_holder(roof_z, floor_z)
    lo, hi = holder.bounds
    print(f"low holder {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f} mm, roof at z {hi[2]:.2f}, "
          f"{holder.volume:.0f} mm^3, scale {scale}")
    H.for_printing(holder).export(dst)
    return holder


if __name__ == "__main__":
    args = sys.argv[1:]
    sc = 1.0
    if args and args[0] == "--scale":
        sc = float(args[1]); args = args[2:]
    main(args[0], scale=sc)
