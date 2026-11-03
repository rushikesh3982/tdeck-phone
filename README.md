# T-Deck Phone

A working mobile phone for India (voice calls, SMS, mobile data and GPS) built around a stock
**LilyGO T-Deck**, a **SIMCom A7672S** 4G modem board and a modified 3D-printed case.

**Status (2 Nov 2026):** the design is settled. Parts are not ordered yet, nothing is built yet, and there is
no firmware yet.

## How it works

The T-Deck (base model: ESP32-S3FN16R8, 2.8" 320×240 screen, keyboard, trackball, SX1262 LoRa, speaker,
two microphones, battery charger) has no cellular radio. Its only free external port is the Grove UART socket.
So:

- A 4G modem board (**KTRON KSTM1548**, SIMCom A7672S) talks to the T-Deck over four wires soldered to the
  Grove socket pins.
- **Calls run on the modem itself.** An earpiece and a microphone are wired straight to the modem board.
  The T-Deck shows the dialer and SMS screens and plays the ringtone on its own speaker.
- **One battery powers both boards:** a 1700 mAh cell salvaged from a Micromax Canvas A1. The T-Deck's own power
  switch turns the modem on and off too, through a small MOSFET switch.
- Everything fits inside the Alley Cat TD1 case (Printables 741124) with a re-laid-out back. The outside size
  of the case does not change.

```
                     4 soldered wires (TX, RX, 3.3 V, GND)
  LilyGO T-Deck  ─────────────────────────────────  KTRON A7672S board ──── LTE antenna (SMA)
  screen, keyboard,                                   │      │      └────── GPS patch antenna
  speaker (ringtone)                               earpiece  mic
       │                                              │
       └─────────── 1700 mAh cell ──── MOSFET ────────┘
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
| [case/](case/) | Modified case files to print (CC BY-SA 4.0), starting with the front |

## Next steps

1. Order the KTRON board, GPS patch, antenna cable and mics. Buy a multimeter. Choose the LTE antenna.
2. When the parts arrive, run the bench checks in [docs/bring-up.md](docs/bring-up.md) from the Mac through the
   USB-serial adapter, including a VoLTE test call inside the seller's return window.
3. Case: the front (earpiece grille, mic pocket) and the back (modem standoffs, SIM slit, GPS patch cradle) are done
   in [case/](case/). Print both and dry-fit. The KTRON's two tall capacitors get swapped for flat ones first.
4. Firmware: a T-Deck app with dialer and SMS screens, a modem driver, ringtone, sleep with wake-on-call,
   and a low-battery guard.

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
