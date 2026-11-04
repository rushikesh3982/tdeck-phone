"""Cut a short fit-test ring from the front: the screen face, the walls and the snap ridge that hold the T-Deck.

Usage:
    python make_fit_test.py <front-earpiece-mic.stl> <output folder>

Writes test-fit-ring-100.stl and test-fit-ring-101.stl. Print them screen side down like the front, and press the
T-Deck in. The ring is only a gauge. Its scale must not be applied to the finished case files in the slicer,
because the modem standoffs, inserts and other parts must stay true to size (see case/README.md, "Fit and scale").

Why: the front's inside is drawn at exactly the T-Deck's 68.00 mm width for the first 5 mm above the screen
face (z -13.7..-8.8). A ridge at z -8.8..-6.4 then narrows it to 67.4-67.5 mm. That ridge snaps over the T-Deck's
side and holds it, and the case is meant to flex as the T-Deck goes in. So the fit depends on how a given printer
and filament come out, to a few tenths of a millimetre.
"""
import os
import sys

import trimesh

CUT_Z = -5.5          # keeps the screen face (z -14.7), the 68.00 mm walls and the whole snap ridge
SCALES = (1.00, 1.01)


def main(front_path, out_dir):
    front = trimesh.load(front_path, force="mesh")
    lo, hi = front.bounds
    keep = trimesh.creation.box(bounds=[[lo[0] - 1, lo[1] - 1, lo[2] - 1], [hi[0] + 1, hi[1] + 1, CUT_Z]])
    ring = trimesh.boolean.intersection([front, keep], engine="manifold")
    assert ring.is_watertight
    rlo, rhi = ring.bounds
    centre = [(rlo[0] + rhi[0]) / 2, (rlo[1] + rhi[1]) / 2, rlo[2]]
    for s in SCALES:
        m = ring.copy()
        m.apply_translation([-c for c in centre])
        m.apply_scale(s)
        m.apply_translation(centre)
        path = os.path.join(out_dir, f"test-fit-ring-{round(s * 100)}.stl")
        m.export(path)
        b = m.bounds
        print(f"{os.path.basename(path)}: {b[1][0] - b[0][0]:.2f} x {b[1][1] - b[0][1]:.2f} x {b[1][2] - b[0][2]:.2f} mm, "
              f"{m.volume / 1000:.1f} cm^3, inside width at the screen side {68.0 * s:.2f} mm")


if __name__ == "__main__":
    main(*sys.argv[1:3])
