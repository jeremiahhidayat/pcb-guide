# Chapter 2 — Passive Components: Ideal vs. Real

> **Mentor's note:** A schematic symbol is a promise that the part behaves ideally. The real part doesn't.
> Most of the skill in board design comes down to knowing *where* and *when* each part stops behaving
> like its symbol.

---

## 2.1 Resistors

### Ideal
V = IR, for all frequencies, temperatures and voltages.

### Real
```
         L_parasitic (≈0.4-1 nH for 0402/0603)
   ○───[ R ]───⌇⌇⌇───○
      │                │
      └──── C_p ───────┘   (≈0.05-0.2 pF across the body)
```

| Parameter | What it means | Where it bites you |
|-----------|---------------|--------------------|
| **Tolerance** (1%, 0.1%) | Initial value accuracy | Dividers, gain-setting, references |
| **TCR** (ppm/°C) | Drift with temperature | Precision analog: 100 ppm/°C × 50 °C = 0.5% |
| **Power rating** | Max continuous dissipation (usually derate to 50%) | Current sense, pull-ups on high voltage |
| **Voltage rating** | Max voltage across the part (often 50 V for 0402!) | HV dividers: string several in series |
| **Noise** | Thermal (Johnson) noise always; thick-film adds excess (1/f) noise | Low-noise front ends: use thin-film |
| **Pulse handling** | Surge energy capability | Inrush limiting, ESD protection series R |

### 🧠 First principles: thermal noise

Every resistor at temperature T generates noise voltage because its electrons jiggle thermally:

```
v_n = √(4·k·T·R·B)
k = 1.38×10⁻²³ J/K, T in kelvin, B = bandwidth in Hz

1 kΩ at 300 K:   √(4 × 1.38e-23 × 300 × 1000) = 4.07 nV/√Hz
Scaling: noise ∝ √R  → 100 kΩ = 40.7 nV/√Hz, 10 MΩ = 407 nV/√Hz
```

**Implication:** In a low-noise amplifier, a 100 kΩ feedback network can contribute more noise than
the op-amp itself. Lowering resistor values reduces noise but costs power and loads the output.
That trade-off shows up in almost every analog design.

### Package sizes (imperial code → metric)

| Imperial | Metric | Size (mm) | Typical power | Notes |
|----------|--------|-----------|---------------|-------|
| 0201 | 0603M | 0.6×0.3 | 50 mW | Phones; painful to hand-rework |
| 0402 | 1005M | 1.0×0.5 | 63 mW | Default for dense digital |
| 0603 | 1608M | 1.6×0.8 | 100 mW | **Best for prototypes you hand-solder** |
| 0805 | 2012M | 2.0×1.25 | 125 mW | Easy hand solder |
| 1206 | 3216M | 3.2×1.6 | 250 mW | Higher voltage (200 V) and power |
| 2512 | 6332M | 6.3×3.2 | 1-2 W | Current sense shunts |

⚠️ **Gotcha:** "0603" means different sizes in imperial and metric. Altium's IPC Compliant Footprint
Wizard uses metric codes in its naming (e.g. `RESC1608X55N`). Always check the dimensions.

---

## 2.2 Capacitors

### Real capacitor model

```
   ○───[ESR]───⌇⌇ESL⌇⌇───||C||───○
```

- **ESR** (equivalent series resistance): losses. Sets the minimum impedance and damps resonance.
- **ESL** (equivalent series inductance): set by the package *and the mounting* (pads + vias + planes).
  Typically 0.3–1 nH for small MLCCs *before* mounting inductance, and often 1–2 nH once mounted.

Impedance magnitude:

```
|Z| = √(ESR² + (2πf·ESL − 1/(2πf·C))²)

Self-resonant frequency: f_SRF = 1 / (2π√(ESL·C))
Below SRF → capacitive.  At SRF → |Z| = ESR (minimum).  Above SRF → inductive.
```

**Worked example:** 100 nF 0402 MLCC, ESL = 0.5 nH, ESR = 20 mΩ.
```
f_SRF = 1/(2π√(0.5e-9 × 100e-9)) = 1/(2π × 7.07e-9) ≈ 22.5 MHz
At 200 MHz: |Z| ≈ 2π × 200e6 × 0.5e-9 = 0.63 Ω   ← it's an inductor now
```

