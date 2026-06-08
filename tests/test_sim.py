"""Smoke tests and regression-direction tests for sim.py.

Runs in CI on every push.  Fast: completes in under 60 seconds on
GitHub Actions runners.

The point is not exact numerical regression (the model has stochastic
elements) but qualitative invariants:

  1. The model imports.
  2. A short run completes without crashing.
  3. Status quo concentrates wealth at the top.
  4. The £5M inheritance cap reduces top concentration substantially.
  5. The hybrid wealth tax at 10% above £10M reduces top concentration
     even more than the cap.

If any of these fail, the model has regressed and the headline
findings are at risk.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import sim   # noqa: E402


SCALE_SMALL = 10     # N = 1,000
TICKS_SHORT = 90


def _terminal_top10_share(d: sim.Dials) -> float:
    rng = np.random.default_rng(d.seed)
    agents = sim.make_initial_population(rng, d)
    accum: dict = {}
    for t in range(TICKS_SHORT):
        sim.step(agents, d, rng, t, accum)
    living = [a for a in agents
              if a.alive and a.type != sim.Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    total = max(nws.sum(), 1e-9)
    return float(np.sort(nws)[::-1][: max(1, len(nws) // 10)].sum() / total)


def _terminal_bot50_share(d: sim.Dials) -> float:
    rng = np.random.default_rng(d.seed)
    agents = sim.make_initial_population(rng, d)
    accum: dict = {}
    for t in range(TICKS_SHORT):
        sim.step(agents, d, rng, t, accum)
    living = [a for a in agents
              if a.alive and a.type != sim.Type.STATE]
    nws = np.array([max(0.0, a.net_worth) for a in living])
    total = max(nws.sum(), 1e-9)
    return float(np.sort(nws)[: len(nws) // 2].sum() / total)


def test_import():
    assert hasattr(sim, "Dials")
    assert hasattr(sim, "step")
    assert hasattr(sim, "make_initial_population")
    assert hasattr(sim, "Type")
    assert hasattr(sim, "WEALTH_UNIT_GBP")


def test_short_run_no_crash():
    d = sim.Dials(seed=42, population_scale=SCALE_SMALL)
    rng = np.random.default_rng(d.seed)
    agents = sim.make_initial_population(rng, d)
    accum: dict = {}
    for t in range(20):
        h = sim.step(agents, d, rng, t, accum)
        assert "metabolic_rate" in h
        assert h["alive"] >= 0
        assert not np.isnan(h["metabolic_rate"])


def test_status_quo_concentrates():
    """At r=0.08 with no policy intervention, top-10% holds the majority."""
    d = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
    )
    top10 = _terminal_top10_share(d)
    assert top10 >= 0.80, (
        f"Status quo top-10% share was {top10:.2%}, expected >=80%. "
        "The compounding mechanism may have regressed."
    )


def test_cap_reduces_top_concentration():
    """The £5M inheritance cap reduces top-10% share substantially
    vs status quo."""
    spend_kwargs = dict(
        ubi=0.4, state_employs_fraction=0.3,
        state_employs_wage=0.8, state_buys_maker_output=5.0,
    )
    d_sq = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
    )
    d_cap = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
        inheritance_cap=50.0, **spend_kwargs,
    )
    top_sq = _terminal_top10_share(d_sq)
    top_cap = _terminal_top10_share(d_cap)
    bot_sq = _terminal_bot50_share(d_sq)
    bot_cap = _terminal_bot50_share(d_cap)

    assert top_cap < top_sq - 0.20, (
        f"Cap top-10% {top_cap:.2%} not >20pp below status quo {top_sq:.2%}. "
        "Cap mechanism may have regressed."
    )
    assert bot_cap > bot_sq + 0.05, (
        f"Cap bot-50% {bot_cap:.2%} not >5pp above status quo {bot_sq:.2%}. "
        "Ownership-redistribution claim may have regressed."
    )


def test_hybrid_dominates_zucman_2pct():
    """At r=0.08, the 10% wealth tax above £10M reduces top-10% more
    than Zucman 2%, by the Benhabib threshold (tau > r vs tau < r)."""
    spend_kwargs = dict(
        ubi=0.4, state_employs_fraction=0.3,
        state_employs_wage=0.8, state_buys_maker_output=5.0,
    )
    d_zucman = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
        wealth_tax_tiers=((100.0, 0.02),), **spend_kwargs,
    )
    d_hybrid = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
        wealth_tax_tiers=((100.0, 0.10),), **spend_kwargs,
    )
    top_zucman = _terminal_top10_share(d_zucman)
    top_hybrid = _terminal_top10_share(d_hybrid)

    assert top_hybrid < top_zucman - 0.20, (
        f"Hybrid top-10% {top_hybrid:.2%} not >20pp below Zucman 2% "
        f"{top_zucman:.2%}. The Benhabib-threshold claim may have regressed."
    )


def test_enforcement_friction_collapses_cap():
    """Cap at <100% enforcement should produce more top concentration
    than at full enforcement (dynastic-recompounding nonlinearity)."""
    spend_kwargs = dict(
        ubi=0.4, state_employs_fraction=0.3,
        state_employs_wage=0.8, state_buys_maker_output=5.0,
    )
    d_full = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
        inheritance_cap=50.0, inheritance_capture_rate=1.0,
        **spend_kwargs,
    )
    d_leaky = sim.Dials(
        seed=42, population_scale=SCALE_SMALL,
        capital_return=0.08, rent_share_of_wage=0.20, subsistence=0.30,
        inheritance_cap=50.0, inheritance_capture_rate=0.5,
        **spend_kwargs,
    )
    top_full = _terminal_top10_share(d_full)
    top_leaky = _terminal_top10_share(d_leaky)

    assert top_leaky > top_full + 0.05, (
        f"50% capture top-10% {top_leaky:.2%} not >5pp above 100% "
        f"capture {top_full:.2%}. Enforcement-friction R2-4 finding "
        "may have regressed."
    )
