# Referee report — JASSS (Round 2)

**Recommendation: Minor-to-major revision.** A clear advance on the previous
version. My three round-1 concerns (Φ construction, the definitional
state-spending result, "by-inspection" clustering) are all addressed in
substance and in code. What remains is a numerical-consistency pass, a
repositioning forced by the authors' own honest retraction, and two residual
modelling-justification points on Φ.

---

## 1. Round-1 concerns: status

- **Φ now defined symmetrically (CC-2).** Verified in `sim.py`: maker
  value-add (`output − inputs`, line 466) and employer markup (line 490) are
  now in the numerator; rent, interest, and capital return in the denominator.
  This directly answers my objection that the numerator was "wages only" while
  the denominator counted rentier wealth-creation. Good.

- **The state-spending result is no longer definitional.** The clean factorial
  (Table 4) separates the three levers, and the headline is now correctly
  restated: spending raises *alive* by ~40% but barely moves Φ (0.369 vs
  0.364). This is exactly the honest version of the result and I am glad to see
  it. It is a *better* finding than the original overclaim.

- **Regimes now from k-means with a silhouette score**, replacing "by
  inspection." Survival curves added per my request.

These are real fixes. Thank you for taking them seriously.

## 2. Blocking issue: internal numerical consistency

See `04_round2_overview.md` §"blocking problem." For JASSS specifically, the
stale prose sits on the policy comparison (§5.6) and the phase/flow narrative
(§5.3 socialist Φ = 0.81 vs Table 2's 0.890). JASSS readers will be reading the
prose as the claim. Reconcile every in-text number with the regenerated tables
before this can go further. I verified Table 5 is the authoritative set against
`out/data/policies_summary.json`.

## 3. The JASSS positioning is now self-contradictory and must change

§6.4 still recommends leading the JASSS submission with "the autocatalytic-
closure metric, the phase portrait, and **the state-spending result**." But the
revision has just demonstrated (Table 4, §5.2) that the state-spending result
*does not move Φ* and was previously overclaimed. You cannot lead a JASSS paper
with a result you retract two sections earlier. Repoint: the natural JASSS lead
is now **(i) the productive-flow-share metric and the Sankey visualisation**
(still the single best artefact in the paper), **(ii) the phase portrait under
proper state-excluded Gini**, and **(iii) the clean factorial showing that
alive, Gini, and Φ are three distinct targets answering to three distinct
levers**. That last point is, post-revision, the paper's actual thesis (you say
so yourself in the conclusion) and it is a natural JASSS contribution.

## 4. Residual modelling-justification issues on Φ

The symmetric redefinition is a real improvement but introduces two choices
that now need defending in the text:

1. **Speculation is excluded from Φ entirely; rentier capital return is
   not** (`sim.py:538–548` vs `:536`). The stated reason — speculation is
   "intra-stock volatility ... not an inter-class accrual" — applies *equally*
   to rentier capital return, which the code explicitly counts as extractive
   while calling it "intra-stock creation." Both are wealth changing on an
   agent's own stock with no counterparty. Treating one as extraction and
   dropping the other is the kind of asymmetry I flagged in round 1, now
   relocated rather than removed. Either count both as accrual to their class
   (rentier→extractive, speculator→extractive) or exclude both. The current
   split needs a principled justification or it will read as tuned.

2. **The employer-markup contribution carries a bare coefficient of 0.4**
   (`sim.py:488`, `markup_value = worker_output * d.employer_markup * 0.4`),
   undocumented in the paper. Since this term now enters the headline metric,
   the 0.4 must be stated and motivated in §3.3.

## 5. The k=3 regime claim is weaker than presented

The paper reports silhouette 0.55 for k=3 — but also 0.55 for k=2 (§5.1). A tie
between k=2 and k=3 does *not* support "three clearly separated regions"; on the
silhouette criterion two regions fit equally well. The choice of three is a
theoretical/interpretive decision (collapse vs extractive-equilibrium is a
meaningful distinction even if the data only weakly separates them), and that
is fine — but say so honestly rather than presenting silhouette as deciding for
three. With 13 points, any clustering claim is fragile; consider softening
"clearly separated" to "interpretable as three regimes, with the collapse/
extractive boundary the least sharp."

## 6. Minor

- Remove the reviewer-facing scaffolding ("a reviewer pointed out," "CC-1,"
  "CC-2"); see overview.
- "meta" column in Table 5 is undefined (metabolic rate?). Label it.
- Bertotti & Modanese now cited (`bertotti2018modanese`) — good, this was a
  round-1 gap. Confirm the bib entry exists and compiles; it is referenced in
  §6.6 but I did not see it in the round-1 `references.bib`.
- ODD appendix is welcome and adequate for JASSS at working-paper stage; the
  promise of a full ODD+D supplement should be kept for final submission.

## 7. Verdict

The conceptual objections from round 1 are resolved. What stands between this
and acceptance is (a) a numerical-consistency pass, (b) repositioning the JASSS
lead away from the retracted state-spending claim, and (c) two short
justifications on the Φ accrual choices. If the consistency pass is clean I
would be comfortable at **minor revision**; given the number of stale figures
I'll formally say **minor-to-major**.