Above ~20 MHz, a 100 nF cap behaves like a 0.5 nH inductor, and so does a 10 nF cap in the same
package. **In the inductive region, ESL (package + mounting) decides everything; the capacitance value
barely matters.** Chapter 14 builds a whole methodology on this. Try it in
[`diagrams/decoupling-impedance.html`](../../diagrams/decoupling-impedance.html).

### Dielectric types (the most under-appreciated datasheet section)

| Class | Code | Stability | Use |
|-------|------|-----------|-----|
| Class 1 | **C0G / NP0** | ±30 ppm/°C, **no DC bias effect**, low loss | Filters, timing, oscillator load caps, precision |
| Class 2 | **X7R**, X5R | ±15% over temp, **loses capacitance with DC bias** | Decoupling, bulk |
| Class 2 | Y5V, Z5U | −82% over temp | Avoid |

### ⚠️ Gotcha: DC-bias derating of ceramic capacitors

A 10 µF, 6.3 V, 0402 X5R capacitor biased at 5 V may only give you **~2 µF**. Ferroelectric
(Class 2) dielectrics lose permittivity under a DC field. Smaller packages and lower voltage ratings
make it worse.

**How to handle it:**
- Use the manufacturer's tool (Murata SimSurfing, TDK SEAT, KEMET K-SIM, Samsung) to get the bias curve.
- Choose a higher voltage rating or a bigger package for the same nominal C.
- **Switching regulator output caps are where this breaks designs.** The loop was stabilized for
  22 µF and you really have 8 µF, so the regulator oscillates.

### Other capacitor types

| Type | Strengths | Weaknesses |
|------|-----------|------------|
| Aluminum electrolytic | Huge C, cheap | High ESR, dries out (lifetime ∝ 2^((T_rated−T)/10)), polarized |
| Polymer (Al or tantalum) | Low ESR, stable, no DC bias loss | Cost, leakage |
| Tantalum (MnO₂) | Stable C | **Can fail short and burn.** Derate voltage 50%. Needs inrush-limited supplies |
| Film (PP, PET) | Very low loss, low distortion, self-healing | Big |

### Piezoelectric effect ("singing capacitors")
Class 2 MLCCs are piezoelectric. Audio-frequency ripple (for example from a regulator in pulse-skip mode)
makes them audibly buzz. It works the other way too: mechanical vibration produces voltage noise, which
matters in sensitive analog paths. **Use C0G or film in the signal path of precision or audio circuits.**

---

## 2.3 Inductors and ferrite beads

### Inductor
```
   ○───[DCR]───⌇⌇ L ⌇⌇───○
            └──C_winding──┘   (sets SRF; above it, the inductor looks capacitive)
```

| Parameter | Meaning |
|-----------|---------|
| **L** | Inductance at zero (or specified) current |
| **DCR** | Winding resistance → I²R loss |
| **I_sat** | Current where L drops (typically by 20–30%) because the core saturates. **Exceed it and a buck converter's current runs away.** |
| **I_rms / I_temp** | Current for a given temperature rise (thermal limit) |
| **Shielded vs. unshielded** | Unshielded inductors radiate magnetic field. Near sensitive analog, **always use shielded** |

### Ferrite bead: *not* an inductor

A ferrite bead is **resistive** in its useful band. It turns HF noise energy into heat instead of
storing and returning it. Its datasheet gives impedance vs. frequency (often "600 Ω @ 100 MHz").

⚠️ **Gotchas:**
1. Beads lose impedance under DC current, often 50–90% at rated current. Check the Z vs. I_DC curve.
2. A bead plus a decoupling cap forms an **LC low-pass filter that can resonate** at low frequency
   (where the bead is inductive) and *amplify* noise. Add damping (a series R or a lossy bulk cap)
   and simulate it. See [`spice/04_ferrite_lc_resonance.cir`](../../spice/04_ferrite_lc_resonance.cir).
3. Don't put beads in the ground path "to isolate grounds." It usually makes things worse (Chapter 12).

