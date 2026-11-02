# Wiring

Everything is soldered. The only plug is the battery's JST plug into the T-Deck. The pin headers come off the
KTRON board and wires are soldered straight to its pads.

## KTRON board pads

```
left header:   STA  NET  DTR  RI  VDD  GND  RX  TX  RST  1V8
right header:  CLK  CS  MOSI  MISO  M-  M+  S-  S+  SCL  SDA  GND  VCC
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

The T-Deck has no spare GPIO, so the modem's power is a manual switch. A slide switch drives an AO3401 P-MOSFET
in the battery + line to the modem. It sits in the case's GPS switch pocket. A slide switch used on its own,
without the MOSFET, must be rated for at least 1.5 A. (The exact switch circuit is not drawn yet.)

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
