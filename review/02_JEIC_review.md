# Referee report — JEIC

**Manuscript:** *Unequal Agents: An autocatalytic-closure agent-based model
of wealth inequality, cultural transmission, and the design of progressive
wealth taxes*

**Venue framing (per authors):** lead with the inheritance trapdoor, the
top-tier-does-not-bind result, and the wealth-tax design factorisation;
position directly against Spangler & Sarkar (2022) and Cardoso et al. (2025).

**Recommendation: Reject and resubmit.** The economic-design claims are the
most quotable in the paper and also the least defensible as currently
evidenced. I would welcome a resubmission, but the present version makes
quantitative policy claims that the model, by its own admission, cannot
support without calibration and without fixing two confounds.

---

## 1. Overall assessment

JEIC is the natural competitive ground for this paper because Spangler &
Sarkar (2022) appeared here and is the closest neighbour. The authors know
this and engage it. The differentiation claims (multi-channel extraction;
bandwidth-coupled transmission; closure metric vs terminal Gini) are real and
the engagement with Cardoso et al. (2025) is appropriate.

But the three results the authors want to lead with at JEIC are economic-design
claims with numbers attached — "£10M is the rightmost viable threshold," "the
top tier is mechanically idle," "low-threshold high-rate taxes are
regressive." A JEIC readership will hold these to an economics standard, and
at that standard three problems are disqualifying in the current draft:

1. Every monetary claim rests on an **arbitrary, unfitted unit mapping**
   (1 unit = £100k).
2. The headline distributional results are **contaminated by the State agent**
   sitting in the percentile statistics.
3. The most striking new result, the "regressive trap," is **plausibly the
   same mortality artefact** the authors themselves flag for Gini — re-badged.

## 2. Major issues

### 2.1 The policy conclusions are non-identified because the £ scale is uncalibrated

The paper sets 1 model unit = £100,000 "as a convenience for labelling and not
a calibration" (§3.4), and then builds its central political conclusion on
threshold *levels* expressed in pounds: "£10M is approximately the rightmost
threshold at which a wealth tax remains both progressive in effect and viable"
(Conclusion, §5.6, §5.8). These two statements are in direct tension. If the
unit mapping is arbitrary, then "£10M" is arbitrary: rescale the unit and the
"rightmost viable threshold" moves with it. The threshold result is a
statement about a dimensionless ratio (threshold / typical agent wealth in the
model), dressed up in pounds it has not earned.

The §5.9 Pareto check makes the problem concrete and the authors are
commendably honest about it: the model's top-tail slope is ≈ −0.07 to −0.26
against a UK fit of −0.706, the top fortune is an order of magnitude too small,
and the per-capita billionaire density is ~600× too high. A model whose wealth
distribution is wrong in the tail by these margins cannot then tell us that
£10M specifically is the policy-relevant kink. **The threshold-dominates-rate
finding is interesting as a qualitative mechanism; it is not yet a number.**

*Required for resubmission:* either (a) calibrate at least one scenario to
WID/SCF UK wealth-share data (as the authors themselves recommend in §5.9 and
`FINDINGS.md`) so the £ axis means something, or (b) strip the pound labels
entirely and state the result dimensionlessly (threshold as a percentile of
the model wealth distribution, or as a multiple of mean/median wealth). Option
(b) is achievable immediately and would make the qualitative claim publishable;
option (a) is what would make it a genuine policy contribution.

### 2.2 The "top tier does not bind" result is arithmetic, not emergent

Sweep B shows column-identical alive/closure surfaces in (bottom rate, top
rate), and the Zucman flat ≡ progressive equivalence shows identical outcomes
(§5.6, §5.7). The stated mechanism is correct: under a 2% tax above £10M, no
agent ever reaches the £1B tier, so the £1B marginal rate multiplies
`max(0, w − θ) = 0` for every agent (see `sim.py` line 572–574). But that
makes the result a *tautology conditional on the wealth ceiling*: any tier
whose threshold exceeds the post-tax maximum wealth contributes exactly zero,
by construction, with zero variance. "Indistinguishable steady states
(77 vs 77)" is not an empirical discovery about equilibria; it is the
statement "no agent crossed £100M," which the authors confirm directly
(top agent ≈ £270M).

