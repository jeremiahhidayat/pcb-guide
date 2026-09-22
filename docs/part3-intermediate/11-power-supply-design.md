# Chapter 11 — Power Supply Design

> **Mentor's note:** Most "mysterious" board problems are power problems: noise, brownouts, oscillation,
> heat. Design the power tree first and most carefully. Everything else sits on top of it.

---

## 11.1 The power tree

Draw it before choosing any parts:
```
 USB-C 5V ──► [eFuse/PTC + TVS] ──► 5V_SYS
                                      ├──► Buck (TPS62xxx) ──► 3V3_D  (MCU, digital, 300 mA)
                                      │                          └──► LDO (low-noise) ──► 3V3_A (ADC/AFE, 20 mA)
                                      ├──► LDO ──► 2V5_REF? (use a real reference instead)
                                      └──► Charge pump / inverting ──► −2.5V (bipolar op-amps)
```
For every node: voltage, max current, tolerance, allowed ripple/noise, sequencing needs.

## 11.2 Linear regulators (LDOs)

🧠 **How they work:** A pass transistor acts as a variable resistor, controlled by an error amplifier
that compares the output (via a divider) to an internal reference. The difference in voltage is **burned as heat**.
```
Efficiency ≈ Vout / Vin      (5 V → 3.3 V: 66%;  12 V → 3.3 V: 27%!)
P_loss = (Vin − Vout) · Iout
```
**Use an LDO when:** low current, small Vin−Vout, low noise needed, or as a post-regulator after a switcher.

### Key LDO specs

| Spec | Why it matters |
|------|----------------|
| Dropout | Minimum Vin − Vout for regulation (at max load, max temp) |
| PSRR vs. frequency | Ability to reject input ripple. Usually 60–80 dB at 1 kHz, **20–40 dB at 1 MHz** |
| Output noise (µV rms, 10 Hz–100 kHz) | Low-noise LDOs (e.g. LT3045, TPS7A20/TPS7A47, ADM7150) reach ~1–5 µV rms |
| Stability requirements | Min output C, ESR window |

### Setting output voltage (adjustable LDO or buck)
```
Vout = Vref · (1 + R_top / R_bot)
Choose R_bot so divider current ≫ feedback pin leakage (≥ 10–50 µA typical), e.g. Vref = 0.8 V, Vout = 3.3 V:
R_bot = 20 kΩ → R_top = 20k × (3.3/0.8 − 1) = 62.5 kΩ → pick 62 kΩ (E96: 61.9k) → Vout = 3.276 V (check tolerance)
```
The repo tool searches standard values and reports the resulting error: `python tools/pcb_calc.py divider --vref 0.8 --vout 3.3`.
It finds 35.7k/11.5k → 3.284 V (0.5%). 🧠 Why can't E96 hit 3.300 V exactly? E96 values are spaced
geometrically (10^(1/96) ≈ 2.4% apart), so *ratios* of E96 values are quantized the same way. If you need better,
use a series pair for one resistor, or accept the error: it's usually smaller than the regulator's
own Vref tolerance (often ±1%), which dominates anyway.

## 11.3 Switching regulators: the buck converter

