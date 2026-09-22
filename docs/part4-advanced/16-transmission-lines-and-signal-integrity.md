# Chapter 16 — Transmission Lines & Signal Integrity

> **Mentor's note:** Signal integrity looks like black magic until you accept one idea: **a signal is a wave
> travelling between a trace and its reference plane, and at every point it only knows the local impedance.**
> Wherever that impedance changes, part of the wave reflects. Everything else in this chapter follows from that.

👉 Interactive: [`diagrams/transmission-line.html`](../../diagrams/transmission-line.html) (reflections, termination),
[`diagrams/square-wave-harmonics.html`](../../diagrams/square-wave-harmonics.html) (why edges matter).

---

## 16.1 When is a trace a transmission line?

A signal edge has a physical length on the board:
```
edge length = t_rise × v          v = c / √ε_eff  ≈ 150–170 mm/ns on FR-4 (≈ 6–7 in/ns)

t_r = 1 ns → edge length ≈ 170 mm (microstrip, ε_eff ≈ 3)
```
If the trace is short compared with the edge (rule of thumb: one-way delay < t_r/6, i.e. **length < ~edge length/6**),
the whole trace charges up more or less at once and you can treat it as a lumped capacitor. If it's longer, different parts of
the trace are at different voltages at the same instant, and it's a transmission line.

```bash
python tools/pcb_calc.py edge --rise-time 1e-9 --er-eff 3.0
# → treat traces longer than ~29 mm as transmission lines
```
⚠️ **It's the rise time, not the clock frequency.** A 1 MHz signal from a part with 500 ps edges is a transmission line problem on a 15 mm trace.

## 16.2 🧠 Characteristic impedance from first principles

As the wavefront moves forward, it charges the capacitance of each new piece of trace. The current required is:
```
I = C_per_length × v × V        (charge per length × speed)
Z0 = V / I = 1 / (C_per_length × v) = √(L_per_length / C_per_length)
```
So **Z0 is set entirely by geometry and materials**: trace width w, height above plane h, dielectric εr, copper thickness t.
- Wider trace → more C → lower Z0
- Higher above plane → less C → higher Z0
- Higher εr → more C → lower Z0 (and slower propagation)

Common targets: **50 Ω single-ended** (RF, most digital), **90 Ω differential** (USB), **100 Ω differential** (Ethernet, PCIe 85 Ω, LVDS, MIPI, HDMI).

### Geometries

```
 Microstrip (outer layer)          Stripline (inner layer, between two planes)
   ▄▄▄▄  trace (w, t)               ════════════ plane
 ░░░░░░░░░░ dielectric (h, εr)        ▄▄▄▄
 ════════════ plane                 ════════════ plane
 - Field partly in air → ε_eff < εr   - Field fully in dielectric → ε_eff = εr
 - Faster, more radiation, more       - Slower, well shielded, less crosstalk
   susceptible to solder mask/plating  - Tighter tolerance
```
Calculator: `python tools/pcb_calc.py microstrip --width-mm 0.3 --height-mm 0.2 --er 4.1` gives ~56 Ω.
**For fabrication, always confirm with a field solver** (Altium's Layer Stack Manager impedance tab uses Simbeor's
solver) **and with the fab's stackup**, because fabs adjust widths to hit the target given their exact materials.

## 16.3 Reflections

At any impedance discontinuity, some of the incident voltage reflects:
```
Γ = (Z_L − Z_0) / (Z_L + Z_0)

Open (Z_L = ∞): Γ = +1 → reflected wave doubles the voltage at the end
Short (Z_L = 0): Γ = −1 → cancels
Matched (Z_L = Z_0): Γ = 0 → no reflection (the ideal)
CMOS input (≈ a few pF, high R): looks like an open → +100% reflection
```
**Why unterminated lines ring:** The driver (low impedance, e.g. 15 Ω) launches a wave; the CMOS load (open) reflects +100%;
back at the driver (Γ_s = (15−50)/(15+50) = −0.54) it reflects inverted, and so on. The result is overshoot, undershoot,
and ringing that can cause false clocking, exceed abs-max ratings, and radiate.

See it in [`spice/02_transmission_line_reflection.cir`](../../spice/02_transmission_line_reflection.cir).

## 16.4 Termination strategies

| Scheme | Circuit | Power | Pros / cons | Use for |
|--------|---------|-------|-------------|---------|
| **Series (source)** | R_s at driver so R_driver + R_s ≈ Z0 | None | Simple; the wave is half-amplitude on the line and doubles at the open end. **Only for point-to-point** (loads in the middle see a stair-step) | MCU/FPGA clocks, SPI, most point-to-point CMOS. **Default choice** |
| **Parallel (end)** | R = Z0 to GND/VTT at the load | High (DC) | Clean everywhere; burns power | Multi-drop buses; DDR (to VTT) |
| **Thevenin** | Two R's to VCC and GND (parallel = Z0) | High | Biases the line | Legacy buses |
| **AC (RC)** | R = Z0 in series with C to GND at the load | Low | No DC power; C ~ 3× (line delay/Z0) | Clock lines needing end termination |
| **Differential** | R = Z_diff across the pair at the receiver | Low | Standard for LVDS etc. (often on-die) | LVDS, CML |
| **On-die (ODT)** | Inside the chip | — | Programmable | DDR, SERDES, FPGAs |

**Series-termination value:** R_s = Z0 − R_out(driver). Typical CMOS drivers are 15–40 Ω, so R_s ≈ 22–33 Ω for a 50 Ω line.
Get R_out from the **IBIS model** (V-I curve) or measure it. Place R_s **as close to the driver as possible**.

## 16.5 Crosstalk

