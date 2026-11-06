# Decisions

Why each part was chosen and what was turned down. All of these were settled on 2 Nov 2026 and are final unless
a section says otherwise.

## The phone needs a separate modem board

The LilyGO T-Deck has no cellular radio. Its only free external port is the Grove UART socket, so a modem board
connects there. Call audio runs on the modem (analog earpiece and mic wired to the modem board), not through the
ESP32.

Indian networks: Jio is 4G-only and carries calls as VoLTE. Airtel and Vi 2G is shrinking. The modem must cover FDD
B1/B3/B5/B8 and TDD B40/B41, **and** support VoLTE.

## Modem: KTRON KSTM1548 (SIMCom A7672S-FASE), ₹1,530

https://www.ktron.in/product/sim-a7672s-4g-lte-2g-gnss-development-board/

**Why:** LTE Cat-1 on FDD B1/B3/B5/B8 + TDD B34/B38/B39/B40/B41, GSM 900/1800 fallback, built-in GNSS, and
analog audio (one mic in, one earpiece out) on reachable pads. Small board (54.33 × 57.23 mm), in stock,
and KTRON publishes the drawings, audio reference circuit and Eagle library.

**Known risk:** a Jio SIM that has ever been used in a 5G phone may not register ("PLMN not allowed"). SIMCom's
fix is pending. Test with a fresh Jio SIM or an Airtel/Vi SIM, inside the return window.

**Rejected:**

| Option | Why not |
|---|---|
| Valetron A7672S-FASE eval board, ₹2,399 | Dearer and larger (75 × 50 mm, LiPo input); audio pads not confirmed on the product page |
| Valetron A7672S-LASC, ₹1,499 | No GNSS |
| Valetron A7670C-LASS, ₹1,199 | Vendor contradicts itself on voice support |
| rhydoLABZ A7672S-FASE, ₹2,499 + GST | Most expensive, and needs a 5–12 V supply (it does claim Jio VoLTE and has a 3.5 mm jack) |
| Vanix Tracx-1b, Quectel EC200U-CN (owned) | No audio pads. The module's speaker/mic pins (73/74/75/77) are centre pads under the module and can't be reached. Kept for data/GPS tests or to sell |
| Waveshare A7670E HAT | No TDD bands |
| Waveshare SIM7600G-H HAT, ₹6–8k | Expensive, 5 V, big |
| LilyGO T-A7670G | Has its own ESP32, so it duplicates the T-Deck |

## Data link: wires soldered to the T-Deck's Grove pads

**Why:** it is the T-Deck's only free external port. The Grove socket itself is desoldered and the wires are
soldered to its pads. That frees the case's Grove plug slot, and its corner now has a second SMA antenna cut-out. The Grove 3.3 V only provides the modem board's level-shifter reference.
It is switched by GPIO10, so the firmware must hold GPIO10 high, even in sleep.

## Bench tests: USB-serial adapter from the Mac (decided 2 Nov 2026)

**Why:** the modem has to be tested (registration, VoLTE call, audio, GNSS) inside the seller's return window, and
no phone firmware exists yet. A CP2102 USB-serial adapter with a 3.3 V pin (already owned) connects to the same four KTRON pads the
T-Deck will use later (TX, RX, VDD, GND), so the Mac can send modem commands straight away.

**Not chosen:** a small T-Deck "pass-through" program, because it would have to be written before the first test.

**First tests on a 5 V supply:** KTRON's page gives the VCC input as 5–12 V DC. The board arrives without pin
headers, so the bench tests solder wires into just the 10 holes the phone needs. These are the same wires the phone
uses later. The board runs from 5 V on VCC until Jio, VoLTE and GNSS have been checked, so the battery wiring waits
until the board is known to be good. The VCC wire comes out before the battery goes in.

## Power: one cell for both boards

**Why:** the 5000 mAh pack is already owned (65 × 55 × 9 mm). (Earlier notes called it the 1700 mAh Micromax pack; the owner
confirmed 5000 mAh on 6 Nov 2026.) Its label reads HH 955465, IEC 62133-2. It's a bare cell with no protection circuit
(bare tabs, made for power banks), so a 1S protection board goes on its tabs. Nominal thickness is 9.5 mm, which leaves
about 0.4 mm spare in the back's 23 mm depth. The
T-Deck's charger stops at 4.2 V, which suits it.

