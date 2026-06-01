"""
3D phase portraits for Unequal Agents.

(1) State-space trajectories of each scenario in (gini, autocatalytic_closure,
    alive) — the manifold of viable economies.
(2) 3D surface plots over the 2D sweep grids saved in out/sweeps/sweeps.npz.

Usage: python3 phase3d.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from sim import Dials, run_multi, aggregate
from scenarios import SCENARIOS

OUT = Path("out/figures/phase")
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# (1) State-space trajectories
# ---------------------------------------------------------------------------

def trajectory(name: str, d: Dials, ticks: int = 250, seeds: int = 4
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    runs = run_multi(d, ticks=ticks, seeds=seeds)
    gini_m, *_ = aggregate(runs, "gini")
    closure_m, *_ = aggregate(runs, "autocatalytic_closure")
    alive_m, *_ = aggregate(runs, "alive")
    return gini_m, closure_m, alive_m


SCENARIO_COLOURS = {
    "current_world": "#3b82f6",
    "stevenson_world": "#ef4444",
    "maker_economy": "#22c55e",
    "tax_and_spend": "#a855f7",
    "nordic": "#0ea5e9",
    "inheritance_break": "#9333ea",
    "memory_equalised": "#f59e0b",
    "memory_starved": "#7c2d12",
    "inheritance_break_ubi": "#14b8a6",
    "feudal": "#7f1d1d",
    "creditless": "#6b7280",
    "pure_speculation": "#db2777",
    "socialist": "#0f766e",
}


def plot_phase_portrait() -> None:
    fig = plt.figure(figsize=(13, 10))
    ax = fig.add_subplot(111, projection="3d")
    endpoints = []
    for name, d in SCENARIOS.items():
        g, c, a = trajectory(name, d, ticks=250, seeds=4)
        col = SCENARIO_COLOURS.get(name, "k")
        ax.plot(g, c, a, color=col, lw=1.6, alpha=0.85, label=name)
        # Mark endpoint.
        ax.scatter([g[-1]], [c[-1]], [a[-1]], color=col, s=60,
                   edgecolors="black", linewidths=0.6)
        endpoints.append((name, float(g[-1]), float(c[-1]), float(a[-1])))
    ax.set_xlabel("Gini")
    ax.set_ylabel("Autocatalytic closure")
    ax.set_zlabel("Alive")
    ax.set_title("Phase portrait: trajectories in (Gini, Closure, Alive)")
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=2)
    ax.view_init(elev=22, azim=-58)
    fig.tight_layout()
    fig.savefig(OUT / "phase3d_trajectories.png", dpi=120)
    plt.close(fig)
    return endpoints


def plot_phase_views(endpoints) -> None:
    """2D shadows of the same manifold, for inspection."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    pairs = [(1, 2, "closure", "alive"),
             (0, 2, "gini", "alive"),
             (0, 1, "gini", "closure")]
    for ax, (i, j, xl, yl) in zip(axes, pairs):
        for name, *vals in endpoints:
            col = SCENARIO_COLOURS.get(name, "k")
            ax.scatter(vals[i], vals[j], color=col, s=70,
                       edgecolors="black", linewidths=0.5)
            ax.annotate(name, (vals[i], vals[j]), fontsize=7,
                        xytext=(3, 3), textcoords="offset points")
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=0.2)
    fig.suptitle("Endpoint shadows of the phase portrait", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "phase3d_shadows.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# (2) 3D surfaces from saved sweeps
# ---------------------------------------------------------------------------

def plot_sweep_surface(npz_path: Path) -> None:
    data = np.load(npz_path, allow_pickle=True)
    sweep_names = sorted({k.split("_")[0] + ("" if "_" not in k[len(k.split("_")[0]):]
                          else "") for k in data.files if k.endswith("_x")})
    # Pull out base names ending in "_x"
    base_names = [k[:-2] for k in data.files if k.endswith("_x")]

    surface_specs = [
        ("rent_vs_r", "gini"),
        ("rent_vs_r", "autocatalytic_closure"),
        ("tax_vs_ubi", "alive"),
        ("tax_vs_ubi", "autocatalytic_closure"),
        ("memory", "cultural_breadth"),
        ("memory", "gini"),
        ("state_action", "autocatalytic_closure"),
        ("inheritance_x_ubi", "alive"),
        ("inheritance_x_ubi", "autocatalytic_closure"),
    ]

    fig = plt.figure(figsize=(20, 14))
    for idx, (sweep, metric) in enumerate(surface_specs, start=1):
        if f"{sweep}_x" not in data.files:
            continue
        x = data[f"{sweep}_x"]; y = data[f"{sweep}_y"]
        xkey = str(data[f"{sweep}_xkey"]); ykey = str(data[f"{sweep}_ykey"])
        grid = data[f"{sweep}_{metric}"].mean(axis=2)   # (nx, ny)
        X, Y = np.meshgrid(x, y, indexing="ij")
        ax = fig.add_subplot(3, 3, idx, projection="3d")
        ax.plot_surface(X, Y, grid, cmap="viridis", edgecolor="none", alpha=0.95)
        ax.set_xlabel(xkey, fontsize=8)
        ax.set_ylabel(ykey, fontsize=8)
        ax.set_title(f"{sweep}: {metric}", fontsize=9)
        ax.view_init(elev=26, azim=-60)
    fig.suptitle("3D parameter landscapes", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "phase3d_landscapes.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("phase portrait ...")
    endpoints = plot_phase_portrait()
    plot_phase_views(endpoints)
    npz = Path("out/data/sweeps.npz")
    if npz.exists():
        print("sweep landscapes ...")
        plot_sweep_surface(npz)
    print("done. endpoints:")
    print(f"{'scenario':<22} {'gini':>5} {'closure':>8} {'alive':>6}")
    for name, g, c, a in endpoints:
        print(f"{name:<22} {g:5.2f} {c:8.3f} {a:6.1f}")


if __name__ == "__main__":
    main()
