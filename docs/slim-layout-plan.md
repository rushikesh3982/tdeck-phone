# Slim layout plan

**Status: option 3 chosen (9 Nov 2026) and designed. See [design-18650.md](design-18650.md).** This page is kept as
the record of the brainstorm (8 Nov 2026). Some details of option 3 changed in the design: see
[What the design changed](#what-the-design-changed) at the end of option 3.

## Why

The finished handset is about **37 mm** thick, which looks and feels chunky. Most of that is the stack behind the
T-Deck: standoffs, board, SIM holder, foam and a 9 mm battery, all piled on top of each other (23 mm).

## The three options at a glance

All three stop stacking the battery on the modem board. That stack is what makes the phone 37 mm thick.

| | Now | Option 1 | Option 2 | Option 3 |
|---|---|---|---|---|
| **Idea** | Battery over the modem | 103565 battery beside the modem | Case 13 mm longer at the top, your 5000 mAh cell below the modem | One 18650 across the top, in a grip ridge |
| **Size (mm)** | 110 × 76 × 37 | 110 × 76 × 27–28 | about 123 × 76 × 27.5 | 110 × 76 × 27.5, **33.5 at the grip** (designed: 26.5, 32.8 at the grip) |
| **Battery** | 5000 mAh | about 3000 mAh (to buy) | **5000 mAh (already owned)** | 3000–3500 mAh (to buy) |
| **Case outline** | — | unchanged | 13 mm taller top bezel | unchanged |
| **GPS** | 25 mm patch | small antenna, top pocket | in the taller top bezel | in the 15 mm strip at the bottom (designed: in the top slot) |
| **Main catch** | Too thick | Hard-to-find cell, less battery | Longer phone | Grip ridge; the cell sits behind the T-Deck's Wi-Fi/Bluetooth antenna |

Common to all three: the modem board keeps its 9 mm standoffs for now; 4G uses an external SMA antenna (the internal
sticker strip needs a deep back); the back panel shrinks from 18 mm to about 8–9 mm; and the SIM slit, modem switch and
speaker are placed again for the new layout.

## Option 1: a 103565 battery beside the modem

### The idea

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

### Battery

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

### Modem board

- **Position:** back at the top, where it was first drawn (its top edge just below the case screws), to leave the
  lower part free for the battery.
- **Standoffs:** 9 mm, unchanged for now (see "Capacitors" below).
- **Earpiece wires:** with nothing lying over the board, they come down onto its top pads freely. The 7 Nov problem
  of too little room at the top doesn't arise.

### GPS antenna

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

### 4G and LoRa antennas

- **4G:** an external SMA antenna in the top-right hole. The internal sticker strip along the right side
  ([wiring.md](wiring.md), section 6) needs a deep back and the bottom corner, so it no longer fits.
- **LoRa:** unchanged: the T-Deck's cable in the top-left hole, with the 50 mm 868 MHz stubby.

### Left side of the phone

From the bottom to the top:

1. **SIM picture** (the same engraved card outline), now below the slit.
2. **SIM slit:** about 50–67 mm up from the bottom. With the shallower back it moves up into the **front half's** left
   wall, at the card's height (about 2 mm behind the T-Deck).
3. **Modem switch** (SS-12F15): moved up to about 70–90 mm, into the space above the slit. It stays clear of the
   top-left SMA connector, whose inner end reaches down to about 92 mm, so an SMA antenna still fits there.
4. **SMA corner** (LoRa).

The old switch mount (55–76 mm) and the old speaker grille (32–48 mm) on this side are filled in.

### Right side of the phone

- **Speaker:** the T-Deck's own speaker, a box about 12 × 19 × 7 mm. It's only lightly glued to the T-Deck's board,
  and its wires reach either side. It moves to this side, about **66–85 mm up**, right behind the T-Deck. About 5–6 mm
  of it reaches into the case, and there's about 12 mm free there.
- **Grille:** in the wall at the speaker, just above the microSD slot (nearer the back of the phone), so the slot and
  the grille line up one above the other.
- **Don't touch the holding bump:** the inside of this wall has a bump at about **59–65 mm up** that holds the T-Deck's
  edge in place. It sticks out about 1.4 mm and slopes away to nothing about 2.7 mm behind the T-Deck. The speaker sits
  just above it.
- **Below the bump won't work:** toward the T-Deck switch, the speaker would hit the end of the battery.

## Option 2: stretched case, your 5000 mAh battery below the modem

- **The idea:** keep the battery you have (65 × 55 × 9 mm) and lay it **across** the lower part of the case, under the
  keyboard, with the modem board above it. Not on top of it, as now.
- **The space:** that needs about 112 mm of inside length. The case has about 92 mm, or about 101 mm with the solid top
  block (the case-screw block) removed. So the case gets **about 13 mm longer, all of it at the top**, above the T-Deck.
  - **Only the top bezel changes:** it grows from about 8 to about 21 mm. The screen, keyboard, bottom edge and USB-C
    stay as they are.
  - **Why not the bottom:** the T-Deck's USB-C port sits right behind the bottom wall. A thicker bottom would leave the
    port too deep for a cable plug, unless an internal USB-C extension were added.
- **The battery on a 4 mm shelf:** the case's bottom corners are strongly rounded, so the battery starts about 8 mm up,
  on a 4 mm shelf. That costs no thickness: the battery's top then sits level with the modem stack.
- **The two case screws** lose their block and need new places.
- **Bonus:** the taller top bezel has the phone's full depth behind it, not just the thin space behind the T-Deck. It's
  a natural home for the GPS antenna (the 18 mm Abracon patch fits beside the earpiece), and the earpiece can sit
  wherever feels best in that bezel.

## Option 3: one 18650 at the top, in a grip ridge

- **The idea:** one 18650 cell (18.5 × 65 mm, about 67 mm with welded tabs) lies **across the top** of the back, just
  below the top block, which keeps its case screws. The modem board goes below it, and about 15 mm stays free at the
  bottom. The case outline stays **110 × 76 mm**.
- **Thickness:**
  - **Most of the phone:** about **27.5 mm**, set by the modem stack.
  - **The grip:** the cell needs about 19.5 mm behind the T-Deck, so the back gets a rounded **ridge about 6 mm high
    and 22–25 mm tall** across its top, making it **33.5 mm** there.
  - **Comfort:** when typing with both thumbs, your index fingers rest on it, and it stops the phone sliding in one
    hand. In the real design it would run the full width and blend smoothly into the back.
- **Battery:** a genuine 18650 gives about 3000–3500 mAh (for example Samsung 35E or Molicel P30B), handles the
  modem's 2 A bursts easily, and is easy to buy in India. Buy only genuine cells from a reputable seller. It weighs
  about 47 g, against about 80 g for the pouch.
- **Watch:**
  - **Wi-Fi/Bluetooth:** the cell's steel can sits right behind the T-Deck's Wi-Fi/Bluetooth antenna (top centre of
    its board), so Wi-Fi and Bluetooth range would drop. Calls, 4G and LoRa aren't affected.
  - **GPS** would go in the 15 mm strip at the bottom, which points down when the phone is in your hand.
  - **The side-wall parts** (SIM slit, modem switch, speaker) all move again, because the board sits lower.

The rough mock-up pictures drawn for this brainstorm have been removed, now that the design is finished. The real
pictures of option 3 are in [design-18650.md](design-18650.md).

### What the design changed

The finished design is in [design-18650.md](design-18650.md). Compared with the idea above:

- **Thinner:** 26.5 mm over most of the phone and 32.8 mm at the grip, built on Alley Cat's S back made 0.5 mm deeper.
- **Grip:** round, 6.25 mm high, with sides blending in at 45° so the back prints standing up.
- **Cell:** LG MJ1 (about 3400 mAh), held by contacts taken from an 18650 holder.
- **Modem board:** on 8 mm standoffs, not 9.
- **GPS:** an Eteily 18 mm active antenna standing on its edge in the top slot, over the earpiece, not in the bottom
  strip. The bottom strip and the right side are kept free for the 4G antenna instead.
- **Side-wall parts:** the SIM slit is in the front's left wall, the speaker on the right below the T-Deck's switch,
  and the modem switch on the back's right wall.

## Capacitors (not pursued)

If the 470 µF capacitor C11 were replaced by flat polymer capacitors (about 3 mm tall), the tallest part under the
board would be the regulator (about 4.5 mm). The standoffs could then drop to about 5 mm, and the modem stack to about
10 mm. Everything would then fit inside Alley Cat's 7 mm S back (`Alley Chat TD1 S Inside Cat Edition.stl`), for a phone
about 26 mm thick. **Not needed:** the 18650 design keeps the 470 µF laid flat, on 8 mm standoffs, in the S back made
0.5 mm deeper.

## Open items (closed)

1. **Choose an option:** option 3, on 9 Nov 2026.
2. **Option 1 only:** no longer needed.
3. **GPS antenna:** the Eteily ET-GPL12-5L15C-U-184 (active, 18 × 18 mm, 15 cm cable, 2.2–5 V) was ordered instead of
   the Abracon. The KTRON's GNSS socket gives 3.0 V (the modem's default, read back with `AT+CVAUXV?`).
4. **Capacitors:** not reworked (above).
