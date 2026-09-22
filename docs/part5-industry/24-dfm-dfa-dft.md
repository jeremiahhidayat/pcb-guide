# Chapter 24 — DFM, DFA and DFT

> **Mentor's note:** A design that works but can't be built reliably, assembled cheaply, or tested quickly
> is not finished. "Design for X" is how professional teams make a hundred boards that all behave the same.

---

## 24.1 DFM — Design for Manufacturing (the bare board)

| Area | Guideline | Reason |
|------|-----------|--------|
| Trace/space | Stay ≥ fab's *standard* (not minimum), e.g. ≥ 0.127 mm, prefer 0.15+ | Yield |
| Annular ring | ≥ 0.13–0.15 mm | Drill wander |
| Drill sizes | Minimize the number of distinct drill sizes (each is a tool change) | Cost, time |
| Copper to board edge | ≥ 0.3–0.5 mm (planes pulled back) | Routing exposes copper → shorts, delamination |
| Solder mask webs | ≥ 0.1 mm between pads; if not possible, gang relief | Mask can't hold tiny slivers |
| Acid traps / slivers | Avoid acute angles and tiny copper slivers (Altium: *Acute Angle* and *Minimum Solder Mask Sliver* rules) | Etching defects |
| Copper balance | Similar copper density on symmetric layers | Warpage |
| Silkscreen | ≥ 0.15 mm line width, ≥ 0.8 mm text height (1.0 mm preferred), not over pads | Legibility |
| Via tenting | Tent vias unless test points | Prevents shorts and solder wicking |

**Run the fab's DFM check** (most fabs offer free online DFM on Gerber upload; Altium users can also check with tools like **Altium's
manufacturing checks**, or third-party tools such as Valor NPI at production companies).

## 24.2 DFA — Design for Assembly

| Guideline | Reason |
|-----------|--------|
| **Single-sided SMT** if possible; if double-sided, put only light passives on the bottom | Each side is a separate reflow pass. Heavy parts fall off on the 2nd pass |
| Consistent orientation of polarized parts (all diodes the same way) | AOI and human inspection |
| ≥ 0.2–0.5 mm courtyard spacing; more around tall parts and BGAs | Nozzles, inspection, rework |
| Fiducials: 3 global per board/panel + locals for fine-pitch parts | Pick-and-place accuracy |
| Avoid through-hole parts where possible; if needed, put them all on one side for wave/selective solder | Cost |
| Standard package sizes (0402 over 01005 unless needed) | Yield, cost, rework |
| Paste reduction on large pads (thermal pads 50–70%) | Floating, voiding, bridging |
| Tooling holes / panel rails (5 mm) with fiducials | Conveyors |
| Parts ≥ 3–5 mm from board edges (or add breakaway rails) | Conveyor clamps |
| Avoid parts under/near connectors' mating zone | Mechanical damage |

⚠️ **Tombstoning** in small passives comes from imbalanced heating: one pad connected to a big pour without thermal relief, or
asymmetric pad sizes. Use thermal reliefs on small passives connected to pours.

### Panelization
Small boards are delivered in panels: typically **V-score** (straight cuts, no parts overhanging) or **tab-routing with mouse bites**
(any shape). Many assemblers panelize for you. If you do it yourself, Altium has **Embedded Board Arrays** (Place » Embedded Board Array/Panelize)
which reference your PCB document, so the panel updates when the board changes.

## 24.3 DFT — Design for Test

Every board should be testable without heroic effort:
1. **Test points** on every power rail, key signals, clocks, reset, and interfaces. Size ≥ 1 mm (0.9 mm min for flying probe), ≥ 2.54 mm spacing
   for bed-of-nails fixtures, all on one side (usually bottom) for production testing.
2. **Debug/programming access:** SWD/JTAG header or a Tag-Connect footprint (no-connector cable, great for production).
3. **Isolation points:** 0 Ω resistors or solder jumpers between power stages and loads, so each stage can be tested separately
   and you can measure current by inserting a meter.
4. **Current-sense options:** a footprint for a shunt resistor in each rail (0 Ω until needed).
5. **LEDs** for power good and heartbeat. Cheap, and they save hours.
6. **Boundary scan (JTAG IEEE 1149.1)** for BGA-heavy boards: tests connectivity without physical probes.
7. **Production test firmware** plus a test fixture (pogo pins) for anything built in quantity.

🛠️ **Altium:** set pads to be *Testpoint* (pad properties → Testpoint: Fabrication/Assembly, top/bottom), then use **Testpoint Manager**
(Tools » Testpoint Manager) and the **Testpoint Style/Usage** rules. Outputs include a **Test Point Report** for fixture builders.

## 24.4 Assembly drawing and fab drawing
Created with **Draftsman** (File » New » Draftsman Document):
- **Fab drawing:** board outline with dimensions, drill table (Place » Drill Table), layer stack table, impedance table, fab notes
  (material, Tg, finish, thickness, copper, IPC class, mask color, silkscreen color, impedance control, tolerances).
- **Assembly drawing:** component outlines and designators (from the assembly mechanical layers), polarity marks, special notes (DNP parts,
  conformal coating areas, torque, labels).

Example fab notes (adapt them):
```
1. MATERIAL: FR-4, Tg ≥ 170 °C, IPC-4101/126 or equivalent, RoHS compliant.
2. FINISHED THICKNESS: 1.60 mm ±10% over copper.
3. COPPER: 1 oz finished on all layers (outer layers 1 oz base + plating).
4. SURFACE FINISH: ENIG per IPC-4552.
5. SOLDER MASK: LPI, green, both sides. SILKSCREEN: white, both sides.
6. FABRICATE AND INSPECT TO IPC-6012 CLASS 2, IPC-A-600 CLASS 2.
7. CONTROLLED IMPEDANCE: see impedance table. Tolerance ±10%. Fab may adjust trace widths to meet impedance.
8. VIAS: tented both sides unless noted. Minimum finished hole size 0.25 mm.
9. ELECTRICAL TEST: 100% netlist test required (IPC-D-356 netlist provided).
10. BOARD OUTLINE: tolerance ±0.15 mm.
```

## 24.5 IPC classes
- **Class 1:** general consumer (toys).
- **Class 2:** dedicated service (most commercial products, lab instruments). **Default.**
- **Class 3:** high reliability (medical life-support, aerospace, military). Stricter annular ring, plating thickness, inspection; costs more.

**Next:** [Chapter 25 — Manufacturing Outputs & Fab Release](25-manufacturing-outputs.md)
