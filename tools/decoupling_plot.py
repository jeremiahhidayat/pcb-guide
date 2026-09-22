#!/usr/bin/env python3
"""
decoupling_plot.py — Plot the impedance of a decoupling capacitor network vs. frequency.

Each capacitor group is modeled as N identical series R-L-C branches in parallel
(ESR, *mounted* ESL, C). The total network impedance is the parallel combination of all groups.

Edit NETWORKS below (or import `network_impedance`) to explore your own design.
Compare with diagrams/decoupling-impedance.html and spice/03_decoupling_antiresonance.cir.

    python decoupling_plot.py                 # show plot
    python decoupling_plot.py --save out.png  # save instead
"""
from __future__ import annotations

import argparse

import numpy as np

# (quantity, capacitance F, mounted ESL H, ESR ohm)
NETWORKS = {
    "Ladder 10µ + 100n + 10n + 1n": [(1, 10e-6, 1.0e-9, 0.005), (1, 100e-9, 0.8e-9, 0.02),
                                     (1, 10e-9, 0.8e-9, 0.05), (1, 1e-9, 0.8e-9, 0.1)],
    "10µ + 4 × 100n (same value)": [(1, 10e-6, 1.0e-9, 0.005), (4, 100e-9, 0.8e-9, 0.02)],
    "10µ + 4 × 100n, poor mounting (2 nH)": [(1, 10e-6, 3e-9, 0.005), (4, 100e-9, 2.0e-9, 0.02)],
}
TARGET_Z = 0.1  # ohms — e.g. 3.3 V × 3% / 1 A


def group_impedance(f: np.ndarray, n: int, c: float, esl: float, esr: float) -> np.ndarray:
    w = 2 * np.pi * f
    return (esr + 1j * w * esl + 1 / (1j * w * c)) / n


def network_impedance(f: np.ndarray, groups) -> np.ndarray:
    y = sum(1 / group_impedance(f, *g) for g in groups)
    return 1 / y


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", help="save the figure to this path instead of showing it")
    args = ap.parse_args()

    import matplotlib
    if args.save:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    f = np.logspace(3, 9, 2000)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for name, groups in NETWORKS.items():
        z = np.abs(network_impedance(f, groups))
        ax.loglog(f, z, lw=2, label=name)
        # report the worst anti-resonance peak between the lowest and highest SRF
        srfs = [1 / (2 * np.pi * np.sqrt(g[1] * g[2])) for g in groups]
        band = (f > min(srfs)) & (f < max(srfs))
        i = np.argmax(z[band])
        print(f"{name:40s} SRFs: {', '.join(f'{s / 1e6:.2f} MHz' for s in srfs)}"
              f" | worst |Z| between SRFs: {z[band][i] * 1e3:.0f} mΩ @ {f[band][i] / 1e6:.1f} MHz")
    ax.axhline(TARGET_Z, ls="--", color="tab:red", label=f"Target {TARGET_Z * 1e3:.0f} mΩ")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("|Z| (Ω)")
    ax.set_title("Decoupling network impedance")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    if args.save:
        fig.savefig(args.save, dpi=150)
        print(f"saved {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
