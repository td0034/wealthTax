"""Figures for the growth paper."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA = Path("out/data")
OUT = Path("out/figures/growth")
OUT.mkdir(parents=True, exist_ok=True)

ARMS_ORDER = ["A_status_quo", "C_zucman_2pct", "D_cap_5M",
              "E_hybrid_5pct", "F_hybrid_10pct"]
ARM_LABELS = {
    "A_status_quo":   "status quo",
    "C_zucman_2pct":  "Zucman 2%",
    "D_cap_5M":       "cap £5M",
    "E_hybrid_5pct":  "hybrid 5%",
    "F_hybrid_10pct": "hybrid 10%",
}
REGIME_ORDER = ["R0_baseline", "R1_heterodox", "R2_symmetric", "R3_orthodox"]
REGIME_LABELS = {
    "R0_baseline":   "no productivity\nchannel",
    "R1_heterodox":  "heterodox\n(skill 0.5, cap 0.1)",
    "R2_symmetric":  "symmetric\n(skill 0.3, cap 0.3)",
    "R3_orthodox":   "orthodox\n(skill 0.1, cap 0.5)",
}


def fig_portfolio_six():
    s = json.loads((DATA / "growth_portfolio.json").read_text())
    measures = [
        ("GMT_cum",      "GMT\n(extractive-inclusive)",      True),
        ("CGDP_cum",     "CGDP\n(orthodox proxy)",            True),
        ("PT_cum",       "PT\n(productive only)",             False),
        ("CI_terminal",  "CI\n(capability)",                  False),
        ("KS_total_skill_mass", "KS\n(knowledge stock)",      False),
        ("bottom_50_share", "bottom-50%\nwealth share",       False),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for idx, (mkey, title, log_scale) in enumerate(measures):
        ax = axes[idx // 3][idx % 3]
        sq_baseline = s[f"A_status_quo__R0_baseline"][mkey]

        for j, arm in enumerate(ARMS_ORDER):
            x_pos = j
            values = [s[f"{arm}__{r}"][mkey] for r in REGIME_ORDER]
            if mkey == "bottom_50_share":
                values_scaled = [v * 100 for v in values]
            elif log_scale:
                values_scaled = [v / max(sq_baseline, 1e-9) for v in values]
            else:
                values_scaled = [v / max(sq_baseline, 1e-9) for v in values]

            color = "#777777" if arm == "A_status_quo" else (
                    "#cc6677" if arm == "C_zucman_2pct" else (
                    "#ddcc77" if arm == "D_cap_5M" else "#117733"))
            offsets = (np.arange(len(REGIME_ORDER)) - 1.5) * 0.18
            alphas = [0.4, 0.7, 0.85, 1.0]
            for off, val, alpha in zip(offsets, values_scaled, alphas):
                ax.bar(x_pos + off, val, width=0.18,
                        color=color, alpha=alpha)

        ax.set_xticks(range(len(ARMS_ORDER)))
        ax.set_xticklabels([ARM_LABELS[a] for a in ARMS_ORDER],
                            fontsize=8, rotation=15)
        ax.set_title(title, fontsize=10)
        if log_scale:
            ax.set_yscale("log")
            ax.set_ylabel("ratio vs status quo (log)")
        elif mkey == "bottom_50_share":
            ax.set_ylabel("share (%)")
        else:
            ax.set_ylabel("ratio vs status quo")
        ax.grid(True, alpha=0.3, axis="y")
        if idx == 0:
            from matplotlib.patches import Patch
            handles = [Patch(facecolor="grey", alpha=a,
                              label=REGIME_LABELS[r].replace("\n", " "))
                       for a, r in zip([0.4, 0.7, 0.85, 1.0], REGIME_ORDER)]
            ax.legend(handles=handles, fontsize=6, loc="upper right")

    fig.suptitle("Six growth measures across five policy arms and four "
                  "productivity-channel regimes\n"
                  "The orthodox prediction holds only on extractive-inclusive "
                  "measures (GMT, CGDP); reverses on all others.",
                  fontsize=11, y=1.00)
    fig.tight_layout()
    fig.savefig(OUT / "fig_portfolio_six.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_portfolio_six.png'}")


def fig_orthodox_vs_alternative():
    """Two-panel: orthodox measure says wealth tax bad; alternatives say good."""
    s = json.loads((DATA / "growth_portfolio.json").read_text())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    ax = axes[0]
    cgdp = [s[f"{a}__R0_baseline"]["CGDP_cum"] for a in ARMS_ORDER]
    cgdp_sq = cgdp[0]
    cgdp_norm = [c / cgdp_sq for c in cgdp]
    colors = ["#777777", "#cc6677", "#ddcc77", "#117733", "#117733"]
    bars = ax.bar(range(len(ARMS_ORDER)), cgdp_norm, color=colors)
    ax.set_xticks(range(len(ARMS_ORDER)))
    ax.set_xticklabels([ARM_LABELS[a] for a in ARMS_ORDER], fontsize=9)
    ax.set_ylabel("CGDP (productive + 0.2 × extractive)\nratio vs status quo")
    ax.set_title("Orthodox measure (CGDP-style)\nThe wealth tax 'destroys 99% of GDP'")
    ax.set_yscale("log")
    for i, v in enumerate(cgdp_norm):
        if v >= 1e-3:
            ax.text(i, v * 1.5, f"{v:.2f}x", ha="center", fontsize=9)
        else:
            ax.text(i, v * 1.5, f"{v:.0e}", ha="center", fontsize=9)

    ax = axes[1]
    pt = [s[f"{a}__R0_baseline"]["PT_cum"] for a in ARMS_ORDER]
    ci = [s[f"{a}__R0_baseline"]["CI_terminal"] for a in ARMS_ORDER]
    ks = [s[f"{a}__R0_baseline"]["KS_total_skill_mass"] for a in ARMS_ORDER]
    pt_norm = [p / pt[0] for p in pt]
    ci_norm = [c / ci[0] for c in ci]
    ks_norm = [k / ks[0] for k in ks]

    x = np.arange(len(ARMS_ORDER))
    w = 0.27
    ax.bar(x - w, pt_norm, width=w, color="#117733", label="PT (productive throughput)")
    ax.bar(x, ci_norm, width=w, color="#332288", label="CI (capability)")
    ax.bar(x + w, ks_norm, width=w, color="#cc6677", label="KS (knowledge stock)")
    ax.axhline(1.0, color="black", linestyle=":", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([ARM_LABELS[a] for a in ARMS_ORDER], fontsize=9)
    ax.set_ylabel("ratio vs status quo")
    ax.set_title("Alternative measures\nThe wealth tax raises every other measure by 9-15%")
    ax.set_ylim(0.85, 1.20)
    ax.legend(fontsize=8, loc="upper left")
    for i, (p, c, k) in enumerate(zip(pt_norm, ci_norm, ks_norm)):
        ax.text(i - w, p + 0.005, f"{p:.2f}", ha="center", fontsize=7)
        ax.text(i, c + 0.005, f"{c:.2f}", ha="center", fontsize=7)
        ax.text(i + w, k + 0.005, f"{k:.2f}", ha="center", fontsize=7)

    fig.suptitle("The choice of growth measure is the choice of conclusion.",
                  fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_orthodox_vs_alternative.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_orthodox_vs_alternative.png'}")


def fig_growth_rates():
    s = json.loads((DATA / "growth_portfolio.json").read_text())

    fig, ax = plt.subplots(1, 1, figsize=(11, 5))

    measures = [("CGDP_growth", "CGDP growth\n(orthodox proxy)", "#cc6677"),
                ("PT_growth", "PT growth\n(productive only)", "#117733"),
                ("CI_growth", "CI growth\n(capability)", "#332288")]

    x = np.arange(len(ARMS_ORDER))
    w = 0.27
    for offset, (mkey, label, color) in zip([-w, 0, w], measures):
        values = [s[f"{a}__R0_baseline"][mkey] * 100 for a in ARMS_ORDER]
        ax.bar(x + offset, values, width=w, color=color, label=label)
        for i, v in enumerate(values):
            ax.text(i + offset, v + 0.05 if v >= 0 else v - 0.15,
                     f"{v:+.2f}", ha="center", fontsize=7)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([ARM_LABELS[a] for a in ARMS_ORDER], fontsize=10)
    ax.set_ylabel("per-tick growth rate (%)")
    ax.set_title("Status quo CGDP 'growth' is the extractive-loop compounding artefact.\n"
                  "Wealth tax 'destroys growth' only on the artefact.")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig(OUT / "fig_growth_rates.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_growth_rates.png'}")


def fig_regime_robustness():
    s = json.loads((DATA / "growth_portfolio.json").read_text())

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    for ax_i, (mkey, title, ylim) in enumerate([
        ("PT_cum", "PT (productive throughput)", (0.95, 1.18)),
        ("CI_terminal", "CI (capability)", (0.95, 1.18)),
        ("KS_total_skill_mass", "KS (knowledge stock)", (0.95, 1.20)),
    ]):
        ax = axes[ax_i]
        for r_i, regime in enumerate(REGIME_ORDER):
            sq = s[f"A_status_quo__{regime}"][mkey]
            values = [s[f"{a}__{regime}"][mkey] / max(sq, 1e-9)
                       for a in ARMS_ORDER]
            ax.plot(range(len(ARMS_ORDER)), values, "o-", linewidth=2,
                     markersize=7, label=REGIME_LABELS[regime].replace("\n", " "))
        ax.axhline(1.0, color="black", linestyle=":", linewidth=1)
        ax.set_xticks(range(len(ARMS_ORDER)))
        ax.set_xticklabels([ARM_LABELS[a] for a in ARMS_ORDER],
                            fontsize=8, rotation=15)
        ax.set_ylabel("ratio vs status quo (within regime)")
        ax.set_title(title)
        ax.set_ylim(ylim)
        ax.grid(True, alpha=0.3)
        if ax_i == 0:
            ax.legend(fontsize=7, loc="upper left")

    fig.suptitle("Robustness across productivity-channel regimes.\n"
                  "The orthodox-dominant regime (skill 0.1, capital 0.5) "
                  "does not reverse the wealth-tax advantage.",
                  fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_regime_robustness.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_regime_robustness.png'}")


def main():
    fig_portfolio_six()
    fig_orthodox_vs_alternative()
    fig_growth_rates()
    fig_regime_robustness()


if __name__ == "__main__":
    main()
