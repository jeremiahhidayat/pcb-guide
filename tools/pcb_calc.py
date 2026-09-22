#!/usr/bin/env python3
"""
pcb_calc.py — First-principles PCB design calculators (no third-party dependencies).

Every function documents the physics / standard it comes from so you can read the code
as a worked example. Treat results as engineering ESTIMATES: for controlled impedance,
confirm with a 2D field solver (Altium Layer Stack Manager → Impedance tab) and your fab.

Usage examples:
    python pcb_calc.py trace-width --current 3 --temp-rise 10 --copper-oz 1 --layer external --length-mm 50
    python pcb_calc.py microstrip --width-mm 0.30 --height-mm 0.20 --er 4.1
    python pcb_calc.py stripline --width-mm 0.15 --b-mm 0.40 --er 4.1
    python pcb_calc.py diff-microstrip --width-mm 0.15 --gap-mm 0.15 --height-mm 0.1 --er 4.1
    python pcb_calc.py via --drill-mm 0.3 --length-mm 1.6 --pad-mm 0.6 --antipad-mm 1.0 --er 4.3
    python pcb_calc.py cap --c 100e-9 --esl 0.5e-9 --esr 0.02 --freq 1e6 10e6 100e6
    python pcb_calc.py target-z --voltage 1.0 --ripple-pct 3 --step-current 2
    python pcb_calc.py divider --vref 0.8 --vout 3.3 --series E96
    python pcb_calc.py rc --r 1e3 --c 10e-9
    python pcb_calc.py buck --vin 12 --vout 3.3 --iout 2 --fsw 1e6 --ripple-pct 30
    python pcb_calc.py noise --r 1e3 --bw 10e3
    python pcb_calc.py thermal --power 0.5 --theta-ja 60 --ambient 40
    python pcb_calc.py edge --rise-time 1e-9 --er-eff 3.0
    python pcb_calc.py skin --freq 1e9
    python pcb_calc.py reflection --z0 50 --zl 75
"""

from __future__ import annotations

import argparse
import math
from typing import Iterable

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
C0 = 299_792_458.0            # speed of light, m/s
MU0 = 4e-7 * math.pi          # permeability of free space, H/m
EPS0 = 8.8541878128e-12       # permittivity of free space, F/m
K_B = 1.380649e-23            # Boltzmann constant, J/K
RHO_CU = 1.72e-8              # copper resistivity at 20 °C, ohm·m
ALPHA_CU = 0.00393            # copper temperature coefficient, 1/°C
OZ_TO_UM = 34.79              # 1 oz/ft² copper ≈ 34.79 µm (commonly rounded to 35 µm)
MIL = 25.4e-6                 # 1 mil in metres

E_SERIES = {
    "E6":  [1.0, 1.5, 2.2, 3.3, 4.7, 6.8],
    "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
    "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1],
    "E96": [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
            1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
            1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
            2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
            3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
            4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
            5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
            7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76],
}


# ---------------------------------------------------------------------------
# Formatting helper
# ---------------------------------------------------------------------------
_PREFIXES = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""),
             (1e-3, "m"), (1e-6, "µ"), (1e-9, "n"), (1e-12, "p"), (1e-15, "f")]


def eng(value: float, unit: str = "", digits: int = 3) -> str:
    """Format a number with an SI prefix: eng(4.7e-9, 'F') -> '4.70 nF'."""
    if value == 0 or not math.isfinite(value):
        return f"{value} {unit}".strip()
    mag = abs(value)
    for scale, prefix in _PREFIXES:
        if mag >= scale:
            return f"{value / scale:.{digits}g} {prefix}{unit}".strip()
    return f"{value:.{digits}e} {unit}".strip()


# ---------------------------------------------------------------------------
# 1. Trace width (IPC-2221) and trace resistance
# ---------------------------------------------------------------------------
def ipc2221_width(current_a: float, temp_rise_c: float, copper_oz: float,
                  external: bool = True) -> float:
    """
    Minimum trace width in metres from IPC-2221 (derived from 1950s NBS data).

        I = k · ΔT^0.44 · A^0.725       (A = cross-section in mil²)

    k = 0.048 for external layers, 0.024 for internal layers.
    IPC-2152 (2009) superseded this with better data; IPC-2221 is conservative for
    internal layers and roughly right for external ones. Good for a first estimate.
    """
    k = 0.048 if external else 0.024
    area_mil2 = (current_a / (k * temp_rise_c ** 0.44)) ** (1 / 0.725)
    thickness_mil = copper_oz * OZ_TO_UM * 1e-6 / MIL
    return area_mil2 / thickness_mil * MIL


