"""
Unequal Agents v1.

Adds to v0:
- State spending: state employs unemployed workers and buys maker output.
- Lender recapitalisation: surplus deposits replenish the lending pool.
- Reproduction + inheritance: agents age, die, are replaced by children who
  inherit (capped) wealth and a *bandwidth-limited* skill vector.
- Memory transmission: skills are a K-dimensional vector. The number of
  dimensions a child inherits scales with parent wealth (the supervisor's
  mechanism). Tracks cultural diversity over time.
- Multi-seed runs with aggregated ribbon plots.
- New metrics: cultural diversity, autocatalytic closure, knowledge lost.

One tick ~ one year. Default lifespan ~70 ticks.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from enum import IntEnum
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Wealth unit interpretation
# ---------------------------------------------------------------------------
# For political-policy scenarios we treat one model wealth unit as £100,000.
# That gives:
#   100   units = £10M    (Zucman lower bracket)
#   500   units = £50M    (Warren lower bracket)
#   1000  units = £100M
#   3200  units = £320M
#   10000 units = £1B     (billionaire bracket)
WEALTH_UNIT_GBP = 100_000.0


# ---------------------------------------------------------------------------
# Cast
# ---------------------------------------------------------------------------

class Type(IntEnum):
    WORKER = 0
    MAKER = 1
    EMPLOYER = 2
    LENDER = 3
    RENTIER = 4
    SPECULATOR = 5
    STATE = 6


TYPE_COLOURS = {
    Type.WORKER: "#3b82f6",
    Type.MAKER: "#22c55e",
    Type.EMPLOYER: "#f97316",
    Type.LENDER: "#eab308",
    Type.RENTIER: "#ef4444",
    Type.SPECULATOR: "#a855f7",
    Type.STATE: "#1f2937",
}

PRODUCTIVE = {Type.WORKER, Type.MAKER, Type.EMPLOYER}
EXTRACTIVE = {Type.LENDER, Type.RENTIER, Type.SPECULATOR}

INITIAL_COUNTS = {
    Type.WORKER: 72,
    Type.MAKER: 9,
    Type.EMPLOYER: 7,
    Type.LENDER: 5,
    Type.RENTIER: 3,
    Type.SPECULATOR: 3,
    Type.STATE: 1,
}

INITIAL_WEALTH_SHARE = {
    Type.WORKER: 50,
    Type.MAKER: 80,
    Type.EMPLOYER: 120,
    Type.LENDER: 150,
    Type.RENTIER: 350,
    Type.SPECULATOR: 200,
    Type.STATE: 50,
}

# K-dimensional skill vector. Each dimension is a class of competence.
# A skill being 0 means it has been lost; >0 means present at some level.
SKILL_DIMS = 5
SKILL_NAMES = ["technical", "organisational", "social", "financial", "generative"]


# ---------------------------------------------------------------------------
# Dials
# ---------------------------------------------------------------------------

@dataclass
class Dials:
    """Viewer-as-legislator's panel."""
    # production
    wage: float = 1.0
    maker_multiplier: float = 1.6
    employer_markup: float = 0.4
    workers_per_maker: int = 2
    workers_per_employer: int = 6

    # capital
    capital_return: float = 0.04
    rent_share_of_wage: float = 0.35
    interest_rate: float = 0.06
    spec_drift: float = 0.015
    spec_vol: float = 0.12

    # state
    ubi: float = 0.0
    flat_tax_rate: float = 0.0
    tax_progressivity: float = 0.0
    wealth_tax_threshold: float = 50.0
    # Stacked-marginal progressive wealth tax. List of (threshold, marginal_rate)
    # tuples; total tax = sum_i max(0, wealth - threshold_i) * marginal_rate_i.
    # Per-tick (annual) rate. Example Zucman flat:  [(100, 0.02)]
    # Example Zucman progressive: [(100, 0.02), (1000, 0.02), (10000, 0.04)]
    # (2% above £10M, +2% above £100M, +4% above £1B -> 8% effective at top.)
    wealth_tax_tiers: tuple[tuple[float, float], ...] = ()
    # State-spending dials (new in v1).
    state_employs_fraction: float = 0.0   # fraction of unemployed workers state hires
    state_employs_wage: float = 1.0       # wage state pays its hires
    state_buys_maker_output: float = 0.0  # spend per tick on maker output
    state_recap_lenders: float = 0.0      # min lending pool size state will backstop

    # life
    subsistence: float = 0.6
    debt_ceiling: float = 25.0
    lifespan_mean: float = 70.0
    # Material constraint (A6). If material_pool_initial > 0, makers draw
    # from a global material pool that depletes with use and replenishes
    # via material_regen per tick. Closure metric should track survival
    # under finite material supply. Default 0 disables.
    material_pool_initial: float = 0.0
    material_pool_regen: float = 0.0
    material_cost_per_unit: float = 2.0       # cost paid per maker tick
    lifespan_std: float = 12.0
    starvation_lifespan_penalty: float = 20.0   # how much sooner the poor die

    # transmission (new in v1)
    inheritance_cap: float = float("inf")     # absolute cap on bequest
    inheritance_tax_rate: float = 0.0         # share clawed back at death
    memory_bandwidth_base: float = 0.5        # skill-dims always transmitted
    memory_bandwidth_wealth_scale: float = 0.5  # extra dims = scale * (wealth / 100)
    skill_mutation_rate: float = 0.05         # chance per dim per generation
    # When True, child's transmitted skill values are drawn from the class-typical
    # prior rather than copied from the parent. Bandwidth (number of dimensions)
    # is unchanged. Used for the clean Spangler & Sarkar comparison: this isolates
    # whether *the transmitted values* are parent-derived vs class-typical, while
    # holding the bandwidth-gating mechanism intact.
    inherit_from_class_prior: bool = False

    # logistics
    seed: int = 42
    # Scale: agent counts and initial wealth totals are multiplied by
    # population_scale (state stays a singleton). Per-capita stays invariant.
    # Spending dials with absolute budgets (state_buys_maker_output,
    # state_recap_lenders) are scaled at point of use.
    population_scale: int = 1


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    id: int
    type: Type
    wealth: float
    skills: np.ndarray            # length SKILL_DIMS
    age: int = 0
    lifespan: int = 70
    debt: float = 0.0
    alive: bool = True
    starved_at: int | None = None
    died_at: int | None = None              # tick of any death (starve or age)
    death_cause: str | None = None          # "starvation" | "debt_writeoff" | "age"
    peak_wealth: float = 0.0                # max lifetime wealth (for mortality-corrected metrics)
    bandwidth_dims_at_birth: int = 0        # realised bandwidth at inheritance
    employed_this_tick: bool = False

    @property
    def net_worth(self) -> float:
        return self.wealth - self.debt

    @property
    def skill_total(self) -> float:
        return float(self.skills.sum())

    @property
    def skill_breadth(self) -> int:
        return int((self.skills > 0).sum())


