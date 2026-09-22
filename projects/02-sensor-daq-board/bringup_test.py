#!/usr/bin/env python3
"""
bringup_test.py — Scripted bring-up / characterization for the Sensor DAQ board (Project 2).

It speaks a deliberately simple line-based protocol that your firmware implements over USB CDC or UART:

    host → "ID?\n"               board → "DAQ4,revA,<serial>,<fw-version>\n"
    host → "RAILS?\n"            board → "3V3_D=3.301,3V3_A=3.299,VEXC=4.998\n"   (from internal ADC/monitor)
    host → "READ <ch> <n>\n"     board → n lines, each one conversion result in volts (input-referred)
    host → "RATE <sps>\n"        board → "OK\n"

Run without hardware to see what the report looks like:
    python bringup_test.py --simulate
With hardware:
    python bringup_test.py --port COM5            (Linux: /dev/ttyACM0)

Requires: numpy; pyserial (only for real hardware: pip install pyserial).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict

import numpy as np

# Pass criteria — copy these from your design notes' noise budget.
NOISE_PP_LIMIT_V = 1.0e-6        # input-referred peak-to-peak (0.1–10 Hz class measurement)
RAIL_LIMITS = {"3V3_D": (3.234, 3.366), "3V3_A": (3.267, 3.333), "VEXC": (4.95, 5.05)}
SPUR_FREQS_HZ = [50.0, 60.0]     # mains; add SMPS/USB-frame aliases for your sample rate


@dataclass
class Result:
    name: str
    passed: bool
    detail: str


class Board:
    """Real hardware over a serial port."""

    def __init__(self, port: str, baud: int = 115200):
        try:
            import serial  # type: ignore
        except ImportError:
            sys.exit("pyserial not installed: pip install pyserial")
        self.s = serial.Serial(port, baud, timeout=2)
        time.sleep(0.2)
        self.s.reset_input_buffer()

    def query(self, cmd: str) -> str:
        self.s.write((cmd + "\n").encode())
        return self.s.readline().decode().strip()

    def read(self, ch: int, n: int) -> np.ndarray:
        self.s.write(f"READ {ch} {n}\n".encode())
        return np.array([float(self.s.readline()) for _ in range(n)])


class SimBoard:
    """Synthetic board: white noise + a little 60 Hz pickup on channel 2, so you can see a failing test."""

    def __init__(self, sps: float = 16.6):
        self.sps, self.rng = sps, np.random.default_rng(0)

    def query(self, cmd: str) -> str:
        if cmd == "ID?":
            return "DAQ4,revA,SIM0001,0.1.0"
        if cmd == "RAILS?":
            return "3V3_D=3.302,3V3_A=3.298,VEXC=4.997"
        if cmd.startswith("RATE"):
            self.sps = float(cmd.split()[1])
            return "OK"
        return "ERR"

    def read(self, ch: int, n: int) -> np.ndarray:
        t = np.arange(n) / self.sps
        x = self.rng.normal(0, 0.12e-6, n)
        if ch == 2:  # simulated 60 Hz mains pickup; at 16.6 SPS it aliases to 6.4 Hz
            x += 0.6e-6 * np.sin(2 * np.pi * 60.0 * t + 0.3)
        return x


def noise_stats(x: np.ndarray, sps: float) -> dict:
    x = x - x.mean()
    rms = x.std()
    f = np.fft.rfftfreq(len(x), 1 / sps)
    win = np.hanning(len(x))
    spec = np.abs(np.fft.rfft(x * win)) / (win.sum() / 2)
    peak_i = 1 + np.argmax(spec[1:])
    return {"rms": rms, "pp": x.max() - x.min(),
            "peak_freq": float(f[peak_i]), "peak_amp": float(spec[peak_i]),
            "median_floor": float(np.median(spec[1:]))}


def aliased(f_sig: float, sps: float) -> float:
    """Where a tone at f_sig appears after sampling at sps (folding)."""
    f = f_sig % sps
    return min(f, sps - f)


def run(board, sps: float, n: int, channels: list[int]) -> list[Result]:
    results: list[Result] = []

    ident = board.query("ID?")
    results.append(Result("identify", ident.startswith("DAQ4"), ident))

    rails = dict(kv.split("=") for kv in board.query("RAILS?").split(","))
    for name, (lo, hi) in RAIL_LIMITS.items():
        v = float(rails.get(name, "nan"))
        results.append(Result(f"rail {name}", lo <= v <= hi, f"{v:.3f} V (limits {lo}–{hi})"))

    board.query(f"RATE {sps:g}")
    for ch in channels:
        x = board.read(ch, n)
        st = noise_stats(x, sps)
        results.append(Result(f"ch{ch} noise p-p", st["pp"] <= NOISE_PP_LIMIT_V,
                              f"{st['pp'] * 1e6:.3f} µV p-p, {st['rms'] * 1e9:.1f} nV rms (limit {NOISE_PP_LIMIT_V * 1e6:.2f} µV p-p)"))
        spur_bins = [aliased(fs, sps) for fs in SPUR_FREQS_HZ]
        is_spur = any(abs(st["peak_freq"] - fb) < sps / n * 2 for fb in spur_bins)
        spur_ratio = st["peak_amp"] / st["median_floor"]
        results.append(Result(f"ch{ch} spectrum", not (is_spur and spur_ratio > 6),
                              f"largest tone {st['peak_freq']:.3f} Hz, {spur_ratio:.1f}× floor"
                              + ("  ← matches aliased mains!" if is_spur else "")))
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--sps", type=float, default=16.6, help="data rate; 16.6 SPS is a common ΔΣ rate")
    ap.add_argument("-n", type=int, default=256)
    ap.add_argument("--channels", type=int, nargs="+", default=[0, 1, 2, 3])
    ap.add_argument("--json", help="write results to this file (keep it with the bring-up log)")
    a = ap.parse_args()

    if not a.simulate and not a.port:
        ap.error("give --port or --simulate")
    board = SimBoard(a.sps) if a.simulate else Board(a.port)

    results = run(board, a.sps, a.n, a.channels)
    width = max(len(r.name) for r in results)
    for r in results:
        print(f"{'PASS' if r.passed else 'FAIL'}  {r.name:<{width}}  {r.detail}")
    print(f"\n{sum(r.passed for r in results)}/{len(results)} passed")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump([asdict(r) for r in results], fh, indent=2)
    sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
    main()
