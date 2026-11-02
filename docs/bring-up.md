# Bring-up

## Bench checks when the parts arrive

Do these before anything goes into the case, and do the VoLTE call inside the seller's return window.

The phone firmware doesn't exist yet, so on the bench the **Mac talks to the modem through a USB-serial
adapter**: the owned CP2102 module with a 3.3 V pin. It connects to the same four KTRON pads that the T-Deck will
use later. The CP2102's signals are 3.3 V, the same as the T-Deck's, so no settings to change.

### Bench wiring: USB-serial adapter → KTRON

| Adapter pin | KTRON pad | Notes |
|---|---|---|
| TXD | RX | |
| RXD | TX | |
| 3V3 | VDD | Sets the board's signal level to 3.3 V, the same as the T-Deck. Draws only microamps |
| GND | GND | |
| 5V | — | **Leave unconnected** |

The adapter does **not** power the modem. The modem runs from the cell on the battery pad, the same way as in the
finished phone ([wiring.md](wiring.md), section 2). Never connect the adapter's 5V pin to VCC or anything else.

Leave the four data wires long. After the bench tests they move to the T-Deck's Grove pins.

### Steps

1. Remove the pin headers from the KTRON board and solder wires to the pads (see [wiring.md](wiring.md)).
2. **Battery pad check** with the multimeter: the pad you will feed must show continuity to the + leg of the
   330 µF capacitor, and **not** to VCC. Then connect the cell as in wiring.md.
3. **Bench set-up:** USB-serial adapter as in the table above, LTE antenna on U.FL1, GNSS patch on U.FL2,
   earpiece on S+/S−, mic on M+/M−, SIM in the holder on the back of the board.
4. **First contact:** open a serial terminal on the Mac (see below) at 115200 baud. Type `AT`, and you should get
   `OK`. Type `ATI` to see the modem's firmware build. If nothing comes back, swap the TX and RX wires at the
   adapter.
5. **Mic polarity:** the pin connected to the mic's metal can goes to M−.
6. **Earpiece:** listen test at `AT+CLVL=1` (quiet) during a call.
7. **GNSS:** after `AT+CGNSSPWR=1`, the centre pin of U.FL2 should read about 1.8–3.3 V DC (this is the
   antenna's power). Outdoors, `AT+CGNSSINFO` should get a position fix within a couple of minutes.
8. **VoLTE call** with a fresh SIM (see the warning below). Run the commands from the table further down. During
   the call, `AT+CPSI?` should show `LTE`.

### Serial terminal on the Mac

- **Arduino IDE Serial Monitor:** pick the adapter's port, set **115200 baud**, set line ending to
  **Carriage return** (or **Both NL & CR**). The modem ignores commands that don't end with a carriage return.
- **Or Terminal:** `ls /dev/cu.*` shows the adapter's name. Then `screen /dev/cu.<name> 115200`. To quit, press
  Ctrl-A, then K, then Y.
- If the Mac doesn't list the adapter at all, install Silicon Labs' CP210x USB-to-UART driver.

### SIM warning

KTRON's own note and an open LilyGO GitHub issue
([#231](https://github.com/Xinyuan-LilyGO/LilyGo-Modem-Series/issues/231)) both report the same problem. A
**Jio SIM that has ever been used in a 5G phone** may not register on the A7672S ("PLMN not allowed"). A SIMCom fix
is pending. Test with a fresh Jio SIM or an Airtel/Vi SIM.

There is no SIM-free audio loop test on SIMCom modules (`AT+QAUDLOOP` does not exist on them). Test audio with a
real call.

## T-Deck side (firmware)

```
GPIO10 HIGH (PWR_EN) + gpio_hold_en(10)    Grove 3.3 V stays on in light sleep
UART0 115200 8N1 on GPIO43 (TX) / GPIO44 (RX)
```

Sleep: the modem sleeps with `AT+CSCLK=2`, and any byte sent to it wakes it. The ESP32-S3 goes into light sleep
and wakes on serial data on GPIO44, so an incoming `RING` / `+CLIP:` wakes the phone.

## Modem commands

| Command | What it does |
|---|---|
| `ATI` | Shows the modem firmware build |
| `AT+CPMVT=1,3300,4300` | Clean power-off below 3.3 V |
| `AT+CSCLK=2` | Modem sleeps; any byte wakes it |
| `AT+CSDVC=1` | Call audio to the earpiece pins (S+/S−) |
| `AT+CLVL=1` | Earpiece volume, start quiet |
| `AT+CMICGAIN=3` | Mic gain (raise if the other person hears you faintly) |
| `AT+CGNSSPWR=1` | GNSS on. Then `AT+CGNSSINFO` for a position, or `AT+CGNSSINFO=10` for repeated reports |
| `AT+CLIP=1` | Caller number shown with each `RING` |
| `AT+CMGF=1` | SMS in text mode |
| `AT+CNMI=2,1,0,0,0` | Tell the T-Deck when a new SMS arrives. `AT+CMGS` sends, `AT+CMGR` reads |
| `AT*IMSRCFG="switch"` | Expect `"switch","on"`: the VoLTE path is on |
| `ATD+91XXXXXXXXXX;` | Dial (the `;` makes it a voice call) |
| `ATA` | Answer |
| `AT+CHUP` | Hang up |
| `AT+CPSI?` | During a call: `LTE` = VoLTE, `GSM` = 2G fallback |

Other audio commands: `AT+COUTGAIN` (output gain), `AT+CMUT` (mute the mic).

Messages the modem sends by itself: `RING`, `+CLIP:` (caller number), `VOICE CALL: BEGIN`, `VOICE CALL: END`.

**Never send `AT+BTPOWER=1`.** The module's built-in Bluetooth stays off.

### Spare Tracx-1b (Quectel EC200U) equivalents

GNSS: `AT+QGPS`, `AT+QGPSLOC=2`. Audio: `AT+CLVL`, `AT+QAUDMOD=2`.

## Manuals

- A76XX AT Command Manual V1.12:
  https://eicut.com/wp-content/uploads/2025/10/A76XX_Series_AT_Command_Manual_V1.12.pdf
- A7672S Hardware Design V1.00:
  https://www.ktron.in/wp-content/uploads/2023/03/A7672S_Hardware_Design_V1.00-1.pdf