**Modem feed:** straight from the cell to the modem board's regulator output (MIC29302 pin 4, or the + pad of
C11, the bulk capacitor). The regulator stays fitted and does nothing. Its datasheet allows output above input with
no reverse current. The module's own supply window (3.4–4.2 V) matches a single lithium cell.

**Optional for v2:** replace the regulator with a buck-boost set to 3.9 V (the T-Deck MAX does this with an
SGM6609).

## KTRON's tall capacitors swapped for radial ones laid flat (decided 3 Nov 2026)

**Why:** the battery turned out to be 9 mm thick, not 5 mm. The board's two SMD electrolytics (C11 330 µF 50 V and
C17 100 µF 50 V) are 11 mm tall and hang below the board, so with them the stack would be
12 + 1.6 + 1.5 + 9 = 24.1 mm, more than the 23 mm available.

**What:** owned radial capacitors laid flat, glued to the board:

- **C11 → 470 µF 16 V** (6–7 × 12 mm). It sits on the modem's battery rail, which never exceeds 4.2 V, and the
  extra capacitance helps with transmit bursts.
- **C17 → 100 µF 16 V** (4–5 × 8 mm), or left off. Its + leg read 4.97 V with 5 V on VCC (5 Nov 2026), which fits it being the regulator's input on VCC, which is unused on
  battery power. 16 V also covers a 12 V supply if VCC is ever used again.

The standoffs drop to 9 mm and the SIM slit ends up fully inside the back's wall.

**Not chosen:** SMD 6.3 V parts (330 µF 6.3 × 7.7 mm, 100 µF 5 × 5.3 mm). They would fit the old pads, but a 6.3 V
capacitor is unsafe on VCC, and they would have to be bought. A thinner battery was not chosen either.

## Status LED: one window, for the network LED (decided 3 Nov 2026)

