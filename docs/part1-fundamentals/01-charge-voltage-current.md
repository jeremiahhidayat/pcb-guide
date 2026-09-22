# Chapter 1 — Charge, Voltage, Current & the Laws That Govern Them

> **Mentor's note:** You already "know" Ohm's law. This chapter asks you to *believe* a few things more
> deeply than most students do, because PCB design is where those beliefs are tested. The three that matter
> most are: **current always flows in a closed loop**, **energy lives in fields, not in wires**, and
> **every real wire has resistance, inductance and capacitance.**

---

## 1.1 The physical quantities

| Quantity | Symbol | Unit | What it *physically* is |
|----------|--------|------|------------------------|
| Charge | Q | coulomb (C) | 6.24×10¹⁸ electrons' worth of charge |
| Current | I | ampere (A) = C/s | Rate of charge flow past a point |
| Voltage | V | volt (V) = J/C | Energy per unit charge; the *difference* in potential energy between two points |
| Power | P | watt (W) = J/s | Rate of energy transfer. P = V·I |
| Resistance | R | ohm (Ω) = V/A | How much voltage it takes to push a given current |
| Capacitance | C | farad (F) = C/V | How much charge is stored per volt; energy in the **electric field** |
| Inductance | L | henry (H) = V·s/A | How much magnetic flux a current creates; energy in the **magnetic field** |

### 🧠 First principles: voltage is always *between two points*

There is no such thing as "the voltage at a node." There is only the voltage **between** that node and
some reference. When we say "the MCU pin is at 3.3 V," we silently mean "relative to the ground net."

This matters on a PCB because "ground" is not one point. It is a sheet of copper with finite resistance
and inductance. When 2 A flows through 10 mΩ of ground copper, the two ends of that copper differ by 20 mV.
A 16-bit ADC with a 2.5 V reference has an LSB of 38 µV, so to that ADC, 20 mV is a huge error.
**Chapter 12 is built entirely on this one fact.**

### 🧠 First principles: current flows in loops

Charge is conserved and doesn't pile up (except on capacitor plates, where it builds the E-field). So every
electron that leaves a source through a signal trace must come back to that source. **Every signal
has a return path.** Beginners draw the signal trace and forget about the return. Experienced engineers
design the return path *first*.

```
     Source ──────── signal trace ───────► Load
       ▲                                    │
       └────────── return path ◄────────────┘
                (usually "ground")

The loop area formed by these two paths determines:
  • inductance        (bigger loop → more L → slower edges, more ringing)
  • radiated emission (bigger loop → better antenna → fails EMC)
  • susceptibility    (bigger loop → picks up more external noise)
```

---

## 1.2 Ohm's law and power

```
V = I · R        P = V · I = I²R = V²/R
```

**Worked example (PCB relevance):** A 1 oz copper trace is 35 µm thick. How much resistance does
a 0.25 mm wide, 50 mm long trace have?

```
ρ_copper = 1.72×10⁻⁸ Ω·m  (at 20 °C; rises ~0.39 %/°C)
A = 0.25 mm × 0.035 mm = 8.75×10⁻³ mm² = 8.75×10⁻⁹ m²
R = ρ·L/A = 1.72e-8 × 0.05 / 8.75e-9 = 0.098 Ω  ≈ 0.1 Ω
```

Carry 1 A through that and you get a 98 mV drop and ~98 mW of heat. The drop is enough to push a
3.3 V rail close to a brownout threshold. This is why power traces are wide and why we use planes.

> **Rule of thumb derived from above:** 1 oz copper has a sheet resistance of about **0.5 mΩ per square**
> (ρ/t = 1.72e-8/35e-6 ≈ 0.49 mΩ). A "square" is any length×width with L = W. A trace 0.25 mm × 50 mm is
> 200 squares long → 200 × 0.49 mΩ ≈ 98 mΩ. You can now estimate any trace or plane resistance in your head.

---

## 1.3 Kirchhoff's laws

**KCL (current law):** The sum of currents into any node is zero, because charge is conserved.

