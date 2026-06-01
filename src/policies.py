"""
Real-world wealth-tax policies as Unequal Agents scenarios.

Wealth unit interpretation:
  1 model unit = £100,000.
  100 units = £10M  (Zucman lower bracket)
  500 units = £50M  (Warren lower bracket)
  1000 units = £100M
  10000 units = £1B

Each policy below couples a wealth-tax design with the rest of the
fiscal package a real government implementing that policy would run
(state employment, state purchasing of maker output, lender backstop,
UBI). The point is *what the policy does in equilibrium* not just the
tax mechanism in isolation.

Usage: python3 policies.py
"""
from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, Type, TYPE_COLOURS, make_initial_population, step
from scenarios import METRICS, plot_scenario, plot_wealth_share_by_type, summarise

OUT = Path("out/figures/policies")
OUT_DATA = Path("out/data")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Policy library
# ---------------------------------------------------------------------------
#
# Notes on construction. For each non-status-quo policy, we couple the
# advertised wealth tax with what that political project actually proposes
# *to do with the revenue*. Zucman (2024 G20) is explicitly a minimum
# floor for global tax cooperation; the revenue side is unspecified in his
# proposal so we model two flavours: revenue-hoarding (no state spending,
# minimum case) and recirculated (state spending matched to revenue).

POLICIES: dict[str, Dials] = {
    # Last 14 years of UK fiscal policy: no wealth tax, IHT 40% above £325k
    # (≈3.25 units), minimal state spending in the productive sector.
    "uk_tory_2010_24": Dials(
        flat_tax_rate=0.0,
        tax_progressivity=0.0,
        wealth_tax_tiers=(),
        inheritance_tax_rate=0.4,
        inheritance_cap=float("inf"),
        ubi=0.0,
        state_employs_fraction=0.0,
        state_buys_maker_output=0.0,
    ),

    # Labour 2024–25 actual policy: no wealth tax, slightly higher CGT and
    # closing IHT carve-outs, mild state-employment uptick (NHS hiring etc).
    "uk_labour_2024": Dials(
        flat_tax_rate=0.002,
        tax_progressivity=0.005,
        wealth_tax_threshold=80,
        inheritance_tax_rate=0.5,
        inheritance_cap=float("inf"),
        ubi=0.0,
        state_employs_fraction=0.1,
        state_employs_wage=0.8,
        state_buys_maker_output=2.0,
    ),

    # Zucman flat 2% on wealth above £10M, with revenue *not* recirculated.
    # Minimum case — what the headline policy alone does.
    "zucman_2pct_hoard": Dials(
        wealth_tax_tiers=((100, 0.02),),
        inheritance_tax_rate=0.4,
    ),

    # Zucman flat 2%, revenue recirculated through state employment & UBI.
    "zucman_2pct_spend": Dials(
        wealth_tax_tiers=((100, 0.02),),
        inheritance_tax_rate=0.4,
        ubi=0.4,
        state_employs_fraction=0.3,
        state_employs_wage=0.8,
        state_buys_maker_output=5.0,
    ),

    # User's example: 2% above £10M, 4% above £100M, 8% above £1B,
    # stacked-marginal form.
    "zucman_progressive_2_4_8": Dials(
        wealth_tax_tiers=((100, 0.02), (1000, 0.02), (10000, 0.04)),
        inheritance_tax_rate=0.4,
        ubi=0.4,
        state_employs_fraction=0.3,
        state_employs_wage=0.8,
        state_buys_maker_output=5.0,
    ),

    # Elizabeth Warren 2020: 2% > $50M (≈500), 6% > $1B (≈10000).
    "warren_2020": Dials(
        wealth_tax_tiers=((500, 0.02), (10000, 0.04)),
        inheritance_tax_rate=0.4,
        ubi=0.3,
        state_employs_fraction=0.3,
        state_buys_maker_output=4.0,
    ),

    # Bernie Sanders 2020: 1% > $32M ramping to 8% > $10B. Approximated as
    # 1% > 320, +2% > 3200, +5% > 32000  (top marginal ≈ 8%).
    "sanders_2020": Dials(
        wealth_tax_tiers=((320, 0.01), (3200, 0.02), (32000, 0.05)),
        inheritance_tax_rate=0.5,
        ubi=0.4,
        state_employs_fraction=0.4,
        state_buys_maker_output=6.0,
    ),

    # Piketty (Capital, 2014): 0.1% > €1M, 1% > €5M, 2% > €100M.
    "piketty_book": Dials(
        wealth_tax_tiers=((10, 0.001), (50, 0.009), (1000, 0.01)),
        inheritance_tax_rate=0.6,
        ubi=0.3,
        state_employs_fraction=0.3,
        state_buys_maker_output=4.0,
    ),

    # Norway (actual): ~1% on net wealth above ~£130k.
    "norway_actual": Dials(
        wealth_tax_tiers=((1.3, 0.01),),
        inheritance_tax_rate=0.0,           # Norway abolished IHT in 2014
        ubi=0.0,
        state_employs_fraction=0.4,         # high public-sector employment
        state_buys_maker_output=4.0,
        state_recap_lenders=200.0,
    ),

    # Spain solidarity tax: 0.2–3.5% above €700k, with extra above €3M.
    "spain_solidarity": Dials(
        wealth_tax_tiers=((7, 0.002), (30, 0.005), (100, 0.01), (1000, 0.015)),
        inheritance_tax_rate=0.3,
        ubi=0.2,
        state_employs_fraction=0.2,
        state_buys_maker_output=3.0,
    ),

    # Reform-flavour: cut taxes, cut state spending (a real political prospectus).
    "reform_uk_flavour": Dials(
        flat_tax_rate=0.0,
        tax_progressivity=0.0,
        wealth_tax_tiers=(),
        inheritance_tax_rate=0.2,
        ubi=0.0,
        state_employs_fraction=0.0,
        state_buys_maker_output=0.0,
        rent_share_of_wage=0.4,             # less regulation, higher extraction
    ),
}


