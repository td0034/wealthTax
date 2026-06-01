"""
J-K4 knockout: dial sensitivity analysis (OFAT).

For each principal dial, run current_world at 0.5x and 2x the default
value and report response of (alive, Gini, Phi, top10) to each.

Usage: python3 dial_sensitivity.py
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, run

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)

TICKS = 250
SEEDS = 8

DIALS = {
    "wage": 1.0,
    "maker_multiplier": 1.6,
    "employer_markup": 0.4,
    "capital_return": 0.04,
    "rent_share_of_wage": 0.35,
    "interest_rate": 0.06,
    "subsistence": 0.6,
    "lifespan_mean": 70.0,
    "memory_bandwidth_base": 0.5,
    "memory_bandwidth_wealth_scale": 0.5,
    "skill_mutation_rate": 0.05,
}

PERTURBATIONS = [0.5, 1.0, 2.0]


def _run(args):
    dial_name, factor, seed = args
    d = Dials(seed=seed)
    if dial_name is not None:
        setattr(d, dial_name, getattr(d, dial_name) * factor)
    h = run(d, ticks=TICKS)
    last = h[-1]
    return dial_name, factor, seed, last


def main():
    args = []
    for seed in range(SEEDS):
        args.append((None, 1.0, seed))   # baseline
        for dial in DIALS:
            for f in PERTURBATIONS:
                if f == 1.0:
                    continue
                args.append((dial, f, seed))
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        rows = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    metric_keys = ["alive", "autocatalytic_closure", "gini", "top10_share"]
    grouped: dict[tuple, dict[str, list[float]]] = {}
    for dial, f, seed, last in rows:
        k = (dial, f)
        grouped.setdefault(k, {m: [] for m in metric_keys})
        for m in metric_keys:
            grouped[k][m].append(float(last[m]))

    baseline = {m: float(np.median(grouped[(None, 1.0)][m])) for m in metric_keys}
    print()
    print(f"BASELINE: alive={baseline['alive']:.0f}  "
          f"Phi={baseline['autocatalytic_closure']:.3f}  "
          f"Gini={baseline['gini']:.2f}  top10={baseline['top10_share']:.2f}")
    print()
    print(f"{'dial':<26}{'factor':>7}  "
          f"{'alive':>7} {'Phi':>7} {'Gini':>7} {'top10':>7}  "
          f"{'d_alive':>8} {'d_Phi':>8} {'d_Gini':>8} {'d_top10':>8}")

    summary = {"baseline": baseline, "perturbations": {}}
    for (dial, f), m in grouped.items():
        if dial is None:
            continue
        med = {k: float(np.median(v)) for k, v in m.items()}
        delta = {k: med[k] - baseline[k] for k in metric_keys}
        summary["perturbations"].setdefault(dial, {})[str(f)] = {
            "median": med, "delta": delta}
        print(f"{dial:<26}{f:>7.1f}  "
              f"{med['alive']:>7.0f} {med['autocatalytic_closure']:>7.3f} "
              f"{med['gini']:>7.2f} {med['top10_share']:>7.2f}  "
              f"{delta['alive']:>+8.0f} {delta['autocatalytic_closure']:>+8.3f} "
              f"{delta['gini']:>+8.2f} {delta['top10_share']:>+8.2f}")

    with open(OUT_DATA / "dial_sensitivity.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
