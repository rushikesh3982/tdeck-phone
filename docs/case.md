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
| `Alley Chat TD1 Switch.stl` | Slide-switch part |
| `Alley Chat TD1 X Antenna Plug.stl` | Only if the LoRa antenna stays inside |
| `Alley Cat TDeck Back Cover Custom.step` | "S" back, used only for its mating edge when drawing the new back |

Fasteners: 2× M3×5 heat-set inserts (4.5 mm hole) + 2× M3×8 screws.

Printing: PLA+ or PETG, 0.2 mm layers, 3 perimeters, 20 % infill, no supports. Tolerances are tight, so print a
test piece first.

## Why these variants

The **Standard front** keeps the pocket for the T-Deck's speaker, which plays the ringtone. The **GPS** version of
the front adds two pockets that this project reuses:

- a module pocket at the top centre above the screen, sized for an M10-Mini-class GPS
  (~12–16 × 15–18 × 5–7 mm), which becomes the **earpiece pocket**;
- a slide-switch pocket, which becomes the **modem power switch**.

The **X back** gives 23 mm of depth behind the T-Deck, enough for the modem board and battery.

Rejected: the Slim front (no speaker pocket), and the Nuts and TBall variants.

## T-Deck edge layout (from LilyGO's product photo)

- Grove socket: one top corner
- ESP32-S3 module (Wi-Fi/BT antenna): top centre
- Power switch: right side edge
- USB-C: bottom edge

## Front changes

- **Earpiece**, in the GPS pocket:
  - a grille: a row of five 0.8 mm holes, or a 1 × 6 mm slot;
  - the receiver's foam ring between its face and the grille;
  - a spacer or foam behind it so it presses against the grille;
  - wires out through the pocket's existing cable path.
- **Microphone:** a 6.3 mm pocket, 3 mm deep, in the bottom edge wall beside the USB-C opening, with a 1.5 mm
  sound hole.
- **LTE antenna:** the top corner opposite the LoRa antenna has a blind vertical slot, which is clearance for a
  Grove *plug*. This project solders wires instead of using a plug, so that slot is replaced with a mirror of the
  LoRa SMA cut-out (6.5 mm hole + hex recess) for the LTE antenna. Dry-fit check: the antenna connector body must
  clear the empty Grove socket housing under it.
- **Modem power switch:** in the existing slide-switch pocket.

## Back changes

The back needs a new layout, not just cut-outs. Either draw a new back from the S-back STEP's mating edge using
the X back's depth, or edit the X back STL.

- **Modem board** on four M3 heat-set bosses (4.5 mm hole, ~7 mm outside diameter) at its corner holes
  (3.2 mm holes, 47.9 mm apart). Mount it **component side toward the back cover** so the capacitors sit inside
  the standoff gap. Standoff height = tallest part + 1 mm: **14 mm** with the stock capacitors (≈13 mm tall), or
  8 mm with low-profile ones. Put the board in the top half, LTE socket (U.FL1) toward the LTE antenna corner.
- **GPS patch** in the bottom half, at least 60 mm from the LTE antenna, on 2 mm bosses with M2 self-tapping
  screws into 1.6 mm holes. Ceramic side toward the back cover.
- **Battery** flat under both, nearest the T-Deck. A foam sheet between the battery and the modem board's solder
  side, with a cut-out for the SIM holder.
- **Channels** for the four data wires and the battery pair.
- Print a 20 mm test coupon with one M3 boss and one M2 boss first.

### Depth check (23 mm available)

| Stack | Battery | Foam | Board / boss | Standoff / patch | Total |
|---|---|---|---|---|---|
| Over the modem board, stock capacitors | 5 | 1 | 1.6 | 14 | **21.6 mm** |
| Over the modem board, low-profile capacitors | 5 | 1 | 1.6 | 8 | **15.6 mm** |
| Over the GPS patch | 5 | — | 2 | 8 | **15 mm** |

## Order of work

1. Print the stock front and X back once, unchanged.
2. Dry-fit the T-Deck, modem board, battery, patch and antennas.
3. Then do the CAD: front cut-outs and the new back with bosses.