_id_counter = 0


def _next_id() -> int:
    global _id_counter
    _id_counter += 1
    return _id_counter


def reset_id_counter() -> None:
    global _id_counter
    _id_counter = 0


def make_agent(t: Type, wealth: float, rng: np.random.Generator,
               d: Dials, parent_skills: np.ndarray | None = None,
               parent_wealth: float | None = None) -> Agent:
    if parent_skills is None:
        # First-generation: skills sampled with class-specific bias.
        skills = rng.beta(2, 2, SKILL_DIMS).astype(float)
        # Makers get a generative boost, employers get organisational+financial,
        # rentiers/speculators get financial only, workers get social/technical.
        if t == Type.MAKER:
            skills[4] += 0.4   # generative
            skills[0] += 0.2   # technical
        elif t == Type.EMPLOYER:
            skills[1] += 0.3
            skills[3] += 0.2
        elif t in (Type.RENTIER, Type.SPECULATOR, Type.LENDER):
            skills[3] += 0.4   # financial
        elif t == Type.WORKER:
            skills[2] += 0.2
            skills[0] += 0.2
        skills = np.clip(skills, 0.0, 1.5)
    else:
        # Inherited via bandwidth-limited transmission. AL-2 redesign:
        # use log-wealth so the coupling stays graded across orders of magnitude
        # rather than saturating at parent_wealth ~ 500.
        # log_term = log10(max(1, parent_wealth)) / 4   in [0, ~1.3]
        # bandwidth_dims = b0*K + bw*K*log_term, clipped to [1, K]
        log_term = float(np.log10(max(1.0, parent_wealth or 1.0))) / 4.0
        bandwidth_dims = int(np.clip(
            round(d.memory_bandwidth_base * SKILL_DIMS
                  + d.memory_bandwidth_wealth_scale * SKILL_DIMS * log_term),
            1, SKILL_DIMS,
        ))
        transmitted = np.zeros(SKILL_DIMS, dtype=float)
        if d.inherit_from_class_prior:
            # Clean Spangler & Sarkar comparison arm: same bandwidth, same
            # class-typical biases, but transmitted values are drawn from the
            # class-typical prior rather than copied from the parent. This
            # isolates "transmitted values are parent-derived" as the only
            # toggle relative to baseline.
            prior = rng.beta(2, 2, SKILL_DIMS).astype(float)
            if t == Type.MAKER:
                prior[4] += 0.4; prior[0] += 0.2
            elif t == Type.EMPLOYER:
                prior[1] += 0.3; prior[3] += 0.2
            elif t in (Type.RENTIER, Type.SPECULATOR, Type.LENDER):
                prior[3] += 0.4
            elif t == Type.WORKER:
                prior[2] += 0.2; prior[0] += 0.2
            prior = np.clip(prior, 0.0, 1.5)
            # Pick the *prior's* strongest bandwidth_dims values for the child;
            # bandwidth still scales with parent wealth.
            idx = np.argsort(prior)[::-1][:bandwidth_dims]
            transmitted[idx] = prior[idx]
        else:
            # Default: pick the parent's strongest `bandwidth_dims` skills.
            idx = np.argsort(parent_skills)[::-1][:bandwidth_dims]
            transmitted[idx] = parent_skills[idx]
        # Small chance of fresh draw per dimension (mutation).
        for i in range(SKILL_DIMS):
            if rng.random() < d.skill_mutation_rate:
                transmitted[i] = float(rng.beta(2, 2))
        skills = transmitted

    lifespan = int(np.clip(rng.normal(d.lifespan_mean, d.lifespan_std), 20, 120))
    # Wealth at birth: rich kids get full inheritance, poor get poor lifespan.
    if t == Type.WORKER and wealth < 5:
        lifespan = max(20, lifespan - int(d.starvation_lifespan_penalty))
    # Record realised bandwidth for AL-2 decomposition analysis.
    bdims = 0
    if parent_skills is not None:
        bdims = int((skills > 0).sum())
    a = Agent(id=_next_id(), type=t, wealth=wealth, skills=skills,
              lifespan=lifespan, peak_wealth=max(0.0, wealth),
              bandwidth_dims_at_birth=bdims)
    return a


