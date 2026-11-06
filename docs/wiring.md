# Wiring

Everything is soldered. The only plug is the battery's JST plug into the T-Deck. The KTRON board
arrives without pin headers, and wires are soldered straight into its holes.

## KTRON board pads

```
left row:      STA  NET  DTR  RI  VDD  GND  RX  TX  RST  1V8
right row:     CLK  CS  MOSI  MISO  M-  M+  S-  S+  SCL  SDA  GND  VCC
```

Used in v1: **VDD, GND, RX, TX** (data link), **M+, M−** (mic), **S+, S−** (earpiece), plus the battery feed
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
| VCC (switched 3.3 V) | switched by GPIO10 | → | VDD | Reference for the board's level shifters (microamps). Also tells the modem power switch to turn on (section 2). Does **not** power the modem |
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

The cell is the 5000 mAh pack, 65 × 55 × 9 mm. **Check that it has its own protection circuit**: a small board at the
tab end, usually under tape. Don't use a bare cell without one. Use only its
+ and − terminals and ignore the thermistor pin.

```
 Cell + ──┬── JST PH2.0 plug ─────────────────────► T-Deck battery socket (+)
          │
          └── modem power switch (AO3401A) ──────────► KTRON: MIC29302 pin 4 (OUTPUT)
                                                        or the + pad of C11 (bulk capacitor)
 Cell − ──┬── JST PH2.0 plug ─────────────────────► T-Deck battery socket (−)
          │
          └──────────────────────────────────────► KTRON GND (the regulator's metal tab)
```

- The modem pair is joined at the battery terminals, not run through the Grove wires.
  Use 24 AWG wire, 10 cm or shorter.
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

### Modem power switch: the modem follows the T-Deck's own switch

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

**Earlier plan (not used):** a separate slide switch pulling the AO3401A's gate to ground. (The front's left-side
switch mount could have held it. It is now filled in.)

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

A 2-wire electret mic (Sunrom 6027) across **M+ and M−**. The module provides the mic bias on M+.

- The mic's pin that connects to its metal can (Sunrom's "term 2") → **M−**.
- The other pin, the one in the insulating ring ("term 1") → **M+**.
- The mic's datasheet powers it through a 2.2 kΩ resistor. Here the modem provides that bias on M+ (as above), so
  nothing extra should be needed. If the bench test call is silent, measure the voltage between M+ and M− with the
  multimeter while a call is up. It should be about 1–2.5 V.

If the person you call hears you faintly, raise the gain with `AT+CMICGAIN=5` or higher. Sunrom lists this mic at
−60 dB sensitivity without saying what that's measured against, so it can't be compared with other mics' figures.
Check the level in the bench test call.

## 5. Ringtone

The T-Deck's own speaker plays the ringtone when the modem sends `RING`. No extra wiring and no third speaker.

## 6. Antennas

| Antenna | Connects to | Part | Where it goes |
|---|---|---|---|
| LTE | KTRON U.FL1 (top edge) | SMA antenna rated 700–2700 MHz, through the KTRON IPX → SMA female cable | Recommended: the case's top-right SMA cut-out (old Grove corner), close to U.FL1. Away from the top centre, where the T-Deck's Wi-Fi/BT antenna is |
| GNSS | KTRON U.FL2 (beside L2; it powers an active antenna) | KTRON KSTA1417 active patch | Bottom half of the back, at least 60 mm from the LTE antenna, ceramic side toward the back cover |
| LoRa | T-Deck's own u.FL | T-Deck's own u.FL-to-SMA cable | The case's top-left SMA cut-out, where it already sits (or the printed plug if the LoRa antenna stays inside) |

Both top corners now have identical SMA cut-outs, so either antenna can go in either corner. **Recommended:** 4G
in the top-right (old Grove corner), and the T-Deck's LoRa connector staying top-left, where it already sits.
From the top-right, the 4G cable drops straight into the empty strip beside the modem board, to its 4G socket on
that side (about 4 cm; the 10 cm cable is plenty). From the top-left, it would have to get around the battery,
which covers the board with only about 1 mm to spare (about 11 cm, so use the 15 cm cable).

## Version 2: speakerphone

The A7672S has only one audio output. For a speakerphone, an amplifier input taps **S+ only** (S− left alone),
in parallel with the earpiece. The amplifier is powered from the cell through its own switch. Parts are listed
in [../bom.md](../bom.md).

## Never do

- Feed the KTRON VCC pad while the cell is connected.
- Connect an 8 Ω speaker directly to S+/S−.
- Send `AT+BTPOWER=1`. The module has Bluetooth inside, and it stays off.
