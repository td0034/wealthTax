"""
Round 2 R2-3: Capital-flight channel.

Hunt's critique: the 2024 non-dom reform produced UHNW emigration that
surprised the Treasury. CEBR estimates several billion in lost revenue
per year. The cap is the most flight-sensitive policy on the table and
the paper's wave-of-the-hand exit-tax response is what the Treasury
also said in 2022.

Implementation:

  Each tick, for each non-state living agent whose wealth exceeds the
  flight threshold, sample a flight event. The flight probability is
  proportional to the agent's wealth above the cap threshold, scaled
  by a base annual rate.

  Calibration anchor: Young et al. (2016) find millionaire migration
  responses of order 0.1-0.4 percentage points per percentage point of
  effective tax. The cap is structurally more aggressive than a tax
  rate, so we use a higher base rate.

      flight_rate_per_tick(w, cap) =
          base_rate * max(0, (w - cap)) / cap

  base_rate is swept across 0.005, 0.01, 0.02, 0.05 (annual probability
  per cap-multiple above the cap).

  A flying agent's wealth leaves the simulation entirely (no state
  capture, no redistribution). This is the worst case for the cap
  arm: maximally pessimistic on flight, no capture by exit tax.

Re-run the five-arm decomposition under each flight rate.
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
SEEDS = 4

CAP_UNITS = 50.0    # £5M cap = 50 model units

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
    "B_spend_only":    {**SPEND},
    "C_iht40_spend":   {**SPEND, "inheritance_tax_rate": 0.40},
    "D_cap_spend":     {**SPEND, "inheritance_cap": CAP_UNITS},
    "E_cap_iht_spend": {**SPEND, "inheritance_cap": CAP_UNITS,
                         "inheritance_tax_rate": 0.40},
}

FLIGHT_RATES = [0.0, 0.005, 0.01, 0.02, 0.05]
ARMS_WITH_CAP = {"D_cap_spend", "E_cap_iht_spend"}


def _apply_flight(agents, rng, base_rate: float, cap: float):
    """Stochastically remove wealth from agents with wealth > cap.

    Returns (flown_count, flown_wealth_units).
    """
    flown_count = 0
    flown_wealth = 0.0
    for a in agents:
        if not a.alive or a.type == Type.STATE:
            continue
        if a.wealth <= cap:
            continue
        excess_ratio = (a.wealth - cap) / cap
        p = min(base_rate * excess_ratio, 0.5)   # cap per-tick at 50%
        if rng.random() < p:
            flown_wealth += a.wealth
            a.wealth = 0.0
            a.alive = False
            a.died_at = -1     # sentinel: emigrated, not died
            a.death_cause = "flight"
            flown_count += 1
    return flown_count, flown_wealth


def _run(args):
    name, seed, flight_rate = args
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[name])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    flight_active = name in ARMS_WITH_CAP and flight_rate > 0
    total_flown_count = 0
    total_flown_wealth = 0.0

    for t in range(TICKS):
        step(agents, d, rng, t, accum)
        if flight_active:
            fc, fw = _apply_flight(agents, rng, flight_rate, CAP_UNITS)
            total_flown_count += fc
            total_flown_wealth += fw

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))
    top10 = float(np.sort(nws)[::-1][: max(1, n // 10)].sum() / max(total_w, 1e-9))
    top1 = float(np.sort(nws)[::-1][: max(1, n // 100)].sum() / max(total_w, 1e-9))

    return name, seed, flight_rate, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "top_1_share": top1,
        "flown_count": total_flown_count,
        "flown_wealth_gbp": total_flown_wealth * WEALTH_UNIT_GBP,
    }


def main():
    args = [(n, s, fr)
            for n in ARMS
            for s in range(SEEDS)
            for fr in FLIGHT_RATES]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_arm_rate: dict[tuple[str, float], list[dict]] = {}
    for name, _, fr, m in results:
        by_arm_rate.setdefault((name, fr), []).append(m)

    summary: dict[str, dict] = {}
    for (name, fr), ms in by_arm_rate.items():
        keys = ms[0].keys()
        key = f"{name}__flight{fr}"
        summary[key] = {k: float(np.mean([m[k] for m in ms])) for k in keys}

    print()
    print(f"{'arm':<20} {'flight':>7}  {'alive':>7} "
          f"{'bn':>5} {'bot-50':>8} {'top-10':>8} "
          f"{'flown':>7} {'flown £T':>10}")
    for arm in ARMS:
        for fr in FLIGHT_RATES:
            key = f"{arm}__flight{fr}"
            s = summary[key]
            print(f"{arm:<20} {fr:>7.3f}  "
                  f"{s['alive_rate']*100:>6.1f}% "
                  f"{s['billionaires']:>5.0f} "
                  f"{s['bottom_50_share']*100:>7.1f}% "
                  f"{s['top_10_share']*100:>7.1f}% "
                  f"{s['flown_count']:>7.0f} "
                  f"{s['flown_wealth_gbp']/1e12:>9.1f}T")

    out_path = OUT_DATA / "round2_flight.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
