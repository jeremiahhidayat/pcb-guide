# PCB Design From First Principles — An Altium-Based Field Guide

> *"Every trace is a transmission line, every capacitor is an inductor above some frequency, and every
> ground is a wire with resistance. The job is knowing when those facts matter."*

This repository is a structured, mentor-style course in printed circuit board (PCB) design. It starts
at **charge and voltage** and ends at **multi-gigabit stackups, EMC compliance, and production release**.
All the practical work is done in **Altium Designer**, but the physics is tool-agnostic.

It is written the way a senior EE would teach an intern: every rule of thumb is traced back to the
physics that produces it, so that when you meet a situation no rule covers, you can reason it out yourself.

---

## How this guide is organized

| Part | Theme | You will be able to... |
|------|-------|------------------------|
| **[Part 1 — Circuit Fundamentals](docs/part1-fundamentals/)** | Physics & components | Analyze circuits, read datasheets, understand *real* (non-ideal) components |
| **[Part 2 — PCB Foundations](docs/part2-pcb-foundations/)** | What a PCB is + Altium basics | Take a simple circuit from schematic to fabricated board in Altium |
| **[Part 3 — Intermediate Design](docs/part3-intermediate/)** | Power, grounding, layout, sensors | Design robust 2–4 layer mixed-signal boards for research instruments |
| **[Part 4 — Advanced Design](docs/part4-advanced/)** | SI, PI, high-speed, EMC, RF, thermal | Design controlled-impedance, high-speed, low-noise boards |
| **[Part 5 — Industry Practice](docs/part5-industry/)** | Reviews, DFM, bring-up, release | Work like a professional hardware team |
| **[Appendices](docs/appendices/)** | Reference | Formula cheat sheet, Altium shortcuts, glossary, reading list |

Supporting material:

| Folder | Contents |
|--------|----------|
| [`diagrams/`](diagrams/) | **Interactive HTML diagrams** (open in a browser): RC filter Bode plots, return-current paths, transmission-line reflections, decoupling impedance, stackups, buck converter hot loops, and more. Start at [`diagrams/index.html`](diagrams/index.html), or view them live at **https://jeremiahhidayat.github.io/pcb-guide/diagrams/**. |
| [`tools/`](tools/) | Python calculators: trace width (IPC-2221/2152), microstrip/stripline impedance, via parasitics, decoupling networks, tolerance Monte Carlo, thermal, buck converter design. |
| [`spice/`](spice/) | ngspice / Altium Mixed-Sim netlists that let you *see* the concepts: ringing, reflections, capacitor anti-resonance, filter response. |
| [`altium-scripts/`](altium-scripts/) | DelphiScript utilities for Altium (via reports, design-rule presets, etc.). |
| [`projects/`](projects/) | Three guided build projects of increasing difficulty. |
| [`checklists/`](checklists/) | Printable schematic, layout, and fab-release review checklists used in industry. |

---

## Suggested learning path

```
Week 1-2   Part 1 (ch 01-05)      Circuit physics, components, datasheets
Week 3     Part 2 (ch 06-09)      PCB anatomy, Altium setup, schematic + libraries
Week 4-5   Project 1              2-layer USB-C powered 3.3 V regulator + LED + test points
Week 6-8   Part 3 (ch 11-15)      Power, grounding, layout, decoupling, mixed-signal
Week 9-11  Project 2              4-layer sensor/DAQ board (MCU + precision ADC + analog front end)
Week 12+   Part 4 (ch 16-22)      SI/PI, high-speed, stackups, EMC, thermal, RF
           Project 3              6-layer board with USB 2.0 HS, buck converter, controlled impedance
Ongoing    Part 5 (ch 23-30)      Apply to every board you design from now on
```

Don't skip Part 1 because it "looks basic." Nearly every layout mistake I have seen from a new engineer
comes from a hole in the fundamentals: not truly believing that current flows in loops, or that a
capacitor has inductance.

---

## Table of contents

### Part 1 — Circuit Fundamentals
1. [Charge, Voltage, Current & the Laws That Govern Them](docs/part1-fundamentals/01-charge-voltage-current.md)
2. [Passive Components — Ideal vs. Real](docs/part1-fundamentals/02-passive-components.md)
3. [Semiconductors — Diodes, BJTs, MOSFETs](docs/part1-fundamentals/03-semiconductors.md)
4. [Op-Amps and Analog Building Blocks](docs/part1-fundamentals/04-op-amps-and-analog-blocks.md)
5. [Reading Datasheets Like an Engineer](docs/part1-fundamentals/05-reading-datasheets.md)

