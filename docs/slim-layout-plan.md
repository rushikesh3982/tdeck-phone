# Slim layout plan

**Status: brainstorm only (8 Nov 2026). Nothing here is designed yet.** The rest of the docs and the case files still
describe the current build: the X back, the 5000 mAh battery over the modem board, and the GPS patch in the
bottom-left corner. The redesign happens in one go once the open items at the end are settled.

## Why

The finished handset is about **37 mm** thick, which looks and feels chunky. Most of that is the stack behind the
T-Deck: standoffs, board, SIM holder, foam and a 9 mm battery, all piled on top of each other (23 mm).

## The idea

Put the battery **beside** the modem board instead of on top of it. The modem board goes back to the top of the case,
and a 10 mm battery lies across the phone in the lower part, under the keyboard. Then the modem stack (about
13–14 mm) is the thickest thing behind the T-Deck, and the back panel can be much shallower.

| Back panel | Back's height | Space behind the T-Deck | Phone thickness |
|---|---|---|---|
| X back (current build) | 18 mm | 23 mm | about 37 mm |
| **This plan** | **about 8–9 mm** | about 13–14 mm | **about 27–28 mm** |
| Alley Cat's slim S back (for comparison) | 7 mm | about 11.8 mm | about 26 mm |

The front's own 7 mm behind the T-Deck is part of the "space behind the T-Deck" in every row. With this plan the
modem board sits across the joint, partly in the front half.

## Battery

- **Size: 103565** (10 × 35 × 65 mm), sold as about 3000 mAh, realistically 2500–3000 mAh. That's about half to 60 %
  of the current 5000 mAh cell.
- **Space:** below the modem board there's about 34–36 mm (bottom to top) by 64–66 mm (side to side). So the cell must
  measure **no more than 66 × 36 × 10 mm, including its tabs.**
- **A bare cell** with welded nickel tabs, used with the 3 A two-MOSFET protection board already chosen (see
  [wiring.md](wiring.md), section 2). Cells with protection built in are usually 3–5 mm longer, which won't fit
  across the case. Their built-in protection also often cuts out below the 2 A the modem draws in 2G call bursts.
