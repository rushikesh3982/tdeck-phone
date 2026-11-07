# Case

Base design: **"Lilygo T-Deck TD1 Case" by Alley Cat**, Printables model 741124,
https://www.printables.com/model/741124-lilygo-t-deck-td1-case. Licensed
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): credit is required, and modified files must be
shared under the same licence.

The outside size of the case does not change.

## Source files (Alley Cat's originals on Printables)

You don't need to download anything to print: everything is in [case/stl/](../case/stl/). These are the
originals the scripts start from, and where the unchanged small parts were copied from.

| File | Use |
|---|---|
| `Alley Chat TD1 Standard Front GPS Inserts.stl` | Front |
| `Alley Chat TD1 X Back Outside Cat Edition.stl` | Back (gives 23 mm behind the T-Deck). The Outside Cat edition is the source for our back, with its cat replaced by the rushiWorks logo |
| `Alley Chat TD1 Switch.stl` | Slider for the T-Deck's own power switch (right side). Copied unchanged to case/stl/ |
| `Alley Chat TD1 Reset Button.stl` | Button for the T-Deck's reset (left side). Copied unchanged to case/stl/ |
| `Alley Chat TD1 X Antenna Plug.stl` | Only for an SMA hole left empty. Needed only if the internal LTE sticker antenna replaces the 4G SMA antenna (top-right hole). Copied unchanged to case/stl/ |
| `Alley Cat TDeck Back Cover Custom.step` | "S" back, used only for its mating edge when drawing the new back |

Print the modified front and back from this repository ([case/stl/](../case/stl/)), not the downloaded ones.

Fasteners: 2× M3×5 heat-set inserts (4.5 mm hole) + 2× M3×8 screws.

Printing: ASA (ours), PLA+ or PETG; 0.2 mm layers, 3 perimeters, 20 % infill, no supports.

**Fit:** the T-Deck's fit is deliberately tight. The inside of Alley Cat's front is exactly the T-Deck's 68 mm,
with a snap ridge. We print in **ASA**, which shrinks a little more as it cools. The parts built **1 % larger** fit
our T-Deck and everything else well (7 Nov 2026), so [case/stl/](../case/stl/) holds that 101 % set.
- **Already scaled:** print the files at 100 % in the slicer.
- **Don't scale them in the slicer:** scaling there would move the modem standoffs off the board's holes.
- **On a different printer or filament:** print the 9 mm fit-test ring first. See "Fit and scale" in
  [case/README.md](../case/README.md).

## Why these variants

The **Standard front** keeps the pocket for the T-Deck's speaker, which plays the ringtone. The **GPS** version of
the front adds a module pocket at the top centre above the screen. It measures 16.4 × 7.3 mm inside, and becomes the
**earpiece pocket**.

The GPS front also has a **slide-switch mount on its left side**. It is a slider window between two screw holes
15 mm apart, about 52–75 mm up from the bottom edge, and was meant for the GPS module's power switch. (The
"Switch" file is something else: the slider for the T-Deck's own power switch on the right side.) This project
uses the mount for the **modem's own on/off switch**, an SS-12F15, the switch it was drawn for (see
[wiring.md](wiring.md), section 2). It is kept exactly as in Alley Cat's file.

The **X back** gives 23 mm of depth behind the T-Deck, enough for the modem board and battery.

Rejected: the Slim front (no speaker pocket), and the Nuts and TBall variants.

## T-Deck edge layout (from LilyGO's product photo)

- Grove socket: one top corner
- ESP32-S3 module (Wi-Fi/BT antenna): top centre
- Power switch: right side edge
- USB-C: bottom edge

## Front changes

The earpiece and mic cuts are done (3 Nov 2026): [case/stl/front-earpiece-mic.stl](../case/stl/front-earpiece-mic.stl).
Full details are in [case/README.md](../case/README.md).

- **Earpiece (done):** a 1 × 6 mm slot through the 3.6 mm face above the screen, centred under the GPS pocket.
  - The receiver lies on the pocket floor facing the slot. It is 12 × 6 mm. It is 2 mm thick with its rubber
    gasket, and 3 mm with its two contacts folded over its back.
  - **Earpiece holder (done, 4 Nov 2026):** [case/stl/earpiece-holder.stl](../case/stl/earpiece-holder.stl). It is a printed
    block that fills the pocket and presses on the middle of the receiver's back (a 1.7 mm cup, 3.5 mm deep at
    both ends for the folded contacts). The cup is open on its far side, where the pocket wall holds the 6 mm
    receiver. Each wire goes up its own groove toward the T-Deck, and the back closes 0.1 mm above the holder.
- **Microphone (done):** bottom edge, 15 mm left of the USB-C opening as you look at the screen. That corner points
  toward the mouth when the phone is at the right ear.
  - A 6.3 mm pocket opens on the inside, with a 1.2 mm skin and a 1.5 mm sound hole.
  - A wire groove runs up the inside wall and through the mating lip.
