# Chapter 12 — Grounding and Return Paths

> **Mentor's note:** If you take one chapter from this guide into every design, take this one. "Ground"
> is the most misunderstood word in electronics. Ground is not a place where current goes to disappear.
> It's the **return conductor** of every circuit on the board, and it behaves like any other conductor.

---

## 12.1 Three truths

1. **Every current returns to its source.** The return path is part of the circuit.
2. **Return current takes the path of least *impedance*,** not least resistance. At DC that means least resistance.
   At high frequency it means least inductance.
3. **Ground is a conductor with impedance.** Any current through it creates a voltage difference between two
   "ground" points: V = I·Z_ground.

## 12.2 🧠 Where the return current actually flows

Take a trace over a solid plane.

- **At DC / low frequency** (roughly below ~10–100 kHz for typical boards), the return current spreads out across the plane
  along the **lowest-resistance** paths, roughly a straight line between source and load ground connections.
- **At high frequency** the return current concentrates **directly underneath the signal trace**, because that path
  encloses the smallest loop area, and so has the **lowest inductance**. The return current density falls off as
  ```
  J(x) ∝ 1 / (1 + (x/h)²)        x = lateral distance from trace, h = height above plane
  ```
  About 80% of the return current flows within ±3h of the trace centerline.

The crossover frequency where inductance dominates (ωL > R) is surprisingly low: typically in the **kHz range**. So
almost every digital signal edge (and switching regulator current) returns directly beneath its trace.

👉 See it: [`diagrams/return-path.html`](https://jeremiahhidayat.github.io/pcb-guide/diagrams/return-path.html). Toggle frequency and add a plane slot.

### What follows from this

| Rule | Physical reason |
|------|-----------------|
| **Don't route signals across splits or slots in the reference plane** | The return current has to detour around the gap. Loop area grows, inductance rises, and the slot radiates as a slot antenna |
| **Keep the reference plane continuous under high-speed traces** | Same |
| **When a signal changes layers, give its return a path too** | If the reference changes from GND (L2) to GND (L5), place a **ground stitching via** next to the signal via. If from GND to PWR, place a **stitching capacitor** nearby |
| **Via fields (anti-pads) can create "slots"** | A row of through-vias with large anti-pads can merge into a long slot in the plane. Check plane layers in single-layer mode (`Shift+S`) |
| **Traces near the board edge** | Returns are compressed and fields fringe out → more radiation. Keep high-speed traces ≥ 3–5h (or several mm) from the plane edge |

## 12.3 Ground impedance and ground noise

Any shared ground impedance **couples** circuits: this is *common-impedance coupling*.
```
  Power-hungry circuit (motor driver, 1 A pulses)
          │ I_noisy
  ────────┴───────────── shared ground trace (R + jωL) ─────────── regulator GND
          ▲
  Sensitive ADC GND connected here "sees" V = I_noisy · Z_shared as a signal
```
**Fix:** don't share return paths. Place parts so that noisy return currents don't flow through the ground area
under sensitive circuits. **With a solid plane, you control this through placement, not by cutting the plane.**

## 12.4 The split ground plane debate: AGND vs. DGND

Many datasheets say "connect AGND and DGND at one point." Here is what that actually means.

- Datasheet AGND/DGND **pins** are about *inside the chip*: they keep the chip's own digital return current off
  its analog bond wires. At the board level, most mixed-signal ADC vendors (ADI's MT-031, TI app notes) recommend:
  **connect both AGND and DGND pins to one solid ground plane directly underneath the ADC.**
- **Splitting the board's ground plane** creates problems when anything crosses the split (every SPI line from the MCU to the ADC
  crosses it!). Their return currents must detour to the single "star" connection point, and you've made a loop antenna.

### The modern recommendation (for most boards)
1. **Use one solid, unbroken ground plane.**
2. **Partition by placement:** analog section in one area, digital in another, power supplies in a third,
   with the ADC straddling the boundary between analog and digital.
3. Route analog signals only over the analog area and digital signals only over the digital area.
   Then the return currents stay in their own region naturally, **because they flow under their traces.**
4. Only split the plane when there's a specific reason (isolation barriers, very high-current motor returns with
   a known return path, chassis vs. signal ground) and **never route across the split.**

