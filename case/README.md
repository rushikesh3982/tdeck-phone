# Case files

Modified from **"Lilygo T-Deck TD1 Case" by Alley Cat**, Printables model 741124,
https://www.printables.com/model/741124-lilygo-t-deck-td1-case, licensed
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The STL files and images in this folder are
changed versions of that design and are shared under the same licence, CC BY-SA 4.0. The originals are on
Printables. (The script in `scripts/` is MIT, like the rest of the repository.)

| File | What it is | Changed from |
|---|---|---|
| [front-earpiece-mic.stl](front-earpiece-mic.stl) | Front, with earpiece grille, mic pocket, a second SMA antenna cut-out, the unused switch mount filled, Alley Cat's cat-head logo on the top-edge badge, and "rushiworks" along the right bezel | `Alley Chat TD1 Standard Front GPS Inserts.stl` |
| [test-mic-coupon.stl](test-mic-coupon.stl) | Small test print: 18 mm of the bottom wall around the mic pocket | the front above |
| [earpiece-holder.stl](earpiece-holder.stl) | Small block that fills the earpiece pocket and holds the earpiece on the grille slot | new part, sized to the front's pocket |
| [back-modem-gps.stl](back-modem-gps.stl) | Back with modem standoffs, SIM slit, GPS patch cradle, network-LED window, the back's half of the old GPS-module slot filled, and the rushiWorks logo on the outside (first version: print and dry-fit) | `Alley Chat TD1 X Back Outside Cat Edition.stl` |

The other parts (Switch, Antenna Plug, Reset Button) are unchanged, so print those from the Printables download.

**Assembly diagrams** (what every cut-out is for, and where each part goes) and the step-by-step assembly order are in
[../docs/assembly.md](../docs/assembly.md).

## Front: what changed

Only these changes were made. The outer size and everything else are exactly as the original.

**Earpiece grille.** A 1 × 6 mm slot with rounded ends goes through the 3.6 mm face above the screen. It is
centred under the GPS pocket, which measures 16.4 × 7.3 mm inside.

- The receiver (the Micromax one) lies on the pocket floor, facing the slot, with its rubber gasket against the floor.
  It is about 13 × 5 mm and 2 mm thick with the gasket. Its two spring contacts, folded over its back at the short
  ends, make it 3 mm.
