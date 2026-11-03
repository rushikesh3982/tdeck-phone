# Case files

Modified from **"Lilygo T-Deck TD1 Case" by Alley Cat**, Printables model 741124,
https://www.printables.com/model/741124-lilygo-t-deck-td1-case, licensed
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The STL files and images in this folder are
changed versions of that design and are shared under the same licence, CC BY-SA 4.0. The originals are on
Printables. (The script in `scripts/` is MIT, like the rest of the repository.)

| File | What it is | Changed from |
|---|---|---|
| [front-earpiece-mic.stl](front-earpiece-mic.stl) | Front, with earpiece grille and mic pocket | `Alley Chat TD1 Standard Front GPS Inserts.stl` |
| [test-mic-coupon.stl](test-mic-coupon.stl) | Small test print: 18 mm of the bottom wall around the mic pocket | the front above |

Everything else (X back, Switch, Antenna Plug, Reset Button) is unchanged for now, so print those from the
Printables download. The back gets its own changes next (see [../docs/case.md](../docs/case.md)).

## Front: what changed

Only these cuts were made. The outer size and everything else are exactly as the original.

**Earpiece grille.** A 1 × 6 mm slot with rounded ends goes through the 3.6 mm face above the screen. It is
centred under the GPS pocket, which measures 16.4 × 7.3 mm inside.

- The receiver lies on the pocket floor, facing the slot.
- Its foam ring goes between it and the floor, and foam behind it keeps it pressed down.
- **The receiver has to fit inside 16.4 × 7.3 mm.** Measure the Micromax receiver before printing.

**Microphone.** In the bottom edge, 15 mm left of the USB-C opening as you look at the screen. This is the corner
that points toward your mouth when the phone is at your right ear.

- **Pocket:** 6.3 mm round, opening on the inside of the case. Its top is pointed (a "teardrop") so it prints
  without supports.
- **Skin and sound hole:** 1.2 mm of plastic is left at the outside, with a 1.5 mm sound hole through it.
- **Fitting the mic:** push the Sunrom 6027 (6 × 2.7 mm) in from inside until it touches the skin. Hold it with a
  dab of glue.
- **Wire groove:** a 2.4 mm groove runs from the pocket up the inside wall and through the mating lip, so the
  two mic wires reach the back half without the T-Deck pinching them.
- **Before soldering:** trim the mic's pins short and bend the wires flat. There are 1.5–3.7 mm behind the mic
  before the inside surface of the wall.

![Screen side](images/front-screen-side.png)

![Close-ups from inside: mic pocket with sound hole and wire groove (left), earpiece slot in the GPS pocket (right)](images/front-cuts-inside.png)

## Printing

- Print the files as they are oriented: screen side down on the bed, no supports. The slot is vertical, and the
  mic pocket has a 45° roof.
- PLA+ or PETG, 0.2 mm layers, 3 perimeters, 20 % infill.
- In the slicer preview, check that the 1 mm slot and the 1.5 mm sound hole are open.
- **Print `test-mic-coupon.stl` first** (a few minutes). Check that the mic slides in and sits against the skin. If
  it's too tight or too loose, the pocket size can be changed in the script.

## Making the front again

`scripts/make_front.py` makes the front from the original Printables file. All sizes are set at the top of the
script. It needs Python with numpy, trimesh, shapely and manifold3d:

```
python scripts/make_front.py "Alley Chat TD1 Standard Front GPS Inserts.stl" front-earpiece-mic.stl
```
