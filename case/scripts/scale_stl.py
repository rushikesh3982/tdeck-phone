"""Scale a part uniformly (for Alley Cat's small parts in a larger case set: Switch, Reset Button, Antenna Plug).

Usage:
    python scale_stl.py <input.stl> <output.stl> <scale>

These parts fit openings in the case, so they grow with it. The front, back and earpiece holder have their own
--scale option instead, because parts of them must stay true to size.
"""
import sys

import trimesh


def main(src, dst, scale):
    m = trimesh.load(src, force="mesh")
    m.apply_scale(float(scale))
    assert m.is_watertight
    m.export(dst)
    lo, hi = m.bounds
    print(f"{dst}: x{float(scale):g}, {hi[0] - lo[0]:.2f} x {hi[1] - lo[1]:.2f} x {hi[2] - lo[2]:.2f} mm")


if __name__ == "__main__":
    main(*sys.argv[1:4])
