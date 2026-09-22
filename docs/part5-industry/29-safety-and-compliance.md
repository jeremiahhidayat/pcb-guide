# Chapter 29 — Safety, Compliance, Creepage & Clearance

> **Mentor's note:** Most boards in this guide run on 3.3–24 V, which is inherently safe. Research
> labs, though, often end up building high-voltage drivers (piezo, electrophoresis, PMTs, electrospinning),
> mains-powered instruments, or devices that attach to humans. There the stakes change completely.
> **If a board touches mains or a person, get an experienced reviewer. No exceptions.**

---

## 29.1 Voltage classes (roughly)
- **SELV / ES1** (safety extra-low voltage): ≤ 60 V DC / 30 V AC rms in normal conditions (thresholds vary by standard). Generally touch-safe.
- **Hazardous voltage:** above that. Needs insulation, spacing, enclosures, interlocks.
- **Mains-connected:** additional requirements for isolation (basic, supplementary, reinforced), fusing, protective earth, leakage current.

## 29.2 🧠 Clearance vs. creepage
- **Clearance:** shortest distance **through air** between conductors. Governed by **breakdown of air**: impulses and peak voltage.
- **Creepage:** shortest distance **along a surface**. Governed by **surface tracking**: contamination, humidity, material CTI
  (comparative tracking index). Creepage ≥ clearance always.

```
   Conductor A  ▓▓▓        ▓▓▓  Conductor B
   ─────────────────────────────────────── board surface
                 ←creepage→ (along the surface)
   clearance = straight line through air (can be shorter if a component body or edge is in the way)
```
**Slots** milled in the board between HV and LV increase creepage (the path has to go around/over the slot) and remove the contaminated surface.

## 29.3 Functional spacing (IPC-2221B, Table 6-1, excerpt)

For *functional* (not safety) spacing between conductors. Verify against the current standard before relying on it.

| Voltage between conductors (DC or AC peak) | B1: Internal layers | B2: External, uncoated, sea level–3050 m | B4: External, with permanent polymer coating |
|---|---|---|---|
| 0–15 V | 0.05 mm | 0.1 mm | 0.05 mm |
| 16–30 V | 0.05 mm | 0.1 mm | 0.05 mm |
| 31–50 V | 0.1 mm | 0.6 mm | 0.13 mm |
| 51–100 V | 0.1 mm | 0.6 mm | 0.13 mm |
| 101–150 V | 0.2 mm | 0.6 mm | 0.4 mm |
| 151–170 V | 0.2 mm | 1.25 mm | 0.4 mm |
| 171–250 V | 0.2 mm | 1.25 mm | 0.4 mm |
| 251–300 V | 0.2 mm | 1.25 mm | 0.4 mm |
| 301–500 V | 0.25 mm | 2.5 mm | 0.8 mm |
| > 500 V | +0.0025 mm/V | +0.005 mm/V | +0.00305 mm/V |

**Safety spacing** (isolation between hazardous and user-accessible circuits) comes from product safety standards, not IPC-2221:
**IEC 61010-1** (lab/measurement/control equipment, the one most relevant for research instruments), **IEC 62368-1** (IT/AV),
and **IEC 60601-1** (medical, with the strictest patient-protection requirements). Their tables depend on working voltage, pollution degree,
overvoltage category, material group, and altitude. For 230 VAC mains, reinforced isolation typically requires **several millimeters**
(often 5–8 mm creepage). Look it up for your specific case.

## 29.4 🛠️ In Altium: enforcing HV spacing
1. Put HV nets in a net class `HV` (via a schematic Parameter Set directive, `ClassName = HV`).
2. **Design » Rules » Electrical » Clearance**: new rule, `InNetClass('HV')` vs. `All`, value from your table, priority above the default.
3. **Creepage Distance** rule (Electrical category in newer Altium versions): scope `InNetClass('HV')` vs. `InNetClass('LV')`, and set the
   surface distance. DRC then checks the path *along the surface* (accounting for slots/cutouts).
4. Add **board cutouts** (slots) under isolation barriers (optocouplers, isolators, transformers) and keep all layers clear in the barrier (keep-out region on all layers).
5. Put the barrier on the silkscreen as a dashed line and label it "ISOLATION BARRIER — NO COPPER."

## 29.5 High-voltage layout tips (hundreds of volts to kV)
- Round every copper corner (sharp points concentrate the E-field → corona). Large radii, teardrops, no sharp pad corners.
- Avoid vias in HV regions where possible. Internal layers give much better spacing (B1 column) because there's no air or contamination.
- Conformal coat (and specify a coating that's rated for the voltage).
- Use parts rated for the voltage: resistors have voltage ratings (Chapter 2), so string them in series; use HV MLCCs (safety-rated X/Y caps across isolation).
- Bleeder resistors on HV caps so they discharge when off. Label the hazard.
- **Test with a current-limited supply first**, stand clear, and follow your lab's HV safety procedure.

## 29.6 Certification landscape (so you know what exists)

| Scope | Standards |
|-------|-----------|
| Lab/measurement equipment safety | IEC/UL 61010-1 |
| Medical electrical equipment | IEC 60601-1 (+ -1-2 EMC) |
| EMC for lab equipment | IEC 61326-1 (EU), FCC Part 15 (US, as unintentional radiator) |
| Radios | FCC Part 15.247, ETSI EN 300 328 (2.4 GHz), plus RED (EU) |
| Batteries | IEC 62133, UN 38.3 (shipping lithium cells) |
| Hazardous substances | RoHS, REACH |

For research prototypes used only in your lab, formal certification usually isn't required, but **your institution's EHS office may have rules**
(especially for HV and human-subject devices, which usually need IRB review and electrical safety testing). Ask early.

**Next:** [Chapter 30 — PCB Design in a Research Lab](30-research-lab-workflow.md)