def make_initial_population(rng: np.random.Generator, d: Dials) -> list[Agent]:
    reset_id_counter()
    agents: list[Agent] = []
    scale = max(1, int(d.population_scale))
    for t, n in INITIAL_COUNTS.items():
        # State stays a singleton; all other counts and totals scale.
        if t == Type.STATE:
            n_eff = 1
            total = INITIAL_WEALTH_SHARE[t] * scale
        else:
            n_eff = n * scale
            total = INITIAL_WEALTH_SHARE[t] * scale
        if n_eff == 1:
            shares = np.array([1.0])
        else:
            raw = rng.lognormal(0, 0.5, n_eff)
            shares = raw / raw.sum()
        for i in range(n_eff):
            w = float(total * shares[i])
            a = make_agent(t, w, rng, d)
            if t == Type.WORKER and rng.random() < 0.18:
                a.debt = float(rng.uniform(3, 10))
            a.age = int(rng.uniform(0, a.lifespan * 0.9))
            agents.append(a)
    return agents


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def gini(values: np.ndarray) -> float:
    """Standard Gini on non-negative wealth values. Callers exclude State."""
    v = np.clip(values, 0.0, None)
    s = v.sum()
    if s == 0:
        return 0.0
    v = np.sort(v)
    n = len(v)
    cum = np.cumsum(v)
    return float((n + 1 - 2 * cum.sum() / cum[-1]) / n)


