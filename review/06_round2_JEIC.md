# Referee report — JEIC (Round 2)

**Recommendation: Major revision** (round 1 was reject-and-resubmit). This is a
large improvement. The two structural objections I raised — the top-tier result
being a conditional tautology, and the regressive trap being a possible
mortality artefact — have been confronted directly: the first is now derived
analytically, and the second has been *retracted* after the authors found it
was a state-contamination artefact. I respect both moves. The paper is now in
revisable range for JEIC. Three substantive issues remain.

---

## 1. Round-1 concerns: status

- **Top-tier-does-not-bind is now an analytical result** (§5.8): the fixed
  point w* = τθ/(τ−r), defined for τ > r, with divergence for τ ≤ r, and a
  figure comparing prediction to simulation (`fixed_point.py`). This is exactly
  the move from "symptom" to "mechanism" I asked for, and the τ-vs-r framing is
  a genuine economic result that engages the r > g tradition properly. The
  derivation is correct as a first-order single-agent characterisation.

- **Regressive trap retracted** (§5.12). The honest finding is the opposite:
  top-1% share falls monotonically in the rate at every threshold, most
  strongly at the £10M threshold (0.18 → 0.04). The authors correctly attribute
  the original error to State contamination rather than (my guess) mortality —
  and the mortality-corrected metric, now actually implemented, moves the
  number by < 0.005, which settles the question. Good science.

- **Spangler & Sarkar is now a direct empirical test** (§5.6), not a feature
  list, and returns the opposite of their result — discussed with appropriate
  care. See §3 below for a caveat on how the test was implemented.

## 2. Blocking: the policy table prose contradicts the policy table

The JEIC-critical table is Table 5, and the three numbered "observations"
beneath it are stale (77/77, top-10 0.88, hoard 49 vs tory 52, reform 0.007)
where the table and the regenerated data say 80/80, 0.54, 51 vs 57, 0.020.
Adjacent contradictions also appear in §5.7. See `04_round2_overview.md`. For an
economics audience this is fatal on contact: the first thing a JEIC referee
does is check whether the prose matches the tables. Fix comprehensively.

## 3. The calibration does not transfer to the policy claims

This is the most important *remaining* substantive issue. §5.9 reports a partial
calibration: a UK-Pareto-slope match of −0.673 is achievable at **r = 0.06,
rent share 0.50, inheritance tax 0.40**. But every policy result in the paper
(Tables 5, 7, the fixed-point reading, the τ-vs-r conclusion) is run at the
**default r = 0.04, rent 0.35**. So the configuration that earns the £ axis is
*not* the configuration in which the policy claims are made. Two consequences:

1. The statement (§6.6) that the calibration "backs the £10M anchor in
   particular" is not supported: the £10M anchor lives in the default-parameter
   runs, which were not calibrated. You have calibrated configuration A and
   drawn policy conclusions from configuration B.

2. The τ-vs-r conclusion (§5.8, conclusion) — "none of the eleven proposals
   have τ > r at their lowest tier, so all rely on cap-by-mortality" — is
   *parameter-dependent on the very quantity (r) that calibration moved*. At
   the calibrated r = 0.06, the gap between nominal wealth-tax rates and r is
   even wider, so the qualitative claim survives; but the paper should make the
   τ-vs-r argument *at the calibrated r*, not at the default, and say which r it
   means each time. As written, r = 0.04 is doing load-bearing work in a
   headline claim while the calibration says r should be 0.06.

Additionally: the calibrated config keeps only **26% of the population alive**
(§5.9, acknowledged). A configuration that matches the wealth tail only by
killing three-quarters of the population is not a calibration a JEIC referee
will accept as validating the model's demographic behaviour. The honest reading
is that the model cannot currently match tail-steepness and survival
simultaneously — the authors say this — which means the calibration is better
described as "a sensitivity result showing the slope is *reachable*" than as
"a calibration backing the policy claims." Reframe accordingly, and either (a)
run the policy suite at the calibrated parameters and report how much the policy
conclusions move, or (b) state explicitly that policy results are at default
parameters and the calibration is illustrative only. Option (a) is the
defensible JEIC paper.

## 4. The Spangler test conflates two mechanisms

§5.6 implements "skill inheritance off" as `skill_mutation_rate μ = 1.0` (full
fresh redraw each generation) versus the default μ = 0.05. But μ = 1.0 does not
isolate *skill inheritance*; it simultaneously destroys (i) the transmission of
parental skill, (ii) the wealth-coupled *bandwidth* mechanism that is the
paper's own novelty (a fully redrawn child has no inherited dimensions to gate),
and (iii) the class-typical skill biases' persistence across generations. So
"skill inheritance lowers Gini in our model, contra Spangler & Sarkar" is
confounded: the μ = 1.0 arm changes more than inheritance. A clean test would
hold bandwidth and class-bias fixed and toggle only whether the *transmitted
values* come from the parent vs a class-typical prior. As it stands the
"opposite result" claim is interesting but not yet a clean refutation/contrast,
and Spangler & Sarkar referees (this is their home venue) will catch it. Either
implement the clean toggle or downgrade the claim to "under a coarse
inheritance on/off proxy, we do not reproduce their direction; a cleaner
isolation is future work."

## 5. Minor

- The fixed-point figure reports "predicted 300, observed 308" etc. in model
  units while the surrounding text mixes model units and pounds freely.
  State units explicitly at each comparison.
- §5.8's "boundary case 0.04·£100M/(0.04−0.04) → ∞" is a correct but awkward
  way to make the point; consider just stating that the tier is inactive
  because τ = r there.
- Benhabib, Bisin & Zhu (2011) and Saez & Zucman (2016) — were these brought
  into the *results* discussion as I asked? They belong next to the fixed-point
  derivation (Benhabib et al. is the rigorous bequest-and-tail analogue) and
  the calibration (Saez & Zucman for the WID targets). Currently I see WID
  targets used but not cited to Saez & Zucman at the point of use.
- Remove reviewer-facing scaffolding (see overview).

## 6. Verdict

The structural problems are solved; the analytical fixed point is a real
contribution and the retraction is handled with integrity. What blocks
acceptance is (a) the table/prose contradictions, (b) the calibration-transfer
gap, which currently leaves the £-denominated policy claims resting on an
uncalibrated parameter set, and (c) the confounded Spangler test. All three are
addressable within a revision. **Major revision**, and I would be glad to see
it again.
