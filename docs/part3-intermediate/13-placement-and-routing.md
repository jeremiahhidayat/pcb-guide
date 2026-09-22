# Chapter 13 — Component Placement & Routing Strategy

> **Mentor's note:** Good placement routes itself. If routing is a fight, stop and re-place. Senior
> designers often spend 60–70% of layout time on placement.

---

## 13.1 Placement order (the professional sequence)

1. **Mechanical first:** board outline, mounting holes, connectors, switches, LEDs, displays, anything that has to
   line up with an enclosure. Lock them (`Properties » Locked`).
2. **Define functional zones** (power entry, SMPS, digital, analog, RF) per Chapter 12's partitioning.
   Drawing rooms or keep-outs helps you visualize them.
3. **Critical components:** the main IC (MCU/FPGA), the ADC, the crystal, the SMPS hot loop, high-speed connectors.
4. **Critical support parts** tightly around them: decoupling caps, crystal load caps, feedback dividers, termination resistors.
5. **Everything else**, following signal flow.
6. **Test points and debug** last (but reserve space for them early).

### Placement heuristics with the physics behind them

| Heuristic | Why |
|-----------|-----|
| Follow the schematic signal flow physically | Short, un-crossing connections, and separation of input and output (prevents feedback/oscillation) |
| Decoupling cap between the IC power pin and its via, as close as possible (<1–2 mm) | Minimizes loop inductance (Chapter 14) |
| Crystal within ~5 mm of the MCU, nothing routed under it, ground guard | High-impedance, low-level oscillator nodes are very susceptible |
| Keep switchers ≥ 10–20 mm from sensitive analog, and orient the inductor's field away | Magnetic and capacitive coupling |
| Connectors grouped on one edge when possible | Cables are antennas. Grouping I/O keeps common-mode currents from flowing *across* the board between cables (Chapter 19) |
| Heat sources spread out, away from temperature-sensitive parts (references, sensors, crystals) | Thermal gradients cause drift and thermocouple effects |
| Same-orientation passives in rows | Assembly yield, AOI, reflow evenness |
| Components ≥ 3–5 mm from board edge and from V-score lines, MLCCs parallel to the edge | Depanelization stress cracks MLCCs |
| Leave room for rework: 1–2 mm around BGAs/QFNs for a hot air nozzle | You will rework the prototype |

## 13.2 Routing priority order

1. **Power and ground** connections (short, wide, many vias).
2. **Critical signals:** clocks, high-speed diff pairs, sensitive analog, SMPS feedback.
3. **General digital signals.**
4. **Slow signals** (LEDs, config straps) last. They can go anywhere.

## 13.3 Trace width: current, drop, and impedance

Width is set by whichever requirement is strictest:
1. **Current (heating):** IPC-2221 (older, conservative) or IPC-2152 (modern, more accurate, and accounts for planes nearby, which help cool the trace).
2. **Voltage drop:** R = 0.5 mΩ/□ × (length/width) for 1 oz. For power rails this often dominates.
3. **Impedance:** controlled-impedance nets have their width set by the stackup (Chapter 16/18).
4. **Manufacturability:** ≥ fab minimum, preferably ≥ 0.15 mm.

```
IPC-2221:  I = k · ΔT^0.44 · A^0.725     A in mil², I in A, ΔT in °C
           k = 0.048 (external), 0.024 (internal)
```
Quick table (1 oz, ΔT = 10 °C, IPC-2221, external):

| Current | Min width |
|---------|-----------|
| 0.5 A | 0.12 mm |
| 1 A | 0.30 mm |
| 2 A | 0.79 mm |
| 3 A | 1.38 mm |
| 5 A | 2.78 mm |

Internal layers need roughly 2.6× the width by IPC-2221, but IPC-2152 shows the difference is much smaller in practice.
Use the calculator: `python tools/pcb_calc.py trace-width ...`.

## 13.4 Via sizing and current
- A standard via (0.3 mm drill, ~25 µm plating) carries roughly 1 A for a modest temperature rise. **Use multiple vias
  for power transitions:** e.g. 3 A → 4–6 vias. More vias also means lower inductance (vias in parallel).
- Via inductance estimate: `L ≈ 5.08·h·[ln(4h/d) + 1]` nH (h, d in inches). See `python tools/pcb_calc.py via`.

## 13.5 Routing style rules
- **45° corners or arcs.** 90° corners don't cause the reflections people claim at typical speeds (the discontinuity
  is tiny below tens of GHz), but acute angles can trap etchant ("acid traps" on old processes) and 45°/arc is
  the industry norm and routes denser.
