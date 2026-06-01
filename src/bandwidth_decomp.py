"""
Decomposition of the memory-sweep cultural-breadth response into the
base-bandwidth (b0) effect and the wealth-coupling (bw) effect (AL-2).

Also reports the realised distribution of bandwidth_dims_at_birth by
class across a representative run, so the reader can see whether the
wealth coupling actually bites at default parameters.

Usage: python3 bandwidth_decomp.py
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import Dials, Type, make_initial_population, step, SKILL_DIMS

OUT = Path("out/figures/sweeps")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")


def decompose_memory_sweep():
    d = np.load(OUT_DATA / "sweeps.npz", allow_pickle=True)
    if "memory_cultural_breadth" not in d.files:
        print("Memory sweep results not found in sweeps.npz; rerun sweeps.py first.")
        return None
    grid = d["memory_cultural_breadth"].mean(axis=2)  # (nb0, nbw)
    b0 = d["memory_x"]
    bw = d["memory_y"]
    # Marginal effects
    b0_marg = grid.mean(axis=1)  # mean over bw axis: response as function of b0
    bw_marg = grid.mean(axis=0)  # mean over b0 axis
    b0_range = float(b0_marg.max() - b0_marg.min())
    bw_range = float(bw_marg.max() - bw_marg.min())
    print(f"Memory sweep cultural breadth grid {grid.shape}")
    print(f"  b0 axis range: {b0[0]:.2f} - {b0[-1]:.2f}")
    print(f"  bw axis range: {bw[0]:.2f} - {bw[-1]:.2f}")
    print(f"  marginal breadth response to b0: {b0_range:.3f}  "
          f"(min {b0_marg.min():.2f}, max {b0_marg.max():.2f})")
    print(f"  marginal breadth response to bw: {bw_range:.3f}  "
          f"(min {bw_marg.min():.2f}, max {bw_marg.max():.2f})")
    return grid, b0, bw, b0_marg, bw_marg


def realised_bandwidth_distribution(seed: int = 0, ticks: int = 250):
    """Run a representative current_world scenario and return realised
    bandwidth_dims_at_birth per class for the population produced over the
    run via reproduction."""
    d = Dials(seed=seed)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    by_class: dict[str, list[int]] = {}
    snapshot_ids = {a.id for a in agents}
    for t in range(ticks):
        step(agents, d, rng, t, accum)
    # Bandwidth dims at birth recorded on each child agent; the parent has
    # `bandwidth_dims_at_birth = 0` (initial generation never inherited).
    for a in agents:
        if a.id in snapshot_ids:
            continue
        by_class.setdefault(a.type.name, []).append(a.bandwidth_dims_at_birth)
    return by_class


def main():
    out = decompose_memory_sweep()
    if out is None:
        return
    grid, b0, bw, b0_marg, bw_marg = out

    by_class = realised_bandwidth_distribution()

    fig, axes = plt.subplots(1, 3, figsize=(20, 5.5))

    # 1) heatmap of breadth on (b0, bw)
    im = axes[0].imshow(grid.T, origin="lower", aspect="auto",
                        extent=(b0.min(), b0.max(), bw.min(), bw.max()),
                        cmap="viridis")
    axes[0].set_xlabel("b0 (base bandwidth share)")
    axes[0].set_ylabel("bw (wealth coupling slope)")
    axes[0].set_title("Cultural breadth (sweep mean)")
    plt.colorbar(im, ax=axes[0], fraction=0.045)

    # 2) marginal effects
    axes[1].plot(b0, b0_marg, marker="o", label="vs b0 (avg over bw)", lw=2)
    axes[1].plot(bw, bw_marg, marker="s", label="vs bw (avg over b0)", lw=2)
    axes[1].set_xlabel("parameter value")
    axes[1].set_ylabel("mean cultural breadth")
    axes[1].set_title("Marginal effect of b0 vs bw")
    axes[1].grid(alpha=0.3); axes[1].legend()

    # 3) realised bandwidth distribution by class
    classes_present = [c for c in ["WORKER", "MAKER", "EMPLOYER",
                                   "LENDER", "RENTIER", "SPECULATOR"]
                       if c in by_class and by_class[c]]
    if classes_present:
        bx = np.arange(1, SKILL_DIMS + 1)
        width = 0.8 / len(classes_present)
        for i, cls in enumerate(classes_present):
            arr = np.array(by_class[cls])
            counts = np.array([(arr == k).sum() for k in bx], dtype=float)
            counts = counts / counts.sum() if counts.sum() else counts
            axes[2].bar(bx + (i - len(classes_present) / 2) * width, counts,
                        width, label=cls)
        axes[2].set_xticks(bx); axes[2].set_xlabel("bandwidth_dims_at_birth")
        axes[2].set_ylabel("share of children")
        axes[2].set_title(
            "Realised bandwidth distribution by class\n"
            "(current_world, log-wealth coupling)")
        axes[2].legend(fontsize=8)
        axes[2].grid(alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig(OUT / "bandwidth_decomp.png", dpi=130)
    plt.close(fig)
    print(f"saved {OUT / 'bandwidth_decomp.png'}")


if __name__ == "__main__":
    main()
