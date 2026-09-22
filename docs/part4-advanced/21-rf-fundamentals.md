# Chapter 21 — RF Fundamentals for PCB Designers

> **Mentor's note:** Most research boards touch RF through a BLE/Wi-Fi module or an antenna. You don't
> need to be an RF engineer to get that right, but you do need to respect a few rules. And once you
> understand them, full RF design is a natural next step.

---

## 21.1 The RF mindset
- At RF, **everything is a transmission line, and every pad and via is a lumped L or C.** Geometry is the circuit.
- Everything is referenced to **50 Ω**.
- Power is in **dBm**; gains/losses in **dB** add and subtract.
- Performance is described by **S-parameters**: S11 (input reflection / return loss), S21 (insertion gain/loss), etc.

## 21.2 Using a pre-certified module (the right answer for most research boards)
Modules (e.g. ESP32-WROOM, nRF52 modules, u-blox, Laird) come with integrated antennas and **regulatory certification** (FCC/CE),
provided you follow the integration guide exactly.

**Module antenna placement rules:**
1. Antenna at the **board edge or corner**, ideally overhanging the edge.
2. **No copper on any layer** under/around the antenna area (the keep-out region from the datasheet). No ground pour, no traces, no components.
3. No metal (enclosure, battery, screws, displays) near the antenna. Plastic enclosures only near it.
4. Good ground plane on the rest of the board: the ground plane is the *other half* of many PCB antennas. Its size affects tuning.
5. Decouple the module supply per datasheet; radios draw bursty current (TX peaks of 200–500 mA for Wi-Fi). Use a sufficiently sized regulator and bulk cap.

## 21.3 Designing your own RF path (chip + antenna)

### Controlled-impedance feed: grounded coplanar waveguide (GCPW)
On a 4-layer board with L2 ground 0.1–0.2 mm below, a 50 Ω microstrip is a convenient width (~0.2–0.35 mm). Many designers
use **grounded coplanar waveguide**: the trace has ground pour on both sides (gap g) plus the plane below, with a **dense via fence**
along both sides (every ~λ/20 or tighter, e.g. 1–1.5 mm pitch at 2.4 GHz).
- Advantages: better isolation, and less dependence on the dielectric thickness.
- Altium's impedance solver supports coplanar structures (*Coplanar* option in the Impedance profile).

### Matching network
Always place a **π-network footprint** (series + two shunt pads, 0402/0201) between the radio and the antenna:
```
 RF chip ─── 50 Ω line ──┬── [series L/C/0Ω] ──┬── 50 Ω line ─── antenna
                        [shunt]              [shunt]
                         GND                   GND
```
Populate a 0 Ω series resistor initially (shunts DNP), then tune with a VNA on the real board in its enclosure. The antenna's
impedance shifts with ground plane size, the enclosure, and nearby objects, so tuning is almost always needed.

### Chip antennas and PCB trace antennas
- **Chip antennas:** follow the vendor's reference layout (ground clearance dimensions matter a lot).
- **PCB antennas** (inverted-F, meander): copy a proven reference design exactly (TI's DN007/AN043 designs for 2.4 GHz are classics),
  including substrate thickness.

## 21.4 RF layout rules

| Rule | Reason |
|------|--------|
| Keep RF traces short and straight; use curves (not sharp corners) at GHz | Minimize loss and discontinuities |
| Ground vias right next to every shunt component and RF IC ground pad | Minimize ground inductance (0.5 nH at 2.4 GHz is j7.5 Ω!) |
| Continuous ground under the entire RF path | Defined impedance |
| Void inner planes under wide RF pads (if needed to keep 50 Ω) | Pad capacitance |
| Shield cans over the RF section (with pads/vias ring) | Isolation, emissions |
| Keep digital and switching away from RF inputs | Desense: harmonics of clocks landing in your receive band reduce sensitivity |
| Crystal/TCXO for the radio: short, grounded guard | Frequency accuracy, phase noise |

## 21.5 Measuring RF
- **VNA** (NanoVNA is fine for learning, up to a few GHz) to measure S11 of the antenna and tune the matching network.
  Calibrate at the reference plane (use a pigtail with a U.FL connector and calibrate at its end).
- **Spectrum analyzer** for harmonics, spurs, TX power.
- Include a **U.FL test connector** footprint or a 0 Ω switch point in the RF path on the prototype to measure conducted power.

## 21.6 Hybrid stackups for RF
For serious RF (>6 GHz or low-loss requirements), use a Rogers RO4350B layer on top with FR-4 underneath (hybrid). Fabs do this routinely; talk to them early.

## Exercises
1. Compute the reactance of a 0.5 nH ground via at 2.4 GHz and 5.8 GHz. *(7.5 Ω, 18.2 Ω.)*
2. Design a 50 Ω GCPW in Altium on your 4-layer stackup. Compare the width with plain microstrip.
3. Read an RF module's hardware design guide (ESP32 or nRF52) and list its layout rules. Compare them with this chapter.

**Next:** [Chapter 22 — HDI, Flex, Rigid-Flex & Advanced Fabrication](22-hdi-flex-advanced-fab.md)