def trace_resistance(width_m: float, length_m: float, copper_oz: float,
                     temp_c: float = 20.0) -> float:
    """R = ρ·L/A with copper's temperature coefficient applied."""
    rho = RHO_CU * (1 + ALPHA_CU * (temp_c - 20.0))
    thickness = copper_oz * OZ_TO_UM * 1e-6
    return rho * length_m / (width_m * thickness)


def sheet_resistance(copper_oz: float) -> float:
    """Ohms per square: ρ/t. 1 oz ≈ 0.49 mΩ/□."""
    return RHO_CU / (copper_oz * OZ_TO_UM * 1e-6)


# ---------------------------------------------------------------------------
# 2. Transmission line impedance
# ---------------------------------------------------------------------------
def microstrip(w: float, h: float, er: float, t: float = 0.0) -> dict:
    """
    Surface microstrip, closed-form (Hammerstad/Wheeler, as given in Pozar, *Microwave Engineering*).
    Accuracy ≈ 1-2% vs a field solver for zero-thickness copper; a simple Wheeler width
    correction is applied for trace thickness t. Ignores solder mask (which lowers Z by ~1-3 Ω).

    ε_eff accounts for the field being partly in air and partly in the dielectric.
    """
    if t > 0:  # effective width grows with thickness (Wheeler)
        w = w + (t / math.pi) * (1 + math.log(2 * h / t if w / h >= 1 / (2 * math.pi) else 4 * math.pi * w / t))
    u = w / h
    if u <= 1:
        e_eff = (er + 1) / 2 + (er - 1) / 2 * ((1 + 12 / u) ** -0.5 + 0.04 * (1 - u) ** 2)
        z0 = 60 / math.sqrt(e_eff) * math.log(8 / u + u / 4)
    else:
        e_eff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 / u) ** -0.5
        z0 = 120 * math.pi / (math.sqrt(e_eff) * (u + 1.393 + 0.667 * math.log(u + 1.444)))
    return _line_params(z0, e_eff)


def ipc2141_microstrip(w: float, h: float, er: float, t: float) -> float:
    """The classic (less accurate) IPC-2141 formula, valid 0.1 < w/h < 2.0. Shown for comparison."""
    return 87 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))


def _ellipk(k: float) -> float:
    """Complete elliptic integral of the first kind K(k) via the arithmetic-geometric mean."""
    a, b = 1.0, math.sqrt(1 - k * k)
    while abs(a - b) > 1e-15:
        a, b = (a + b) / 2, math.sqrt(a * b)
    return math.pi / (2 * a)


def stripline(w: float, b: float, er: float) -> dict:
    """
    Symmetric (centered) stripline, zero-thickness strip — exact conformal-mapping result (Cohn):

        Z0 = (30π/√εr) · K(k') / K(k),   k = sech(πw / 2b),  k' = tanh(πw / 2b)

    b = total dielectric thickness between the two reference planes.
    Real copper thickness lowers Z0 by a few ohms — check with a field solver.
    Field is entirely in dielectric → ε_eff = εr.
    """
    x = math.pi * w / (2 * b)
    k = 1 / math.cosh(x)
    kp = math.tanh(x)
    z0 = 30 * math.pi / math.sqrt(er) * _ellipk(kp) / _ellipk(k)
    return _line_params(z0, er)


def diff_microstrip(w: float, s: float, h: float, er: float, t: float = 0.0) -> dict:
    """
    Edge-coupled differential microstrip — IPC-2141 approximation:
        Z_diff ≈ 2·Z0·(1 − 0.48·exp(−0.96·s/h))
    Rough (±10%). Use a field solver for anything you will fabricate.
    """
    single = microstrip(w, h, er, t)
    zdiff = 2 * single["z0"] * (1 - 0.48 * math.exp(-0.96 * s / h))
    return {"z_single": single["z0"], "z_diff": zdiff, "z_odd": zdiff / 2, "e_eff": single["e_eff"]}