Two coupling mechanisms between an aggressor and a victim trace:
- **Capacitive (mutual C_m):** electric field coupling (dV/dt).
- **Inductive (mutual L_m):** magnetic field coupling (dI/dt).

Their sum gives:
- **Near-end crosstalk (NEXT, backward):** saturates after a coupled length ≈ (t_r × v)/2. Amplitude ≈ K_b × ΔV.
- **Far-end crosstalk (FEXT, forward):** grows with coupled length and edge rate. In **stripline** (homogeneous dielectric) the
  capacitive and inductive components cancel and FEXT ≈ 0. In **microstrip** it doesn't cancel.

**Reducing crosstalk (most effective first):**
1. **Reduce h** (trace closer to its reference plane). Coupling ∝ 1/(1 + (s/h)²).
2. **Increase spacing s** (≥ 3w, or ≥ 2–3h for critical nets).
3. **Shorten parallel run length** (affects FEXT).
4. **Route on stripline** for sensitive nets.
5. **Slow the edges** where you can (drive-strength settings).
6. Guard traces with stitching vias (for extreme cases).

## 16.6 Losses (matters above ~1 Gbps / several inches)

- **Conductor loss** grows with √f because of the **skin effect**: current crowds into a skin depth δ = √(ρ/(πfµ)), about 2 µm at 1 GHz.
  Copper **surface roughness** (foil tooth profile) adds more loss. Specify smooth copper (VLP/HVLP) for fast SERDES.
- **Dielectric loss** grows ∝ f × **Df (loss tangent)**. FR-4 Df ≈ 0.02; mid-loss ≈ 0.008–0.01; low-loss (Megtron 6, Rogers) ≈ 0.002–0.004.
- Rule of thumb: standard FR-4 loses roughly **~0.1 dB/inch/GHz** (at the Nyquist frequency), which becomes significant at multi-Gbps over long traces.
- **Fiber weave effect:** glass bundles have εr ≈ 6, resin ≈ 3. A trace that runs along a glass bundle has different Z and delay than
  its differential partner running over resin. That causes skew. Fixes: route at a slight angle (e.g. 10°) or zig-zag, or use spread-glass (1067/1086/1078) laminates.

## 16.7 Discontinuities you create without meaning to

| Discontinuity | Effect | Mitigation |
|---------------|--------|------------|
| **Via** | Capacitive/inductive bump, **stub** beyond the used layer resonates at f = c/(4·L_stub·√εr) | Back-drill, blind vias, route to the far layer so there's no stub |
| **Connector** | Impedance bump | Pick connectors specified for your data rate; follow the footprint guidelines (anti-pads, voids under pads) |
| **SMD pad of AC-coupling cap** | Pad wider than trace → low Z | **Void the reference plane under the pad** (cut-out on L2) to raise its impedance |
| **Reference plane change** | Return path interruption | Stitching vias (GND→GND) or stitching caps (PWR→GND) near the signal via |
| **Plane split / gap** | Big impedance spike + EMI | Never route across |
| **Width change / neck-down** | Local impedance change | Keep short |
| **Stubs / T-branches** | Reflections | Fly-by topology, or keep stubs < edge length/10 |

Via stub resonance example: a 1.4 mm stub in FR-4 (εr 4) resonates at c/(4 × 1.4 mm × 2) ≈ **27 GHz**. That's fine for USB 2.0, but a
3 mm stub resonates at ~12.5 GHz, which hurts at 25 Gbps.

## 16.8 Simulation: IBIS and Altium's SI tools

- **IBIS models** describe I/O buffers behaviorally (V-I, V-t curves, package parasitics). Download them from the IC vendor.
- 🛠️ **Altium Signal Integrity** (**Tools » Signal Integrity**, in the PCB): after assigning IBIS models to components (via the
  *Model Assignments* dialog), you can run reflection and crosstalk analysis on selected nets, sweep termination values, and see
  waveforms. It's a good pre-layout/post-layout sanity check for clocks and memory buses.
- **Altium Layer Stack Manager » Impedance tab:** define **Impedance Profiles** (e.g. `SE50`, `USB90`, `ETH100`). The solver
  computes widths per layer. Then in rules (**Routing » Width**, **Differential Pairs Routing**), select "Use Impedance Profile" so the router
  uses the solved widths automatically.
- For multi-gigabit channels, dedicated tools (Ansys SIwave/HFSS, Keysight ADS, Cadence Sigrity, Simbeor, HyperLynx) extract S-parameters
  of vias and channels. Altium can export to them.

## 16.9 A quick SI checklist for any digital board
- [ ] Identify nets with fast edges (clocks, SPI > 10 MHz, SDIO, Ethernet RMII, USB, DDR, camera/display interfaces).
- [ ] Put them on layers adjacent to a solid ground plane.
- [ ] Series-terminate point-to-point clock and fast signals at the driver (footprint for R_s even if you start with 0 Ω).
- [ ] Controlled impedance where the interface spec requires it (USB, Ethernet, HDMI, LVDS, RF).
- [ ] No crossing plane gaps; stitching vias at every layer change.
- [ ] Spacing ≥ 3w between clocks and everything else.
- [ ] Keep slow-edge settings in firmware where the interface allows.

## Exercises
1. A driver with 25 Ω output drives a 50 Ω, 150 mm microstrip into a CMOS input. Compute the reflection at the load and at the source.
   Choose the series termination.
2. Use `pcb_calc.py microstrip` to find the width for 50 Ω on 0.2 mm prepreg with εr 4.2. Then enter the same in Altium's Layer Stack
   Manager impedance tab and compare. Why do they differ?
3. Simulate `spice/02_transmission_line_reflection.cir` with R_s = 0, 25, 50 Ω and explain each waveform.

**Next:** [Chapter 17 — High-Speed Digital Design](17-high-speed-digital.md)
