# Chapter 26 — Board Bring-Up & Debugging

> **Mentor's note:** Bring-up is where you find out which of your assumptions were wrong. Go slowly,
> power things up one piece at a time, measure before you conclude, and **write everything down**.
> The bring-up log is how the next revision gets better.

---

## 26.1 Before power: inspection

1. **Visual inspection** under magnification: solder bridges, tombstones, missing parts, rotated parts (pin 1!), polarity of diodes/electrolytics.
2. **X-ray** for BGAs/QFNs if available (voids, bridges under the part).
3. **Resistance checks with the board unpowered** (multimeter, known-good-board comparison if you have one):
   - Each rail to GND: should not be a short (< 1–10 Ω is suspicious; note that big caps charge, so watch the reading climb).
   - Record the values in the bring-up log.
4. **Check the reference designator of the one part you were unsure about.**

## 26.2 First power-up (the "smoke test," done safely)

1. Use a **bench supply with current limit.** Set the voltage correctly and the current limit to ~2× the expected idle current (e.g. 50–100 mA).
2. If the board has multiple regulators with jumpers or 0 Ω isolators (DFT!), **power stages one at a time.**
3. Power on while watching the current. If it goes into current limit immediately, power off and find the short.
4. Measure each rail's voltage **at the load** (not just at the regulator).
5. Feel for hot parts (carefully), or better, use a thermal camera. A hot part at idle means something is wrong.
6. Check rail **ripple and noise** with the oscilloscope (see 26.4 for how to probe it properly).
7. Check **power sequencing** and reset timing with a multi-channel scope capture at power-on.

### Finding a short
- Inject a current (e.g. 1 A current limit at 0.5 V; low voltage protects parts) into the shorted rail, and use a **thermal camera or
  IPA on the board** (the evaporating spot marks the hot part).
- Or measure mV drops along the copper with a sensitive meter: the voltage slopes toward the short.
- Common causes: solder bridge, wrong/rotated part, a damaged MLCC (cracked caps fail short), footprint pinout errors.

## 26.3 Bring-up order
```
Power rails → clocks/oscillators (scope the crystal carefully, the probe loads it) →
reset/boot → debug interface (SWD connects? read device ID) → programming →
simple GPIO/LED blink → communication interfaces (UART console first!) →
each peripheral (I²C scan, SPI device IDs) → analog measurement chains → full system
```
Each step verifies the base the next one relies on. Don't skip ahead to the "interesting" part.

A scripted bring-up test (e.g. Python + pyserial) that exercises every peripheral and logs results is a great investment. See the
example in [`projects/02-sensor-daq-board/bringup_test.py`](../../projects/02-sensor-daq-board/bringup_test.py).

## 26.4 Measurement technique (where many "board problems" actually come from)

### Scope probing
- **Ground lead inductance:** a standard 15 cm ground clip (~150 nH) forms an LC with the probe tip capacitance (~10 pF). It resonates near
  **~130 MHz** and shows ringing that **isn't on the board**. For fast edges and ripple, **use the short ground spring** (tip-and-barrel)
  or a dedicated probe point.
- **Rail ripple measurement:** 20 MHz bandwidth limit on, AC coupling, spring ground on the output capacitor. Or use a **50 Ω coax pigtail**
  soldered across the cap into a 50 Ω scope input (with a DC block) for the lowest noise floor.
- **Probe loading:** 10× probe = 10 MΩ ∥ ~10 pF. On a high-impedance node or a crystal, that changes the circuit.
- **Differential probes** for measuring the high-side switch node or anything not ground-referenced. **Never** float the scope ground by lifting
  its mains earth (it's a safety hazard).
- **Current probes** for inrush and transients.

### Noise measurement of an analog chain
- Short the input (or use a precise input source) and record a long ADC data stream. Compute the RMS and the **noise spectral density (FFT)**.
  Spectral peaks tell you the source: 50/60 Hz (ground loop/mains), SMPS frequency, clock harmonics, USB frame rate (1 kHz).
- Compare with your noise budget (Chapter 15). The difference is your layout/interference problem.

## 26.5 Common first-spin bugs (keep this list)

| Symptom | Common cause |
|---------|--------------|
| Regulator output oscillating | Wrong output cap (ESR, DC bias derating), feedback trace picking up noise |
| MCU won't program | Wrong SWD pinout, missing pull-up on NRST, BOOT pin wrong, missing VDDA/VREF+ connection, no decoupling |
| Crystal doesn't start | Wrong load caps, wrong crystal (ESR too high for the MCU's drive), long traces, probe loading it |
| I²C doesn't work | Missing/duplicate pull-ups, SDA/SCL swapped, wrong address, level mismatch |
| USB not enumerating | D+/D− swapped, missing CC resistors (USB-C), bad 48 MHz clock accuracy, VBUS detect pin config |
| ADC reads noisy | Reference not decoupled, SMPS coupling, ground loop via USB, input RC missing |
| Part gets hot | Rotated/wrong part, back-powering through I/O, thermal design |
| Everything works on the bench, fails in the enclosure | ESD, thermal, antenna detuning, cable EMI |

## 26.6 Rework skills (you will use them)
- **Bodge wires:** 30 AWG Kynar wire (magnet wire for fine pitch), secured with Kapton tape or UV glue.
- **Cutting traces:** scalpel, two cuts and remove the copper between them. Verify with continuity.
- **Lifting a pin** of a QFP to insert a series component.
- **Hot air** for QFN/SOT/removal, with flux. Preheating the board helps on big ground planes.
- Record every rework in the bring-up log, and carry it into the next revision's schematic as a change request (ECO list).

## 26.7 The bring-up log (template)
```markdown
## Board: my-board rev A, S/N 003    Date: 2026-10-05    By: <name>
### Inspection
- [x] Visual, 2 bridges on U4 fixed
### Power
| Rail | Expected | Measured (no load) | Ripple p-p | Notes |
| 3V3  | 3.30     | 3.31               | 12 mV      | OK    |
### Issues
| ID | Symptom | Root cause | Fix on this board | Fix for rev B |
| 1  | USB not enumerating | D+/D- swapped at J3 | swapped via bodge wires | swap in schematic |
```

**Next:** [Chapter 27 — Component Selection & Supply Chain](27-component-selection-supply-chain.md)
