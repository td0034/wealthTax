"""
Scale-up experiments at N=10,000.

Goal: test whether the headline findings from the N=100 sweep survive at
realistic population size, with particular focus on the *fat tail* —
billionaires are an exponential phenomenon and N=100 has no room for
the tail to express itself.

Three experiments:
(1) Policy comparison — a focused subset of policies at N=10k.
(2) Wealth-tax sweep — (threshold × rate) at N=10k.
(3) Wealth distribution at the top — the actual £-distribution of the
    richest agents under each policy, plotted on log axes.

Usage: python3 scale_up.py
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import (Dials, Type, make_initial_population, step,
                 WEALTH_UNIT_GBP)
from policies import POLICIES, aggregate

OUT = Path("out/figures/scale_up")
OUT_DATA = Path("out/data")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)


SCALE = 100             # 100 = 10,000 agents
TICKS = 180
SEEDS = 10            # J-3: bumped from 3 for IQR bands on equivalence claims


# Subset that exercises the key findings from N=100.
POLICY_SUBSET = [
    "uk_tory_2010_24",
    "uk_labour_2024",
    "zucman_2pct_hoard",
    "zucman_2pct_spend",
    "zucman_progressive_2_4_8",
    "warren_2020",
    "piketty_book",
    "reform_uk_flavour",
]


# ---------------------------------------------------------------------------
# Runner that also returns final agent wealth distribution
# ---------------------------------------------------------------------------

def run_returning_wealth(d: Dials, ticks: int) -> tuple[list[dict], np.ndarray, dict]:
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    history = []
    accum = {}
    for t in range(ticks):
        history.append(step(agents, d, rng, t, accum))
    living = [a for a in agents if a.alive]
    nws = np.array([a.net_worth for a in living])
    # Wealth by type for context.
    by_type = {t.name: float(sum(a.net_worth for a in living if a.type == t))
               for t in Type}
    return history, nws, by_type


def _one_policy_seed(args):
    policy_name, seed = args
    d = replace(POLICIES[policy_name], population_scale=SCALE, seed=seed)
    h, nws, _ = run_returning_wealth(d, TICKS)
    return policy_name, seed, h, nws


def run_policy_suite():
    args = [(name, s) for name in POLICY_SUBSET for s in range(SEEDS)]
    t0 = time.time()
    # Reasonably-sized worker pool, but cap to avoid memory pressure.
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} N=10k policy runs across {n_proc} procs ...")
    with Pool(n_proc) as p:
        results = p.map(_one_policy_seed, args)
    print(f"  done in {time.time()-t0:.1f}s")

    by_policy: dict[str, dict] = {}
    for name, seed, h, nws in results:
        by_policy.setdefault(name, {"runs": [], "final_wealth": []})
        by_policy[name]["runs"].append(h)
        by_policy[name]["final_wealth"].append(nws)
    return by_policy


# ---------------------------------------------------------------------------
# Wealth tax sweep at N=10k
# ---------------------------------------------------------------------------

SPENDING_BASE_SCALED = Dials(
    inheritance_tax_rate=0.4,
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)


def _one_sweep_run(args):
    thresh, rate, seed, ticks = args
    d = replace(SPENDING_BASE_SCALED,
                population_scale=SCALE,
                wealth_tax_tiers=((float(thresh), float(rate)),),
                seed=seed)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(ticks):
        step(agents, d, rng, t, accum)
    # State excluded from percentile metrics (CC-1).
    living = [a for a in agents if a.alive and a.type != Type.STATE]
    nws = np.array([a.net_worth for a in living]) if living else np.array([0.0])
    # Mortality-corrected denominator (E-3): living + peak wealth of agents
    # who died in last 30 ticks.
    recent_deaths = accum.get("recent_deaths", [])
    extras = [pw for (td, tn, pw, _c) in recent_deaths
              if ticks - td <= 30 and tn != "STATE"]
    nws_corr = (np.concatenate([nws, np.array(extras, dtype=float)])
                if extras else nws)
    final_metrics = {
        "gini": _gini(nws),
        "gini_corrected": _gini(nws_corr),
        "alive": len(living),
        "top1_share": _top_k_share(nws, max(1, int(0.01 * len(nws)))),
        "top10_share": _top_k_share(nws, max(1, int(0.10 * len(nws)))),
        "top1_share_corrected": _top_k_share(
            nws_corr, max(1, int(0.01 * len(nws_corr)))),
        "top10_share_corrected": _top_k_share(
            nws_corr, max(1, int(0.10 * len(nws_corr)))),
        "max_wealth_units": float(nws.max()) if len(nws) else 0.0,
        "max_wealth_gbp": float(nws.max()) * WEALTH_UNIT_GBP if len(nws) else 0.0,
        "state_wealth": float(next((a.wealth for a in agents
                                    if a.type == Type.STATE and a.alive), 0.0)),
    }
    return final_metrics


def _gini(values: np.ndarray) -> float:
    v = np.clip(values, 0.0, None)
    if v.sum() == 0:
        return 0.0
    v = np.sort(v)
    n = len(v); cum = np.cumsum(v)
    return float((n + 1 - 2 * cum.sum() / cum[-1]) / n)


def _top_k_share(values: np.ndarray, k: int) -> float:
    pos = np.sort(np.clip(values, 0.0, None))[::-1]
    total = pos.sum()
    if total == 0 or k <= 0:
        return 0.0
    return float(pos[:k].sum() / total)


def run_tax_sweep():
    thresholds = np.array([10, 30, 100, 300, 1000, 3000, 10000], dtype=float)
    rates = np.linspace(0.0, 0.08, 7)
    sweep_seeds = 2
    ticks = 150
    args = [(t, r, s, ticks)
            for t in thresholds for r in rates for s in range(sweep_seeds)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"sweep: {len(args)} N=10k runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_one_sweep_run, args)
    print(f"  done in {time.time()-t0:.1f}s")
    keys = ["gini", "gini_corrected", "alive",
            "top1_share", "top10_share",
            "top1_share_corrected", "top10_share_corrected",
            "max_wealth_units", "max_wealth_gbp", "state_wealth"]
    grids = {k: np.zeros((len(thresholds), len(rates), sweep_seeds)) for k in keys}
    i = 0
    for ti in range(len(thresholds)):
        for ri in range(len(rates)):
            for s in range(sweep_seeds):
                for k in keys:
                    grids[k][ti, ri, s] = results[i][k]
                i += 1
    return {"thresholds": thresholds, "rates": rates, "grids": grids}


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_policy_compare(by_policy):
    keys = ["gini", "alive", "metabolic_rate", "autocatalytic_closure",
            "top10_share", "top1_share"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    axes = axes.flatten()
    for ax, key in zip(axes, keys):
        for name in POLICY_SUBSET:
            mean, _, _, _ = aggregate(by_policy[name]["runs"], key)
            ax.plot(mean, label=name, lw=1.3)
        ax.set_title(key); ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8, loc="best", ncol=2)
    fig.suptitle(f"Policy comparison at N={SCALE*100}", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "policy_compare_n10k.png", dpi=110)
    plt.close(fig)


def plot_top_wealth_distribution(by_policy):
    """For each policy, plot the top-200 agents' wealth on log axes."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for name in POLICY_SUBSET:
        # Concatenate top-200 from each seed.
        tops = []
        for nws in by_policy[name]["final_wealth"]:
            sorted_w = np.sort(nws)[::-1][:200]
            tops.append(sorted_w)
        mean_top = np.mean(np.stack(tops, axis=0), axis=0)
        gbp = mean_top * WEALTH_UNIT_GBP
        ax.plot(np.arange(1, len(gbp) + 1), gbp, label=name, lw=1.4)
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("Rank (1 = richest)")
    ax.set_ylabel("Wealth (£, log)")
    ax.set_title(f"Wealth of top 200 agents by policy (mean across seeds, N={SCALE*100})")
    ax.axhline(10_000_000, color="grey", ls=":", alpha=0.5)
    ax.axhline(100_000_000, color="grey", ls=":", alpha=0.5)
    ax.axhline(1_000_000_000, color="grey", ls=":", alpha=0.5)
    ax.text(180, 1.1e7, "£10M", fontsize=8, color="grey")
    ax.text(180, 1.1e8, "£100M", fontsize=8, color="grey")
    ax.text(180, 1.1e9, "£1B", fontsize=8, color="grey")
    ax.legend(fontsize=8, loc="lower left", ncol=2)
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "top_wealth_distribution_n10k.png", dpi=120)
    plt.close(fig)


