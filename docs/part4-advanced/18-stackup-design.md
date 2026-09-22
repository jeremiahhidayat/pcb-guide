# Chapter 18 — Stackup Design

> **Mentor's note:** The stackup is the foundation of SI, PI and EMC. You can't fix a bad stackup with good
> routing. Decide it early, ideally together with your fab, and don't change it casually.

👉 Visualize: [`diagrams/pcb-stackup.html`](../../diagrams/pcb-stackup.html).

---

## 18.1 Principles (Henry Ott's rules, derived)

1. **Every signal layer should be adjacent to a reference plane** → controlled impedance + defined return path.
2. **Signal layers tightly coupled (close) to their reference planes** → smaller loops, less crosstalk and EMI.
3. **Power and ground planes closely coupled** → plane capacitance, low PDN impedance at high frequency.
4. **High-speed signals on inner layers between planes** (stripline) → shielded, lower EMI.
5. **Multiple ground planes** help: lower impedance, better shielding, return path options.
6. **Symmetric stackup** (mirror about the center) → the board doesn't warp during lamination/reflow.

You can't satisfy all six with few layers. Stackup design is choosing which ones to give up.

## 18.2 Standard stackups

### 2 layers (1.6 mm)
```
L1  Signal + components + some power pours
    1.5 mm core (thick! → loose coupling, high Z for a given width)
L2  Ground (mostly solid) + minimal routing
```
50 Ω on a 1.5 mm core needs a ~3 mm trace. **Controlled impedance is impractical on 2 layers at 1.6 mm.** Use a 0.8 mm board or coplanar
waveguide (trace with ground pour beside it) for short RF runs.

### 4 layers: the workhorse (1.6 mm)
```
L1  Signal/components        ← 0.1–0.2 mm prepreg
L2  GND (solid)
    ~1.0–1.2 mm core
L3  Power (or signal + power pours)
    ← 0.1–0.2 mm prepreg
L4  Signal/components
```
- ✔ L1 tightly coupled to L2 GND; controlled impedance easy on L1.
- ✗ L3/L4 references L3 power (OK if well decoupled; the return current transfers through decoupling caps), and L2–L3 plane
  capacitance is poor because they're far apart.
- **Alternative (better EMC):** L1 Sig, L2 GND, L3 GND, L4 Sig with power routed as pours on signal layers. Both signal layers reference ground.
  Many experienced designers prefer this for mixed-signal and research boards.

### 6 layers
```
Option A (balanced, 3 routing layers)     Option B (dense, 4 routing layers)
L1 Sig                                     L1 Sig
L2 GND                                     L2 GND
L3 Sig  (stripline: GND above, PWR below)  L3 Sig  ┐ "dual stripline": route L3 horizontal,
L4 PWR                                     L4 Sig  ┘ L4 vertical, keep the L3–L4 gap thick
L5 GND                                     L5 GND
L6 Sig                                     L6 Sig   (power as pours on signal layers)
```
- **Option A** (**Sig / GND / Sig / PWR / GND / Sig**) is the usual default. Every signal layer is next to a plane, and L3 sits
  close to L2 GND (thin dielectric on that side). The L4 PWR / L5 GND pair gives some plane capacitance.
- **Option B** trades plane capacitance for routing density. Adjacent signal layers L3/L4 need orthogonal routing and a thick
  dielectric between them to limit broadside crosstalk. Power is delivered via pours, so decoupling matters more.

### 8 layers (good for dense digital / FPGA)
```
L1 Sig   L2 GND   L3 Sig   L4 PWR   L5 GND   L6 Sig   L7 GND   L8 Sig
```
Or with a tightly coupled PWR/GND pair in the middle for PDN.

## 18.3 Materials