- **No stubs** on high-speed nets. Daisy-chain or use fly-by topology.
- **Neck-down** allowed at fine-pitch pads (for example a 0.5 mm trace narrowing to 0.2 mm to enter a QFN pad). Keep the neck short.
- **Teardrops** (**Tools » Teardrops**): add copper at trace-pad and trace-via junctions. They improve mechanical and drill-registration robustness.
  Do it at the end, before release.
- **Don't route between pads of 0402/0201 parts** if it can be avoided.
- **Orthogonal routing on adjacent signal layers** (L3 horizontal, L4 vertical) minimizes broadside crosstalk when two signal layers sit next to each other.

## 13.6 Crosstalk basics (more in Chapter 16)
- **3W rule:** center-to-center spacing ≥ 3× trace width keeps ~70% of flux from coupling.
  It's a heuristic. The real driver is spacing relative to **height above the plane** (h). Crosstalk ∝ 1/(1 + (s/h)²).
  **Moving traces closer to their reference plane is the most effective crosstalk fix.**
- Avoid long parallel runs between aggressive (clocks, SMPS switch nodes) and sensitive (analog, reset lines) traces.
- **Guard traces**: grounded traces between aggressor and victim help only if stitched to ground with vias every
  ~λ/10 (or much more often). Otherwise, a floating or poorly stitched guard can make things *worse*. In analog high-impedance circuits,
  a *driven guard* (at the same potential as the guarded node) stops leakage (Chapter 15).

## 13.7 Polygons (copper pours)
- **Ground pour on outer layers**: useful on 2-layer boards (it *is* your ground plane). On 4+ layer boards with solid inner
  planes, outer-layer pours are optional. If you use them, **stitch them densely** (every ~λ/20 at your highest frequency
  of concern, e.g. every 3–5 mm) or remove small unstitched fingers. An unstitched copper island is a resonant antenna.
- **Thermal reliefs** on pads connected to pours so hand-soldering and reflow can heat the joint (spokes 0.25–0.3 mm).
  Use **direct connect** for high-current or thermal pads (with a dedicated rule scoped to those pads).
- Pour order: **Polygon Pour Manager**. Priority determines which pour wins where two overlap.

## 13.8 🛠️ Altium layout power tools

| Tool | Access | Use |
|------|--------|-----|
| Interactive Routing | `Ctrl+W` | Main routing |
| Differential Pair Routing | Route » Interactive Differential Pair Routing | Diff pairs |
| Multi-trace (bus) Routing | Route » Interactive Multi-Routing | Route a bus of selected nets together |
| ActiveRoute | Route » ActiveRoute (`Shift+A`) | Guided auto-routing of selected connections, useful for buses |
| Glossing / retracing | Route » Gloss Selected / Retrace Selected | Clean up routes, update to new rule widths |
| Length tuning | Route » Interactive Length Tuning / Diff Pair Length Tuning | Serpentines to match lengths |
| xSignals | Design » xSignals | Define pad-to-pad paths through series resistors for length matching |
| Net color / highlighting | View » Panels » PCB, or `F5` net color override | Visual clarity of power nets |
| Select connected copper | `Ctrl`+click on a net / `S`, `C` | Check net topology |
| Board Insight / Pad info | `Shift+X` / hover | Inspect under the cursor |
| Measure | `Ctrl+M`, **Reports » Measure Primitives** | Distances |
| Snap guides & Align | `A` | Clean placement |
| Rooms / Copy Room Formats | Design » Rooms | Replicate multi-channel layout |
| Component Unions / Snippets | Right-click » Unions | Keep a proven placement group (e.g. an SMPS) together; save as a Snippet to reuse |
| Design Reuse Blocks (AD 21+, with workspace) | | Reuse a validated SMPS or MCU circuit across projects |

## 13.9 A layout workflow that scales
```
1. Import netlist (ECO), set board outline, stackup, rules, classes
2. Place mechanical → zones → critical parts → support parts → rest
3. Fan out BGAs/QFNs (short stubs to vias), place decoupling
4. Route power (pours/planes), then critical signals, then the rest
5. Pour polygons, stitch ground, add teardrops
6. DRC → fix → DRC (repeat until clean)
7. Silkscreen cleanup, fab notes, assembly drawing
8. Peer review with the checklist (Chapter 23)
```

## Exercises
1. Take a finished eval-board layout and identify its zones, hot loops, and how it handled crystal and ADC placement.
2. For a 5 A rail over 40 mm on a 1 oz outer layer, compute the width needed for 10 °C rise and for < 50 mV drop. Which dominates?
3. Practice: route an 8-bit parallel bus with Multi-Routing and match lengths to ±1 mm.

**Next:** [Chapter 14 — Decoupling and the Power Delivery Network](14-decoupling-and-pdn.md)
