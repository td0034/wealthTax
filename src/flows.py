"""
Sankey of steady-state per-tick wealth flows.

Runs three policies at N=10k (UK Tory, Zucman 2pct spend, Socialist),
collects mean per-tick flows by (source_class, destination_class) from
the steady-state phase, and renders ribbon Sankey diagrams.

Steady state is taken as ticks 80..180 (first 80 dropped as transient).

Usage: python3 flows.py
"""
from __future__ import annotations

import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle

from sim import Dials, Type, TYPE_COLOURS, make_initial_population, step
from policies import POLICIES
from scenarios import SCENARIOS

OUT = Path("out/figures/policies")
OUT.mkdir(parents=True, exist_ok=True)

SCALE = 100
TICKS_TOTAL = 180
TICKS_TRANSIENT = 80
SEEDS = 3

PANELS = [
    ("uk_tory_2010_24", POLICIES["uk_tory_2010_24"]),
    ("zucman_2pct_spend", POLICIES["zucman_2pct_spend"]),
    ("socialist", SCENARIOS["socialist"]),
]

# Display order of classes top-to-bottom in the Sankey.
NODE_ORDER = ["WORKER", "MAKER", "EMPLOYER", "LENDER", "RENTIER",
              "SPECULATOR", "STATE"]
NODE_INDEX = {name: i for i, name in enumerate(NODE_ORDER)}
NODE_COLOURS = {n: TYPE_COLOURS[Type[n]] for n in NODE_ORDER}


def _run_one(args):
    name, dials, seed = args
    d = replace(dials, population_scale=SCALE, seed=seed)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(TICKS_TOTAL):
        step(agents, d, rng, t, accum)
        if t == TICKS_TRANSIENT - 1:
            accum["flows"] = {}    # discard transient
    flows = accum.get("flows", {})
    # Convert to a 7x7 matrix; mean per tick.
    M = np.zeros((len(NODE_ORDER), len(NODE_ORDER)))
    n_ticks_steady = TICKS_TOTAL - TICKS_TRANSIENT
    for (src, dst), v in flows.items():
        if src not in NODE_INDEX or dst not in NODE_INDEX:
            continue
        M[NODE_INDEX[src], NODE_INDEX[dst]] += v / n_ticks_steady
    return name, seed, M


# ---------------------------------------------------------------------------
# Sankey rendering
# ---------------------------------------------------------------------------

def ribbon(ax, sx, sy_top, sy_bot, dx, dy_top, dy_bot, color, alpha=0.45):
    """Draw a filled ribbon between (sx, sy_top..sy_bot) and (dx, dy_top..dy_bot)."""
    cx_a = (sx + dx) / 2
    verts = [
        (sx, sy_top),
        (cx_a, sy_top), (cx_a, dy_top), (dx, dy_top),
        (dx, dy_bot),
        (cx_a, dy_bot), (cx_a, sy_bot), (sx, sy_bot),
        (sx, sy_top),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    ax.add_patch(PathPatch(MplPath(verts, codes),
                           facecolor=color, edgecolor="none", alpha=alpha))


def draw_sankey(ax, M: np.ndarray, title: str, min_share: float = 0.005):
    """Draw a two-column ribbon Sankey on the given Axes."""
    n = len(NODE_ORDER)
    outflow = M.sum(axis=1)
    inflow = M.sum(axis=0)
    total = max(outflow.sum(), inflow.sum(), 1e-9)

    F = M / total
    out_n = outflow / total
    in_n = inflow / total

    gap = 0.025
    src_top = np.zeros(n); pos = 0.0
    for i in range(n):
        src_top[i] = pos
        pos += out_n[i] + (gap if out_n[i] > 0 else 0)
    dst_top = np.zeros(n); pos = 0.0
    for i in range(n):
        dst_top[i] = pos
        pos += in_n[i] + (gap if in_n[i] > 0 else 0)

    out_used = np.zeros(n)
    in_used = np.zeros(n)

    SRC_X, DST_X = 0.18, 0.82

    # Sort flows: draw biggest first so smaller ribbons sit on top.
    flow_list = []
    for i in range(n):
        for j in range(n):
            if F[i, j] >= min_share:
                flow_list.append((F[i, j], i, j))
    flow_list.sort(reverse=True)

    for f, i, j in flow_list:
        sy_t = src_top[i] + out_used[i]
        sy_b = sy_t + f
        dy_t = dst_top[j] + in_used[j]
        dy_b = dy_t + f
        out_used[i] += f
        in_used[j] += f
        ribbon(ax, SRC_X, sy_t, sy_b, DST_X, dy_t, dy_b, NODE_COLOURS[NODE_ORDER[i]])

    # Node boxes + labels
    box_w = 0.04
    for i, name in enumerate(NODE_ORDER):
        if out_n[i] > 0:
            ax.add_patch(Rectangle((SRC_X - box_w, src_top[i]), box_w, out_n[i],
                                   facecolor=NODE_COLOURS[name], edgecolor="none"))
            ax.text(SRC_X - box_w - 0.01, src_top[i] + out_n[i] / 2,
                    name, ha="right", va="center", fontsize=8)
        if in_n[i] > 0:
            ax.add_patch(Rectangle((DST_X, dst_top[i]), box_w, in_n[i],
                                   facecolor=NODE_COLOURS[name], edgecolor="none"))
            ax.text(DST_X + box_w + 0.01, dst_top[i] + in_n[i] / 2,
                    name, ha="left", va="center", fontsize=8)

    span = max(src_top[-1] + out_n[-1], dst_top[-1] + in_n[-1])
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(span + 0.05, -0.05)   # inverted so top-to-bottom
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(title, fontsize=11)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = [(name, dials, s) for name, dials in PANELS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} N=10k runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run_one, args)
    print(f"  done in {time.time()-t0:.1f}s")

    # Aggregate flow matrices per policy.
    by_policy: dict[str, np.ndarray] = {}
    for name, dials in PANELS:
        Ms = [M for nm, sd, M in results if nm == name]
        by_policy[name] = np.mean(np.stack(Ms), axis=0)

    # Render three panels side-by-side.
    fig, axes = plt.subplots(1, len(PANELS), figsize=(20, 7.5))
    for ax, (name, _) in zip(axes, PANELS):
        M = by_policy[name]
        total = M.sum()
        title = f"{name}\nmean total flow / tick: {total:,.0f} units"
        draw_sankey(ax, M, title)
    fig.suptitle("Steady-state wealth flows by policy (per-tick mean, N=10,000)",
                 fontsize=14, y=1.02)
    fig.tight_layout()
    out_path = OUT / "sankey_flows.png"
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {out_path}")

    # Print top flows per panel for inspection.
    for name, _ in PANELS:
        M = by_policy[name]
        total = M.sum()
        print(f"\n== {name}  (total = {total:,.0f} / tick) ==")
        flow_list = []
        for i, src in enumerate(NODE_ORDER):
            for j, dst in enumerate(NODE_ORDER):
                if M[i, j] > 0:
                    flow_list.append((M[i, j], src, dst))
        flow_list.sort(reverse=True)
        for v, s, d in flow_list[:10]:
            print(f"  {s:>10} -> {d:<10} {v:>10.1f}  ({100*v/total:.1f}%)")


if __name__ == "__main__":
    main()
