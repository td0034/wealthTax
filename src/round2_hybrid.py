"""
Round 2 R2-9 + R2-10: Steep wealth tax as a hybrid instrument.

Hypothesis: a wealth tax rate above r (capital return) approximates
the cap as rate -> 1. Crucially, it operates on the living, is
recurrent (errors are correctable next year), and the dynastic
recompounding nonlinearity that destroys the cap at <100% enforcement
does not apply because each year's tax compounds against the prior
year's wealth.

If rate t > r, net growth (r - t) is negative; wealth shrinks
deterministically toward the threshold even at imperfect enforcement.

Experiments:
  R2-9 (perfect enforcement): sweep wealth-tax rates {0.02, 0.05, 0.10,
       0.20, 0.50, 0.90} above thresholds {£10M, £50M}. Compare
       distributional outcomes to the £5M cap.
  R2-10 (enforcement sensitivity): take the most promising rate from
       R2-9 and sweep wealth_tax_capture_rate 0.4-1.0. Compare with
       R2-4 cap enforcement curve.
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
CAP_UNITS = 50.0       # £5M
T10M = 100.0           # £10M
T50M = 500.0           # £50M

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


def _arms_r2_9() -> dict:
    """R2-9: rate sweep at perfect enforcement."""
    arms = {
        "cap_5M":    {"inheritance_cap": CAP_UNITS},
        "wt2_10M":   {"wealth_tax_tiers": ((T10M, 0.02),)},
        "wt5_10M":   {"wealth_tax_tiers": ((T10M, 0.05),)},
        "wt10_10M":  {"wealth_tax_tiers": ((T10M, 0.10),)},
        "wt20_10M":  {"wealth_tax_tiers": ((T10M, 0.20),)},
        "wt50_10M":  {"wealth_tax_tiers": ((T10M, 0.50),)},
        "wt90_10M":  {"wealth_tax_tiers": ((T10M, 0.90),)},
        "wt5_50M":   {"wealth_tax_tiers": ((T50M, 0.05),)},
        "wt10_50M":  {"wealth_tax_tiers": ((T50M, 0.10),)},
        "wt20_50M":  {"wealth_tax_tiers": ((T50M, 0.20),)},
        "wt50_50M":  {"wealth_tax_tiers": ((T50M, 0.50),)},
        "wt90_50M":  {"wealth_tax_tiers": ((T50M, 0.90),)},
    }
    return arms


def _run(args):
    arm_name, overrides, seed = args
    config = dict(CALIBRATED)
    config.update(overrides)
    d = Dials(seed=seed, population_scale=SCALE, **config)
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
    gbp = nws * WEALTH_UNIT_GBP
    state_agent = next((a for a in agents
                        if a.type == Type.STATE and a.alive), None)

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))
    top10 = float(np.sort(nws)[::-1][: max(1, n // 10)].sum() / max(total_w, 1e-9))
    top1 = float(np.sort(nws)[::-1][: max(1, n // 100)].sum() / max(total_w, 1e-9))

    return arm_name, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centimillionaires": int((gbp >= 1e8).sum()),
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "top_1_share": top1,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
        "tax_revenue_cum_gbp": float(np.sum(tax_history)) * WEALTH_UNIT_GBP,
    }


def run_r2_9():
    arms = _arms_r2_9()
    args = [(name, ov, s) for name, ov in arms.items() for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"R2-9: running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_arm: dict[str, list[dict]] = {}
    for name, _, m in results:
        by_arm.setdefault(name, []).append(m)

    summary: dict[str, dict] = {}
    for name, ms in by_arm.items():
        keys = ms[0].keys()
        summary[name] = {k: float(np.mean([m[k] for m in ms])) for k in keys}

    print()
    print(f"{'arm':<14} {'alive':>7} {'bn':>5} {'£100M+':>7} "
          f"{'bot-50':>8} {'top-10':>8} {'top-1':>8} "
          f"{'state £B':>10} {'tax £B':>10}")
    for name in arms:
        s = summary[name]
        print(f"{name:<14} {s['alive_rate']*100:>6.1f}% "
              f"{s['billionaires']:>5.0f} "
              f"{s['centimillionaires']:>7.0f} "
              f"{s['bottom_50_share']*100:>7.1f}% "
              f"{s['top_10_share']*100:>7.1f}% "
              f"{s['top_1_share']*100:>7.1f}% "
              f"{s['state_wealth_final_gbp']/1e9:>9.0f}B "
              f"{s['tax_revenue_cum_gbp']/1e9:>9.0f}B")

    (OUT_DATA / "round2_hybrid_r9.json").write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {OUT_DATA / 'round2_hybrid_r9.json'}")
    return summary


def _run_enforce(args):
    """R2-10: hybrid with enforcement leakage."""
    arm_name, overrides, capture_rate, seed = args
    config = dict(CALIBRATED)
    config.update(overrides)
    config["wealth_tax_capture_rate"] = capture_rate
    d = Dials(seed=seed, population_scale=SCALE, **config)
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

    return arm_name, capture_rate, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centimillionaires": int((gbp >= 1e8).sum()),
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "top_1_share": top1,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
    }


def run_r2_10(focus_arm: str, focus_overrides: dict):
    """Sweep enforcement on the chosen hybrid arm."""
    CAPTURE_RATES = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    args = [(focus_arm, focus_overrides, cr, s)
             for cr in CAPTURE_RATES
             for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"\nR2-10: running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run_enforce, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_cr: dict[float, list[dict]] = {}
    for _, cr, _, m in results:
        by_cr.setdefault(cr, []).append(m)

    summary: dict[str, dict] = {}
    for cr, ms in by_cr.items():
        keys = ms[0].keys()
        summary[f"capture_{cr}"] = {
            k: float(np.mean([m[k] for m in ms])) for k in keys
        }

    print()
    print(f"hybrid arm: {focus_arm}")
    print(f"{'capture':>8} {'alive':>7} {'bn':>5} {'£100M+':>7} "
          f"{'bot-50':>8} {'top-10':>8} {'top-1':>8} {'state £B':>10}")
    for cr in CAPTURE_RATES:
        s = summary[f"capture_{cr}"]
        print(f"{cr:>7.2f}  {s['alive_rate']*100:>6.1f}% "
              f"{s['billionaires']:>5.0f} "
              f"{s['centimillionaires']:>7.0f} "
              f"{s['bottom_50_share']*100:>7.1f}% "
              f"{s['top_10_share']*100:>7.1f}% "
              f"{s['top_1_share']*100:>7.1f}% "
              f"{s['state_wealth_final_gbp']/1e9:>9.0f}B")

    out_path = OUT_DATA / "round2_hybrid_r10.json"
    out_path.write_text(json.dumps(
        {"focus_arm": focus_arm, "overrides": focus_overrides,
         "results": summary}, indent=2))
    print(f"\nsaved {out_path}")


def main():
    s9 = run_r2_9()
    # Pick the most promising hybrid arm: lowest top-1 share among
    # WT arms (most cap-like distribution) with the highest threshold
    # (least disruptive at the median upper-class wealth).
    candidates = [
        ("wt50_10M", {"wealth_tax_tiers": ((T10M, 0.50),)}),
        ("wt90_10M", {"wealth_tax_tiers": ((T10M, 0.90),)}),
        ("wt20_50M", {"wealth_tax_tiers": ((T50M, 0.20),)}),
        ("wt50_50M", {"wealth_tax_tiers": ((T50M, 0.50),)}),
    ]
    # Find the one with best (lowest) top-1 share.
    best = min(candidates, key=lambda c: s9[c[0]]["top_1_share"])
    print(f"\nR2-10 will use: {best[0]} (top_1_share={s9[best[0]]['top_1_share']*100:.1f}%)")
    run_r2_10(best[0], best[1])


if __name__ == "__main__":
    main()