def plot_billionaire_count(by_policy):
    """Bar chart: mean count of agents above £1B by policy."""
    names = POLICY_SUBSET
    counts_mean, counts_std = [], []
    counts_above_10m, counts_above_100m = [], []
    for name in names:
        cs_b = []
        cs_100m = []
        cs_10m = []
        for nws in by_policy[name]["final_wealth"]:
            gbp = nws * WEALTH_UNIT_GBP
            cs_b.append(int((gbp >= 1_000_000_000).sum()))
            cs_100m.append(int((gbp >= 100_000_000).sum()))
            cs_10m.append(int((gbp >= 10_000_000).sum()))
        counts_mean.append(float(np.mean(cs_b)))
        counts_std.append(float(np.std(cs_b)))
        counts_above_100m.append(float(np.mean(cs_100m)))
        counts_above_10m.append(float(np.mean(cs_10m)))

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(names))
    w = 0.27
    ax.bar(x - w, counts_above_10m, w, label="≥ £10M")
    ax.bar(x, counts_above_100m, w, label="≥ £100M")
    ax.bar(x + w, counts_mean, w, label="≥ £1B (billionaires)")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Agent count")
    ax.set_yscale("log")
    ax.set_title(f"Count of agents above wealth thresholds (N={SCALE*100}, mean across seeds)")
    ax.legend(); ax.grid(alpha=0.25, axis="y", which="both")
    fig.tight_layout()
    fig.savefig(OUT / "billionaire_count_n10k.png", dpi=120)
    plt.close(fig)

    return {name: {"≥£10M": cm10, "≥£100M": cm100, "≥£1B": cmb}
            for name, cm10, cm100, cmb in zip(names, counts_above_10m,
                                              counts_above_100m, counts_mean)}


