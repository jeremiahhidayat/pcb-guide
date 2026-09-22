# Chapter 4 — Op-Amps and Analog Building Blocks

> **Mentor's note:** Most research instruments are, at their core, a sensor → amplifier → filter → ADC
> chain. If you can design that chain with a known noise and error budget, you can build very capable
> lab hardware.

---

## 4.1 The ideal op-amp and the two golden rules

With negative feedback:
1. **No current flows into the inputs.**
2. **The output does whatever it takes to make V+ = V−.**

These two rules let you analyze most op-amp circuits in your head.

### Core topologies

```
Non-inverting:  Vout = Vin · (1 + Rf/Rg)          Zin ≈ ∞
Inverting:      Vout = −Vin · (Rf/Rin)             Zin = Rin
Buffer:         Vout = Vin                          Zin ≈ ∞, Zout ≈ 0
Difference:     Vout = (V2 − V1)·(Rf/Rin)          (matched ratios needed for CMRR)
Transimpedance: Vout = −Iin · Rf                   (photodiodes, electrochemistry)
Integrator:     Vout = −(1/RC)∫Vin dt
```

## 4.2 The real op-amp: specs that break designs

| Spec | Meaning | Error it causes |
|------|---------|-----------------|
| **V_OS** (input offset voltage) | Inputs aren't exactly equal | Output DC error = V_OS × noise gain |
| **I_B** (input bias current) | Inputs draw some current | I_B × R_source → error. Critical for high-Z sensors (pH, photodiodes). Use CMOS/JFET (pA-fA) |
| **GBW** (gain-bandwidth product) | Closed-loop BW ≈ GBW / noise gain | Gain of 100 on a 1 MHz GBW op-amp → 10 kHz bandwidth |
| **Slew rate** | Max dV/dt at output | Full-power BW = SR/(2π·V_peak) |
| **e_n, i_n** | Voltage and current noise density | Noise floor (see 4.4) |
| **Input/output range** | "Rail-to-rail" or not | Clipping near rails; inputs outside CM range can **phase-reverse** in some parts |
| **CMRR, PSRR** | Rejection of common-mode signal and supply noise | Supply ripple leaks into output |
| **Capacitive load stability** | Phase margin with C_L | Op-amp driving a cable or ADC input can **oscillate** |

### ⚠️ Gotcha: driving capacitive loads
The op-amp's output resistance plus a capacitive load adds a pole inside the feedback loop. Phase margin
disappears and the circuit oscillates. **The standard fix** is a small isolation resistor (10–100 Ω) in
series with the output, outside the feedback loop, or feedback taken from after it (with care). The same
applies to the RC filter in front of an ADC (4.5).

---

## 4.3 Noise gain vs. signal gain

**Noise gain** = 1 + Rf/Rg for *both* the inverting and non-inverting configuration. Op-amp V_OS and e_n
are amplified by noise gain, not signal gain. An inverting amplifier with gain −1 has a noise gain of 2.

---

## 4.4 🧠 Noise analysis from first principles

Uncorrelated noise sources add as root-sum-of-squares:

```
e_total = √(e₁² + e₂² + e₃² + ...)
```

For a non-inverting amp with source resistance R_s, input-referred noise density is:
```
e_in² = e_n² + (i_n · R_s)² + 4kT·R_s + 4kT·(Rf‖Rg)  [+ (i_n·(Rf‖Rg))²]
Output noise (V rms) = e_in · NoiseGain · √(ENBW)
ENBW for a single-pole filter = (π/2)·f_c ≈ 1.57·f_c
```

**Worked example:** OPA320-class op-amp (e_n ≈ 7 nV/√Hz), R_s = 1 kΩ (4 nV/√Hz), gain 100 with Rf = 99 kΩ,
Rg = 1 kΩ (Rf‖Rg ≈ 990 Ω → 4 nV/√Hz), bandwidth 10 kHz.
```
e_in = √(7² + 4² + 4²) ≈ 9.0 nV/√Hz
ENBW = 1.57 × 10 kHz = 15.7 kHz  → √ENBW = 125
Output noise = 9.0 nV × 100 × 125 ≈ 113 µV rms   (≈ 0.75 mV p-p, using 6.6× rms)
```
If your ADC's LSB is 76 µV (16-bit, 5 V), noise covers about 1.5 LSB rms. This is how you pick op-amps,
resistor values and filter bandwidths *before* touching Altium. Code:
[`tools/pcb_calc.py noise`](../../tools/pcb_calc.py).

