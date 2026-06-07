"""
Bootstrap CIs for the headline six-measure portfolio.

Inputs: growth_seeds20.json (per-seed results, 20 seeds per arm).
Outputs:
  - growth_cis.json with mean, std, 95% percentile bootstrap CI for
    each (arm, measure)
  - terminal table to stdout

The percentile bootstrap resamples seeds with replacement B times,
computes the statistic, and takes the 2.5/97.5 percentiles of the
resampled distribution. With 20 seeds and B=2000 we have stable CIs.

For each measure we also report the ratio-vs-status-quo CI by
resampling the ratio (status-quo seed and policy-arm seed are
independent draws so the bootstrap is the ratio of two means each
resampled).
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

MEASURES = [
    ("PT_cum",      "PT (productive)"),
    ("CGDP_cum",    "CGDP (orthodox)"),
    ("CI_terminal", "CI (capability)"),
    ("KS_total_skill", "KS (knowledge)"),
    ("bottom_50_share", "bot-50%"),
    ("survival",    "survival"),
    ("phi_mean",    "phi"),
]

B = 2000   # bootstrap resamples
RNG = np.random.default_rng(123)


def percentile_ci(values: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    lo = np.percentile(values, 100 * alpha / 2)
    hi = np.percentile(values, 100 * (1 - alpha / 2))
    return float(lo), float(hi)


def ratio_bootstrap(numerator: np.ndarray, denominator: np.ndarray,
                     B: int = 2000, alpha: float = 0.05) -> dict:
    """Bootstrap CI on the ratio of means."""
    n = len(numerator)
    m = len(denominator)
    ratios = np.empty(B)
    for b in range(B):
        idx_n = RNG.integers(0, n, n)
        idx_d = RNG.integers(0, m, m)
        num_mean = numerator[idx_n].mean()
        den_mean = denominator[idx_d].mean()
        ratios[b] = num_mean / max(den_mean, 1e-12)
    lo, hi = percentile_ci(ratios, alpha)
    return {"mean_ratio": float(ratios.mean()),
            "ci_lo": lo, "ci_hi": hi}


def main():
    raw = json.loads((DATA / "growth_seeds20.json").read_text())

    summary: dict = {}
    for arm in ARMS_ORDER:
        summary[arm] = {}
        for mkey, _ in MEASURES:
            vals = np.array([raw[arm][s][mkey]
                              for s in raw[arm].keys()])
            mu = float(vals.mean())
            sd = float(vals.std(ddof=1))
            # Bootstrap CI on the mean.
            boots = np.empty(B)
            for b in range(B):
                idx = RNG.integers(0, len(vals), len(vals))
                boots[b] = vals[idx].mean()
            lo, hi = percentile_ci(boots)
            summary[arm][mkey] = {
                "mean": mu, "sd": sd,
                "ci_lo": lo, "ci_hi": hi,
                "n_seeds": int(len(vals)),
            }

    # Ratio CIs vs status quo for each policy arm.
    ratio_cis: dict = {}
    sq = raw["A_status_quo"]
    for arm in ARMS_ORDER:
        if arm == "A_status_quo":
            continue
        ratio_cis[arm] = {}
        for mkey, _ in MEASURES:
            num = np.array([raw[arm][s][mkey] for s in raw[arm].keys()])
            den = np.array([sq[s][mkey] for s in sq.keys()])
            ratio_cis[arm][mkey] = ratio_bootstrap(num, den)

    print("=" * 90)
    print("Headline measures with 95% bootstrap CI (20 seeds, B=2000)")
    print("=" * 90)
    for mkey, label in MEASURES:
        print(f"\n{label}")
        print(f"{'arm':<18} | {'mean':>14} | {'95% CI':>32}")
        print("-" * 75)
        for arm in ARMS_ORDER:
            s = summary[arm][mkey]
            print(f"{arm:<18} | {s['mean']:>14,.3f} | "
                  f"[{s['ci_lo']:>12,.3f}, {s['ci_hi']:>14,.3f}]")

    print()
    print("=" * 90)
    print("Ratio vs status quo, 95% bootstrap CI")
    print("=" * 90)
    for mkey, label in MEASURES:
        print(f"\n{label} (vs status quo)")
        print(f"{'arm':<18} | {'mean ratio':>12} | {'95% CI':>26}")
        print("-" * 65)
        for arm in ARMS_ORDER:
            if arm == "A_status_quo":
                continue
            rc = ratio_cis[arm][mkey]
            print(f"{arm:<18} | {rc['mean_ratio']:>11.4f}x | "
                  f"[{rc['ci_lo']:>9.4f}, {rc['ci_hi']:>11.4f}]")

    out = {"summary": summary, "ratio_cis": ratio_cis}
    out_path = DATA / "growth_cis.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
