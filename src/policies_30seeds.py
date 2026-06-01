"""
J-K2 knockout: 30-seed reruns of the policy comparison with 95%
bootstrap CIs.

Replaces median/IQR with proper bootstrap 95% confidence intervals
on every reported metric. Default-parameter version; the calibrated
version follows.

Usage: python3 policies_30seeds.py
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, run
from policies import POLICIES

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)

TICKS = 250
SEEDS = 30        # bumped from 6


def _run_one(args):
    name, seed = args
    d = replace(POLICIES[name], seed=seed)
    h = run(d, ticks=TICKS)
    return name, seed, h[-1]


def bootstrap_ci(values: np.ndarray, n_boot: int = 2000,
                 alpha: float = 0.05) -> tuple[float, float, float]:
    """Returns (median, lower CI, upper CI) of the median statistic."""
    rng = np.random.default_rng(0)
    medians = np.empty(n_boot)
    n = len(values)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        medians[b] = np.median(values[idx])
    lo = float(np.percentile(medians, 100 * alpha / 2))
    hi = float(np.percentile(medians, 100 * (1 - alpha / 2)))
    return float(np.median(values)), lo, hi


def main():
    args = [(n, s) for n in POLICIES.keys() for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    t0 = time.time()
    print(f"running {len(args)} runs ({len(POLICIES)} policies x {SEEDS} seeds) ...")
    with Pool(n_proc) as p:
        results = p.map(_run_one, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_policy: dict[str, list[dict]] = {}
    for n, s, last in results:
        by_policy.setdefault(n, []).append(last)

    metric_keys = ["alive", "autocatalytic_closure", "gini",
                   "top1_share", "top10_share", "state_wealth"]

    summary = {}
    print()
    print(f"{'policy':<28} "
          f"{'alive (95% CI)':>22} "
          f"{'Phi (95% CI)':>22} "
          f"{'top10 (95% CI)':>22}")
    for n, runs in by_policy.items():
        arr = {k: np.array([r[k] for r in runs]) for k in metric_keys}
        cis = {k: bootstrap_ci(arr[k]) for k in metric_keys}
        summary[n] = {k: {"median": cis[k][0], "ci_lo": cis[k][1],
                          "ci_hi": cis[k][2]} for k in metric_keys}
        a = cis["alive"]
        p = cis["autocatalytic_closure"]
        t = cis["top10_share"]
        print(f"{n:<28} "
              f"{a[0]:5.0f}  [{a[1]:5.0f}, {a[2]:5.0f}]  "
              f"{p[0]:5.3f}  [{p[1]:5.3f}, {p[2]:5.3f}]  "
              f"{t[0]:5.2f}  [{t[1]:5.2f}, {t[2]:5.2f}]")

    with open(OUT_DATA / "policies_summary_30seeds_with_ci.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nsaved {OUT_DATA / 'policies_summary_30seeds_with_ci.json'}")


if __name__ == "__main__":
    main()
