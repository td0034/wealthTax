"""
Round 2 kill-switch: does the cap deliver bottom-50% wealth share that
high IHT plus the same state-spending package cannot?

Five arms at joint-calibrated UK baseline (r=0.08, rent=0.20, sub=0.30):
  A status_quo            no cap, no IHT, no state spending package
  B spend_only            no cap, no IHT, state spending on (UBI + state jobs)
  C iht40_spend           no cap, IHT 40% at death, state spending on
  D cap_spend             £5M cap, no IHT, state spending on   (paper headline)
  E cap_iht_spend         £5M cap + IHT 40% + state spending

Decomposition:
  bottom-50% share lift attributable to:
    recirculation (B - A)
    IHT-plus-recirculation (C - A)
    cap-plus-recirculation (D - A)
    cap-specific contribution beyond IHT (D - C)
    both stacked (E - A)

If (D - C) is small, the cap adds nothing beyond what IHT-plus-spending
delivers, and the paper's central claim collapses.
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

SCALE = 100        # N = 10,000
TICKS = 180
SEEDS = 4

CALIBRATED = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    interest_rate=0.06,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    wealth_tax_tiers=(),
)

SPEND = dict(
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)

NO_SPEND = dict(
    ubi=0.0,
    state_employs_fraction=0.0,
    state_employs_wage=1.0,
    state_buys_maker_output=0.0,
)

ARMS = {
    "A_status_quo":    {**NO_SPEND},
    "B_spend_only":    {**SPEND},
    "C_iht40_spend":   {**SPEND, "inheritance_tax_rate": 0.40},
    "D_cap_spend":     {**SPEND, "inheritance_cap": 50.0},
    "E_cap_iht_spend": {**SPEND, "inheritance_cap": 50.0,
                         "inheritance_tax_rate": 0.40},
}


def _run(args):
    name, seed = args
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[name])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    tax_history = []
    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        tax_history.append(h["tax_collected"])

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    nws_sorted = np.sort(nws)
    gbp = nws * WEALTH_UNIT_GBP
    state_agent = next((a for a in agents
                        if a.type == Type.STATE and a.alive), None)

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bottom_50_share = float(nws_sorted[: n // 2].sum() / max(total_w, 1e-9))
    top_10_share = float(np.sort(nws)[::-1][: max(1, n // 10)].sum()
                          / max(total_w, 1e-9))
    top_1_share = float(np.sort(nws)[::-1][: max(1, n // 100)].sum()
                         / max(total_w, 1e-9))

    return name, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "bottom_50_share": bottom_50_share,
        "top_10_share": top_10_share,
        "top_1_share": top_1_share,
        "median_wealth_gbp": float(np.median(gbp)) if len(gbp) else 0.0,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
        "tax_revenue_cumulative_gbp": float(np.sum(tax_history)) * WEALTH_UNIT_GBP,
    }


def main():
    args = [(n, s) for n in ARMS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_arm: dict[str, list[dict]] = {}
    for n, _, m in results:
        by_arm.setdefault(n, []).append(m)

    summary: dict[str, dict] = {}
    for n, ms in by_arm.items():
        keys = ms[0].keys()
        summary[n] = {k: float(np.mean([m[k] for m in ms])) for k in keys}
        for k in keys:
            summary[n][k + "_sd"] = float(np.std([m[k] for m in ms], ddof=1))

    fmt = lambda v: f"{v*100:.1f}%"
    print()
    print(f"{'arm':<20} {'alive':>7} {'bn':>5} "
          f"{'bottom-50':>10} {'top-10':>10} {'top-1':>10} "
          f"{'state £B':>10}")
    for arm in ARMS:
        s = summary[arm]
        print(f"{arm:<20} {s['alive_rate']*100:>6.1f}% "
              f"{s['billionaires']:>5.0f} "
              f"{fmt(s['bottom_50_share']):>10} "
              f"{fmt(s['top_10_share']):>10} "
              f"{fmt(s['top_1_share']):>10} "
              f"{s['state_wealth_final_gbp']/1e9:>9.0f}B")

    print()
    print("DECOMPOSITION (mean bottom-50% share):")
    bA = summary["A_status_quo"]["bottom_50_share"]
    bB = summary["B_spend_only"]["bottom_50_share"]
    bC = summary["C_iht40_spend"]["bottom_50_share"]
    bD = summary["D_cap_spend"]["bottom_50_share"]
    bE = summary["E_cap_iht_spend"]["bottom_50_share"]
    print(f"  A status quo                  {bA*100:>5.1f}%")
    print(f"  B + recirculation alone       {bB*100:>5.1f}%  (delta {(bB-bA)*100:+.1f})")
    print(f"  C + IHT40 + recirculation     {bC*100:>5.1f}%  (delta {(bC-bA)*100:+.1f})")
    print(f"  D + cap  + recirculation      {bD*100:>5.1f}%  (delta {(bD-bA)*100:+.1f})")
    print(f"  E + cap + IHT40 + recirc      {bE*100:>5.1f}%  (delta {(bE-bA)*100:+.1f})")
    print()
    print(f"  cap-specific lift beyond IHT  {(bD-bC)*100:+.1f}pp")
    print(f"  IHT-specific lift beyond cap  {(bC-bD)*100:+.1f}pp")
    print(f"  stacking gain (E - max(C,D))  {(bE - max(bC,bD))*100:+.1f}pp")

    out_path = OUT_DATA / "round2_killswitch.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