### Part 2 — PCB Foundations (Altium)
6. [What a PCB Physically Is](docs/part2-pcb-foundations/06-what-is-a-pcb.md)
7. [Setting Up Altium Designer Properly](docs/part2-pcb-foundations/07-altium-environment-setup.md)
8. [Schematic Capture as Engineering Communication](docs/part2-pcb-foundations/08-schematic-capture.md)
9. [Libraries, Symbols & Footprints](docs/part2-pcb-foundations/09-libraries-and-footprints.md)
10. [Your First Board: End-to-End Walkthrough](docs/part2-pcb-foundations/10-first-board-walkthrough.md)

### Part 3 — Intermediate Design
11. [Power Supply Design (LDOs, Bucks, Protection)](docs/part3-intermediate/11-power-supply-design.md)
12. [Grounding and Return Paths](docs/part3-intermediate/12-grounding-and-return-paths.md)
13. [Component Placement & Routing Strategy](docs/part3-intermediate/13-placement-and-routing.md)
14. [Decoupling and the Power Delivery Network](docs/part3-intermediate/14-decoupling-and-pdn.md)
15. [Mixed-Signal, Sensors & Precision Analog](docs/part3-intermediate/15-mixed-signal-and-precision-analog.md)

### Part 4 — Advanced Design
16. [Transmission Lines & Signal Integrity](docs/part4-advanced/16-transmission-lines-and-signal-integrity.md)
17. [High-Speed Digital Design](docs/part4-advanced/17-high-speed-digital.md)
18. [Stackup Design](docs/part4-advanced/18-stackup-design.md)
19. [EMC / EMI Design](docs/part4-advanced/19-emc-emi.md)
20. [Thermal Design](docs/part4-advanced/20-thermal-design.md)
21. [RF Fundamentals for PCB Designers](docs/part4-advanced/21-rf-fundamentals.md)
22. [HDI, Flex, Rigid-Flex & Advanced Fabrication](docs/part4-advanced/22-hdi-flex-advanced-fab.md)

### Part 5 — Industry Practice
23. [Design Reviews](docs/part5-industry/23-design-reviews.md)
24. [DFM, DFA and DFT](docs/part5-industry/24-dfm-dfa-dft.md)
25. [Manufacturing Outputs & Fab Release](docs/part5-industry/25-manufacturing-outputs.md)
26. [Board Bring-Up & Debugging](docs/part5-industry/26-bring-up-and-debug.md)
27. [Component Selection & Supply Chain](docs/part5-industry/27-component-selection-supply-chain.md)
28. [Version Control, Revisions & Release Process](docs/part5-industry/28-version-control-and-release.md)
29. [Safety, Compliance, Creepage & Clearance](docs/part5-industry/29-safety-and-compliance.md)
30. [PCB Design in a Research Lab](docs/part5-industry/30-research-lab-workflow.md)

### Appendices
- [A — Formula Cheat Sheet](docs/appendices/A-formula-cheatsheet.md)
- [B — Altium Shortcuts & Menu Map](docs/appendices/B-altium-shortcuts.md)
- [C — Glossary](docs/appendices/C-glossary.md)
- [D — Further Reading](docs/appendices/D-further-reading.md)

---

## Using the tools

```bash
cd tools
python -m pip install -r requirements.txt    # numpy + matplotlib (optional; core calc has no deps)

python pcb_calc.py trace-width --current 3 --temp-rise 10 --copper-oz 1 --layer external
python pcb_calc.py microstrip --width-mm 0.3 --height-mm 0.2 --er 4.1
python pcb_calc.py via --drill-mm 0.3 --length-mm 1.6
python pcb_calc.py target-z --voltage 1.0 --ripple-pct 3 --step-current 2
python decoupling_plot.py                     # plots impedance of a capacitor bank
python tolerance_montecarlo.py                # worst-case vs statistical divider analysis
```

To view the diagrams, open `diagrams/index.html` in any browser. To host them, enable
**GitHub Pages** (Settings → Pages → Deploy from branch → `main` / root), then browse to
`https://<you>.github.io/<repo>/diagrams/`.

To run the SPICE decks, install [ngspice](https://ngspice.sourceforge.io/) and run `ngspice spice/<file>.cir`,
or import them into Altium's Mixed-Signal Simulation (see [spice/README.md](spice/README.md)).

---

## Conventions used in this guide

- 🧠 **First principles** callouts derive a rule from physics.
- 🛠️ **In Altium** callouts give concrete menu paths and settings (written against Altium Designer 23–25;
  menu locations occasionally move between versions, but the names stay close).
- ⚠️ **Gotcha** callouts are mistakes I've seen cost real money or real weeks.
- 🏭 **Industry practice** callouts describe how professional teams do it.
- Units: I use **mm** for geometry, with **mil** (1 mil = 0.001 in = 0.0254 mm) where the industry does.
  Press `Q` in Altium to toggle between them.

## License

MIT for code. The written content is CC BY 4.0. Use it, fork it, teach with it.