def plot_tax_sweep(sweep):
    metrics = ["gini", "alive", "top10_share", "top1_share",
               "max_wealth_gbp", "state_wealth"]
    thresholds = sweep["thresholds"]; rates = sweep["rates"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    axes = axes.flatten()
    for ax, m in zip(axes, metrics):
        grid = sweep["grids"][m].mean(axis=2)
        im = ax.imshow(grid.T, origin="lower", aspect="auto",
                       extent=(0, len(thresholds) - 1, rates.min(), rates.max()),
                       cmap="viridis")
        ax.set_xticks(range(len(thresholds)))
        ax.set_xticklabels([f"{int(t)}" for t in thresholds], rotation=45, fontsize=8)
        ax.set_xlabel("threshold (model units; 100 = £10M)")
        ax.set_ylabel("annual rate")
        ax.set_title(m)
        plt.colorbar(im, ax=ax, fraction=0.045)
    fig.suptitle(f"Wealth-tax sweep at N={SCALE*100}: single-tier (threshold × rate) "
                 f"with state spending package", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "tax_sweep_n10k.png", dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"### Scale-up experiments at N={SCALE*100} ###")

    by_policy = run_policy_suite()
    plot_policy_compare(by_policy)
    plot_top_wealth_distribution(by_policy)
    counts = plot_billionaire_count(by_policy)

    # Save policy summary.
    policy_summary = {}
    for name in POLICY_SUBSET:
        last = [r[-1] for r in by_policy[name]["runs"]]
        policy_summary[name] = {
            "final_gini": float(np.mean([h["gini"] for h in last])),
            "final_alive": float(np.mean([h["alive"] for h in last])),
            "final_closure": float(np.mean([h["autocatalytic_closure"]
                                            for h in last])),
            "final_top10": float(np.mean([h["top10_share"] for h in last])),
            "final_top1": float(np.mean([h["top1_share"] for h in last])),
            "final_state_wealth": float(np.mean([h["state_wealth"] for h in last])),
            "mean_metabolic": float(np.mean([row["metabolic_rate"]
                                             for r in by_policy[name]["runs"]
                                             for row in r])),
            "billionaire_count_mean": float(counts[name]["≥£1B"]),
            "centi_millionaire_count_mean": float(counts[name]["≥£100M"]),
            "decimillionaire_count_mean": float(counts[name]["≥£10M"]),
        }
    with open(OUT_DATA / "policy_summary_n10k.json", "w") as f:
        json.dump(policy_summary, f, indent=2)

    # Table.
    print()
    print(f"{'policy':<28} {'alive':>6} {'closure':>8} {'top1':>6} "
          f"{'≥£10M':>7} {'≥£100M':>7} {'≥£1B':>5}")
    for name in POLICY_SUBSET:
        s = policy_summary[name]
        print(f"{name:<28} {s['final_alive']:6.0f} "
              f"{s['final_closure']:8.3f} {s['final_top1']:6.3f} "
              f"{s['decimillionaire_count_mean']:7.0f} "
              f"{s['centi_millionaire_count_mean']:7.0f} "
              f"{s['billionaire_count_mean']:5.0f}")

    # Sweep.
    sweep = run_tax_sweep()
    plot_tax_sweep(sweep)
    np.savez_compressed(OUT_DATA / "tax_sweep_n10k.npz",
                        thresholds=sweep["thresholds"],
                        rates=sweep["rates"],
                        **{k: v for k, v in sweep["grids"].items()})

    print()
    print("== Sweep: max_wealth_gbp (rows=threshold, cols=rate 0→0.08) ==")
    print((sweep["grids"]["max_wealth_gbp"].mean(axis=2) / 1e9).round(3))
    print("(values in £billions)")
    print()
    print("== Sweep: top1_share ==")
    print(sweep["grids"]["top1_share"].mean(axis=2).round(3))


if __name__ == "__main__":
    main()
