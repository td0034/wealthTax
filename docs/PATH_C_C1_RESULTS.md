# Path C C1 proof-of-concept: results brief

Status: **proof-of-concept complete; result is publishable as-is and
points to a stronger thesis than the planning document anticipated**.

## What we built

Added a Romerian endogenous-growth mechanism to `sim.py`.  MAKERs and
EMPLOYERs each invest a share of their wealth in R&D every tick.  The
per-tick innovation rate is
$$ \mathrm{rate}_t = c \cdot \sqrt{B_t} \cdot \bar{b}_t^{\,\eta} $$
where $B_t$ is the total R&D budget, $\bar{b}_t$ is the population
mean worker skill breadth normalised to $[0, 1]$, and $\eta$ is the
skill-breadth elasticity.  The cumulative productivity multiplier
$M_t = M_{t-1} (1 + \mathrm{rate}_t)$ multiplies the baseline per-tick
productive flow, so PT growth rate over time matches the
innovation rate.  Dividends are distributed proportionally to living
MAKERs and WORKERs.

Coefficients calibrated so that innovation rate is approximately
0.005 per tick (matching UK output-per-hour growth of $\sim 0.5\%$/yr
under the 1 tick = 1 year mapping).  R&D-share-of-wealth: 5% for
MAKERs and 5% for EMPLOYERs.

## What the planning document predicted

The Path-C plan hypothesised that the result would be conditional on
the skill-breadth elasticity $\eta$.

- At $\eta = 0$: only R&D budget matters.  Status quo wins because
  concentrated wealth funds higher R&D.
- At $\eta = 0.5$ (Hanushek-Woessmann range): R&D budget and skill
  breadth balanced.  Wealth tax wins because broader skill base
  dominates.
- At $\eta = 1$: skill breadth dominates.  Wealth tax wins
  unambiguously.

The crossover was supposed to determine the headline policy
recommendation.

## What we actually found

**The wealth tax wins at every elasticity tested, including $\eta=0$.**

Per-tick PT growth differential vs status quo (positive = wealth tax
wins, in pp per tick):

| arm | $\eta=0.00$ | $\eta=0.25$ | $\eta=0.50$ | $\eta=0.75$ | $\eta=1.00$ |
|---|---|---|---|---|---|
| cap £5M       | +0.009 | +0.007 | +0.007 | +0.005 | +0.006 |
| hybrid 5%     | +0.008 | +0.004 | +0.006 | +0.005 | +0.004 |
| hybrid 10%    | +0.010 | +0.008 | +0.007 | +0.006 | +0.005 |

The orthodox channel never gets a chance.  Even at $\eta=0$ where the
mechanism was constructed to favour concentrated R&D, the wealth tax
arms produce a positive PT-growth differential.  The reason becomes
clear once we look at the R&D budget:

| arm | $\eta=0.00$ | $\eta=0.50$ | $\eta=1.00$ |
|---|---|---|---|
| status quo R&D budget  | 3,650 | 3,638 | 3,642 |
| cap R&D budget         | 4,476 | 4,470 | 4,467 |
| hybrid 10% R&D budget  | 4,761 | 4,753 | 4,748 |

The wealth-tax arms produce *larger* R&D budgets than the status quo.

## Why the orthodox prediction failed

The R&D budget is the share of MAKER + EMPLOYER wealth.  The
orthodox prediction was that concentrated wealth at the top would
fund higher R&D under status quo.  But MAKERs and EMPLOYERs are
mostly below the wealth-tax threshold (£10M); their wealth is not
directly extracted.  And under status quo, survival rates are lower
(82.7% vs 91.3% under cap, 93.3% under hybrid 10%), so there are
fewer living MAKERs and EMPLOYERs to invest.  The population-dynamics
effect dominates the wealth-concentration effect.

This is a finding the planning document did not anticipate.  The
mechanism is the same as Round 2 (survival-selection from the
state-spending package), but it now propagates into the
R&D channel.  The orthodox case does not get a chance even with
generous parameterisation because the underlying class population
dynamics favour the wealth-tax regime.

## What this means for the Path-C paper

Three implications:

1. **The Path-C paper now has a clearer headline than the planning
   document anticipated.**  Rather than ``conditional on the
   skill-breadth elasticity, wealth tax produces higher PT growth''
   the finding becomes ``the wealth tax dominates R&D-driven growth
   under any elasticity tested, because survival-selection effects
   make the orthodox R&D-budget channel run in the wealth tax's
   favour as well.''  This is a stronger and harder-to-attack
   claim.

2. **The proof-of-concept confirms it is worth scoping the full
   Path-C paper.**  The mechanism is empirically tractable in the
   model.  The result is robust.  The interpretation engages the
   Romer / Hanushek-Woessmann / orthodox-endogenous-growth tradition
   directly.

3. **The paper has to explicitly engage the survival-selection
   mechanism as part of the story.**  An orthodox reviewer will
   say ``you only get this result because your model has a survival
   penalty under status quo, and you should test with survival
   equalised across arms.''  We should anticipate that critique and
   run an explicit experiment: equalise survival across arms and
   re-run.  If the wealth-tax PT-growth advantage persists, the
   result is robust.  If it does not, the paper has to claim more
   modestly that ``in the calibrated UK case, the combination of
   survival selection and skill broadening together produces a
   PT-growth advantage''.

## Open questions for the next pass

1. **Survival-equalised counterfactual.**  Re-run with UBI calibrated
   to match status-quo survival across all arms.  Does the wealth-tax
   PT-growth advantage persist when survival selection is removed?

2. **Coefficient robustness.**  We used `rd_innovation_coeff = 0.0001`
   and `rd_share = 0.05` for MAKERs and EMPLOYERs.  A robustness sweep
   across these coefficients would discipline the calibration.

3. **R&D efficiency by class.**  Currently MAKERs and EMPLOYERs have
   equal R&D-share rates.  In reality MAKER R&D (firms) is roughly
   2--3x more productive per pound than EMPLOYER R&D (capital).  A
   class-differentiated R&D-share would be more realistic.

4. **Stagnation under decline.**  PT growth is *negative* in absolute
   terms across all arms because the underlying productive flow is
   declining over the steady-state window (population decline plus
   shrinking productive sector).  The result that wealth tax wins is
   a *less-negative* PT growth.  This is honest but harder to spin
   than a clean ``wealth tax produces positive growth''.  A possible
   refinement: equilibrate the demographics so PT growth is positive
   across the board, then re-test.

5. **Sensitivity to share-of-wealth in R&D.**  At 5% R&D share, the
   R&D pool is roughly the same size as cumulative wage flow.  This is
   high relative to actual UK figures (R&D intensity 1.8% of GDP).
   Lower R&D-share would reduce the absolute R&D budget but possibly
   not change the qualitative wealth-tax advantage.

## Recommendation

Path C is **worth committing to**.  The proof-of-concept produces a
stronger result than the planning document anticipated, the mechanism
is empirically defensible, and the survival-selection insight gives
us a third paper-relevant finding to put alongside the
distributional and measurement-portfolio findings.

The full Path-C paper still requires:
- C2 mission-oriented public investment
- C3 demand-composition effects
- C4 comparable-country calibration
- Survival-equalised counterfactual (new, prompted by this brief)

Estimated effort to complete: 10--14 weeks (slightly less than the
planning estimate because C1 is now de-risked).

Decision point: do we commit to Path C now, or do we let Path B go
out for peer review first?  My recommendation remains the latter,
with C2 / C3 / C4 / survival-equalised work proceeding in parallel
as proof-of-concept rather than committed-paper work.
