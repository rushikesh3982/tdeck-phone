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

Four wires soldered to the Grove socket pins on the back of the T-Deck board. No Grove plug.

| T-Deck Grove pin | ESP32-S3 pin | Direction | KTRON pad | Notes |
|---|---|---|---|---|
| TX | GPIO43 | → | RX | |
| RX | GPIO44 | ← | TX | Incoming calls (`RING`) arrive on this wire |
| VCC (switched 3.3 V) | switched by GPIO10 | → | VDD | Reference for the board's level shifters only (microamps). Does **not** power the modem |
| GND | — | — | GND | |

Serial settings: 115200 baud, 8N1.

**Important:** the Grove 3.3 V is switched on and off by GPIO10 (PWR_EN). The firmware must keep GPIO10 HIGH all
the time, including in light sleep (`gpio_hold_en`). If it drops, the level shifters lose their reference and
incoming-call messages never reach the T-Deck.

The board's RI (ring indicator) pad is not wired in v1 because the T-Deck has no spare GPIO.

## 2. Power: one battery for both boards

The cell is the 1700 mAh pack from the Micromax Canvas A1. It has its own protection circuit. Use only its
+ and − terminals and ignore the thermistor pin.

```
 Cell + ──┬── JST PH2.0 plug ─────────────────────► T-Deck battery socket (+)
          │
          └── modem switch (slide switch + AO3401) ─► KTRON: MIC29302 pin 4 (OUTPUT)
                                                        or the + leg of the 330 µF capacitor
 Cell − ──┬── JST PH2.0 plug ─────────────────────► T-Deck battery socket (−)
          │
          └──────────────────────────────────────► KTRON GND (the regulator's metal tab)
```

- The modem pair is joined at the battery terminals, not run through the Grove wires.
  Use 24 AWG wire, 10 cm or shorter.
- **Never feed the KTRON VCC pad while the cell is connected.**
- The board's MIC29302 regulator (K1) stays on the board but does nothing. Its datasheet allows the output to sit
  above the input with no reverse current, and its enable pin is low when nothing is on VCC.
- **Before soldering:** with the multimeter, check that the pad you chose has continuity to the + leg of the
  330 µF capacitor and **not** to VCC.
- The T-Deck's own charger charges the cell over USB-C and stops at 4.2 V, which suits this cell.
- The modem runs from 3.4 V to 4.2 V. The firmware turns the modem off cleanly below 3.3 V
  (`AT+CPMVT=1,3300,4300`). The screen treats a battery reading under 3.5 V (BAT_ADC, GPIO4) as "modem off".

### Modem power switch

**Why it's needed:** the modem's battery wires join at the battery, so the T-Deck's own power switch doesn't turn
the modem off. The T-Deck also has no spare pin to control the modem's power. Without this switch the modem stays
on whenever the battery is connected, and the only way to restart a frozen modem would be to open the case.

**Parts:** AO3401A P-MOSFET (SOT-23), one 100 kΩ resistor, and a small slide switch. (Where the switch goes in the case is decided
with the back.)

```
                       AO3401A (P-MOSFET)
                    ┌──────────────────────┐
 Cell + ─────────┬──┤ S (pin 2)  D (pin 3) ├───────────► KTRON: MIC29302 pin 4 (OUTPUT)
 (24 AWG)        │  │      G (pin 1)       │               or the + leg of the 330 µF capacitor
                 │  └──────────┬───────────┘               (24 AWG)
              100 kΩ           │
                 │             │
                 └─────────────┤
                               │  thin wire
                               │
                               o
                                /    slide switch
                               o
                               │  thin wire
 Cell − ───────────────────────┴───────────────────────► KTRON GND (the regulator's metal tab)
```

The resistor goes between the MOSFET's **S** and **G** pins.

**How it works:**

- **Switch open = modem OFF.** The 100 kΩ resistor holds the gate at battery voltage, so the MOSFET is off and the
  modem gets no power.
- **Switch closed = modem ON.** The switch pulls the gate to ground, the MOSFET turns on, and the modem gets the
  battery. The resistor then draws about 40 µA, tiny next to what the modem uses.