- **Where to buy:**
  - **Robu:** not stocked.
  - **Amazon.in:** only overpriced imports. For example, the Hiteuoms 3000 mAh cell measures 67 × 36 × 10 mm, 1 mm
    too long, and its protection allows only about 1.5 A.
  - **IndiaMART:** the likely route. Candidates are
    [Sheth Electronics, Bengaluru](https://www.indiamart.com/proddetail/lithium-polymer-battery-3-7v-3000mah-11673382233.html)
    (₹430, in stock) and
    [Pastiche Energy Solutions, Panchkula](https://www.indiamart.com/proddetail/3-7v-3000mah-lithium-polymer-battery-12300426162.html)
    (a battery maker). Neither listing states a size, so ask:

    > Need 1 or 2 pieces of a 3.7 V lithium-polymer pouch cell, size **103565** (10 × 35 × 65 mm).
    > - **Maximum size including the tabs: 66 × 36 × 10 mm.**
    > - Real capacity about 3000 mAh.
    > - Bare cell with nickel tabs (I have my own protection board). If it comes with a protection board, the total
    >   length must still be 66 mm or less, and the over-current cut-off must be 3 A or more.
    > - It must handle 2 A peaks.
    >
    > Please send a photo with the cell's measured size, the datasheet, the price and shipping cost.

**Other layouts considered:**

| Layout | Phone | Battery | Why not |
|---|---|---|---|
| Current: pouch over the board | about 37 mm | 5000 mAh | Too thick |
| Thin pouch (4–6 mm) over the GPS patch, in the lower part | about 28–30 mm | about 1000–1700 mAh | Too little battery |
| Large thin pouch (6 mm) over the board | about 33 mm | about 3000 mAh | Thicker for the same battery |
| Two 18650 cells across the lower part | about 33.5 mm | about 6000–7000 mAh | An 18650 is 18.5 mm thick on its own, so the phone can't get thin |

## Modem board

- **Position:** back at the top, where it was first drawn (its top edge just below the case screws), to leave the
  lower part free for the battery.
- **Standoffs:** 9 mm, unchanged for now (see "Capacitors" below).
- **Earpiece wires:** with nothing lying over the board, they come down onto its top pads freely. The 7 Nov problem
  of too little room at the top doesn't arise.

## GPS antenna

- **Type:** a small active antenna with a U.FL plug, about 12–15 mm across, in place of the 25 mm patch. The patch's
  corner is where the battery goes.
- **Where:** in the top pocket behind the earpiece, with a thin separator between them, facing the top edge of the
  phone. That pocket was Alley Cat's GPS-module pocket originally. The back's half of it, filled solid in the current
  design, can be opened again for more room.
- **No window needed:** GPS signals pass through the plastic wall. Only metal blocks them, so the cat badge on the top
  edge can stay.
- **Risks:**
  - **Electrical noise:** it sits next to the T-Deck's ESP32 chip, whose noise can upset GPS.
  - **The earpiece magnet** is close by.
  - **A small antenna receives less** than the 25 mm patch.

  **Test it on the bench before designing around it,** with the T-Deck running, by checking time to fix and the
  number of satellites.

## 4G and LoRa antennas

- **4G:** an external SMA antenna in the top-right hole. The internal sticker strip along the right side
  ([wiring.md](wiring.md), section 6) needs a deep back and the bottom corner, so it no longer fits.
- **LoRa:** unchanged: the T-Deck's cable in the top-left hole, with the 50 mm 868 MHz stubby.

## Left side of the phone

From the bottom to the top:

1. **SIM picture** (the same engraved card outline), now below the slit.
2. **SIM slit:** about 50–67 mm up from the bottom. With the shallower back it moves up into the **front half's** left
   wall, at the card's height (about 2 mm behind the T-Deck).
3. **Modem switch** (SS-12F15): moved up to about 70–90 mm, into the space above the slit. It stays clear of the
   top-left SMA connector, whose inner end reaches down to about 92 mm, so an SMA antenna still fits there.
4. **SMA corner** (LoRa).

The old switch mount (55–76 mm) and the old speaker grille (32–48 mm) on this side are filled in.

## Right side of the phone

- **Speaker:** the T-Deck's own speaker, a box about 12 × 19 × 7 mm. It's only lightly glued to the T-Deck's board,
  and its wires reach either side. It moves to this side, about **66–85 mm up**, right behind the T-Deck. About 5–6 mm
  of it reaches into the case, and there's about 12 mm free there.
- **Grille:** in the wall at the speaker, just above the microSD slot (nearer the back of the phone), so the slot and
  the grille line up one above the other.
- **Don't touch the holding bump:** the inside of this wall has a bump at about **59–65 mm up** that holds the T-Deck's
  edge in place. It sticks out about 1.4 mm and slopes away to nothing about 2.7 mm behind the T-Deck. The speaker sits
  just above it.
- **Below the bump won't work:** toward the T-Deck switch, the speaker would hit the end of the battery.

## Capacitors (to discuss later)

If the 470 µF capacitor C11 were replaced by flat polymer capacitors (about 3 mm tall), the tallest part under the
board would be the regulator (about 4.5 mm). The standoffs could then drop to about 5 mm, and the modem stack to about
10 mm. Everything would then fit inside Alley Cat's 7 mm S back (`Alley Chat TD1 S Inside Cat Edition.stl`), for a phone
about 26 mm thick. **Left for later, once everything else is settled.**

## Open items

1. **Battery:** the seller's actual measured size, which must be 66 × 36 × 10 mm or less including the tabs.
2. **GPS antenna:** choose a small active one with a U.FL plug, and bench-test it.
3. **Capacitors:** decide later whether to rework C11 to reach the S back's thickness.
