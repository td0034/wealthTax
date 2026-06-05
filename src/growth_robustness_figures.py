"""Figures for the robustness checks in the growth paper."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA = Path("out/data")
OUT = Path("out/figures/growth")

ARMS_ORDER = ["A_status_quo", "C_zucman_2pct", "D_cap_5M",
              "E_hybrid_5pct", "F_hybrid_10pct"]
ARM_LABELS = {
    "A_status_quo":   "status quo",
    "C_zucman_2pct":  "Zucman 2%",
    "D_cap_5M":       "cap £5M",
    "E_hybrid_5pct":  "hybrid 5%",
    "F_hybrid_10pct": "hybrid 10%",
}
COLOURS = ["#777777", "#cc6677", "#ddcc77", "#117733", "#117733"]


def fig_alpha_sweep():
    r = json.loads((DATA / "growth_robustness.json").read_text())["alpha_sweep"]
    alphas = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]

    fig, ax = plt.subplots(1, 1, figsize=(9, 5))

    regime = "R0_baseline"   # use baseline as representative
    for arm, colour in zip(ARMS_ORDER, COLOURS):
        ratios = [r[regime][f"alpha_{a}"][arm] for a in alphas]
        ax.plot(alphas, ratios, "o-", color=colour, linewidth=2,
                 markersize=7, label=ARM_LABELS[arm])

    ax.axhline(1.0, color="black", linestyle=":", linewidth=1,
                label="status quo line")
    ax.axvspan(0.18, 0.22, alpha=0.20, color="grey",
                label=r"empirical $\alpha=0.20$")
    ax.set_xlabel(r"$\alpha$: share of extractive flow counted as GDP")
    ax.set_ylabel("CGDP ratio vs status quo (log scale)")
    ax.set_yscale("log")
    ax.set_title("R-A: CGDP-collapse finding is robust across the entire "
                  r"$\alpha$ range." + "\n"
                  "Wealth-tax arms never cross status quo on the CGDP measure.")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig_alpha_sweep.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_alpha_sweep.png'}")


def fig_capability_compositions():
    r = json.loads((DATA / "growth_robustness.json").read_text())[
        "capability_composition"]

    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5), sharey=True)

    forms = [("product", "product\n(base case)"),
              ("geomean", "geometric mean\n(HDI-style)"),
              ("addmean", "arithmetic mean\n(simple average)"),
              ("mpi",     "MPI-style\n(deprivation)")]
    regimes = ["R0_baseline", "R1_heterodox",
                "R2_symmetric", "R3_orthodox"]
    regime_labels = ["baseline", "heterodox", "symmetric", "orthodox"]

    for ax, (form_key, form_label) in zip(axes, forms):
        x = np.arange(len(ARMS_ORDER))
        w = 0.20
        for j, (reg, reg_lbl) in enumerate(zip(regimes, regime_labels)):
            vals = [r[reg][a][f"CI_{form_key}"] for a in ARMS_ORDER]
            ax.bar(x + (j - 1.5) * w, vals, width=w,
                    label=reg_lbl, alpha=0.85)
        ax.axhline(1.0, color="black", linestyle=":", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels([ARM_LABELS[a] for a in ARMS_ORDER],
                            fontsize=7, rotation=20)
        ax.set_title(form_label)
        ax.set_ylim(0.97, 1.16)
        ax.grid(True, alpha=0.3, axis="y")
        if form_key == "product":
            ax.set_ylabel("CI ratio vs status quo")
            ax.legend(fontsize=6, loc="upper left")

    fig.suptitle("R-B: Capability composition robustness.\n"
                 "All four composition forms show the wealth-tax case "
                 "winning across all four regimes.",
                  fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_capability_compositions.png",
                 dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_capability_compositions.png'}")


def main():
    fig_alpha_sweep()
    fig_capability_compositions()


if __name__ == "__main__":
    main()
