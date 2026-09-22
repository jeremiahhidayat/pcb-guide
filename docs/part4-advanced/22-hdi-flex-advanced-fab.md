# Chapter 22 — HDI, Flex, Rigid-Flex & Advanced Fabrication

> **Mentor's note:** Advanced fabrication gets you density and form factor, and costs money and lead time.
> Know what each technology does and what it costs, and bring the fab in *before* you start the layout.

---

## 22.1 When do you need HDI?

**BGA pitch drives it.** Escape routing from a BGA needs vias between balls:

| BGA pitch | Typical escape |
|-----------|----------------|
| 1.0 mm | Through-hole vias between balls ("dog-bone" fanout), standard fab |
| 0.8 mm | Through vias possible (0.2–0.25 mm drill, 0.45 mm pads), dog-bone. Tight but standard |
| 0.65 mm | Via-in-pad (filled & capped) or microvias |
| 0.5 mm and below | **HDI: laser microvias in pad**, often stacked/staggered, sequential lamination |

## 22.2 HDI structures (IPC-2226 types)
```
 1+N+1 : one microvia layer on each side of a standard core stack
 2+N+2 : two sequential build-up layers each side (stacked or staggered microvias)
 Any-layer: every layer built up with microvias (smartphones)
```
- **Microvias:** laser drilled, ~0.1 mm diameter, aspect ratio ≤ ~0.8:1, span one dielectric layer.
- **Staggered** microvias are more reliable than **stacked** ones (stacked need copper filling and are a known reliability concern under thermal cycling).
- **Via-in-pad plated over (VIPPO):** the via is filled (epoxy or copper), planarized and plated. Allows vias directly in BGA/QFN pads without solder wicking.
- Each sequential lamination cycle adds cost and lead time. **1+N+1 with staggered vias is the cost-effective entry to HDI.**

🛠️ **Altium:** Layer Stack Manager → **Via Types** tab: define each allowed span (e.g. L1–L2 microvia, L2–L7 buried, L1–L8 through).
Then in *Routing Via Style* rules pick the allowed types, and the router uses them when changing layers. Mark microvias as such
(the *Microvia* checkbox) so DRC applies the right checks.

## 22.3 Back-drilling
Removes the unused via stub on thick boards for multi-gigabit signals (Chapter 16). Specify it in Altium in Layer Stack Manager
(**Back Drills** tab) and it generates the back-drill files.

## 22.4 Flex and rigid-flex
- **Flex:** polyimide base with rolled-annealed copper (ductile), coverlay instead of solder mask, stiffeners where components mount.
- **Rigid-flex:** rigid sections connected by flex layers that continue through the rigid parts. Replaces connectors and cables, and allows
  3D folding (wearables, compact instruments, implant/probe research).

### Flex design rules (derived from mechanics)

| Rule | Why |
|------|-----|
| Bend radius ≥ 10× thickness (dynamic flex: ≥ 20–40×; single layer best) | Copper fatigue cracks at the outer fiber of the bend |
| Traces perpendicular to the bend line; no vias or pads in bend areas | Stress concentration |
| Stagger traces on adjacent layers (I-beam effect avoidance) | Stacking stiffens and stresses |
| Curved traces, teardrops everywhere, no sharp corners | Crack initiation points |
| Cross-hatched ground instead of solid copper in flex areas | Flexibility (at some SI cost) |
| Stiffeners (FR-4/polyimide/steel) under connectors and components | Solder joints can't flex |
| Keep copper in the neutral bend axis for dynamic flex (single-layer or symmetric) | Minimizes strain |

🛠️ **Altium rigid-flex:** Layer Stack Manager → *Features → Rigid/Flex* (enable), create **multiple sub-stacks** (e.g. "Rigid 6L" and "Flex 2L"),
then in the PCB's **Board Planning Mode** (`1` key) draw *split lines* to define regions and assign each a sub-stack, and define **bending lines**
with radius and angle. The 3D view (`3`) can show the board **folded**. Check fit against the enclosure STEP.

## 22.5 Other advanced options

| Technology | Use |
|------------|-----|
| Heavy copper (3–10 oz) | Power electronics, bus bars on PCB |
| Metal-core PCB (IMS, aluminum base) | High-power LEDs, power modules (single layer, excellent thermal) |
| Embedded components / cavities | Ultra-thin or high-performance modules |
| Castellated holes | Modules that solder onto other boards (half-plated holes on the edge) |
| Edge plating | Shielding, grounding to chassis rails |
| Controlled-depth routing / milling | Slots, pockets |
| Press-fit holes | Connectors without soldering (tight hole tolerance) |
| Ceramic (LTCC, alumina) | RF, harsh environments, biomedical implants |

## 22.6 Cost drivers (roughly in order)
1. Layer count
2. HDI build-up cycles / via types
3. Board area and panel utilization
4. Special materials (Rogers, polyimide, low-loss)
5. Min trace/space and drill (below "standard")
6. Controlled impedance, back-drilling, via-in-pad
7. Finish (ENIG vs. HASL), thickness, copper weight
8. Lead time

🏭 **Industry practice:** Get a **DFM quote early** with a draft stackup and design rules. Ask the fab: "What's your standard capability that doesn't cost extra?"
and design to that.

## Exercises
1. For a 0.5 mm-pitch BGA with 12×12 balls, sketch an escape strategy using 1+N+1 HDI. How many routing layers do you need?
2. Design a 2-layer flex cable connecting two rigid boards with a 5 mm bend radius. What copper type and coverlay do you specify?

**Next part:** [Part 5 — Chapter 23: Design Reviews](../part5-industry/23-design-reviews.md)