| Material | εr (@1 GHz) | Df | Tg | Use |
|----------|-------------|-----|-----|-----|
| Standard FR-4 (e.g. Isola 370HR, Shengyi S1000-2) | ~4.0–4.5 | ~0.015–0.02 | 150–180 °C | General; fine to a few Gbps over short runs |
| Mid-loss (Isola FR408HR, Panasonic Megtron 4) | ~3.6–3.8 | ~0.008–0.01 | 180–200 °C | 5–10 Gbps |
| Low-loss (Megtron 6, Isola I-Speed/Tachyon) | ~3.3–3.6 | ~0.002–0.005 | High | 25+ Gbps |
| Rogers RO4350B | 3.48 | 0.0037 | >280 °C | RF/microwave, **can be hybrid with FR-4** (RF layer only) |
| PTFE (RT/duroid) | 2.2 | 0.0009 | — | mmWave; hard to fabricate |
| Polyimide | ~3.4 | ~0.002–0.01 | — | Flex circuits |

⚠️ εr **depends on frequency and resin content**. Thin prepregs with lots of resin have lower εr. Use the fab's numbers for their specific glass style
(106, 1080, 2116, 7628...).

## 18.4 Working with your fab

🏭 **Industry practice:**
1. Draft your desired stackup (layer order, approximate thicknesses, impedance targets, total thickness).
2. Send it to the fab as a **stackup request**. The fab responds with their actual materials, glass styles, and **the widths they'll
   use to hit your impedances**. They may adjust trace widths slightly in CAM.
3. Put the approved stackup and **impedance table** in the fab drawing: "50 Ω ±10% SE on L1/L6, w = 0.12 mm ref L2/L5; 90 Ω ±10% diff..."
4. Order **impedance coupons** (test structures on the panel) for controlled impedance jobs.

Budget fabs (JLCPCB, PCBWay) publish their fixed stackups with impedance calculators. **Design to their stackup** instead of inventing your own.

## 18.5 🛠️ Altium Layer Stack Manager (`D`, `K`)

1. **Add layers:** right-click → Insert layer above/below (Signal, Plane, Core, Prepreg).
2. **Materials:** click the Material cell → Material Library (you can add your fab's materials with εr/Df).
3. **Symmetry:** the *Stack Symmetry* checkbox enforces mirrored thicknesses.
4. **Impedance tab:** add profiles (Single/Differential), pick target Z, and pick reference layers per signal layer. Width/gap are solved per layer.
5. **Via types tab:** define through, blind, buried, microvia spans (for HDI).
6. **Stackup documentation:** the stackup table can be placed in Draftsman (Place » Layer Stack Table) for the fab drawing.
7. **Board thickness:** shown at the bottom. Target 1.6 mm ±10% unless you have a reason.

## 18.6 Plane design details

- **Anti-pads:** the clearance hole in a plane around a via that doesn't connect. Too big and neighbouring anti-pads merge into slots.
  Check plane layers after placement, especially under BGAs and connectors.
- **Pull-back from the board edge:** planes should pull back ~0.3–0.5 mm from the edge (manufacturing), and a power plane pulling back further than
  ground (the "20H rule", with a pullback of 20× the plane spacing) is claimed to reduce edge radiation. The benefit is debated and
  small at typical spacings. **Edge via stitching of ground planes** is the more effective technique.
- **Split power planes:** OK to split a *power* plane into regions for different rails, **as long as no signal referencing that plane crosses
  the split**. Keep signals over solid ground, or add stitching caps.
- **Copper thieving/balance:** fabs add non-functional copper dots in empty areas to even out plating. Agree to this on inner/outer layers unless it affects RF.

## Exercises
1. Design a 4-layer stackup for a board with USB 2.0 HS, a 24-bit ADC, and a buck converter. Which layer order would you pick, and why?
2. Download JLCPCB's (or your fab's) 4-layer stackup data and enter it into Altium's Layer Stack Manager with a 50 Ω and a 90 Ω profile.
3. Explain why an asymmetric stackup (e.g. 3 thin layers on top and one thick core at the bottom) might bow.

**Next:** [Chapter 19 — EMC/EMI Design](19-emc-emi.md)
