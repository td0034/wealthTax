"""
Robustness checks for the growth paper.

R-A. Alpha sweep on CGDP weighting.
  CGDP = PT + alpha * EXT, where alpha reflects the share of extractive
  activity counted at face value by national accounts. The base case
  uses alpha = 0.20 (UK financial + real-estate share of GVA). We test
  alpha in {0.10, 0.15, 0.20, 0.25, 0.30, 0.40} from the existing
  portfolio data (no new runs needed since GMT_cum and PT_cum give
  EXT_cum = GMT_cum - PT_cum).

R-B. Capability composition.
  The base CI is survival * breadth * diversity (product form). We test
  four alternative compositions:
    P_product  product, the base case (normalised to status quo)
    P_geomean  geometric mean of survival, breadth, diversity (HDI flavour)
    P_addmean  arithmetic mean of survival, breadth, diversity
    P_mpi      Multi-dimensional Poverty Index flavour: penalise the worst
               of the three deprivations rather than the best gain
  All computed from terminal-tick survival, breadth, diversity.

Both checks operate on the existing growth_portfolio.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

DATA = Path("out/data")

ARMS_ORDER = ["A_status_quo", "C_zucman_2pct", "D_cap_5M",
              "E_hybrid_5pct", "F_hybrid_10pct"]
ARM_LABELS = {
    "A_status_quo":   "status quo",
    "C_zucman_2pct":  "Zucman 2%",
    "D_cap_5M":       "cap £5M",
    "E_hybrid_5pct":  "hybrid 5%",
    "F_hybrid_10pct": "hybrid 10%",
}
REGIME_ORDER = ["R0_baseline", "R1_heterodox",
                "R2_symmetric", "R3_orthodox"]
REGIME_LABELS = {
    "R0_baseline":   "no productivity channel",
    "R1_heterodox":  "heterodox (0.5, 0.1)",
    "R2_symmetric":  "symmetric (0.3, 0.3)",
    "R3_orthodox":   "orthodox (0.1, 0.5)",
}

ALPHAS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]


def alpha_sweep(summary: dict) -> dict:
    """Recompute CGDP at multiple alphas. Returns ratio vs status quo
    (within regime) for each (arm, regime, alpha) cell."""
    out = {}
    for regime in REGIME_ORDER:
        out[regime] = {}
        for alpha in ALPHAS:
            sq_key = f"A_status_quo__{regime}"
            sq_pt = summary[sq_key]["PT_cum"]
            sq_gmt = summary[sq_key]["GMT_cum"]
            sq_ext = sq_gmt - sq_pt
            sq_cgdp = sq_pt + alpha * sq_ext
            out[regime][f"alpha_{alpha}"] = {}
            for arm in ARMS_ORDER:
                key = f"{arm}__{regime}"
                pt = summary[key]["PT_cum"]
                gmt = summary[key]["GMT_cum"]
                ext = gmt - pt
                cgdp = pt + alpha * ext
                ratio = cgdp / max(sq_cgdp, 1e-12)
                out[regime][f"alpha_{alpha}"][arm] = ratio
    return out


def capability_composition(summary: dict) -> dict:
    """Recompute capability indices under four compositions.

    Needs per-arm terminal survival, cultural_breadth, cultural_diversity.
    The portfolio JSON has these via the per-tick window means; we use
    those as terminal-tick proxies (steady-state window mean).
    """
    out = {}
    SKILL_DIMS = 5     # for breadth normalisation

    for regime in REGIME_ORDER:
        sq_key = f"A_status_quo__{regime}"
        sq_s = summary[sq_key]
        # Components: survival in [0,1], breadth in [0,SKILL_DIMS],
        # diversity in [0, ~1].
        def comps(s):
            return (s["survival"], s["breadth_mean"] / SKILL_DIMS,
                     min(1.0, s["diversity_mean"]))

        ss, sb, sd = comps(sq_s)

        def make_composites(s):
            v, b, d = comps(s)
            # Avoid zeros for geometric mean.
            v_, b_, d_ = max(v, 1e-6), max(b, 1e-6), max(d, 1e-6)
            return {
                "product": v * b * d,
                "geomean": (v_ * b_ * d_) ** (1.0 / 3.0),
                "addmean": (v + b + d) / 3.0,
                # MPI flavour: 1 - mean(deprivation). Deprivation of each
                # dimension is 1 - normalised value. Lower is worse.
                "mpi":     1.0 - np.mean([1 - v, 1 - b, 1 - d]),
            }

        sq_comp = make_composites(sq_s)

        out[regime] = {}
        for arm in ARMS_ORDER:
            key = f"{arm}__{regime}"
            comp = make_composites(summary[key])
            ratios = {f"CI_{name}": comp[name] / max(sq_comp[name], 1e-9)
                      for name in comp}
            out[regime][arm] = ratios

    return out


def main():
    summary = json.loads((DATA / "growth_portfolio.json").read_text())

    print("=" * 80)
    print("R-A. ALPHA SWEEP on CGDP (ratio vs status quo, within regime)")
    print("=" * 80)
    alpha_data = alpha_sweep(summary)
    for regime in REGIME_ORDER:
        print(f"\nRegime: {REGIME_LABELS[regime]}")
        print(f"{'arm':<18} | " +
              " | ".join(f"a={a:.2f}" for a in ALPHAS))
        print("-" * (20 + 10 * len(ALPHAS)))
        for arm in ARMS_ORDER:
            row = []
            for a in ALPHAS:
                r = alpha_data[regime][f"alpha_{a}"][arm]
                if r >= 0.01:
                    row.append(f"{r:6.2f}x")
                else:
                    row.append(f"{r:6.1e}")
            print(f"{arm:<18} | " + " | ".join(row))

    print()
    print("=" * 80)
    print("R-B. CAPABILITY COMPOSITION (ratio vs status quo, within regime)")
    print("=" * 80)
    cap_data = capability_composition(summary)
    for regime in REGIME_ORDER:
        print(f"\nRegime: {REGIME_LABELS[regime]}")
        print(f"{'arm':<18} | {'product':>9} {'geomean':>9} "
              f"{'addmean':>9} {'mpi':>9}")
        print("-" * 65)
        for arm in ARMS_ORDER:
            r = cap_data[regime][arm]
            print(f"{arm:<18} | "
                  f"{r['CI_product']:>8.2f}x {r['CI_geomean']:>8.2f}x "
                  f"{r['CI_addmean']:>8.2f}x {r['CI_mpi']:>8.2f}x")

    out_path = DATA / "growth_robustness.json"
    out_path.write_text(json.dumps(
        {"alpha_sweep": alpha_data,
         "capability_composition": cap_data}, indent=2))
    print(f"\nsaved {out_path}")

    # Summary print: under what alpha does the wealth-tax case stop winning?
    print()
    print("== Where does alpha put the wealth-tax case 'over' status quo? ==")
    print("(CGDP ratio of E_hybrid_5pct vs status quo crossing 1.0)")
    for regime in REGIME_ORDER:
        for a in ALPHAS:
            r = alpha_data[regime][f"alpha_{a}"]["E_hybrid_5pct"]
            if r >= 1.0:
                print(f"  {regime}: crosses 1.0 at alpha <= {a:.2f}")
                break
        else:
            print(f"  {regime}: never crosses 1.0 in tested range")


if __name__ == "__main__":
    main()
