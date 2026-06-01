"""
Calibration of Tory baseline to UK WID wealth shares (E-1 Route B).

Targets (UK, approximate):
  top 1%  wealth share = 0.30
  top 10% wealth share = 0.57
  top 0.1% wealth share = 0.13
  Pareto slope (top 50) = -0.706

We sweep over (capital_return, rent_share_of_wage, inheritance_tax_rate)
and report L2 distance to target. The best-fit combination is the
"calibrated Tory" specification used in the revised paper to put pound
labels back on policy claims.

Grid is intentionally coarse for tractability; refine in a follow-up
paper. Default Tory dials otherwise.

Usage: python3 calibration.py
"""
from __future__ import annotations

import json
from dataclasses import asdict, replace
from itertools import product
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import (Dials, Type, top_k_share, make_initial_population, step)

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)


# UK targets (approximate from WID 2022; small variation across sources)
TARGETS = {
    "top1": 0.30,
    "top10": 0.57,
    "top01": 0.13,
    "pareto_slope_top50": -0.706,
}

SCALE = 10                  # N=1000 for calibration grid (fast)
TICKS = 200
SEEDS = 5


def _run_one(args):
    r, rent, iota, seed = args
    d = Dials(
        seed=seed,
        population_scale=SCALE,
        capital_return=float(r),
        rent_share_of_wage=float(rent),
        inheritance_tax_rate=float(iota),
        # Tory baseline: no wealth tax, no UBI, no state spending.
    )
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    if len(nws) < 10:
        return r, rent, iota, seed, {"top1": 0.0, "top10": 0.0, "top01": 0.0,
                                      "slope": 0.0, "alive": len(nws)}
    n = len(nws)
    top1 = top_k_share(nws, max(1, int(0.01 * n)))
    top10 = top_k_share(nws, max(1, int(0.10 * n)))
    top01 = top_k_share(nws, max(1, int(0.001 * n)))
    sorted_w = np.sort(nws)[::-1]
    top50 = sorted_w[:min(50, len(sorted_w))]
    valid = top50 > 0
    if valid.sum() >= 5:
        slope, _ = np.polyfit(np.log(np.arange(1, valid.sum() + 1)),
                               np.log(top50[valid]), 1)
    else:
        slope = 0.0
    return r, rent, iota, seed, {"top1": float(top1), "top10": float(top10),
                                  "top01": float(top01), "slope": float(slope),
                                  "alive": int(len(nws))}


def main():
    # Coarse grid
    rs = [0.04, 0.06, 0.08, 0.10]
    rents = [0.20, 0.35, 0.50]
    iotas = [0.0, 0.2, 0.4]
    args = [(r, rent, iota, s)
            for r in rs for rent in rents for iota in iotas
            for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} calibration cells ...")
    with Pool(n_proc) as p:
        rows = p.map(_run_one, args)

    by_cell: dict[tuple, dict[str, list[float]]] = {}
    for r, rent, iota, seed, m in rows:
        k = (r, rent, iota)
        by_cell.setdefault(k, {"top1": [], "top10": [], "top01": [],
                               "slope": [], "alive": []})
        for kk, v in m.items():
            by_cell[k][kk].append(v)

    summary = []
    for (r, rent, iota), m in by_cell.items():
        med = {kk: float(np.median(v)) for kk, v in m.items()}
        loss = (
            (med["top1"] - TARGETS["top1"]) ** 2
            + (med["top10"] - TARGETS["top10"]) ** 2
            + (med["top01"] - TARGETS["top01"]) ** 2
            + 0.1 * (med["slope"] - TARGETS["pareto_slope_top50"]) ** 2
        )
        summary.append({"capital_return": r,
                        "rent_share_of_wage": rent,
                        "inheritance_tax_rate": iota,
                        "top1": med["top1"], "top10": med["top10"],
                        "top01": med["top01"], "slope": med["slope"],
                        "alive": med["alive"], "loss": float(loss)})

    summary.sort(key=lambda x: x["loss"])

    print()
    print(f"{'rank':>4}  {'r':>5} {'rent':>5} {'iota':>5}  "
          f"{'top1':>5} {'top10':>5} {'top01':>5} {'slope':>7} "
          f"{'alive':>5} {'loss':>8}")
    for rk, s in enumerate(summary[:12], start=1):
        print(f"{rk:>4}  {s['capital_return']:>5.2f} "
              f"{s['rent_share_of_wage']:>5.2f} "
              f"{s['inheritance_tax_rate']:>5.2f}  "
              f"{s['top1']:>5.2f} {s['top10']:>5.2f} {s['top01']:>5.2f} "
              f"{s['slope']:>7.3f} {s['alive']:>5.0f} {s['loss']:>8.4f}")

    print("\nUK targets:")
    print(f"     top1 = {TARGETS['top1']}, top10 = {TARGETS['top10']}, "
          f"top01 = {TARGETS['top01']}, pareto slope = {TARGETS['pareto_slope_top50']}")

    print(f"\nBest fit:")
    best = summary[0]
    print(f"   capital_return = {best['capital_return']}")
    print(f"   rent_share_of_wage = {best['rent_share_of_wage']}")
    print(f"   inheritance_tax_rate = {best['inheritance_tax_rate']}")
    print(f"   yields top1={best['top1']:.2f}, top10={best['top10']:.2f}, "
          f"top01={best['top01']:.2f}, slope={best['slope']:.3f}")

    with open(OUT_DATA / "calibration_results.json", "w") as f:
        json.dump({"targets": TARGETS, "results": summary[:30]}, f, indent=2)


if __name__ == "__main__":
    main()
