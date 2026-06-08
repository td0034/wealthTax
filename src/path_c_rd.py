"""
Path-C C1 proof-of-concept: endogenous R&D mechanism.

The central question: under what conditions does the wealth tax
produce higher long-run productive-throughput growth than the status
quo?

Mechanism (see sim.py for full description):
  rd_budget_pool = share * (sum MAKER+EMPLOYER wealth)
  innovation_rate = rd_innovation_coeff
                   * sqrt(rd_budget_pool)
                   * (mean_worker_skill_breadth / SKILL_DIMS) ** elasticity

The skill_breadth_elasticity is the key parameter:
  elasticity = 0: only R&D budget matters
  elasticity = 1: budget and breadth equally weighted
  elasticity > 1: skill breadth dominates

Sweep:
  Policy arms: status_quo, hybrid_5pct, hybrid_10pct, cap_5M
  Elasticities: 0.0, 0.25, 0.5, 0.75, 1.0

Measure PT growth rate over the steady-state window. The hypothesis
is that at elasticities >= 0.3 (the Hanushek-Woessmann human-capital
elasticity range), wealth-tax arms produce higher PT growth than the
status quo.

Falsifiability: at elasticity ~0, status quo should win because
concentrated R&D budget dominates.

If the hypothesis holds, the Path-C paper has its central finding.
If not, the result is interesting in its own right (the orthodox
prediction is empirically confirmed at low skill-elasticity) and the
paper writes itself around the conditional answer.
"""
from __future__ import annotations

import json
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, Type, WEALTH_UNIT_GBP, make_initial_population, step

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)

SCALE = 100
TICKS = 180
WINDOW_START = 80
SEEDS = 4

# R&D parameters held constant across the sweep.
RD_SHARE_MAKER = 0.05
RD_SHARE_EMPLOYER = 0.05
# Coefficient calibrated so that under typical RD budget (~5000 units)
# and breadth_norm ~ 0.7, innovation rate is around 0.005 per tick
# (matching UK output-per-hour growth at ~0.5%/year under the 1 tick
# = 1 year mapping).
RD_INNOVATION_COEFF = 0.0001

CALIBRATED = dict(
    capital_return=0.08, rent_share_of_wage=0.20,
    subsistence=0.30, interest_rate=0.06,
    inheritance_tax_rate=0.0, inheritance_cap=float("inf"),
    wealth_tax_tiers=(),
)
SPEND = dict(ubi=0.4, state_employs_fraction=0.3,
              state_employs_wage=0.8, state_buys_maker_output=5.0)
NO_SPEND = dict(ubi=0.0, state_employs_fraction=0.0,
                 state_employs_wage=1.0, state_buys_maker_output=0.0)

ARMS = {
    "A_status_quo":    {**NO_SPEND},
    "D_cap_5M":        {**SPEND, "inheritance_cap": 50.0},
    "E_hybrid_5pct":   {**SPEND, "wealth_tax_tiers": ((100.0, 0.05),)},
    "F_hybrid_10pct":  {**SPEND, "wealth_tax_tiers": ((100.0, 0.10),)},
}

ELASTICITIES = [0.0, 0.25, 0.5, 0.75, 1.0]


def _run(args):
    arm, elasticity, seed = args
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[arm])
    overrides["rd_share_of_maker_wealth"] = RD_SHARE_MAKER
    overrides["rd_share_of_employer_wealth"] = RD_SHARE_EMPLOYER
    overrides["rd_innovation_coeff"] = RD_INNOVATION_COEFF
    overrides["rd_skill_breadth_elasticity"] = elasticity

    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    productive_series = []
    innovation_series = []
    rd_budget_series = []
    breadth_series = []
    prod_mult_series = []

    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        if t >= WINDOW_START:
            productive_series.append(h["productive_flow"])
            innovation_series.append(h["innovation_rate"])
            rd_budget_series.append(h["rd_budget"])
            breadth_series.append(h["cultural_breadth"])
            prod_mult_series.append(h["productivity_multiplier"])

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))

    ps = np.array(productive_series)
    if len(ps) >= 40 and ps[:20].mean() > 0:
        early = float(ps[:20].mean())
        late = float(ps[-20:].mean())
        pt_growth = ((late / early) ** (1.0 / (len(ps) - 20))) - 1.0
    else:
        pt_growth = 0.0

    return arm, elasticity, seed, {
        "PT_cum": float(ps.sum()),
        "PT_growth": float(pt_growth),
        "innovation_mean": float(np.mean(innovation_series))
                           if innovation_series else 0.0,
        "innovation_cum": float(np.sum(innovation_series))
                          if innovation_series else 0.0,
        "rd_budget_mean": float(np.mean(rd_budget_series))
                          if rd_budget_series else 0.0,
        "breadth_mean": float(np.mean(breadth_series))
                         if breadth_series else 0.0,
        "productivity_multiplier_final": float(prod_mult_series[-1])
                                          if prod_mult_series else 1.0,
        "bottom_50_share": bot50,
        "survival": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
    }


