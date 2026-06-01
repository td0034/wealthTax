"""
Analytical stationary wealth for the top rentier under tax tau above
threshold theta and capital return r (E-2).

Derivation. Per tick a rentier with wealth w >= theta accrues r*w from
capital return and pays tau*(w - theta) in wealth tax. The fixed point
of w' = w + r*w - tau*max(0, w - theta) is

    w*  =  tau * theta / (tau - r)   when tau > r,
    diverges                         when tau <= r,

assuming mortality and debt write-off do not bind.

This script computes w* for a grid of (tau, theta), runs the simulation
with each, and plots predicted vs observed top wealth. Replaces the
"top-tier-does-not-bind tautology" framing.

Usage: python3 fixed_point.py
"""
from __future__ import annotations

import json
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import (Dials, Type, WEALTH_UNIT_GBP, make_initial_population, step)

OUT = Path("out/figures/wealth_tax")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")


SCALE = 10                       # N=1000 for speed
TICKS = 250
SEEDS = 4


def predicted_w_star(tau: float, theta: float, r: float) -> float:
    if tau <= r:
        return float("inf")
    return tau * theta / (tau - r)


def _run(args):
    tau, theta, seed = args
    d = Dials(
        population_scale=SCALE,
        seed=seed,
        wealth_tax_tiers=((float(theta), float(tau)),),
        inheritance_tax_rate=0.4,
        ubi=0.4,
        state_employs_fraction=0.3,
        state_buys_maker_output=5.0,
    )
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
    living = [a for a in agents if a.alive and a.type != Type.STATE]
    if not living:
        return tau, theta, seed, 0.0
    return tau, theta, seed, float(max(a.net_worth for a in living))


def main():
    # Grid of (tau, theta) sweeping the tau>r and tau<r regimes
    taus = np.array([0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12])
    thetas = np.array([100.0, 1000.0])   # 10M and 100M
    r = Dials().capital_return            # default 0.04

    args = [(t, th, s) for t in taus for th in thetas for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} sims (N={SCALE*100}) ...")
    with Pool(n_proc) as p:
        rows = p.map(_run, args)

    by_param: dict[tuple, list[float]] = {}
    for tau, theta, seed, top in rows:
        by_param.setdefault((tau, theta), []).append(top)

    # Build comparison table.
    print()
    print(f"r = {r}")
    print(f"{'tau':>6} {'theta':>8} {'w* (predicted)':>18} "
          f"{'observed (median)':>20} {'IQR':>25}")
    table = []
    for theta in thetas:
        for tau in taus:
            w_star = predicted_w_star(tau, theta, r)
            obs = np.array(by_param[(tau, theta)])
            med = float(np.median(obs))
            lo, hi = float(np.percentile(obs, 25)), float(np.percentile(obs, 75))
            ws_str = "diverges" if not np.isfinite(w_star) else f"{w_star:>12.1f}"
            print(f"{tau:>6.3f} {theta:>8.0f} {ws_str:>18} "
                  f"{med:>20.1f} [{lo:.0f}, {hi:.0f}]")
            table.append({"tau": tau, "theta": theta, "r": r,
                          "w_star_predicted": (None if not np.isfinite(w_star)
                                               else float(w_star)),
                          "w_top_observed_median": med,
                          "w_top_observed_iqr": [lo, hi]})

    with open(OUT_DATA / "fixed_point_predictions.json", "w") as f:
        json.dump(table, f, indent=2)

    # Plot.
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, theta in zip(axes, thetas):
        obs_med = np.array([np.median(by_param[(t, theta)]) for t in taus])
        obs_lo  = np.array([np.percentile(by_param[(t, theta)], 25) for t in taus])
        obs_hi  = np.array([np.percentile(by_param[(t, theta)], 75) for t in taus])
        ax.fill_between(taus, obs_lo * WEALTH_UNIT_GBP, obs_hi * WEALTH_UNIT_GBP,
                        alpha=0.2, color="C0", label="observed IQR")
        ax.plot(taus, obs_med * WEALTH_UNIT_GBP, "o-", color="C0",
                lw=2, label="observed median top wealth")
        # analytical
        w_pred = np.array([predicted_w_star(t, theta, r) for t in taus])
        valid = np.isfinite(w_pred)
        ax.plot(taus[valid], w_pred[valid] * WEALTH_UNIT_GBP, "x--",
                color="C3", lw=2, label="analytical w* (tau>r)")
        ax.axvline(r, color="grey", ls=":", alpha=0.6)
        ax.text(r * 1.02, ax.get_ylim()[1] * 0.9, "tau = r",
                fontsize=9, color="grey")
        ax.set_xlabel("tau (wealth-tax rate above threshold)")
        ax.set_ylabel("top wealth (£)")
        ax.set_yscale("log")
        ax.set_title(f"theta = {int(theta)} units = £{theta * WEALTH_UNIT_GBP/1e6:.0f}M")
        ax.grid(alpha=0.25, which="both")
        ax.legend(fontsize=9)
    fig.suptitle(
        "Stationary top wealth: analytical fixed point vs simulation observation\n"
        f"(N={SCALE*100}, r={r}, baseline spending package)",
        fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "fixed_point.png", dpi=120)
    plt.close(fig)
    print(f"\nsaved {OUT / 'fixed_point.png'}")


if __name__ == "__main__":
    main()
