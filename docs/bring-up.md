# Bring-up

## Bench checks when the parts arrive

The bench tests come in two phases:

- **Phase A, no soldering.** Test everything on the KTRON board's own pin headers, using plug-on jumper wires and a
  5 V supply. Nothing is soldered to the board, so it can still go back to KTRON if Jio, VoLTE or GNSS fails. Do this
  inside the return window.
- **Phase B, after deciding to keep the board.** Remove the headers, solder wires, and move the modem to battery
  power, as in the finished phone.

The phone firmware doesn't exist yet, so the **Mac talks to the modem through the CP2102 USB-serial adapter** (owned,
3.3 V pin). It uses the same four KTRON pins the T-Deck will use later. The CP2102's signals are 3.3 V, the same as
the T-Deck's, so there are no settings to change.

### What you need for phase A

- KTRON board, CP2102 adapter, about 10 female-to-female jumper wires
- **5 V supply, at least 2 A:** a phone charger with a USB breakout board or a cut-open USB cable. KTRON's page gives
  the VCC input as 5–12 V DC. Use 5 V, because the board's regulator then runs coolest. Do **not** use the CP2102's
  5V pin: a Mac USB port can't reliably supply the modem's current bursts.
- LTE antenna (700–2700 MHz) and the IPX → SMA cable
- GPS patch antenna
- SIM: a fresh Jio SIM, or Airtel/Vi (see the SIM warning below). The holder takes **micro-SIM**.
- Multimeter
- Earpiece with two wires soldered to it, and a Sunrom mic (its pins push into jumper-wire ends)

If something hasn't arrived yet, skip the step that needs it and come back to it. But don't run the network steps
without the LTE antenna.

### Phase A wiring (on the header pins)

| From | KTRON pin | Notes |
|---|---|---|
| CP2102 TXD | RX (left header) | |
| CP2102 RXD | TX (left header) | The modem's replies arrive on this wire |
| CP2102 3V3 | VDD (left header) | Sets the signal level to 3.3 V. Draws only microamps |
| CP2102 GND | GND (left header) | |
| CP2102 5V | — | **Leave unconnected** |
| 5 V supply + | VCC (right header) | **Check the polarity with the multimeter first** |
| 5 V supply − | GND (right header) | |
| Earpiece | S+ and S− | Either way round. Nothing to ground |
| Mic | M+ and M− | The mic pin connected to its metal can → M−. Find it with the multimeter's continuity mode |
| LTE antenna cable | U.FL1 (top edge) | Press straight down until it clicks |
| GPS patch | U.FL2 (beside L2) | |

There is **no battery in phase A**. VCC is the board's normal input. The "never feed VCC" rule only applies once the
cell is connected in phase B.

KTRON's warranty doesn't cover short-circuited boards, so check every wire before switching on.

### Phase A steps

0. **Look before powering.** Check the board for damage. Confirm it has **two** u.FL antenna sockets: U.FL1 at the
   top edge (LTE), and U.FL2 beside inductor L2 (GNSS). KTRON's product page only mentions one. Look up KTRON's
   return policy and note the last day you can return the board.
1. **Power and serial, no SIM yet.** Connect the CP2102 and the 5 V supply. The power LED should light. If it
   doesn't, unplug at once and recheck the polarity. Open the serial terminal (see below), wait about 20 seconds for
   the modem to start, then type `AT`. You should get `OK`. If nothing comes back, swap TX and RX at the adapter.
   Then check that VDD is on 3V3, and that the terminal is set to 115200 baud with a carriage return. Type `ATI` and
   **write down the firmware build**. It matters if the Jio problem shows up.
2. **SIM and network.** Unplug the 5 V. Put the SIM in the holder on the back of the board. Make sure the LTE
   antenna is connected. Power on and wait about 30 seconds.

   | Command | Good answer |
   |---|---|
   | `AT+CPIN?` | `+CPIN: READY` (SIM found) |
   | `AT+CSQ` | First number 10–31 is usable signal. `99` = no signal |
   | `AT+CEREG?` | Second number `1` (home) or `5` (roaming) = registered on 4G. `2` = still searching. `3` = refused (on a Jio SIM this is the known problem: try an Airtel/Vi SIM) |
   | `AT+COPS?` | Operator name |
   | `AT+CPSI?` | Shows LTE and the band |
   | `AT*IMSRCFG="switch"` | `"switch","on"` (VoLTE path on) |

   The network LED also changes its blink pattern once the modem is registered.
3. **Call.** Connect the earpiece and mic. Then send `AT+CSDVC=1`, `AT+CLVL=1`, `AT+CMICGAIN=3`, `AT+CLIP=1`.
   - Call your other phone with `ATD+91XXXXXXXXXX;` and answer it. The modem prints `VOICE CALL: BEGIN`.
   - During the call, send `AT+CPSI?`. `LTE` means **VoLTE works**. `GSM` means it fell back to 2G.
   - Listen on the earpiece and talk into the mic. Raise `AT+CLVL` a step at a time if it's too quiet. If the other
     side hears you faintly, send `AT+CMICGAIN=5`.
   - Hang up with `AT+CHUP`.
   - Then call the module from your phone. `RING` and `+CLIP: "<number>"` appear. Answer with `ATA`.
4. **SMS (receive).** Send `AT+CMGF=1` and `AT+CNMI=2,1,0,0,0`. Send an SMS to the module from your phone.
   `+CMTI:` appears with a number at the end. `AT+CMGR=<that number>` shows the message. (Sending an SMS from the
   module needs Ctrl-Z to finish the message, which works in Terminal's `screen` but not in the Arduino Serial
   Monitor.)
5. **GNSS.** Take the patch outdoors with the ceramic side facing the sky, and send `AT+CGNSSPWR=1`. Then send
   `AT+CGNSSINFO` every minute or so. Empty commas = no fix yet. Latitude and longitude = fix. The first fix can take
   a few minutes. If there is still no fix after about 15 minutes outdoors, check the antenna power: the centre pin
   of U.FL2 should read about 1.8–3.3 V DC. Probe it carefully, because a slipped probe shorts it.
6. **Decide.** If everything passed, keep the board and go to phase B. If something failed, contact KTRON before
   the return deadline. If only Jio fails but Airtel/Vi works, that is the known Jio problem. Decide whether you can
   live with Airtel/Vi until SIMCom fixes it.

### Phase B: after deciding to keep the board

1. Unplug the 5 V supply. From now on the **VCC pin is never used again**.
2. Remove the pin headers and solder wires to the pads (see [wiring.md](wiring.md)). Leave the four data wires long.
   They move to the T-Deck's Grove pins later.
3. **Battery pad check** with the multimeter: the pad you will feed must show continuity to the + leg of the
   330 µF capacitor, and **not** to VCC. Then connect the cell (through the modem power switch, if it's built) as in
   [wiring.md](wiring.md), section 2.
4. Repeat `AT` → `OK` and one test call, now on battery power.

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
