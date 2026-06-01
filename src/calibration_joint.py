"""
E-K1 knockout: joint calibration to wealth distribution + mortality.

Sweeps over (r, rent, iota, subsistence, inheritance_cap) and
optimizes against five targets:
  - top 1% share (UK ~0.30)
  - top 10% share (UK ~0.57)
  - top 0.1% share (UK ~0.13)
  - Pareto slope of top 50 (-0.706)
  - alive rate at terminal tick (~0.95)

The mortality target makes calibration genuinely joint rather than
tail-only. Reports best L2 fit.

Usage: python3 calibration_joint.py
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from itertools import product
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, Type, top_k_share, make_initial_population, step

OUT_DATA = Path("out/data")


TARGETS = {
    "top1": 0.30,
    "top10": 0.57,
    "top01": 0.13,
    "pareto_slope_top50": -0.706,
    "alive_rate": 0.85,    # 85% alive at terminal tick (relaxed from UK)
}

SCALE = 10            # N=1000 for tractability
TICKS = 200
SEEDS = 4


def _run_one(args):
    r, rent, iota, sub, inh_cap, seed = args
    d = Dials(
        seed=seed,
        population_scale=SCALE,
        capital_return=float(r),
        rent_share_of_wage=float(rent),
        inheritance_tax_rate=float(iota),
        subsistence=float(sub),
        inheritance_cap=float(inh_cap),
    )
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_n = sum(1 for a in agents if a.type != Type.STATE)
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    if len(nws) < 10:
        return r, rent, iota, sub, inh_cap, seed, {
            "top1": 0.0, "top10": 0.0, "top01": 0.0,
            "slope": 0.0, "alive_rate": 0.0,
        }
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
    alive_rate = len(living) / max(initial_n, 1)
    return r, rent, iota, sub, inh_cap, seed, {
        "top1": float(top1), "top10": float(top10),
        "top01": float(top01), "slope": float(slope),
        "alive_rate": float(alive_rate),
    }


def main():
    # Wider grid including subsistence and inheritance_cap.
    rs = [0.04, 0.06, 0.08]
    rents = [0.20, 0.35, 0.50]
    iotas = [0.0, 0.4]
    subs = [0.3, 0.6]          # lower subsistence helps survival
    inh_caps = [50.0, 500.0, float("inf")]   # capping inheritance affects tail concentration
    grid = list(product(rs, rents, iotas, subs, inh_caps))

    args = [(r, rent, iota, sub, ic, s)
            for r, rent, iota, sub, ic in grid
            for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} cells ({len(grid)} configs x {SEEDS} seeds) ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        rows = p.map(_run_one, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_cell: dict[tuple, dict[str, list[float]]] = {}
    for r, rent, iota, sub, ic, seed, m in rows:
        k = (r, rent, iota, sub, ic)
        by_cell.setdefault(k, {key: [] for key in
                               ["top1", "top10", "top01", "slope",
                                "alive_rate"]})
        for key in by_cell[k]:
            by_cell[k][key].append(m[key])

    summary = []
    for (r, rent, iota, sub, ic), m in by_cell.items():
        med = {k: float(np.median(v)) for k, v in m.items()}
        # Weighted L2 loss with mortality target weighted heavily.
        loss = (
            (med["top1"]  - TARGETS["top1"])  ** 2
            + (med["top10"] - TARGETS["top10"]) ** 2
            + (med["top01"] - TARGETS["top01"]) ** 2
            + 0.1 * (med["slope"] - TARGETS["pareto_slope_top50"]) ** 2
            + 1.0 * (med["alive_rate"] - TARGETS["alive_rate"]) ** 2
        )
        summary.append({
            "r": r, "rent": rent, "iota": iota,
            "subsistence": sub, "inheritance_cap": ic if ic != float("inf") else "inf",
            "top1": med["top1"], "top10": med["top10"], "top01": med["top01"],
            "slope": med["slope"], "alive_rate": med["alive_rate"],
            "loss": float(loss),
        })

    summary.sort(key=lambda x: x["loss"])

    print(f"\nUK targets: top1={TARGETS['top1']}, top10={TARGETS['top10']}, "
          f"top01={TARGETS['top01']}, slope={TARGETS['pareto_slope_top50']}, "
          f"alive_rate>={TARGETS['alive_rate']}")
    print()
    print(f"{'rank':>3}  {'r':>5} {'rent':>5} {'iota':>5} {'sub':>5} {'inh_cap':>8}  "
          f"{'top1':>5} {'top10':>5} {'top01':>5} {'slope':>7} {'alive':>5}  {'loss':>7}")
    for rk, s in enumerate(summary[:15], start=1):
        ic_disp = "inf" if s["inheritance_cap"] == "inf" else f"{s['inheritance_cap']:.0f}"
        print(f"{rk:>3}  {s['r']:>5.2f} {s['rent']:>5.2f} {s['iota']:>5.2f} "
              f"{s['subsistence']:>5.2f} {ic_disp:>8}  "
              f"{s['top1']:>5.2f} {s['top10']:>5.2f} {s['top01']:>5.2f} "
              f"{s['slope']:>7.3f} {s['alive_rate']:>5.2f}  {s['loss']:>7.4f}")

    with open(OUT_DATA / "joint_calibration_results.json", "w") as f:
        json.dump({"targets": TARGETS, "results": summary[:30]}, f, indent=2)


if __name__ == "__main__":
    main()
