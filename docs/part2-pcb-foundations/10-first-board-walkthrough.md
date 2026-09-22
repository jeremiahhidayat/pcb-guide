# Chapter 10 — Your First Board: End-to-End Walkthrough

> **Mentor's note:** We'll build a small, useful board so you touch every step once: a **USB-C powered 3.3 V
> supply with an LED, a user header, and test points**. It's simple enough to finish in a weekend and
> covers the same flow as a 20-layer server board. The full spec is in [`projects/01-usb-c-power-board/`](../../projects/01-usb-c-power-board/README.md).

---

## Step 1 — Requirements

- Input: USB-C (5 V sink only, default USB power, up to 500 mA / or 1.5–3 A if the source advertises it).
- Output: 3.3 V @ up to 500 mA on a 2.54 mm header, plus 5 V passthrough.
- Protection: ESD on USB, overcurrent (PTC), reverse polarity isn't possible with USB-C but add a TVS on VBUS.
- Power-good LED. Test points on VBUS, 3V3, GND.
- 2 layers, 1.6 mm, 1 oz, ENIG, ~30 × 25 mm.

## Step 2 — Design decisions from first principles

**USB-C sink identification:** A USB-C source only turns on VBUS when it sees a sink. The sink signals itself with
**5.1 kΩ pull-down resistors on CC1 and CC2** (Rd). Leaving them out is the most common mistake on hobby USB-C boards:
the board works with an A-to-C cable but not with a C-to-C charger. *Each CC pin gets its own 5.1 kΩ*. Don't
tie CC1 and CC2 together through one resistor.

**Regulator choice:** 5 V → 3.3 V at 0.5 A.
```
LDO dissipation: (5 − 3.3) × 0.5 = 0.85 W
SOT-223 on 2-layer with a copper pour: θJA ≈ 60–70 °C/W → ΔT ≈ 55 °C. OK at room temp.
SOT-23-5: θJA ≈ 200 °C/W → ΔT = 170 °C. Not OK.
```
Decision: an LDO in SOT-223 (e.g. AMS1117-3.3-class or better, a modern LDO like the AP2112 is only 600 mA in SOT-23-5 → too hot).
*Alternative*: a small buck module. For a first board, the LDO keeps layout simple.

⚠️ AMS1117-class parts need a **tantalum or ESR-specified output cap** for stability (older LDO architecture). Read
the datasheet's stability section, or choose a modern ceramic-stable LDO (e.g. TLV1117LV, or an LDO explicitly "stable with ceramic").

**LED resistor:** (3.3 − 2.0) / 2 mA = 650 Ω → 680 Ω. 2 mA is plenty for modern LEDs.

**Decoupling:** input 10 µF + 100 nF, output per datasheet (e.g. 10 µF ceramic + 100 nF).

## Step 3 — Schematic in Altium

1. **File » New » Project » PCB Project** `usbc-power.PrjPcb`. Add `01_Power.SchDoc`.
2. Place parts from your library (Chapter 9). Search Manufacturer Part Search for: USB-C receptacle 16-pin
   (e.g. GCT USB4105 / Hirose / Molex — pick one with good stock), TVS (e.g. `ESD5Z5V` / `SMF5.0A` on VBUS, low-C
   array on D+/D− if used), PTC (0.5–1 A hold), LDO, caps, LED, header, test points.
3. Wire it up following Chapter 8's style rules. Net labels: `VBUS`, `VBUS_F` (after fuse), `3V3`, `GND`, `CC1`, `CC2`.
4. Add a **Parameter Set** directive with `ClassName = PWR` on `VBUS`, `VBUS_F`, `3V3`.
5. **Project » Validate PCB Project**, and fix every warning.

```
 J1 USB-C                F1 PTC        U1 LDO
 VBUS ──┬───────────────[////]──┬────── IN   OUT ──┬──────┬─── 3V3 ──► J2, TP2
        │ D1 TVS               │C1 10µ   GND      │C3 10µ│C4 100n
        ▼                      │C2 100n   │       │      │   R1 680 ── LED D2 ── GND
 CC1 ──[5.1k R2]── GND         GND       GND     GND    GND
 CC2 ──[5.1k R3]── GND
 GND/Shell ── GND   (shell via 1 MΩ ∥ 4.7 nF to GND is a common EMC practice; direct is fine for a first board)
```

## Step 4 — PCB setup

1. **Design » Update PCB Document**. Parts land in a Room next to the board. Delete the room (or keep it for grouping).
2. **Board shape:** Draw the outline on Mech 1 with lines/arcs, select it, then **Design » Board Shape » Define from selected objects**.
   Round the corners (radius 1 mm).
