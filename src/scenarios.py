"""
Scenario harness for Unequal Agents v1.

Runs each scenario with multiple seeds, aggregates, plots ribbon charts,
and writes a summary JSON.

Usage: python3 scenarios.py
"""
from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, Type, TYPE_COLOURS, run_multi, aggregate


OUT = Path("out/figures/scenarios")
OUT_DATA = Path("out/data")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIOS: dict[str, Dials] = {
    "current_world": Dials(),
    "stevenson_world": Dials(
        rent_share_of_wage=0.55,
        capital_return=0.05,
        interest_rate=0.09,
        employer_markup=0.55,
    ),
    "maker_economy": Dials(
        maker_multiplier=2.2,
        rent_share_of_wage=0.15,
        capital_return=0.01,
        employer_markup=0.2,
    ),
    "tax_and_spend": Dials(
        flat_tax_rate=0.01,
        tax_progressivity=0.03,
        wealth_tax_threshold=80,
        ubi=0.5,
        state_employs_fraction=0.5,
        state_employs_wage=0.8,
        state_buys_maker_output=8.0,
        state_recap_lenders=200.0,
    ),
    "nordic": Dials(
        flat_tax_rate=0.005,
        tax_progressivity=0.04,
        wealth_tax_threshold=60,
        ubi=0.6,
        state_employs_fraction=0.6,
        state_employs_wage=0.9,
        state_buys_maker_output=10.0,
        state_recap_lenders=250.0,
        rent_share_of_wage=0.25,
        inheritance_tax_rate=0.4,
        inheritance_cap=500.0,
    ),
    "inheritance_break": Dials(
        inheritance_tax_rate=1.0,    # 100% — state takes everything at death
        inheritance_cap=0.0,
    ),
    "memory_equalised": Dials(
        memory_bandwidth_base=1.0,                # everyone gets full transmission
        memory_bandwidth_wealth_scale=0.0,        # wealth no longer buys bandwidth
    ),
    "memory_starved": Dials(
        memory_bandwidth_base=0.2,                # only 1 dim baseline
        memory_bandwidth_wealth_scale=1.0,        # wealth strongly buys bandwidth
    ),
    "inheritance_break_ubi": Dials(
        inheritance_tax_rate=1.0,
        inheritance_cap=0.0,
        ubi=1.0,                                  # safety net for the new generation
        flat_tax_rate=0.005,
        tax_progressivity=0.02,
        state_employs_fraction=0.4,
        state_employs_wage=0.8,
    ),
    "feudal": Dials(
        rent_share_of_wage=0.6,
        capital_return=0.06,
        employer_markup=0.5,
        inheritance_cap=float("inf"),
        inheritance_tax_rate=0.0,
        memory_bandwidth_base=0.2,                 # only the wealthy preserve knowledge
        memory_bandwidth_wealth_scale=1.0,
    ),
    "creditless": Dials(
        interest_rate=0.0,
        debt_ceiling=0.1,                          # almost no borrowing tolerated
    ),
    "pure_speculation": Dials(
        maker_multiplier=1.1,                      # production barely catalytic
        spec_drift=0.04,
        spec_vol=0.20,
        capital_return=0.05,
    ),
    "socialist": Dials(
        flat_tax_rate=0.015,
        tax_progressivity=0.06,
        wealth_tax_threshold=40,
        ubi=0.8,
        state_employs_fraction=0.9,                # state hires almost all unemployed
        state_employs_wage=1.0,
        state_buys_maker_output=15.0,
        state_recap_lenders=400.0,
        rent_share_of_wage=0.10,
        inheritance_tax_rate=0.8,
        inheritance_cap=200.0,
    ),
}


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

METRICS = [
    ("gini", "Gini (net worth)"),
    ("alive", "Population alive"),
    ("metabolic_rate", "Metabolic rate / tick"),
    ("autocatalytic_closure", "Autocatalytic closure"),
    ("cultural_breadth", "Cultural breadth (skills > 0)"),
    ("top10_share", "Top 10% wealth share"),
    ("knowledge_lost_cum", "Knowledge lost (cumulative)"),
    ("state_wealth", "State wealth"),
]


