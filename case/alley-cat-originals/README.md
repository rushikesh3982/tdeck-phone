# Alley Cat's original files

Unchanged copies of the files from **"Lilygo T-Deck TD1 Case" by Alley Cat** (Printables model 741124,
https://www.printables.com/model/741124-lilygo-t-deck-td1-case) that the 18650 version is built from: the back and
front, and her three small parts. They are kept here so the case can always be made again, even if the Printables
page changes. Downloaded on 15 Nov 2026.

| File | Used for | SHA-256 |
|---|---|---|
| `Alley Chat TD1 S Inside Cat Edition.stl` | The 18650 back (`scripts/make_back_18650.py`) | `7ccd1b23dac4e0987124141f7ef33f0c2926eaa5f8b7245a0656f6c4134bfda3` |
| `Alley Chat TD1 Standard Front GPS Inserts.stl` | The 18650 front (`scripts/make_front_18650.py`); the back also reads the modem switch's slot from it | `579fb3d525b33c73ad481c501fdd0ade39b3f9b3c065b3a8bbe42c4be58153a6` |
| `Alley Chat TD1 Switch.stl` | The slider for the T-Deck's own switch | `9a8477040d3fcce9e07b39d54df979ca2cbd83cdced2654a229f3338e478fb65` |
| `Alley Chat TD1 Reset Button.stl` | The T-Deck's reset button | `9a542ad6a6ca0c3a007c594e7527a97b533f9178d72be539e38b2c3ac0eefb80` |
| `Alley Chat TD1 X Antenna Plug.stl` | The plug for an empty antenna hole (used for both holes) | `fb4f3595b54b2b3231b43dd09f92f8c9606c5a68629fd601e72551648e98ebfe` |

The small parts' print files (`alley-chat-td1-*.stl` in [../18650/stl/](../18650/stl/) and
[../x-back-5000mah/stl/](../x-back-5000mah/stl/)) are these three scaled by 1 % with `scripts/scale_stl.py`: checked
on 15 Nov 2026, they match byte for byte.

**Licence:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), Alley Cat's licence for the design.
These copies are shared under it, unchanged, with this credit. The changed parts made from them are in
[../18650/stl/](../18650/stl/), under the same licence.

The current build's X back (`Alley Chat TD1 X Back Outside Cat Edition.stl`) isn't copied here.