- The slide switch only ever carries that 40 µA, so any small slide switch will do. The
  modem's current (bursts up to about 1.5–2 A) goes through the MOSFET, which is rated about 4 A.
- With a 3-pin slide switch, use the **middle pin** and **one outer pin**. Leave the other outer pin unconnected.
  Which way is "on" depends on which outer pin you pick.

**Building it:**

- The AO3401A is tiny (SOT-23, about 3 × 1.4 mm). A SOT-23 adapter board makes it much easier to solder. The
  resistor can sit on the same adapter board.
- Put the MOSFET in the back half of the case, in the battery + wire between the pack and the KTRON board. Keep
  the whole 24 AWG run 10 cm or shorter. Only the two thin wires (gate and ground) run to the switch.
- Cover the joints with heat-shrink.

**Checks with the multimeter:**

1. **Before soldering, find the pins.** In diode-test mode, put the red probe on D (pin 3) and the black probe on
   S (pin 2). It should read about 0.5–0.8 V. With the probes swapped it should read OL. This is the MOSFET's
   built-in diode, and it tells you which pin is which.
2. **After wiring it to the KTRON board:** switch on, and the + leg of the 330 µF capacitor reads the battery
   voltage. Switch off, and it falls to about 0 V within a few seconds.
3. **With the modem running,** measure from S to D. It should read under about 0.1 V. More than that means the
   MOSFET isn't fully on.
4. **If the switch never turns the modem off,** S and D are swapped. The built-in diode is then feeding the modem.

**Simpler alternative:** no MOSFET or resistor, just a slide switch rated **at least 1.5 A** directly in the battery +
wire to the modem. A switch with that rating is usually bigger, so it is harder to fit in the case.

## 3. Earpiece (call audio out)

The earpiece receiver from the Micromax Canvas A1: the **32 Ω** part from the top of the phone, under the
earpiece slot. Not the 8 Ω rear loudspeaker.

- Solder two wires at the base of its spring contacts.
- Connect straight across **S+ and S−**. Polarity does not matter. **Nothing goes to ground.**
- Keep its foam ring.

S+/S− are the module's EAR_P/EAR_N outputs, a 37 mW driver made for a 32 Ω receiver. There is no amplifier on the
board. **Never connect an 8 Ω speaker directly to S+/S−.**

## 4. Microphone

A 2-wire electret mic (Sunrom 6027) across **M+ and M−**. The module provides the mic bias on M+.

- The mic's pin or pad that connects to its metal can → **M−**.
- The other pin → **M+**.

If the person you call hears you faintly, raise the gain with `AT+CMICGAIN=5` or higher.

## 5. Ringtone

The T-Deck's own speaker plays the ringtone when the modem sends `RING`. No extra wiring and no third speaker.

## 6. Antennas

| Antenna | Connects to | Part | Where it goes |
|---|---|---|---|
| LTE | KTRON U.FL1 (top edge) | SMA antenna rated 700–2700 MHz, through the IPX → SMA female cable | Case top corner opposite the LoRa antenna. Away from the top centre, where the T-Deck's Wi-Fi/BT antenna is |
| GNSS | KTRON U.FL2 (beside L2; it powers an active antenna) | KTRON KSTA1417 active patch | Bottom half of the back, at least 60 mm from the LTE antenna, ceramic side toward the back cover |
| LoRa | T-Deck's own u.FL | T-Deck's own u.FL-to-SMA cable | The case's existing antenna hole (or the printed plug if the LoRa antenna stays inside) |

## Version 2: speakerphone

The A7672S has only one audio output. For a speakerphone, an amplifier input taps **S+ only** (S− left alone),
in parallel with the earpiece. The amplifier is powered from the cell through its own switch. Parts are listed
in [../bom.md](../bom.md).

## Never do

- Feed the KTRON VCC pad while the cell is connected.
- Connect an 8 Ω speaker directly to S+/S−.
- Send `AT+BTPOWER=1`. The module has Bluetooth inside, and it stays off.
