# Tools

First-principles calculators. Read the source: every function says where its formula comes from and when it stops being valid.

| Script | Dependencies | What it does |
|--------|--------------|--------------|
| `pcb_calc.py` | none | Trace width (IPC-2221), trace/sheet resistance, microstrip / stripline / differential impedance, via parasitics, capacitor impedance & SRF, target impedance, feedback-divider E-series search, RC corner, buck converter first pass, resistor noise, junction temperature, edge/critical length, skin depth, reflection coefficient |
| `decoupling_plot.py` | numpy, matplotlib | Impedance vs frequency of capacitor banks; reports anti-resonance peaks |
| `tolerance_montecarlo.py` | numpy (matplotlib for `--plot`) | Worst-case vs statistical tolerance of dividers and regulator feedback networks |

```bash
python -m pip install -r requirements.txt
python pcb_calc.py --help
python pcb_calc.py <command> --help
```

## Example session

```text
$ python pcb_calc.py microstrip --width-mm 0.3 --height-mm 0.2 --er 4.1
Z0 = 55.7 Ω   ε_eff = 3.09
Delay = 5.87 ps/mm (149 ps/in)
C = 0.105 pF/mm   L = 0.327 nH/mm
IPC-2141 formula (comparison): 54.5 Ω

$ python pcb_calc.py buck --vin 12 --vout 3.3 --iout 2 --fsw 1e6
Duty cycle D           = 0.275
L (calculated)         = 3.99 µH  → chosen 4.7 µH
Inductor ripple ΔI_L   = 0.509 A ; peak = 2.255 A (choose I_sat above IC current limit)
C_in RMS current       = 0.893 A
V_out ripple (C=22 µF effective) ≈ 5.44 mV

$ python pcb_calc.py edge --rise-time 1e-9
Knee frequency (0.5/tr): 500 MHz   BW (0.35/tr): 350 MHz
Spatial length of edge: 173.1 mm → treat traces longer than ~28.8 mm as transmission lines (t_r/6 criterion)
```

## Accuracy notes
- **Impedance:** closed-form formulas are ±2–10%. For anything you fabricate, use Altium's Layer Stack Manager solver
  and your fab's stackup/impedance report.
- **Trace current:** IPC-2221 is the legacy chart. IPC-2152 is more accurate and usually *less* conservative for internal
  layers with nearby planes.
- **Buck:** first-pass sizing only. Loop compensation, current limit, and the IC's datasheet requirements still apply.
- On Windows terminals that don't show Unicode (Ω, µ), set `PYTHONIOENCODING=utf-8`.
