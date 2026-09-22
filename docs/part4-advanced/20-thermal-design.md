# Chapter 20 — Thermal Design

> **Mentor's note:** Heat is energy that has to reach the air somehow. Think of it as a circuit: power is
> current, temperature is voltage, thermal resistance is resistance. Then use the same analysis you use for circuits.

---

## 20.1 The thermal circuit

```
  P (W) ──► [θ_JC] ──► [θ_CB (solder/pad)] ──► [θ_BA (board to air)] ──► T_ambient
  T_j                 T_case                  T_board
T_j = T_a + P · (θ_JC + θ_CB + θ_BA)      units: °C/W
```

| Quantity | Meaning |
|----------|---------|
| θ_JA | Junction-to-ambient on the **JEDEC test board** (not your board!). Useful only for comparisons |
| θ_JC(top/bot) | Junction to case top / bottom (exposed pad) |
| **Ψ_JT, Ψ_JB** | Thermal *characterization parameters*: estimate T_j from a measured T_top or T_board. **Use these with a thermocouple/IR camera on your prototype** |

JEDEC θ_JA is measured on a 76 × 114 mm, 4-layer (2s2p) board with 2 oz outer copper, which is often much more copper than your board. Expect worse.

## 20.2 🧠 Spreading heat with copper

Copper conducts heat ~1000× better than FR-4 (k_Cu ≈ 390 W/m·K vs. k_FR4 ≈ 0.3 W/m·K through the thickness and ~0.8 W/m·K in-plane).
- **Heat spreads laterally in copper planes** and then leaves through the board surface area.
- **Thermal vias** carry heat *through* the board from an exposed pad to inner and bottom planes.

Thermal resistance of one via barrel (conduction along the plating):
```
R_via = L / (k_Cu · A_plating)       A_plating = π·(d_outer² − d_inner²)/4
0.3 mm drill, 25 µm plating, 1.6 mm long:
A = π/4·(0.35² − 0.30²) mm² = 0.0255 mm²  →  R = 1.6e-3 / (390 × 0.0255e-6) ≈ 161 °C/W per via
10 vias in parallel → ~16 °C/W.   Filling with conductive epoxy/copper lowers this further.
```
So an array of vias under a QFN exposed pad into a big ground plane is the main thermal path for most power ICs.

### Practical thermal-pad via array
- 0.3 mm drill, 1.0–1.2 mm pitch, as many as fit (e.g. 3×3 to 5×5 under a 3–5 mm pad).
- Avoid solder wicking: **tent from the bottom** (mask over the via on the far side), use small vias (≤ 0.3 mm), or pay for **filled and capped (VIPPO)** vias.
- Connect the vias **directly** (no thermal relief) to inner planes. Thermal reliefs defeat the purpose.
- Big copper areas on L2/L(n) and the bottom connected to the pad.

## 20.3 Copper area vs. θ_JA (a feel)
For a SOT-223 / DPAK-class part on FR-4, a rough guide:

| Top copper area connected to tab | θ_JA (approx.) |
|---------------------------------|----------------|
| Minimum pad | 100–150 °C/W |
| 1 cm² | ~70 °C/W |
| 4 cm² | ~50 °C/W |
| 4 cm² + vias to bottom plane | ~35–40 °C/W |

Diminishing returns set in past a few cm², because the heat can't spread through thin copper much further.
**Doubling copper weight (2 oz) helps spreading significantly.**

## 20.4 Current-carrying traces heat up too
See Chapter 13 (IPC-2152). High-current paths on inner layers run hotter (less convection). Put high-current routes on outer layers or use multiple layers in parallel.

## 20.5 Other thermal considerations
- **Component derating:** electrolytic caps lose life ×2 per 10 °C (Arrhenius). Keep them away from hot parts.
- **Thermal gradients** affect precision analog (Chapter 15): keep references and input stages away from regulators.
- **Solderability:** big copper pours make hand-soldering hard and cause cold joints on through-hole parts. Thermal reliefs on non-thermal pads.
- **Airflow and orientation:** tall parts upstream block airflow. Vertical boards convect better.
- **Enclosure:** a sealed plastic box traps heat. The internal ambient can be 10–20 °C above room.

## 20.6 Verifying
- **Hand estimate** (above) → **simulation** (Altium doesn't include full thermal simulation, but you can export to Ansys Icepak, Simcenter FloTHERM, Cadence Celsius) →
  **measure** on the prototype: an IR camera (tape a small piece of Kapton or black paint over shiny metal for emissivity) or thermocouples, and
  use Ψ_JT to estimate T_j.
- Test at max ambient and max load, in the enclosure.

## 20.7 🛠️ In Altium
- **Polygon connect rule for thermal pads:** create a rule `Polygon Connect Style` with scope `IsPad and InComponent('U3')` (or `HasFootprint('QFN*')` for EP pads by name) → *Direct Connect*.
- **Via arrays:** place one via, then copy with **Edit » Paste Special » Paste Array**; or use **Tools » Via Stitching** restricted to a region/polygon.
- **Tented vias:** in via properties, set Solder Mask *Tented* on the bottom side only (Solder Mask Expansion → tented top/bottom settings).
- **PDN Analyzer** shows current density, which highlights hot spots in narrow copper necks.

## Exercises
1. A buck IC dissipates 1.2 W, θ_JA (JEDEC) = 40 °C/W, your board has half the copper. Estimate T_j at 50 °C ambient, and how many thermal vias you would add.
2. Why do thermal reliefs make sense for a through-hole connector pin on a ground plane, but not for an exposed thermal pad?

**Next:** [Chapter 21 — RF Fundamentals](21-rf-fundamentals.md)
