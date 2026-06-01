"""
Round 2 R2-6: Equal-revenue wealth tax head-to-head.

Hunt's strongest constructive critique: the wealth tax is the
proportionate instrument. The paper should show what an equal-revenue
wealth tax achieves, head-to-head with the cap.

Method:
  1. Run the cap (£5M, 100% capture, with spending package) and record
     ending state wealth.
  2. Sweep wealth-tax rates over £10M threshold to find the rate that
     produces the same ending state wealth as the cap.
  3. Report bottom-50% share, top-10% share, billionaire count at the
     equal-revenue WT rate.

This isolates the cap-specific distributional contribution holding
state revenue constant.
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
SEEDS = 4
CAP_UNITS = 50.0

CALIBRATED = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    interest_rate=0.06,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    wealth_tax_tiers=(),
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)

# Wealth tax rates to sweep (annual, above £10M threshold).
WT_RATES = [0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
# Plus the cap arm as a reference.
ARMS = ["cap"] + [f"wt_{r}" for r in WT_RATES]


def _config_for(arm: str) -> dict:
    overrides = dict(CALIBRATED)
    if arm == "cap":
        overrides["inheritance_cap"] = CAP_UNITS
    elif arm.startswith("wt_"):
        rate = float(arm[3:])
        overrides["wealth_tax_tiers"] = ((100.0, rate),)
    return overrides


def _run(args):
    arm, seed = args
    overrides = _config_for(arm)
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    for t in range(TICKS):
        step(agents, d, rng, t, accum)

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    state_agent = next((a for a in agents
                        if a.type == Type.STATE and a.alive), None)

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))
    top10 = float(np.sort(nws)[::-1][: max(1, n // 10)].sum() / max(total_w, 1e-9))
    top1 = float(np.sort(nws)[::-1][: max(1, n // 100)].sum() / max(total_w, 1e-9))

    return arm, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centimillionaires": int((gbp >= 1e8).sum()),
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "top_1_share": top1,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
    }


def main():
    args = [(arm, s) for arm in ARMS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_arm: dict[str, list[dict]] = {}
    for arm, _, m in results:
        by_arm.setdefault(arm, []).append(m)

    summary: dict[str, dict] = {}
    for arm, ms in by_arm.items():
        keys = ms[0].keys()
        summary[arm] = {k: float(np.mean([m[k] for m in ms])) for k in keys}

    print()
    print(f"{'arm':<14} {'alive':>7} {'bn':>5} {'£100M+':>7} "
          f"{'bot-50':>8} {'top-10':>8} {'top-1':>8} {'state £B':>10}")
    cap_revenue = summary["cap"]["state_wealth_final_gbp"]
    for arm in ARMS:
        s = summary[arm]
        rev = s["state_wealth_final_gbp"]
        marker = " <-- match" if (arm != "cap" and abs(rev - cap_revenue) < cap_revenue * 0.5) else ""
        print(f"{arm:<14} {s['alive_rate']*100:>6.1f}% "
              f"{s['billionaires']:>5.0f} "
              f"{s['centimillionaires']:>7.0f} "
              f"{s['bottom_50_share']*100:>7.1f}% "
              f"{s['top_10_share']*100:>7.1f}% "
              f"{s['top_1_share']*100:>7.1f}% "
              f"{rev/1e9:>9.0f}B{marker}")

    print(f"\nCap revenue target: £{cap_revenue/1e9:.0f}B")

    out_path = OUT_DATA / "round2_equal_revenue.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