def gini_signed(values: np.ndarray) -> float:
    """Gini on signed net worth (allowing negative). Adds 2*|min| offset
    to all entries so values are non-negative before computing the
    standard formula. Reports the same number as gini() when min >= 0."""
    if len(values) == 0:
        return 0.0
    shift = max(0.0, -float(np.min(values))) + 1e-9
    return gini(values + shift)


def cultural_diversity(agents: list[Agent]) -> float:
    """Mean per-dimension variance of skills across the living population."""
    living = [a for a in agents if a.alive]
    if len(living) < 2:
        return 0.0
    mat = np.array([a.skills for a in living])
    return float(mat.var(axis=0).mean())


def cultural_breadth(agents: list[Agent]) -> float:
    """Mean number of skills present (>0) across living agents."""
    living = [a for a in agents if a.alive]
    if not living:
        return 0.0
    return float(np.mean([(a.skills > 0).sum() for a in living]))


def top_k_share(values: np.ndarray, k: int) -> float:
    """Wealth share held by the top-k by count. Callers exclude State."""
    pos = np.sort(np.clip(values, 0.0, None))[::-1]
    total = pos.sum()
    if total == 0 or k <= 0:
        return 0.0
    return float(pos[:k].sum() / total)


def top_frac_share(values: np.ndarray, frac: float) -> float:
    """Wealth share held by the top fraction of the population by count.
    Population size is len(values); caller must include all relevant
    entries (e.g. for mortality correction, include recent deaths)."""
    n = len(values)
    if n == 0:
        return 0.0
    k = max(1, int(round(frac * n)))
    return top_k_share(values, k)


# ---------------------------------------------------------------------------
# Mortality-corrected metrics
# ---------------------------------------------------------------------------
# A "mortality-corrected" wealth array is built from living agents'
# current net worth plus the peak-lifetime wealth of agents who died within
# the last `window` ticks. The intuition: if a policy kills wealth-bearing
# agents, those wealth holdings should not vanish from the denominator of
# share statistics; otherwise top-share rises mechanically.

def mortality_corrected_values(
    living_values: np.ndarray,
    recent_deaths: list[tuple],            # [(tick_died, type_name, peak_wealth, cause)]
    current_tick: int,
    window: int = 30,
    exclude_types: tuple[str, ...] = ("STATE",),
) -> np.ndarray:
    extras = [pw for (td, tn, pw, _c) in recent_deaths
              if current_tick - td <= window and tn not in exclude_types]
    if not extras:
        return living_values
    return np.concatenate([living_values, np.array(extras, dtype=float)])


def gini_corrected(living_values, recent_deaths, current_tick, window=30):
    return gini(mortality_corrected_values(living_values, recent_deaths,
                                           current_tick, window))


def top_frac_share_corrected(living_values, recent_deaths, current_tick,
                             frac: float, window: int = 30) -> float:
    return top_frac_share(
        mortality_corrected_values(living_values, recent_deaths,
                                   current_tick, window),
        frac,
    )


# ---------------------------------------------------------------------------
# One tick
# ---------------------------------------------------------------------------

