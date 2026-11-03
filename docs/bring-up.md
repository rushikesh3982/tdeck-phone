# Bring-up

## Bench checks when the parts arrive

The KTRON board arrives **without pin headers**: its holes are empty. So the bench tests need a few wires soldered
in. They are the same wires the finished phone uses, so nothing is wasted.

- **Phase A, bench tests.** Solder wires into only the 10 holes the phone needs. Power the board from a 5 V supply
  on VCC and test it from the Mac, inside the return window.
- **Phase B, after deciding to keep the board.** Remove the VCC wire and move the modem to battery power, as in the
  finished phone.

The phone firmware doesn't exist yet, so the **Mac talks to the modem through the CP2102 USB-serial adapter** (owned,
3.3 V pin). It uses the same four KTRON holes the T-Deck will use later. The CP2102's signals are 3.3 V, the same as
the T-Deck's, so there are no settings to change.

### What you need for phase A

- Soldering iron, solder, thin wire (24 AWG for the two power wires)
- KTRON board, CP2102 adapter, about 10 female-to-female jumper wires. Cut each in half. The cut end is soldered into
  the KTRON board, and the plug end goes onto the CP2102 or the 5 V supply.
- **5 V supply, at least 2 A:** a phone charger with a USB breakout board or a cut-open USB cable. KTRON's page gives
  the VCC input as 5–12 V DC. Use 5 V, because the board's regulator then runs coolest. Do **not** use the CP2102's
  5V pin: a Mac USB port can't reliably supply the modem's current bursts.
- LTE antenna (700–2700 MHz) and the IPX → SMA cable
- GPS patch antenna
- SIM: a fresh Jio SIM, or Airtel/Vi (see the SIM warning below). The holder takes **micro-SIM**.
- Multimeter
- Earpiece (the Micromax receiver) and a Sunrom mic

If something hasn't arrived yet, skip the step that needs it and come back to it. But don't run the network steps
without the LTE antenna.

### Phase A: the 10 holes to solder

```
left row:   STA  NET  DTR  RI  [VDD] [GND] [RX] [TX]  RST  1V8
right row:  CLK  CS  MOSI  MISO  [M-] [M+] [S-] [S+]  SCL  SDA  [GND] [VCC]
```

Solder only the holes in brackets, and leave the rest empty.

| KTRON hole | Wire goes to | Notes |
|---|---|---|
| RX (left) | CP2102 TXD | Leave the four data wires long. They move to the T-Deck's Grove pins later |
| TX (left) | CP2102 RXD | The modem's replies arrive on this wire |
| VDD (left) | CP2102 3V3 | Sets the signal level to 3.3 V. Draws only microamps |
| GND (left) | CP2102 GND | |
| — | CP2102 5V | **Leave unconnected** |
| VCC (right) | 5 V supply + | **Bench only**, removed in phase B. Check the supply's polarity with the multimeter first |
| GND (right) | 5 V supply − | Bench only, removed in phase B |
| S+ and S− | Earpiece | Either way round. Nothing to ground. Can be soldered straight in, because this is the final wiring |
| M+ and M− | Mic | The mic pin connected to its metal can → M−. Find it with the multimeter's continuity mode |
| U.FL1 (top edge) | LTE antenna cable | Press straight down until it clicks |
| U.FL2 (beside L2) | GPS patch | |

**Soldering tips:**

- Strip about 2 mm, twist and tin the wire, push it through the hole, solder, and trim what sticks out.
- The holes are 2.54 mm apart and the wanted ones sit side by side. Watch for solder bridges between neighbours.
- Keep the iron on each joint only for a couple of seconds.

There is **no battery in phase A**. VCC is the board's normal input. The "never feed VCC" rule only applies once the
cell is connected in phase B.

KTRON's warranty doesn't cover short-circuited boards, so check every joint before switching on.

### Phase A steps

0. **Look first.** Check the board for damage. Confirm it has **two** u.FL antenna sockets: U.FL1 at the top edge
   (LTE), and U.FL2 beside inductor L2 (GNSS). KTRON's product page only mentions one. Look up KTRON's return policy
   and note the last day. A board with soldered wires may not be accepted back, so check that too.
1. **Solder the 10 wires** as in the table. Then check, with the multimeter in continuity mode, between VCC and the
   GND next to it. A short beep that stops is just the capacitors charging. A steady beep means a solder bridge: fix
   it before going on. Look closely at every joint for bridges to the neighbouring holes.