def _line_params(z0: float, e_eff: float) -> dict:
    v = C0 / math.sqrt(e_eff)             # propagation velocity
    tpd = 1 / v                           # s/m
    return {
        "z0": z0,
        "e_eff": e_eff,
        "velocity_m_per_s": v,
        "delay_ps_per_mm": tpd * 1e12 / 1e3,
        "delay_ps_per_in": tpd * 1e12 * 0.0254,
        "C_pF_per_mm": tpd / z0 * 1e12 / 1e3,   # C = tpd / Z0
        "L_nH_per_mm": tpd * z0 * 1e9 / 1e3,    # L = tpd · Z0
    }


# ---------------------------------------------------------------------------
# 3. Vias
# ---------------------------------------------------------------------------
def via_parasitics(drill_m: float, length_m: float, pad_m: float | None = None,
                   antipad_m: float | None = None, er: float = 4.3) -> dict:
    """
    Classic approximations (Howard Johnson, *High-Speed Digital Design*):
        L ≈ 5.08·h·[ln(4h/d) + 1]   nH  (h, d in inches)  — partial self-inductance of the barrel
        C ≈ 1.41·εr·T·D1/(D2 − D1)  pF  (T, D1, D2 in inches; D1 = pad, D2 = antipad)
    The real loop inductance depends on where the RETURN via/plane is — keep return vias close.
    """
    h_in = length_m / 0.0254
    d_in = drill_m / 0.0254
    out = {"L_nH": 5.08 * h_in * (math.log(4 * h_in / d_in) + 1)}
    if pad_m and antipad_m and antipad_m > pad_m:
        out["C_pF"] = 1.41 * er * h_in * (pad_m / 0.0254) / ((antipad_m - pad_m) / 0.0254)
        out["Z_via_ohm"] = math.sqrt(out["L_nH"] * 1e-9 / (out["C_pF"] * 1e-12))
    out["aspect_ratio"] = length_m / drill_m
    return out


# ---------------------------------------------------------------------------
# 4. Capacitors and PDN
# ---------------------------------------------------------------------------
def cap_impedance(c: float, esl: float, esr: float, f: float) -> float:
    """|Z| of a series R-L-C capacitor model."""
    w = 2 * math.pi * f
    return math.hypot(esr, w * esl - 1 / (w * c))


def srf(c: float, esl: float) -> float:
    return 1 / (2 * math.pi * math.sqrt(esl * c))


def target_impedance(voltage: float, ripple_pct: float, step_current: float) -> float:
    """Z_target = V·ripple / ΔI — the PDN must stay below this across the band of interest."""
    return voltage * ripple_pct / 100 / step_current


# ---------------------------------------------------------------------------
# 5. Resistor networks
# ---------------------------------------------------------------------------
def e_series_values(series: str) -> list[float]:
    base = E_SERIES[series]
    return [m * 10 ** d for d in range(0, 7) for m in base]


def nearest_e(value: float, series: str = "E96") -> float:
    return min(e_series_values(series), key=lambda v: abs(v - value))


def feedback_divider(vref: float, vout: float, series: str = "E96",
                     r_bot_candidates: Iterable[float] | None = None) -> list[tuple]:
    """
    Vout = Vref·(1 + Rtop/Rbot). Searches standard values for the best pair.
    Keeps Rbot between 10 k and 100 k (divider current 8–80 µA at 0.8 V) as a sensible default.
    """
    results = []
    cands = r_bot_candidates or [v for v in e_series_values(series) if 10e3 <= v <= 100e3]
    for rb in cands:
        rt = nearest_e(rb * (vout / vref - 1), series)
        actual = vref * (1 + rt / rb)
        results.append((abs(actual - vout) / vout, rt, rb, actual))
    results.sort()
    return results[:5]


