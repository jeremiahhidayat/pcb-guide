# Appendix A — Formula Cheat Sheet

Every formula below is implemented in [`tools/pcb_calc.py`](../../tools/pcb_calc.py).

## Constants

| | |
|---|---|
| c | 299.79 mm/ns (11.8 in/ns) |
| ε₀ | 8.854 pF/m |
| µ₀ | 4π×10⁻⁷ H/m (1.257 µH/m) |
| k_B | 1.381×10⁻²³ J/K;  4kT at 300 K = 1.656×10⁻²⁰ J |
| ρ_Cu | 1.72×10⁻⁸ Ω·m (20 °C), +0.393%/°C |
| 1 oz Cu | 34.8 µm (1.37 mil);  sheet R ≈ 0.49 mΩ/□ |
| 1 mil | 25.4 µm |

## Circuit basics

| Quantity | Formula |
|----------|---------|
| Ohm / power | V = IR, P = VI = I²R = V²/R |
| Divider | Vout = Vin·R2/(R1+R2), R_th = R1‖R2 |
| RC corner | f_c = 1/(2πRC), τ = RC, ENBW(1-pole) = (π/2)f_c |
| N-bit settling | t ≈ N·ln2·τ ≈ 0.69·N·τ |
| Capacitor/inductor | i = C dv/dt, v = L di/dt, \|Z_C\| = 1/(2πfC), \|Z_L\| = 2πfL |
| LC resonance | f = 1/(2π√(LC)) |
| Real cap impedance | \|Z\| = √(ESR² + (ωESL − 1/ωC)²) |
| dB | 20·log(V2/V1), 10·log(P2/P1); dBm = 10·log(P/1 mW) |
| Thermal noise | v_n = √(4kTRB); 1 kΩ → 4.07 nV/√Hz |
| RSS noise | e_tot = √(Σ eᵢ²) |
| Crystal load caps | C_each = 2(C_L − C_stray) |

## Semiconductors

| Quantity | Formula |
|----------|---------|
| Diode | I = I_S(e^(V/nV_T) − 1), V_T ≈ 25.9 mV; V_F tempco ≈ −2 mV/°C |
| MOSFET losses | P_cond = I²R_DS(on); P_sw ≈ ½·V·I·(t_r+t_f)·f; P_gate = Q_g·V_drv·f |
| LDO loss | P = (Vin − Vout)·I_out |
| Junction temp | T_j = T_a + P·θ_JA |

## Buck converter

| Quantity | Formula |
|----------|---------|
| Duty | D = Vout/Vin |
| Inductor ripple | ΔI_L = (Vin − Vout)·D/(L·f_sw) |
| Output ripple | ΔV ≈ ΔI_L/(8·f_sw·C) + ΔI_L·ESR |
| Input cap RMS | I_rms = I_out·√(D(1−D)) |
| Feedback divider | Vout = Vref·(1 + R_top/R_bot) |

## PCB conductors

| Quantity | Formula |
|----------|---------|
| Trace resistance | R = ρL/(w·t) = R_□·(L/w) |
| IPC-2221 current | I = k·ΔT^0.44·A^0.725 (A in mil²; k = 0.048 ext, 0.024 int) |
| Skin depth | δ = √(ρ/(πfµ₀)); Cu: 66 mm/√f → 2.1 µm @ 1 GHz, 8.5 mm @ 60 Hz |
| Plane capacitance | C = ε₀εr·A/d (≈ 38 pF/cm² at 0.1 mm, εr 4.3) |
| Via inductance | L ≈ 5.08·h·[ln(4h/d) + 1] nH (inches) ≈ 1.3 nH for 1.6 mm/0.3 mm |
| Via capacitance | C ≈ 1.41·εr·T·D1/(D2 − D1) pF (inches) |
| Via thermal R | R = L/(k_Cu·A_plating); k_Cu ≈ 390 W/m·K |

## Signal integrity

| Quantity | Formula |
|----------|---------|
| Knee frequency | f_knee ≈ 0.35/t_r (BW) … 0.5/t_r |
| Velocity | v = c/√ε_eff. FR-4 microstrip (ε_eff ≈ 3): ~170 mm/ns ≈ 147 ps/in; stripline (εr ≈ 4.1): ~148 mm/ns ≈ 172 ps/in |
| Critical length | L_crit ≈ t_r·v/6 |
| Z0 (lossless) | Z0 = √(L/C);  C/len = t_pd/Z0;  L/len = t_pd·Z0 |
| Microstrip (IPC-2141) | Z0 ≈ 87/√(εr+1.41)·ln(5.98h/(0.8w+t)) |
| Stripline (IPC-2141) | Z0 ≈ 60/√εr·ln(1.9b/(0.8w+t)) |
| Diff microstrip (approx) | Z_diff ≈ 2Z0(1 − 0.48e^(−0.96s/h)) |
| Reflection | Γ = (Z_L − Z0)/(Z_L + Z0);  RL = −20log\|Γ\|; VSWR = (1+\|Γ\|)/(1−\|Γ\|) |
| Series termination | R_s = Z0 − R_driver |
| Via stub resonance | f = c/(4·L_stub·√εr) |
| Wavelength | λ = c/(f√ε_eff); stitching ≤ λ/20 |
| Crosstalk vs spacing | ∝ 1/(1 + (s/h)²) |
| Return current spread | J(x) ∝ 1/(1 + (x/h)²); ~80% within ±3h |

## PDN / EMC

| Quantity | Formula |
|----------|---------|
| Target impedance | Z_t = V·ripple%/ΔI |
| Ground bounce | V = L·di/dt |
| DM radiation | E ≈ 1.316×10⁻¹⁴·f²·A·I/r (V/m) |
| CM radiation | E ≈ 1.257×10⁻⁶·f·L·I_cm/r (V/m) |
| ADC | SNR_ideal = 6.02N + 1.76 dB; ENOB = (SINAD − 1.76)/6.02; SNR_jitter = −20log(2πf·t_j) |
