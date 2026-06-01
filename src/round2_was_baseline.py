"""
Round 2 R2-2: WAS-calibrated baseline.

Stewart's critique: the paper's baseline has the bottom 50% holding
0.0% of household wealth, but the ONS Wealth and Assets Survey puts the
real UK figure at ~9%. The headline effect of "0% to 25%" is measured
against a model artefact, not the real distribution.

The model captures financial-wealth dynamics. It does not have housing
equity or DC/DB pension entitlements, which constitute most of the
real-UK bottom-50% wealth holding. The honest fix is to augment the
reported wealth statistic with a household non-financial-wealth floor
that approximates real housing + pension wealth for worker/maker
households, then re-report the headline.

Sources for the floor:
  ONS WAS 2018-2020: median household property wealth £210k, median
  private pension wealth £85k, total non-financial median ~£250-300k
  for households in the broad middle of the distribution.

Implementation:
  HOUSING_PENSION_FLOOR_GBP = £200k per WORKER and MAKER household.
  Convert to model units (WEALTH_UNIT_GBP = £100k -> 2.0 units) and
  add to net worth before share computation. RENTIER/EMPLOYER/LENDER
  households also have housing+pensions in reality but the model's
  financial-wealth dynamics already place them well above the floor,
  so adding it does not change their share materially.

Re-run the kill-switch 5 arms with the floor included.
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

# ONS WAS rough floor: median UK household non-financial wealth.
# £200k = housing equity for owners + pension entitlement for typical worker.
HOUSING_PENSION_FLOOR_GBP = 200_000.0
FLOOR_UNITS = HOUSING_PENSION_FLOOR_GBP / WEALTH_UNIT_GBP   # = 2.0

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
    "D_cap_spend":     {**SPEND, "inheritance_cap": 50.0},
    "E_cap_iht_spend": {**SPEND, "inheritance_cap": 50.0,
                         "inheritance_tax_rate": 0.40},
}

FLOOR_TYPES = {Type.WORKER, Type.MAKER}


def _augmented_net_worth(a) -> float:
    base = max(0.0, a.net_worth)
    if a.type in FLOOR_TYPES:
        return base + FLOOR_UNITS
    return base


def _run(args):
    name, seed = args
    overrides = dict(CALIBRATED)
    overrides.update(ARMS[name])
    d = Dials(seed=seed, population_scale=SCALE, **overrides)
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    accum = {}
    initial_nonstate = sum(1 for a in agents if a.type != Type.STATE)

    for t in range(TICKS):
        step(agents, d, rng, t, accum)

    living = [a for a in agents
              if a.alive and a.type != Type.STATE]

    raw = np.array([max(0.0, a.net_worth) for a in living])
    aug = np.array([_augmented_net_worth(a) for a in living])

    def shares(values):
        s = np.sort(values)
        n = len(values)
        total = values.sum() if values.sum() > 0 else 1.0
        bot50 = float(s[: n // 2].sum() / total)
        top10 = float(np.sort(values)[::-1][: max(1, n // 10)].sum() / total)
        top1 = float(np.sort(values)[::-1][: max(1, n // 100)].sum() / total)
        return bot50, top10, top1

    bot_raw, top10_raw, top1_raw = shares(raw)
    bot_aug, top10_aug, top1_aug = shares(aug)

    return name, seed, {
        "alive_rate": len(living) / max(initial_nonstate, 1),
        "bottom_50_share_raw": bot_raw,
        "bottom_50_share_was": bot_aug,
        "top_10_share_raw": top10_raw,
        "top_10_share_was": top10_aug,
        "top_1_share_raw": top1_raw,
        "top_1_share_was": top1_aug,
    }


def main():
    print(f"Housing + pension floor: £{HOUSING_PENSION_FLOOR_GBP:,.0f} "
          f"per worker/maker household (= {FLOOR_UNITS:.1f} model units)")
    args = [(n, s) for n in ARMS for s in range(SEEDS)]
    n_proc = min(max(1, cpu_count() - 1), len(args))
    print(f"running {len(args)} runs across {n_proc} procs ...")
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(_run, args)
    print(f"  done in {time.time() - t0:.1f}s")

    by_arm: dict[str, list[dict]] = {}
    for n, _, m in results:
        by_arm.setdefault(n, []).append(m)

    summary: dict[str, dict] = {}
    for n, ms in by_arm.items():
        keys = ms[0].keys()
        summary[n] = {k: float(np.mean([m[k] for m in ms])) for k in keys}

    print()
    print(f"{'arm':<20} {'alive':>7}  "
          f"{'bot-50 raw':>10} {'bot-50 WAS':>10}  "
          f"{'top-10 raw':>10} {'top-10 WAS':>10}  "
          f"{'top-1 raw':>10} {'top-1 WAS':>10}")
    for arm in ARMS:
        s = summary[arm]
        print(f"{arm:<20} {s['alive_rate']*100:>6.1f}%  "
              f"{s['bottom_50_share_raw']*100:>9.1f}% "
              f"{s['bottom_50_share_was']*100:>9.1f}%  "
              f"{s['top_10_share_raw']*100:>9.1f}% "
              f"{s['top_10_share_was']*100:>9.1f}%  "
              f"{s['top_1_share_raw']*100:>9.1f}% "
              f"{s['top_1_share_was']*100:>9.1f}%")

    out_path = OUT_DATA / "round2_was_baseline.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
