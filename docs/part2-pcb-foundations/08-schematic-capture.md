# Chapter 8 — Schematic Capture as Engineering Communication

> **Mentor's note:** A schematic has two readers: the netlist compiler and the human who has to debug the
> board at 11 pm. The compiler is easy to satisfy. Write for the human.

---

## 8.1 Start before Altium: requirements and block diagram

Answer these on paper first:

1. **What does the board do?** One sentence.
2. **Inputs/outputs:** connectors, signals, voltage ranges, currents, data rates.
3. **Power:** input source(s), rails needed, current per rail (a **power budget table**).
4. **Environment:** temperature, size, enclosure, mounting.
5. **Performance targets:** noise floor, sample rate, accuracy, battery life.
6. **Constraints:** cost, fab/assembly vendor, timeline, parts you can actually buy.

### Power budget table (fill this out on every board)

| Rail | Source | Consumer | Typ mA | Max mA | Notes |
|------|--------|----------|--------|--------|-------|
| 3V3 | Buck U2 | MCU | 30 | 80 | incl. radio TX peaks |
| 3V3 | Buck U2 | ADC digital | 2 | 5 | |
| 3V3A | LDO U3 from 5V | ADC analog + AFE | 10 | 15 | low-noise |
| **Total 3V3** | | | 32 | 85 | → U2 rated ≥ 150 mA (≥ 1.5× margin) |

## 8.2 Organize with hierarchy

For anything beyond ~50 parts, use **multiple sheets**:
```
00_Top.SchDoc        ← sheet symbols (blocks) with ports; a readable block diagram
 ├─ 01_Power.SchDoc
 ├─ 02_MCU.SchDoc
 ├─ 03_AFE.SchDoc
 ├─ 04_Connectors.SchDoc
 └─ 05_Debug_Test.SchDoc
```
🛠️ **In Altium:**
- **Place » Sheet Symbol** on the top sheet, set its *File Name* to the child sheet, then
  **Design » Synchronize Sheet Entries and Ports**.
- **Project » Project Options » Options » Net Identifier Scope**: choose **Hierarchical** (ports connect only
  through sheet entries; safest) or **Automatic**. Avoid *Global* in large designs: it makes every port global
  and a name collision silently shorts nets.
- **Multi-channel design:** for 8 identical sensor channels, draw one channel and place a sheet symbol
  with `Repeat(CH,1,8)` as the designator. Altium creates 8 channels with unique designators,
  and **Rooms** in the PCB let you copy the placement and routing of one channel to all the others
  (Design » Rooms » Copy Room Formats).

## 8.3 Schematic style rules (industry-standard habits)

1. **Signal flow left → right, voltage high at top → low at bottom.** Inputs on the left, outputs on the right.
2. **Power symbols** (VCC arrow up, GND down) instead of drawing long power wires. In Altium, the power port's
   *Net* property is what matters. The style is cosmetic.
3. **Net labels over long wires.** Label every net you'll want to probe, and name them meaningfully:
   `ADC_CS_N`, `I2C1_SDA`, `VBAT_SENSE`. Suffix active-low signals with `_N` (or `_B`/`#`) consistently.
4. **No 4-way junctions.** Use two offset T-junctions, so that a missing junction dot can't be mistaken for a crossing.
5. **Decoupling capacitors drawn next to the IC they belong to**, with a note: "place near U3 pin 7."
6. **Show values that matter:** R/C value, tolerance where it matters, voltage for caps, dielectric where it matters
   (`100n X7R 16V 0402`).
7. **Annotate intent with notes:** "R12/R13 set gain = 21 V/V", "Place TVS D1 within 5 mm of J1."
   Put design intent on the schematic, next to the part it applies to.
8. **Don't hide pins.** Some libraries hide power pins. That hides connection errors, so make power pins visible.
9. **Unused pins:** place a **No ERC** marker (`P`, `V`, `N`) with intention, or tie off per the datasheet
   (unused op-amp sections need a defined state: buffer tied to mid-supply).
10. **Test points** on every rail and key signals (TPxx designators).

## 8.4 Directives: putting layout intent into the schematic

Altium lets the schematic carry PCB constraints:
- **Net Class directive** (`Place » Directives » Parameter Set` with a *Net Class* parameter): put `ClassName=PWR` on the
  power nets. The PCB gets a class automatically when you update.
- **Differential pair directive** (`Place » Directives » Differential Pair`): nets named `USB_P` / `USB_N` (the
  `_P`/`_N` suffixes are required) with a diff-pair directive become a diff pair object in the PCB.
- **PCB rules from schematic**: a Parameter Set can hold a *Rule* (width, clearance, etc.).
- **Blanket directives**: draw a blanket around an area (for example the whole AFE) and attach a directive to all the nets inside it.

## 8.5 Compile, ERC, and what the warnings actually mean

**Project » Validate PCB Project** (older: *Compile*). Then read the **Messages** panel.

Configure **Project Options » Error Reporting** and **Connection Matrix** once:

| Typical violation | Usual root cause |
|-------------------|------------------|
| *Floating net label / power object* | Label placed off the wire end, or wire not snapped to grid |
| *Net has only one pin* | Typo in a net label (`SDA` vs `SDA1`), or an unconnected port |
| *Duplicate part designators* | Need **Tools » Annotation » Annotate Schematics** |
| *Nets with multiple names* | Two different labels on the same net. Sometimes intentional (use a net tie), usually a bug |
| *Unconnected input pin* | Real problem, or needs a No-ERC with justification |
| *Output pin connected to output pin* | Real bus contention. Check it |

⚠️ **Treat ERC warnings as errors until you understand each one.** Tune the connection matrix so
the warnings you *keep* all mean something.

### Annotation strategy
- **Tools » Annotation » Annotate Schematics** (`T`, `A`, `A`) → order: *Down then Across*. Keep designators stable
  after the first release (lock annotation), otherwise every revision renames parts and breaks traceability.
- **Board-level annotation** (optional) re-numbers designators by PCB location (useful for assembly). Do it once, deliberately.

## 8.6 Transferring to PCB

1. **Design » Update PCB Document my-board.PcbDoc** → the **Engineering Change Order (ECO)** dialog.
2. **Validate Changes** first. Any red X means a footprint wasn't found or a pin-pad mismatch exists.
3. **Execute Changes.** Components appear to the right of the board in a **Room** named after each sheet.
4. Round-trip: changes made in PCB (for example pin swaps) → **Design » Update Schematics**.

⚠️ **Gotcha:** never edit connectivity only in the PCB. The schematic is the source of truth. Use ECO both ways.

## 8.7 Schematic review checklist (short form)
Full version: [`checklists/schematic-review.md`](../../checklists/schematic-review.md).
- Every IC: all power pins decoupled, ground pins connected, exposed pad connected per datasheet.
- Every pull-up/pull-down justified. Reset, boot, and enable pins in a defined state at power-up.
- Every connector pin: ESD protection where exposed, pinout double-checked against the mating connector (**draw the mating side!**).
- Every regulator: input/output caps per datasheet, thermal calc done, enable logic understood.
- Voltage levels compatible across every interface (3.3 V MCU → 5 V sensor?).
- Every polarized part oriented correctly (diodes, electrolytics, tantalums).

## Exercises
1. Draw the block diagram and power budget for a board you want to build for your research.
2. Make a two-sheet hierarchical schematic in Altium with ports and a sheet symbol. Compile it and fix every warning.
3. Deliberately create the 6 violations in the table above and see how Altium reports each one.

**Next:** [Chapter 9 — Libraries, Symbols & Footprints](09-libraries-and-footprints.md)
