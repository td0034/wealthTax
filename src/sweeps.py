"""
2D parameter sweeps for Unequal Agents.

Each sweep varies two dials across a grid, runs multiple seeds, and stores
final-tick averages of {gini, alive, autocatalytic_closure, cultural_breadth,
top10_share, knowledge_lost_cum, mean_metabolic_rate, state_wealth}.

Produces a heatmap PNG per output-metric per sweep, plus a .npz with raw
arrays for downstream 3D plotting.

Usage: python3 sweeps.py
"""
from __future__ import annotations

from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, run


OUT = Path("out/figures/sweeps")
OUT_DATA = Path("out/data")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Sweep definitions
# ---------------------------------------------------------------------------

SWEEPS = {
    "rent_vs_r": {
        "x_key": "rent_share_of_wage",
        "y_key": "capital_return",
        "x_range": np.linspace(0.05, 0.65, 9),
        "y_range": np.linspace(0.005, 0.06, 9),
        "base": Dials(),
    },
    "tax_vs_ubi": {
        "x_key": "flat_tax_rate",
        "y_key": "ubi",
        "x_range": np.linspace(0.0, 0.025, 9),
        "y_range": np.linspace(0.0, 1.5, 9),
        "base": Dials(state_employs_fraction=0.3, state_employs_wage=0.8,
                      tax_progressivity=0.02),
    },
    "memory": {
        "x_key": "memory_bandwidth_base",
        "y_key": "memory_bandwidth_wealth_scale",
        "x_range": np.linspace(0.2, 1.0, 9),
        "y_range": np.linspace(0.0, 1.0, 9),
        "base": Dials(),
    },
    "state_action": {
        "x_key": "state_employs_fraction",
        "y_key": "state_buys_maker_output",
        "x_range": np.linspace(0.0, 1.0, 9),
        "y_range": np.linspace(0.0, 20.0, 9),
        # Give the state some income — otherwise spending is constrained.
        "base": Dials(flat_tax_rate=0.005, tax_progressivity=0.02),
    },
    "inheritance_x_ubi": {
        "x_key": "inheritance_tax_rate",
        "y_key": "ubi",
        "x_range": np.linspace(0.0, 1.0, 9),
        "y_range": np.linspace(0.0, 1.5, 9),
        "base": Dials(flat_tax_rate=0.005, tax_progressivity=0.02,
                      state_employs_fraction=0.3),
    },
}


METRIC_KEYS = [
    "gini", "alive", "autocatalytic_closure", "cultural_breadth",
    "top10_share", "knowledge_lost_cum", "state_wealth",
]


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def _one_run(args):
    base, x_key, y_key, x_val, y_val, seed, ticks = args
    d = replace(base, **{x_key: float(x_val), y_key: float(y_val)}, seed=seed)
    h = run(d, ticks=ticks)
    last = h[-1]
    mean_metabolic = float(np.mean([row["metabolic_rate"] for row in h]))
    out = {k: float(last[k]) for k in METRIC_KEYS}
    out["mean_metabolic_rate"] = mean_metabolic
    return out


def run_sweep(name: str, spec: dict, seeds: int = 3, ticks: int = 200,
              processes: int | None = None) -> dict:
    x_range = spec["x_range"]
    y_range = spec["y_range"]
    x_key, y_key = spec["x_key"], spec["y_key"]
    base = spec["base"]
    args = []
    for xi, x in enumerate(x_range):
        for yi, y in enumerate(y_range):
            for s in range(seeds):
                args.append((base, x_key, y_key, x, y, s, ticks))

    n_proc = processes or max(1, cpu_count() - 1)
    print(f"  {name}: {len(args)} runs across {n_proc} procs ...")
    with Pool(n_proc) as p:
        results = p.map(_one_run, args)

    nx, ny = len(x_range), len(y_range)
    metrics = METRIC_KEYS + ["mean_metabolic_rate"]
    grids = {m: np.zeros((nx, ny, seeds)) for m in metrics}
    i = 0
    for xi in range(nx):
        for yi in range(ny):
            for s in range(seeds):
                for m in metrics:
                    grids[m][xi, yi, s] = results[i][m]
                i += 1
    return {
        "x_range": x_range, "y_range": y_range,
        "x_key": x_key, "y_key": y_key,
        "grids": grids,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_heatmaps(name: str, sweep: dict) -> None:
    metrics = METRIC_KEYS + ["mean_metabolic_rate"]
    fig, axes = plt.subplots(2, 4, figsize=(20, 9))
    axes = axes.flatten()
    x = sweep["x_range"]; y = sweep["y_range"]
    for ax, m in zip(axes, metrics):
        grid = sweep["grids"][m].mean(axis=2).T   # (ny, nx) for imshow
        im = ax.imshow(grid, origin="lower", aspect="auto",
                       extent=(x.min(), x.max(), y.min(), y.max()),
                       cmap="viridis")
        ax.set_xlabel(sweep["x_key"])
        ax.set_ylabel(sweep["y_key"])
        ax.set_title(m)
        plt.colorbar(im, ax=ax, fraction=0.045)
    fig.suptitle(f"Sweep: {name}", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    all_data = {}
    for name, spec in SWEEPS.items():
        print(f"running sweep: {name}")
        sweep = run_sweep(name, spec)
        plot_heatmaps(name, sweep)
        all_data[name] = sweep
    # Persist raw arrays for 3D plots / downstream analysis.
    save_dict = {}
    for name, sweep in all_data.items():
        save_dict[f"{name}_x"] = sweep["x_range"]
        save_dict[f"{name}_y"] = sweep["y_range"]
        save_dict[f"{name}_xkey"] = sweep["x_key"]
        save_dict[f"{name}_ykey"] = sweep["y_key"]
        for m, g in sweep["grids"].items():
            save_dict[f"{name}_{m}"] = g
    np.savez_compressed(OUT_DATA / "sweeps.npz", **save_dict)
    print(f"saved {OUT/'sweeps.npz'}")


if __name__ == "__main__":
    main()