def main():
    args = [(a, e, s) for a in ARMS for e in ELASTICITIES
             for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    print(f"  R&D: share_maker={RD_SHARE_MAKER}, "
          f"share_employer={RD_SHARE_EMPLOYER}, "
          f"innovation_coeff={RD_INNOVATION_COEFF}")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s\n")

    by_cell: dict = {}
    for arm, e, _, m in results:
        by_cell.setdefault((arm, e), []).append(m)

    summary: dict = {}
    for (arm, e), ms in by_cell.items():
        keys = ms[0].keys()
        summary[f"{arm}__elast_{e}"] = {
            k: float(np.mean([m[k] for m in ms])) for k in keys
        }

    print("=" * 100)
    print("Path-C C1 SWEEP: PT growth rate (per-tick %), R&D budget, "
          "productivity multiplier")
    print("=" * 100)
    print(f"{'arm':<18} | " +
          " | ".join(f"el={e:.2f}" for e in ELASTICITIES))
    print("-" * (20 + 12 * len(ELASTICITIES)))
    for arm in ARMS:
        print(f"\n{arm}")
        for metric, label in [
            ("PT_growth", "PT growth %"),
            ("innovation_mean", "innov rate"),
            ("rd_budget_mean", "RD budget"),
            ("breadth_mean", "breadth"),
            ("productivity_multiplier_final", "prod mult"),
        ]:
            row = []
            for e in ELASTICITIES:
                v = summary[f"{arm}__elast_{e}"][metric]
                if metric == "PT_growth":
                    row.append(f"{v*100:+6.3f}%")
                elif metric in ("rd_budget_mean", "productivity_multiplier_final"):
                    row.append(f"{v:>9.3f}")
                else:
                    row.append(f"{v:>9.4f}")
            print(f"  {label:<18} | " + " | ".join(row))

    print()
    print("=" * 100)
    print("HYPOTHESIS TEST: PT growth rate, wealth-tax arm minus status quo")
    print("=" * 100)
    print(f"{'arm':<18} | " +
          " | ".join(f"el={e:.2f}" for e in ELASTICITIES))
    print("-" * (20 + 12 * len(ELASTICITIES)))
    for arm in ARMS:
        if arm == "A_status_quo":
            continue
        row = []
        for e in ELASTICITIES:
            sq = summary[f"A_status_quo__elast_{e}"]["PT_growth"]
            ar = summary[f"{arm}__elast_{e}"]["PT_growth"]
            diff = (ar - sq) * 100
            marker = " WIN" if diff > 0.01 else (" LOSE" if diff < -0.01 else "  --")
            row.append(f"{diff:+6.3f}{marker}")
        print(f"{arm:<18} | " + " | ".join(row))

    print()
    print("READING THE RESULT:")
    print("  WIN  = wealth-tax arm PT-growth > status quo by >0.01pp/tick")
    print("  LOSE = wealth-tax arm PT-growth < status quo by >0.01pp/tick")
    print("  Find the lowest elasticity at which the wealth tax wins.")
    print("  If wealth tax wins at elasticity 0.5 or below, C1 confirms")
    print("  the heterodox hypothesis at empirically calibrated parameters.")

    out_path = OUT_DATA / "path_c_rd.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
