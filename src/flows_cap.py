"""
Cap-specific Sankey: how the inheritance cap reshapes the per-tick
wealth flows at the joint-calibrated UK baseline.

Three panels:
  status_quo     : no cap, no wealth tax (baseline)
  cap_alone      : £5M absolute cap on inheritance, no wealth tax
  cap_plus_zucman: £5M cap + Zucman 2% above £10M

All three at the joint-calibrated UK baseline (r=0.08, rent=0.20,
subsistence=0.30) with the state-spending package on (so the
inheritance excess collected by the state actually recirculates as
UBI and state-employment wages).

The story the diagram tells: the cap converts dynastic stock into
circulating flow. Wealth that would have stayed locked in the
rentier-lender deposit loop becomes state revenue (via inheritance
excess at death) which then flows back to workers, makers, and
employers via UBI and state employment.

Usage: python3 src/flows_cap.py
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

OUT = Path("out/figures/policies")
OUT.mkdir(parents=True, exist_ok=True)

SCALE = 100
TICKS_TOTAL = 180
TICKS_TRANSIENT = 80
SEEDS = 3

# Joint-calibrated UK baseline with state-spending package on.
BASE = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    interest_rate=0.06,
    wealth_tax_tiers=(),
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)

PANELS = [
    ("status_quo",      dict()),
    ("zucman_2pct",     dict(wealth_tax_tiers=((100.0, 0.02),))),
    ("interest_ban",    dict(interest_rate=0.0)),
    ("cap_alone",       dict(inheritance_cap=50.0)),
    ("cap_plus_zucman", dict(inheritance_cap=50.0,
                              wealth_tax_tiers=((100.0, 0.02),))),
]

DISPLAY_TITLE = {
    "status_quo":      "status quo",
    "zucman_2pct":     "Zucman 2% above £10M",
    "interest_ban":    "interest ban ($i=0$)",
    "cap_alone":       "£5M bequest cap",
    "cap_plus_zucman": "£5M cap + Zucman 2%",
}

# Display order of classes top-to-bottom in the Sankey.
NODE_ORDER = ["WORKER", "MAKER", "EMPLOYER", "LENDER", "RENTIER",
              "SPECULATOR", "STATE"]
NODE_INDEX = {name: i for i, name in enumerate(NODE_ORDER)}
NODE_COLOURS = {n: TYPE_COLOURS[Type[n]] for n in NODE_ORDER}


def _run_one(args):
    name, overrides, seed = args
    config = dict(BASE)
    config.update(overrides)
    d = Dials(population_scale=SCALE, seed=seed, **config)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(TICKS_TOTAL):
        step(agents, d, rng, t, accum)
        if t == TICKS_TRANSIENT - 1:
            accum["flows"] = {}    # discard transient
    flows = accum.get("flows", {})
    n_ticks_steady = TICKS_TOTAL - TICKS_TRANSIENT
    M = np.zeros((len(NODE_ORDER), len(NODE_ORDER)))
    for (src, dst), v in flows.items():
        if src not in NODE_INDEX or dst not in NODE_INDEX:
            continue
        M[NODE_INDEX[src], NODE_INDEX[dst]] += v / n_ticks_steady
    return name, seed, M


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
        ribbon(ax, SRC_X, sy_t, sy_b, DST_X, dy_t, dy_b,
               NODE_COLOURS[NODE_ORDER[i]])

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
    ax.set_ylim(span + 0.05, -0.05)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(title, fontsize=11)


def main():
    args = [(name, overrides, s)
            for name, overrides in PANELS
            for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} N=10k runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run_one, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_panel: dict[str, np.ndarray] = {}
    for name, _ in PANELS:
        Ms = [M for nm, sd, M in results if nm == name]
        by_panel[name] = np.mean(np.stack(Ms), axis=0)

    # Split into two figures for readability: three rate-based
    # interventions in the first figure, two cap-based in the second.
    noncap_panels = [("status_quo", None), ("zucman_2pct", None),
                      ("interest_ban", None)]
    cap_panels = [("cap_alone", None), ("cap_plus_zucman", None)]

    def _render(panels, n_cols, figsize, out_name, suptitle):
        fig, axes = plt.subplots(1, n_cols, figsize=figsize)
        if n_cols == 1:
            axes = [axes]
        for ax, (name, _) in zip(axes, panels):
            M = by_panel[name]
            total = M.sum()
            title = (f"{DISPLAY_TITLE[name]}\n"
                     f"mean total flow / tick: {total:,.0f} units")
            draw_sankey(ax, M, title)
        fig.suptitle(suptitle, fontsize=13, y=1.02)
        fig.tight_layout()
        path = OUT / out_name
        fig.savefig(path, dpi=140, bbox_inches="tight")
        plt.close(fig)
        print(f"saved {path}")

    _render(noncap_panels, 3, (17, 6.5), "sankey_cap_noncap.png",
            "Per-tick wealth flows under the three rate-based interventions\n"
            "(joint-calibrated UK baseline, $r=0.08$, "
            "$N=10{,}000$, 3 seeds, steady-state ticks 80--180)")
    _render(cap_panels, 2, (12, 6.5), "sankey_cap_capped.png",
            "Per-tick wealth flows under the two cap-based interventions\n"
            "(same baseline, same seeds)")

    print()
    for name, _ in PANELS:
        M = by_panel[name]
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
