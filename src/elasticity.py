"""
Skill -> wealth elasticity (AL-3).

Quantifies how strongly skills feed wealth. Runs a baseline simulation,
snapshots per-agent (skills, wealth) at tick 50 and tick 200, computes
wealth gain over the window, and regresses on skill vector by class.

A weak elasticity supports the ALIFE reviewer's worry that the
cultural/economic asymmetry is structurally built in. A strong
elasticity makes it more genuinely emergent.

Usage: python3 elasticity.py
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import (Dials, Type, SKILL_NAMES, SKILL_DIMS,
                 make_initial_population, step)

OUT = Path("out/figures/scenarios")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)


SCENARIO = Dials(population_scale=5)  # default; main()/main_multi() override
WARMUP = 20                            # discard transient
WINDOW = 40                            # measure gain over this many ticks (<< median lifespan)
SEEDS = 8


def run_once(seed: int):
    d = replace(SCENARIO, seed=seed)
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
                "alive_end": int(a.alive),
            })
    return rows


def main():
    all_rows = []
    for s in range(SEEDS):
        all_rows.extend(run_once(s))
    print(f"collected {len(all_rows)} agent-windows across {SEEDS} seeds")

    by_class: dict[str, list] = {}
    for r in all_rows:
        by_class.setdefault(r["type"], []).append(r)

    summary = {}
    for cls, rows in sorted(by_class.items()):
        X = np.stack([r["skills"] for r in rows])
        y = np.array([r["gain"] for r in rows])
        if len(rows) < SKILL_DIMS + 5:
            continue
        # Regression: gain ~ skills
        X1 = np.column_stack([np.ones(len(rows)), X])
        coefs, *_ = np.linalg.lstsq(X1, y, rcond=None)
        residuals = y - X1 @ coefs
        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        std_y = float(np.std(y))
        summary[cls] = {
            "n": len(rows),
            "mean_gain": float(np.mean(y)),
            "std_gain": std_y,
            "intercept": float(coefs[0]),
            "coefs": {SKILL_NAMES[i]: float(coefs[i + 1])
                      for i in range(SKILL_DIMS)},
            "r2": float(r2),
            # Elasticity = (coef) * std(skill) / mean(|gain|) when mean(y) > 0
            "elasticities": {
                SKILL_NAMES[i]: float(
                    coefs[i + 1] * np.std(X[:, i]) / (abs(np.mean(y)) + 1e-9))
                for i in range(SKILL_DIMS)
            },
        }

    # Table.
    print()
    header = f"{'class':<12}" + "  " + "  ".join(f"{n[:6]:>7}" for n in SKILL_NAMES) + f"  {'R^2':>5}  {'n':>4}"
    print(header)
    for cls, s in summary.items():
        coefs_row = "  ".join(f"{s['coefs'][n]:>7.3f}" for n in SKILL_NAMES)
        print(f"{cls:<12}  {coefs_row}  {s['r2']:>5.2f}  {s['n']:>4}")
    print("\nNormalised elasticities (coef * std(skill) / |mean(gain)|):")
    print(header)
    for cls, s in summary.items():
        e = "  ".join(f"{s['elasticities'][n]:>7.3f}" for n in SKILL_NAMES)
        print(f"{cls:<12}  {e}  {'':>5}  {s['n']:>4}")

    # Bar chart: per-class elasticity sum across skills.
    classes = list(summary.keys())
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    bx = np.arange(SKILL_DIMS)
    width = 0.8 / len(classes)
    for i, cls in enumerate(classes):
        vals = [summary[cls]["coefs"][n] for n in SKILL_NAMES]
        axes[0].bar(bx + (i - len(classes) / 2) * width, vals, width,
                    label=cls)
    axes[0].set_xticks(bx); axes[0].set_xticklabels(SKILL_NAMES, fontsize=9)
    axes[0].set_ylabel("OLS coefficient (wealth gain per skill unit)")
    axes[0].set_title("Skill -> wealth coefficients by class")
    axes[0].grid(alpha=0.25, axis="y")
    axes[0].legend(fontsize=8)

    for i, cls in enumerate(classes):
        vals = [summary[cls]["elasticities"][n] for n in SKILL_NAMES]
        axes[1].bar(bx + (i - len(classes) / 2) * width, vals, width,
                    label=cls)
    axes[1].set_xticks(bx); axes[1].set_xticklabels(SKILL_NAMES, fontsize=9)
    axes[1].set_ylabel("Normalised elasticity")
    axes[1].set_title("Skill -> wealth normalised elasticity by class")
    axes[1].grid(alpha=0.25, axis="y")
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "skill_wealth_elasticity.png", dpi=120)
    plt.close(fig)

    import json
    with open(OUT_DATA / "skill_wealth_elasticity.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nsaved {OUT / 'skill_wealth_elasticity.png'}")
    print(f"saved {OUT_DATA / 'skill_wealth_elasticity.json'}")


if __name__ == "__main__":
    main()
