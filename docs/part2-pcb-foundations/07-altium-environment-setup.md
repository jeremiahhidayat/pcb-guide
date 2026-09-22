# Chapter 7 — Setting Up Altium Designer Properly

> **Mentor's note:** An hour of setup saves a hundred hours later. Juniors skip it and fight the tool on
> every board. A consistent environment (templates, libraries, rules, output jobs) is what lets a
> senior engineer turn out a clean board in a week.

---

## 7.1 The Altium design flow (big picture)

```
 Requirements ─► Block diagram ─► Schematic (.SchDoc) ─► Compile / ERC ─► ECO: Update PCB
                                        ▲                                       │
                                        │  (back-annotate)                      ▼
 Libraries (.SchLib/.PcbLib or DbLib/Workspace) ─────────────►  PCB (.PcbDoc)
                                                              Stackup → Rules → Placement → Routing
                                                                                 │
                                                                                 ▼
                                               DRC ─► Outputs (.OutJob): Gerber/ODB++, drill,
                                                       pick-place, BOM (.BomDoc), drawings (Draftsman)
```
See [`diagrams/altium-design-flow.html`](../../diagrams/altium-design-flow.html).

## 7.2 Project anatomy

| File | Purpose |
|------|---------|
| `*.PrjPcb` | Project file: which documents belong to it, project options (ERC matrix, class generation, variants) |
| `*.SchDoc` | Schematic sheets (use several, organized hierarchically) |
| `*.PcbDoc` | The board layout |
| `*.SchLib` / `*.PcbLib` | Symbol / footprint libraries |
| `*.IntLib` | Compiled integrated library (read-only) |
| `*.DbLib` / `*.DbLink` | Database library: symbols + footprints + parameters driven from a database/Excel |
| `*.BomDoc` | ActiveBOM: the managed BOM with supply chain data |
| `*.OutJob` | Output Job: a saved recipe for all fabrication and assembly outputs |
| `*.PCBDwf` | Draftsman drawing (fab and assembly drawings) |
| `*.Harness`, `*.PrjMbd` | Harness / multi-board projects |

### Recommended repository layout (per board)
```
my-board/
├── hardware/
│   ├── my-board.PrjPcb
│   ├── sheets/            00_TopLevel.SchDoc, 01_Power.SchDoc, 02_MCU.SchDoc, 03_AFE.SchDoc ...
│   ├── my-board.PcbDoc
│   ├── my-board.BomDoc
│   ├── my-board.OutJob
│   └── drawings/          Fab.PCBDwf, Assembly.PCBDwf
├── libraries/             (or reference a shared lab library repo as a git submodule)
├── docs/
│   ├── design-notes.md    ← calculations, decisions, datasheet references
│   └── bringup-log.md
├── releases/
│   └── rev-A/             frozen outputs: gerbers.zip, BOM.xlsx, PnP, PDFs, STEP
└── firmware-test/         bring-up test scripts
```

Use the provided [`.gitignore`](../../.gitignore). Altium generates `History/`, `__Previews/`,
`Project Logs for */` and `Project Outputs for */`, and those shouldn't be committed.

## 7.3 Preferences to change on day one

Open **Tools » Preferences** (or the gear icon at top-right).

| Location | Setting | Recommended | Why |
|----------|---------|-------------|-----|
| System » General | Reload last workspace | On | Convenience |
| System » Backup | Auto-save every 10–15 min, keep 5 | On | Crashes happen |
| Schematic » General | *Auto-increment*: Primary 1 | Default | Placing multiple pins |
| Schematic » Compiler | Show errors/warnings inline | On | Catch ERC issues visually |
| Schematic » Grids | Grid 100 mil (imperial) | **Always keep schematic on a 100 mil or 50 mil grid** | Off-grid pins = unconnected nets that *look* connected |
| PCB Editor » General | Online DRC | **On** | Real-time rule violations |
| PCB Editor » Interactive Routing | Routing Conflict Resolution: *Walkaround* or *Push*; enable *Automatically Terminate Routing*, *Automatically Remove Loops* | On | Cleaner routing |
| PCB Editor » Interactive Routing » Interactive Routing Width Sources | Pickup track width from existing routes; Track width mode: **Rule Preferred** | Rule-driven | Width comes from rules, not ad hoc |
| PCB Editor » Defaults | Set default via, track, polygon | Match your rules | |
| PCB Editor » Board Insight Display | Show net names on tracks and pads | On | Readability |
| Data Management » Installed Libraries | Add your lab library | | |

## 7.4 Build your templates

### Schematic template (sheet border + title block)
1. **File » New » Schematic**. In the Properties panel (with nothing selected) set **Sheet size** A3 or B.
2. Add a title block with **special strings** that fill in automatically:
   `=Title`, `=DocumentNumber`, `=Revision`, `=DrawnBy`, `=Date`, `=SheetNumber`, `=SheetTotal`, `=ProjectName`.
3. Save as a template `.SchDot`. Point **Preferences » Schematic » General » Template** at it, or use
   **Project Options » Parameters** to define project-wide parameters (Revision, Author) that every sheet shows.

