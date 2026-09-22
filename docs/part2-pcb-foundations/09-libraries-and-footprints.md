# Chapter 9 — Libraries, Symbols & Footprints

> **Mentor's note:** A wrong footprint is the most common reason a first board is scrap. Build every
> part as if a mistake costs $2,000 and three weeks, because on a real project it does.

---

## 9.1 What a "component" is in Altium

```
Component (the thing on the BOM)
 ├── Symbol           (SchLib) – pins with numbers & names, graphics
 ├── Footprint(s)     (PcbLib) – pads, silkscreen, courtyard, assembly outline, 3D body
 ├── Parameters       – Value, Manufacturer, MPN, Description, Datasheet URL, Tolerance, Voltage...
 ├── Models           – SPICE simulation model, IBIS model, 3D STEP
 └── Pin mapping      – symbol pin designator ↔ footprint pad designator
```

## 9.2 Where to get parts (and how much to trust them)

| Source | Trust level | Notes |
|--------|-------------|-------|
| Your own, built from datasheet | ✔✔✔ (once reviewed) | The gold standard |
| Altium **Manufacturer Part Search** / Altium Content Vault | ✔✔ | Generally good. **Verify the pad geometry against the datasheet** |
| Ultra Librarian / SnapEDA / SamacSys (Component Search Engine) | ✔ | Convenient. Always review. Errors do happen |
| Random GitHub libraries | ⚠️ | Review everything |

🏭 **Industry practice:** No part enters the company library until a second person checks it against
the datasheet ("library review"). Record who created and who checked it (parameters `Author`, `Checker`).

## 9.3 Building a symbol (SchLib)

1. **File » New » Library » Schematic Library**. **Tools » New Component**.
2. Place pins (`P`, `P`). Set **Designator** (the pad number) and **Name** (function).
3. Electrical types: Input, Output, I/O, Power, Passive, Open Collector, HiZ. These drive ERC, so set them honestly.
4. Grouping conventions: power at top, ground at bottom, inputs left, outputs right, related pins together.
   Don't mirror the physical pin order unless the part is a connector.
5. Multi-part symbols: big ICs (FPGA, MCU) get split into parts (Part A: power, Part B: port A, ...).
   Op-amp duals get parts A, B plus a separate power part.
6. Pin length 200 or 300 mil, **on a 100 mil grid.** Pin ends must fall on grid points.
7. Parameters: add `Manufacturer`, `Manufacturer Part Number`, `Description`, `Datasheet` (URL), and for passives
   `Value`, `Tolerance`, `Voltage`, `Package`.

## 9.4 Building a footprint (PcbLib) — the right way

### Use IPC-7351 and the IPC Compliant Footprint Wizard
**Tools » IPC Compliant Footprint Wizard** (in PcbLib). Enter the package dimensions **from the datasheet
package drawing** (min/max tolerances), and Altium computes pad sizes using IPC-7351 solder fillet goals:

| Density level | Toe/heel/side fillets | Use |
|---------------|------------------------|-----|
| **Most (A)** | Largest pads | Hand soldering, rugged |
| **Nominal (B)** | Standard | **Default for most boards** |
| **Least (C)** | Smallest pads | High density |

🧠 **Why fillet goals matter:** Solder wets the pad and climbs the component terminal. The *toe* fillet (outside)
is the visible joint that inspectors (and AOI) check; the *heel* gives mechanical strength. Too little pad
gives a weak joint; too much pad can lead to **tombstoning**: uneven wetting forces lift one end of a small passive
upright during reflow.

### Or: follow the datasheet's recommended land pattern
Many ICs (especially QFN, DFN, BGA, modules) come with a **recommended land pattern**. For these, use it over
IPC calculation, because it reflects the vendor's reliability testing.

### Footprint elements checklist

