"""
Round 2 R2-11: Hybrid wealth tax loose-end experiments.

Four sub-experiments to harden the hybrid finding:

  A. Flight under hybrid. Capital flight elasticities applied to the
     hybrid WT 10% > £10M, sweep base rates from 0 to 0.05.
  B. Transition ramp. Phase the rate from 2% to 10% over a 50-tick
     transition window; compare distributional outcome to instant
     deployment.
  C. Class-conditional hybrid. WT 10% > £10M applied only to extractive
     classes (RENTIER, LENDER, SPECULATOR), exempting productive.
  D. Stacked. Hybrid plus £5M cap simultaneously; isolate marginal
     contribution of each.

All compared against the baseline (status quo), the £5M cap, and the
flat hybrid WT 10% > £10M as references.
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
CAP_UNITS = 50.0
T10M = 100.0
HYBRID_RATE = 0.10

CALIBRATED = dict(
    capital_return=0.08,
    rent_share_of_wage=0.20,
    subsistence=0.30,
    interest_rate=0.06,
    inheritance_tax_rate=0.0,
    inheritance_cap=float("inf"),
    wealth_tax_tiers=(),
    ubi=0.4,
    state_employs_fraction=0.3,
    state_employs_wage=0.8,
    state_buys_maker_output=5.0,
)

EXTRACTIVE = {Type.RENTIER, Type.LENDER, Type.SPECULATOR}

# --------------------------------------------------------------------
# Sub-experiment A: flight under hybrid
# --------------------------------------------------------------------

def _apply_flight(agents, rng, base_rate: float, threshold: float):
    flown_count = 0
    flown_wealth = 0.0
    for a in agents:
        if not a.alive or a.type == Type.STATE:
            continue
        if a.wealth <= threshold:
            continue
        excess_ratio = (a.wealth - threshold) / threshold
        p = min(base_rate * excess_ratio, 0.5)
        if rng.random() < p:
            flown_wealth += a.wealth
            a.wealth = 0.0
            a.alive = False
            a.died_at = -1
            a.death_cause = "flight"
            flown_count += 1
    return flown_count, flown_wealth


def _run_A(args):
    flight_rate, seed = args
    overrides = dict(CALIBRATED)
    overrides["wealth_tax_tiers"] = ((T10M, HYBRID_RATE),)
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    flown_count = 0
    flown_wealth = 0.0
    for t in range(TICKS):
        step(agents, d, rng, t, accum)
        if flight_rate > 0:
            fc, fw = _apply_flight(agents, rng, flight_rate, T10M)
            flown_count += fc
            flown_wealth += fw

    return ("A", flight_rate, seed,
            _metrics(agents, initial_nonstate, flown_count, flown_wealth))


def _metrics(agents, initial_nonstate, flown_count=0, flown_wealth=0.0):
    living = [a for a in agents
              if a.alive and a.type != Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    gbp = nws * WEALTH_UNIT_GBP
    state_agent = next((a for a in agents
                        if a.type == Type.STATE and a.alive), None)

    total_w = nws.sum() if len(nws) else 1.0
    n = len(nws)
    bot50 = float(np.sort(nws)[: n // 2].sum() / max(total_w, 1e-9))
    top10 = float(np.sort(nws)[::-1][: max(1, n // 10)].sum() / max(total_w, 1e-9))
    top1 = float(np.sort(nws)[::-1][: max(1, n // 100)].sum() / max(total_w, 1e-9))

    return {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centimillionaires": int((gbp >= 1e8).sum()),
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "top_1_share": top1,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
        "flown_count": flown_count,
        "flown_wealth_gbp": flown_wealth * WEALTH_UNIT_GBP,
    }


# --------------------------------------------------------------------
# Sub-experiment B: transition ramp
# --------------------------------------------------------------------

RAMP_SCHEDULES = {
    "instant":   [(0, 0.10)],
    "ramp_50":   [(0, 0.02), (12, 0.04), (24, 0.06), (36, 0.08), (50, 0.10)],
    "ramp_100":  [(0, 0.02), (25, 0.04), (50, 0.06), (75, 0.08), (100, 0.10)],
}


def _run_B(args):
    schedule_name, seed = args
    overrides = dict(CALIBRATED)
    overrides["wealth_tax_tiers"] = ((T10M, 0.02),)   # start
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    schedule = RAMP_SCHEDULES[schedule_name]
    sched_idx = 0
    for t in range(TICKS):
        while (sched_idx + 1 < len(schedule)
               and schedule[sched_idx + 1][0] <= t):
            sched_idx += 1
        rate = schedule[sched_idx][1]
        d.wealth_tax_tiers = ((T10M, rate),)
        step(agents, d, rng, t, accum)

    return ("B", schedule_name, seed, _metrics(agents, initial_nonstate))


# --------------------------------------------------------------------
# Sub-experiment C: class-conditional hybrid
# --------------------------------------------------------------------

def _run_C(args):
    arm, seed = args
    overrides = dict(CALIBRATED)
    if arm == "hybrid_universal":
        overrides["wealth_tax_tiers"] = ((T10M, HYBRID_RATE),)
    # arm == "hybrid_extractive": we run with no built-in WT and apply
    # the rate manually only to extractive-class agents per tick.
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)
    state = next((a for a in agents if a.type == Type.STATE), None)

    for t in range(TICKS):
        step(agents, d, rng, t, accum)
        if arm == "hybrid_extractive":
            for a in agents:
                if (not a.alive or a.type == Type.STATE
                        or a.type not in EXTRACTIVE
                        or a.wealth <= T10M):
                    continue
                tax = HYBRID_RATE * (a.wealth - T10M)
                tax = min(tax, a.wealth)
                a.wealth -= tax
                if state is not None:
                    state.wealth += tax

    return ("C", arm, seed, _metrics(agents, initial_nonstate))


# --------------------------------------------------------------------
# Sub-experiment D: stacked
# --------------------------------------------------------------------

D_ARMS = {
    "baseline":         {},
    "cap_only":         {"inheritance_cap": CAP_UNITS},
    "hybrid_only":      {"wealth_tax_tiers": ((T10M, HYBRID_RATE),)},
    "stacked":          {"inheritance_cap": CAP_UNITS,
                          "wealth_tax_tiers": ((T10M, HYBRID_RATE),)},
}


def _run_D(args):
    arm, seed = args
    overrides = dict(CALIBRATED)
    overrides.update(D_ARMS[arm])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    for t in range(TICKS):
        step(agents, d, rng, t, accum)

    return ("D", arm, seed, _metrics(agents, initial_nonstate))


# --------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------

def main():
    n_proc = max(1, cpu_count() - 1)

    print("== R2-11A: flight under hybrid ==")
    args_A = [(fr, s) for fr in [0.0, 0.005, 0.01, 0.02, 0.05]
              for s in range(SEEDS)]
    t0 = time.time()
    with Pool(n_proc) as p:
        rA = p.map(_run_A, args_A)
    print(f"  done in {time.time() - t0:.1f}s")

    print("\n== R2-11B: transition ramp ==")
    args_B = [(name, s) for name in RAMP_SCHEDULES for s in range(SEEDS)]
    t0 = time.time()
    with Pool(n_proc) as p:
        rB = p.map(_run_B, args_B)
    print(f"  done in {time.time() - t0:.1f}s")

    print("\n== R2-11C: class-conditional hybrid ==")
    args_C = [(arm, s) for arm in ["hybrid_universal", "hybrid_extractive"]
               for s in range(SEEDS)]
    t0 = time.time()
    with Pool(n_proc) as p:
        rC = p.map(_run_C, args_C)
    print(f"  done in {time.time() - t0:.1f}s")

    print("\n== R2-11D: stacked vs alone ==")
    args_D = [(arm, s) for arm in D_ARMS for s in range(SEEDS)]
    t0 = time.time()
    with Pool(n_proc) as p:
        rD = p.map(_run_D, args_D)
    print(f"  done in {time.time() - t0:.1f}s")

    def summarise(results, key_field):
        by_key: dict = {}
        for _, key, _, m in results:
            by_key.setdefault(key, []).append(m)
        out = {}
        for k, ms in by_key.items():
            keys = ms[0].keys()
            out[str(k)] = {kk: float(np.mean([m[kk] for m in ms]))
                           for kk in keys}
        return out

    sA = summarise(rA, "flight_rate")
    sB = summarise(rB, "schedule_name")
    sC = summarise(rC, "arm")
    sD = summarise(rD, "arm")

    def show(label, summary, keys):
        print(f"\n{label}")
        print(f"{'arm':<22} {'alive':>7} {'bn':>5} {'£100M+':>7} "
              f"{'bot-50':>8} {'top-10':>8} {'top-1':>8} {'state £B':>10}")
        for k in keys:
            s = summary[str(k)]
            extra = ""
            if "flown_count" in s and s["flown_count"] > 0:
                extra = f"  flown={s['flown_count']:.0f} (£{s['flown_wealth_gbp']/1e9:.0f}B)"
            print(f"{str(k):<22} {s['alive_rate']*100:>6.1f}% "
                  f"{s['billionaires']:>5.0f} "
                  f"{s['centimillionaires']:>7.0f} "
                  f"{s['bottom_50_share']*100:>7.1f}% "
                  f"{s['top_10_share']*100:>7.1f}% "
                  f"{s['top_1_share']*100:>7.1f}% "
                  f"{s['state_wealth_final_gbp']/1e9:>9.0f}B{extra}")

    show("R2-11A: FLIGHT (hybrid WT 10% > £10M, flight rate sweep)",
         sA, [0.0, 0.005, 0.01, 0.02, 0.05])
    show("R2-11B: TRANSITION RAMP", sB, list(RAMP_SCHEDULES.keys()))
    show("R2-11C: CLASS-CONDITIONAL", sC,
         ["hybrid_universal", "hybrid_extractive"])
    show("R2-11D: STACKED vs ALONE", sD, list(D_ARMS.keys()))

    out = {"A_flight": sA, "B_ramp": sB,
            "C_classcond": sC, "D_stacked": sD}
    out_path = OUT_DATA / "round2_hybrid_loose_ends.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