### PCB template
Create a `.PcbDoc` with:
- Layer stack for your common stackups (2L, 4L) with the fab's dielectric data.
- **Mechanical layer definitions** (as in Chapter 6).
- **Design rules** preset for your fab ([see 7.5](#75-design-rules-your-fab-class-preset)).
- Standard classes (Power nets, DiffPairs).
- Default **fiducials, mounting holes, and board-info text** (a special string such as `.Layer_Name` on each copper
  layer lets you verify layer order on the physical board).

Also save your rules separately: in **Design » Rules** right-click » **Export Rules** → a `.rul` file you can import into any board.

## 7.5 Design rules: your "fab class" preset

Open **Design » Rules** (shortcut `D`, `R`). Rules are **query-scoped** and **priority-ordered**:
the most specific matching rule with the highest priority wins. Start with a baseline for a standard prototype fab:

| Rule category | Rule | Scope | Value (conservative prototype) |
|---------------|------|-------|--------------------------------|
| Electrical | Clearance | All–All | 0.15 mm (6 mil) |
| Electrical | Clearance (HV) | `InNetClass('HV')` – All | per Chapter 29 |
| Electrical | Short-Circuit | All | Not allowed |
| Electrical | Un-Routed Net | All | Check |
| Routing | Width | All | min 0.15 / pref 0.2 / max 3 mm |
| Routing | Width (Power) | `InNetClass('PWR')` | min 0.3 / pref 0.5 / max 5 mm |
| Routing | Routing Via Style | All | 0.3 mm drill / 0.6 mm dia |
| Routing | Differential Pairs Routing | `InDifferentialPairClass('USB')` | width/gap from impedance calc |
| Plane | Power Plane Connect Style | All | Relief connect, 4 spokes, 0.25 mm width, 0.25 mm air gap |
| Plane | Polygon Connect Style | All | Relief 0.25 mm × 4 (or Direct for power FETs/thermal pads, with a specific rule) |
| Plane | Power Plane Clearance | All | 0.25 mm |
| Mask | Solder Mask Expansion | All | 0.05 mm (2 mil), or per fab |
| Mask | Paste Mask Expansion | All | 0 (set per footprint where needed) |
| Manufacturing | Minimum Annular Ring | All | 0.13 mm |
| Manufacturing | Hole Size | All | 0.2–6.3 mm |
| Manufacturing | Hole To Hole Clearance | All | 0.25 mm |
| Manufacturing | Minimum Solder Mask Sliver | All | 0.1 mm |
| Manufacturing | Silk To Solder Mask Clearance | All | 0.05 mm |
| Manufacturing | Silk to Silk Clearance | All | 0 (or 0.05) |
| Placement | Component Clearance | All | 0.2 mm (3D check enabled) |
| High Speed | Matched Lengths, Max Via Count, etc. | As needed | Chapter 17 |

### The query language (worth learning)
```
InNet('VBUS')                     a single net
InNetClass('PWR')                 a net class
InComponent('U1')                 pads of U1
InDifferentialPairClass('USB')    diff pairs in class
IsPad and InNet('GND')            combined scopes
HasFootprint('QFN*')              wildcard footprints
InNamedPolygon('GND_L2')          a named polygon
```
Use **Query Helper** or **Query Builder** in the rule dialog to construct these, and **PCB Filter** (`F12`) to test them.

⚠️ **Gotcha:** rule priority. A generic rule with higher priority than a specific one will silently override it.
In the Rules dialog, click **Priorities** and keep specific rules above general ones.

## 7.6 Output Job file (do it once, reuse forever)

Create **File » New » Output Job File** with these outputs (details in Chapter 25):
- Gerber X2 (or Gerber RS-274X) for all used layers + **NC Drill** (Excellon), or **ODB++** / **IPC-2581** (preferred by many fabs)
- Pick and Place (centroid) file
- BOM (from ActiveBOM)
- Schematic PDF, Assembly Drawings PDF, Fab Drawing (Draftsman)
- 3D STEP export
- Design Rule Check report (as a validation output, so you can't release without a clean DRC)
- ERC / Differences report

Then **Container** outputs let you generate everything into a folder (`releases/rev-A/`) with one click.

## 7.7 Libraries strategy (decide early)

| Strategy | Pros | Cons | Good for |
|----------|------|------|----------|
| Per-project SchLib/PcbLib | Simple | Duplicated, drift | One-off experiments |
| **Shared lab SchLib/PcbLib in git** | Simple, versioned, shared | Manual parameter management | **Small research labs** ✔ |
| DbLib (Excel/Access/SQL + shared libs) | Parametric, one source of truth | More setup | Groups with lots of boards |
| Altium 365 / Workspace managed components | Lifecycle, where-used, supply chain | Needs a workspace license | Companies |

Chapter 9 details how to build parts properly.

## 7.8 Altium 365 (if your institution has it)
- Cloud-hosted projects with version history, web viewer for reviewers without Altium, commenting on the design, and a
  shared managed component library.
- Using git instead is fine: Altium has built-in git support in the **Projects panel** (right-click » *Version Control*).

## Exercises
1. Create your schematic template with special strings. Verify the title block fills in automatically.
2. Create your 2-layer PCB template with the rules table above. Export the rules to a `.rul` file.
3. Build an OutJob that produces Gerber X2 + drill + PnP + BOM + schematic PDF to a single output container.

**Next:** [Chapter 8 — Schematic Capture as Engineering Communication](08-schematic-capture.md)