2. **Power and serial, no SIM yet.** Connect the CP2102 and the 5 V supply. The power LED should light. If it
   doesn't, unplug at once and recheck the polarity. Open the serial terminal (see below), wait about 20 seconds for
   the modem to start, then type `AT`. You should get `OK`. If nothing comes back, swap TX and RX at the adapter.
   Then check that VDD is on 3V3, and that the terminal is set to 115200 baud with a carriage return. Type `ATI` and
   **write down the firmware build**. It matters if the Jio problem shows up.
3. **SIM and network.** Unplug the 5 V. Put the SIM in the holder on the back of the board. Make sure the LTE
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
4. **Call.** With the earpiece and mic connected, send `AT+CSDVC=1`, `AT+CLVL=1`, `AT+CMICGAIN=3` and `AT+CLIP=1`.
   - Call your other phone with `ATD+91XXXXXXXXXX;` and answer it. The modem prints `VOICE CALL: BEGIN`.
   - During the call, send `AT+CPSI?`. `LTE` means **VoLTE works**. `GSM` means it fell back to 2G.
   - Listen on the earpiece and talk into the mic. Raise `AT+CLVL` a step at a time if it's too quiet. If the other
     side hears you faintly, send `AT+CMICGAIN=5`.
   - Hang up with `AT+CHUP`.
   - Then call the module from your phone. `RING` and `+CLIP: "<number>"` appear. Answer with `ATA`.
5. **SMS (receive).** Send `AT+CMGF=1` and `AT+CNMI=2,1,0,0,0`. Send an SMS to the module from your phone.
   `+CMTI:` appears with a number at the end. `AT+CMGR=<that number>` shows the message. (Sending an SMS from the
   module needs Ctrl-Z to finish the message, which works in Terminal's `screen` but not in the Arduino Serial
   Monitor.)
6. **GNSS.** Take the patch outdoors with the ceramic side facing the sky, and send `AT+CGNSSPWR=1`. Then send
   `AT+CGNSSINFO` every minute or so. Empty commas = no fix yet. Latitude and longitude = fix. The first fix can take
   a few minutes. If there is still no fix after about 15 minutes outdoors, check the antenna power: the centre pin
   of U.FL2 should read about 1.8–3.3 V DC. Probe it carefully, because a slipped probe shorts it.
7. **Decide.** If everything passed, keep the board and go to phase B. If something failed, contact KTRON before
   the return deadline. If only Jio fails but Airtel/Vi works, that is the known Jio problem. Decide whether you can
   live with Airtel/Vi until SIMCom fixes it.

### Phase B: after deciding to keep the board

1. Unplug the 5 V supply. Desolder the two bench power wires (VCC and the GND beside it). From now on the **VCC
   hole is never used again**.
2. **Swap the two tall capacitors.** The stock ones are 11 mm tall SMD cans, too tall for the board to fit under the
   9 mm battery. Before removing each one, note which pad is +.
   - **C11** (330 µF 50 V, next to the modem chip): replace it with the **470 µF 16 V** radial capacitor, laid flat
     (about 7 mm high). Solder its leads flat onto the old pads.
   - **C17** (100 µF 50 V, next to the regulator): replace it with the **100 µF 16 V**, laid flat. If its + pad
     beeps to the VCC pin, you can leave it off instead, because VCC isn't used on battery power.
   - **Glue both bodies to the board** with hot glue or silicone, so they can't lever the pads off.
   - Lay them on bare board or small resistors and capacitors, **not** on the modem chip or the regulator.
     Nothing on that side may stand more than 8 mm off the board, because the back's standoffs are 9 mm.
3. **Battery pad check** with the multimeter: the pad you will feed must show continuity to the + pad of C11, and
   **not** to VCC. Then connect the cell (through the modem power switch, if it's built) as in
   [wiring.md](wiring.md), section 2.
4. Repeat `AT` → `OK` and one test call, now on battery power.
5. **LEDs:**
   - **Power LED (PWR):** check it on battery power. If it's dark, it's on the unused VCC input and draws nothing,
     so leave it. If it lights, it's on the battery rail and draws about 2 mA all the time. Remove its resistor R6
     (1 kΩ, just below it).
   - **Network LED (NETLIGHT):** once registered it is lit half the time (200 ms on / 200 ms off) through R1
     (220 Ω, beside it). That's roughly 2–4 mA on average, depending on the LED's colour, and the AT commands
     can't switch it off. To save power but keep it visible through the back's window, replace R1 with a 1 kΩ
     0805, which uses about a fifth of the current. Or remove R1 to turn it off completely.

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
