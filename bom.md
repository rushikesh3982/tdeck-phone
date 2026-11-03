# Bill of materials

Prices are in rupees and include GST unless noted. Status as of 2 Nov 2026.

## To buy for version 1

| # | Part | Where | Price | Status | Notes |
|---|---|---|---|---|---|
| 1 | KTRON KSTM1548: SIMCom A7672S 4G + GNSS development board | [ktron.in](https://www.ktron.in/product/sim-a7672s-4g-lte-2g-gnss-development-board/) | ₹1,530 | to order | In stock. 54.33 × 57.23 mm, 28 g |
| 2 | KTRON GPS active patch antenna KSTA1417 | [ktron.in](https://www.ktron.in/product/gps-antenna-with-ufl-female-connector/) | ₹105 | to order | 25 × 25 × ~8 mm, 4 corner holes, short u.FL lead |
| 3 | KTRON IPX → SMA female antenna cable, 10 cm | [ktron.in](https://www.ktron.in/product/rf-cable-ipx-to-sma-female-10cm-length/) | ≈₹44 | to order 10 cm for the top-right corner (recommended). The 15 cm version ([KSTA0380](https://www.ktron.in/product/rf-cable-ipx-to-sma-female/), ₹42) if the 4G antenna goes top-left. Comes with nut and washers |
| 4 | LTE antenna, SMA male, **rated 700–2700 MHz** | any | ~₹100–200 | to choose | **Not** the KTRON "4G LTE 3.5 dBi foldable": out of stock, and its own spec says 2.4–5 GHz |
| 5 | Sunrom 6027 electret microphone, 6 × 2.7 mm with pins, ×3 | [sunrom.com](https://www.sunrom.com/p/omnidirectional-electret-condenser-microphone-6x27mm-with-pins-6027-capacitive-sensitivity-60db) | ₹20.70 each | to order | Order 3 (spares) |
| 6 | Multimeter | any | ~₹250 | to buy | Needed **before** soldering the battery wire to the modem board |
| 7 | AO3401A P-MOSFET + AO3400A N-MOSFET (both SOT-23) + 2× 100 kΩ resistors | any | ~₹20 | v1 | Modem power switch: the modem follows the T-Deck's own switch, circuit in [docs/wiring.md](docs/wiring.md). Prefer AO3401**A** (the older AO3401 is weaker at low battery) |
| 8 | M3 heat-set inserts (4.5 mm hole), M3 screws, M2 self-tapping screws | any | — | case stage | Case closure: 2× M3×5 inserts + 2× M3×8 screws. Modem board: 4 more M3 inserts + screws. GPS patch: M2 self-tappers |

**Rough total** for items 1–7: about ₹2,100–2,200, before shipping and fasteners.

### Small parts named in the plan

- JST PH2.0 2-pin plug for the T-Deck battery socket
- 24 AWG wire for the modem's battery feed (≤10 cm), thinner wire for the data and audio wires
- Thin foam sheet (between battery and modem board)
- PLA+ or PETG filament for the case
- SOT-23 adapter board (optional, makes the MOSFET easier to solder) and heat-shrink tubing
- For the bench tests: about 10 female-to-female jumper wires (cut in half; the cut end is soldered to the KTRON
  board, the plug end goes on the CP2102), and a 5 V ≥2 A phone charger with a USB
  breakout board or a cut-open USB cable

## Already owned

| Part | Used for |
|---|---|
| LilyGO T-Deck (base model, ESP32-S3FN16R8) | The phone itself |
| CP2102 USB-serial adapter (with 3.3 V pin) | Bench tests from the Mac before the firmware exists ([docs/bring-up.md](docs/bring-up.md)) |
| Micromax Canvas A1 (AQ4502), salvaged: 1700 mAh battery, 65 × 55 × 9 mm | Powers both boards |
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
