# Case

Base design: **"Lilygo T-Deck TD1 Case" by Alley Cat**, Printables model 741124,
https://www.printables.com/model/741124-lilygo-t-deck-td1-case. Licensed
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): credit is required, and modified files must be
shared under the same licence.

The outside size of the case does not change.

## Files to download

| File | Use |
|---|---|
| `Alley Chat TD1 Standard Front GPS Inserts.stl` | Front |
| `Alley Chat TD1 X Back Inside Cat Edition.stl` | Back (gives 23 mm behind the T-Deck) |
| `Alley Chat TD1 Switch.stl` | Slider for the T-Deck's own power switch (right side) |
| `Alley Chat TD1 X Antenna Plug.stl` | Only if the LoRa antenna stays inside |
| `Alley Cat TDeck Back Cover Custom.step` | "S" back, used only for its mating edge when drawing the new back |

The modified front is in this repository: [case/front-earpiece-mic.stl](../case/front-earpiece-mic.stl). Print that
instead of the downloaded front.

Fasteners: 2× M3×5 heat-set inserts (4.5 mm hole) + 2× M3×8 screws.

Printing: PLA+ or PETG, 0.2 mm layers, 3 perimeters, 20 % infill, no supports. Tolerances are tight, so print a
test piece first.

## Why these variants

The **Standard front** keeps the pocket for the T-Deck's speaker, which plays the ringtone. The **GPS** version of
the front adds a module pocket at the top centre above the screen. It measures 16.4 × 7.3 mm inside, and becomes the
**earpiece pocket**.

The GPS front also has a **slide-switch mount on its left side**. It is a slider window between two screw holes
15 mm apart, about 52–75 mm up from the bottom edge, and was meant for the GPS module's power switch. (The
"Switch" file is something else: the slider for the T-Deck's own power switch on the right side.) This project
doesn't need the mount, because the modem follows the T-Deck's own power switch (see [wiring.md](wiring.md),
section 2). The mount's holes stay open unless we decide to fill them.

The **X back** gives 23 mm of depth behind the T-Deck, enough for the modem board and battery.

Rejected: the Slim front (no speaker pocket), and the Nuts and TBall variants.

## T-Deck edge layout (from LilyGO's product photo)

- Grove socket: one top corner
- ESP32-S3 module (Wi-Fi/BT antenna): top centre
- Power switch: right side edge
- USB-C: bottom edge

## Front changes

The earpiece and mic cuts are done (3 Nov 2026): [case/front-earpiece-mic.stl](../case/front-earpiece-mic.stl).
Full details are in [case/README.md](../case/README.md).

- **Earpiece (done):** a 1 × 6 mm slot through the 3.6 mm face above the screen, centred under the GPS pocket.
  - The receiver lies on the pocket floor facing the slot, with its foam ring in between and foam behind it.
  - The receiver has to fit inside 16.4 × 7.3 mm.
  - Its wires leave through the open back of the pocket.
- **Microphone (done):** bottom edge, 15 mm left of the USB-C opening as you look at the screen. That corner points
  toward the mouth when the phone is at the right ear.
  - A 6.3 mm pocket opens on the inside, with a 1.2 mm skin and a 1.5 mm sound hole.
  - A wire groove runs up the inside wall and through the mating lip.
- **LTE antenna (later):** the top corner opposite the LoRa antenna has a blind vertical slot, which is clearance for a
  Grove *plug*. This project solders wires instead of using a plug, so that slot is replaced with a mirror of the
  LoRa SMA cut-out (6.5 mm hole + hex recess) for the LTE antenna. Dry-fit check: the antenna connector body must
  clear the empty Grove socket housing under it.
- **Modem power switch:** none needed. The modem follows the T-Deck's own switch.

## Back changes

**First version ready to print and dry-fit (3 Nov 2026):** [case/back-modem-gps.stl](../case/back-modem-gps.stl),
made by [case/scripts/make_back.py](../case/scripts/make_back.py) from the X back. Details and pictures are in
[case/README.md](../case/README.md).

KTRON board (from KTRON's drawing): **54.33 × 57.23 mm**, four 3.2 mm holes on a **47.90 × 50.70 mm** rectangle,
about 3.2 mm in from each edge. The 4G socket (U.FL1) is on the top edge. The GPS socket (U.FL2) is on the left
edge, low down. The micro-SIM (push-push holder on the solder side) slides in from the bottom edge, at the end
nearest the VDD/RX/TX header.

- **Modem board** on four 9 mm standoffs with M3 heat-set insert holes (4.5 mm), 7 mm wide with a 10 mm foot.
  - **Placement:** top half, component side toward the back cover.
  - **Orientation:** the SIM edge faces the phone's **left** side. That puts the 4G socket on the right, toward
    the planned 4G antenna corner, and the GPS socket near the bottom, right above the patch.
  - **Fixing:** M3 × 6 screws from the solder side.
  - **Capacitor swap:** the 9 mm height needs the KTRON's two 11 mm capacitors replaced by radial ones laid flat
    ([bring-up.md](bring-up.md), phase B).
- **SIM slit** in the left wall, 15 × 1.8 mm, flared on the outside, in line with the SIM holder. It is fully in the
  back panel, 4.65 mm below the rim.
- **GPS patch cradle** in the bottom half, about 90 mm from the 4G antenna corner.
  - A 27 mm square opening with a 7 mm fence, for the measured 26 × 26 mm patch with its 25 × 25 × 4 mm ceramic.
  - The ceramic faces down onto four 0.5 mm pads.
  - There is a cable notch in every side, and the patch is fixed with glue.
- **Battery** (65 × 55 × 9 mm) lies over the board, its long side top to bottom, with its connector end over the
  patch.

**Still to do:** the 4G antenna cut-out in the front's top-right corner (postponed). After the dry fit, maybe a
retainer for the battery.

### Depth check (23 mm available)

Measured from the inside floor of the back. The T-Deck (11 mm thick, LilyGO's figure) leaves 23 mm.

| Stack | Total |
|---|---|
| Modem board: 9 standoffs + 1.6 board + 1.5 SIM holder + 1 foam + 9 battery | **22.1 mm** |
| Same with the stock 11 mm capacitors (12 mm standoffs) | **25.1 mm: doesn't fit**, hence the capacitor swap |
| GPS patch: 0.5 pads + 4 ceramic + 1.6 board + ~2.5 shield | **~8.6 mm** (the battery passes above it) |

## Order of work

1. Print the mic test coupon, then the front and back.
2. Swap the KTRON's two tall capacitors after the 5 V bench tests ([bring-up.md](bring-up.md), phase B).
3. Dry-fit the T-Deck, modem board, battery, patch and antennas, and check that a SIM goes in through the slit.
