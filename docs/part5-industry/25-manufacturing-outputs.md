# Chapter 25 — Manufacturing Outputs & Fab Release

> **Mentor's note:** The fab and the assembler never see your Altium file. They see only the outputs. An error
> in the outputs is an error in the product. Treat generating and checking outputs as a formal step, not
> something you do at 5 pm on Friday.

---

## 25.1 What goes in a release package

```
releases/rev-A/
├── fab/
│   ├── gerbers/  (Gerber X2 or RS-274X: every copper, mask, paste, silk, outline layer)
│   ├── drill/    (NC Drill Excellon: plated + non-plated, drill map)
│   ├── (or) ODB++ / IPC-2581 package — single intelligent file, preferred by many fabs
│   ├── IPC-D-356 netlist (for electrical test)
│   └── Fab drawing PDF (outline, stackup, impedance table, fab notes, drill table)
├── assembly/
│   ├── BOM (xlsx/csv: designators, qty, MPN, manufacturer, description, DNP flag, alternates)
│   ├── Pick-and-place / centroid (designator, X, Y, rotation, side)
│   ├── Assembly drawing PDF (top/bottom)
│   └── Paste layers (for stencil) — included in Gerbers
├── docs/
│   ├── Schematic PDF
│   ├── 3D STEP of the assembled board
│   └── Release notes (what changed vs. previous rev)
└── source/  (zip of the Altium project at release, or a git tag reference)
```

## 25.2 🛠️ Generating outputs with an OutJob

Create/open `my-board.OutJob`:
1. **Fabrication Outputs:**
   - *Gerber X2 Files* (preferred, carries layer function metadata) or *Gerber Files* → Configure: units mm, format 4:6 (or 2:5 inch),
     select *used layers*, include board outline (mechanical outline layer). Include **Mechanical layers** used for outline and dimensions.
   - *NC Drill Files* → Excellon, same units/format as Gerbers, separate plated/non-plated, and *Generate board edge rout paths* if the fab wants it.
   - *ODB++ Files* or *IPC-2581 Files* (select the whole design).
   - *Test Point Report* / *IPC-D-356A Netlist*.
2. **Assembly Outputs:** *Generates pick and place files* (units mm, CSV), *Assembly Drawings* (or Draftsman).
3. **Report Outputs:** *Bill of Materials* (from the BomDoc, with template) and *Design Rule Check* (as a **validation output**).
4. **Documentation Outputs:** *Schematic Prints* (PDF), *PCB 3D Print*, *Draftsman*.
5. **Export Outputs:** *Export STEP*.
6. **Output Containers:** *PDF* (combine all documentation into one PDF) and *Folder Structure* (fab/, assembly/, docs/), pointing at `releases/rev-X/`.
7. Add **Validation Outputs** *Design Rules Check* and *Electrical Rules Check* so that **Generate** fails if either has errors.

Then: **Run all** (or *Generate Content* per container).

🏭 **Industry practice with Altium 365 / Workspace:** use **Project Releaser** (Project » Project Releaser). It runs the OutJob
against a *clean snapshot* of a committed revision, validates it, and releases immutable data to the workspace with a revision
ID. Git users can emulate this by tagging the commit and generating outputs only from a clean checkout of that tag.

## 25.3 Check your outputs independently

**Never order a board without viewing the Gerbers in a different tool than the one that made them.**
- Altium CAMtastic (File » New » CAM Document, then import) or **free viewers**: Gerbv, tracespace.io, KiCad's Gerber viewer, or the fab's own online viewer.
- Checklist:
  - [ ] Every layer present, correct order, correctly named (the fab will ask about unlabeled files).
  - [ ] Board outline closed, correct dimensions.
  - [ ] Drill file aligned with pads (overlay them). Plated vs. non-plated correct (mounting holes!).
  - [ ] Solder mask openings on all pads, none on tented vias.
  - [ ] Paste layer: no paste on test points, fiducials, or through-hole pads; thermal pad windowed.
  - [ ] Silkscreen not on pads; readable; polarity marks visible.
  - [ ] Inner planes: correct net, correct thermals/anti-pads, no unexpected islands.
  - [ ] PnP: rotation and origin sanity. Assembler preview tools (JLC/PCBWay) show parts over pads; **check rotation of every polarized part and IC.**
  - [ ] BOM: every line has an MPN, stock available, DNP marked, quantities match the designator count.

## 25.4 Ordering

| Option | Good for |
|--------|----------|
| Bare boards (JLCPCB, PCBWay, OSH Park, Eurocircuits, Aisler) + hand assembly | Simple boards, 1–5 units, learning |
| **Turnkey assembly** at a prototype house (JLCPCB/PCBWay assembly, MacroFab, Seeed, local assemblers) | Fine-pitch, QFN/BGA, 5–100 units. Cheap and fast now |
| Consigned assembly (you supply parts) | Special parts, lab-sourced sensors |
| Stencil + reflow in the lab (hot plate / reflow oven) | Iteration speed, moderate complexity |

**Always order a stencil** if you assemble SMT yourself (framed or frameless, 0.1–0.12 mm thick for fine pitch).

## 25.5 Revision control on the physical board
- Put **board name + revision + date** in copper (not only silkscreen). Copper survives, and ink can be omitted by a fab.
- Put the **git hash or release ID** in silkscreen for traceability (Altium special strings: `.PCB_File_Name`, `.Print_Date`, or project parameters such as `.Revision`).
- Keep the released outputs **frozen**. Never regenerate "the same" revision later from modified files.

**Next:** [Chapter 26 — Board Bring-Up & Debugging](26-bring-up-and-debug.md)
