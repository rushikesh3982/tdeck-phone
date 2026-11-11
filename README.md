# T-Deck Phone

A working mobile phone for India (voice calls, SMS, mobile data and GPS) built around a stock
**LilyGO T-Deck**, a **SIMCom A7672S** 4G modem board and a modified 3D-printed case.

**Status (7 Nov 2026):**
- **Case:** printed and fits the T-Deck and all the parts (the files are built 1 % larger).
- **Modem, tested on the bench with a Jio SIM:**
  - registers on 4G with VoLTE;
  - makes and takes calls, with clear earpiece sound;
  - sends and receives SMS;
  - gets a GPS fix.
- **Mic:** works, clear in a call. It needed a resistor from M− to GND that the first wiring left out.
- **Firmware:** none yet.

## How it works

The T-Deck (base model: ESP32-S3FN16R8, 2.8" 320×240 screen, keyboard, trackball, SX1262 LoRa, speaker,
two microphones, battery charger) has no cellular radio. Its only free external port is the Grove UART socket.
So:

- A 4G modem board (**KTRON KSTM1548**, SIMCom A7672S) talks to the T-Deck over four wires soldered to the
  Grove socket pins.
- **Calls run on the modem itself.** An earpiece and a microphone are wired straight to the modem board.
  The T-Deck shows the dialer and SMS screens and plays the ringtone on its own speaker.
- **One battery powers both boards:** a 5000 mAh Li-ion pouch cell (65 × 55 × 9 mm), already owned. A protection board guards
  the cell, and a small slide switch on the left side turns the modem on and off.
- Everything fits inside the Alley Cat TD1 case (Printables 741124) with a re-laid-out back. The outside size
  of the case does not change.

```
                     4 soldered wires (TX, RX, 3.3 V, GND)
  LilyGO T-Deck  ─────────────────────────────────  KTRON A7672S board ──── LTE antenna (SMA, or internal sticker)
  screen, keyboard,                                   │      │      └────── GPS patch antenna
  speaker (ringtone)                               earpiece  mic
       │                                              │
       └──── 5000 mAh cell + protection board ── switch ──┘
```

## Why India needs a specific modem

Jio is 4G-only, so calls on Jio are VoLTE (voice over 4G). Airtel and Vi are shrinking their 2G networks. The
phone needs the Indian 4G bands (FDD B1/B3/B5/B8, TDD B40/B41) **and** VoLTE. The A7672S has both, plus 2G
fallback and GNSS.

## What's in this repository

| File | What it covers |
|---|---|
| [bom.md](bom.md) | Parts list: prices, where to buy, what is already owned |
| [docs/wiring.md](docs/wiring.md) | Every wire: data link, battery, earpiece, mic, antennas |
| [docs/bring-up.md](docs/bring-up.md) | First power-on checks and the modem commands |
| [docs/case.md](docs/case.md) | Which case files to print and what to change in them |
| [docs/assembly.md](docs/assembly.md) | Diagrams of every cut-out and part, and step-by-step assembly |
| [docs/decisions.md](docs/decisions.md) | Why each part was chosen and what was rejected |
| [docs/slim-layout-plan.md](docs/slim-layout-plan.md) | Brainstorm (not designed yet): three options for a slimmer phone, about 27.5 mm instead of 37 |
| [case/](case/) | The case (CC BY-SA 4.0): every file to print is in [case/stl/](case/stl/) (built 1 % larger, which fits; print at 100 % in the slicer), test pieces in [case/stl/test-prints/](case/stl/test-prints/) |

## Next steps

1. **Mic:** done. It works with a 1 kΩ resistor from M− to GND on the modem board
   ([docs/wiring.md](docs/wiring.md), section 4).
2. **Antenna:** check that the full-band sticker antenna (used for 4G in all the bench tests) still works well
   inside the closed case ([docs/wiring.md](docs/wiring.md), section 6).
3. **Phase B:**
   - Remove the 5 V bench wires.
   - Feed the modem from the battery through the protection board and the slide switch.
   - Move the data wires to the T-Deck's Grove pads ([docs/bring-up.md](docs/bring-up.md)).
4. **Slimmer case (later):** see the brainstorm in [docs/slim-layout-plan.md](docs/slim-layout-plan.md).
5. **Firmware:** a T-Deck app with dialer and SMS screens, a modem driver, ringtone, sleep with wake-on-call, and
   a low-battery guard.

## Reference documents

- A76XX AT Command Manual V1.12:
  https://eicut.com/wp-content/uploads/2025/10/A76XX_Series_AT_Command_Manual_V1.12.pdf
- A7672S Hardware Design V1.00:
  https://www.ktron.in/wp-content/uploads/2023/03/A7672S_Hardware_Design_V1.00-1.pdf
- KTRON board: product page https://www.ktron.in/product/sim-a7672s-4g-lte-2g-gnss-development-board/,
  dimension/pinout drawing https://www.ktron.in/wp-content/uploads/2024/04/4G-module-1-scaled.jpg,
  speaker/mic circuit https://www.ktron.in/wp-content/uploads/2023/03/SPK_MIC_CKT-scaled.jpg,
  Eagle library https://www.ktron.in/wp-content/uploads/2025/04/KTRON_4G-DEV_BOARD.zip
- MIC29302 regulator datasheet (pinout and reverse-current note):
  https://www.rlocman.ru/i/File/2017/11/18/MIC29150.pdf
- LilyGO T-Deck (schematic, examples): https://github.com/Xinyuan-LilyGO/T-Deck,
  product page https://lilygo.cc/products/t-deck
- Jio registration issue on the A7672S: https://github.com/Xinyuan-LilyGO/LilyGo-Modem-Series/issues/231
- Quectel EC200U AT manual (for the spare Tracx-1b board):
  https://quectel.com/content/uploads/2024/02/Quectel_EC200UEG91xUEG915G_Series-AT-Commands-Manual_V1.1.pdf

## Credits

- Case: **"Lilygo T-Deck TD1 Case" by Alley Cat**, Printables model 741124,
  https://www.printables.com/model/741124-lilygo-t-deck-td1-case, licensed
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Modified case files from this project must be
  shared under the same licence, with this credit. Alley Cat's
  cat-head logo, taken from her TD1 files, is on the front's top-edge badge as a visible credit.
- LilyGO T-Deck by LilyGO (Xinyuan-LilyGO).
- KTRON for the published board drawings, reference circuit and Eagle library.

## Licence

[MIT](LICENSE) for everything in this repository (docs, wiring, firmware when it comes) **except**:

- **Case files modified from Alley Cat's design.** These stay under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), as the original requires.
- **The rushiWorks name and logo** ([case/logo/rushi-logo.jpg](case/logo/rushi-logo.jpg), and the logo engraved on
  the case's back cover).
  These belong to Rushikesh Deshmukh. The MIT licence doesn't cover them, and CC BY-SA 4.0 doesn't license
  trademark rights, so neither licence lets anyone else use the name or logo.

By Rushikesh Deshmukh · [rushiworks](https://sites.google.com/view/rushikeshdeshmukh/rushiworks)
