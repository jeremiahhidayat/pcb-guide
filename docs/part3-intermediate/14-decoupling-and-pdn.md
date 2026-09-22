# Chapter 14 — Decoupling and the Power Delivery Network (PDN)

> **Mentor's note:** "Put a 100 nF on every pin" works for simple boards. To know *why* it works, and when
> it stops working, you need to treat the power delivery network as an impedance to be designed.

---

## 14.1 The problem

A digital IC draws current in sharp pulses on every clock edge. The regulator can't respond at nanosecond
speeds: its control loop bandwidth is maybe 10–100 kHz, and there's inductance between it and the chip.

```
V_droop = ΔI · Z_PDN(f)
```
Keep Z_PDN low enough across the whole frequency range where the chip's current changes, and the
rail stays within tolerance.

## 14.2 Target impedance

```
Z_target = V_rail × allowed_ripple / ΔI_transient

Example: 1.0 V FPGA core, ±3% ripple, 2 A transient → Z_target = 1.0 × 0.03 / 2 = 15 mΩ
Example: 3.3 V MCU, ±5% ripple, 100 mA transient → 1.65 Ω   (easy!)
```
The second example shows why simple MCU boards forgive casual decoupling. The first shows why FPGA and processor
boards need real PDN design.

## 14.3 🧠 Who covers which frequency band

```
|Z|
 │ regulator    bulk caps     MLCCs (0402/0201)  plane capacitance   on-die/package
 │ (DC-~50kHz)  (~10k-1MHz)   (~1-100 MHz)        (~100MHz-1GHz)      (>~100 MHz-GHz)
 │ ─────────┐
 │          └────┐                                          PCB can't help up here;
 │               └──────┐       ┌──┐                         package & die caps do it
 │                      └───────┘  └────────────────────
 │── Z_target ───────────────────────────────────────────────
 └───────────────────────────────────────────────────────────── log f
```
- **Regulator:** low impedance up to its loop bandwidth.
- **Bulk capacitors** (10–100 µF): take over from ~kHz to ~1 MHz.
- **MLCCs** (0.1–10 µF): 1–100 MHz. **Above their SRF, their mounted inductance is what counts.**
- **Plane pair capacitance:** a tight power/ground plane pair (thin dielectric) has very low inductance and covers hundreds of MHz.
- **Package and die capacitance:** above roughly 200–500 MHz the PCB mostly can't help. The IC vendor designed that part.

👉 Play with it: [`diagrams/decoupling-impedance.html`](../../diagrams/decoupling-impedance.html) and
[`tools/decoupling_plot.py`](../../tools/decoupling_plot.py).

## 14.4 🧠 Mounted inductance: why placement beats value

A capacitor's effective inductance in the circuit is the **whole current loop**: IC power pin → trace → cap → trace → via
→ ground plane → via → IC ground pin.
```
L_mounted = L_cap(ESL) + L_traces + L_vias + L_plane-spreading
Typical: ESL 0.3-0.5 nH + vias 0.5-1 nH + traces 1 nH/mm → total often 1.5-3 nH
```
**Everything that shrinks loop area lowers L:**
1. **Shortest possible trace from pad to via.** Put the via right at the pad edge, or use via-in-pad.
2. **Vias on the sides of the pad** (both vias on the same long side of the cap) give a smaller loop than vias at the ends.
3. **Two vias per pad** halve via inductance.
4. **Thin dielectric between the cap's layer and its planes:** put power/ground planes right under the top layer (L2, L3).
5. **Smaller packages**, or reverse-geometry (0204, 0306) or 3-terminal/X2Y caps for very low ESL.

```
BAD                                  GOOD
 ┌──┐                                ┌──┐
 │C │── 3 mm trace ── via            │C │● via at pad edge
 └──┘                                └──┘● (two vias)
 loop area large → ~3 nH             loop area tiny → ~0.7 nH
```

## 14.5 Anti-resonance: why mixing values can backfire

When a capacitor goes inductive (above its SRF) in parallel with another that is still capacitive, the pair forms a
**parallel LC tank**, and the impedance **peaks** (anti-resonance) between the two SRFs. With low-ESR MLCCs these
peaks can be sharp and high. If the peak lands where the IC draws current, it causes trouble.

Mitigations:
- **Use several caps of the *same* value** rather than a 100 nF + 10 nF + 1 nF "decade" ladder. Identical caps in parallel lower
  both L and ESR without creating anti-resonances between each other. (The classic 3-value ladder is mostly folklore now:
  a 1 nF 0402 has about the same ESL as a 100 nF 0402, so it adds almost nothing above the SRF.)
- **Use caps with some ESR**, or add *controlled-ESR* caps, to damp peaks.
- **Simulate** the PDN (the Python tool, LTspice, or the Altium PDN Analyzer / SIwave-class tools for big designs).

See [`spice/03_decoupling_antiresonance.cir`](../../spice/03_decoupling_antiresonance.cir).

## 14.6 Practical decoupling recipe (MCU / general digital board)

1. **One 100 nF (0402, X7R) per power pin**, placed on the same side as the IC, via right at the pad, and the IC's
   power pin trace entering through the cap if possible (pin → cap pad → via).
2. **One 1–4.7 µF per IC** (or per power domain) nearby.
3. **Bulk 10–47 µF at each regulator output** (check DC bias!) and where power enters a board region.
4. **Analog supply pins (VDDA):** ferrite bead + 1 µF + 100 nF (a π filter). Check the bead-and-cap resonance, and add damping.
5. **Follow the IC datasheet or hardware guide when it's more specific.** The IC vendor knows its package.

## 14.7 Advanced PDN (FPGAs, SoCs, DDR)
- Vendors publish **PDN design guides with calculators** (Xilinx/AMD "PDN" spreadsheets, Intel PDN tool). They give
  the target impedance and a validated capacitor list per rail.
- **Plane-pair design:** put power planes adjacent to ground with thin dielectric (≤ 0.1 mm) → high plane capacitance, low spreading inductance.
- **DC IR drop:** at 20 A on a 0.9 V rail, a 5 mV drop is already 0.5% of the rail. Do DC analysis (Altium **PDN Analyzer**).
  Watch for plane "swiss cheese" from via anti-pads under BGAs.
- **Remote sense:** regulators with a sense pair (VSENSE+/−) routed as a differential pair from the load regulate at the load, not at the regulator.

## 14.8 🛠️ In Altium
- Place decoupling caps with the IC: select the IC and its caps in the schematic, then in PCB use **Tools » Component Placement » Arrange Within Rectangle**.
- A **fanout** of power pins: **Route » Fanout » Component** can auto-fanout BGA pins to vias.
- **Rule: Power Plane Connect Style → Direct connect** for decoupling-cap vias to planes (no thermal relief on plane vias; reliefs add inductance).
  Note that vias to planes are *direct* by default in most setups. It's pads on pours that get reliefs.
- **PDN Analyzer** (Altium extension): define sources and loads, and it simulates DC voltage drop and current density on the copper.

## Exercises
1. Compute Z_target for a 1.8 V rail, 5% ripple, 500 mA step. Which cap bank would you use?
2. Using `tools/decoupling_plot.py`, compare 1×10 µF + 1×100 nF + 1×1 nF with 1×10 µF + 4×100 nF. Where are the anti-resonance peaks?
3. Estimate the mounted inductance of an 0402 cap with 2 mm traces to each via, vs. vias at the pads.

**Next:** [Chapter 15 — Mixed-Signal, Sensors & Precision Analog](15-mixed-signal-and-precision-analog.md)
