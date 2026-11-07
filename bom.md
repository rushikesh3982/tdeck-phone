# Bill of materials

Prices are in rupees and include GST unless noted. Status as of 7 Nov 2026.

## Still to order (7 Nov 2026), both from Robu

| Part | Where | Notes |
|---|---|---|
| **1S Li-ion protection board, 3 A, two MOSFETs** ("1S 3.7V 3A 2MOS BMS") | [Robu](https://robu.in/product/1s-3-7v-3a-2mos-bms-li-ion-18650-battery-protection-board/) | For the bare 5000 mAh cell. Why this one: see "Small parts" below. Cheap, so a spare is worth adding |
| **LoRa antenna: "865–868 MHz 1.8 dBi Gain Rubber Duck Antenna"** (Lambdoid LWC-868-RD-ST-SMA-PLUG-02) | [Robu](https://robu.in/product/865-868mhz-1-8-dbi-gain-rubber-duck-antenna/) | 50 × 10 mm stubby, SMA male, 865–868 MHz (India's LoRa band), **LoRa only** (no 4G). For the top-left hole, because the T-Deck's own antenna now serves 4G. **Not** Robu's "865–868 MHz 1 dBi" listing: that one is 210 mm long. Check first: the T-Deck must be the 868 MHz version, and the T-Deck's LoRa cable end must be plain SMA (a hole in the centre, not a pin) |

## Version 1 parts (all owned now)

| # | Part | Where | Price | Status | Notes |
|---|---|---|---|---|---|
| 1 | KTRON KSTM1548: SIMCom A7672S 4G + GNSS development board | [ktron.in](https://www.ktron.in/product/sim-a7672s-4g-lte-2g-gnss-development-board/) | ₹1,530 | owned, bench-tested | 54.33 × 57.23 mm, 28 g |
| 2 | KTRON GPS active patch antenna KSTA1417 | [ktron.in](https://www.ktron.in/product/gps-antenna-with-ufl-female-connector/) | ₹105 | owned, works | 25 × 25 × ~8 mm, 4 corner holes, short u.FL lead |
| 3 | KTRON IPX → SMA female antenna cable, 10 cm | [ktron.in](https://www.ktron.in/product/rf-cable-ipx-to-sma-female-10cm-length/) | ≈₹44 | owned | 10 cm for the top-right corner (recommended). The 15 cm version ([KSTA0380](https://www.ktron.in/product/rf-cable-ipx-to-sma-female/), ₹42) if the 4G antenna goes top-left. Comes with nut and washers |
| 4 | LTE antenna, SMA male, **rated 700–2700 MHz** | any | ~₹100–200 | **not owned: fallback only** | The bench tests used the full-band sticker (below) instead. Buy one only if the sticker is too weak inside the case. **Not** the KTRON "4G LTE 3.5 dBi foldable": out of stock, and its own spec says 2.4–5 GHz |
| 5 | Sunrom 6027 electret microphone, 6 × 2.7 mm with pins, ×3 | [sunrom.com](https://www.sunrom.com/p/omnidirectional-electret-condenser-microphone-6x27mm-with-pins-6027-capacitive-sensitivity-60db) | ₹20.70 each | owned, with spares | The first one fitted gave nothing in a call: fit a spare ([docs/bring-up.md](docs/bring-up.md)) |
| 6 | Multimeter | any | ~₹250 | owned | Needed **before** soldering the battery wire to the modem board |
| 7 | Modem power switch: **SS-12F15** slide switch (owned, 4 mm knob) + 2 × M2 countersunk screws (6–8 mm) + 2 × M2 nuts | owned / any | ~₹10 | owned | Fits Alley Cat's left-side mount. Circuit in [docs/wiring.md](docs/wiring.md), section 2. The earlier two-MOSFET switch that follows the T-Deck (AO3401A + AO3400A + 2 × 100 kΩ) is documented there as an alternative, not used |
| 8 | M3 heat-set inserts (4.5 mm hole), M3 screws, M2 self-tapping screws | any | — | owned | Case closure: 2× M3×5 inserts + 2× M3×8 screws. Modem board: 4 more M3 inserts + screws. GPS patch: M2 self-tappers |

**Rough total** for items 1–7: about ₹2,100–2,200, before shipping and fasteners. The small parts below are owned too,
except the protection board (to order, above).

### Small parts named in the plan

- **1S Li-ion protection board, the 3 A two-MOSFET version:** "1S 3.7V 3A 2MOS BMS" (DW01A + two 8205A in parallel),
  about 33 × 7 × 3 mm, e.g. [Robu](https://robu.in/product/1s-3-7v-3a-2mos-bms-li-ion-18650-battery-protection-board/). The 5000 mAh cell is bare and has no protection circuit
  of its own (see [docs/wiring.md](docs/wiring.md), section 2). The two MOSFETs in parallel halve the resistance, so the
  modem's 2 A bursts drop less voltage and stay well below the overcurrent trip. The 1-MOSFET boards trip at about 3 A, and
  sooner when the battery is low. Thresholds: overcharge about 4.25 V, overdischarge about 2.3–2.5 V.

- JST PH2.0 2-pin plug for the T-Deck battery socket
- 24 AWG wire for the modem's battery feed (≤10 cm), thinner wire for the data and audio wires
- Thin foam sheet (between battery and modem board)
- Filament for the case: ASA (used; the 101 % files suit it)
- Heat-shrink tubing
- 2 × 47 µF electrolytic capacitors, 10 V or more, about 4–5 mm across: one in series with each earpiece wire
  (SIMCom's and KTRON's reference circuit)
- For the bench tests: 10 female-to-female jumper wires, 20 cm long, one per hole (one plug cut off and soldered to
  the KTRON board, the other plug on the CP2102 or the supply), and a 5 V ≥2 A phone charger with a USB
  breakout board or a cut-open USB cable

## Already owned

| Part | Used for |
|---|---|
| LilyGO T-Deck (base model, ESP32-S3FN16R8) | The phone itself |
| Full-band LTE sticker antenna, 698–960 / 1710–2690 MHz, 110 × 20 mm, U.FL plug on an 11 cm cable (came in the T-Deck's box as its LoRa antenna) | **The 4G antenna**, on U.FL1, inside the case ([docs/wiring.md](docs/wiring.md), section 6). Used for all the bench tests. LoRa gets the stubby above instead |
| CP2102 USB-serial adapter (with 3.3 V pin) | Bench tests from the Mac before the firmware exists ([docs/bring-up.md](docs/bring-up.md)) |
| Li-ion pouch cell HH 955465, 5000 mAh, 9.5 × 54 × 65 mm nominal (measured 65 × 55 × 9), bare tabs with a JST lead. No protection circuit, so it needs a protection board (above) | Powers both boards |
| Radial electrolytics: 470 µF 16 V (6–7 × 12 mm) and 100 µF 16 V (4–5 × 8 mm) | Replace the KTRON's 11 mm tall C11 and C17, laid flat, so the board fits under the battery |
| Micromax Canvas A1, salvaged: earpiece receiver (32 Ω, from the top of the phone) | Call earpiece |
| Micromax Canvas A1, salvaged: rear loudspeaker (8 Ω) and coin vibration motor | Kept for version 2 |
| Vanix Tracx-1b (Quectel EC200U-CN) | Not used in v1. No reachable audio pins. Keep for data/GPS tests or sell |

## Fallbacks

- **Earpiece:** PUI AR01532MS (DigiKey India, ₹344 + ₹1,200 delivery), or any phone "ear speaker" that reads
  25–32 Ω, or a driver cut out of a wired earphone for bench tests.
- **Microphone:** KTRON 9 × 7 mm, ₹8.75 (https://www.ktron.in/product/microphone-9x7mm-th/); Robu pack of 3,
  ₹36 (https://robu.in/?p=699586); Sunrom HM4522P-423-G, 4.5 × 2.2 mm phone mic, for a later carrier PCB.

## Version 2 (later)

| Part | Where | Price | Notes |
|---|---|---|---|
| Speakerphone, option A: SmartElex Digital Speaker Module (8002 amp + 8 Ω speaker) | Robu | ₹189 | 40 × 40 × 14 mm, 2–5.5 V |
| Speakerphone, option B: Waveshare 2030 cavity speaker (8 Ω 2 W) + PAM8403 amp board | ThinkRobotics | ₹300 + amp | Speaker 20 × 30 × 5.5 mm |
| Buck-boost regulator set to 3.9 V (optional) | — | — | Replaces the modem board's LDO (the T-Deck MAX does this with an SGM6609) |