🧠 **First principles:** Instead of burning excess voltage, a buck *chops* the input with a switch and
averages it with an LC filter. An ideal switch dissipates no power (it's either fully on, V≈0, or fully off, I=0),
so efficiency can be 85–95%.

```
            SW node
 VIN ──[High FET]──┬──⌇⌇ L ⌇⌇──┬── VOUT
                   │           │
              [Low FET]      C_out
                   │           │
                  GND         GND

Duty cycle:        D = Vout / Vin
Inductor ripple:   ΔI_L = (Vin − Vout) · D / (L · f_sw)       → choose ΔI_L ≈ 20–40% of I_out
Output ripple:     ΔV ≈ ΔI_L / (8 · f_sw · C_out) + ΔI_L · ESR
Input RMS current: I_in,rms ≈ I_out · √(D(1−D))             → max at D = 0.5: I_out/2
```

**Worked example:** 12 V → 3.3 V, 2 A, f_sw = 1 MHz.
```
D = 0.275
Pick ΔI_L = 30% × 2 A = 0.6 A → L = (12 − 3.3) × 0.275 / (0.6 × 1e6) = 3.99 µH → 4.7 µH
Actual ΔI_L = 8.7 × 0.275 / (4.7e-6 × 1e6) = 0.51 A
I_peak = 2 + 0.255 = 2.26 A → inductor I_sat ≥ ~2.8 A (margin + current-limit consideration: I_sat should exceed the IC's current limit ideally)
C_out = 22 µF (effective after DC bias!) → ΔV ≈ 0.51 / (8 × 1e6 × 22e-6) = 2.9 mV + ESR term
C_in RMS current = 2 × √(0.275 × 0.725) = 0.89 A → ceramic caps rated for this
```
Run: `python tools/pcb_calc.py buck --vin 12 --vout 3.3 --iout 2 --fsw 1e6 --ripple-pct 30`

### 🧠 The hot loop: the single most important buck layout concept

There are two current loops in a buck:
- **Loop 1 (high-side FET on):** C_in → high FET → L → C_out → back to C_in (via ground)
- **Loop 2 (low-side FET on):** low FET → L → C_out → back to the low FET

The current in the **inductor and output cap** is *continuous* in both states. The current that **switches abruptly** (a
square wave with ns edges) flows only in the loop **C_in → high FET → low FET → C_in**. This is the **hot loop**.
Its di/dt is huge, so its inductance produces voltage spikes (V = L·di/dt) and its area radiates magnetic field.

**Layout rules that follow from this:**
1. **Place C_in (a small 100 nF–1 µF ceramic, plus the bulk) as close as physically possible to VIN and PGND pins.**
   This is the #1 rule, more important than anything else in the buck layout.
2. Keep the **SW node copper small**: it's a large dv/dt node (0 → Vin in ns) that capacitively couples to everything
   nearby. Just large enough to carry the current.
3. Keep the **feedback trace away from SW and L**, and take the feedback from the output cap (the regulation point), routed as a quiet trace.
4. **Solid ground plane directly under the hot loop** (layer 2). This minimizes loop area because return current flows
   directly underneath.
5. Put the inductor close to SW, and the output cap ground close to the input cap ground.

👉 Interactive: [`diagrams/buck-hot-loop.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/buck-hot-loop.html) compares good and bad layouts.

### Other topologies

| Topology | Converts | Notes |
|----------|----------|-------|
| **Boost** | Vout > Vin | The hot loop is on the *output* side (low FET → diode/high FET → C_out) |
| **Buck-boost / 4-switch** | Vin above or below Vout | Batteries (Li-ion 3.0–4.2 V → 3.3 V) |
| **Inverting buck-boost** | Negative rail | For −5 V op-amp rails |
| **Charge pump** | ±Vin, 2×Vin at low current | No inductor. Good for small negative rails (<50 mA) |
| **Flyback** | Isolated | Isolated sensors, safety barriers |
| **Isolated DC-DC module** | Isolated | The easy answer for isolated rails (e.g. for EEG/biopotential safety or ground-loop breaking) |

### Buck modules vs. discrete
For a research lab, **power modules** (inductor integrated, e.g. TI TPSM/LMZM, Murata, RECOM) remove most layout risk.
The input cap still has to be close.

## 11.4 Getting low noise from a switching supply

Options, from cheapest to best:
1. **Higher f_sw** (1–2 MHz): ripple is easier to filter, but switching noise moves closer to RF bands.
2. **Spread-spectrum (dithered) f_sw**: spreads EMI peaks (helps EMC), but spreads noise in your band too. Know your signal band.
3. **Second-stage LC filter** (ferrite/inductor + cap) with damping. Can knock ripple down by 20–40 dB.
4. **Post-regulate with a low-noise, high-PSRR-at-f_sw LDO** (e.g. LT3045 keeps ~70+ dB PSRR up to 1 MHz). Leave 0.3–1 V headroom.
5. **Synchronize f_sw to your ADC's sample clock** (a harmonic lands in a known place, or gets rejected by the digital filter).
6. **Silent Switcher-type regulators** (ADI) with split, symmetric hot loops that cancel their magnetic fields.

## 11.5 Protection and power-entry circuits

| Problem | Solution |
|---------|----------|
| Reverse polarity | P-FET (Chapter 3) or ideal diode controller |
| Overcurrent | PTC, **eFuse** (e.g. TPS259xx): adjustable limit, OVP, reverse blocking, soft start |
| Hot-plug inrush | eFuse / soft-start / NTC. **Big bulk caps + a long cable = inductive ringing up to 2× Vin at plug-in!** Add a TVS and some bulk electrolytic (its ESR damps the LC) |
| Brown-out | Supervisor/reset IC or MCU BOR config |
| Load dump (automotive) | TVS + OVP controller per ISO 7637/16750 |

⚠️ **Gotcha: hot-plugging ceramic-only inputs.** Cable inductance (~1 µH/m) and a 10 µF ceramic form a high-Q LC. At plug-in
the voltage rings to nearly twice Vin. A 24 V supply briefly reaches ~45 V and destroys a 40 V-rated regulator.
Fix: add a damping electrolytic (the ESR provides damping) or a TVS.

## 11.6 Sequencing, enable, and power-good
- Some ICs (FPGAs, ADCs with separate AVDD/DVDD, processors) require **rails in a specific order** or within timing windows.
  Chain `PGOOD` of regulator N to `EN` of regulator N+1, or use a sequencer IC.
- **No signal pin may be driven while its IC is unpowered.** Current flows through the ESD diodes into the unpowered rail
  ("back-powering" or "phantom powering"). Classic bug: a UART from a powered MCU backpowers an unpowered sensor.

## 11.7 🛠️ In Altium: power-related tools
- **Net classes** for power nets → width rules → polygons.
- **PDN Analyzer** (Altium extension, license-dependent): DC IR-drop analysis on planes and pours. It shows current
  density and voltage drop maps, so you can find neck-downs where a plane is cut by via fields.
- **Polygon Pour Manager** (**Tools » Polygon Pours » Polygon Manager**): name polygons (e.g. `3V3_PWR_L1`), set pour order (priority).
- Mark hot-loop components with a **Room** or a **Union** so they move together.

## Exercises
1. Design a 24 V → 5 V, 1 A buck at 500 kHz: compute L, C_out, C_in RMS current. Choose real parts.
2. For the design in 1, sketch the hot loop and the placement. Where does the input cap go?
3. Your 3.3 V sensor rail needs < 10 µV rms noise. Sketch the power chain from a 5 V USB input.
4. Simulate the hot-plug ringing in [`spice/05_hotplug_ringing.cir`](../../spice/05_hotplug_ringing.cir) with and without a damping electrolytic.

**Next:** [Chapter 12 — Grounding and Return Paths](12-grounding-and-return-paths.md)
