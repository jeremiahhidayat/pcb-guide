# Chapter 6 — What a PCB Physically Is

> **Mentor's note:** Design gets easier once you picture how the board is *made*. Every design rule is
> a fabrication limit or a physics limit. Learn the process and the rules stop feeling arbitrary.

👉 Visual companions: [`diagrams/pcb-stackup.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/pcb-stackup.html) (layers, vias) and
[`diagrams/pcb-fab-process.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/pcb-fab-process.html) (manufacturing steps).

---

## 6.1 Anatomy of a PCB

```
      Silkscreen (legend)          ← ink, text/outlines
      Solder mask (usually green)  ← polymer coating; prevents solder bridges, protects copper
  ════ Top copper (L1) ════         ← traces, pads, pours
  ░░░░ Prepreg (dielectric) ░░░░   ← glass fabric + resin (partially cured before lamination)
  ════ Inner copper (L2) ════       ┐
  ████ Core (dielectric) ████       ├ a "core" = cured laminate with copper on both sides
  ════ Inner copper (L3) ════       ┘
  ░░░░ Prepreg ░░░░
  ════ Bottom copper (L4) ════
      Solder mask
      Silkscreen
```

| Term | Meaning |
|------|---------|
| **Core** | Rigid, fully cured fiberglass/epoxy with copper foil bonded to both sides |
| **Prepreg** | "Pre-impregnated" glass cloth with partially cured resin. Melts and bonds layers during lamination |
| **FR-4** | Flame-retardant glass-epoxy laminate class. εr ≈ 3.8–4.6 (frequency-dependent), Tg 130–180 °C |
| **Copper weight** | oz/ft²: 0.5 oz ≈ 17.5 µm, **1 oz ≈ 35 µm**, 2 oz ≈ 70 µm. Outer layers get plated up (+~25 µm) |
| **Tg** | Glass transition temperature; above it the resin softens and expands fast in Z. Use **high-Tg (≥170 °C)** for lead-free assembly and thick boards |
| **Finish** | Coating on exposed pads: HASL (cheap, uneven), **ENIG** (flat, good for fine pitch; default choice), OSP, immersion silver/tin, ENEPIG (wire bonding) |

## 6.2 Vias

| Via type | Description | Cost |
|----------|-------------|------|
| **Through-hole via** | Drilled through all layers, plated | Base cost |
| **Blind via** | Connects an outer layer to inner layer(s), doesn't go through | $$ (sequential lamination) |
| **Buried via** | Connects only inner layers | $$ |
| **Microvia** | Laser-drilled, ≤ 0.15 mm, spans one layer pair (HDI) | $$$ |
| **Via-in-pad (filled & capped)** | Via inside an SMD pad, filled with epoxy and plated over | $$ (needed for fine-pitch BGA) |

🧠 **Aspect ratio** = board thickness / drill diameter. Plating chemistry has to flow through the hole, and
long thin holes plate poorly. Standard fabs handle about 8:1 to 10:1. For a 1.6 mm board, the minimum
drill is around 0.2 mm (8 mil), and 0.3 mm (12 mil) is comfortable everywhere.

**Annular ring** = (pad diameter − drill diameter)/2. The drill can wander, and a ring that's too thin breaks
out. A typical minimum is 0.125–0.15 mm (5–6 mil) for prototype fabs.

**Tenting**: covering vias with solder mask so they don't wick solder or short to things. Tent vias by default,
except test-point vias.

## 6.3 How a multilayer PCB is manufactured (summary)

1. **Inner layer imaging:** photoresist on the core → expose with the layer image → develop → **etch** unwanted copper → strip.
2. **AOI** (automated optical inspection) of the inner layers.
3. **Oxide treatment** for adhesion → **lay-up** cores + prepreg + outer foils → **lamination** under heat and pressure.
4. **Drilling** (mechanical; laser for microvias).
5. **Desmear + electroless copper** (makes hole walls conductive) → **pattern plating** (copper plated up in holes and on outer traces).
6. **Outer layer etch.**
7. **Solder mask** application, exposure, cure.
8. **Surface finish** (ENIG, etc.).
9. **Silkscreen.**
10. **Electrical test** (flying probe or bed of nails) → **routing/V-scoring** of the board outline → final inspection.

