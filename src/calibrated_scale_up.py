"""
Calibrated N=10k policy comparison (E2-1).

Runs the policy subset from scale_up.py at calibrated parameters
(r=0.06, rent=0.50) so we can compare the headline billionaire counts
and top-1 share between calibrated and default-parameter worlds.

Usage: python3 calibrated_scale_up.py
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Type, WEALTH_UNIT_GBP, make_initial_population, step
from policies import POLICIES
from scale_up import POLICY_SUBSET

OUT_DATA = Path("out/data")
SCALE = 100
TICKS = 180
SEEDS = 6   # smaller than baseline 10 for compute budget

CALIBRATED = dict(capital_return=0.06, rent_share_of_wage=0.50)


def _run_one(args):
    name, seed = args
    d = replace(POLICIES[name], population_scale=SCALE, seed=seed, **CALIBRATED)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
    living = [a for a in agents if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    closures = [step_history["autocatalytic_closure"]
                for step_history in [{"autocatalytic_closure": 0.0}]]  # placeholder
    # Closure: pull from the final accum-like state. We re-derive from the last
    # tick by inspecting whether productive_flow tracking is in accum; but step()
    # already returned closure per-tick. We don't keep the history here; instead
    # recompute via accum["recent_deaths"] (no closure stored). Simpler: rerun
    # the run() function from sim and use its history.
    return name, seed, {
        "alive": len(living),
        "billionaires_count": int((gbp >= 1e9).sum()),
        "centi_count": int((gbp >= 1e8).sum()),
        "deci_count": int((gbp >= 1e7).sum()),
        "max_wealth_gbp": float(gbp.max()) if len(gbp) else 0.0,
        "top1_share": (sorted(nws, reverse=True)[:max(1, len(nws)//100)] and
                       sum(sorted(nws, reverse=True)[:max(1, len(nws)//100)]) /
                       max(nws.sum(), 1e-9)),
    }


def main():
    args = [(n, s) for n in POLICY_SUBSET for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} N=10k runs at calibrated parameters ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run_one, args)
    print(f"done in {time.time() - t0:.1f}s")

    by_policy: dict[str, list[dict]] = {}
    for n, s, m in results:
        by_policy.setdefault(n, []).append(m)

    summary = {}
    for n, runs in by_policy.items():
        summary[n] = {
            "alive_median": float(np.median([r["alive"] for r in runs])),
            "billionaires_median": float(np.median([r["billionaires_count"]
                                                    for r in runs])),
            "centi_median": float(np.median([r["centi_count"] for r in runs])),
            "deci_median": float(np.median([r["deci_count"] for r in runs])),
            "top1_share_median": float(np.median([r["top1_share"] for r in runs])),
            "max_wealth_gbp_median": float(np.median(
                [r["max_wealth_gbp"] for r in runs])),
        }

    print(f"\n{'policy':<28} {'alive':>6} {'top1':>6} {'>=10M':>6} {'>=100M':>7} {'>=1B':>5} {'max £':>10}")
    for n in POLICY_SUBSET:
        s = summary[n]
        print(f"{n:<28} {s['alive_median']:6.0f} {s['top1_share_median']:6.3f} "
              f"{s['deci_median']:6.0f} {s['centi_median']:7.0f} "
              f"{s['billionaires_median']:5.0f} "
              f"{s['max_wealth_gbp_median']/1e9:>8.2f}B")

    with open(OUT_DATA / "policy_summary_n10k_calibrated.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