**Why:** a glance at the back shows whether the modem is searching (lit steadily) or registered (200 ms on /
200 ms off, from SIMCom's A7672S hardware design guide). The power LED gets no window. KTRON describes it as
showing the input supply, so on battery power (VCC unused) it should stay dark. If it turns out to be on the
battery rail, its resistor R6 comes off.

**Power:** the network LED runs through 220 Ω (R1) and is lit half the time when registered, roughly 2–4 mA on
average. The A76XX AT command manual has no command to turn it off. Replacing R1 with 1 kΩ is the suggested
compromise.

## Modem power switch: SS-12F15 slide switch on the left side (decided 6 Nov 2026)

**What:** a small SS-12F15 slide switch (owned, 4 mm knob) in the modem's battery + wire. It sits in Alley Cat's
original slide-switch mount on the front's left side, which was drawn for exactly this switch: 15 mm screw spacing,
2.2 mm holes, a 6.9 × 3.4 mm slot for its 3 × 3 mm knob. The mount is restored; it had been filled. Circuit in
[wiring.md](wiring.md), section 2.

**Why:** simpler and cheaper than the MOSFET pair: one part already owned, two solder joints, no SOT-23 soldering.
And the mount already exists.

**Accepted trade-offs:**
- **Two switches:** the T-Deck and the modem are switched separately, so switch both off together. A modem left on
  drains the 5000 mAh cell in about 10 days.
- **Current rating:** about 0.5 A, against the modem's 2 A transmit bursts. The average stays far below 0.5 A, and
  C11's 470 µF right after the switch smooths the bursts. If 2G calls ever reset the modem on a low battery, the switch
  can instead drive one AO3401A's gate.
- **Battery position:** the battery moves about 9 mm toward the phone's right to clear the switch's body and pins.
  This was checked against the case files.

## Earlier plan (replaced 6 Nov 2026): modem follows the T-Deck's own switch (decided 3 Nov 2026)

**Why a switch at all:** the modem is wired straight to the battery, so on its own it would stay on whenever the
battery is connected. The T-Deck's power switch wouldn't reach it, and a frozen modem could only be restarted by
opening the case.

**What:** an AO3401A P-MOSFET in the modem's battery feed, turned on through an AO3400A N-MOSFET by the Grove 3.3 V.
That wire is already connected to the KTRON's VDD pad, and it only has power while the T-Deck is on (GPIO10 high).
So the T-Deck's own power switch turns the modem on and off as well. The MOSFET (rated about 4 A) carries the
modem's current. Circuit in [wiring.md](wiring.md), section 2.

**Not chosen:** a separate slide switch driving the MOSFET, which was the handoff's plan. It would have used the
front's left-side switch mount (filled in at the time; restored on 6 Nov 2026 for the SS-12F15), and it's
one more control to remember.

**Trade-off:** the modem can't be switched off on its own while the T-Deck stays on.

## Sleep and wake-on-call

**Why:** the modem sleeps with `AT+CSCLK=2` (any byte wakes it). The ESP32-S3 uses light sleep and wakes on serial
data on GPIO44, so `RING` / `+CLIP:` wake the phone. The modem board's RI pin would be an alternative, but no GPIO
is free for it.

## Ringtone on the T-Deck speaker

**Why:** the T-Deck already has a speaker (MAX98357A amp). The ESP32 plays the ringtone when `RING` arrives, so no
third speaker is needed.

## Earpiece: salvaged Micromax 32 Ω receiver

**Why:** the modem's earpiece output (EAR_P/EAR_N on S+/S−) is a 37 mW driver made for a 32 Ω receiver, with no
amplifier on the board. The Micromax earpiece is the right part and already owned.

**Wired through two 47 µF capacitors** (added 4 Nov 2026), one in each wire. SIMCom's A7672S Hardware Design
(figure 28) and KTRON's speaker/mic circuit both show them. They block any steady current through the earpiece's
coil, and with 32 Ω they still pass everything down to about 200 Hz, which covers voice.

**Fallbacks:** PUI AR01532MS (DigiKey India, ₹344 + ₹1,200 delivery), any 25–32 Ω phone ear speaker, or a wired
earphone driver for bench tests.

## Microphone: Sunrom 6027 electret, 6 × 2.7 mm, ₹20.70

**Why:** the modem has an analog mic input with its own electret bias, so a plain 2-wire electret mic works with
no extra parts. It is small enough for a pocket in the case's bottom edge.

**Rejected:**

| Option | Why not |
|---|---|
| INMP441 | Digital (I2S) mic. Can't connect to an analog mic input |
| Primo EM272 | Works electrically, but ~15 dB too hot, and the quality is wasted behind the modem's codec |

## Speakerphone: version 2

**Why later:** the A7672S has only one audio output. A speakerphone needs an amplifier tapping S+ (one leg only)
in parallel with the earpiece, powered from the cell through a switch. Options: SmartElex Digital Speaker Module
(Robu, ₹189) or Waveshare 2030 cavity speaker (ThinkRobotics, ₹300) + PAM8403 board. The Micromax rear loudspeaker
(8 Ω) and vibration motor are kept for this. Never connect an 8 Ω speaker directly to S+/S−.

## Bluetooth inside the module: never enabled

The A7672S has Bluetooth built in. It stays off: never send `AT+BTPOWER=1`.

## Antennas

- **LTE:** an external SMA antenna **rated 700–2700 MHz**, through a short IPX → SMA female cable to U.FL1.
  Rejected: the KTRON "4G LTE 3.5 dBi foldable" antenna. It is out of stock, and its own spec says 2.4–5 GHz,
  which misses most of the Indian LTE bands (B1, B3, B5, B8, B40). Both top corners of the front have identical SMA cut-outs. The 4G antenna goes top-right
  (old Grove corner), close to the modem's 4G socket, and away from the T-Deck's Wi-Fi/BT antenna at the top centre.
- **GNSS:** KTRON KSTA1417 active ceramic patch, ₹105, on U.FL2, which powers active antennas. At least 60 mm from
  the LTE antenna.
- **LoRa:** unchanged, the T-Deck's own cable and the case's existing antenna hole.

## Case: Alley Cat TD1, Standard front (GPS inserts) + X back

**Why:** the Standard front keeps the T-Deck speaker pocket. The GPS version's module pocket becomes the earpiece
pocket. The X back gives 23 mm of depth, enough for the
modem board on 9 mm standoffs plus the 9 mm battery (22.1 mm stack).

**Rejected:** Slim front (no speaker pocket), Nuts and TBall variants.

Details in [case.md](case.md).
