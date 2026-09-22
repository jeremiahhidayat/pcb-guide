# Project 3 — High-Speed USB + Buck Converter Board (4–6 layers, controlled impedance)

> Goal: apply Part 4 (Chapters 16–19). Build a board where impedance, return paths, the switching regulator
> layout, and EMC all matter, and verify them with measurements rather than hope.

## Specification

| Item | Requirement |
|------|-------------|
| Function | USB 2.0 High-Speed (480 Mbps) device that streams data from a sensor/FPGA/MCU, or a USB 2.0 HS hub with 2 downstream ports |
| Input power | 9–24 V DC barrel jack (lab supply), or USB-C PD sink (stretch) |
| Rails | 5 V @ 2 A (buck, for downstream ports), 3.3 V @ 500 mA (buck or LDO from 5 V), 1.2/1.8 V core if required by the chip |
| USB | USB-C receptacle (upstream), 90 Ω ±10% differential, ESD with < 0.5 pF/line, optional CM choke footprint |
| Clock | 24/12 MHz crystal or oscillator per the USB chip (e.g. a USB2 hub IC or an HS-capable MCU with ULPI PHY) |
| Stackup | 4 layers minimum (Sig/GND/PWR/Sig) with the fab's controlled-impedance stackup; 6 layers optional |
| EMC | Design for FCC Part 15 Class B / CISPR 32 Class B (pre-compliance scan) |

## Decisions to justify in design notes
1. **Stackup and impedance:** get your fab's controlled-impedance stackup. Enter it in the Layer Stack Manager, create a `DIFF90`
   profile, and record width/gap. Compare with `tools/pcb_calc.py diff-microstrip`.
2. **Buck converter:** Vin 9–24 V → 5 V 2 A. Compute L, C_in RMS, C_out (DC-bias!), and I_sat with `tools/pcb_calc.py buck`.
   Draw the hot loop on your placement *before* routing.
3. **Protection:** reverse polarity (P-FET or ideal diode), TVS sized for your input, hot-plug ringing (simulate `spice/05`).
4. **USB-C:** both D+/D− pin pairs on the receptacle join with short, matched stubs right at the connector. CC resistors for a sink.
5. **Diff-pair routing:** max via count, intra-pair skew budget, keep-out from other nets, reference plane continuity, ESD part placement.
6. **Clocking:** crystal load caps (Chapter 5), layout guard.
7. **EMC:** where are the cables? Where does the chassis/shield connect? Spread-spectrum on the buck? Filter on the DC input?

## Altium skills to practice
- Impedance profiles; differential pair classes and rules; `Interactive Differential Pair Routing`; diff-pair length tuning.
- xSignals through ESD parts or CM chokes.
- Return-path check rule; via stitching near diff-pair layer changes.
- Polygon pours per rail on the power layer (named, prioritized), and PDN Analyzer (if licensed) on the 5 V path.
- Draftsman fab drawing with the layer stack table and impedance notes.

## Acceptance tests

| Test | Pass criterion |
|------|----------------|
| Enumerates as High-Speed (check with `lsusb -v` / USBTreeView) | HS (480 Mbps), no errors in bulk transfer stress test (e.g. 1 GB transfer) |
| 5 V rail under 2 A step load | Within ±5%, recovers per the design; no oscillation |
| SW node ringing (scope with short ground spring) | Overshoot < 20% of Vin; no sustained ringing |
| Efficiency at 12 V in, 5 V/2 A out | Within 5% of the datasheet curve |
| Near-field scan of buck and USB cable CM current | No unexplained peaks; CM current consistent with the emission estimate (Chapter 19) |
| Thermal at full load, 40 °C ambient | T_j estimates within limits |
| TDR (if you have access to one) or fab impedance coupon report | 90 Ω ±10% |

## Stretch goals
- Add USB-PD sink controller (e.g. to request 9–20 V) and compare with the barrel-jack path.
- Build a 6-layer version with the USB pair as stripline and compare emissions.
- Measure an eye diagram with a USB compliance fixture if your lab has a fast scope.