- **Second SMA antenna cut-out (done):** the Grove socket is desoldered from the T-Deck and the wires are soldered
  to its pads, so the Grove plug slot in the top-right corner is filled in. The corner gets an exact mirror of the
  top-left SMA cut-out:
  - 6.56 mm hole through a 2 mm wall;
  - 8.4 mm hex pocket inside;
  - 12 mm nut recess outside.

  The KTRON IPX → SMA-female cable fits it. Before printing, check that the connector's tail (3–8 mm past the
  T-Deck's top edge) clears the T-Deck in that corner. Either antenna can go in either corner. 4G top-right is
  recommended (see [case/README.md](../case/README.md)).
- **Modem power switch:** an SS-12F15 slide switch in Alley Cat's original left-side mount (kept, not filled). The
  battery sits about 9 mm toward the phone's right to clear it.
- **microSD picture (added 7 Nov 2026):** an engraved microSD outline beside the T-Deck's microSD opening on the right
  side, toward the phone's top. It shows which way the card goes: with the phone screen-up, gold contacts up,
  contacts end first. Details are in [case/README.md](../case/README.md).
- **Top-edge badge:** Alley Cat's cat-head logo, from her TD1 files (the same cat as on her HT Pocket case), on a
  fresh badge of the original footprint. It's a visible credit to the case's designer. The head is recessed and the
  eyes and nose are cut deeper. It reads upright with the phone screen-up.

## Back changes

**First version ready to print and dry-fit (3 Nov 2026):** [case/stl/back-modem-gps.stl](../case/stl/back-modem-gps.stl),
made by [case/scripts/make_back.py](../case/scripts/make_back.py) from the X back. Details and pictures are in
[case/README.md](../case/README.md).

KTRON board (from KTRON's drawing): **54.33 × 57.23 mm**, four 3.2 mm holes on a **47.90 × 50.70 mm** rectangle,
about 3.2 mm in from each edge. The 4G socket (U.FL1) is on the top edge. The GPS socket (U.FL2) is on the left
edge, low down. The micro-SIM (push-push holder on the solder side) slides in from the bottom edge, at the end
nearest the VDD/RX/TX header.

- **Outside:** built from the *Outside Cat* edition (middle grooves shortened). The cat head is filled, and the
  rushiWorks logo is engraved in its place (24 × 17 mm, 1 mm deep).
- **Inside floor:** Alley Cat's engraved cat head and "Alley Chat TD1 X" text are filled flat (they're hidden once
  assembled). The cat-head logo on the front's top-edge badge credits the designer instead.
- **Modem board** on four 9 mm standoffs with M3 heat-set insert holes (4.5 mm), 7 mm wide with a 10 mm foot.
  - **Placement:** top half, component side toward the back cover.
  - **Orientation:** the SIM edge faces the phone's **left** side. That puts the 4G socket on the right, toward
    the planned 4G antenna corner, and the GPS socket near the bottom, right above the patch.
  - **Fixing:** M3 × 6 screws from the solder side.
  - **Capacitor swap:** the 9 mm height needs the KTRON's two 11 mm capacitors replaced by radial ones laid flat
    ([bring-up.md](bring-up.md), phase B).
- **SIM slit** in the left wall, 15 × 1.8 mm, flared on the outside, in line with the SIM holder. It is fully in the
  back panel, 4.65 mm below the rim. An engraved picture beside it, toward the phone's top, shows which way the card goes in (added
  7 Nov 2026; see [case/README.md](../case/README.md)).
- **GPS patch cradle** in the bottom half, about 90 mm from the 4G antenna corner.
  - A 27 mm square opening with a 7 mm fence, for the measured 26 × 26 mm patch with its 25 × 25 × 4 mm ceramic.
  - The ceramic faces down onto four 0.5 mm pads.
  - There is a cable notch in every side, and the patch is fixed with glue.
- **Old GPS-module slot filled:** its back half (16.4 × 6.1 × 10 mm, between the two case-screw holes) is filled
  solid. The earpiece holder only fills the front's part, and the filled block caps it.
- **Network LED window**: a printed light tube under the KTRON's NETLIGHT LED, and a 1.6 mm hole through the
  back cover (in a decorative groove). There is no window for the power LED.
- **Battery** (65 × 55 × 9 mm) lies over the board, its long side top to bottom, with its connector end over the
  patch.

**Still to do:** after the dry fit, maybe a retainer for the battery.

### Depth check (23 mm available)

Measured from the inside floor of the back. The T-Deck (11 mm thick, LilyGO's figure) leaves 23 mm.

| Stack | Total |
|---|---|
| Modem board: 9 standoffs + 1.6 board + 1.5 SIM holder + 1 foam + 9 battery | **22.1 mm** |
| Same with the stock 11 mm capacitors (12 mm standoffs) | **25.1 mm: doesn't fit**, hence the capacitor swap |
| GPS patch: 0.5 pads + 4 ceramic + 1.6 board + ~2.5 shield | **~8.6 mm** (the battery passes above it) |

## Order of work

1. Print the front, the back, the earpiece holder and Alley Cat's small parts from [case/stl/](../case/stl/) (done: the
   101 % set fits).
2. Swap the KTRON's two tall capacitors after the 5 V bench tests ([bring-up.md](bring-up.md), phase B).
3. Dry-fit the T-Deck, modem board, battery, patch and antennas, and check that a SIM goes in through the slit.