# ---------------------------------------------------------------------------
# 6. Buck converter first-pass design
# ---------------------------------------------------------------------------
def buck_design(vin: float, vout: float, iout: float, fsw: float,
                ripple_pct: float = 30.0, c_out: float = 22e-6, esr: float = 0.005) -> dict:
    d = vout / vin
    di_target = ripple_pct / 100 * iout
    l_calc = (vin - vout) * d / (di_target * fsw)
    # Round UP to the next E12 value so the ripple stays at or below the target.
    l_std = min(v for v in e_series_values("E12") if v >= l_calc * 1e6 * 0.999) * 1e-6
    di = (vin - vout) * d / (l_std * fsw)
    return {
        "duty": d,
        "L_calc_H": l_calc,
        "L_chosen_H": l_std,
        "ripple_A": di,
        "I_peak_A": iout + di / 2,
        "Cin_rms_A": iout * math.sqrt(d * (1 - d)),
        "Vout_ripple_V": di / (8 * fsw * c_out) + di * esr,
        "c_out_assumed_F": c_out,
    }


# ---------------------------------------------------------------------------
# 7. Noise, thermal, edges, skin depth
# ---------------------------------------------------------------------------
def johnson_noise_density(r: float, temp_k: float = 300.0) -> float:
    """v_n = √(4kTR) in V/√Hz."""
    return math.sqrt(4 * K_B * temp_k * r)


def junction_temp(power: float, theta_ja: float, ambient: float) -> float:
    return ambient + power * theta_ja


def edge_analysis(rise_time: float, er_eff: float) -> dict:
    """
    Knee frequency and "critical length" — the length at which a trace should be treated as a
    transmission line. We use the common criterion: one-way delay > t_r / 6 (some use t_r/4 or t_r/2).
    """
    v = C0 / math.sqrt(er_eff)
    return {
        "f_knee_Hz_0.5": 0.5 / rise_time,
        "f_bw_Hz_0.35": 0.35 / rise_time,
        "edge_length_m": rise_time * v,              # spatial extent of the rising edge
        "critical_length_m": rise_time * v / 6,
    }


def skin_depth(freq: float, rho: float = RHO_CU) -> float:
    """δ = √(ρ / (π·f·µ0)) — current crowds into this depth at the conductor surface."""
    return math.sqrt(rho / (math.pi * freq * MU0))


