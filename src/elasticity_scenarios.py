"""
A7 knockout: skill-to-wealth elasticity across multiple scenarios.

Runs the elasticity regression under current_world, nordic,
maker_economy, and feudal to demonstrate that the per-class skill-to-
wealth pattern is robust to the macroscenario.

Usage: python3 elasticity_scenarios.py
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import (Type, SKILL_NAMES, SKILL_DIMS,
                 make_initial_population, step)
from scenarios import SCENARIOS

OUT = Path("out/figures/scenarios")
OUT_DATA = Path("out/data")

SCENARIO_NAMES = ["current_world", "nordic", "maker_economy", "feudal"]
WARMUP = 20
WINDOW = 40
SEEDS = 8
POPULATION_SCALE = 5


def _one_run(args):
    name, seed = args
    base = SCENARIOS[name]
    d = replace(base, seed=seed, population_scale=POPULATION_SCALE)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    for t in range(WARMUP):
        step(agents, d, rng, t, accum)
    snapshot = {a.id: {"type": a.type.name, "wealth0": a.wealth,
                       "skills": a.skills.copy()}
                for a in agents if a.alive and a.type != Type.STATE}
    for t in range(WARMUP, WARMUP + WINDOW):
        step(agents, d, rng, t, accum)
    rows = []
    for a in agents:
        if a.id in snapshot:
            s = snapshot[a.id]
            wealth1 = a.wealth if a.alive else 0.0
            rows.append({
                "type": s["type"],
                "skills": s["skills"],
                "gain": wealth1 - s["wealth0"],
            })
    return name, rows


def main():
    args = [(name, s) for name in SCENARIO_NAMES for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    t0 = time.time()
    print(f"running {len(args)} runs ...")
    with Pool(n_proc) as p:
        results = p.map(_one_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_scenario_class: dict[tuple[str, str], list] = {}
    for name, rows in results:
        for r in rows:
            k = (name, r["type"])
            by_scenario_class.setdefault(k, []).append(r)

    summary: dict[str, dict] = {}
    for (scenario, cls), rows in by_scenario_class.items():
        if len(rows) < SKILL_DIMS + 5:
            continue
        X = np.stack([r["skills"] for r in rows])
        y = np.array([r["gain"] for r in rows])
        X1 = np.column_stack([np.ones(len(rows)), X])
        coefs, *_ = np.linalg.lstsq(X1, y, rcond=None)
        residuals = y - X1 @ coefs
        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        norm = abs(np.mean(y)) + 1e-9
        elasts = [float(coefs[i + 1] * np.std(X[:, i]) / norm)
                  for i in range(SKILL_DIMS)]
        summary.setdefault(scenario, {})[cls] = {
            "n": len(rows),
            "r2": float(r2),
            "elasticities": {SKILL_NAMES[i]: elasts[i] for i in range(SKILL_DIMS)},
            "mean_gain": float(np.mean(y)),
        }

    # Table.
    print()
    print(f"{'scenario':<16} {'class':<11} {'R^2':>5}  {'tech':>5} {'org':>5} {'soc':>5} {'fin':>5} {'gen':>5}  {'n':>4}")
    for sc in SCENARIO_NAMES:
        if sc not in summary:
            continue
        for cls in ("WORKER", "MAKER", "EMPLOYER", "LENDER", "RENTIER", "SPECULATOR"):
            if cls not in summary[sc]:
                continue
            s = summary[sc][cls]
            e = s["elasticities"]
            print(f"{sc:<16} {cls:<11} {s['r2']:5.2f}  "
                  f"{e['technical']:5.2f} {e['organisational']:5.2f} "
                  f"{e['social']:5.2f} {e['financial']:5.2f} {e['generative']:5.2f}  "
                  f"{s['n']:>4}")

    with open(OUT_DATA / "skill_wealth_elasticity_by_scenario.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Plot: heatmap of R^2 by (scenario, class)
    classes_present = ["WORKER", "MAKER", "EMPLOYER", "LENDER",
                       "RENTIER", "SPECULATOR"]
    R2_grid = np.full((len(SCENARIO_NAMES), len(classes_present)), np.nan)
    for i, sc in enumerate(SCENARIO_NAMES):
        for j, cls in enumerate(classes_present):
            if sc in summary and cls in summary[sc]:
                R2_grid[i, j] = summary[sc][cls]["r2"]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    im = ax.imshow(R2_grid, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(classes_present)))
    ax.set_xticklabels(classes_present, fontsize=10)
    ax.set_yticks(range(len(SCENARIO_NAMES)))
    ax.set_yticklabels(SCENARIO_NAMES, fontsize=10)
    for i in range(len(SCENARIO_NAMES)):
        for j in range(len(classes_present)):
            v = R2_grid[i, j]
            if np.isnan(v):
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=9, color="white")
            else:
                col = "white" if v < 0.5 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=9, color=col)
    ax.set_title("Skill$\\to$wealth $R^2$ by scenario and class")
    plt.colorbar(im, ax=ax, fraction=0.04, label="$R^2$")
    fig.tight_layout()
    fig.savefig(OUT / "elasticity_by_scenario.png", dpi=120)
    plt.close(fig)
    print(f"\nsaved {OUT / 'elasticity_by_scenario.png'}")


if __name__ == "__main__":
    main()
