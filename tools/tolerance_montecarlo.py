#!/usr/bin/env python3
"""
tolerance_montecarlo.py — Worst-case vs. statistical tolerance analysis of a voltage divider
(or a regulator feedback divider), the way you'd justify resistor tolerances in a design review.

Worst case: every part at its tolerance limit in the direction that hurts most.
Statistical: parts drawn from a distribution (uniform within ±tol is a conservative assumption for
resistors; real lots are often tighter and roughly Gaussian).

    python tolerance_montecarlo.py
    python tolerance_montecarlo.py --r1 35.7e3 --r2 11.5e3 --vref 0.8 --vref-tol 1 --tol 1 --feedback
"""
from __future__ import annotations

import argparse

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vin", type=float, default=12.0, help="divider input (ignored with --feedback)")
    ap.add_argument("--r1", type=float, default=100e3, help="top resistor")
    ap.add_argument("--r2", type=float, default=10e3, help="bottom resistor")
    ap.add_argument("--tol", type=float, default=1.0, help="resistor tolerance, %%")
    ap.add_argument("--feedback", action="store_true", help="analyze Vout = Vref·(1 + R1/R2) instead")
    ap.add_argument("--vref", type=float, default=0.8)
    ap.add_argument("--vref-tol", type=float, default=1.0, help="reference tolerance, %%")
    ap.add_argument("-n", type=int, default=200_000)
    ap.add_argument("--plot", action="store_true")
    a = ap.parse_args()

    rng = np.random.default_rng(1)
    t = a.tol / 100
    r1 = a.r1 * (1 + rng.uniform(-t, t, a.n))
    r2 = a.r2 * (1 + rng.uniform(-t, t, a.n))

    if a.feedback:
        tv = a.vref_tol / 100
        vref = a.vref * (1 + rng.uniform(-tv, tv, a.n))
        out = vref * (1 + r1 / r2)
        nominal = a.vref * (1 + a.r1 / a.r2)
        lo = a.vref * (1 - tv) * (1 + a.r1 * (1 - t) / (a.r2 * (1 + t)))
        hi = a.vref * (1 + tv) * (1 + a.r1 * (1 + t) / (a.r2 * (1 - t)))
        what = "Vout = Vref·(1 + R1/R2)"
    else:
        out = a.vin * r2 / (r1 + r2)
        nominal = a.vin * a.r2 / (a.r1 + a.r2)
        lo = a.vin * a.r2 * (1 - t) / (a.r1 * (1 + t) + a.r2 * (1 - t))
        hi = a.vin * a.r2 * (1 + t) / (a.r1 * (1 - t) + a.r2 * (1 + t))
        what = "Vout = Vin·R2/(R1+R2)"

    pct = lambda v: (v - nominal) / nominal * 100
    print(what)
    print(f"Nominal:            {nominal:.5f} V")
    print(f"Worst case:         {lo:.5f} … {hi:.5f} V   ({pct(lo):+.3f}% / {pct(hi):+.3f}%)")
    print(f"Monte Carlo (n={a.n}):")
    print(f"  std dev:          {out.std():.5f} V ({out.std() / nominal * 100:.3f}%)")
    print(f"  ±3σ:              {nominal - 3 * out.std():.5f} … {nominal + 3 * out.std():.5f} V")
    print(f"  observed min/max: {out.min():.5f} … {out.max():.5f} V")
    print("\nInterpretation: design to worst case when failure is unacceptable (safety, abs-max limits);")
    print("statistical (RSS / ±3σ) is standard for performance specs across a production batch.")

    if a.plot:
        import matplotlib.pyplot as plt
        plt.hist(out, bins=200, color="tab:blue", alpha=0.8)
        for v, c in [(lo, "tab:red"), (hi, "tab:red"), (nominal, "k")]:
            plt.axvline(v, color=c, ls="--")
        plt.xlabel("Vout (V)"); plt.ylabel("count"); plt.title(what + " — Monte Carlo vs worst case")
        plt.tight_layout(); plt.show()


if __name__ == "__main__":
    main()
