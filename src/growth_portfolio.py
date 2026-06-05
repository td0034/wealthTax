"""
Growth portfolio: six measures across five policy arms across four
productivity regimes.

Measures (computed from steady-state window ticks 80-180):

  1. Gross monetary throughput (GMT)
     Sum of (productive + extractive flow). Includes the rentier-lender
     deposit loop at face value. Closest analogue to a naive
     transactional-volume aggregate.

  2. Productive throughput (PT)
     Sum of productive_flow only. Mazzucato value-creation measure.

  3. Calibrated GDP proxy (CGDP)
     PT + alpha * extractive_flow.  alpha = 0.20 reflects UK financial-
     services + real-estate share of national-accounts value added.
     The empirically-anchored GDP analogue.

  4. Capability index (CI)
     Terminal-tick survival_rate * cultural_breadth * cultural_diversity.
     Sen-Nussbaum capability flavour.

  5. Median consumption proxy (MC)
     Median worker net worth at terminal tick (in £). Direct welfare
     proxy at the median.

  6. Knowledge stock (KS)
     Sum of skill_total across living non-state agents at terminal tick.
     Human-capital stock.

Policy arms:
  A status_quo               no cap, no WT, no spending
  C zucman_2pct              spending + WT 2% > £10M
  D cap_5M                   spending + cap £5M
  E hybrid_5pct              spending + WT 5% > £10M
  F hybrid_10pct             spending + WT 10% > £10M

Productivity regimes (skill_coeff, capital_coeff):
  R0 baseline_stationary     (0.0, 0.0)   no productivity dynamics
  R1 heterodox_dominant      (0.5, 0.1)   skill channel dominant
  R2 symmetric_balanced      (0.3, 0.3)   Hanushek-Solow balanced
  R3 orthodox_dominant       (0.1, 0.5)   capital channel dominant
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
ALPHA_GDP = 0.20

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
    "A_status_quo":    {**NO_SPEND},
    "C_zucman_2pct":   {**SPEND, "wealth_tax_tiers": ((100.0, 0.02),)},
    "D_cap_5M":        {**SPEND, "inheritance_cap": 50.0},
    "E_hybrid_5pct":   {**SPEND, "wealth_tax_tiers": ((100.0, 0.05),)},
    "F_hybrid_10pct":  {**SPEND, "wealth_tax_tiers": ((100.0, 0.10),)},
}

REGIMES = {
    "R0_baseline":           (0.0, 0.0),
    "R1_heterodox":          (0.5, 0.1),
    "R2_symmetric":          (0.3, 0.3),
    "R3_orthodox":           (0.1, 0.5),
}


def _run(args):
    arm, regime, seed = args
    skill_c, capital_c = REGIMES[regime]
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[arm])
    overrides["skill_productivity_coeff"] = skill_c
    overrides["capital_productivity_coeff"] = capital_c

    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    history = []
    for t in range(TICKS):
        h = step(agents, d, rng, t, accum)
        if t >= WINDOW_START:
            history.append({
                "metabolic": h["metabolic_rate"],
                "productive": h["productive_flow"],
                "extractive": h["extractive_flow"],
                "phi": h["autocatalytic_closure"],
                "breadth": h["cultural_breadth"],
                "diversity": h["cultural_diversity"],
                "alive": h["alive"],
                "human_capital": h["human_capital_boost"],
                "capital_deep": h["capital_deepening_boost"],
            })

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    workers = [a for a in living if a.type == Type.WORKER]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    total_skill_mass = float(sum(a.skill_total for a in living))
    knowledge_lost_cum = accum.get("knowledge_lost_cum", 0.0)
    state_agent = next((a for a in agents
                        if a.type == Type.STATE and a.alive), None)

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))
    top10 = float(np.sort(nws)[::-1][: max(1, n // 10)].sum() / max(total_w, 1e-9))
    median_worker_gbp = (
        float(np.median([max(0.0, a.net_worth) for a in workers]) * WEALTH_UNIT_GBP)
        if workers else 0.0
    )
    survival = len(living) / max(initial_nonstate, 1)

    # Six measures.
    prod_arr = np.array([h["productive"] for h in history])
    extr_arr = np.array([h["extractive"] for h in history])
    breadth_arr = np.array([h["breadth"] for h in history])
    diversity_arr = np.array([h["diversity"] for h in history])
    alive_arr = np.array([h["alive"] for h in history])

    gmt_cum = float((prod_arr + extr_arr).sum())
    pt_cum = float(prod_arr.sum())
    cgdp_cum = float(prod_arr.sum() + ALPHA_GDP * extr_arr.sum())
    init_alive = SCALE * 99
    ci_terminal = survival * history[-1]["breadth"] * history[-1]["diversity"]
    mc_terminal_gbp = median_worker_gbp
    ks_terminal = total_skill_mass

    def growth_rate(series: np.ndarray) -> float:
        if len(series) < 40 or series[:20].mean() <= 0:
            return 0.0
        early = float(series[:20].mean())
        late = float(series[-20:].mean())
        if early <= 0 or late <= 0:
            return 0.0
        n_ticks = len(series) - 20
        return ((late / early) ** (1.0 / n_ticks)) - 1.0

    gmt_growth = growth_rate(prod_arr + extr_arr)
    pt_growth = growth_rate(prod_arr)
    cgdp_growth = growth_rate(prod_arr + ALPHA_GDP * extr_arr)
    ci_series = np.array([alive_arr[i] / max(init_alive, 1)
                           * breadth_arr[i] * diversity_arr[i]
                           for i in range(len(history))])
    ci_growth = growth_rate(ci_series)

    return arm, regime, seed, {
        # Six headline measures
        "GMT_cum": gmt_cum,
        "PT_cum": pt_cum,
        "CGDP_cum": cgdp_cum,
        "CI_terminal": float(ci_terminal),
        "MC_median_worker_gbp": mc_terminal_gbp,
        "KS_total_skill_mass": ks_terminal,
        # Per-tick growth rates over the window
        "GMT_growth": gmt_growth,
        "PT_growth": pt_growth,
        "CGDP_growth": cgdp_growth,
        "CI_growth": ci_growth,
        # Compositional context
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "billionaires": int((gbp >= 1e9).sum()),
        "survival": survival,
        "phi_mean": float(np.array([h["phi"] for h in history]).mean()),
        "breadth_mean": float(breadth_arr.mean()),
        "diversity_mean": float(diversity_arr.mean()),
        "knowledge_lost_cum": float(knowledge_lost_cum),
        "human_capital_boost_mean": float(
            np.array([h["human_capital"] for h in history]).mean()),
        "capital_deep_boost_mean": float(
            np.array([h["capital_deep"] for h in history]).mean()),
        "state_wealth_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                              if state_agent else 0.0),
    }


def main():
    args = [(a, r, s) for a in ARMS for r in REGIMES for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s\n")

    # Aggregate.
    by_key: dict = {}
    for arm, regime, _, m in results:
        by_key.setdefault((arm, regime), []).append(m)

    summary: dict = {}
    for (arm, regime), ms in by_key.items():
        keys = ms[0].keys()
        summary[f"{arm}__{regime}"] = {
            k: float(np.mean([m[k] for m in ms])) for k in keys
        }

    # Print regime-by-regime headline tables.
    for regime in REGIMES:
        print(f"\n== Regime {regime} (skill={REGIMES[regime][0]}, "
              f"capital={REGIMES[regime][1]}) ==")
        sq_key = f"A_status_quo__{regime}"
        sq = summary[sq_key]
        print(f"{'arm':<18} | {'GMT':>9} {'PT':>9} {'CGDP':>9} {'CI':>9} "
              f"{'MC £k':>9} {'KS':>9} | {'bot-50':>7} {'phi':>5}")
        print("-" * 110)
        for arm in ARMS:
            key = f"{arm}__{regime}"
            s = summary[key]
            gmt_r = s["GMT_cum"] / max(sq["GMT_cum"], 1e-9)
            pt_r = s["PT_cum"] / max(sq["PT_cum"], 1e-9)
            cgdp_r = s["CGDP_cum"] / max(sq["CGDP_cum"], 1e-9)
            ci_r = s["CI_terminal"] / max(sq["CI_terminal"], 1e-9)
            mc_k = s["MC_median_worker_gbp"] / 1000
            ks_r = s["KS_total_skill_mass"] / max(sq["KS_total_skill_mass"], 1e-9)
            print(f"{arm:<18} | "
                  f"{gmt_r:>8.2f}x {pt_r:>8.2f}x {cgdp_r:>8.2f}x {ci_r:>8.2f}x "
                  f"{mc_k:>8.1f}k {ks_r:>8.2f}x | "
                  f"{s['bottom_50_share']*100:>6.1f}% {s['phi_mean']:>5.3f}")

    print(f"\n== Productivity-growth rates (per-tick %) ==")
    print(f"{'arm':<18} | {'regime':<14} | "
          f"{'PT %':>6} {'CGDP %':>7} {'CI %':>6}")
    print("-" * 70)
    for arm in ARMS:
        for regime in REGIMES:
            key = f"{arm}__{regime}"
            s = summary[key]
            print(f"{arm:<18} | {regime:<14} | "
                  f"{s['PT_growth']*100:>5.2f}% "
                  f"{s['CGDP_growth']*100:>6.2f}% "
                  f"{s['CI_growth']*100:>5.2f}%")

    out_path = OUT_DATA / "growth_portfolio.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