**KVL (voltage law):** The sum of voltages around any closed loop is zero, because energy is conserved.
Strictly, KVL holds only when there is no changing magnetic flux through the loop. When there is,
Faraday's law adds a term: V_induced = −dΦ/dt. **That extra term is what inductive noise, crosstalk,
and ground bounce all are.** KVL is an approximation that's good until your loops are big or your
edges are fast.

```
Faraday:  ∮ E·dl = −dΦ_B/dt
          └ "KVL"   └ the part lumped-circuit theory ignores
```

This is the bridge from circuit theory to PCB physics. In a schematic, a wire is a perfect node.
On a board, a wire is a loop with an area, and changing magnetic fields induce voltage in it.

---

## 1.4 Series, parallel, and the voltage divider

```
Series:   R_total = R1 + R2 + ...
Parallel: 1/R_total = 1/R1 + 1/R2 + ...      (two resistors: R1·R2/(R1+R2))

Voltage divider:
   Vin ──[R1]──┬── Vout = Vin · R2/(R1+R2)
               [R2]
               GND
```

### Engineer thinking: the divider is never unloaded

The formula assumes nothing draws current from Vout. Connect an ADC input whose sampling capacitor
draws charge, and the divider's **Thevenin resistance** (R1‖R2) matters:

```
R_th = R1·R2/(R1+R2)
```

If R1 = R2 = 1 MΩ (chosen to "save power" on a battery-monitor divider), R_th = 500 kΩ. A SAR ADC with a
5 pF sampling cap and a 1 µs acquisition time needs R_th·C ≪ t_acq. 500 kΩ × 5 pF = 2.5 µs, so the
input never settles and your readings are wrong. **The fix is to add a 100 nF capacitor at Vout.**
It acts as a charge reservoir for the sampling cap. This is one of the most common real-world mistakes,
and it only makes sense when you think about the load.

