"""
A6 knockout: hard material constraint.

Run current_world and maker_economy with finite material pool that
depletes via maker production and replenishes at a fixed rate. Show
that closure metric tracks survival (low regen rate -> material
exhaustion -> collapse) and validate the autopoietic reading of Phi.

Usage: python3 material_constraint.py
"""
from __future__ import annotations

import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, make_initial_population, step, Type
from scenarios import SCENARIOS

OUT = Path("out/figures/scenarios")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)


TICKS = 200
SEEDS = 4


def _run(args):
    scenario, regen_rate, seed = args
    base = SCENARIOS[scenario]
    d = replace(base, seed=seed,
                material_pool_initial=50.0,
                material_pool_regen=regen_rate)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    history = []
    pool_history = []
    for t in range(TICKS):
        history.append(step(agents, d, rng, t, accum))
        pool_history.append(accum.get("material_pool", 0.0))
    return scenario, regen_rate, seed, history, pool_history


def main():
    # regen rates: 0 (no replenishment), 5 (low), 20 (high), 100 (infinite-like)
    regens = [0.0, 5.0, 20.0, 100.0]
    scenarios = ["current_world", "maker_economy"]
    args = [(sc, r, s) for sc in scenarios for r in regens for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    t0 = time.time()
    print(f"running {len(args)} runs ...")
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    # Group: (scenario, regen) -> list of (history, pool_history)
    grouped: dict[tuple[str, float], list] = {}
    for sc, r, sd, h, p in results:
        grouped.setdefault((sc, r), []).append((h, p))

    summary = {}
    for (sc, r), runs in grouped.items():
        final_alive = [run[0][-1]["alive"] for run in runs]
        final_phi   = [run[0][-1]["autocatalytic_closure"] for run in runs]
        final_pool  = [run[1][-1] for run in runs]
        summary[(sc, r)] = {
            "alive_median": float(np.median(final_alive)),
            "phi_median": float(np.median(final_phi)),
            "pool_median": float(np.median(final_pool)),
        }

    print()
    print(f"{'scenario':<16} {'regen':>6} {'alive':>6} {'Phi':>6} {'pool_final':>11}")
    for sc in scenarios:
        for r in regens:
            s = summary[(sc, r)]
            print(f"{sc:<16} {r:>6.1f} {s['alive_median']:>6.1f} "
                  f"{s['phi_median']:>6.3f} {s['pool_median']:>11.1f}")

    # Plot.
    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    for col, sc in enumerate(scenarios):
        ax_alive = axes[0, col]
        ax_pool = axes[1, col]
        for r in regens:
            runs = grouped[(sc, r)]
            alives = np.stack([np.array([h["alive"] for h in run[0]]) for run in runs])
            pools = np.stack([np.array(run[1]) for run in runs])
            t = np.arange(TICKS)
            ax_alive.plot(t, alives.mean(axis=0), lw=1.8,
                          label=f"regen={r:.0f}")
            ax_alive.fill_between(t, alives.min(axis=0), alives.max(axis=0),
                                  alpha=0.15)
            ax_pool.plot(t, pools.mean(axis=0), lw=1.8,
                         label=f"regen={r:.0f}")
        ax_alive.set_title(f"{sc}: alive over time")
        ax_alive.set_xlabel("tick"); ax_alive.set_ylabel("alive")
        ax_alive.grid(alpha=0.3); ax_alive.legend(fontsize=9)
        ax_pool.set_title(f"{sc}: material pool over time")
        ax_pool.set_xlabel("tick"); ax_pool.set_ylabel("material units")
        ax_pool.grid(alpha=0.3); ax_pool.legend(fontsize=9)
    fig.suptitle("Hard material constraint: finite input pool with "
                 "regeneration", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "material_constraint.png", dpi=120)
    plt.close(fig)
    print(f"\nsaved {OUT / 'material_constraint.png'}")


if __name__ == "__main__":
    main()