```
┌──────────────────────── one solid GND plane ────────────────────────┐
│  ┌──────────┐        ┌────────────────┐        ┌─────────────────┐   │
│  │ Analog   │  AIN   │   ADC (straddle│  SPI   │  Digital (MCU,  │   │
│  │ front end│───────►│   the boundary)│───────►│  USB, radio)    │   │
│  └──────────┘        └────────────────┘        └─────────────────┘   │
│                         ┌────────────┐                               │
│   (keep noisy SMPS away │  Buck SMPS │ with its own local ground     │
│    from analog)         └────────────┘ return area near power entry  │
└──────────────────────────────────────────────────────────────────────┘
```

## 12.5 Ground types and when they're genuinely separate

| Ground | What it is | Connect how |
|--------|-----------|-------------|
| **Signal ground (GND)** | Return for circuits | Solid plane |
| **Chassis / earth ground** | Metal enclosure / protective earth | Connect to GND at **one point near the I/O connectors**, often via a capacitor ± resistor (e.g. 1 MΩ ∥ 4.7 nF, or direct). ESD current should go to chassis, *not* through your circuits |
| **Isolated ground** | Other side of an isolator (digital isolator, isolated DC-DC) | **Never connected.** Keep creepage/clearance across the barrier (Chapter 29). Only a small Y-cap if EMC requires it |
| **Power ground (PGND)** | High-current return of an SMPS or motor | Same plane, but placed so the high current path is local. Some regulator datasheets ask for a single-point connect of PGND to AGND (their quiet feedback ground). Follow the datasheet for that IC |

## 12.6 Ground loops (the system-level version)

When two instruments connect to each other *and* each connects to mains earth, a loop forms. Magnetic fields
(transformers, mains wiring) induce current in it, and you see 50/60 Hz hum.

Fixes:
- Break the loop with **isolation** (isolated USB, isolated DC-DC + digital isolator, battery power, differential input stage).
- Use **differential measurements** (INA) so the ground difference becomes common-mode, which CMRR rejects.
- Cable shields: connect at one end for low-frequency hum, both ends for RF. Or one end direct + other end via a capacitor.

In a research lab setup (sensor board + USB to a PC + a bench supply + an oscilloscope), ground loops are common.
An isolated USB (e.g. ADuM3160/ADuM4160 isolator) can clean up your noise floor dramatically.

## 12.7 Ground bounce (a chip-level return path problem)
When many outputs switch at once, their return current shares the package's ground pins and bond wires (L ≈ 1–5 nH).
```
V_bounce = L_gnd · N · C_load · dV/dt / t_r   (≈ L · di/dt)
```
Mitigations: more ground pins/vias, lower drive strength or slew rate settings, series termination resistors,
low-inductance decoupling, fewer simultaneously switching outputs.

## 12.8 🛠️ In Altium: implementing solid grounds
- **Layer Stack Manager:** make the layer below the top a **plane layer** (negative) or a signal layer with a full polygon pour
  named `GND_L2`. Many engineers prefer *positive polygon pours* over negative planes because pours show you
  exactly what's there and handle voids clearly.
- **Plane view check:** `Shift+S` (single-layer mode) on the ground layer, zoomed out. You should see nearly solid copper.
  Look for islands, slivers, and via-antipad "slots".
- **Split planes** (if genuinely needed): draw **Place » Line** on the plane layer to split it, then double-click each region to
  assign a net. Name it clearly, and add a **keepout** so nothing gets routed across.
- **Net ties** to join separate ground nets at a single point (if you insist on separate net names such as AGND/GND for documentation).
  The Net Tie component type makes DRC accept the short.
- **Return path check:** In AD 22+, the **Signal Integrity » Return Path** rule (High Speed rules) lets you check that nets in
  a class have a continuous reference plane within an expansion distance. Use it on high-speed nets.
- **Via stitching:** **Tools » Via Stitching/Shielding » Add Stitching to Net**, grid ~ 2–5 mm near RF, ~10 mm general.

## Exercises
1. Estimate the loop inductance change when a 10 cm trace at 0.2 mm above a plane must detour 2 cm around a slot.
   (Use the diagram, and think in terms of loop area.)
2. Your ADC shows a 60 Hz tone that disappears on battery power. Explain it and propose two fixes.
3. Open a vendor ADC eval board layout (e.g. an AD7124 or ADS1262 EVM). Is its ground plane split? How is it partitioned?

**Next:** [Chapter 13 — Placement & Routing Strategy](13-placement-and-routing.md)
