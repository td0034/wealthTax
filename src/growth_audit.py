"""
Growth audit: compute four alternative measures of growth across the
existing policy arms to test the GDP-vs-alternative-measures hypothesis
before committing to a model extension.

Four measures:

  1. Gross monetary throughput (GMT)
     Sum of metabolic_rate per tick over the steady-state window.
     This is the maximally extractive-inclusive measure: counts every
     monetary flow at face value, including the rentier-lender deposit
     loop that drives the status quo. Closest analogue to a naive
     "transaction value added" GDP variant.

  2. Productive throughput (PT)
     Sum of Phi-weighted metabolic_rate per tick. Phi is the share of
     monetary flow accruing to productive-class agents (worker, maker,
     employer). Mazzucato-style: counts only productive activity as
     economic value.

  3. Calibrated GDP proxy (CGDP)
     Productive throughput plus alpha times extractive throughput,
     where alpha = 0.20 reflects the UK financial-services + real-
     estate share of GDP. This is the empirically grounded GDP
     analogue: extractive activity contributes to GDP at the rate
     national accounts assign to financial intermediation and rents,
     not at face value.

  4. Capability index (CI)
     Survival rate * cultural_breadth * cultural_diversity, at the
     terminal tick. Sen-Nussbaum capability flavour: what the
     population can actually do, weighted by what fraction of the
     population is alive to do it.

Policy arms (joint-calibrated UK baseline):

  A status_quo  no cap, no WT, no IHT, no spending package
  B status_quo_with_spending  spending package on
  C zucman_2pct  state-spending + WT 2% > GBP 10M
  D cap_5M  state-spending + cap GBP 5M
  E hybrid_5pct  state-spending + WT 5% > GBP 10M
  F hybrid_10pct  state-spending + WT 10% > GBP 10M

Reports per arm: (1) the four growth measures, (2) cumulative
production, (3) distribution metrics for context, (4) per-tick growth
rate over the steady-state window for each measure.
"""
from __future__ import annotations

import json
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, Type, WEALTH_UNIT_GBP, make_initial_population, step

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)

SCALE = 100
TICKS = 180
WINDOW_START = 80
SEEDS = 4
ALPHA_GDP = 0.20      # UK financial + real-estate share of value added

CALIBRATED = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    interest_rate=0.06,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    wealth_tax_tiers=(),
)

SPEND = dict(
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)

NO_SPEND = dict(
    ubi=0.0,
    state_employs_fraction=0.0,
    state_employs_wage=1.0,
    state_buys_maker_output=0.0,
)

ARMS = {
    "A_status_quo":      {**NO_SPEND},
    "B_spend_only":      {**SPEND},
    "C_zucman_2pct":     {**SPEND, "wealth_tax_tiers": ((100.0, 0.02),)},
    "D_cap_5M":          {**SPEND, "inheritance_cap": 50.0},
    "E_hybrid_5pct":     {**SPEND, "wealth_tax_tiers": ((100.0, 0.05),)},
    "F_hybrid_10pct":    {**SPEND, "wealth_tax_tiers": ((100.0, 0.10),)},
}


def _run(args):
    name, seed = args
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[name])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    history = []
    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        history.append({
            "tick": t,
            "metabolic_rate": h["metabolic_rate"],
            "productive_flow": h["productive_flow"],
            "extractive_flow": h["extractive_flow"],
            "autocatalytic_closure": h["autocatalytic_closure"],
            "alive": h["alive"],
            "cultural_diversity": h["cultural_diversity"],
            "cultural_breadth": h["cultural_breadth"],
        })

    # Terminal-state agent inventory.
    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    living_workers = [a for a in living if a.type == Type.WORKER]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    state_agent = next((a for a in agents
                        if a.type == Type.STATE and a.alive), None)

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))
    median_worker_wealth_gbp = (
        float(np.median([a.net_worth for a in living_workers]) * WEALTH_UNIT_GBP)
        if living_workers else 0.0
    )

    return name, seed, history, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "bottom_50_share": bot50,
        "median_worker_wealth_gbp": median_worker_wealth_gbp,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
        "total_household_wealth_gbp": float(total_w) * WEALTH_UNIT_GBP,
    }