- The [earpiece holder](#earpiece-holder) goes in on top of it and keeps it pressed down.

**Microphone.** In the bottom edge, 15 mm left of the USB-C opening as you look at the screen. This is the corner
that points toward your mouth when the phone is at your right ear.

- **Pocket:** 6.3 mm round, opening on the inside of the case. Its top is pointed (a "teardrop") so it prints
  without supports.
- **Skin and sound hole:** 1.2 mm of plastic is left at the outside, with a 1.5 mm sound hole through it.
- **Fitting the mic, before the T-Deck goes in:** the pocket opens on the inside face of the bottom wall, which
  the T-Deck covers once it's in. Push the Sunrom 6027 (6 × 2.7 mm) in from inside until it touches the skin. Hold
  it with a dab of glue, lay its wires in the groove, then fit the T-Deck.
- **Wire groove:** a 2.4 mm groove runs from the pocket up the inside wall and through the mating lip, so the
  two mic wires reach the back half without the T-Deck pinching them.
- **Before soldering:** trim the mic's pins short and bend the wires flat. There are 1.5–3.7 mm behind the mic
  before the inside surface of the wall.

**Alley Cat's cat-head logo on the top-edge badge.** It's a visible credit to the case's designer.

- **Badge:** the original badge (cat ears + GPS pin) is replaced by a fresh one of the same footprint: a 1 mm raised
  pad with 45° bevels and a 16.8 × 10.5 mm face.
- **The cat:** the cat head is taken from Alley Cat's own TD1 files, and is the same cat as on her *Alley Chat HT
  Pocket* case (see [logo/](logo/)). It's 9.4 mm tall and cut the same way as on the HT Pocket: the head recessed
  0.35 mm, the closed eyes and nose 0.7 mm deep.
- **Orientation:** it reads upright when the phone lies screen-up, with the ears toward the screen side.

![Top edge with the phone screen-up: 4G SMA cut-out, Alley Cat's cat-head badge, LoRa SMA cut-out](images/front-top-edge.png)

**"rushiworks" along the right bezel.** Engraved on the screen side, beside the screen, reading bottom-to-top with
the tops of the letters toward the screen.

- **Font and size:** DejaVu Sans Mono Bold (a coding font, free licence), 4.2 mm tall and 29 mm long, with strokes
  about 0.7 mm.
- **Depth:** that part of the face is a 1 mm lip lying on the T-Deck's front, so the engraving is 0.3 mm deep and
  0.7 mm of plastic stays behind it.
- **Optional:** fill it with paint for contrast.

![Screen side, right half: rushiworks along the right bezel](images/front-side-text.png)

**Unused switch mount filled.** The GPS version's slide-switch mount on the left side (a window and two
countersunk screw holes) isn't used, because the modem follows the T-Deck's power switch. It is filled
completely, including the recess for the switch body on the inside. The fill copies the wall's normal shape from
just beside the mount, so inside and out the wall now matches the rest of the side, where the T-Deck already fits.
The Reset Button opening just below stays, with its small inside recess for the button's flange. So does a small
original bump on the inside wall below the old switch, up to 0.8 mm high.

**Second SMA antenna cut-out (top-right corner).** The Grove socket is desoldered from the T-Deck and the modem
wires are soldered to its pads, so the Grove plug slot in that corner is no longer needed. It is filled in, and the
corner gets an exact mirror image of the case's own SMA cut-out from the top-left corner. Its fit with the KTRON
IPX → SMA-female cable (KSTA0380):

| Cut-out (both corners) | Size | KTRON connector | Fit |
|---|---|---|---|
| Hole through the wall | Ø 6.56 mm | SMA thread 6.35 mm | ✓ 0.2 mm clearance |
| Hex pocket on the inside, 3 mm deep | 8.4 mm across flats | 8 mm hex collar | ✓ snug, and stops it turning when the antenna is tightened |
| Nut recess on the outside, 2.8 mm deep | Ø 12 mm | 8 mm nut + lock washer | ✓ sits just below the surface |
| Wall | 2 mm | 9.5 mm thread (typical) | leaves about 4.7 mm outside for the antenna. Measure yours: it needs at least 9 mm |

- **Check on the T-Deck before printing:** the case's wall block in that corner is 7.8 mm deep. The connector's
  hex collar, crimp and heat-shrink reach about 11–16 mm in from the outer surface. So 3–8 mm of it goes past the
  T-Deck's top edge, level with the T-Deck's back surface. With the Grove socket removed, hold the connector in
  that corner and check that nothing on the T-Deck is in the way. In the top-left corner, the LoRa connector already
  uses the same space.
- **Which antenna where:** see below.

Both top corners now have identical SMA cut-outs, so either antenna can go in either corner. **Recommended:** 4G
in the top-right (old Grove corner), and the T-Deck's LoRa connector staying top-left, where it already sits.
From the top-right, the 4G cable drops straight into the empty strip beside the modem board, to its 4G socket on
that side (about 4 cm; the 10 cm cable is plenty). From the top-left, it would have to get around the battery,
which covers the board with only about 1 mm to spare (about 11 cm, so use the 15 cm cable).

![Screen side](images/front-screen-side.png)

![Close-ups from inside: mic pocket with sound hole and wire groove (left), earpiece slot in the GPS pocket (right)](images/front-cuts-inside.png)

## Earpiece holder

[earpiece-holder.stl](earpiece-holder.stl) is a new printed part, 16.0 × 6.9 × 16.5 mm. It fills the front's old
GPS-module pocket and keeps the earpiece pressed onto the grille slot. In the GPS version of the case, the
module's slot ran from the front up into the back. The back's half is now filled solid (see the back changes
below), so the holder only fills the front's part.

![Earpiece holder: views, and a cut through the closed case](images/earpiece-holder.png)

- **Cup:** the earpiece sits in a 13.4 × 5.4 mm cup on the holder's underside, centred over the slot.
  - **Middle:** the cup is 1.7 mm deep here, and the holder presses on the middle of the earpiece's back. That squeezes
    the 2 mm body and gasket 0.3 mm onto the pocket floor, sealing the sound path to the slot.
  - **Ends:** over the last 3 mm at each end the cup is 3.5 mm deep. That leaves room for the folded contacts (1 mm)
    and their solder joints.
- **Held by the back:** the holder stands on the pocket floor, and its top ends 0.1 mm under the back's filled block.
  Once the case is closed, it can't lift.
- **Wires:** from the solder joints at both ends, the wires run to the middle along a 2 mm path on the T-Deck side of
  the cup. They then go up a 3 × 2.4 mm groove on the face toward the T-Deck, and over the T-Deck to the modem.
- **Fit:** 0.2 mm clearance all round in the pocket. The script checks that it touches neither case half.
- **If your earpiece is shorter:** at 12 mm it can slide about 1.4 mm along the cup, but it still covers the 6 mm
  slot. A scrap of tape at one end of the cup centres it.
- **Printing:** lay it on the face with the wire groove (the face toward the T-Deck). Then no supports are needed.

## Back: what changed

**Outside.** Made from Alley Cat's *Outside Cat* edition of the X back. It has the same vertical grooves, with the
three middle ones shortened, which leaves a clear area near the top. That area had a cat-head outline engraved in
it. The cat is filled flush, and the **rushiWorks logo** is engraved in its place:

- **Size:** 24 × 17 mm, 1 mm deep, matching the grooves. The letter strokes are about 0.8 mm wide.
- **Clearances:** it stays clear of the grooves and of the two case-screw countersinks.
- **Orientation:** it reads normally when you look at the back with the phone upright.
- **Printing:** the back prints face-down, so the logo forms in the first layers and comes out crisp.
- **Inside:** identical to the Inside Cat edition, so all the changes below are the same with either.
- **Inside floor:** Alley Cat's engraved cat head and "Alley Chat TD1 X" text (hidden once assembled) are filled
  flat. The designer is credited by the badge kept on the front's top edge and in the README.

![Back cover from outside: Outside Cat groove layout with the rushiWorks logo](images/back-outside.png)

![Back from inside: layout of the modem board and GPS patch](images/back-layout.png)

![Back from inside and from outside](images/back-preview.png)

**Old GPS-module slot filled.** The GPS version's module slot continued from the front's pocket up into the back:
16.4 × 6.1 mm, 10 mm tall, in the thick block between the two case-screw holes. Only the earpiece uses the
front's part of it now, so the back's part is filled solid. The fill copies the block's cross-section from just beside
the slot, so the block now runs unbroken between the screw holes and caps the earpiece holder.

**Modem standoffs.** Four columns at the KTRON board's holes.

- **Board:** the KTRON is 54.33 × 57.23 mm, with its holes on a 47.90 × 50.70 mm rectangle.
- **Columns:** 7 mm wide, with a 10 mm foot, and their tops 9 mm above the inside floor. The two next to the left
  wall are joined to it.
- **Inserts:** each column has a 4.5 mm hole, 6 mm deep, for an M3 × 5 heat-set insert. The board is held with
  M3 × 6 screws from its solder side.
- **Board orientation:** component side down toward the back cover. The SIM edge faces the phone's left side,
  0.6 mm from the wall. The 4G socket faces right, and the GPS socket is at the bottom, just above the patch.
- **9 mm only works after the capacitor swap.** The KTRON's two 11 mm tall capacitors are replaced by radial
  ones laid flat (see [../docs/bring-up.md](../docs/bring-up.md), phase B). Nothing on the board's component side
  may stand more than 8 mm high.

**SIM slit.** Through the left side wall, in line with the SIM holder.

- **Size:** 15 × 1.8 mm on the inside, flaring to about 16 × 3 mm on the outside so the card finds its way in.
- **Position:** its centre is 11.35 mm above the inside floor and 4.65 mm below the rim, so it is entirely in the
  back panel. That is the card's height in a standard 1.5 mm push-push micro-SIM holder sitting on a board on 9 mm
  standoffs.
- **Using it:** push the card in until it clicks, using a fingernail or a SIM pin. Push again to release it, then
  pull it out.
- **SIM size:** a nano-SIM in a micro adapter can catch in push-push holders. A fresh multi-cut SIM, popped out at
  micro size, is safer.

![Left side of the back from outside, showing the SIM slit](images/back-sim-slit.png)

**GPS patch cradle.** A fence with a 27 mm square opening near the bottom. It is sized for the measured patch:
26 × 26 mm board and a 25 × 25 × 4 mm ceramic that sits slightly crooked.

- **Pads:** the ceramic faces down and rests on four 3 mm pads, 0.5 mm high, so it stays just off the cover.
- **Fence:** 7 mm tall.
- **Cable notches:** 4 mm wide, in every side, for the cable that leaves the middle of one side of the board.
- **Fixing:** a dab of hot glue at two corners. The 95 mm cable easily reaches the GPS socket about 6 mm away.

**Network LED window.** The KTRON's network LED (NETLIGHT) faces the back cover from 9 mm up.

- **Light tube:** 3.6 mm bore, from the floor to 1.6 mm under the board, so the light goes straight out and the
  power LED next to it doesn't leak through.
- **Hole:** 1.6 mm through the cover, on the flat floor of the decorative groove beside the LED (1 mm thick there).
- **Where it shows:** near the top of the back, on the phone's right side. When you look at the back, that's the
  top-left area.
- **Blink pattern** (SIMCom): lit steadily while searching for the network; 200 ms on / 200 ms off once
  registered.
- **Optional:** a drop of clear glue or UV resin seals the hole and spreads the light.

**Depth** (inside floor to the T-Deck's back, 23 mm with LilyGO's 11 mm T-Deck): 9 standoffs + 1.6 board + 1.5 SIM
holder + 1 foam + 9 battery = 22.1 mm. The battery (65 × 55 × 9 mm) lies over the board, its long side running top
to bottom, with its connector end toward the bottom, over the patch.

## Printing

- Print the files as they are oriented, outer face down on the bed (the screen side for the front), with no
  supports. The earpiece slot is vertical, the mic pocket has a 45° roof, and the back's standoffs and cradle grow
  straight up.
- PLA+ or PETG, 0.2 mm layers, 3 perimeters, 20 % infill.
- The earpiece holder is the exception: lay it on its wire-groove face (see [Earpiece holder](#earpiece-holder)).
- In the slicer preview, check that the 1 mm slot and the 1.5 mm sound hole are open.
- **Print `test-mic-coupon.stl` first** (a few minutes). Check that the mic slides in and sits against the skin. If
  it's too tight or too loose, the pocket size can be changed in the script.

## Making the front again

`scripts/make_front.py` makes the front from the original Printables file. All sizes are set at the top of the
script. It needs Python with numpy, trimesh, shapely and manifold3d:

```
python scripts/make_front.py "Alley Chat TD1 Standard Front GPS Inserts.stl" front-earpiece-mic.stl
python scripts/make_back.py "Alley Chat TD1 X Back Outside Cat Edition.stl" back-modem-gps.stl images/back-layout.png
python scripts/make_earpiece_holder.py earpiece-holder.stl images/earpiece-holder.png front-earpiece-mic.stl back-modem-gps.stl
python scripts/make_diagrams.py front-earpiece-mic.stl back-modem-gps.stl images
```

The back script reads the logo from `logo/rushi-logo.jpg`, and also needs pillow and matplotlib to trace it.
