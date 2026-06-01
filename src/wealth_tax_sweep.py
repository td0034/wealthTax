"""
Wealth tax parameter sweeps.

Two sweeps:

(A) threshold × bottom_rate.  Fixed: state spending package (UBI 0.4 +
    state_employs 0.3 + state_buys 5). Vary the *single-tier* wealth tax
    threshold and rate. Answers: "where to set the bracket and what rate
    is needed for the system to be viable".

(B) bottom_rate × top_rate, holding thresholds at £10M, £100M, £1B.
    Three-tier progressive scheme. Answers: "how aggressive does the top
    rate need to be once the lower brackets are in place".

Output: heatmaps + 3D surfaces in out/wealth_tax_sweep/.

Usage: python3 wealth_tax_sweep.py
"""
from __future__ import annotations

from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from sim import Dials, run

OUT = Path("out/figures/wealth_tax")
OUT_DATA = Path("out/data")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)


# Baseline state-spending package used across sweeps so we isolate the
# tax-design effect rather than mixing it with spending.
SPENDING_BASE = Dials(
    inheritance_tax_rate=0.4,
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)


METRICS = ["gini", "alive", "autocatalytic_closure",
           "top10_share", "top1_share",
           "top1_share_corrected", "top10_share_corrected", "gini_corrected",
           "state_wealth", "tax_collected"]


def _one_run_A(args):
    """Sweep A: single-tier tax, vary (threshold, rate)."""
    thresh, rate, seed, ticks = args
    d = replace(SPENDING_BASE, wealth_tax_tiers=((float(thresh), float(rate)),), seed=seed)
    h = run(d, ticks=ticks)
    last = h[-1]
    mean_meta = float(np.mean([row["metabolic_rate"] for row in h]))
    out = {k: float(last[k]) for k in METRICS}
    out["mean_metabolic_rate"] = mean_meta
    return out


def _one_run_B(args):
    """Sweep B: three-tier progressive, fixed thresholds, vary rates."""
    bottom_rate, top_rate, seed, ticks = args
    tiers = ((100.0, float(bottom_rate)),
             (1000.0, float(bottom_rate)),
             (10000.0, float(top_rate)))
    d = replace(SPENDING_BASE, wealth_tax_tiers=tiers, seed=seed)
    h = run(d, ticks=ticks)
    last = h[-1]
    mean_meta = float(np.mean([row["metabolic_rate"] for row in h]))
    out = {k: float(last[k]) for k in METRICS}
    out["mean_metabolic_rate"] = mean_meta
    return out


def run_sweep_A(seeds: int = 3, ticks: int = 200):
    thresholds = np.array([1, 3, 10, 30, 100, 300, 1000, 3000, 10000], dtype=float)
    rates = np.linspace(0.0, 0.08, 9)
    args = [(t, r, s, ticks)
            for t in thresholds for r in rates for s in range(seeds)]
    print(f"sweep A: {len(args)} runs ...")
    with Pool(max(1, cpu_count() - 1)) as p:
        results = p.map(_one_run_A, args)
    nt, nr = len(thresholds), len(rates)
    metrics = METRICS + ["mean_metabolic_rate"]
    grids = {m: np.zeros((nt, nr, seeds)) for m in metrics}
    i = 0
    for ti in range(nt):
        for ri in range(nr):
            for s in range(seeds):
                for m in metrics:
                    grids[m][ti, ri, s] = results[i][m]
                i += 1
    return {"thresholds": thresholds, "rates": rates, "grids": grids}