See [`tools/tolerance_montecarlo.py`](../../tools/tolerance_montecarlo.py) for how resistor tolerance
affects divider accuracy, and the interactive [`diagrams/voltage-divider.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/voltage-divider.html).

---

## 1.5 Thevenin and Norton equivalents

Any linear network of sources and resistors, seen from two terminals, looks like **one voltage source
in series with one resistor** (Thevenin) or **one current source in parallel with one resistor** (Norton).

Why you care: this is how you reason about **source impedance** and **load impedance**, which set:
- whether a sensor's signal survives being connected to an amplifier (you want Z_load ≫ Z_source),
- how fast an output can charge a trace's capacitance (τ = R_source · C_load),
- whether a transmission line reflects (Chapter 16: you want Z_source = Z_line = Z_load).

---

## 1.6 Capacitors and inductors: time and frequency

```
Capacitor:  i = C · dv/dt      "resists changes in voltage"
Inductor:   v = L · di/dt      "resists changes in current"
```

These two equations drive a large share of PCB design:

- **Decoupling capacitors** exist because a chip's current changes fast (di/dt is large), and the
  inductance of the path from the regulator makes V = L·di/dt large. A capacitor placed *close*
  to the chip supplies the current locally, which shrinks the loop and therefore L.
- **Ground bounce**: 8 outputs switching 20 mA each in 1 ns through 1 nH of shared ground pin
  inductance gives V = 1e-9 × (0.16/1e-9) = **160 mV** of bounce on the chip's internal ground.

### RC and RL time constants

```
τ_RC = R·C          τ_RL = L/R
After 1τ: 63%   3τ: 95%   5τ: 99.3%   (7τ ≈ 0.1% → about 10-bit settling)
```

For N-bit settling you need about `N · ln(2) ≈ 0.69·N` time constants. A 16-bit ADC needs about 11τ.

### Impedance: generalizing resistance to AC

For sinusoidal signals at angular frequency ω = 2πf:

```
Z_R = R
Z_C = 1/(jωC)      magnitude 1/(2πfC)    → falls with frequency
Z_L = jωL          magnitude 2πfL        → rises with frequency
```

**Build intuition with these numbers:**

| Component | 1 kHz | 1 MHz | 100 MHz | 1 GHz |
|-----------|-------|-------|---------|-------|
| 100 nF cap | 1.6 kΩ | 1.6 Ω | 16 mΩ | 1.6 mΩ (ideal; really inductive here!) |
| 1 nH (≈1 mm of trace/via) | 6 µΩ | 6 mΩ | 0.63 Ω | 6.3 Ω |
| 10 nH (≈1 cm of wire) | 63 µΩ | 63 mΩ | 6.3 Ω | 63 Ω |

Read the 1 GHz column carefully. **A centimeter of wire has more impedance than a 50 Ω load at 1 GHz.**
This is why at high frequency, *geometry is the circuit.*

---

## 1.7 Frequency domain and why edges matter more than clock rate

A square wave is a sum of sine harmonics. Its useful spectral content extends to roughly:

```
f_knee ≈ 0.35 / t_rise     (10-90% rise time; some texts use 0.5/t_r)
```

A "slow" 10 MHz SPI clock driven by a modern MCU GPIO with 1 ns edges has spectral content out to
about **350 MHz**. **The board sees the edges, not the clock frequency.** A 1 MHz I²C bus from a
modern fast-edged part can still ring and radiate like a 300 MHz signal. Chapter 16 builds on this.

👉 Explore: [`diagrams/rc-filter.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/rc-filter.html) (interactive Bode plot) and
[`diagrams/square-wave-harmonics.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/square-wave-harmonics.html).

### Decibels

```
dB (power)   = 10·log10(P2/P1)
dB (voltage) = 20·log10(V2/V1)
−3 dB  ≈ 0.707× voltage (half power)
−20 dB = 0.1× voltage     −40 dB = 0.01×     −60 dB = 0.001×
dBm  = power relative to 1 mW     (0 dBm into 50 Ω = 0.224 V_rms)
dBµV = voltage relative to 1 µV   (EMC limits are in dBµV/m)
```

---

## 1.8 Energy in fields: the view that ties PCB design together

- Capacitor energy: **E = ½CV²**, stored in the electric field between conductors.
- Inductor energy: **E = ½LI²**, stored in the magnetic field around current.

A signal on a PCB is **an electromagnetic wave traveling in the dielectric between a trace and its
reference plane.** The copper guides the wave. Most of the energy travels in the space between the
copper layers. Once you picture that, several rules follow directly:

- Why you shouldn't route over a split plane: it breaks the waveguide.
- Why reference-plane changes need a nearby stitching via or capacitor: the wave's return has to
  cross between planes somehow.
- Why stackup (dielectric thickness, εr) sets impedance.

---

## 1.9 🛠️ Simulating this in Altium

Altium has a built-in SPICE engine (Mixed-Signal Simulation):

1. Create a new project: **File » New » Project » PCB Project**, then add a schematic.
2. Place parts from the **Simulation Generic Components** library (resistors, caps, sources).
   In Altium 21+, open **Simulate » Simulation Dashboard**.
3. Place a voltage source (VSIN or VPULSE) and set its parameters in the Properties panel.
4. In the Dashboard, add an **Analysis**: *Transient*, *AC Sweep*, or *Operating Point*.
5. Place **probes** (Simulate » Place Probe) on nets and click **Run**.

Start by simulating the RC filter in [`spice/01_rc_lowpass.cir`](../../spice/01_rc_lowpass.cir) and
confirm that the −3 dB point lands at 1/(2πRC).

---

## Exercises

1. A 3.3 V MCU drives an LED with a forward voltage of 2.0 V at 5 mA. What series resistor do you need, and what
   power rating? *(Answer: (3.3−2.0)/0.005 = 260 Ω → use 270 Ω; P = 0.005²×270 = 6.75 mW → any 0402 is fine.)*
2. A 2 oz copper plane is 100 mm × 20 mm and carries 5 A lengthwise. What is the voltage drop?
   *(Sheet R ≈ 0.25 mΩ/□, 5 squares → 1.25 mΩ → 6.25 mV.)*
3. Estimate the knee frequency of a signal with 500 ps rise time. *(0.35/0.5 ns = 700 MHz.)*
4. Why does a bigger loop area pick up more noise from a nearby switching regulator? State your answer
   using Faraday's law.

**Next:** [Chapter 2 — Passive Components: Ideal vs. Real](02-passive-components.md)