# ---------------------------------------------------------------------------
# Run helpers — including a policy-switch run
# ---------------------------------------------------------------------------

def run(d: Dials, ticks: int = 250) -> list[dict]:
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    history = []
    accum = {}
    for t in range(ticks):
        history.append(step(agents, d, rng, t, accum))
    return history


def run_switch(d_initial: Dials, d_post: Dials, switch_tick: int,
               ticks: int, seed: int) -> list[dict]:
    """Run with d_initial until switch_tick, then continue with d_post."""
    rng = np.random.default_rng(seed)
    agents = make_initial_population(rng, d_initial)
    history = []
    accum = {}
    for t in range(ticks):
        d = d_post if t >= switch_tick else d_initial
        history.append(step(agents, d, rng, t, accum))
    return history


def run_multi(d: Dials, ticks: int = 250, seeds: int = 6) -> list[list[dict]]:
    runs = []
    for s in range(seeds):
        runs.append(run(replace(d, seed=s), ticks=ticks))
    return runs


def run_switch_multi(d_initial: Dials, d_post: Dials, switch_tick: int,
                     ticks: int = 250, seeds: int = 6) -> list[list[dict]]:
    runs = []
    for s in range(seeds):
        runs.append(run_switch(replace(d_initial, seed=s),
                               replace(d_post, seed=s),
                               switch_tick, ticks, s))
    return runs


# ---------------------------------------------------------------------------
# Effective-tax-rate curves (for explainer plots)
# ---------------------------------------------------------------------------

def effective_rate(wealth: float, d: Dials) -> float:
    if wealth <= 0:
        return 0.0
    tax = d.flat_tax_rate * wealth
    if wealth > d.wealth_tax_threshold:
        tax += d.tax_progressivity * (wealth - d.wealth_tax_threshold)
    for thresh, rate in d.wealth_tax_tiers:
        if wealth > thresh:
            tax += rate * (wealth - thresh)
    return tax / wealth


