"""Figures for the hybrid wealth tax paper."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA = Path("out/data")
OUT = Path("out/figures/round2")
OUT.mkdir(parents=True, exist_ok=True)


def fig_rate_sweep():
    s = json.loads((DATA / "round2_hybrid_r9.json").read_text())
    # Plot bot-50, top-10, top-1 vs rate at fixed threshold £10M.
    rates = [0.02, 0.05, 0.10, 0.20, 0.50, 0.90]
    arms = ["wt2_10M", "wt5_10M", "wt10_10M", "wt20_10M",
            "wt50_10M", "wt90_10M"]
    bot50 = [s[a]["bottom_50_share"] * 100 for a in arms]
    top10 = [s[a]["top_10_share"] * 100 for a in arms]
    top1 = [s[a]["top_1_share"] * 100 for a in arms]
    cap_b50 = s["cap_5M"]["bottom_50_share"] * 100
    cap_t10 = s["cap_5M"]["top_10_share"] * 100
    cap_t1 = s["cap_5M"]["top_1_share"] * 100

    fig, ax = plt.subplots(1, 1, figsize=(9, 5.5))
    r = 0.08
    ax.axvspan(0.02, r, alpha=0.15, color="red",
               label=r"$\tau < r$ (Zucman 2% zone): tax cannot keep up with $r$")
    ax.axvspan(r, 0.50, alpha=0.10, color="green",
               label=r"$\tau > r$ (hybrid zone): finite ceiling on top wealth")

    ax.plot(rates, bot50, "o-", linewidth=2.5, color="#117733",
             label="bottom-50% share", markersize=8)
    ax.plot(rates, top10, "s-", linewidth=2.5, color="#332288",
             label="top-10% share", markersize=8)
    ax.plot(rates, top1, "^-", linewidth=2.5, color="#cc6677",
             label="top-1% share", markersize=8)

    ax.axhline(cap_b50, linestyle=":", color="#117733", alpha=0.7,
                label=f"cap £5M reference: bot-50 {cap_b50:.0f}%")
    ax.axhline(cap_t10, linestyle=":", color="#332288", alpha=0.7,
                label=f"cap £5M reference: top-10 {cap_t10:.0f}%")

    ax.set_xscale("log")
    ax.set_xticks(rates)
    ax.set_xticklabels([f"{r*100:.0f}%" for r in rates])
    ax.set_xlabel("wealth tax rate above £10M threshold", fontsize=11)
    ax.set_ylabel("wealth share (%)", fontsize=11)
    ax.set_title("R2-9: Wealth tax rate sweep above £10M threshold.\n"
                  r"At $\tau > r = 0.08$ the wealth tax begins to dominate the cap.",
                  fontsize=11)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(OUT / "fig_hybrid_sweep.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_hybrid_sweep.png'}")


def fig_enforce_compare():
    s_cap = json.loads((DATA / "round2_enforcement.json").read_text())
    s_h = json.loads((DATA / "round2_hybrid_r10.json").read_text())
    s_h_results = s_h["results"]

    rates = sorted([float(k.split("_")[1]) for k in s_cap.keys()])
    cap_b50 = [s_cap[f"capture_{r}"]["bottom_50_share"] * 100 for r in rates]
    cap_t10 = [s_cap[f"capture_{r}"]["top_10_share"] * 100 for r in rates]
    h_b50 = [s_h_results[f"capture_{r}"]["bottom_50_share"] * 100 for r in rates]
    h_t10 = [s_h_results[f"capture_{r}"]["top_10_share"] * 100 for r in rates]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    ax.plot(rates, cap_b50, "o-", linewidth=2.5, color="#cc6677",
             label="cap £5M", markersize=9)
    ax.plot(rates, h_b50, "s-", linewidth=2.5, color="#117733",
             label="hybrid WT 90% > £10M", markersize=9)
    ax.fill_between([0.3, 0.6], 0, 50, alpha=0.15, color="red",
                     label="realistic UK enforcement range")
    ax.set_xlabel("effective capture rate", fontsize=11)
    ax.set_ylabel("bottom-50% wealth share (%)", fontsize=11)
    ax.set_title("Bottom-50% share vs enforcement", fontsize=11)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 50)

    ax = axes[1]
    ax.plot(rates, cap_t10, "o-", linewidth=2.5, color="#cc6677",
             label="cap £5M", markersize=9)
    ax.plot(rates, h_t10, "s-", linewidth=2.5, color="#117733",
             label="hybrid WT 90% > £10M", markersize=9)
    ax.fill_between([0.3, 0.6], 0, 110, alpha=0.15, color="red")
    ax.set_xlabel("effective capture rate", fontsize=11)
    ax.set_ylabel("top-10% wealth share (%)", fontsize=11)
    ax.set_title("Top-10% concentration vs enforcement", fontsize=11)
    ax.legend(fontsize=9, loc="center right")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 110)

    fig.suptitle("R2-10 vs R2-4: the cap has a catastrophic enforcement "
                 "cliff; the hybrid is flat across the realistic range.",
                  fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_hybrid_enforce.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_hybrid_enforce.png'}")


def fig_stacked():
    s = json.loads((DATA / "round2_hybrid_loose_ends.json").read_text())
    arms = ["baseline", "cap_only", "hybrid_only", "stacked"]
    labels = ["baseline", "cap £5M only", "hybrid WT 10% > £10M only",
              "stacked\n(cap + hybrid)"]
    bot50 = [s["D_stacked"][a]["bottom_50_share"] * 100 for a in arms]
    top10 = [s["D_stacked"][a]["top_10_share"] * 100 for a in arms]
    state = [s["D_stacked"][a]["state_wealth_final_gbp"] / 1e9 for a in arms]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    colors = ["#777777", "#cc6677", "#117733", "#ddcc77"]
    x = np.arange(len(arms))

    for ax, vals, ylab, ttl in [
        (axes[0], bot50, "bottom-50% wealth share (%)", "Bottom-50% share"),
        (axes[1], top10, "top-10% wealth share (%)", "Top-10% concentration"),
        (axes[2], state, "state ending wealth (£B)", "State revenue"),
    ]:
        ax.bar(x, vals, color=colors)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel(ylab); ax.set_title(ttl)
        for i, v in enumerate(vals):
            if "share" in ylab:
                ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
            else:
                ax.text(i, v + 10, f"£{v:.0f}B", ha="center", fontsize=9)

    fig.suptitle("R2-11D: stacking the cap on the hybrid is worse than "
                 "the hybrid alone.\n"
                 "The cap converts hybrid-distributed stock into one-shot "
                 "state revenue that recirculates as consumed income.",
                  fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig_hybrid_stacked.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_hybrid_stacked.png'}")


def fig_flight_ramp():
    s = json.loads((DATA / "round2_hybrid_loose_ends.json").read_text())
    flight_rates = [0.0, 0.005, 0.01, 0.02, 0.05]
    fA = s["A_flight"]
    b50 = [fA[str(r)]["bottom_50_share"] * 100 for r in flight_rates]
    flown = [fA[str(r)]["flown_wealth_gbp"] / 1e9 for r in flight_rates]

    schedules = ["instant", "ramp_50", "ramp_100"]
    fB = s["B_ramp"]
    b50_ramp = [fB[sch]["bottom_50_share"] * 100 for sch in schedules]
    rev_ramp = [fB[sch]["state_wealth_final_gbp"] / 1e9 for sch in schedules]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    ax = axes[0]
    ax2 = ax.twinx()
    ax.plot(flight_rates, b50, "o-", linewidth=2.5, color="#117733",
             label="bot-50% (left)", markersize=9)
    ax2.plot(flight_rates, flown, "s-", linewidth=2.5, color="#cc6677",
              label="flown wealth £B (right)", markersize=9)
    ax.set_xlabel("flight base rate (per cap-multiple per tick)")
    ax.set_ylabel("bottom-50% share (%)", color="#117733")
    ax2.set_ylabel("flown wealth (£B)", color="#cc6677")
    ax.set_title("R2-11A: Hybrid flight robustness")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    ax = axes[1]
    ax2 = ax.twinx()
    xs = np.arange(len(schedules))
    ax.bar(xs - 0.2, b50_ramp, width=0.4, color="#117733",
            label="bot-50% (left)")
    ax2.bar(xs + 0.2, rev_ramp, width=0.4, color="#ddcc77",
             label="state revenue £B (right)")
    ax.set_xticks(xs)
    ax.set_xticklabels(["instant", "ramp 50 ticks", "ramp 100 ticks"])
    ax.set_ylabel("bottom-50% share (%)", color="#117733")
    ax2.set_ylabel("state revenue (£B)", color="#bb8800")
    ax.set_title("R2-11B: Transition ramp delivers same distribution\n"
                  "and raises more revenue than instant deployment")
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(OUT / "fig_hybrid_flight_ramp.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT / 'fig_hybrid_flight_ramp.png'}")


def main():
    fig_rate_sweep()
    fig_enforce_compare()
    fig_stacked()
    fig_flight_ramp()


if __name__ == "__main__":
    main()
