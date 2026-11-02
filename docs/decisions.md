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
analog audio (one mic in, one earpiece out) on reachable header pads. Small board (54.33 × 50.70 mm), in stock,
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

## Data link: wires soldered to the Grove socket pins

**Why:** it is the T-Deck's only free external port. Soldering instead of using a Grove plug frees the case's
plug-clearance slot for the LTE antenna. The Grove 3.3 V only provides the modem board's level-shifter reference.
It is switched by GPIO10, so the firmware must hold GPIO10 high, even in sleep.

## Bench tests: USB-serial adapter from the Mac (decided 2 Nov 2026)

**Why:** the modem has to be tested (registration, VoLTE call, audio, GNSS) inside the seller's return window, and
no phone firmware exists yet. A CP2102 USB-serial adapter with a 3.3 V pin (already owned) connects to the same four KTRON pads the
T-Deck will use later (TX, RX, VDD, GND), so the Mac can send modem commands straight away.

**Not chosen:** a small T-Deck "pass-through" program, because it would have to be written before the first test.

## Power: one salvaged cell for both boards

**Why:** the 1700 mAh Micromax pack is already owned, about 5 mm thick and has its own protection circuit. The
T-Deck's charger stops at 4.2 V, which suits it.

**Modem feed:** straight from the cell to the modem board's regulator output (MIC29302 pin 4, or the + leg of
the 330 µF capacitor). The regulator stays fitted and does nothing. Its datasheet allows output above input with
no reverse current. The module's own supply window (3.4–4.2 V) matches a single lithium cell.

**Optional for v2:** replace the regulator with a buck-boost set to 3.9 V (the T-Deck MAX does this with an
SGM6609).

## Modem power switch: manual slide switch + AO3401A P-MOSFET

**Why a switch at all:** the modem is wired straight to the battery, so the T-Deck's own power switch doesn't turn it
off. There is no spare GPIO for the T-Deck to switch or reset the modem itself. Without a switch, the modem stays on
whenever the battery is connected, and a frozen modem can only be restarted by opening the case.

**Why a MOSFET:** the switch goes in the case's existing slide-switch pocket, which only fits a small switch. A
plain slide switch carrying the modem current directly would need a rating of at least 1.5 A. With the MOSFET, the
small switch carries only about 40 µA through a 100 kΩ resistor, and the MOSFET (rated about 4 A) carries the
modem's current. Circuit in [wiring.md](wiring.md), section 2.

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
  which misses most of the Indian LTE bands (B1, B3, B5, B8, B40). Placed at the top corner opposite the LoRa antenna, for symmetry and to stay
  away from the T-Deck's Wi-Fi/BT antenna at the top centre.
- **GNSS:** KTRON KSTA1417 active ceramic patch, ₹105, on U.FL2, which powers active antennas. At least 60 mm from
  the LTE antenna.
- **LoRa:** unchanged, the T-Deck's own cable and the case's existing antenna hole.

## Case: Alley Cat TD1, Standard front (GPS inserts) + X back

**Why:** the Standard front keeps the T-Deck speaker pocket. The GPS version's module pocket becomes the earpiece
pocket and its switch pocket becomes the modem power switch. The X back gives 23 mm of depth, enough for the
modem board on 14 mm standoffs plus the battery (21.6 mm stack).

**Rejected:** Slim front (no speaker pocket), Nuts and TBall variants.

Details in [case.md](case.md).