def plot_effective_rate_curves() -> None:
    wealths = np.logspace(0, 5, 200)              # 1 unit to 100k units
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, d in POLICIES.items():
        if not d.wealth_tax_tiers and d.flat_tax_rate == 0 and d.tax_progressivity == 0:
            continue
        rates = [effective_rate(w, d) for w in wealths]
        ax.plot(wealths, rates, label=name, lw=1.6)
    ax.set_xscale("log")
    ax.set_xlabel("Wealth (model units, log scale)  [10 = £1M, 1000 = £100M, 10000 = £1B]")
    ax.set_ylabel("Effective annual tax rate")
    ax.set_title("Effective wealth-tax curves by policy")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    ax.axvline(100, color="grey", linestyle=":", alpha=0.4)
    ax.axvline(1000, color="grey", linestyle=":", alpha=0.4)
    ax.axvline(10000, color="grey", linestyle=":", alpha=0.4)
    ax.text(100, ax.get_ylim()[1] * 0.95, "£10M", rotation=90, fontsize=8, color="grey")
    ax.text(1000, ax.get_ylim()[1] * 0.95, "£100M", rotation=90, fontsize=8, color="grey")
    ax.text(10000, ax.get_ylim()[1] * 0.95, "£1B", rotation=90, fontsize=8, color="grey")
    fig.tight_layout()
    fig.savefig(OUT / "effective_rate_curves.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Aggregation utility (shared with scenarios.py form)
# ---------------------------------------------------------------------------

def aggregate(runs: list[list[dict]], key: str):
    arr = np.array([[h[key] for h in r] for r in runs])
    return arr.mean(0), np.percentile(arr, 25, 0), np.percentile(arr, 75, 0), arr.std(0)


def policy_compare_plot(all_results: dict[str, list[list[dict]]],
                        title: str, fname: str) -> None:
    keys = ["gini", "alive", "metabolic_rate", "autocatalytic_closure",
            "top10_share", "state_wealth"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    axes = axes.flatten()
    for ax, key in zip(axes, keys):
        for name, runs in all_results.items():
            mean, _, _, _ = aggregate(runs, key)
            ax.plot(mean, label=name, lw=1.3)
        ax.set_title(key); ax.grid(alpha=0.2)
    axes[0].legend(fontsize=7, loc="best", ncol=2)
    fig.suptitle(title, fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Top-1 wealth trajectory plot
# ---------------------------------------------------------------------------

def plot_top1_share(all_results: dict[str, list[list[dict]]]) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    for name, runs in all_results.items():
        mean, _, _, _ = aggregate(runs, "top1_share")
        ax.plot(mean, label=name, lw=1.4)
    ax.set_title("Top-1% wealth share over time")
    ax.set_xlabel("tick (years)"); ax.set_ylabel("share")
    ax.set_ylim(0, 1); ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="best", ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "top1_share.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(ticks: int = 250, seeds: int = 6) -> None:
    # Redirect scenarios.plot_scenario per-policy outputs to the policy folder.
    import scenarios as _scen
    _scen.OUT = OUT

    plot_effective_rate_curves()

    # Steady-state policy comparison.
    all_results: dict[str, list[list[dict]]] = {}
    summary: dict[str, dict] = {}
    for name, d in POLICIES.items():
        print(f"running policy: {name}")
        runs = run_multi(d, ticks=ticks, seeds=seeds)
        all_results[name] = runs
        plot_scenario(name, runs)
        plot_wealth_share_by_type(name, runs)
        summary[name] = summarise(name, runs)
        summary[name]["dials"] = asdict(d)
    policy_compare_plot(all_results, "Policy comparison — full equilibrium",
                        "policies_compare.png")
    plot_top1_share(all_results)

    # Policy-switch runs: start as UK Tory baseline, switch at tick 100 to
    # each of the alternatives. Shows transition dynamics.
    initial = POLICIES["uk_tory_2010_24"]
    switch_results: dict[str, list[list[dict]]] = {
        "baseline (no switch)": run_multi(initial, ticks=ticks, seeds=seeds)
    }
    for name in ["uk_labour_2024", "zucman_2pct_spend",
                 "zucman_progressive_2_4_8", "warren_2020", "sanders_2020"]:
        print(f"switch run: tory -> {name}")
        switch_results[name] = run_switch_multi(
            initial, POLICIES[name], switch_tick=100,
            ticks=ticks, seeds=seeds)
    policy_compare_plot(switch_results,
                        "Policy switch at year 100 (start: UK Tory baseline)",
                        "policy_switch.png")

    with open(OUT_DATA / "policies_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print()
    print(f"{'policy':<28} {'gini':>5} {'alive':>5} {'meta':>5} "
          f"{'closure':>8} {'top10':>6} {'state_w':>8}")
    for name, s in summary.items():
        print(f"{name:<28} "
              f"{s['final_gini_mean']:5.2f} "
              f"{s['final_alive_mean']:5.1f} "
              f"{s['mean_metabolic_rate']:5.1f} "
              f"{s['final_autocatalytic_closure']:8.3f} "
              f"{s['final_top10_share']:6.2f} "
              f"{s['final_state_wealth']:8.1f}")


if __name__ == "__main__":
    main()