The economically interesting question — and the one JEIC will want — is *why*
the 2% lower tier caps the maximum at ≈ £270M, i.e. the relationship between
the lower-bracket rate, the capital-return rate r, and the resulting
stationary top wealth. That is a tractable, near-analytical question
(a tax-adjusted r vs g condition for the top agent's stock) and it would turn
a tautology into a result. Right now the paper reports the symptom and skips
the mechanism that a JEIC audience would actually find novel relative to
Piketty & Saez (2013) and Benhabib, Bisin & Zhu (2011) — both relevant here,
the latter currently uncited in the text.

### 2.3 The "regressive trap" is confounded with mortality — the authors' own caveat applied to their best result

This is the most serious issue. The paper's cleanest new claim (§5.11) is that
at a £1M threshold, raising the rate to 8% *increases* top-1% share from 0.37
to 0.84 — the tax made the top richer in relative terms. The stated mechanism
(§5.11) is: "the upper-middle and middle classes are charged a high effective
rate they cannot service, lose net wealth faster ... and concentrate the
surviving wealth at the top." That is *mortality*. The middle class is being
killed (agents starve when they cannot service charges; `sim.py` lines 478–491),
and top-1% **share** rises because the denominator collapses.

But this is exactly the "mortality-blind Gini" confound the authors identify
in §5.4 and recommend correcting with a mortality-adjusted measure. Top-1%
*share* is just as mortality-blind as Gini: both are computed over survivors
(`top_k_share` over the living net-worth array, line 650). The regressive-trap
result therefore needs the same correction the authors prescribe for Gini, and
until it gets one, we cannot distinguish "the tax enriched the top" from "the
tax killed the middle and the top is what's left." These have opposite policy
implications. The result is potentially the paper's best, which is precisely
why it must be shown on a mortality-corrected share (over alive ∪
recently-deceased) and with the State excluded.

### 2.4 The State contaminates every distributional table

top10 share of 0.88–0.99 and Gini of 0.86–0.93 across Table 4 are reported
with the State in the population, and the State's wealth column (16,300–39,700
units) shows it is the richest single agent in every spend/hoard policy. The
authors concede this (§7.2) but claim "qualitative findings unaffected." For
JEIC that claim must be demonstrated, not asserted, because the lead results
here *are* the distributional ones. In particular the regressive-trap (§2.3
above) and the zucman_hoard "tax-without-spending" comparison (§5.6) both turn
on share statistics that the State could be driving. Re-run with the State
excluded from all percentile/Gini/share metrics before resubmission. This is
cheap and non-negotiable for this venue.

### 2.5 Tangled factorial in the policy comparison

As `FINDINGS.md` candidly notes, the spending package (UBI 0.4 + employs 0.3 +
buys 5.0) and the inheritance tax (held at 0.4 across Zucman variants) are
*bundled* with the tax schedule across policies. The "Zucman = Warren =
Piketty" convergence "partly reflects the spending package doing the heavy
lifting." A JEIC paper claiming to *factorise* wealth-tax design (the stated
lead contribution) cannot then leave the design tangled with a fixed spending
bundle. The clean experiment is a full factorial of (tax schedule) ×
(spending package) × (inheritance rate); at minimum, hold spending and
inheritance genuinely fixed and vary only the schedule, and say so explicitly
in the table caption.

## 3. Minor issues

- **Statistical claims.** "Identical," "indistinguishable," "column-identical"
  appear repeatedly with 3 (or 2) seeds and no test. Either report
  bootstrap CIs or soften to "within seed noise (n=3)."
- **Inheritance bandwidth saturation** (`make_agent`, line 221–225): with
  defaults b0 = 0.5, bw = 0.5, the wealth term `bw·(w/100)` reaches the cap of
  5 dimensions for any parent above ~500 units. The "bandwidth scales with
  wealth" coupling is therefore active only across the poor-to-modest range
  and saturates immediately above it. This bears on the inheritance-trapdoor
  interpretation and should be stated.
- **§5.5 inheritance trapdoor** is real and the cleanest *qualitative* result
  in the economic set, but it is also the one the authors' own lit review
  (Piketty & Saez 2013; Benhabib et al. 2011) says is analytically known. Lead
  with it as a vivid ABM demonstration, not as a discovery, and cite the
  analytical precedent in the *result* section, not only in related work.
- **Norway calibration.** `norway_actual` with a 1% tax above 1.3 units
  (= £130k) is a very different instrument from Norway's ~1% net-wealth tax
  with a ~NOK 1.7M floor; check the threshold mapping, it looks off by orders
  of magnitude relative to the others.

## 4. References

- `benhabib2011distribution` and `saez2016wealth` are in the `.bib` but
  **uncited in the text** despite being directly on point for §2.2 and §5.9.
  Both belong in the results discussion, not just the bibliography.
- The engagement with Spangler & Sarkar (2022) is adequate but stays at the
  level of feature lists ("we add channels; they have a Carnegie effect"). A
  JEIC referee wants a *result* comparison: do you reproduce their finding that
  skill inheritance raises inequality? You have the machinery to test it
  directly; please do.
- `pagliarini2017agent` is cited only to argue JEIC accepts calibrated ABMs —
  which rather underlines that this paper is *not* calibrated. Either calibrate
  or drop the appeal to precedent.

## 5. Verdict

The economic-design results are the paper's most marketable and its most
fragile. As written, the threshold result is unidentified (uncalibrated
scale), the top-tier result is a conditional tautology, the regressive-trap is
confounded with mortality, and the distributional tables include the State.
Each is fixable, and the underlying mechanisms (lower-bracket placement
dominating top-rate steepness; tax-without-recycling being wasted) are worth
publishing once shown cleanly and dimensionlessly. I would read a resubmission
with interest. **Reject and resubmit.**
