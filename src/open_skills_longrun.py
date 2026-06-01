"""
A2 knockout: long-run cumulative novelty.

Runs the open-skills variant at increasing time horizons (400, 800,
1600 ticks) to test whether the discovery rate plateaus or continues.
A plateau would suggest pseudo-OEE; continued discovery supports the
open-endedness claim.

Usage: python3 open_skills_longrun.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from open_skills import run

OUT = Path("out/figures/scenarios")
OUT.mkdir(parents=True, exist_ok=True)


def main():
    horizons = [400, 800, 1600]
    seeds = 5
    K_MAX = 25

    K_by_horizon = {}
    for ticks in horizons:
        Ks = []
        for s in range(seeds):
            K_traj, _, _ = run(novelty_rate=0.02, K_max=K_MAX,
                               ticks=ticks, seed=s + 200)
            Ks.append(K_traj)
        K_by_horizon[ticks] = np.stack(Ks)

    # Discovery rate (skill dims added per 100 ticks) across windows.
    print(f"{'horizon':>8} {'K_final mean':>15} {'K_final std':>12} "
          f"{'dims/100 ticks':>16}")
    rates = {}
    for ticks in horizons:
        Ks = K_by_horizon[ticks]
        final = Ks[:, -1]
        per_100 = (final - 5) / (ticks / 100)
        rates[ticks] = (float(np.mean(per_100)),
                        float(np.std(per_100)))
        print(f"{ticks:>8} {float(np.mean(final)):>15.2f} "
              f"{float(np.std(final)):>12.2f} "
              f"{float(np.mean(per_100)):>16.3f}")

    fig, ax = plt.subplots(figsize=(11, 5.5))
    for ticks in horizons:
        Ks = K_by_horizon[ticks]
        t = np.arange(ticks)
        ax.plot(t, Ks.mean(axis=0), lw=1.8, label=f"horizon {ticks}")
        ax.fill_between(t, Ks.min(axis=0), Ks.max(axis=0), alpha=0.18)
    ax.axhline(5, color="grey", ls=":", alpha=0.5)
    ax.axhline(K_MAX, color="grey", ls=":", alpha=0.5)
    ax.set_xlabel("tick")
    ax.set_ylabel("active skill dimensions")
    ax.set_title("Long-run open-skill discovery: novelty rate 0.02, "
                 "wealth-coupled, $K_{max}=25$")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "open_skills_longrun.png", dpi=120)
    plt.close(fig)
    print(f"\nsaved {OUT / 'open_skills_longrun.png'}")


if __name__ == "__main__":
    main()