def plot_scenario(name: str, runs: list[list[dict]]) -> None:
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    axes = axes.flatten()
    for ax, (key, label) in zip(axes, METRICS):
        mean, p25, p75, _ = aggregate(runs, key)
        ticks = np.arange(len(mean))
        ax.fill_between(ticks, p25, p75, alpha=0.25)
        ax.plot(ticks, mean, lw=1.5)
        ax.set_title(label)
        ax.set_xlabel("tick")
        ax.grid(alpha=0.2)
    fig.suptitle(name, fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=110)
    plt.close(fig)


def plot_compare(all_results: dict[str, list[list[dict]]]) -> None:
    keys = ["gini", "alive", "metabolic_rate", "autocatalytic_closure",
            "cultural_breadth", "top10_share"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    axes = axes.flatten()
    for ax, key in zip(axes, keys):
        for name, runs in all_results.items():
            mean, _, _, _ = aggregate(runs, key)
            ax.plot(mean, label=name, lw=1.4)
        ax.set_title(key)
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8, loc="best")
    fig.suptitle("Scenario comparison (mean across seeds)", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "compare.png", dpi=110)
    plt.close(fig)


def plot_wealth_share_by_type(name: str, runs: list[list[dict]]) -> None:
    """Stacked area of mean wealth share by type over time."""
    type_names = [t.name for t in Type]
    arrs = {tn: np.array([[h["wealth_by_type"][tn] for h in r] for r in runs])
            for tn in type_names}
    mean_by_type = {tn: arrs[tn].mean(0) for tn in type_names}
    total = np.sum([mean_by_type[tn] for tn in type_names], axis=0)
    total = np.where(total <= 0, 1.0, total)
    shares = {tn: np.clip(mean_by_type[tn] / total, 0, None) for tn in type_names}
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.stackplot(
        np.arange(len(total)),
        [shares[tn] for tn in type_names],
        labels=type_names,
        colors=[TYPE_COLOURS[Type[tn]] for tn in type_names],
        alpha=0.9,
    )
    ax.set_ylim(0, 1)
    ax.set_title(f"{name}: wealth share by type")
    ax.legend(loc="upper left", fontsize=8, ncol=4)
    fig.tight_layout()
    fig.savefig(OUT / f"{name}_shares.png", dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def summarise(name: str, runs: list[list[dict]]) -> dict:
    last = [r[-1] for r in runs]
    def m(k): return float(np.mean([x[k] for x in last]))
    def s(k): return float(np.std([x[k] for x in last]))
    return {
        "final_gini_mean": m("gini"),
        "final_gini_std": s("gini"),
        "final_alive_mean": m("alive"),
        "final_alive_std": s("alive"),
        "mean_metabolic_rate": float(np.mean([h["metabolic_rate"]
                                              for r in runs for h in r])),
        "final_autocatalytic_closure": m("autocatalytic_closure"),
        "final_top10_share": m("top10_share"),
        "final_cultural_breadth": m("cultural_breadth"),
        "knowledge_lost_cum_mean": m("knowledge_lost_cum"),
        "final_state_wealth": m("state_wealth"),
        "starved_cum_mean": m("starved_cum"),
        "births_cum_mean": m("births_cum"),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(ticks: int = 250, seeds: int = 8) -> None:
    all_results: dict[str, list[list[dict]]] = {}
    summary: dict[str, dict] = {}
    for name, d in SCENARIOS.items():
        print(f"running {name} ...")
        runs = run_multi(d, ticks=ticks, seeds=seeds)
        all_results[name] = runs
        plot_scenario(name, runs)
        plot_wealth_share_by_type(name, runs)
        summary[name] = summarise(name, runs)
        summary[name]["dials"] = asdict(d)
    plot_compare(all_results)
    with open(OUT_DATA / "scenarios_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    # Brief stdout table
    print()
    print(f"{'scenario':<22} {'gini':>6} {'alive':>6} {'meta':>6} "
          f"{'closure':>8} {'top10':>6} {'breadth':>8}")
    for name, s in summary.items():
        print(f"{name:<22} "
              f"{s['final_gini_mean']:6.2f} "
              f"{s['final_alive_mean']:6.1f} "
              f"{s['mean_metabolic_rate']:6.1f} "
              f"{s['final_autocatalytic_closure']:8.3f} "
              f"{s['final_top10_share']:6.2f} "
              f"{s['final_cultural_breadth']:8.2f}")


if __name__ == "__main__":
    main()
