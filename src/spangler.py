"""
Reproduce Spangler & Sarkar 2022's headline finding within our model:
skill inheritance raises inequality (Tier 3 #33).

Test design:
  Baseline:  default bandwidth-coupled skill transmission.
  Treatment: skill_mutation_rate=1.0 (every skill dim fresh-drawn each
             generation, so inheritance carries nothing).

If baseline shows higher Gini / top-shares than treatment, we recover
their result with our different mechanism (channel-rich ABM) instead
of theirs (estate-tax + Carnegie effect ABM).

Usage: python3 spangler.py
"""
from __future__ import annotations

import json
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, run

OUT = Path("out/figures/policies")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")


TICKS = 250
SEEDS = 10


def _run(args):
    label, mutation_rate, from_prior, seed = args
    d = Dials(seed=seed, skill_mutation_rate=mutation_rate,
              inherit_from_class_prior=from_prior)
    h = run(d, ticks=TICKS)
    return label, seed, h[-1]


def main():
    # Three arms:
    #   default        : mu=0.05, parent-derived values (the model baseline)
    #   class_prior    : mu=0.05, class-typical-prior values (CLEAN Spangler toggle,
    #                    holds bandwidth + class-bias persistence fixed)
    #   no_inheritance : mu=1.0,  parent-derived values (confounded arm: also
    #                    destroys bandwidth gating and class-bias persistence;
    #                    kept for reference and contrast with the clean toggle)
    args = []
    for s in range(SEEDS):
        args.append(("default",        0.05, False, s))
        args.append(("class_prior",    0.05, True,  s))
        args.append(("no_inheritance", 1.00, False, s))
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    with Pool(n_proc) as p:
        results = p.map(_run, args)

    by_label = {"default": [], "class_prior": [], "no_inheritance": []}
    for label, seed, last in results:
        by_label[label].append(last)

    summary = {}
    for label, runs in by_label.items():
        gini = np.array([r["gini"] for r in runs])
        top1 = np.array([r["top1_share"] for r in runs])
        top10 = np.array([r["top10_share"] for r in runs])
        alive = np.array([r["alive"] for r in runs])
        breadth = np.array([r["cultural_breadth"] for r in runs])
        diversity = np.array([r["cultural_diversity"] for r in runs])
        summary[label] = {
            "gini_median": float(np.median(gini)),
            "gini_iqr": [float(np.percentile(gini, 25)),
                         float(np.percentile(gini, 75))],
            "top1_median": float(np.median(top1)),
            "top10_median": float(np.median(top10)),
            "alive_median": float(np.median(alive)),
            "breadth_median": float(np.median(breadth)),
            "diversity_median": float(np.median(diversity)),
        }

    print()
    print(f"{'metric':<22} {'default':>11} {'class_prior':>14} {'no_inh':>10}  "
          f"{'cp-def':>8} {'nh-def':>8}")
    for key in ["gini_median", "top1_median", "top10_median",
                "alive_median", "breadth_median", "diversity_median"]:
        a = summary["default"][key]
        b = summary["class_prior"][key]
        c = summary["no_inheritance"][key]
        print(f"{key:<22} {a:>11.3f} {b:>14.3f} {c:>10.3f}  "
              f"{b - a:>+8.3f} {c - a:>+8.3f}")

    print()
    print("Clean Spangler test: default vs class_prior. Both share bandwidth")
    print("gating and class-bias persistence; only transmitted values change.")
    delta_clean = summary["class_prior"]["gini_median"] - summary["default"]["gini_median"]
    if delta_clean < 0:
        print(f"  class_prior Gini is LOWER than default by {-delta_clean:.3f}")
        print("  => skill inheritance from parent RAISES Gini relative to class prior")
        print("     i.e. partial Spangler & Sarkar reproduction.")
    else:
        print(f"  class_prior Gini is HIGHER than default by {delta_clean:.3f}")
        print("  => skill inheritance from parent LOWERS Gini relative to class prior")
        print("     i.e. opposite of Spangler & Sarkar in this clean toggle.")

    with open(OUT_DATA / "spangler_reproduction.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Plot.
    labels = ["default", "class_prior", "no_inheritance"]
    metrics = ["gini_median", "top1_median", "top10_median",
               "alive_median", "breadth_median", "diversity_median"]
    metric_titles = ["Gini (state excluded)", "Top-1% share",
                     "Top-10% share", "Alive", "Cultural breadth",
                     "Cultural diversity"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    for ax, m, t in zip(axes, metrics, metric_titles):
        vals = [summary[l][m] for l in labels]
        bars = ax.bar(labels, vals, color=["#2563eb", "#0ea5e9", "#9ca3af"])
        ax.set_title(t)
        ax.grid(alpha=0.25, axis="y")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=9)
    fig.suptitle("Spangler & Sarkar (2022) reproduction: "
                 "does skill inheritance raise inequality?", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "spangler_reproduction.png", dpi=120)
    plt.close(fig)
    print(f"saved {OUT / 'spangler_reproduction.png'}")


if __name__ == "__main__":
    main()
