# Wiring

Everything is soldered. The only plug is the battery's JST plug into the T-Deck. The KTRON board
arrives without pin headers, and wires are soldered straight into its holes.

## KTRON board pads

```
left row:      STA  NET  DTR  RI  VDD  GND  RX  TX  RST  1V8
right row:     CLK  CS  MOSI  MISO  M-  M+  S-  S+  SCL  SDA  GND  VCC
```

Used in v1: **VDD, GND, RX, TX** (data link), **M+, M−** and the right row's **GND** (mic), **S+, S−** (earpiece), plus the battery feed
described below. **Never use the VCC pad** while the battery is connected.

Antenna sockets on the board: **U.FL1** at the top edge = LTE. **U.FL2** beside inductor L2 = GNSS. The micro-SIM
holder is on the back of the board.

## 1. Data link: T-Deck Grove socket → KTRON

The Grove socket is desoldered from the T-Deck, and the four wires are soldered to its pads. No Grove plug. This
also frees that corner of the case for a second SMA antenna cut-out.

| T-Deck Grove pin | ESP32-S3 pin | Direction | KTRON pad | Notes |
|---|---|---|---|---|
| TX | GPIO43 | → | TX | |
| RX | GPIO44 | ← | RX | Incoming calls (`RING`) arrive on this wire |
| VCC (switched 3.3 V) | switched by GPIO10 | → | VDD | Reference for the board's level shifters (microamps). Does **not** power the modem |
| GND | — | — | GND | |

**TX and RX go straight across: TX to TX, RX to RX.** This was found on the bench on 5 Nov 2026. With a CP2102 the
modem stayed silent when the wires were crossed, and answered as soon as they went straight. So the KTRON's labels
seem to name the signal on the connected device's side, not the modem's own. If the T-Deck gets no reply, check this
first.

Serial settings: 115200 baud, 8N1.

**Important:** the Grove 3.3 V is switched on and off by GPIO10 (PWR_EN). The firmware must keep GPIO10 HIGH all
the time, including in light sleep (`gpio_hold_en`). If it drops, the level shifters lose their reference and
incoming-call messages never reach the T-Deck.

The board's RI (ring indicator) pad is not wired in v1 because the T-Deck has no spare GPIO.

## 2. Power: one battery for both boards

