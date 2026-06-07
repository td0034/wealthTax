"""
20-seed run of the five policy arms at the R0 baseline regime, with
per-seed measure logging for bootstrap CIs.

Same model and arms as growth_portfolio.py, just SEEDS=20 and
per-seed output saved. We restrict to R0 (no productivity channel)
because the qualitative pattern is invariant across regimes and the
CI work is most informative on the level-effect numbers.
"""
from __future__ import annotations

import json
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, Type, WEALTH_UNIT_GBP, make_initial_population, step

OUT_DATA = Path("out/data")
SCALE = 100
TICKS = 180
WINDOW_START = 80
SEEDS = 20
ALPHA_GDP = 0.20

CALIBRATED = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    interest_rate=0.06,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    wealth_tax_tiers=(),
)
SPEND = dict(ubi=0.4, state_employs_fraction=0.3,
              state_employs_wage=0.8, state_buys_maker_output=5.0)
NO_SPEND = dict(ubi=0.0, state_employs_fraction=0.0,
                 state_employs_wage=1.0, state_buys_maker_output=0.0)

ARMS = {
    "A_status_quo":    {**NO_SPEND},
    "C_zucman_2pct":   {**SPEND, "wealth_tax_tiers": ((100.0, 0.02),)},
    "D_cap_5M":        {**SPEND, "inheritance_cap": 50.0},
    "E_hybrid_5pct":   {**SPEND, "wealth_tax_tiers": ((100.0, 0.05),)},
    "F_hybrid_10pct":  {**SPEND, "wealth_tax_tiers": ((100.0, 0.10),)},
}


def _run(args):
    arm, seed = args
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[arm])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    productive_sum = 0.0
    extractive_sum = 0.0
    breadth_window = []
    diversity_window = []
    phi_window = []
    alive_window = []
    productive_series = []

    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        if t >= WINDOW_START:
            productive_sum += h["productive_flow"]
            extractive_sum += h["extractive_flow"]
            breadth_window.append(h["cultural_breadth"])
            diversity_window.append(h["cultural_diversity"])
            phi_window.append(h["autocatalytic_closure"])
            alive_window.append(h["alive"])
            productive_series.append(h["productive_flow"])

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    workers = [a for a in living if a.type == Type.WORKER]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    total_skill = float(sum(a.skill_total for a in living))
    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))

    survival = len(living) / max(initial_nonstate, 1)
    breadth_term = float(np.mean(breadth_window))
    diversity_term = float(np.mean(diversity_window))
    ci_terminal = survival * breadth_window[-1] * diversity_window[-1]

    # PT growth: window early vs late.
    ps = np.array(productive_series)
    if len(ps) >= 40 and ps[:20].mean() > 0:
        n_t = len(ps) - 20
        pt_growth = float(((ps[-20:].mean() / ps[:20].mean()) ** (1.0 / n_t)) - 1.0)
    else:
        pt_growth = 0.0

    return arm, seed, {
        "GMT_cum": productive_sum + extractive_sum,
        "PT_cum": productive_sum,
        "CGDP_cum": productive_sum + ALPHA_GDP * extractive_sum,
        "CI_terminal": float(ci_terminal),
        "KS_total_skill": total_skill,
        "MC_median_worker_gbp": (
            float(np.median([max(0.0, a.net_worth) for a in workers])
                    * WEALTH_UNIT_GBP)
            if workers else 0.0
        ),
        "bottom_50_share": bot50,
        "billionaires": int((gbp >= 1e9).sum()),
        "survival": survival,
        "phi_mean": float(np.mean(phi_window)),
        "breadth_mean": breadth_term,
        "diversity_mean": diversity_term,
        "PT_growth": pt_growth,
    }


def main():
    args = [(a, s) for a in ARMS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s\n")

    # Save per-seed.
    per_seed: dict = {}
    for arm, seed, m in results:
        per_seed.setdefault(arm, {})[str(seed)] = m
    out = OUT_DATA / "growth_seeds20.json"
    out.write_text(json.dumps(per_seed, indent=2))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
