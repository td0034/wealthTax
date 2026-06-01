"""
Round 2 R2-5: BPR-style productive-business carve-out.

The Hunt critique: £5M captures every UK family business. The paper's
own implementation section concedes "carve-outs for productive-business
assets". Test what happens when the cap applies only to extractive
classes (RENTIER, LENDER, SPECULATOR) and exempts productive classes
(EMPLOYER, MAKER, WORKER) entirely.

This is the maximally generous carve-out interpretation: a perfect
test that productively-employed wealth is exempt, only extractively-held
wealth is capped.

Arms:
  baseline       no cap, no IHT, no spend         (status quo)
  cap_all        £5M cap on every class           (current paper)
  cap_extract    £5M cap only on RENTIER/LENDER/SPECULATOR
                  (BPR-style: productive business exempt)
  cap_extract_strict
                 same, but the productive classes are also capped at
                 £50M (preserves the no-dynasties goal at the very top)

All cap arms use state-spending package and 100% capture, so the cap
is in its strongest form. The only thing that changes is which classes
the cap applies to.
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

from sim import Dials, Type, WEALTH_UNIT_GBP, make_initial_population, step

OUT_DATA = Path("out/data")
OUT_DATA.mkdir(parents=True, exist_ok=True)

SCALE = 100
TICKS = 180
SEEDS = 4
CAP_UNITS = 50.0          # £5M
SOFT_CAP_UNITS = 500.0    # £50M soft cap for productive classes

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

EXTRACTIVE_CLASSES = {Type.RENTIER, Type.LENDER, Type.SPECULATOR}
PRODUCTIVE_CLASSES = {Type.EMPLOYER, Type.MAKER, Type.WORKER}

ARMS = ["baseline", "cap_all", "cap_extract", "cap_extract_strict"]


def _post_step_cap(agents, arm: str, state):
    """Apply a class-conditional cap to any deaths that just occurred
    in this tick. We approximate the carve-out by post-processing newly
    dead agents whose children inherited above the cap. Because the
    base sim.step already applies the configured cap uniformly, here we
    do not need a post-processing step when the cap is configured at
    runtime via the standard inheritance_cap field. Instead we run with
    inheritance_cap=inf for the carve-out arms and apply the class-
    conditional cap directly in the step wrapper below.
    """
    pass   # placeholder; logic is in _run


def _run_arm_with_class_cap(seed: int, arm: str):
    """Run with a class-conditional cap by post-processing each death.

    We disable the configured cap (set to inf) and instead intercept
    each death event in the step loop by maintaining a parallel
    bookkeeping: read state.wealth before/after step, identify the new
    children spawned, and rebalance.

    Simpler approach: copy the step's inheritance logic into a custom
    runner that respects class-conditional caps. To keep this local
    and avoid forking sim.step, we run the underlying step with a
    very loose cap and apply a class-conditional re-capping pass at
    each tick by walking newly-spawned children of each class.
    """
    overrides = dict(CALIBRATED)
    # Always disable the built-in cap for these arms; we will apply
    # class-conditional capping by post-processing.
    overrides["inheritance_cap"] = float("inf")
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    def class_cap_for(t: Type) -> float:
        if arm == "baseline":
            return float("inf")
        if arm == "cap_all":
            return CAP_UNITS
        if arm == "cap_extract":
            return CAP_UNITS if t in EXTRACTIVE_CLASSES else float("inf")
        if arm == "cap_extract_strict":
            if t in EXTRACTIVE_CLASSES:
                return CAP_UNITS
            return SOFT_CAP_UNITS
        return float("inf")

    # Walk births by detecting agents at age 0 immediately after step.
    # We post-process them: if their starting wealth > class cap, trim
    # excess and add to state.
    state = next((a for a in agents if a.type == Type.STATE), None)
    last_seen_ids = set(a.id for a in agents)

    for t in range(TICKS):
        step(agents, d, rng, t, accum)
        # Find new agents (born this tick) and apply class cap.
        for a in agents:
            if a.id in last_seen_ids:
                continue
            if a.age != 0 or a.type == Type.STATE:
                last_seen_ids.add(a.id)
                continue
            cap = class_cap_for(a.type)
            if a.wealth > cap:
                excess = a.wealth - cap
                a.wealth = cap
                if state is not None:
                    state.wealth += excess
            last_seen_ids.add(a.id)

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

    return arm, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "billionaires": int((gbp >= 1e9).sum()),
        "centimillionaires": int((gbp >= 1e8).sum()),
        "bottom_50_share": bot50,
        "top_10_share": top10,
        "top_1_share": top1,
        "state_wealth_final_gbp": (state_agent.wealth * WEALTH_UNIT_GBP
                                     if state_agent else 0.0),
    }


def _worker(args):
    seed, arm = args
    return _run_arm_with_class_cap(seed, arm)


def main():
    args = [(s, arm) for arm in ARMS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_worker, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_arm: dict[str, list[dict]] = {}
    for arm, _, m in results:
        by_arm.setdefault(arm, []).append(m)

    summary: dict[str, dict] = {}
    for arm, ms in by_arm.items():
        keys = ms[0].keys()
        summary[arm] = {k: float(np.mean([m[k] for m in ms])) for k in keys}

    print()
    print(f"{'arm':<22} {'alive':>7} {'bn':>5} {'£100M+':>7} "
          f"{'bot-50':>8} {'top-10':>8} {'top-1':>8} {'state £B':>10}")
    for arm in ARMS:
        s = summary[arm]
        print(f"{arm:<22} {s['alive_rate']*100:>6.1f}% "
              f"{s['billionaires']:>5.0f} "
              f"{s['centimillionaires']:>7.0f} "
              f"{s['bottom_50_share']*100:>7.1f}% "
              f"{s['top_10_share']*100:>7.1f}% "
              f"{s['top_1_share']*100:>7.1f}% "
              f"{s['state_wealth_final_gbp']/1e9:>9.0f}B")

    out_path = OUT_DATA / "round2_carveout.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
