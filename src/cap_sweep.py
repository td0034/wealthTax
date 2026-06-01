"""
Sweep the inheritance cap value at the joint-calibrated baseline.

Cap values in model units (1 unit = £100,000):
    10     £1M
    50     £5M       <- joint-cal best fit
    100    £10M
    500    £50M
    1000   £100M
    5000   £500M
    10000  £1B
    50000  £5B
    inf    no cap

For each cap value we measure: alive rate, billionaire count,
centi-millionaire and deci-millionaire counts, top-1 share, top-10
share, max wealth, and the Pareto slope of the top 50.

Compares the cap as a sole intervention (no wealth tax) and combined
with Zucman 2% above £10M.

Usage: python3 cap_sweep.py
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

SCALE = 100
TICKS = 180
SEEDS = 4

CAPS = [10, 50, 100, 500, 1000, 5000, 10000, 50000, float("inf")]
ARMS = [("cap_only", ()), ("cap_plus_zucman", ((100.0, 0.02),))]

BASE = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    inheritance_tax_rate=0.0,
)


def _run(args):
    arm, tiers, cap, seed = args
    d = Dials(seed=seed, population_scale=SCALE,
              wealth_tax_tiers=tiers, inheritance_cap=float(cap),
              **BASE)
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
    top50 = sorted_gbp[:min(50, len(sorted_gbp))]
    valid = top50 > 0
    if valid.sum() >= 5:
        slope, _ = np.polyfit(
            np.log(np.arange(1, valid.sum() + 1)),
            np.log(top50[valid]), 1)
    else:
        slope = 0.0
    return arm, cap, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centi_millionaires": int((gbp >= 1e8).sum()),
        "deci_millionaires": int((gbp >= 1e7).sum()),
        "max_wealth_gbp": float(sorted_gbp[0]),
        "top1_share": float(sorted_gbp[:max(1, len(gbp) // 100)].sum()
                            / max(gbp.sum(), 1e-9)),
        "top10_share": float(sorted_gbp[:max(1, len(gbp) // 10)].sum()
                             / max(gbp.sum(), 1e-9)),
        "pareto_slope": float(slope),
    }


def main():
    args = [(arm, tiers, cap, s)
            for arm, tiers in ARMS
            for cap in CAPS
            for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    t0 = time.time()
    print(f"running {len(args)} runs ({len(CAPS)} caps x {len(ARMS)} arms x {SEEDS} seeds) ...")
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_cell: dict[tuple, list[dict]] = {}
    for arm, cap, seed, m in results:
        by_cell.setdefault((arm, cap), []).append(m)

    summary: dict[str, list] = {arm: [] for arm, _ in ARMS}
    print()
    print(f"{'arm':<18} {'cap':>10} {'alive %':>8} {'>=£1B':>7} "
          f"{'>=£100M':>9} {'>=£10M':>8} {'top1':>6} {'top10':>6} "
          f"{'slope':>7}")
    for arm, _ in ARMS:
        for cap in CAPS:
            runs = by_cell[(arm, cap)]
            med = {k: float(np.median([r[k] for r in runs]))
                   for k in runs[0]}
            cap_disp = "inf" if cap == float("inf") else f"{cap:.0f}"
            cap_label_gbp = "no cap" if cap == float("inf") else f"£{cap * 0.1:.0f}M"
            summary[arm].append({"cap": cap_disp, "cap_gbp": cap_label_gbp, **med})
            print(f"{arm:<18} {cap_label_gbp:>10} {med['alive_rate']*100:>7.0f}% "
                  f"{med['billionaires']:>7.0f} {med['centi_millionaires']:>9.0f} "
                  f"{med['deci_millionaires']:>8.0f} {med['top1_share']:>6.3f} "
                  f"{med['top10_share']:>6.3f} {med['pareto_slope']:>7.3f}")

    with open(OUT_DATA / "cap_sweep_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # ===================================================================
    # The trade-off chart
    # ===================================================================
    cap_gbp = [10**4 * 100_000 if c == float("inf") else c * 100_000
               for c in CAPS]
    cap_labels = ["£1M", "£5M", "£10M", "£50M", "£100M", "£500M",
                  "£1B", "£5B", "no cap"]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    metrics_to_plot = [
        ("billionaires", "billionaire count (out of 10,000)",
         "log",         "#dc2626"),
        ("top1_share",   "top-1% wealth share",
         "linear",      "#7c3aed"),
        ("alive_rate",   "% population alive at terminal tick",
         "linear",      "#16a34a"),
        ("max_wealth_gbp","max wealth (£B)",
         "log",         "#0ea5e9"),
    ]
    for ax, (key, ylabel, yscale, _) in zip(axes.flatten(), metrics_to_plot):
        for arm, _t in ARMS:
            ys = [s[key] for s in summary[arm]]
            if key == "max_wealth_gbp":
                ys = [y / 1e9 for y in ys]
            if key == "alive_rate":
                ys = [y * 100 for y in ys]
            label = "cap only" if arm == "cap_only" else "cap + Zucman 2%"
            ls = "-" if arm == "cap_only" else "--"
            ax.plot(range(len(CAPS)), ys, marker="o", lw=2.2, ls=ls,
                    label=label, markersize=7)
        ax.set_xticks(range(len(CAPS)))
        ax.set_xticklabels(cap_labels, rotation=30, ha="right", fontsize=9)
        ax.set_xlabel("inheritance cap")
        ax.set_ylabel(ylabel)
        if yscale == "log":
            ax.set_yscale("symlog", linthresh=1)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=10, loc="best")
    axes[0, 0].axhline(1, color="grey", ls=":", alpha=0.5)
    axes[0, 0].text(len(CAPS) - 0.5, 1.2, "one billionaire",
                    fontsize=8, color="grey", ha="right")
    fig.suptitle("Inheritance cap sweep at joint-calibrated UK baseline\n"
                 "($r = 0.08$, rent $= 0.20$, subsistence $= 0.30$; "
                 "$N = 10{,}000$, 4 seeds)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "cap_sweep.png", dpi=140)
    plt.close(fig)
    print(f"\nsaved {OUT / 'cap_sweep.png'}")


if __name__ == "__main__":
    main()