The cell is a 5000 mAh Li-ion pouch cell: Jiangxi Huahao **HH 955465**, 3.7 V, 18.5 Wh, BIS-registered
(IS 16046-2 / IEC 62133-2). It's nominally 9.5 × 54 × 65 mm (measured 65 × 55 × 9). **It has no protection circuit:**
its bare tabs come straight out of the cell, as on cells made for power banks. So it gets a **1S Li-ion protection
board**, the 3 A two-MOSFET version ("1S 3.7V 3A 2MOS BMS": DW01A + two 8205A), soldered on its two tabs. Everything else (the T-Deck's JST lead and
the modem's feed) connects to the board's output, P+ and P−, never straight to the cell. The board cuts off a short
circuit, overcharge and overdischarge (about 2.4–2.5 V). It sits at the cell's tab end, toward the bottom of the phone.

```
 Cell tabs ──► protection board B+ / B−

 P+ ──┬── JST PH2.0 plug ──────────────────────────────► T-Deck battery socket (+)
      │
      └── modem switch SS-12F15: middle pin → outer pin ─► KTRON: + leg of C11 (470 µF bulk capacitor)
                                                           (or MIC29302 pin 4, the same rail)
 P− ──┬── JST PH2.0 plug ──────────────────────────────► T-Deck battery socket (−)
      │
      └────────────────────────────────────────────────► KTRON GND (the regulator's metal tab)
```

- The modem's pair is joined at the protection board's P+ / P−, not run through the Grove wires. Use 24 AWG wire
  (22 AWG if you have it). The + side goes out to the switch in the left wall and back to C11, about 15 cm in total.
  At the modem's 2 A bursts that loses only about 0.03 V.
- **Never feed the KTRON VCC pad while the cell is connected.**
- The board's MIC29302 regulator (K1) stays on the board but does nothing. Its datasheet allows the output to sit
  above the input with no reverse current, and its enable pin is low when nothing is on VCC.
- **Before soldering:** with the multimeter, check that the pad you chose has continuity to the + pad of C11
  and **not** to VCC.
- **C11 is the bulk capacitor** next to the modem chip. It was a 330 µF 50 V SMD can, 11 mm tall, which is too tall to
  fit under the battery. It gets replaced by a 470 µF 16 V radial capacitor laid flat (see
  [bring-up.md](bring-up.md), phase B).
- The T-Deck's own charger charges the cell over USB-C and stops at 4.2 V, which suits this cell.
- The modem runs from 3.4 V to 4.2 V. The firmware turns the modem off cleanly below 3.3 V
  (`AT+CPMVT=1,3300,4300`). The screen treats a battery reading under 3.5 V (BAT_ADC, GPIO4) as "modem off".
  **Check before using that command:** on the bench, on 5 V, this board reports its supply as about 0.01 V
  (`AT+CBC`). If it reads that low on battery too, the command could turn the modem off straight away. Read `AT+CBC` on
  battery power first (phase B).

### Modem power switch: an SS-12F15 slide switch on the left side (decided 6 Nov 2026)

The modem has its own on/off switch, a small **SS-12F15** slide switch (owned) in the battery + wire to the modem. It
sits in Alley Cat's original slide-switch mount on the case's left side, which was drawn for exactly this switch.

**The switch (from its drawing):**
- **Plate:** 19.7 × 5.6 × 0.5 mm, with two Ø2.2 mm holes 15 mm apart.
- **Knob:** 3 × 3 mm, **4 mm tall** (yours), with 3 mm of travel.
- **Body:** 11.5 × 4.6 × 5 mm under the plate. With the pins it stands about 8 mm into the case.
- **Pins:** 3 at a 3 mm pitch.
- **Rating:** usually sold as 0.5 A at 50 V DC (not on the drawing).

**The mount (front, left wall, about 52–75 mm up from the bottom edge):**
- **Plate:** sits in the 21.6 × 8.4 mm recess on the inside.
- **Knob:** comes out through a 6.9 × 3.4 mm slot and stands about **1 mm proud** of the side.
- **Fixing:** two **M2 countersunk screws (6–8 mm)** from outside, with M2 nuts inside. A dab of glue also works.
- **Clearances** (checked against the case files): it touches neither case half, its lowest point is **0.5 mm above
  the T-Deck's back**, and its pins point into the case.

**Wiring:** P+ from the protection board goes to the **middle pin**, and **one outer pin** goes to C11's + leg. Leave
the other outer pin free. The switch replaces the plug used on the bench.

**Battery position:** the switch's body and pins take the space where the battery's left edge was. So the battery
sits about **9 mm further toward the phone's right**, and low enough to leave room at the top for the earpiece wires. It
still fits both halves, with 2.5 mm between the switch's pins and the battery's edge.

**Using it:**
- The T-Deck's own switch (right side) turns the T-Deck on and off, and this switch does the same for the modem.
- **T-Deck on, modem off:** the firmware just sees a silent modem and shows it as off.
- **T-Deck off, modem on:** the modem drains the battery (about 17 mA idle, so roughly 10 days on 5000 mAh), so
  switch both off together.
- **Frozen modem:** switch it off and on.

**Current:** the modem's average current is well under the switch's 0.5 A. Its short transmit bursts (up to about
2 A on 2G, less on 4G) pass through it too.
- Typical contact resistance makes that a dip of about 0.1 V per burst, and C11's 470 µF right after the switch
  smooths it.
- That's fine with a reasonably charged battery. A modem that restarts during 2G calls on a nearly flat battery would
  point to the switch: then use the middle way below.

**Check after wiring:** with the switch off, C11's + leg reads about 0 V. With it on, it reads the battery's voltage.

### Alternative (not used now): the modem follows the T-Deck's own switch

**Why it's needed:** the modem's battery wires join at the battery, so without help the T-Deck's own power switch
would not turn the modem off. The modem would stay on whenever the battery is connected, and a frozen modem could
only be restarted by opening the case.

**How:** the Grove 3.3 V wire (already going to the KTRON's VDD pad) only has power while the T-Deck is on, because
the firmware keeps GPIO10 high, also in sleep. That 3.3 V switches the modem's battery feed through two small
MOSFETs. So the **T-Deck's own power switch turns the modem on and off too**. No separate switch and no hole in the
case.

**Parts:** AO3401A P-MOSFET, AO3400A N-MOSFET (both SOT-23), two 100 kΩ resistors.

```
                        AO3401A (P-MOSFET)
                     ┌──────────────────────┐
 Cell + ──────────┬──┤ S (pin 2)  D (pin 3) ├─────────► KTRON: MIC29302 pin 4 (OUTPUT)
 (24 AWG)         │  │      G (pin 1)       │              or the + pad of C11 (bulk capacitor)
                  │  └──────────┬───────────┘              (24 AWG)
               100 kΩ           │
                  │             │
                  └─────────────┤
                                │
                     ┌──────────┴───────────┐
                     │      D (pin 3)       │
                     │  AO3400A (N-MOSFET)  │
 Grove 3.3 V ───┬────┤ G (pin 1)            │
 (thin wire from│    │      S (pin 2)       │
  the VDD pad)  │    └──────────┬───────────┘
             100 kΩ             │
                │               │
 Cell − ────────┴───────────────┴──────────────────────► KTRON GND (the regulator's metal tab)
```

- The first 100 kΩ goes between the AO3401A's **S** and **G** pins.
- The second 100 kΩ goes between the AO3400A's **G** and **S** pins (that is, to ground).

**How it works:**

- **T-Deck on:** the firmware holds GPIO10 high, so the Grove 3.3 V is on. The AO3400A turns on and pulls the
  AO3401A's gate to ground. The AO3401A turns on and the modem gets the battery.
- **T-Deck off** (its own power switch): the Grove 3.3 V is gone. The resistors hold both MOSFETs off, and the
  modem gets no power.
- **Frozen modem:** switch the T-Deck off and on.
- **Current used:** while on, the two resistors draw about 75 µA in total, tiny next to the modem. While off,
  nothing.
- **The modem's current** (bursts up to about 1.5–2 A) goes through the AO3401A, which is rated about 4 A.
- **What you give up:** the modem can't be switched off on its own while the T-Deck stays on.
- **Not checked yet:** whether the T-Deck runs from USB with its switch off. If it does, the modem comes on as
  well once the firmware sets GPIO10.

**Building it:**

- Both MOSFETs are tiny (SOT-23, about 3 × 1.4 mm). SOT-23 adapter boards, or a small scrap of perfboard, make
  them much easier to solder. The resistors can sit on the same board.
- Put this little board in the back half of the case, in the battery + wire between the pack and the KTRON board.
  Keep the whole 24 AWG run 10 cm or shorter.
- Besides the two 24 AWG battery wires, it needs two thin wires: one to the KTRON's VDD pad (Grove 3.3 V) and one
  to ground.
- Cover the joints with heat-shrink.

**Checks with the multimeter:**

1. **Before soldering, find the pins** in diode-test mode. Each should read about 0.5–0.8 V one way and OL the
   other. This is the MOSFET's built-in diode, and it tells you which pin is which.
   - AO3401A: red probe on D (pin 3), black on S (pin 2).
   - AO3400A: red probe on S (pin 2), black on D (pin 3).
2. **After wiring:**
   - T-Deck on, with the firmware setting GPIO10 high: the + pad of C11 reads the battery voltage.
   - T-Deck off: it falls to about 0 V within a few seconds.
3. **With the modem running,** measure the AO3401A from S to D. It should read under about 0.1 V.
4. **If the modem stays on with the T-Deck off,** the AO3401A's S and D are swapped. Its built-in diode is then
   feeding the modem.
5. **If the modem never comes on,** check the AO3400A's orientation, and that the Grove 3.3 V is really there
   (GPIO10 high).

**Middle way, if the slide switch ever gives trouble:** keep the SS-12F15 but let it drive only an AO3401A's gate
(switch between the gate and ground, 100 kΩ from gate to source). The switch then carries microamps, and the
MOSFET carries the modem's current. That's one SOT-23 part and one resistor.

## 3. Earpiece (call audio out)

The earpiece receiver from the Micromax Canvas A1: the **32 Ω** part from the top of the phone, under the
earpiece slot. Not the 8 Ω rear loudspeaker.

- Fold its two spring contacts flat over its back, and solder a thin wire to each.
- Connect it across **S+ and S−** through a **47 µF capacitor in each wire** (10 V or more, + leg toward the
  KTRON). This is SIMCom's and KTRON's reference circuit: the capacitors stop any steady current through the coil.
  The earpiece's own polarity doesn't matter. **Nothing goes to ground.**
- The capacitors sit on the wires near the KTRON, covered in heat-shrink, lying flat in the gap under the board.

S+/S− are the module's EAR_P/EAR_N outputs, a 37 mW driver made for a 32 Ω receiver. There is no amplifier on the
board. **Never connect an 8 Ω speaker directly to S+/S−.**

## 4. Microphone

A 2-wire electret mic (Sunrom 6027) across **M+ and M−**, plus a **1 kΩ resistor from M− to GND**.

- The mic's pin that connects to its metal can (Sunrom's "term 2") → **M−**.
- The other pin, the one in the insulating ring ("term 1") → **M+**.
- **The resistor is required.** The module feeds M+ through its own 2.2 kΩ, but the resistor from M− to ground sits
  outside the module (SIMCom A7672S Hardware Design, figure 28, which shows 2.2 kΩ). KTRON's speaker/mic drawing
  doesn't show it. Without it no current can flow through the mic, and the other person hears silence.
- **Where it goes:** between M− and the GND hole in the same row (right row, beside VCC), on the board's component
  side, because the SIM side has too little room once the case is closed. Sleeve its legs, because they pass over
  M+, S−, S+, SCL and SDA. On the bench that GND hole also holds the 5 V supply's negative wire. Only that wire
  comes off in phase B; the resistor stays.
- **Tested 11 Nov 2026:** 1 kΩ, soldered at the mic end with a jumper to GND, gave clear, loud enough speech at
  `AT+CMICGAIN=4`. It has not yet been tested in its place on the board. 2.2 kΩ, SIMCom's value, wasn't tried. 4.7 kΩ
  wasn't tried either, and would probably leave the mic too little voltage.
- **If a call is silent:** measure each mic pad to GND while a call is up. Without the resistor, both pads read
  1.65 V, with 0 V between them.

If the person you call hears you faintly, raise the gain with `AT+CMICGAIN=5` or higher. Sunrom lists this mic at
−60 dB sensitivity without saying what that's measured against, so it can't be compared with other mics' figures.
Check the level in the bench test call.

## 5. Ringtone

The T-Deck's own speaker plays the ringtone when the modem sends `RING`. No extra wiring and no third speaker.

## 6. Antennas

| Antenna | Connects to | Part | Where it goes |
|---|---|---|---|
| LTE, **in use** | KTRON U.FL1 directly | The full-band LTE sticker antenna that came in the T-Deck's box as its LoRa antenna (110 × 20 mm, U.FL, 11 cm). Used for all the bench tests on 7 Nov 2026 | Inside the back, along its right side, wrapped from the floor up the wall (see below). Antenna plug in the top-right hole |
| LTE, fallback (not owned) | KTRON U.FL1 (top edge) | SMA antenna rated 700–2700 MHz, through the KTRON IPX → SMA female cable | Only if the sticker is too weak inside the case: the case's top-right SMA cut-out (old Grove corner), close to U.FL1. Away from the top centre, where the T-Deck's Wi-Fi/BT antenna is |
| GNSS | KTRON U.FL2 (beside L2; it powers an active antenna) | KTRON KSTA1417 active patch | Bottom half of the back, at least 60 mm from the LTE antenna, ceramic side toward the back cover |
| LoRa | T-Deck's own u.FL | T-Deck's own u.FL-to-SMA cable, and a 50 mm 865–868 MHz SMA stubby (to order: [bom.md](../bom.md)), because the T-Deck's own antenna now serves 4G | The case's top-left SMA cut-out, where it already sits |

Both top corners now have identical SMA cut-outs, so either antenna can go in either corner. **Recommended:** 4G
in the top-right (old Grove corner), and the T-Deck's LoRa connector staying top-left, where it already sits.
From the top-right, the 4G cable drops straight into the empty strip beside the modem board, to its 4G socket on
that side (about 5 cm; the 10 cm cable is plenty). From the top-left, it would have to get around the battery,
which covers the board with only about 1 mm to spare (about 11 cm, so use the 15 cm cable).

### Internal LTE sticker antenna (option to try, 6 Nov 2026)

The **full-band LTE sticker antenna** that came with the T-Deck can serve the modem from inside the case.
- **Antenna:** labelled "Full Band LTE Antenna, 698–960 / 1710–2690 MHz", which covers every Indian 4G band (B1, B3, B5, B8,
  B40, B41) and 2G. **110 × 20 mm**, with an **11 cm** cable ending in a **U.FL plug**. It plugs straight into
  **U.FL1**, so the IPX → SMA cable isn't needed.
- **SMA option stays:** the case doesn't change. The SMA cut-outs stay, so an external antenna can go back on at any
  time. With the sticker inside, fit the printed **antenna plug** in the top-right hole.
- **LoRa:** if the sticker serves the modem, LoRa needs its own antenna in the top-left hole, for example a 50 mm
  868 MHz SMA stubby. If LoRa isn't used, plug that hole too.

**Where it goes:** along the **right side of the back**, in the band beside the modem board (back diagram ⑲). Measured
from the case file, with distances counted from the inside of the right wall:
- **Floor:** the right-hand standoffs' feet end about 12.5 mm from the wall. From there the floor is flat for
  about **7.5 mm**, to 5 mm from the wall. It then curves up into the wall (1 mm up at 3 mm from the wall, 4 mm up
  at 1 mm), and the wall is vertical, **16 mm** tall.
- **Length:** about **91 mm**, from where the bottom corner starts to curve to a 5 mm-high step near the top.
- **How it's wrapped:**
  - **Across its width:** about 7 mm flat on the floor, about 4 mm around the curve, and about 9 mm up the wall.
  - **Along its length:** about 91 mm along the side, plus about 10 mm up the bottom corner and about 9 mm over the
    top step.
- **Nothing in the way:** the LED tube, SIM slit, GPS cradle and switch are all elsewhere.
- **Cable:** U.FL1 sits just beside the band, a little above halfway up. It is about 40 mm from the strip's top
  end and about 53 mm from its bottom end, so the 11 cm cable reaches from either end. Lay any spare cable on the
  floor, not across the strip.

**Why there:** it lies **beside** the KTRON board, not under it. An antenna under the board (9 mm below its copper
layer) or under the battery's foil casing would lose a lot, most of all on 850/900 MHz.

**What will cost some signal:**
- **Battery:** its right edge, moved for the modem switch, is about 5 mm from the wall part of the strip, and it
  overhangs the floor part 13 mm above.
- **GPS:** the GPS patch is about 28 mm from the strip, edge to edge (23 mm before the patch moved into the
  bottom-left corner on 7 Nov 2026). That's still closer than the 60 mm aimed for. GPS only suffers while the
  modem transmits.

**Decide by measurement** (see [bring-up.md](bring-up.md), "Checking the sticker antenna inside the case"):
1. **Reading in the open:** read the 4G signal (`AT+CPSI?`) with the strip lying flat in the open, away from the
   board and battery. On the bench on 7 Nov 2026 this gave RSRP −91 dBm on band 5, with a clean VoLTE call.
2. **Reading inside the case:** at the same spot, tape the strip in place (don't peel its backing yet), with the
   board and battery fitted, and read it again.
3. **Within about 5 dB:** stick it down. **Much worse:** buy an SMA antenna rated 700–2700 MHz for the top-right
   hole.

## Version 2: speakerphone

The A7672S has only one audio output. For a speakerphone, an amplifier input taps **S+ only** (S− left alone),
in parallel with the earpiece. The amplifier is powered from the cell through its own switch. Parts are listed
in [../bom.md](../bom.md).

## Never do

- Feed the KTRON VCC pad while the cell is connected.
- Connect anything straight to the cell's tabs. Everything goes through the protection board's P+ / P−.
- Connect an 8 Ω speaker directly to S+/S−.
- Send `AT+BTPOWER=1`. The module has Bluetooth inside, and it stays off.
