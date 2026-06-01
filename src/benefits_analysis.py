"""
Benefits analysis: what each policy intervention does *to* the
economy (productive activity, middle-class wealth, public revenue),
not just *against* billionaires.

For each of five interventions at the joint-calibrated UK baseline:
  - Total revenue raised (wealth tax + inheritance excess to state)
  - Final state wealth (stock)
  - Median private wealth (middle-class proxy)
  - Bottom-50% wealth share
  - Top-10% wealth share
  - Average productive-flow share (Phi)
  - Total value created (cumulative metabolic rate)
  - Survival to terminal tick

Usage: python3 benefits_analysis.py
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, Type, WEALTH_UNIT_GBP, make_initial_population, step

OUT = Path("out/figures/scenarios")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)

SCALE = 100              # N = 10,000
TICKS = 180
SEEDS = 4


BASE = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    interest_rate=0.06,
    wealth_tax_tiers=(),
    # State spending package: needed to recirculate revenue.
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)

POLICIES = {
    "status_quo":      dict(),
    "zucman_2pct":     dict(wealth_tax_tiers=((100.0, 0.02),)),
    "interest_ban":    dict(interest_rate=0.0),
    "bequest_cap_5M":  dict(inheritance_cap=50.0),
    "zucman_plus_cap": dict(wealth_tax_tiers=((100.0, 0.02),),
                             inheritance_cap=50.0),
}


def _run(args):
    name, seed = args
    overrides = dict(BASE)
    overrides.update(POLICIES[name])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    tax_history = []
    phi_history = []
    metabolic_history = []
    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        tax_history.append(h["tax_collected"])
        phi_history.append(h["autocatalytic_closure"])
        metabolic_history.append(h["metabolic_rate"])

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

    return name, seed, {
        "alive": len(living),
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "median_wealth_gbp": float(np.median(gbp)) if len(gbp) else 0.0,
        "mean_wealth_gbp": float(np.mean(gbp)) if len(gbp) else 0.0,
        "bottom_50_share": bottom_50_share,
        "top_10_share": top_10_share,
        "phi_mean": float(np.mean(phi_history)),
        "phi_last_quarter": float(np.mean(phi_history[-TICKS // 4:])),
        "metabolic_cumulative": float(np.sum(metabolic_history)),
        "tax_revenue_cumulative_gbp": float(np.sum(tax_history)) * WEALTH_UNIT_GBP,
        "tax_revenue_per_tick_gbp": (float(np.mean(tax_history[-TICKS // 2:]))
                                      * WEALTH_UNIT_GBP),
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
    }


def main():
    args = [(n, s) for n in POLICIES for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_policy: dict[str, list[dict]] = {}
    for n, s, m in results:
        by_policy.setdefault(n, []).append(m)

    summary = {}
    print()
    print(f"{'policy':<20} {'alive %':>8} {'bil':>4} "
          f"{'median £':>11} {'bottom 50%':>11} {'top 10%':>9} "
          f"{'Phi':>5} {'metab':>9} {'revenue/yr':>13}")
    for name in POLICIES:
        runs = by_policy[name]
        med = {k: float(np.median([r[k] for r in runs]))
               for k in runs[0]}
        summary[name] = med
        print(f"{name:<20} {med['alive_rate']*100:>7.0f}% "
              f"{med['billionaires']:>4.0f} "
              f"£{med['median_wealth_gbp']/1e3:>8.0f}k "
              f"{med['bottom_50_share']*100:>10.1f}% "
              f"{med['top_10_share']*100:>8.1f}% "
              f"{med['phi_last_quarter']:>5.2f} "
              f"{med['metabolic_cumulative']/1e3:>7.1f}k "
              f"£{med['tax_revenue_per_tick_gbp']/1e9:>10.2f}B")

    with open(OUT_DATA / "benefits_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nsaved {OUT_DATA / 'benefits_summary.json'}")

    # =================================================================
    # The figure: positive-case dashboard
    # =================================================================
    policy_order = ["status_quo", "zucman_2pct", "interest_ban",
                    "bequest_cap_5M", "zucman_plus_cap"]
    display_names = {
        "status_quo":      "status quo",
        "zucman_2pct":     "Zucman 2%",
        "interest_ban":    "interest ban",
        "bequest_cap_5M":  "£5M cap",
        "zucman_plus_cap": "cap + Zucman",
    }
    names = [display_names[p] for p in policy_order]

    median_wealth = [summary[p]["median_wealth_gbp"] / 1e3 for p in policy_order]
    bottom_share  = [summary[p]["bottom_50_share"] * 100 for p in policy_order]
    phi_vals      = [summary[p]["phi_last_quarter"] for p in policy_order]
    revenue       = [summary[p]["tax_revenue_per_tick_gbp"] / 1e9
                      for p in policy_order]
    metabolic     = [summary[p]["metabolic_cumulative"] / 1e3
                      for p in policy_order]

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))

    colours = ["#9ca3af", "#3b82f6", "#a855f7", "#16a34a", "#0f766e"]

    def _bar(ax, vals, title, ylabel, fmt="{:.1f}", suffix=""):
        bars = ax.bar(names, vals, color=colours, width=0.55)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v,
                    fmt.format(v) + suffix,
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.grid(alpha=0.3, axis="y")
        ax.set_axisbelow(True)

    _bar(axes[0, 0], median_wealth,
         "Median wealth of a surviving agent",
         "median wealth (£k)", fmt="£{:.0f}k")
    _bar(axes[0, 1], bottom_share,
         "Wealth share held by the bottom 50% of the population",
         "share (%)", fmt="{:.1f}", suffix="%")
    _bar(axes[1, 0], phi_vals,
         "Productive-flow share Φ (final quarter)",
         "Φ (final quarter)", fmt="{:.2f}")
    _bar(axes[1, 1], revenue,
         "State revenue per year (steady state, last 90 ticks)",
         "revenue / year (£B)", fmt="£{:.1f}B")

    fig.suptitle("What each intervention does FOR the economy, not just "
                 "AGAINST billionaires\n"
                 f"(joint-calibrated UK baseline, $r=0.08$, $N={SCALE*100:,}$, "
                 f"{SEEDS} seeds, with state-spending package on)",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "benefits_dashboard.png", dpi=140)
    plt.close(fig)
    print(f"saved {OUT / 'benefits_dashboard.png'}")


if __name__ == "__main__":
    main()
