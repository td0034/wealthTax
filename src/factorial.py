"""
Clean tax x spending x inheritance factorial (E-5).

Separates the wealth-tax schedule from the spending package from the
inheritance regime, so the policy comparison no longer bundles them.

Cells:
    tax_schedule  in  {none, zucman_flat_2pct, zucman_progressive_2_4_8}
    spending      in  {off, on}                       (UBI+employs+buys bundle)
    inheritance   in  {0.0, 0.4, 0.8}

3 x 2 x 3 = 18 cells. N=100, 6 seeds, 200 ticks.

Usage: python3 factorial.py
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, replace
from itertools import product
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, run

OUT = Path("out/figures/policies")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")


TAX_SCHEDULES = {
    "none": (),
    "zucman_flat":        ((100.0, 0.02),),
    "zucman_progressive": ((100.0, 0.02), (1000.0, 0.02), (10000.0, 0.04)),
}

SPENDING = {
    "off": dict(ubi=0.0, state_employs_fraction=0.0,
                state_employs_wage=1.0, state_buys_maker_output=0.0),
    "on":  dict(ubi=0.4, state_employs_fraction=0.3,
                state_employs_wage=0.8, state_buys_maker_output=5.0),
}

INHERITANCE_RATES = [0.0, 0.4, 0.8]

SEEDS = 6
TICKS = 200


def _run(args):
    tax_name, spend_name, iota, seed = args
    spend_kwargs = SPENDING[spend_name]
    d = Dials(
        seed=seed,
        wealth_tax_tiers=TAX_SCHEDULES[tax_name],
        inheritance_tax_rate=iota,
        **spend_kwargs,
    )
    h = run(d, ticks=TICKS)
    last = h[-1]
    return tax_name, spend_name, iota, seed, last


def main():
    cells = list(product(TAX_SCHEDULES.keys(), SPENDING.keys(),
                         INHERITANCE_RATES))
    args = [(*c, s) for c in cells for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    t0 = time.time()
    print(f"running {len(args)} factorial cells across {n_proc} procs ...")
    with Pool(n_proc) as p:
        rows = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    keys = ["gini", "alive", "autocatalytic_closure",
            "top10_share", "state_wealth"]
    grouped: dict[tuple, dict[str, list[float]]] = {}
    for tn, sn, io, sd, last in rows:
        k = (tn, sn, io)
        grouped.setdefault(k, {kk: [] for kk in keys})
        for kk in keys:
            grouped[k][kk].append(float(last[kk]))

    cell_summary = []
    for (tn, sn, io), vals in grouped.items():
        cell_summary.append({
            "tax_schedule": tn, "spending": sn, "inheritance": io,
            **{f"{kk}_median": float(np.median(vals[kk])) for kk in keys},
            **{f"{kk}_iqr_lo": float(np.percentile(vals[kk], 25)) for kk in keys},
            **{f"{kk}_iqr_hi": float(np.percentile(vals[kk], 75)) for kk in keys},
        })
    with open(OUT_DATA / "factorial_summary.json", "w") as f:
        json.dump(cell_summary, f, indent=2)

    # Print table
    print()
    print(f"{'tax':<22} {'spend':<5} {'iota':>5} {'alive':>6} "
          f"{'gini':>5} {'Phi':>6} {'top10':>6}")
    for cell in cell_summary:
        print(f"{cell['tax_schedule']:<22} "
              f"{cell['spending']:<5} "
              f"{cell['inheritance']:>5.1f} "
              f"{cell['alive_median']:>6.0f} "
              f"{cell['gini_median']:>5.2f} "
              f"{cell['autocatalytic_closure_median']:>6.3f} "
              f"{cell['top10_share_median']:>6.2f}")

    # Plot: 2x3 grid of small heatmaps. Rows: 2 spending levels. Cols: 3 inheritance levels.
    metrics = ["alive_median", "gini_median",
               "autocatalytic_closure_median", "top10_share_median"]
    titles = ["alive", "Gini (no state)", "Phi", "top-10 share"]
    tax_names = list(TAX_SCHEDULES.keys())
    spend_names = list(SPENDING.keys())
    iotas = INHERITANCE_RATES

    for metric, title in zip(metrics, titles):
        fig, axes = plt.subplots(len(spend_names), len(iotas),
                                 figsize=(13, 6), sharey=True)
        for r_idx, sn in enumerate(spend_names):
            for c_idx, io in enumerate(iotas):
                ax = axes[r_idx, c_idx]
                vals = []
                for tn in tax_names:
                    cell = next(c for c in cell_summary
                                if c["tax_schedule"] == tn
                                and c["spending"] == sn
                                and abs(c["inheritance"] - io) < 1e-6)
                    vals.append(cell[metric])
                ax.bar(tax_names, vals, color=["#9ca3af", "#2563eb", "#0ea5e9"])
                ax.set_title(f"spend={sn}, iota={io}", fontsize=10)
                for i, v in enumerate(vals):
                    ax.text(i, v, f"{v:.2f}" if v < 100 else f"{v:.0f}",
                            ha="center", va="bottom", fontsize=8)
                ax.grid(alpha=0.25, axis="y")
                ax.tick_params(axis="x", rotation=30, labelsize=8)
        fig.suptitle(f"Factorial: {title}", fontsize=13)
        fig.tight_layout()
        fname = OUT / f"factorial_{metric}.png"
        fig.savefig(fname, dpi=120)
        plt.close(fig)
        print(f"  saved {fname}")

    # Compute marginal effects.
    def mean_by(filter_fn) -> dict[str, float]:
        out = {kk: [] for kk in keys}
        for cell in cell_summary:
            if filter_fn(cell):
                for kk in keys:
                    out[kk].append(cell[f"{kk}_median"])
        return {kk: float(np.mean(v)) if v else 0.0 for kk, v in out.items()}

    print("\nMarginal mean over levels:")
    for tn in tax_names:
        m = mean_by(lambda c, _tn=tn: c["tax_schedule"] == _tn)
        print(f"  tax={tn:<22} alive={m['alive']:.1f}  "
              f"Phi={m['autocatalytic_closure']:.3f}  top10={m['top10_share']:.2f}")
    for sn in spend_names:
        m = mean_by(lambda c, _sn=sn: c["spending"] == _sn)
        print(f"  spend={sn:<5}                  alive={m['alive']:.1f}  "
              f"Phi={m['autocatalytic_closure']:.3f}  top10={m['top10_share']:.2f}")
    for io in iotas:
        m = mean_by(lambda c, _io=io: abs(c["inheritance"] - _io) < 1e-6)
        print(f"  iota={io}                        alive={m['alive']:.1f}  "
              f"Phi={m['autocatalytic_closure']:.3f}  top10={m['top10_share']:.2f}")


if __name__ == "__main__":
    main()
