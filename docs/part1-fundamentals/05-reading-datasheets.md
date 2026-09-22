# Chapter 5 — Reading Datasheets Like an Engineer

> **Mentor's note:** The first page of a datasheet is marketing. The truth is in the tables, the
> footnotes, the typical-performance graphs, and the "Layout Guidelines" section. Read in the order below.

---

## 5.1 Reading order

1. **Absolute Maximum Ratings.** These are *damage* limits, not operating limits. Never design to them.
2. **Recommended Operating Conditions.** Design inside these.
3. **Electrical Characteristics table.** Note the **test conditions** column and the difference
   between *typ* and *min/max*. **Only min/max are guaranteed.** Typ is often a single-lot mean.
4. **Footnotes.** "Guaranteed by design, not production tested." "Measured with 1 µF on output."
   The important caveats usually live here.
5. **Typical performance curves.** How a parameter varies with temperature, load and frequency.
6. **Application / Typical Application circuit.** The vendor's reference design. Deviate only with a reason.
7. **Layout guidelines and example.** For regulators, clock chips, and high-speed parts, **follow them
   closely.** They came from a lab that already made the mistakes.
8. **Package drawing and recommended land pattern.** Your footprint comes from here.
9. **Errata** (separate document for MCUs/FPGAs). Read it *before* committing the design.

## 5.2 Worked example: reading an LDO datasheet (TLV755P-class, 500 mA LDO)

| What you look for | Why |
|-------------------|-----|
| Dropout voltage **at your load current and max temperature** | Vin_min − dropout must be ≥ Vout |
| Output capacitor requirements (min C, ESR range) | Some LDOs are **unstable** with low-ESR ceramics, others *require* them |
| PSRR vs. frequency | PSRR is great at 100 Hz and poor at 1 MHz. It won't clean a switcher's ripple |
| Quiescent current I_Q | Battery life |
| Thermal resistance θJA **and the test board it was measured on** | JEDEC boards are 4-layer with lots of copper; your 2-layer board will be worse |
| Enable pin threshold, internal pull-down? | Floating EN = random behavior |
| Reverse current protection | If Vout > Vin (e.g. a battery on the output), some LDOs back-feed |

**Thermal check (always do this):**
```
P = (Vin − Vout) · Iout + Vin · I_Q
Tj = Ta + P · θJA

Example: 5 V → 3.3 V at 300 mA, SOT-23-5 (θJA ≈ 200 °C/W on JEDEC board)
P = 1.7 × 0.3 = 0.51 W  →  ΔT = 102 °C  →  at Ta = 40 °C, Tj = 142 °C  → exceeds 125 °C!
```
The fix: a buck converter, a bigger package (with thermal pad plus vias), or a pre-regulator.

## 5.3 Worked example: MCU datasheet items that affect the board

- **Power pins:** each VDD pin gets its own 100 nF. Check for separate VDDA (analog) and VREF+ requirements.
- **Decoupling:** the reference manual or "hardware getting started" app note (e.g. ST AN4488-type documents)
  gives the exact scheme. Use it.
- **Boot pins / strap pins:** what level do they need at reset?
- **Clock:** crystal load capacitance C_L. Compute the load caps:
  ```
  C_load_each = 2·(C_L − C_stray)      C_stray ≈ 2–5 pF (pins + traces)
  e.g. C_L = 9 pF, C_stray = 3 pF → 2 × 6 = 12 pF each (C0G)
  ```
- **GPIO drive strength / slew-rate settings:** you can often *lower* the edge rate in firmware, which fixes EMI for free.
- **Debug interface:** SWD/JTAG pinout. Always bring it out to a standard connector (e.g. Tag-Connect or 10-pin 1.27 mm Cortex debug header).

## 5.4 The "typical" trap

A spec like "offset voltage: 50 µV typ, 500 µV max" means your production units may all be 10× worse than the
number on the front page. **Budget with max values. Use typical values only for a "likely" performance estimate.**

## 5.5 Guaranteed over what temperature?

Many specs are given at 25 °C in normal type, and over the full range in **bold** (TI's convention) or with a
"•" symbol (ADI). Check which one you're reading.

## 5.6 Maintain a design notebook

🏭 **Industry practice:** Engineers keep a *design calculations document* per board that records every
component choice with the equation and the datasheet page it came from. In reviews, the first question is
often "show me the calc." For a research lab, keep a `design-notes.md` in the project repo (template in
[`projects/templates/design-notes-template.md`](../../projects/templates/design-notes-template.md)).

## 5.7 Where to find the documents that aren't the datasheet

| Document | What's in it |
|----------|--------------|
| Reference manual (MCUs) | Register-level details, clock tree, power domains |
| Application notes | Layout, thermal, specific use cases. **Often better than textbooks** |
| Evaluation board user guide | **Schematic + layout + BOM of a known-working design. Copy it** |
| Reliability report | FIT rates, qualification |
| Errata / silicon bugs | Things that don't work as documented |
| IBIS models | Signal integrity simulation of the I/O buffers (Chapter 16) |

Eval board Altium files are frequently available from the vendor. Open them and study the layout.

## Exercises
1. Pick any buck converter (for example TPS62133 or LMR33630). Find: max switching frequency, recommended inductor, output cap
   requirement, and the layout guideline figure. Sketch the "hot loop."
2. For a crystal with C_L = 12.5 pF, compute load capacitors assuming 4 pF stray.
   *(2 × 8.5 = 17 pF → pick 18 pF.)*

**Next part:** [Part 2 — Chapter 6: What a PCB Physically Is](../part2-pcb-foundations/06-what-is-a-pcb.md)