def step(agents: list[Agent], d: Dials, rng: np.random.Generator,
         tick: int, accum: dict) -> dict:
    living = [a for a in agents if a.alive]
    by_type: dict[Type, list[Agent]] = {t: [] for t in Type}
    for a in living:
        by_type[a.type].append(a)
        a.employed_this_tick = False
        a.age += 1

    recent_deaths = accum.setdefault("recent_deaths", [])

    def _record_death(a: Agent, cause: str) -> None:
        a.alive = False
        a.died_at = tick
        a.death_cause = cause
        if cause == "starvation":
            a.starved_at = tick
        # Peak-lifetime wealth becomes the mortality-corrected denominator entry.
        recent_deaths.append((tick, a.type.name, float(a.peak_wealth), cause))

    workers = by_type[Type.WORKER]
    makers = by_type[Type.MAKER]
    employers = by_type[Type.EMPLOYER]
    lenders = by_type[Type.LENDER]
    rentiers = by_type[Type.RENTIER]
    speculators = by_type[Type.SPECULATOR]
    state = by_type[Type.STATE][0] if by_type[Type.STATE] else None

    metabolic_rate = 0.0   # new value created
    productive_flow = 0.0  # value flowing between productive types
    extractive_flow = 0.0  # value flowing from productive to extractive types

    # Per-(from_type, to_type) flow accumulator. Keys are tuples of type names.
    flows = accum.setdefault("flows", {})
    def _rec(src: str, dst: str, amount: float) -> None:
        if amount <= 0:
            return
        key = (src, dst)
        flows[key] = flows.get(key, 0.0) + amount

    # --- MATERIAL POOL (A6 optional) ------------------------------------
    # If material_pool_initial > 0, makers draw from a finite global pool
    # that depletes with use and replenishes each tick. Initialised on
    # first call. Once pool is empty, makers cannot produce.
    if d.material_pool_initial > 0:
        if "material_pool" not in accum:
            accum["material_pool"] = float(d.material_pool_initial)
        accum["material_pool"] += float(d.material_pool_regen)
    material_pool_active = d.material_pool_initial > 0
    material_pool = accum.get("material_pool", float("inf"))

    # --- PRODUCTION ------------------------------------------------------
    # Most-skilled worker hired first (use technical+organisational sum).
    def worker_skill(w: Agent) -> float:
        return float(w.skills[0] + w.skills[1])
    queue = sorted(workers, key=lambda w: -worker_skill(w))

    def pay_wage(w: Agent, wage: float) -> float:
        paid = wage * (0.7 + 0.6 * worker_skill(w) / 2.0)
        w.wealth += paid
        return paid

    # Makers produce (catalytic).
    for m in sorted(makers, key=lambda x: -x.wealth):
        material_cost = float(d.material_cost_per_unit)
        max_wage_bill = d.wage * d.workers_per_maker
        if m.wealth < material_cost + max_wage_bill:
            continue
        # A6: skip if material pool is exhausted.
        if material_pool_active and material_pool < material_cost:
            continue
        if material_pool_active:
            material_pool -= material_cost
            accum["material_pool"] = material_pool
        hires: list[Agent] = []
        for _ in range(d.workers_per_maker):
            if not queue:
                break
            w = queue.pop(0)
            hires.append(w)
            w.employed_this_tick = True
            paid = pay_wage(w, d.wage)
            productive_flow += paid
            _rec("MAKER", "WORKER", paid)
        m.wealth -= material_cost + d.wage * len(hires)
        labour_value = sum(d.wage * (0.7 + 0.6 * worker_skill(h) / 2.0)
                           for h in hires)
        inputs = material_cost + labour_value
        # Maker's own generative skill scales the multiplier.
        eff_mult = d.maker_multiplier * (0.7 + 0.6 * m.skills[4])
        output = inputs * eff_mult
        m.wealth += output
        metabolic_rate += output - inputs
        productive_flow += output - inputs       # CC-2: maker value-add counted as productive creation

    # Employers capture markup.
    for e in sorted(employers, key=lambda x: -x.wealth):
        wage_bill = d.wage * d.workers_per_employer
        if e.wealth < wage_bill:
            continue
        hires = []
        for _ in range(d.workers_per_employer):
            if not queue:
                break
            w = queue.pop(0)
            hires.append(w)
            w.employed_this_tick = True
            paid = pay_wage(w, d.wage)
            productive_flow += paid
            _rec("EMPLOYER", "WORKER", paid)
        worker_output = sum(d.wage * (0.7 + 0.6 * worker_skill(h) / 2.0)
                            for h in hires)
        e.wealth -= d.wage * len(hires)
        captured = worker_output * (1 + d.employer_markup)
        e.wealth += captured
        markup_value = worker_output * d.employer_markup * 0.4
        metabolic_rate += markup_value
        productive_flow += markup_value          # CC-2: employer markup counted as productive

    # State as employer of last resort.
    if state is not None and d.state_employs_fraction > 0 and queue:
        max_hires = int(np.ceil(len(queue) * d.state_employs_fraction))
        wage_each = d.state_employs_wage
        bill = max_hires * wage_each
        if state.wealth >= bill:
            for _ in range(max_hires):
                if not queue:
                    break
                w = queue.pop(0)
                w.employed_this_tick = True
                state.wealth -= wage_each
                w.wealth += wage_each
                productive_flow += wage_each
                _rec("STATE", "WORKER", wage_each)
                metabolic_rate += wage_each * 0.5  # service output

    # State as customer for makers (props up demand). Budget scales with N.
    if state is not None and d.state_buys_maker_output > 0 and makers:
        scaled_budget = d.state_buys_maker_output * d.population_scale
        budget = min(scaled_budget, max(0.0, state.wealth))
        per_maker = budget / len(makers)
        state.wealth -= budget
        for m in makers:
            m.wealth += per_maker
            productive_flow += per_maker
            _rec("STATE", "MAKER", per_maker)

    # Rent. O(W + R) — accumulate then distribute.
    if rentiers and workers and d.rent_share_of_wage > 0:
        rent_per_worker = d.rent_share_of_wage * d.wage
        for w in workers:
            w.wealth -= rent_per_worker
        total_rent = rent_per_worker * len(workers)
        total_rentier_wealth = sum(r.wealth for r in rentiers) or 1.0
        for r in rentiers:
            r.wealth += total_rent * (r.wealth / total_rentier_wealth)
        extractive_flow += total_rent
        _rec("WORKER", "RENTIER", total_rent)

    # Capital return.
    for r in rentiers:
        gain = r.wealth * d.capital_return
        r.wealth += gain
        extractive_flow += gain

    # Speculation. Speculator gains accrue to the extractive class on the
    # same footing as rentier capital return (both are intra-stock wealth
    # creation accruing to an extractive class). Positive speculator returns
    # count toward F_ext symmetrically with capital_return; negative returns
    # are wealth losses that did not transfer to anyone, treated the same way
    # rent and interest do not have negative counterparts.
    speculator_net_delta = 0.0
    for s in speculators:
        ret = float(rng.normal(d.spec_drift, d.spec_vol))
        delta = s.wealth * ret
        s.wealth = max(0.0, s.wealth + delta)
        speculator_net_delta += delta
        if delta > 0:
            extractive_flow += delta

    # --- CONSUMPTION -----------------------------------------------------
    # Compute lender capacity once, accumulate total borrowing, distribute at end.
    if lenders:
        lender_capacity = np.array([max(0.0, l.wealth - d.subsistence * 2)
                                    for l in lenders])
        cap_weights = (lender_capacity / lender_capacity.sum()
                       if lender_capacity.sum() > 0 else None)
        total_cap_remaining = float(lender_capacity.sum())
    else:
        cap_weights = None
        total_cap_remaining = 0.0
    new_starved = 0
    total_borrowed = 0.0
    for a in living:
        if a.type == Type.STATE:
            continue
        a.wealth -= d.subsistence
        if a.wealth >= 0:
            continue
        shortfall = -a.wealth
        a.wealth = 0.0
        if total_cap_remaining <= 0:
            _record_death(a, "starvation")
            new_starved += 1
            continue
        borrow = min(shortfall, total_cap_remaining)
        a.debt += borrow
        total_borrowed += borrow
        total_cap_remaining -= borrow
        _rec("LENDER", a.type.name, borrow)
        if borrow < shortfall:
            _record_death(a, "starvation")
            new_starved += 1
    if total_borrowed > 0 and cap_weights is not None:
        for i, l in enumerate(lenders):
            l.wealth -= total_borrowed * cap_weights[i]

    # --- INTEREST & REPAYMENT --------------------------------------------
    # Accumulate total flows; distribute to lenders in a single O(L) pass.
    total_lender_wealth = sum(l.wealth for l in lenders) or 1.0
    total_to_lenders = 0.0
    for a in living:
        if a.debt <= 0 or not a.alive:
            continue
        interest = a.debt * d.interest_rate
        if a.wealth >= interest:
            a.wealth -= interest
            total_to_lenders += interest
            extractive_flow += interest
            _rec(a.type.name, "LENDER", interest)
        else:
            a.debt += interest
        if a.wealth > d.subsistence * 3:
            repay = min(a.debt, a.wealth - d.subsistence * 3)
            a.wealth -= repay
            a.debt -= repay
            total_to_lenders += repay
            _rec(a.type.name, "LENDER", repay)
    if total_to_lenders > 0 and lenders:
        for l in lenders:
            l.wealth += total_to_lenders * (l.wealth / total_lender_wealth)

    # Write-offs at debt ceiling.
    debt_written_off = 0.0
    for a in living:
        if a.type == Type.STATE or not a.alive:
            continue
        if a.net_worth < -d.debt_ceiling:
            _record_death(a, "debt_writeoff")
            new_starved += 1
            if a.debt > 0:
                debt_written_off += a.debt
                a.debt = 0.0
    if debt_written_off > 0 and lenders:
        tlw = sum(l.wealth for l in lenders) or 1.0
        for l in lenders:
            l.wealth -= debt_written_off * (l.wealth / tlw)

    # --- LENDER RECAPITALISATION ----------------------------------------
    # Wealthy private agents deposit a fraction of surplus with lenders
    # (earning the system implicit demand for credit). State backstops the
    # pool if it falls below the configured floor.
    deposit_pool = 0.0
    for a in living:
        if a.type in (Type.RENTIER, Type.EMPLOYER, Type.MAKER) and a.wealth > 20:
            deposit = (a.wealth - 20) * 0.02
            a.wealth -= deposit
            deposit_pool += deposit
            _rec(a.type.name, "LENDER", deposit)
    if deposit_pool > 0 and lenders:
        for l in lenders:
            l.wealth += deposit_pool / len(lenders)

    if state is not None and d.state_recap_lenders > 0:
        floor = d.state_recap_lenders * d.population_scale
        cur = sum(l.wealth for l in lenders)
        if cur < floor and state.wealth > 0:
            need = min(floor - cur, state.wealth)
            state.wealth -= need
            for l in lenders:
                l.wealth += need / max(1, len(lenders))
            _rec("STATE", "LENDER", need)

    # --- STATE TAX + UBI ------------------------------------------------
    tax_collected = 0.0
    if state is not None:
        for a in living:
            if a.type == Type.STATE or not a.alive or a.wealth <= 0:
                continue
            tax = d.flat_tax_rate * a.wealth
            if a.wealth > d.wealth_tax_threshold:
                tax += d.tax_progressivity * (a.wealth - d.wealth_tax_threshold)
            for thresh, rate in d.wealth_tax_tiers:
                if a.wealth > thresh:
                    tax += rate * (a.wealth - thresh)
            tax = min(tax, a.wealth)
            a.wealth -= tax
            tax_collected += tax
            _rec(a.type.name, "STATE", tax)
        state.wealth += tax_collected
        if d.ubi > 0 and state.wealth > 0:
            recipients = [a for a in living if a.type != Type.STATE and a.alive]
            per_head = min(d.ubi, state.wealth / max(1, len(recipients)))
            for a in recipients:
                a.wealth += per_head
                _rec("STATE", a.type.name, per_head)
            state.wealth -= per_head * len(recipients)

    # --- LIFE: AGE-OUT, REPRODUCTION, TRANSMISSION ----------------------
    knowledge_lost = 0.0
    births = 0
    for a in living:
        if not a.alive or a.type == Type.STATE:
            continue
        if a.age >= a.lifespan:
            # Natural death: spawn a child of the same type.
            _record_death(a, "age")
            net = max(0.0, a.net_worth)
            after_tax = net * (1 - d.inheritance_tax_rate)
            bequest = min(after_tax, d.inheritance_cap)
            if state is not None:
                state.wealth += (net - bequest)
                _rec(a.type.name, "STATE", net - bequest)
            # Skill transmission via finite bandwidth.
            child = make_agent(a.type, bequest, rng, d,
                               parent_skills=a.skills, parent_wealth=net)
            agents.append(child)
            # Knowledge loss = the share of the parent's skill vector that was
            # *not* transmitted (the bandwidth was too narrow).
            transmitted_mass = child.skills.sum()
            knowledge_lost += max(0.0, a.skill_total - transmitted_mass)
            births += 1

    # --- PEAK-WEALTH UPDATE ---------------------------------------------
    # Update each agent's peak lifetime wealth for mortality-corrected stats.
    for a in agents:
        if a.alive and a.wealth > a.peak_wealth:
            a.peak_wealth = a.wealth

    # --- METRICS --------------------------------------------------------
    alive = [a for a in agents if a.alive]
    alive_nonstate = [a for a in alive if a.type != Type.STATE]
    nws_all = np.array([a.net_worth for a in alive])
    nws = np.array([a.net_worth for a in alive_nonstate])   # CC-1: exclude State
    wealth_by_type = {t: float(sum(a.net_worth for a in alive if a.type == t))
                      for t in Type}

    autocatalytic_closure = (
        productive_flow / (productive_flow + extractive_flow)
        if (productive_flow + extractive_flow) > 0 else 0.0
    )

    accum["knowledge_lost_cum"] = accum.get("knowledge_lost_cum", 0.0) + knowledge_lost
    accum["starved_cum"] = accum.get("starved_cum", 0) + new_starved
    accum["births_cum"] = accum.get("births_cum", 0) + births

    # Trim recent_deaths older than 60 ticks (well past any window we use).
    if recent_deaths:
        recent_deaths[:] = [r for r in recent_deaths
                            if tick - r[0] <= 60]

    # Mortality-corrected variants. E-3.
    nws_corrected = mortality_corrected_values(
        nws, recent_deaths, tick, window=30)

    # Prune dead agents periodically to keep iteration cost bounded at scale.
    if tick % 10 == 9:
        agents[:] = [a for a in agents if a.alive]

    return {
        "tick": tick,
        # Default Gini and top-shares exclude State (CC-1).
        "gini": gini(nws),
        "gini_with_state": gini(nws_all),
        "gini_corrected": gini(nws_corrected),
        "gini_signed": gini_signed(nws),
        "metabolic_rate": metabolic_rate,
        "productive_flow": productive_flow,
        "extractive_flow": extractive_flow,
        "speculator_net_delta": speculator_net_delta,
        "autocatalytic_closure": autocatalytic_closure,
        "total_wealth": float(nws.sum()),
        "alive": len(alive_nonstate),
        "alive_with_state": len(alive),
        "starved_cum": accum["starved_cum"],
        "births_cum": accum["births_cum"],
        "knowledge_lost_cum": accum["knowledge_lost_cum"],
        "cultural_diversity": cultural_diversity(agents),
        "cultural_breadth": cultural_breadth(agents),
        "total_debt": float(sum(a.debt for a in alive)),
        "debt_written_off": debt_written_off,
        "tax_collected": tax_collected,
        "wealth_by_type": {t.name: wealth_by_type[t] for t in Type},
        # Top-shares: state excluded by default; corrected variants added.
        "top1_share": top_k_share(nws, max(1, int(0.01 * len(nws)))),
        "top10_share": top_k_share(nws, max(1, int(0.1 * len(nws)))),
        "top01_share": top_k_share(nws, max(1, int(0.001 * len(nws)))),
        "top1_share_corrected": top_frac_share_corrected(
            nws, recent_deaths, tick, 0.01),
        "top10_share_corrected": top_frac_share_corrected(
            nws, recent_deaths, tick, 0.10),
        "state_wealth": float(state.wealth) if state else 0.0,
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def run(d: Dials, ticks: int = 300) -> list[dict]:
    rng = np.random.default_rng(d.seed)
    agents = make_initial_population(rng, d)
    history = []
    accum = {}
    for t in range(ticks):
        history.append(step(agents, d, rng, t, accum))
    return history


def run_multi(d: Dials, ticks: int = 300, seeds: int = 20) -> list[list[dict]]:
    runs = []
    for s in range(seeds):
        runs.append(run(replace(d, seed=s), ticks=ticks))
    return runs


def aggregate(runs: list[list[dict]], key: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    arr = np.array([[h[key] for h in run] for run in runs])  # (seeds, ticks)
    return arr.mean(0), np.percentile(arr, 25, 0), np.percentile(arr, 75, 0), arr.std(0)
