# Unequal Agents: state of the project

Last refreshed during the Path-C planning phase.

## What this project is

An agent-based simulation of UK wealth inequality, used to test
policy interventions on three structural outcomes: ownership
distribution, productive economic activity, and population survival.
The original inspiration was a Gary Stevenson / Gabriel Zucman
discussion of an inheritance cap.  The project began as a single
intuition-pump simulation and has grown into a four-paper
empirical-policy research programme.

## The intellectual arc

The project went through three phases:

**Phase 1 (round 1).**  Built the seven-class agent model
(WORKER, MAKER, EMPLOYER, LENDER, RENTIER, SPECULATOR, STATE), the
productive-flow share metric $\Phi$, the cultural-transmission
mechanism with bandwidth-limited skill transfer, the inheritance-cap
sweep, and the wealth-tax sweep.  Headline finding: a £5M cap on
inheritance raises the bottom-50% wealth share from 0% to 25%.
Produced the master paper plus three venue variants (JASSS, JEIC,
ALIFE) and one policy paper (cap, for Fiscal Studies).

**Phase 2 (round 2).**  Adversarial stress testing against simulated
Stewart and Hunt critiques.  Eight experiments: kill-switch
decomposition, WAS-calibrated baseline, capital flight, enforcement
friction, productive-class carve-out, equal-revenue head-to-head,
hybrid wealth tax sweep, and the loose-ends pack (flight on hybrid,
transition ramp, class-conditional hybrid, stacked policies).

The round-2 finding that changed the paper: enforcement friction
collapses the cap below 95% capture, but a recurrent wealth tax at
$\tau > r$ delivers the same distributional mechanism without the
fragility.  The cap is the limit of the wealth tax at $\tau \to 1$
applied once per lifetime; the recurrent version is what actually
works under realistic enforcement.

Produced: round-2 cap paper (cap_v2), wealth-tax paper recommending
5--10% above £10M, the political-economy strategy memo.

**Phase 3 (growth).**  Path-B: address the orthodox-Hunt critique
that the model has no growth term.  Added two productivity channels
(heterodox human-capital, orthodox capital-deepening) and a six-measure
growth portfolio (GMT, PT, CGDP, CI, MC, KS).  Robustness across four
productivity regimes, seven $\alpha$ values, and four capability
compositions.  20-seed bootstrap CIs.  1 tick = 1 year calibration
anchored on four UK 2008-2024 reference points.

Headline finding: across every measure other than CGDP-style aggregates
that count financial-sector compounding at face value, the wealth tax
raises growth by 9-15%.  The orthodox claim ``wealth tax depresses
growth'' is a measurement artefact: the $+5.76\%$ per-year status-quo
CGDP growth is the model's representation of the UK 2008-2024
financialisation pattern, in which GDP grew through financial-sector
compounding while productive output stagnated.

Produced: growth paper.

## Papers in current order of recommended submission

| paper | folder | pages | venue target | status |
|---|---|---|---|---|
| wealth tax | `papers/wealth_tax/` | 13 | Fiscal Studies | submission-ready |
| growth | `papers/growth/` | 15 | Fiscal Studies / JEEA | submission-ready |
| JEIC | `papers/jeic/` | ~25 | JEIC | round-2 ready |
| JASSS | `papers/jasss/` | ~22 | JASSS | round-2 ready |
| ALIFE | `papers/alife/` | ~20 | Artificial Life | round-2 ready |

The wealth-tax paper supersedes the round-1 cap paper and the round-2
cap_v2 paper for submission.  The cap papers are retained as the
intellectual trail showing how the wealth-tax recommendation was
derived from cap stress testing.

The growth paper is methodologically independent: it shows that the
wealth-tax-vs-status-quo choice is a choice about the growth measure.
The wealth-tax paper recommends the policy; the growth paper defends
the policy against the orthodox-growth attack.  Together they are
the round-3 fiscal-policy submission package.

## What still needs doing

**Path C: endogenous growth mechanisms.**  The current growth paper
shows level effects on PT and CI; it does not show sustained PT
growth-rate gains because the model is largely stationary in
productivity.  Path C extends the model with three mechanisms:

1. *C1 endogenous R&D*: a research activity that discovers new skill
dimensions, making PT growth non-stationary.  Hypothesis: wealth-tax
arms produce positive long-run PT growth while status-quo PT remains
stationary because the broader skill base sustains R&D.

2. *C2 mission-oriented public investment*: state revenue from the
wealth tax directed at capability-building, operationalising the
Mazzucato mission-orientation argument.

3. *C3 demand-composition effects*: bottom-50% has higher MPC than
top-1%; redistribution shifts demand toward productive sectors via
the Keynesian multiplier.

Detailed Path C planning document at `docs/PATH_C_PLAN.md`.

**Outstanding round-2 ports.**  The R2 findings (capital flight,
enforcement friction, hybrid recommendation) have not yet been
propagated back into the JEIC, JASSS, and ALIFE technical papers.
These could be done as light updates rather than rewrites.

**Communication piece.**  The original communication-piece script
(`src/elegant_demo.py`) was built around the round-1 cap headline.
A round-3 popular-press version anchored on the 5% wealth tax and
the GDP-is-an-artefact finding would benefit from the new framing.

## Where to look in the project

- `src/INDEX.md` -- catalogue of all simulation and analysis scripts
- `papers/INDEX.md` -- catalogue of papers and their relationships
- `review/INDEX.md` -- catalogue of round-1, round-2, and growth
  findings documents
- `docs/PATH_C_PLAN.md` -- detailed plan for Path-C extensions
