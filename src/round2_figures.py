"""
Round 2 figures generation from JSON outputs.

Three figures for the round 2 paper:
  fig_decomp.png    R2-1 kill-switch 5-arm decomposition (bot-50 share)
  fig_enforcement.png  R2-4 enforcement sensitivity curve
  fig_equal_revenue.png  R2-6 equal-revenue head-to-head
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA = Path("out/data")
OUT = Path("out/figures/round2")
OUT.mkdir(parents=True, exist_ok=True)


def fig_decomp():
    s = json.loads((DATA / "round2_killswitch.json").read_text())
    arms = ["A_status_quo", "B_spend_only", "C_iht40_spend",
            "D_cap_spend", "E_cap_iht_spend"]
    labels = ["status quo",
              "+ recirculation\n(UBI + state jobs)",
              "+ recirculation\n+ IHT 40% flat",
              "+ recirculation\n+ £5M cap",
              "+ recirculation\n+ cap + IHT 40%"]
    bot50 = [s[a]["bottom_50_share"] * 100 for a in arms]
    top10 = [s[a]["top_10_share"] * 100 for a in arms]
    state_rev = [s[a]["state_wealth_final_gbp"] / 1e9 for a in arms]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = ["#777777", "#888888", "#cc6677", "#117733", "#117733"]
    edge = ["none", "none", "none", "none", "black"]
    x = np.arange(len(arms))

    ax = axes[0]
    bars = ax.bar(x, bot50, color=colors, edgecolor=edge, linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=0)
    ax.set_ylabel("bottom-50% wealth share (%)", fontsize=10)
    ax.set_title("Ownership: cap vs IHT decomposition", fontsize=11)
    ax.set_ylim(0, 25)
    for i, v in enumerate(bot50):
        ax.text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)

    ax = axes[1]
    ax.bar(x, top10, color=colors, edgecolor=edge, linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("top-10% wealth share (%)", fontsize=10)
    ax.set_title("Top concentration", fontsize=11)
    ax.set_ylim(0, 110)
    for i, v in enumerate(top10):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    ax.axhline(57, color="black", linestyle="--", linewidth=1)
    ax.text(0.05, 60, "UK reality (WAS): ~57%", fontsize=8)

    ax = axes[2]
    bars = ax.bar(x, state_rev, color=colors, edgecolor=edge, linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("state ending wealth (£B)", fontsize=10)
    ax.set_title("State revenue", fontsize=11)
    for i, v in enumerate(state_rev):
        ax.text(i, v + 200, f"£{v:.0f}B", ha="center", fontsize=9)

    fig.suptitle("R2-1: IHT 40% raises 20x more revenue than the cap "
                  "and delivers zero of the ownership effect",
                  fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_decomp.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_decomp.png'}")


def fig_enforcement():
    s = json.loads((DATA / "round2_enforcement.json").read_text())
    rates = sorted([float(k.split("_")[1]) for k in s.keys()])
    bot50 = [s[f"capture_{r}"]["bottom_50_share"] * 100 for r in rates]
    bn = [s[f"capture_{r}"]["billionaires"] for r in rates]
    top10 = [s[f"capture_{r}"]["top_10_share"] * 100 for r in rates]
    cm = [s[f"capture_{r}"]["centimillionaires"] for r in rates]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    ax = axes[0]
    ax.plot(rates, bot50, marker="o", linewidth=2, color="#117733")
    ax.fill_between([0.3, 0.6], 0, 25, alpha=0.15, color="red",
                     label="realistic UK enforcement\n(BPR/APR/trusts)")
    ax.set_xlabel("inheritance capture rate", fontsize=10)
    ax.set_ylabel("bottom-50% wealth share (%)", fontsize=10)
    ax.set_title("Bottom-50% ownership lift", fontsize=11)
    ax.set_xlim(0.3, 1.05)
    ax.set_ylim(0, 25)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(rates, bn, marker="o", linewidth=2, color="#cc6677",
             label="billionaires (£1B+)")
    ax.plot(rates, cm, marker="s", linewidth=2, color="#ddcc77",
             label="centi-millionaires (£100M+)")
    ax.fill_between([0.3, 0.6], 0, 900, alpha=0.15, color="red")
    ax.set_xlabel("inheritance capture rate", fontsize=10)
    ax.set_ylabel("count at terminal tick", fontsize=10)
    ax.set_title("Top wealth holder counts", fontsize=11)
    ax.set_xlim(0.3, 1.05)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.plot(rates, top10, marker="o", linewidth=2, color="#332288")
    ax.fill_between([0.3, 0.6], 0, 110, alpha=0.15, color="red")
    ax.axhline(57, color="black", linestyle="--", linewidth=1,
                label="UK reality (WAS) ~57%")
    ax.set_xlabel("inheritance capture rate", fontsize=10)
    ax.set_ylabel("top-10% wealth share (%)", fontsize=10)
    ax.set_title("Top-10% concentration", fontsize=11)
    ax.set_xlim(0.3, 1.05)
    ax.set_ylim(40, 105)
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("R2-4: The cap requires near-perfect enforcement.\n"
                 "At 90% capture (still optimistic for UK),"
                 " the ownership effect collapses.",
                  fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_enforcement.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_enforcement.png'}")


def fig_equal_revenue():
    s = json.loads((DATA / "round2_equal_revenue.json").read_text())
    cap_rev = s["cap"]["state_wealth_final_gbp"] / 1e9

    arms = ["cap", "wt_0.0001", "wt_0.002", "wt_0.02"]
    labels = [f"cap £5M\n(£{cap_rev:.0f}B rev)",
              "WT 0.01%\n(equal rev)",
              "WT 0.2%\n(~13x rev)",
              "WT 2% (Zucman)\n(~10x rev)"]
    bot50 = [s[a]["bottom_50_share"] * 100 for a in arms]
    top10 = [s[a]["top_10_share"] * 100 for a in arms]
    bn = [s[a]["billionaires"] for a in arms]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    colors = ["#117733", "#cc6677", "#cc6677", "#cc6677"]
    x = np.arange(len(arms))

    ax = axes[0]
    ax.bar(x, bot50, color=colors)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("bottom-50% wealth share (%)")
    ax.set_title("Bottom-50% ownership lift")
    ax.set_ylim(0, 22)
    for i, v in enumerate(bot50):
        ax.text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)

    ax = axes[1]
    ax.bar(x, top10, color=colors)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("top-10% wealth share (%)")
    ax.set_title("Top-10% concentration")
    ax.set_ylim(0, 110)
    for i, v in enumerate(top10):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)

    ax = axes[2]
    ax.bar(x, bn, color=colors)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("billionaires at terminal tick")
    ax.set_title("Billionaires")
    for i, v in enumerate(bn):
        ax.text(i, v + 20, f"{v:.0f}", ha="center", fontsize=9)

    fig.suptitle("R2-6: An equal-revenue wealth tax delivers zero of the cap's "
                 "distributional effect.\n"
                 "Even at 10x revenue (Zucman 2%), the wealth tax fails "
                 "to break top concentration.",
                  fontsize=11, y=1.05)
    fig.tight_layout()
    fig.savefig(OUT / "fig_equal_revenue.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_equal_revenue.png'}")


def main():
    fig_decomp()
    fig_enforcement()
    fig_equal_revenue()


if __name__ == "__main__":
    main()
