"""
Round 2 R2-4: Enforcement friction.

Stewart's critique: HMRC cannot actually capture 100% of bequest excess
above any cap. Valuation discounts, BPR/APR carve-outs, trust law,
foreign assets, AIM shares, art, all reduce the effective capture rate.
The paper's implicit 100% enforcement is implausible.

Implementation:

  Added a Dials field `inheritance_capture_rate` in {0.0, ..., 1.0}.
  At each death the excess above the cap is split:
    captured -> state at rate `inheritance_capture_rate`
    leaks to heir at rate (1 - inheritance_capture_rate)

  Sweep capture rates {0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0} for the cap
  arms. The realistic UK range based on current IHT effective rates is
  roughly 0.3-0.6.

Question to answer: how much of the cap's distributional effect
survives realistic enforcement friction?
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

CAPTURE_RATES = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def _run(args):
    capture_rate, seed = args
    overrides = dict(CALIBRATED)
    overrides["inheritance_cap"] = CAP_UNITS
    overrides["inheritance_capture_rate"] = capture_rate
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

    return capture_rate, seed, {
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
    args = [(c, s) for c in CAPTURE_RATES for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_rate: dict[float, list[dict]] = {}
    for cr, _, m in results:
        by_rate.setdefault(cr, []).append(m)

    summary: dict[str, dict] = {}
    for cr, ms in by_rate.items():
        keys = ms[0].keys()
        summary[f"capture_{cr}"] = {
            k: float(np.mean([m[k] for m in ms])) for k in keys
        }

    print()
    print(f"{'capture':>8}  {'alive':>7} {'bn':>5} {'£100M+':>7} "
          f"{'bot-50':>8} {'top-10':>8} {'top-1':>8} {'state £B':>10}")
    for cr in CAPTURE_RATES:
        s = summary[f"capture_{cr}"]
        print(f"{cr:>7.2f}   {s['alive_rate']*100:>6.1f}% "
              f"{s['billionaires']:>5.0f} "
              f"{s['centimillionaires']:>7.0f} "
              f"{s['bottom_50_share']*100:>7.1f}% "
              f"{s['top_10_share']*100:>7.1f}% "
              f"{s['top_1_share']*100:>7.1f}% "
              f"{s['state_wealth_final_gbp']/1e9:>9.0f}B")

    out_path = OUT_DATA / "round2_enforcement.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
