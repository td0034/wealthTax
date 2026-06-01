"""
Survival curves per scenario and per policy.

Plots per-tick alive count (mean +/- ribbon) and cumulative starvation
counts. Distinguishes starvation deaths from natural age-out deaths
using the death_cause field added to Agent in the post-review sim revision.

Usage: python3 survival.py
"""
from __future__ import annotations

import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, make_initial_population, step
from scenarios import SCENARIOS
from policies import POLICIES

OUT = Path("out/figures/scenarios")
OUT.mkdir(parents=True, exist_ok=True)

SEEDS = 6
TICKS = 250


SCENARIO_SUBSET = [
    "current_world", "stevenson_world", "nordic", "socialist",
    "inheritance_break", "inheritance_break_ubi", "feudal", "maker_economy",
]

POLICY_SUBSET = [
    "uk_tory_2010_24", "uk_labour_2024", "zucman_2pct_hoard",
    "zucman_2pct_spend", "warren_2020", "piketty_book",
    "reform_uk_flavour",
]

COLOURS = {
    "current_world": "#3b82f6", "stevenson_world": "#ef4444",
    "nordic": "#0ea5e9",        "socialist": "#0f766e",
    "inheritance_break": "#9333ea", "inheritance_break_ubi": "#14b8a6",
    "feudal": "#7f1d1d",        "maker_economy": "#22c55e",
    "uk_tory_2010_24": "#1f2937", "uk_labour_2024": "#dc2626",
    "zucman_2pct_hoard": "#a855f7", "zucman_2pct_spend": "#2563eb",
    "warren_2020": "#f59e0b", "piketty_book": "#16a34a",
    "reform_uk_flavour": "#7f1d1d",
}


def _run(args):
    name, dials, seed = args
    d = replace(dials, seed=seed)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    alive_series = []
    starved_series = []
    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        alive_series.append(h["alive"])
        starved_series.append(h["starved_cum"])
    return name, seed, np.array(alive_series), np.array(starved_series)


def collect(named_dials: list[tuple[str, Dials]]) -> dict:
    args = [(name, d, s) for name, d in named_dials for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    by_name: dict[str, dict] = {}
    for name, _ in named_dials:
        alives = [a for nm, sd, a, _s in results if nm == name]
        starveds = [s for nm, sd, _a, s in results if nm == name]
        by_name[name] = {
            "alive_mean": np.mean(np.stack(alives), axis=0),
            "alive_lo":   np.percentile(np.stack(alives), 25, axis=0),
            "alive_hi":   np.percentile(np.stack(alives), 75, axis=0),
            "starved_mean": np.mean(np.stack(starveds), axis=0),
            "starved_lo":   np.percentile(np.stack(starveds), 25, axis=0),
            "starved_hi":   np.percentile(np.stack(starveds), 75, axis=0),
        }
    return by_name


def plot_pair(by_name: dict, names: list[str], title: str, fname: str,
              initial_pop: int) -> None:
    fig, (ax_alive, ax_starv) = plt.subplots(1, 2, figsize=(16, 5.5))
    ticks = np.arange(TICKS)
    for name in names:
        d = by_name[name]
        col = COLOURS.get(name, "#444")
        ax_alive.plot(ticks, d["alive_mean"], color=col, label=name, lw=1.6)
        ax_alive.fill_between(ticks, d["alive_lo"], d["alive_hi"],
                              color=col, alpha=0.15)
        ax_starv.plot(ticks, d["starved_mean"] / initial_pop * 100,
                      color=col, label=name, lw=1.6)
        ax_starv.fill_between(
            ticks, d["starved_lo"] / initial_pop * 100,
            d["starved_hi"] / initial_pop * 100, color=col, alpha=0.15)
    ax_alive.set_xlabel("tick (years)"); ax_alive.set_ylabel("alive (count)")
    ax_alive.set_title("Population alive over time")
    ax_alive.grid(alpha=0.25); ax_alive.legend(fontsize=8, loc="best", ncol=2)
    ax_starv.set_xlabel("tick (years)")
    ax_starv.set_ylabel("cumulative starved + debt-writeoff (% of initial)")
    ax_starv.set_title("Cumulative excess mortality over time")
    ax_starv.grid(alpha=0.25)
    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=120)
    plt.close(fig)
    print(f"saved {OUT / fname}")


def main():
    t0 = time.time()
    print("scenarios ...")
    s_by = collect([(n, SCENARIOS[n]) for n in SCENARIO_SUBSET])
    plot_pair(s_by, SCENARIO_SUBSET,
              "Survival curves: scenarios at N=100 (6 seeds)",
              "survival_scenarios.png", initial_pop=99)
    print("policies ...")
    p_by = collect([(n, POLICIES[n]) for n in POLICY_SUBSET])
    plot_pair(p_by, POLICY_SUBSET,
              "Survival curves: policies at N=100 (6 seeds)",
              "survival_policies.png", initial_pop=99)
    print(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