| Element | Layer | Rule |
|---------|-------|------|
| Pads | Top Layer (+auto mask and paste) | Correct numbering matching the symbol |
| Pin 1 marker | Silkscreen + Assembly | Unambiguous, visible after placement |
| Silkscreen outline | Top Overlay | **Not over pads**, ~0.15 mm line width, visible after placement |
| Courtyard | Mech (Courtyard type) | Component body + pads + ~0.25 mm margin. Used for placement clearance |
| Assembly outline | Mech (Assembly type) | Body outline + designator string `.Designator` for assembly drawings |
| 3D body | Mech (3D Body type) | STEP model from vendor or Altium's *Place » 3D Body* extruded/generic |
| Origin | — | **Center of the component** (IPC-7351). The pick-and-place file uses it |
| Rotation | — | IPC-7351 zero-orientation: pin 1 top-left for ICs, pin 1 left for 2-pin parts |

### Exposed pads (QFN thermal pads)
- The pad is often large. If paste covers it 100%, the part **floats** on solder and the peripheral pins open.
- **Split the paste** into a grid of windows covering **50–70%** of the pad area.
  In Altium: set the pad's paste mask expansion to cover nothing, then draw paste rectangles on Top Paste manually.
  Or use a pad stack with custom paste shapes.
- Thermal vias in the pad: 0.3 mm drill at 1.0–1.2 mm pitch. Use **filled/capped vias** or **tented from the
  bottom** so solder doesn't wick away (see Chapter 20).

## 9.5 Special footprint types

| Type | Technique |
|------|-----------|
| **Net tie** | A footprint with two pads joined by copper (component type **Net Tie**). Joins two nets deliberately, e.g. AGND to GND at one point, or Kelvin connections to a shunt |
| **Kelvin (4-wire) shunt** | Footprint with 4 pads or 2 pads + net ties so the sense lines connect at the inner edge of the pads |
| **Test point** | SMD pad 1–1.5 mm, or a through-hole loop. Set the component type to *Standard (No BOM)* for pads-only test points |
| **Fiducial** | 1 mm copper circle, 2–3 mm mask opening, component type *Standard (No BOM)* |
| **Mounting hole** | Pad with hole, plated or not, *Mechanical* component type |
| **Logo / graphics** | Import via **Scripts » PCB Logo Creator** (or in newer versions the image import in the PCB editor) |

## 9.6 Verifying footprints (do *all* of these)

1. **Print 1:1** on paper and set the real part on it. (Yes, really. It catches mm-vs-mil and scale errors.)
2. **Compare pin mapping** symbol ↔ footprint, especially for SOT-23 transistors (pinouts vary between vendors!),
   connectors, and anything with an exposed pad.
3. **Check the 3D view** (`3` key): does the STEP model sit right-side-up with pin 1 on pad 1?
4. **Run Tools » Footprint Reports / Component Rule Check** in the PcbLib.
5. For connectors: **check the mating side**. A board-to-board connector pair is a classic place for mirrored pinouts.

⚠️ **Gotcha: SOT-23 pinouts.** The "same" SOT-23 MOSFET from two vendors can have G/S/D in different positions.
Never swap an MPN without re-checking pin mapping.

## 9.7 Managed parameters: making the BOM accurate

Every placed part must resolve to one orderable **MPN**. Generic "10k 0402" is fine if your BOM lists approved
alternates. In ActiveBOM (`.BomDoc`), add **Manufacturer Part Search** results as preferred and alternate parts,
and it will show lifecycle and stock for each.

## Exercises
1. Build a symbol + footprint + 3D model for an SOIC-8 op-amp (e.g. OPA2376) using the IPC Wizard. Verify pin 1, print 1:1.
2. Build a QFN-20 with exposed pad, including a 2×2 paste window array covering 60%.
3. Build a 4-terminal Kelvin shunt footprint for a 2512 resistor.

**Next:** [Chapter 10 — Your First Board: End-to-End](10-first-board-walkthrough.md)