---

## 2.4 The PCB itself is a passive component

Every feature of the board has parasitics. You'll use these numbers all the time:

| Feature | Approximate parasitic |
|---------|-----------------------|
| Trace inductance (no plane underneath) | ~1 nH/mm (≈ 25 nH/in). Can be much less over a close plane |
| Via, 1.6 mm board, 0.3 mm drill | ~1.2 nH (see [`tools/pcb_calc.py via`](../../tools/pcb_calc.py)) |
| Pad-to-plane capacitance | ~0.1–1 pF |
| Trace capacitance over plane (50 Ω line) | ~1 pF/cm on FR-4 (≈ 2.9 pF/in for 50 Ω microstrip) |
| Parallel planes, 0.1 mm apart, εr = 4.3 | ~38 pF/cm² (C = ε₀εr·A/d) |

🧠 **Derivation of plane capacitance:** C = ε₀·εr·A/d = 8.854e-12 × 4.3 × 1e-4 m² / 0.1e-3 m = 38 pF per cm².
A 100 cm² board with a 0.1 mm power–ground spacing gives about 3.8 nF of nearly ideal, very-low-inductance
capacitance. That's why tight power–ground spacing in a stackup matters (Chapter 18).

---

## 2.5 Choosing passives: a senior engineer's defaults

| Situation | Default choice | Why |
|-----------|----------------|-----|
| General digital pull-up | 10 kΩ 1% 0402 | Balances rise time against power |
| I²C pull-up | Compute from bus capacitance: R_max = t_r / (0.8473·C_bus) | Spec-driven (t_r = 1000 ns std, 300 ns fast mode) |
| Local decoupling | 100 nF X7R 0402 (+1 µF nearby) | Small package → low ESL |
| Bulk at regulator | 10–47 µF X5R/X7R 0805/1206 (check bias!) or polymer | Low-frequency energy storage |
| Filter / timing / oscillator load | C0G | Stable, no bias or piezo effects |
| Precision gain resistors | 0.1% thin film, ≤25 ppm/°C, matched networks when ratios matter | Accuracy and drift |
| Current sense | 1% metal-element shunt, 4-terminal (Kelvin) footprint | Accuracy |
| Near sensitive analog | Shielded inductors, C0G caps | Avoid radiated/piezo noise |

🏭 **Industry practice:** Companies keep an **approved parts list** of maybe 30 resistor values and 15 capacitor
values, all from preferred series (E24/E96) and a few packages. That cuts BOM line count, reel changes
at the assembler, and cost. Do this in your lab too: pick 0402 or 0603 and standardize.

### E-series values
- E6: 1.0, 1.5, 2.2, 3.3, 4.7, 6.8 (±20%)
- E12: adds 1.2, 1.8, 2.7, 3.9, 5.6, 8.2 (±10%)
- E24 (±5%), E96 (±1%): pick from these; the tools script can snap values to them.

---

## 2.6 🛠️ In Altium: modeling passives

- Put **parametric data** on every component: Value, Tolerance, Voltage, Dielectric, Package, Manufacturer
  and MPN. In Altium, use **Manufacturer Part Search** (panel) or your company's **database library**
  (DbLib) so that each schematic part links to a real, orderable MPN.
- To simulate, attach a SPICE model to the component (Properties » Models » Add » Simulation). For real
  caps, many manufacturers provide SPICE models that include ESR and ESL. Murata's include DC-bias
  behavior.

---

## Exercises

1. Compute the SRF of a 1 µF 0603 cap with 0.7 nH ESL. *(≈ 6 MHz.)*
2. You need a divider from 48 V down to 3 V for an ADC. The 0402 resistor is rated 50 V. Is one
   resistor on top OK? What about the power? Choose values.
3. Why do we derate tantalum capacitors to 50% of rated voltage? Research the failure mode.
4. Compute the thermal noise of a 10 MΩ photodiode feedback resistor over a 1 kHz bandwidth.
   *(407 nV/√Hz × √1000 ≈ 12.9 µV rms.)*

**Next:** [Chapter 3 — Semiconductors](03-semiconductors.md)