**1/f (flicker) noise:** below the "corner frequency," noise density rises as 1/√f. For DC-precise
measurements (strain gauges, thermocouples), use **zero-drift (chopper/auto-zero)** amplifiers, which
have no 1/f noise.

---

## 4.5 Driving an ADC: the most common analog interface on research boards

```
          ┌──────┐   R_filt        ┌──────┐
 signal ──┤ amp  ├───[ 10-50Ω ]───┬┤ ADC  │
          └──────┘                 │└──────┘
                                C_filt (C0G, ~1-10 nF, ≥ 20× C_sample)
                                   │
                                  GND (ADC's ground, short path)
```
🧠 **Why this RC exists:** at the start of acquisition, the ADC's internal sampling capacitor connects to the input
and demands a step of charge. C_filt supplies that charge instantly (a "charge bucket"), and R_filt isolates
the op-amp from the capacitive load so it stays stable. The datasheet usually recommends values. **Use them.**
C_filt must be C0G. An X7R's voltage coefficient adds distortion.

### Anti-aliasing
The sampling theorem says content above f_s/2 folds back into your band. The RC above is one pole
(−20 dB/decade). For demanding measurements, either use a steeper active filter (Sallen-Key,
multiple-feedback), or oversample with a sigma-delta ADC and filter digitally.

---

## 4.6 Instrumentation amplifiers (INAs)

For small differential signals on a common-mode voltage (bridge sensors, thermocouples, biopotentials):
```
 V+ ──┐
      ├── INA (gain set by one resistor R_G) ── Vout = G·(V+ − V−) + V_REF
 V− ──┘
```
- High CMRR (80–120 dB), high input impedance on both inputs.
- **R_G tempco directly sets gain drift.** Use a low-TC thin-film resistor.
- **Check the input common-mode range against output swing.** INAs have a "diamond plot"
  (e.g. TI's "INA CMV calculator") that limits the combination of common-mode and output voltage.
  Many designs fail here.
- The **REF pin** must be driven by a low impedance (buffer it). A resistive divider on REF breaks CMRR.

---

## 4.7 Voltage references

The ADC can only be as accurate as its reference.

| Spec | Typical good value |
|------|--------------------|
| Initial accuracy | 0.05–0.1% |
| Tempco | 2–10 ppm/°C |
| Noise (0.1–10 Hz) | 1–5 µVpp |
| Long-term drift | ppm/1000h |
| Thermal hysteresis | ppm after temperature cycling |

Layout: the reference output needs its datasheet-specified capacitor (sometimes 10 µF!) placed right at the pin,
and **PCB stress affects precision references**. Keep them away from board-mount holes and flex points,
and consider a slot around them (Chapter 15).

---

## 4.8 Comparators ≠ op-amps
Don't use an op-amp as a comparator unless the datasheet explicitly allows it. They're slow to recover from
saturation and some have input clamp diodes. Real comparators need **hysteresis** (positive feedback) to avoid
chattering on slow or noisy inputs:
```
Hysteresis band ≈ V_out_swing · R1/(R1 + R2)    (R2 from output to +input, R1 from input source)
```

---

## 4.9 🛠️ In Altium: simulate before layout

1. Use op-amp models from the vendor (TI, ADI provide PSpice/SPICE `.lib` files). In Altium, add the model via
   **Component Properties » Models » Add » Simulation**, choose *Subcircuit*, and point to the `.lib`/`.ckt` file.
2. Run **AC Sweep** for gain/phase. For stability, use a loop-gain test (break the loop with a big L and inject via a big C,
   or use the built-in Transfer Function analysis if available in your version).
3. Run **Noise analysis** in the Simulation Dashboard and compare with your hand calculation. If they differ,
   find out why. That's where the learning is.

Vendor tools are worth knowing too: TI's **TINA-TI**, ADI's **LTspice** (the de-facto standard, with good switching regulator models),
TI's **Analog Engineer's Calculator**, and ADI's **Precision Studio / Filter Wizard**.

---

## Exercises
1. You need a gain of 1000 at 1 kHz bandwidth. What minimum GBW is required? Would you use one stage or two? Why?
2. A photodiode produces 10 nA at max light. Design a TIA to produce 1 V. Compute the feedback resistor, its noise,
   and the feedback capacitor for 100 Hz bandwidth.
   *(Rf = 100 MΩ; Cf = 1/(2π·100 MΩ·100 Hz) ≈ 16 pF.)*
3. Why must the INA REF pin be driven from low impedance? Draw the internal difference amplifier and see.

**Next:** [Chapter 5 — Reading Datasheets Like an Engineer](05-reading-datasheets.md)
