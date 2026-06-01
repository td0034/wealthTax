"""
The elegant demonstration: comparing the three structural interventions
that shrink the stocks that grow on their own.

  status_quo     : do nothing
  zucman_2pct    : 2% wealth tax above £10M (the G20 proposal)
  bequest_cap_5M : absolute £5M cap on inheritance, no wealth tax
  zucman_plus_cap: both
  interest_ban   : i = 0, no wealth tax, no cap (a usury-ban analogue)

All five run at the joint-calibrated baseline (r=0.08, rent=0.20,
subsistence=0.30) which matches the UK Pareto slope with realistic
demographics. N=10,000, 5 seeds, 180 ticks.

The plot shows billionaire count (log) and alive % side-by-side
across all five policies; that is the single artefact that lets a
reader see the central claim at a glance.

Usage: python3 elegant_demo.py
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
SEEDS = 5

# Joint-calibrated baseline (matches UK Pareto slope at 80% survival)
BASE = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    inheritance_tax_rate=0.0,   # leave to be a control; only the cap toggles
    inheritance_cap=float("inf"),
    interest_rate=0.06,         # default; interest_ban scenario overrides
    wealth_tax_tiers=(),
)

POLICIES = {
    "status_quo": dict(),
    "zucman_2pct": dict(
        wealth_tax_tiers=((100.0, 0.02),),
    ),
    "bequest_cap_5M": dict(
        inheritance_cap=50.0,   # 50 model units = £5M
    ),
    "zucman_plus_cap": dict(
        wealth_tax_tiers=((100.0, 0.02),),
        inheritance_cap=50.0,
    ),
    "interest_ban": dict(
        interest_rate=0.0,
    ),
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
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    sorted_gbp = np.sort(gbp)[::-1] if len(gbp) else np.array([0.0])
    return name, seed, {
        "alive": len(living),
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centi_millionaires": int((gbp >= 1e8).sum()),
        "deci_millionaires": int((gbp >= 1e7).sum()),
        "max_wealth_gbp": float(sorted_gbp[0]),
        "top1_share": float(sorted_gbp[: max(1, len(gbp) // 100)].sum()
                            / max(gbp.sum(), 1e-9)),
        "top10_share": float(sorted_gbp[: max(1, len(gbp) // 10)].sum()
                             / max(gbp.sum(), 1e-9)),
    }


def main():
    args = [(name, s) for name in POLICIES for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs at calibrated baseline ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_policy: dict[str, list[dict]] = {}
    for name, seed, m in results:
        by_policy.setdefault(name, []).append(m)

    summary = {}
    print()
    print(f"{'policy':<20} {'alive %':>8} {'>=£1B':>7} {'>=£100M':>9} "
          f"{'>=£10M':>8} {'top-1 share':>12}")
    for name in POLICIES:
        runs = by_policy[name]
        med = {k: float(np.median([r[k] for r in runs]))
               for k in runs[0]}
        summary[name] = med
        print(f"{name:<20} {med['alive_rate'] * 100:>7.0f}% "
              f"{med['billionaires']:>7.0f} {med['centi_millionaires']:>9.0f} "
              f"{med['deci_millionaires']:>8.0f} {med['top1_share']:>12.3f}")

    with open(OUT_DATA / "elegant_demo_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # ===================================================================
    # The figure
    # ===================================================================
    policy_order = ["status_quo", "zucman_2pct", "interest_ban",
                    "bequest_cap_5M", "zucman_plus_cap"]
    display_names = {
        "status_quo":      "status quo\n(do nothing)",
        "zucman_2pct":     "Zucman:\n2% above £10M",
        "interest_ban":    "interest ban\n(i = 0)",
        "bequest_cap_5M":  "bequest cap:\n£5M absolute",
        "zucman_plus_cap": "Zucman 2%\n+ bequest cap",
    }

    bils = [summary[p]["billionaires"] for p in policy_order]
    alives = [summary[p]["alive_rate"] * 100 for p in policy_order]
    centi = [summary[p]["centi_millionaires"] for p in policy_order]
    deci = [summary[p]["deci_millionaires"] for p in policy_order]

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(11, 8.5),
                                          gridspec_kw={"height_ratios": [3, 2]},
                                          sharex=True)

    # Top: wealthy population per tier, log scale.
    x = np.arange(len(policy_order))
    width = 0.27
    ax_top.bar(x - width, deci, width, label="≥ £10M",
                color="#6b7280")
    ax_top.bar(x, centi, width, label="≥ £100M",
                color="#0ea5e9")
    bars_b = ax_top.bar(x + width, bils, width, label="≥ £1B (billionaires)",
                         color="#dc2626")
    for bar, val in zip(bars_b, bils):
        ax_top.text(bar.get_x() + bar.get_width() / 2,
                     max(val, 0.6),
                     str(int(val)),
                     ha="center", va="bottom", fontsize=11,
                     fontweight="bold", color="#7f1d1d")
    ax_top.set_yscale("log")
    ax_top.set_ylabel("agents above wealth threshold\n(out of 10,000, log scale)",
                       fontsize=11)
    ax_top.legend(loc="upper right", fontsize=10)
    ax_top.grid(alpha=0.3, axis="y", which="both")
    ax_top.set_axisbelow(True)
    ax_top.set_title("The three interventions, side by side\n"
                      "(joint-calibrated baseline: $r=0.08$, rent=0.20, "
                      "subsistence=0.30; $N=10{,}000$, 5 seeds)",
                      fontsize=12)

    # Bottom: alive rate as a bar (color-coded).
    colours_alive = ["#dc2626" if a < 50 else
                       "#f59e0b" if a < 70 else
                       "#16a34a" for a in alives]
    bars_a = ax_bot.bar(x, alives, color=colours_alive, width=0.55)
    for bar, val in zip(bars_a, alives):
        ax_bot.text(bar.get_x() + bar.get_width() / 2,
                     val + 1, f"{val:.0f}%",
                     ha="center", va="bottom", fontsize=11,
                     fontweight="bold")
    ax_bot.axhline(80, color="black", ls=":", alpha=0.4)
    ax_bot.text(len(policy_order) - 0.6, 81, "UK calibration target (80%)",
                 fontsize=9, color="black", alpha=0.6)
    ax_bot.set_ylim(0, 105)
    ax_bot.set_ylabel("% population alive\nat terminal tick", fontsize=11)
    ax_bot.set_xticks(x)
    ax_bot.set_xticklabels([display_names[p] for p in policy_order],
                            fontsize=10)
    ax_bot.grid(alpha=0.3, axis="y")
    ax_bot.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(OUT / "elegant_demo.png", dpi=140)
    plt.close(fig)
    print(f"\nsaved {OUT / 'elegant_demo.png'}")


if __name__ == "__main__":
    main()