def reflection(z0: float, zl: float) -> dict:
    gamma = (zl - z0) / (zl + z0)
    return {"gamma": gamma,
            "reflected_pct": gamma * 100,
            "return_loss_dB": -20 * math.log10(abs(gamma)) if gamma else float("inf"),
            "vswr": (1 + abs(gamma)) / (1 - abs(gamma)) if abs(gamma) < 1 else float("inf")}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _cli() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("trace-width", help="IPC-2221 trace width + resistance")
    s.add_argument("--current", type=float, required=True)
    s.add_argument("--temp-rise", type=float, default=10)
    s.add_argument("--copper-oz", type=float, default=1)
    s.add_argument("--layer", choices=["external", "internal"], default="external")
    s.add_argument("--length-mm", type=float, default=0)

    s = sub.add_parser("microstrip")
    s.add_argument("--width-mm", type=float, required=True)
    s.add_argument("--height-mm", type=float, required=True)
    s.add_argument("--er", type=float, default=4.1)
    s.add_argument("--thickness-mm", type=float, default=0.035)

    s = sub.add_parser("stripline")
    s.add_argument("--width-mm", type=float, required=True)
    s.add_argument("--b-mm", type=float, required=True, help="plane-to-plane dielectric thickness")
    s.add_argument("--er", type=float, default=4.1)

    s = sub.add_parser("diff-microstrip")
    s.add_argument("--width-mm", type=float, required=True)
    s.add_argument("--gap-mm", type=float, required=True)
    s.add_argument("--height-mm", type=float, required=True)
    s.add_argument("--er", type=float, default=4.1)
    s.add_argument("--thickness-mm", type=float, default=0.035)

    s = sub.add_parser("via")
    s.add_argument("--drill-mm", type=float, required=True)
    s.add_argument("--length-mm", type=float, default=1.6)
    s.add_argument("--pad-mm", type=float)
    s.add_argument("--antipad-mm", type=float)
    s.add_argument("--er", type=float, default=4.3)

    s = sub.add_parser("cap")
    s.add_argument("--c", type=float, required=True)
    s.add_argument("--esl", type=float, default=0.5e-9)
    s.add_argument("--esr", type=float, default=0.02)
    s.add_argument("--freq", type=float, nargs="+", default=[1e6, 10e6, 100e6])

    s = sub.add_parser("target-z")
    s.add_argument("--voltage", type=float, required=True)
    s.add_argument("--ripple-pct", type=float, required=True)
    s.add_argument("--step-current", type=float, required=True)

    s = sub.add_parser("divider")
    s.add_argument("--vref", type=float, required=True)
    s.add_argument("--vout", type=float, required=True)
    s.add_argument("--series", default="E96", choices=list(E_SERIES))

    s = sub.add_parser("rc")
    s.add_argument("--r", type=float, required=True)
    s.add_argument("--c", type=float, required=True)

    s = sub.add_parser("buck")
    s.add_argument("--vin", type=float, required=True)
    s.add_argument("--vout", type=float, required=True)
    s.add_argument("--iout", type=float, required=True)
    s.add_argument("--fsw", type=float, required=True)
    s.add_argument("--ripple-pct", type=float, default=30)
    s.add_argument("--cout", type=float, default=22e-6)

    s = sub.add_parser("noise")
    s.add_argument("--r", type=float, required=True)
    s.add_argument("--bw", type=float, default=1.0)
    s.add_argument("--temp-k", type=float, default=300)

    s = sub.add_parser("thermal")
    s.add_argument("--power", type=float, required=True)
    s.add_argument("--theta-ja", type=float, required=True)
    s.add_argument("--ambient", type=float, default=25)

    s = sub.add_parser("edge")
    s.add_argument("--rise-time", type=float, required=True)
    s.add_argument("--er-eff", type=float, default=3.0)

    s = sub.add_parser("skin")
    s.add_argument("--freq", type=float, required=True)

    s = sub.add_parser("reflection")
    s.add_argument("--z0", type=float, required=True)
    s.add_argument("--zl", type=float, required=True)

    a = p.parse_args()

    if a.cmd == "trace-width":
        w = ipc2221_width(a.current, a.temp_rise, a.copper_oz, a.layer == "external")
        print(f"IPC-2221 minimum width: {w * 1e3:.3f} mm ({w / MIL:.1f} mil)")
        print(f"Sheet resistance ({a.copper_oz} oz): {sheet_resistance(a.copper_oz) * 1e3:.3f} mΩ/□")
        if a.length_mm:
            r = trace_resistance(w, a.length_mm * 1e-3, a.copper_oz)
            print(f"At min width over {a.length_mm} mm: R = {eng(r, 'Ω')}, drop = {eng(r * a.current, 'V')},"
                  f" loss = {eng(r * a.current ** 2, 'W')}")
        print("Note: IPC-2152 is the modern standard; nearby planes let traces run cooler than this estimate.")

    elif a.cmd == "microstrip":
        r = microstrip(a.width_mm * 1e-3, a.height_mm * 1e-3, a.er, a.thickness_mm * 1e-3)
        _print_line(r)
        print(f"IPC-2141 formula (comparison): {ipc2141_microstrip(a.width_mm, a.height_mm, a.er, a.thickness_mm):.1f} Ω")

    elif a.cmd == "stripline":
        _print_line(stripline(a.width_mm * 1e-3, a.b_mm * 1e-3, a.er))

    elif a.cmd == "diff-microstrip":
        r = diff_microstrip(a.width_mm * 1e-3, a.gap_mm * 1e-3, a.height_mm * 1e-3, a.er, a.thickness_mm * 1e-3)
        print(f"Single-ended Z0: {r['z_single']:.1f} Ω   Differential: {r['z_diff']:.1f} Ω   (±10% — verify in field solver)")

    elif a.cmd == "via":
        r = via_parasitics(a.drill_mm * 1e-3, a.length_mm * 1e-3,
                           a.pad_mm * 1e-3 if a.pad_mm else None,
                           a.antipad_mm * 1e-3 if a.antipad_mm else None, a.er)
        print(f"Via inductance ≈ {r['L_nH']:.2f} nH   aspect ratio = {r['aspect_ratio']:.1f}:1")
        if "C_pF" in r:
            print(f"Via capacitance ≈ {r['C_pF']:.2f} pF   ~Z_via ≈ {r['Z_via_ohm']:.0f} Ω")

    elif a.cmd == "cap":
        print(f"SRF = {eng(srf(a.c, a.esl), 'Hz')}")
        for f in a.freq:
            print(f"  |Z| @ {eng(f, 'Hz'):>9}: {eng(cap_impedance(a.c, a.esl, a.esr, f), 'Ω')}")

    elif a.cmd == "target-z":
        print(f"Z_target = {eng(target_impedance(a.voltage, a.ripple_pct, a.step_current), 'Ω')}")

    elif a.cmd == "divider":
        print("Best standard-value pairs (Vout = Vref·(1 + Rtop/Rbot)):")
        for err, rt, rb, actual in feedback_divider(a.vref, a.vout, a.series):
            print(f"  Rtop = {eng(rt, 'Ω'):>9}  Rbot = {eng(rb, 'Ω'):>9}  → {actual:.4f} V  (error {err * 100:.3f}%)")

    elif a.cmd == "rc":
        fc = 1 / (2 * math.pi * a.r * a.c)
        print(f"τ = {eng(a.r * a.c, 's')}   f_c(−3 dB) = {eng(fc, 'Hz')}   ENBW = {eng(fc * math.pi / 2, 'Hz')}")

    elif a.cmd == "buck":
        r = buck_design(a.vin, a.vout, a.iout, a.fsw, a.ripple_pct, a.cout)
        print(f"Duty cycle D           = {r['duty']:.3f}")
        print(f"L (calculated)         = {eng(r['L_calc_H'], 'H')}  → chosen {eng(r['L_chosen_H'], 'H')}")
        print(f"Inductor ripple ΔI_L   = {r['ripple_A']:.3f} A ; peak = {r['I_peak_A']:.3f} A (choose I_sat above IC current limit)")
        print(f"C_in RMS current       = {r['Cin_rms_A']:.3f} A")
        print(f"V_out ripple (C={eng(r['c_out_assumed_F'], 'F')} effective) ≈ {eng(r['Vout_ripple_V'], 'V')}")

    elif a.cmd == "noise":
        d = johnson_noise_density(a.r, a.temp_k)
        print(f"Thermal noise density: {eng(d, 'V/√Hz')}   over {eng(a.bw, 'Hz')}: {eng(d * math.sqrt(a.bw), 'V rms')}")

    elif a.cmd == "thermal":
        tj = junction_temp(a.power, a.theta_ja, a.ambient)
        print(f"T_j = {tj:.1f} °C  (ΔT = {tj - a.ambient:.1f} °C)" + ("  ⚠ exceeds 125 °C" if tj > 125 else ""))

    elif a.cmd == "edge":
        r = edge_analysis(a.rise_time, a.er_eff)
        print(f"Knee frequency (0.5/tr): {eng(r['f_knee_Hz_0.5'], 'Hz')}   BW (0.35/tr): {eng(r['f_bw_Hz_0.35'], 'Hz')}")
        print(f"Spatial length of edge: {r['edge_length_m'] * 1e3:.1f} mm → treat traces longer than "
              f"~{r['critical_length_m'] * 1e3:.1f} mm as transmission lines (t_r/6 criterion)")

    elif a.cmd == "skin":
        print(f"Skin depth in copper @ {eng(a.freq, 'Hz')}: {eng(skin_depth(a.freq), 'm')}")

    elif a.cmd == "reflection":
        r = reflection(a.z0, a.zl)
        print(f"Γ = {r['gamma']:+.3f} ({r['reflected_pct']:+.1f}% of incident voltage)  "
              f"RL = {r['return_loss_dB']:.1f} dB  VSWR = {r['vswr']:.2f}")


def _print_line(r: dict) -> None:
    print(f"Z0 = {r['z0']:.1f} Ω   ε_eff = {r['e_eff']:.2f}")
    print(f"Delay = {r['delay_ps_per_mm']:.2f} ps/mm ({r['delay_ps_per_in']:.0f} ps/in)")
    print(f"C = {r['C_pF_per_mm']:.3f} pF/mm   L = {r['L_nH_per_mm']:.3f} nH/mm")


if __name__ == "__main__":
    _cli()