3. **Layer Stack Manager** (`D`, `K`): 2 layers, 1.6 mm, 1 oz. Enter the fab's actual FR-4 data if you plan impedance later.
4. **Rules:** import your template rules (Chapter 7) or set clearance 0.15 mm, width 0.25 mm default, `PWR` class width 0.5 mm min.
5. **Grid:** set a placement grid (e.g. 0.5 mm) and a routing grid (0.05 mm or 0.025 mm). `Ctrl+G` or `G` opens grid options.

## Step 5 — Placement (this is where 70% of layout quality is decided)

Order of placement:
1. **Mechanically constrained parts first:** USB-C at the edge (the receptacle's shell often overhangs the edge; follow the datasheet!),
   header, mounting holes.
2. **Protection right at the connector:** TVS D1 within a few mm of J1's VBUS pins, then the PTC.
3. **Power path in a straight line:** J1 → F1 → C1/C2 → U1 → C3/C4 → J2. Current flows through the parts in order.
4. **Caps closest to the pins they serve**, with their ground pad close to a ground via or pour.
5. LED and resistor can go anywhere sensible. Test points where a probe can reach them.

🛠️ Useful placement tools:
- **Select parts in schematic → they're selected in PCB** (cross-probe, `Ctrl`+double-click or the **Cross Select Mode** toggle).
- **Tools » Component Placement » Arrange Within Rectangle** to pull a group of parts together.
- **Align** (`A`) tools: align left/top, distribute evenly.
- `Space` rotates, `L` while dragging flips to the bottom layer.

## Step 6 — Routing

- **Ground first:** on a 2-layer board, make the **bottom layer an (almost) solid ground pour**. Route signals on top, and keep bottom-layer
  traces short and few, so they don't cut the ground into islands.
- Power traces: route `VBUS` and `3V3` with wide traces (≥0.5 mm; see the IPC-2152 calc below) or pours on top.
- **Interactive route:** `Ctrl+W` (or **Route » Interactive Routing**). While routing:
  - `Tab` opens properties (width, via style) mid-route
  - `Shift+Space` cycles corner styles (45°, arc, 90°...); use 45° or arcs
  - `*` (numeric keypad) or `Ctrl+Shift+scroll` switches layer and drops a via
  - `Shift+R` cycles conflict resolution (Ignore/Walkaround/Push/Hug & Push)
  - `Backspace` undoes the last segment
- **Polygon pours:** **Place » Polygon Pour** on Bottom, connect to `GND`, *Pour Over All Same Net Objects*, *Remove Dead Copper*.
  Repour everything with `T`, `G`, `A` (Tools » Polygon Pours » Repour All).
- **Stitching vias:** connect top-layer GND pours to the bottom GND plane every ~5–10 mm and at every ground pad of a cap/IC.
  **Tools » Via Stitching/Shielding » Add Stitching to Net**.

**Trace width check (IPC-2152-style estimate, via the repo tool):**
```bash
python tools/pcb_calc.py trace-width --current 0.5 --temp-rise 10 --copper-oz 1 --layer external
# ≈ 0.12 mm minimum (IPC-2221 estimate) → use 0.5 mm anyway: lower drop, lower inductance, margin
```

## Step 7 — Silkscreen & documentation on the board
- Designators readable, all in the same orientation (two orientations max), not on pads or vias.
- Board name, revision, date, your lab name; pin labels on the header (`3V3`, `GND`, `5V`); polarity marks on the LED.
- Hide designators under dense areas and rely on the assembly drawing instead.

## Step 8 — Design rule check
**Tools » Design Rule Check** (`T`, `D`) → *Run Design Rule Check*. Target **zero violations**.
If a violation is intentional (e.g. a net tie), write a specific rule to allow it. Don't just ignore it.
Also look at the 3D view (`3`) for collisions and the **Unrouted Net** rule for missing connections.

## Step 9 — Outputs and ordering
Run your OutJob (Chapter 25): Gerbers + drill + BOM + PnP. **Open the Gerbers in a viewer** (Altium's CAMtastic via
**File » Import » Gerber**, or the fab's online viewer, or tracespace.io) and check each layer. Order 5 boards
(assembled or bare).

## Step 10 — Bring-up
Follow Chapter 26: visually inspect → check for shorts between rails and GND with a multimeter → power from a
**current-limited bench supply** (set 5 V, 100 mA limit) → measure 3V3 → then plug into USB-C.

## What you should have learned
- Every schematic decision came from a calculation or a spec (USB-C Rd, thermal, LED current).
- Placement followed current flow.
- Ground got designed (solid bottom plane), not just "connected."
- Outputs were verified *independently* of the tool that produced them.

**Next part:** [Part 3 — Chapter 11: Power Supply Design](../part3-intermediate/11-power-supply-design.md)