def _measures(history: list[dict], terminal: dict) -> dict:
    """Compute the four growth measures from a single-run history."""
    h_window = history[WINDOW_START:]
    h_early = history[WINDOW_START:WINDOW_START + 20]
    h_late = history[-20:]

    metabolic = np.array([h["metabolic_rate"] for h in h_window])
    prod = np.array([h["productive_flow"] for h in h_window])
    extract = np.array([h["extractive_flow"] for h in h_window])
    phi = np.array([h["autocatalytic_closure"] for h in h_window])
    breadth = np.array([h["cultural_breadth"] for h in h_window])
    diversity = np.array([h["cultural_diversity"] for h in h_window])
    alive = np.array([h["alive"] for h in h_window])

    # Cumulative measures over the steady-state window.
    gmt = float(metabolic.sum())
    pt = float(prod.sum())
    cgdp = float(prod.sum() + ALPHA_GDP * extract.sum())

    # Terminal capability (composite Sen-flavoured).
    last = history[-1]
    init_alive = SCALE * 99   # initial non-state agent count
    final_survival = last["alive"] / max(init_alive, 1)
    ci = final_survival * last["cultural_breadth"] * last["cultural_diversity"]

    # Per-tick growth rate over the steady-state window for each.
    def _growth(series: np.ndarray) -> float:
        if len(series) < 40:
            return 0.0
        early = series[:20].mean()
        late = series[-20:].mean()
        if early <= 0:
            return 0.0
        n_ticks = len(series) - 20
        return float(((late / early) ** (1.0 / n_ticks)) - 1.0)

    gmt_growth = _growth(metabolic)
    pt_growth = _growth(prod)
    cgdp_growth = _growth(prod + ALPHA_GDP * extract)
    ci_series = np.array(
        [h["alive"] / max(init_alive, 1)
            * h["cultural_breadth"] * h["cultural_diversity"]
         for h in h_window]
    )
    ci_growth = _growth(ci_series)

    return {
        # Levels (cumulative over steady-state window, model units)
        "gmt_cum": gmt,
        "pt_cum": pt,
        "cgdp_cum": cgdp,
        "ci_terminal": float(ci),
        # Per-tick growth rates (steady state)
        "gmt_growth": gmt_growth,
        "pt_growth": pt_growth,
        "cgdp_growth": cgdp_growth,
        "ci_growth": ci_growth,
        # Steady-state composition
        "phi_mean": float(phi.mean()),
        "breadth_mean": float(breadth.mean()),
        "diversity_mean": float(diversity.mean()),
        "survival_terminal": float(final_survival),
    }


def main():
    args = [(n, s) for n in ARMS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s\n")

    by_arm: dict[str, dict] = {}
    for name, _, history, terminal in results:
        by_arm.setdefault(name, []).append((history, terminal))

    summary: dict[str, dict] = {}
    for name, runs in by_arm.items():
        measures = [_measures(h, t) for h, t in runs]
        terminals = [t for _, t in runs]
        agg = {}
        for k in measures[0]:
            agg[k] = float(np.mean([m[k] for m in measures]))
        for k in terminals[0]:
            agg[k] = float(np.mean([t[k] for t in terminals]))
        summary[name] = agg

    # Normalise everything to status quo for the headline view.
    sq = summary["A_status_quo"]

    print(f"{'arm':<18} | {'GMT':>9} {'PT':>9} {'CGDP':>9} {'CI':>9} |"
          f" {'bot-50%':>8} {'survival':>8} {'phi':>6} {'breadth':>7}")
    print("-" * 110)
    for name in ARMS:
        s = summary[name]
        gmt_r = s["gmt_cum"] / max(sq["gmt_cum"], 1e-9)
        pt_r = s["pt_cum"] / max(sq["pt_cum"], 1e-9)
        cgdp_r = s["cgdp_cum"] / max(sq["cgdp_cum"], 1e-9)
        ci_r = s["ci_terminal"] / max(sq["ci_terminal"], 1e-9)
        print(f"{name:<18} | "
              f"{gmt_r:>8.2f}x {pt_r:>8.2f}x {cgdp_r:>8.2f}x {ci_r:>8.2f}x | "
              f"{s['bottom_50_share']*100:>7.1f}% "
              f"{s['survival_terminal']*100:>7.1f}% "
              f"{s['phi_mean']:>6.3f} "
              f"{s['breadth_mean']:>7.2f}")

    print()
    print("Levels (cumulative steady-state, model units):")
    print(f"{'arm':<18} | {'GMT':>14} {'PT':>14} {'CGDP':>14} {'CI':>9}")
    print("-" * 80)
    for name in ARMS:
        s = summary[name]
        print(f"{name:<18} | "
              f"{s['gmt_cum']:>14,.0f} {s['pt_cum']:>14,.0f} "
              f"{s['cgdp_cum']:>14,.0f} {s['ci_terminal']:>9.3f}")

    print()
    print("Per-tick growth rates over steady-state window (annualised %):")
    print(f"{'arm':<18} | {'GMT':>8} {'PT':>8} {'CGDP':>8} {'CI':>8}")
    print("-" * 60)
    for name in ARMS:
        s = summary[name]
        print(f"{name:<18} | "
              f"{s['gmt_growth']*100:>7.2f}% "
              f"{s['pt_growth']*100:>7.2f}% "
              f"{s['cgdp_growth']*100:>7.2f}% "
              f"{s['ci_growth']*100:>7.2f}%")

    out_path = OUT_DATA / "growth_audit.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
