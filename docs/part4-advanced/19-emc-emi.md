# Chapter 19 — EMC / EMI Design

> **Mentor's note:** EMC failures are expensive because you find them late: at the test lab, after tooling,
> with a launch date looming. The good news is that EMC mostly follows from what you already learned:
> small loops, continuous return paths, controlled edges, and filtered cables.

---

## 19.1 Terminology
- **EMI** (interference): unwanted energy. **Emissions**: what your product radiates or conducts. **Immunity/susceptibility**: how well
  it tolerates what others emit.
- **EMC** (compatibility): passing both.
- Standards: **FCC Part 15** (US, Class A industrial / Class B residential), **CISPR 32** (multimedia emissions), **CISPR 11** (ISM equipment,
  which covers many lab instruments), **IEC 61326-1** (lab/measurement equipment EMC), **IEC 61000-4-x** immunity tests (ESD -4-2,
  radiated -4-3, EFT -4-4, surge -4-5, conducted -4-6).

## 19.2 🧠 How boards radiate: differential mode vs. common mode

### Differential-mode radiation
A current loop (signal + return) is a small loop antenna:
```
E ≈ 1.316×10⁻¹⁴ · f² · A · I / r    (V/m; f in Hz, A loop area in m², I in A, r in m)
```
It scales with **f²** and **loop area**. Mitigation: small loops (solid planes, return path directly under traces), slower edges.

### Common-mode radiation (usually the one that fails you)
When a cable attached to the board carries a small **common-mode current** (the same direction on all conductors, returning via
stray capacitance to the environment), the cable acts as a monopole antenna:
```
E ≈ 1.257×10⁻⁶ · f · L · I_cm / r
```
**Just 5 µA of common-mode current on a 1 m cable at 100 MHz gives ≈ 210 µV/m (46 dBµV/m) at 3 m, which exceeds the FCC Class B
limit** (150 µV/m = 43.5 dBµV/m at 3 m for 88–216 MHz). Compare that with the milliamps of *differential* signal current on the same cable.
Common-mode currents come from:
- **Ground voltage differences** between where the cable connects and the rest of the board (ground plane noise voltage drives the cable).
- Signals with imbalanced return paths (a split plane forces return current to take a detour, and some goes out the cable).
- Poor diff-pair symmetry.

Mitigations:
1. **Put all connectors on one edge** (the same "ground potential" region) so there's no ground voltage between cables.
2. **Common-mode chokes** on cables and diff pairs (USB, Ethernet, CAN).
3. **Filter every signal leaving the board** (RC, ferrite, feed-through caps) at the connector.
4. **Bond cable shields 360° to the chassis** at the entry point. A "pigtail" shield wire is inductive and useless at high frequency.
5. A **chassis ground** region at the I/O edge, connected to the enclosure.

## 19.3 The EMC design checklist (by source)

| Source | What to do |
|--------|------------|
| Switching regulators | Tiny hot loops (Chapter 11), small SW node, shielded inductors, spread-spectrum, input π-filter, snubber on SW (RC) if ringing |
| Clocks | Lowest frequency and slowest edge that works, series termination, stripline routing, spread-spectrum clocks where tolerated |
| Digital I/O edges | Reduce drive strength / slew in firmware; series R (22–100 Ω) |
| Cables/connectors | Filter at the connector, CM chokes, ESD/TVS, shielded cables bonded 360° |
| Board edges | Keep high-speed traces away from edges; ground via stitching fence along the edge every ~λ/20 of max frequency of concern |
| Plane resonances | Stitch ground planes together with vias regularly; decoupling reduces plane resonance Q |
| Heatsinks | Large floating metal = antenna. Ground it (with several connections) |
| Unused MCU pins | Configure as outputs low or inputs with pulls, not floating |

Via stitching spacing: λ/20 at 1 GHz on FR-4 (λ = c/(f√εr) ≈ 146 mm → λ/20 ≈ 7 mm). A common practice is 5–10 mm stitching near edges and between pours.

## 19.4 Immunity: ESD, EFT, surge

- **ESD (IEC 61000-4-2):** ±8 kV contact / ±15 kV air discharge at user-touchable points. Rise time < 1 ns, peak ~30 A.
  - TVS arrays at every external connector, **first thing the signal meets**, with short, wide connections to ground/chassis.
  - Route: connector pin → TVS pad → then on to the circuit (don't branch off to the TVS with a stub).
  - Keep sensitive traces away from the board edge and from ESD entry points.
  - Series resistors or ferrites after the TVS add more protection.
- **EFT / burst:** fast transients on power and long I/O cables. Filter at the entry point (CM choke + caps).
- **Surge:** energetic transients (lightning-induced) on long lines. TVS rated for the surge energy (e.g. SMBJ/SMCJ), gas discharge tubes,
  series impedance.

## 19.5 Filtering at the connector

```
 Connector ─┬─[Ferrite/CM choke]─┬─[R]─► to circuit
            │                    │
         [TVS]                 [C] (100 pF – 1 nF, to chassis/GND at the connector)
            │                    │
 Chassis/GND at the edge ────────┘
```
- The filter capacitor's ground must be the **quiet** ground at the connector (or chassis), not ground somewhere in the middle of the board.
- A **π-filter** (C-L-C) is common on power inputs.
- Feed-through capacitors or filtered connectors for extreme cases.

## 19.6 Pre-compliance testing (cheap and valuable)

You don't need a chamber to find most problems:
- **Near-field probes** (H-field loops, E-field stubs; commercial sets or DIY) + a **spectrum analyzer** (even an inexpensive one, e.g. Siglent/Rigol).
  Scan the board: SMPS, clocks, cables. Find the source frequency and location.
- **Current probe** (clamp) on cables measures common-mode current. It's the best predictor of radiated emissions.
  (Use the E-field formula above to convert I_cm to field strength.)
- **LISN** for conducted emissions on power inputs.
- Compare "before and after" when you apply fixes. Relative measurements are very informative even in a noisy lab.

## 19.7 🛠️ In Altium: EMC-oriented features
- **Via Stitching / Shielding:** Tools » Via Stitching/Shielding » *Add Shielding to Net* (fence along a trace) and *Add Stitching to Net* (grid).
- **Return Path rule** (High Speed rules, recent versions) checks that high-speed nets stay over their reference plane.
- **Net class for "edge-sensitive" nets** + a Room/keep-out rule keeping them ≥ N mm from the board edge
  (e.g. a Clearance rule between `InNetClass('FAST')` and the board outline, or a keep-out region along the edge).
- **3D clearance checks** for shield cans and enclosure fit (import the enclosure STEP to check the board fits).

## 19.8 Design review questions for EMC
1. Where do the highest di/dt loops live, and how small are they?
2. Is there any signal crossing a plane gap or referencing a different plane after a layer change without a stitch?
3. What leaves the board on each cable, and how is it filtered?
4. Where does ESD current go when someone touches the connector shell?
5. Do the cables all attach to one region of the board?

## Exercises
1. Using the common-mode formula, how much CM current on a 0.5 m USB cable at 480 MHz gives 40 dBµV/m at 3 m?
2. Place a near-field probe over a buck regulator's inductor and SW node (if you have access). Compare with the input capacitor loop.
3. Mark the ESD current path on your Project 1 board. Is it short?

**Next:** [Chapter 20 — Thermal Design](20-thermal-design.md)
