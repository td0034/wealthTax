"""
Rerun the policy suite at calibrated parameters (E2-1).

The calibration (calibration.py / §5.9) matches the UK Sunday Times Rich
List Pareto slope at:
    capital_return r = 0.06
    rent_share_of_wage = 0.50
    inheritance_tax_rate = 0.40 (default for Tory baseline; we keep each
                                  policy's own iota since this is a
                                  policy-distinguishing dial)

The original policy results ran at the *uncalibrated* defaults
(r=0.04, rent=0.35). This script reruns the 11 policies at the
calibrated baseline so we can report how much (or how little) the
qualitative policy conclusions move.

Usage: python3 calibrated_policies.py
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, run, Type
from policies import POLICIES

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)


CALIBRATED_OVERRIDES = dict(
    capital_return=0.06,
    rent_share_of_wage=0.50,
)

TICKS = 250
SEEDS = 6


def _run_one(args):
    name, seed = args
    d = replace(POLICIES[name], seed=seed, **CALIBRATED_OVERRIDES)
    h = run(d, ticks=TICKS)
    return name, seed, h[-1]


def main():
    names = list(POLICIES.keys())
    args = [(n, s) for n in names for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    t0 = time.time()
    print(f"running {len(args)} runs at calibrated parameters ...")
    with Pool(n_proc) as p:
        results = p.map(_run_one, args)
    print(f"done in {time.time() - t0:.1f}s")

    by_policy: dict[str, list[dict]] = {}
    for n, s, last in results:
        by_policy.setdefault(n, []).append(last)

    summary = {}
    for n, runs in by_policy.items():
        m = lambda k: float(np.median([r[k] for r in runs]))
        summary[n] = {
            "alive_median": m("alive"),
            "gini_median": m("gini"),
            "closure_median": m("autocatalytic_closure"),
            "top10_median": m("top10_share"),
            "state_wealth_median": m("state_wealth"),
            "meta_median": float(np.median([
                rr["metabolic_rate"] for run in by_policy[n] for rr in [run]])),
        }

    print(f"\n{'policy':<28} {'alive':>5} {'gini':>5} {'Phi':>6} {'top10':>6} {'state_w':>8}")
    for n in names:
        s = summary[n]
        print(f"{n:<28} {s['alive_median']:5.0f} {s['gini_median']:5.2f} "
              f"{s['closure_median']:6.3f} {s['top10_median']:6.2f} "
              f"{s['state_wealth_median']:8.0f}")

    with open(OUT_DATA / "policies_calibrated_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nsaved {OUT_DATA / 'policies_calibrated_summary.json'}")


if __name__ == "__main__":
    main()
