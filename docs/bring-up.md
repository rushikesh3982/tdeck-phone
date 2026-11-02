# Bring-up

## Bench checks when the parts arrive

Do these before anything goes into the case, and the VoLTE call inside the seller's return window.

1. Remove the pin headers from the KTRON board and solder wires to the pads (see [wiring.md](wiring.md)).
2. **Battery pad check** with the multimeter: the pad you will feed must show continuity to the + leg of the
   330 µF capacitor, and **not** to VCC.
3. **Mic polarity:** the pin connected to the mic's metal can goes to M−.
4. **Earpiece:** listen test at `AT+CLVL=1` (quiet) during a call.
5. **GNSS:** after `AT+CGNSSPWR=1`, the centre pin of U.FL2 should read about 1.8–3.3 V DC (this is the
   antenna's power). Outdoors, `AT+CGNSSINFO` should get a position fix within a couple of minutes.
6. **VoLTE call** with a fresh SIM (see the warning below).

Not decided yet: how to send these commands before the phone firmware exists.

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
