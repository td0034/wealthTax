"""
Pareto tail figure: rank-wealth log-log plot per policy at N=10k, overlaid
with an approximate UK Sunday Times Rich List 2024 fit.

The UK overlay is a power-law fit to publicly known anchor points
(~165 sterling billionaires; top wealth roughly £37B). The fit is
W(rank) = 37 * rank^(-0.706) in £B. The fit is approximate and intended
for shape comparison, not magnitude calibration. The model produces ~16
billionaires per 10,000 agents under the Tory baseline, which is about
600x the per-capita rate of the UK; this magnitude gap is itself a finding
the figure makes visible.

Usage: python3 pareto.py
"""
from __future__ import annotations

import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import (Type, make_initial_population, step, WEALTH_UNIT_GBP)
from policies import POLICIES

OUT = Path("out/figures/scale_up")
OUT.mkdir(parents=True, exist_ok=True)

SCALE = 100      # 10,000 agents
TICKS = 180
SEEDS = 3

POLICY_SUBSET = [
    "uk_tory_2010_24",
    "zucman_2pct_spend",
    "zucman_progressive_2_4_8",
    "warren_2020",
    "piketty_book",
    "reform_uk_flavour",
]

POLICY_COLOURS = {
    "uk_tory_2010_24":            "#1f2937",
    "zucman_2pct_spend":          "#2563eb",
    "zucman_progressive_2_4_8":   "#0ea5e9",
    "warren_2020":                "#a855f7",
    "piketty_book":               "#16a34a",
    "reform_uk_flavour":          "#dc2626",
}


def _run_one(args):
    name, seed = args
    d = replace(POLICIES[name], population_scale=SCALE, seed=seed)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
    living = [a for a in agents if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    return name, seed, nws


def uk_richlist_curve(ranks: np.ndarray) -> np.ndarray:
    """Approximate UK Sunday Times Rich List 2024 power-law fit, in £."""
    return 37e9 * ranks ** (-0.706)


def main():
    args = [(n, s) for n in POLICY_SUBSET for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} N=10k runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run_one, args)
    print(f"  done in {time.time()-t0:.1f}s")

    top_n = 200
    by_policy: dict[str, np.ndarray] = {}
    for name in POLICY_SUBSET:
        tops = []
        for nm, sd, nws in results:
            if nm != name:
                continue
            sorted_w = np.sort(nws)[::-1] * WEALTH_UNIT_GBP
            if len(sorted_w) >= top_n:
                tops.append(sorted_w[:top_n])
            else:
                padded = np.zeros(top_n)
                padded[: len(sorted_w)] = sorted_w
                tops.append(padded)
        by_policy[name] = np.median(np.stack(tops), axis=0)

    fig, ax = plt.subplots(figsize=(11.5, 7.5))
    ranks = np.arange(1, top_n + 1)
    for name in POLICY_SUBSET:
        ax.plot(ranks, by_policy[name], color=POLICY_COLOURS[name],
                lw=1.8, label=name)

    uk_ranks = np.arange(1, 166)
    uk_wealth = uk_richlist_curve(uk_ranks)
    ax.plot(uk_ranks, uk_wealth, color="#000000", lw=2.2, ls="--",
            label="UK Rich List 2024 (approximate fit)", alpha=0.85)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Rank (1 = richest)")
    ax.set_ylabel(u"Wealth (£, log scale)")
    ax.set_title(f"Top-{top_n} wealth per policy, N={SCALE*100}, with UK Rich List overlay")

    for level, label in [(1e7, u"£10M"),
                         (1e8, u"£100M"),
                         (1e9, u"£1B")]:
        ax.axhline(level, color="grey", ls=":", lw=0.7, alpha=0.6)
        ax.text(top_n * 0.95, level * 1.10, label, fontsize=8,
                color="grey", ha="right", va="bottom")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8, loc="lower left", ncol=2)
    fig.tight_layout()
    out_path = OUT / "pareto_with_uk_overlay.png"
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"saved {out_path}")

    print("\nPareto slope estimates (log-log linear fit on top 50):")
    for name in POLICY_SUBSET:
        w = by_policy[name][:50]
        w = w[w > 0]
        if len(w) < 5:
            print(f"  {name:<28} (insufficient data)")
            continue
        log_r = np.log(np.arange(1, len(w) + 1))
        log_w = np.log(w)
        slope, _ = np.polyfit(log_r, log_w, 1)
        print(f"  {name:<28} slope = {slope:.3f}")
    print(f"  {'UK Rich List 2024 (fit)':<28} slope = -0.706")


if __name__ == "__main__":
    main()