### What this teaches you about design rules
- **Etching undercuts** sidewalls, so fine lines need thin copper. That's why 2 oz copper forces wider minimum trace/space.
- **Outer layers get plated**, so they're thicker than the base foil. Impedance calculators need the *final* thickness.
- **Registration between layers is imperfect** (±75 µm is typical), which drives annular ring and mask-expansion rules.
- **Solder mask has a minimum web (sliver)** between openings (~0.1 mm). Fine-pitch ICs may need "gang relief."
- **Copper balance:** big empty areas on one layer and dense copper on its mirror layer cause **bow and twist**
  during lamination. Add copper fill (balanced pours) where reasonable.

## 6.4 Typical fab capabilities (orient yourself; always check your fab's current page)

| Parameter | Budget prototype fab (e.g. JLCPCB/PCBWay/OSH Park standard) | Advanced production |
|-----------|--------------------------------------------------------------|---------------------|
| Min trace/space | 0.127/0.127 mm (5/5 mil) (some go to 3.5 mil) | 0.075 mm (3 mil) or less |
| Min drill (mechanical) | 0.2–0.3 mm | 0.15 mm |
| Min annular ring | 0.13–0.15 mm | 0.075–0.1 mm |
| Layer count | 1–6 (up to 20+ at extra cost) | 40+ |
| Impedance control | ±10% (often available, with fab's stackup) | ±5–7% |
| Board thickness | 1.6 mm standard (0.4–2.4 mm options) | Any |
| Copper | 1 oz (0.5–2 oz options) | Up to 6+ oz |

🏭 **Industry practice:** Design to **the fab's "standard" capability, not their minimum.** The minimum is
possible but costs yield, and sometimes money. Leave margin. If you have to push a limit, push one limit,
in one place.

## 6.5 Board outline, mechanical, and panelization

- **Board outline** (Altium: *Board Shape* plus a mechanical outline layer). Cut by a router bit (typically 2 mm, so
  internal corners get a minimum radius of about 1 mm).
- **Mounting holes:** Plated or not? Connected to ground? M3 clearance = 3.2 mm hole, ~6 mm keep-out for the screw head.
- **Panelization:** small boards get grouped into panels with tabs ("mouse bites") or V-scores. Parts close to the
  edge (<3 mm) can be damaged by depanelization stress. **MLCCs crack!** Orient MLCCs parallel to a V-score line
  and keep them away from it.
- **Fiducials** (1 mm copper dot, 2–3 mm mask opening): at least 3 per panel/board for the pick-and-place machine
  vision; also local fiducials near fine-pitch parts.

## 6.6 🛠️ Mapping this to Altium's layers

| Physical thing | Altium layer(s) |
|----------------|------------------|
| Copper layers | Top Layer, Mid-Layer 1..n, Bottom Layer; **Signal** vs. **Plane** types (planes are drawn in the *negative*) |
| Solder mask | Top/Bottom Solder (openings are drawn: a shape here = *no mask*) |
| Paste stencil | Top/Bottom Paste |
| Silkscreen | Top/Bottom Overlay |
| Mechanical | Mechanical 1..n. **Use Layer Pairs and Component Layer Types** (AD 21+) for Assembly, Courtyard, 3D Body, Board Outline |
| Drill info | Drill Guide / Drill Drawing |
| Keep-out | Keep-Out Layer (routing/placement restrictions) |

**Recommended mechanical layer convention** (set it once in your template and never change it):
```
Mech 1   Board outline / dimensions
Mech 13  Top 3D Body         (paired with Mech 14 Bottom 3D Body)
Mech 15  Top Courtyard        (paired with Mech 16 Bottom Courtyard)
Mech 2/3 Top/Bottom Assembly (component outlines + designators for assembly drawings)
```
Many companies use similar schemes. What matters is consistency across *all* libraries and boards.
In AD21+ you can assign *layer types* (Courtyard, Assembly, 3D Body) to mechanical layers, which makes this robust.

## Exercises
1. For a 2.0 mm thick board, what minimum drill do you expect at 8:1 aspect ratio? *(0.25 mm.)*
2. Why are internal corners of a routed board outline rounded?
3. Read your preferred fab's capability page and fill in the table in 6.4 with their values.

**Next:** [Chapter 7 — Setting Up Altium Properly](07-altium-environment-setup.md)
