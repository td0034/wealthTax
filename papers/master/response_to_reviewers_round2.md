# Response to reviewers, Round 2

Thank you for the careful and detailed reviews. We have addressed every point.
A short response to each reviewer's blocking and major concerns follows.
The body of the manuscript has been re-edited to remove all references to
the review process itself, per the cross-cutting presentational concern.

## Cross-cutting concerns

**CC2-1 (consistency pass).** Verified the table data against
`out/data/scenarios_summary.json`, `out/data/policies_summary.json`, and
`out/data/policy_summary_n10k.json`. Updated all in-text numbers including:

- §5.6 "Three observations" prose (was: 77/77, 0.88, 49 vs 52, 0.007;
  now: 80/80, 0.54, 51 vs 57, 0.019)
- §5.7 scale-up paragraph collision: removed the stale paragraph entirely
- Billionaire-count figure caption (3 seeds → 10 seeds; 16 → 19; 100 → 97)
- §5.9 Pareto ratio (16 → 19; 600× → 2500×)
- Sankey caption (socialist Φ removed in favour of forward-pointer to Table 2)
- Conclusion finding count aligned with abstract

**CC2-2 (reviewer-facing scaffolding).** Removed every reference to
"a reviewer pointed out," "the JEIC/JASSS/ALIFE reviewer," and the internal
revision codes (CC-1, CC-2, AL-2 etc) from the manuscript body. The
intellectual moves the revision makes are now presented as the paper's own
reasoning, not as rebuttals. The scaffolding survives here in this letter.

## JASSS-specific

**J2-1 (repositioning lead).** §6.4 (positioning for publication) now leads
the JASSS recommendation with (i) productive-flow share + Sankey, (ii)
state-excluded phase portrait, (iii) the clean factorial showing three
distinct policy targets answering to three distinct levers. The retracted
state-spending claim no longer appears as a lead.

**J2-2 (Φ accrual symmetry).** Adopted option (a): speculator positive
returns now accrue to F_ext on the same footing as rentier capital return.
Documented in §3.3. The symmetry is now consistent: both rentier capital
return and speculator gains are intra-stock wealth creation accruing to an
extractive class. Reran scenarios and policies under the symmetric
definition; Phi values move by ~0.005–0.05 depending on speculator activity.

**J2-3 (0.4 employer markup coefficient).** Documented in §3.3: 40% of the
gross employer markup is treated as productive value-add (organising work),
60% as zero-sum capture from worker output. Stated as a modelling choice.

**J2-4 (silhouette softening).** §5.1 now reports silhouettes for k=2, 3,
4, 5 explicitly (0.55, 0.55, 0.42, 0.32) and states that the data does not
prefer k=3 over k=2; the choice of three regimes is a theoretical
interpretation, not data-dictated.

## JEIC-specific

**E2-1 (calibration transfer).** This was the biggest substantive change.
We added §5.13 "Policy results at calibrated parameters" with a full table
of the 8-policy subset rerun at r=0.06, rent share 0.50 (the calibrated
configuration from §5.9). The headline result:

- **At default r=0.04 the top tier does not bind** (Zucman flat = Zucman
  progressive within seed noise)
- **At calibrated r=0.06 the top tier binds clearly**: Zucman progressive
  produces zero billionaires, Zucman flat leaves 46. The progressive form
  is the load-bearing instrument under realistic capital-return dynamics.

The τ-vs-r conclusion is preserved and becomes more salient: at calibrated
r=0.06 none of the modelled policies have τ > r at their lowest tier, so
all rely on cap-by-mortality at the lower bracket and the upper tiers
take on the cap-setting role. We present both default and calibrated
results and discuss which result should be considered the headline as a
function of which r is judged a fair representation of UK conditions.

**E2-2 (clean Spangler test).** Added the `inherit_from_class_prior` toggle
to make_agent (sim.py). Holds bandwidth-gating and class-bias persistence
intact; swaps only whether transmitted skill values are parent-derived or
drawn from the class-typical prior. The clean toggle gives:
default Gini 0.885 vs class-prior Gini 0.876, a small but consistent
partial reproduction of Spangler & Sarkar's direction (parent-derived
raises Gini relative to class prior). The earlier μ=1.0 arm is retained
for contrast with the warning that it confounds three mechanisms.

**E2-3 (citations at point of use).** Saez & Zucman 2016 cited next to
the WID targets in §5.9. Benhabib, Bisin & Zhu 2011 cited next to the
fixed-point derivation in §5.8.

## ALIFE-specific

**AL2-1 (per-capita discovery rate).** open_skills.py now computes
discoveries per agent-generation per class, normalised by class size.
Right panel of the open-skills figure shows per-capita rates: RENTIER
0.012, WORKER 0.009, MAKER 0.005. Rentiers discover at 1.3× the worker
rate per capita. The "wealthy lineages disproportionately discover" claim
now stands on per-capita evidence, not raw count.

**AL2-2 (elasticity rentier/speculator rows).** Reran elasticity at N=500
(population_scale=5) to get adequate sample size in rare classes. Table 6
now reports all six non-state classes. RENTIER R²=0.12 with all normalised
elasticities |η|≤0.10; the archetypal extractive-class skill-wealth
weakness is now documented directly.

**AL2-3 (title for ALIFE).** §6.4 explicitly notes that for an ALIFE
submission the title should replace "autocatalytic-closure" with
"productive-flow share" to reduce friction with the RAF-literate audience.
For JASSS/JEIC the current title is retained.

**AL2-4 (Vaesen sentence).** §5.4 now states the Vaesen et al. critique
in one sentence: the relevant population sizes in Henrich's Tasmania
analysis were not as different as the model required, weakening the
population-size-explains-loss inference.

## What changed in the model code

- `sim.py:144`: added `inherit_from_class_prior` Dial for the clean
  Spangler test
- `sim.py:243–262`: new code path for class-prior inheritance
- `sim.py:558`: speculator positive returns now added to
  `extractive_flow` (J2-2)
- `calibrated_policies.py`: new harness for the calibrated rerun
- `calibrated_scale_up.py`: new harness for the calibrated N=10k rerun
- `spangler.py`: now compares three arms (default, class_prior, mu=1.0)
- `open_skills.py`: per-capita discovery rate by class
- `elasticity.py`: N=500 for rentier/speculator sample size

## Numerical differences from round 1

Several Phi values shifted modestly (~0.005–0.05) due to J2-2; the
qualitative regime classification is unchanged. The §5.13 calibrated
rerun is genuinely new content and substantively changes the
top-tier-does-not-bind reading: that result is now scoped to default
parameters and reverses at calibrated parameters. We consider this the
most important new result of round 2.
