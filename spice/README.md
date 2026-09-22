# SPICE Examples

Small netlists that make the chapter concepts visible. They use plain SPICE3/ngspice syntax
(`.control` blocks are ngspice-specific; delete them to use the netlist elsewhere).

| File | Concept | Chapter |
|------|---------|---------|
| `01_rc_lowpass.cir` | −3 dB point, phase, time constant | 1, 4 |
| `02_transmission_line_reflection.cir` | Reflections; unterminated vs. series vs. parallel termination (lossless `T` line) | 16 |
| `03_decoupling_antiresonance.cir` | Capacitor bank impedance; ladder vs. same-value caps | 2, 14 |
| `04_ferrite_lc_resonance.cir` | Ferrite + ceramic cap resonance, and damping it | 2, 11 |
| `05_hotplug_ringing.cir` | Cable inductance + ceramic input caps → 2× overshoot at plug-in | 11 |

## Running with ngspice
```bash
ngspice 02_transmission_line_reflection.cir
```
Windows: download ngspice from https://ngspice.sourceforge.io/download.html, then run `ngspice.exe file.cir`.

## Running in Altium (Mixed-Signal Simulation)
Altium's simulator is SPICE-compatible, but it's schematic-driven:
1. Recreate the circuit on a schematic using parts from the **Simulation Generic Components** library
   (resistors, capacitors, inductors, `VSRC`/`ISRC`, and the lossless transmission line `LLTRA`).
2. Set source parameters (PULSE/AC magnitude) in the Properties panel.
3. **Simulate » Simulation Dashboard** → add *Transient* or *AC Sweep* → place probes → Run.
4. For the subcircuit-based examples, you can attach the `.subckt` text as a component model
   (Component Properties » Models » Add » Simulation » *Subcircuit*).

## Also worth installing
**LTspice** (free, ADI). It's the industry's everyday simulator and ships with switching-regulator models.
The same netlists load there with minor syntax edits (`.control` blocks are not supported; use `.tran`/`.ac`
directives and the waveform viewer instead).