def run_sweep_B(seeds: int = 3, ticks: int = 200):
    bottom = np.linspace(0.0, 0.05, 9)
    top = np.linspace(0.0, 0.10, 9)
    args = [(b, t, s, ticks)
            for b in bottom for t in top for s in range(seeds)]
    print(f"sweep B: {len(args)} runs ...")
    with Pool(max(1, cpu_count() - 1)) as p:
        results = p.map(_one_run_B, args)
    nb, nt = len(bottom), len(top)
    metrics = METRICS + ["mean_metabolic_rate"]
    grids = {m: np.zeros((nb, nt, seeds)) for m in metrics}
    i = 0
    for bi in range(nb):
        for ti in range(nt):
            for s in range(seeds):
                for m in metrics:
                    grids[m][bi, ti, s] = results[i][m]
                i += 1
    return {"bottom": bottom, "top": top, "grids": grids}


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_A(sweep) -> None:
    thresholds = sweep["thresholds"]; rates = sweep["rates"]
    metrics = ["gini", "alive", "autocatalytic_closure", "top10_share",
               "top1_share", "mean_metabolic_rate", "state_wealth", "tax_collected"]
    fig, axes = plt.subplots(2, 4, figsize=(20, 9))
    axes = axes.flatten()
    for ax, m in zip(axes, metrics):
        grid = sweep["grids"][m].mean(axis=2)        # (nt, nr)
        im = ax.imshow(grid.T, origin="lower", aspect="auto",
                       extent=(0, len(thresholds) - 1, rates.min(), rates.max()),
                       cmap="viridis")
        ax.set_xticks(range(len(thresholds)))
        ax.set_xticklabels([f"{int(t)}" for t in thresholds], rotation=45, fontsize=7)
        ax.set_xlabel("threshold (model units; 100 = £10M)")
        ax.set_ylabel("annual rate")
        ax.set_title(m)
        plt.colorbar(im, ax=ax, fraction=0.045)
    fig.suptitle("Sweep A: single-tier wealth tax (threshold × rate) with state-spending package",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "sweep_A_heatmaps.png", dpi=110)
    plt.close(fig)

    # 3D surface for alive + closure.
    fig = plt.figure(figsize=(18, 6))
    for idx, m in enumerate(["alive", "autocatalytic_closure", "gini"], start=1):
        ax = fig.add_subplot(1, 3, idx, projection="3d")
        T = np.log10(thresholds)               # log-spaced thresholds → use index space
        R = rates
        X, Y = np.meshgrid(np.arange(len(thresholds)), R, indexing="ij")
        ax.plot_surface(X, Y, sweep["grids"][m].mean(axis=2),
                        cmap="viridis", edgecolor="none", alpha=0.95)
        ax.set_xticks(range(len(thresholds)))
        ax.set_xticklabels([f"{int(t)}" for t in thresholds], rotation=40, fontsize=7)
        ax.set_xlabel("threshold (model units)")
        ax.set_ylabel("rate"); ax.set_zlabel(m)
        ax.set_title(m)
        ax.view_init(elev=26, azim=-58)
    fig.suptitle("Sweep A: 3D surfaces", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "sweep_A_3d.png", dpi=110)
    plt.close(fig)


def plot_B(sweep) -> None:
    bottom = sweep["bottom"]; top = sweep["top"]
    metrics = ["gini", "alive", "autocatalytic_closure", "top10_share",
               "top1_share", "mean_metabolic_rate", "state_wealth", "tax_collected"]
    fig, axes = plt.subplots(2, 4, figsize=(20, 9))
    axes = axes.flatten()
    for ax, m in zip(axes, metrics):
        grid = sweep["grids"][m].mean(axis=2)
        im = ax.imshow(grid.T, origin="lower", aspect="auto",
                       extent=(bottom.min(), bottom.max(), top.min(), top.max()),
                       cmap="viridis")
        ax.set_xlabel("bottom marginal rate (above £10M)")
        ax.set_ylabel("top marginal rate (above £1B)")
        ax.set_title(m)
        plt.colorbar(im, ax=ax, fraction=0.045)
    fig.suptitle("Sweep B: three-tier progressive wealth tax (£10M / £100M / £1B)",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "sweep_B_heatmaps.png", dpi=110)
    plt.close(fig)

    fig = plt.figure(figsize=(18, 6))
    for idx, m in enumerate(["alive", "autocatalytic_closure", "gini"], start=1):
        ax = fig.add_subplot(1, 3, idx, projection="3d")
        X, Y = np.meshgrid(bottom, top, indexing="ij")
        ax.plot_surface(X, Y, sweep["grids"][m].mean(axis=2),
                        cmap="viridis", edgecolor="none", alpha=0.95)
        ax.set_xlabel("bottom rate"); ax.set_ylabel("top rate"); ax.set_zlabel(m)
        ax.set_title(m)
        ax.view_init(elev=26, azim=-58)
    fig.suptitle("Sweep B: 3D surfaces", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "sweep_B_3d.png", dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    sa = run_sweep_A()
    plot_A(sa)
    sb = run_sweep_B()
    plot_B(sb)
    np.savez_compressed(
        OUT_DATA / "wealth_tax_sweep.npz",
        A_thresholds=sa["thresholds"], A_rates=sa["rates"],
        **{f"A_{m}": sa["grids"][m] for m in sa["grids"]},
        B_bottom=sb["bottom"], B_top=sb["top"],
        **{f"B_{m}": sb["grids"][m] for m in sb["grids"]},
    )
    print()
    print("== Sweep A: alive (rows=threshold, cols=rate 0..0.08) ==")
    print(sa["grids"]["alive"].mean(axis=2).round(1))
    print()
    print("== Sweep A: autocatalytic_closure ==")
    print(sa["grids"]["autocatalytic_closure"].mean(axis=2).round(3))
    print()
    print("== Sweep B: alive (rows=bottom 0..0.05, cols=top 0..0.10) ==")
    print(sb["grids"]["alive"].mean(axis=2).round(1))
    print()
    print("== Sweep B: autocatalytic_closure ==")
    print(sb["grids"]["autocatalytic_closure"].mean(axis=2).round(3))


if __name__ == "__main__":
    main()
