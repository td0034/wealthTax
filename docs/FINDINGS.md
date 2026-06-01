# Unequal Agents — v1 findings

State as of 2026-05-28. 13 scenarios × 8 seeds × 250 ticks plus five 2D
parameter sweeps (9×9 × 3 seeds × 200 ticks each). Plots in `out/`.

## The phase portrait

A 3D trajectory plot in (Gini, autocatalytic closure, alive) — see
`out/phase3d_trajectories.png` and shadow plots in `out/phase3d_shadows.png`
— makes the qualitative structure visible at a glance. Three regimes:

| Regime | Scenarios | Closure | Alive |
|---|---|---|---|
| **Viable autocatalytic** | nordic, socialist, tax_and_spend, maker_economy, inheritance_break_ubi | 0.41–0.81 | 67–100 |
| **Extractive equilibrium** | current_world, memory_*, creditless | 0.00–0.01 | 43–77 |
| **Collapse** | stevenson_world, feudal, pure_speculation, inheritance_break | 0.00 | 1–18 |

Closure ≈ 0 is the death sentence. Once productive flow stops dominating,
the population follows within ~100 ticks.

## Three findings worth defending

### 1. State *spending* (not state revenue) is what flips the regime

The `tax_vs_ubi` sweep (baseline includes state-employs + tax-progressivity)
shows max autocatalytic closure (0.498) at full progressive tax + *moderate*
UBI 0.188 — not at max UBI. Beyond ~0.2 UBI, closure *falls* because cash
handouts bypass productive transformation.

In `state_action` (varying state employment fraction × state purchases of
maker output), closure ranges 0.24–0.37; the highest point is *low employment
+ high direct purchasing*. Direct demand for maker output is the strongest
single state lever for the closure metric.

This sharpens the v0 "tax-and-UBI is the highest-Gini" puzzle into a positive
result: revenue alone hoards in the state; cash redistribution alone passes
through extractive channels; **buying productive output is what makes the
system autocatalytic**.

Lit position: kinetic-tax ABMs (Bertotti & Modanese; Cardoso, Gonçalves &
Iglesias 2025) already show that *how* the state spends matters more than
how much it taxes. Our contribution is the metric — closure as a continuous,
per-tick gauge of the spending-mode effect — not the policy result.

### 2. Inheritance reform without UBI is a trapdoor

The `inheritance_x_ubi` sweep is the headline phase diagram. At inheritance
tax = 1.0 and UBI = 0, only 2/100 agents survive 200 ticks — children born
with zero wealth starve before earning. Add UBI 1.5 and survival jumps to 95
*at the same inheritance tax rate*. The two dials are not substitutes;
inheritance reform conditionally requires a safety net.

The Gini surface across this sweep peaks (0.948) at moderate inheritance tax
+ no UBI, and falls to 0.498 at full inheritance tax + no UBI — but the
"equal" corner has 2 alive. Standard Gini is mortality-blind: extreme
extraction can *look* egalitarian because it culls the bottom tail. This
result also appears in `rent_vs_r`: max Gini is in the moderate-rent
high-r corner; the extreme-rent corner has lower measured Gini but kills
60+ agents. **Without a mortality correction, Gini misrepresents extreme
regimes.** Worth its own short methodological note.

Lit position: optimal-inheritance theory (Piketty & Saez 2013) discusses
this analytically. Spangler & Sarkar (2022, JEIC) — our closest neighbour —
does estate tax + skill inheritance in an ABM. Differentiator: we couple
inheritance to a separate safety-net lever and visualise the trapdoor in
phase space; they study revenue/Carnegie effects in isolation.

### 3. Cultural transmission alone does not equalise wealth

The `memory` sweep (memory_bandwidth_base × memory_bandwidth_wealth_scale)
shows cultural breadth swinging from 1.3 to 5.0 across the grid — a 4×
range. Gini moves between 0.838 and 0.909 — a 7% range. **The wealth
distribution is robust to who-knows-what.** Equalising cultural transmission
(`memory_equalised` scenario: base=1.0, wealth_scale=0) raises breadth to
5.0 but leaves Gini at 0.92.

This is the *negative* finding the project most needs. The supervisor's
mechanism (bandwidth-coupled-to-wealth) reproduces well: in `memory_starved`
(low base + high wealth-scale) only the wealthy preserve knowledge, breadth
falls to 1.8. But cultural concentration is downstream of wealth
concentration, not the cause. **The political claim "cultural inequality
mirrors wealth inequality" is correct, but the causal arrow runs only one
way in this model.**

Lit position: no published ABM couples bandwidth (not target) to wealth.
Lewis & Laland 2012 shows fidelity drives cumulative culture; Henrich 2004
shows population size caps it. We add: *intra-population wealth dispersion*
caps it. The mechanism is novel; the wealth-irrelevance result is the
counter-intuitive finding worth publishing.

## Other things worth recording

- **`feudal`** (high rent + high r + memory tied to wealth) is a robust
  collapse attractor: 12/100 alive, closure 0.000, with cultural breadth 3.0
  because the surviving wealthy preserve their narrower skill set. A clean
  demonstration that extraction kills both the economy and the
  cultural commons.

- **`pure_speculation`** halves metabolic rate (16 vs 37 baseline) and
  drives closure to 0. The speculator class is a value extractor at
  the population scale even when individuals win.

- **`creditless`** (no debt allowed) keeps Gini at 0.85 and alive at 50.
  Banning debt does not help — workers can't smooth consumption shocks and
  starve in dry weeks. Credit is a symptom; removing it kills the patient.

- **`memory_equalised`** has the *highest* final Gini in the sweep (0.92
  vs 0.86–0.90). Counterintuitive: when everyone has full skills, output is
  higher and the extractive channels have *more* to skim. Production
  without redistribution feeds the rentier class.

## Where this should be sent

From the lit review (Spangler & Sarkar 2022 is the closest neighbour;
Cardoso et al. 2025 is the closest recent finding; autocatalytic-closure
metric and wealth-bandwidth coupling are the novel components):

- **Paper 1 — JASSS.** "Autocatalytic closure as a measure of economic
  viability: a stylised ABM." Lead with the metric + phase portrait +
  state-spending finding. JASSS reads political framing fluently.
  Length 8–10k words.

- **Paper 2 — JEIC.** "Inheritance reform without redistribution: a
  trapdoor in an agent-based wealth economy." The
  inheritance×UBI phase diagram + mortality-blindness-of-Gini caveat.
  Direct engagement with Spangler & Sarkar; positions against the
  optimal-tax-theory literature. 8–12k words.

- **Paper 3 — ALIFE 2026 / Artificial Life.** "Wealth-coupled cultural
  transmission and the asymmetry between cultural and economic equality."
  Lead with the bandwidth mechanism and the negative wealth-equalisation
  result. Closest to the supervisor's published interests. 8 pages
  (conference) / 12–20 (journal).

Drop the "extending Ikegami" framing — lit review found no Ikegami-lab
work on economy. Reframe as "alife sensibility" or cite Hashimoto, Oka
& Ikegami 2019 only as a methodological cousin.

## What this model still cannot do

- No spatial structure (no neighbourhood effects, no labour markets with
  geographic friction).
- No firm formation/dissolution (employer count is fixed).
- State has no debt — can't model fiscal crisis.
- Speculator dynamics are toy (Gaussian return). Bubbles/crashes don't appear.
- Skills are a flat 5-vector — no hierarchy, no complementarity, no
  innovation (no new skill dimensions can ever appear).
- Lender deposit mechanism is mechanical; no shadow-banking, no derivatives.
- Calibration: dial values are stylised, not fitted. Magnitudes shouldn't
  be quoted as predictions.

## Wealth-tax extension (2026-05-28, evening)

Added a stacked-marginal progressive wealth tax (`wealth_tax_tiers` dial),
mapped the model wealth unit to £100,000 so political thresholds line up
with real ones (100 units = £10M, 1000 = £100M, 10000 = £1B), and ran
eleven named real-world policies plus two 2D wealth-tax sweeps.

### Policy comparison (250 ticks, 6 seeds)

| policy | alive | closure | top10 | state wealth |
|---|---:|---:|---:|---:|
| uk_tory_2010_24 | 52 | 0.023 | 0.99 | 28,200 |
| uk_labour_2024 | 53 | 0.107 | 0.98 | 26,600 |
| **zucman_2pct_hoard** (no spending) | **49** | 0.252 | 0.96 | 16,300 |
| **zucman_2pct_spend** | **77** | 0.284 | 0.88 | 23,900 |
| **zucman_progressive_2_4_8** | **77** | 0.291 | 0.88 | 23,600 |
| warren_2020 | 73 | 0.177 | 0.92 | 32,900 |
| sanders_2020 | 76 | 0.144 | 0.93 | 31,900 |
| piketty_book | 73 | 0.272 | 0.93 | 26,200 |
| norway_actual | 63 | 0.047 | 0.98 | 39,700 |
| spain_solidarity | 75 | 0.248 | 0.93 | 27,100 |
| reform_uk_flavour | 39 | 0.007 | 0.99 | 28,000 |

### Three findings from the wealth-tax extension

**(i) Zucman flat 2% ≈ Zucman progressive 2/4/8.**
Identical alive (77) and top10 (0.88). The progressive top tiers add 0.007 of
closure. Reason (verified by checking individual wealth distributions):
*the 2% tier above £10M prevents the population from forming any £1B+
wealth in the first place.* Untaxed baseline produces a top agent at £4.2B
and four agents above £1B by tick 250; under 2% above £10M, the top agent
sits at ~£270M and nobody crosses £1B. The higher brackets are politically
symbolic but materially redundant once the lower bracket bites. Sweep B
(progressive top rate × bottom rate) shows column-identical alive and
closure surfaces — the top rate is a free parameter in the post-tax
equilibrium.

**(ii) Taxing without spending kills more people than not taxing at all.**
`zucman_2pct_hoard` (tax but no UBI / state employment / state purchases)
gives 49 alive — *worse* than `uk_tory_2010_24`'s 52. State wealth piles up
to 16,300 units (~£1.6B) while real-economy throughput shrinks. The
finding is robust across seeds. Political consequence: Zucman's policy
without an explicit revenue-recycling commitment fails on its own life-
preservation metric. The "what to spend it on" question is not separable
from the tax question.

**(iii) Threshold dominates rate.** Sweep A varies threshold (£100k → £1B)
× rate (0 → 8%). Autocatalytic closure at 4% rate goes 0.59 (threshold
£10M) → 0.51 (£30M) → 0.43 (£100M) → 0.22 (£300M) → 0.10 (£1B). The
Zucman threshold of £10M is roughly the *highest* threshold that still
moves the system meaningfully. Warren ($50M) and Sanders ($32M) leave
mass on the table; Piketty (1% at €5M) actually pulls more revenue per
year despite the lower headline rate, because the threshold catches the
sub-billionaire rentier class our model is dominated by.

A practical reading: **for any policy that frames itself around
billionaires, the design choice that matters most is where the *lowest*
bracket sits, not how steep the top rate is.**

### What the policy-switch runs add

`out/policies/policy_switch.png` shows a UK-Tory baseline for the first
100 ticks, then a switch to each alternative. Two qualitative observations:

- The Tory baseline already has 40+ agents dead by tick 100 — most policy
  switches are then *triage*, not prevention.
- Zucman-flat-with-spending and Zucman-progressive converge to the same
  trajectory within ~30 ticks of the switch. The two cannot be
  distinguished from the time series at this resolution.

### Caveats specific to the wealth-tax results

- N=100 agents is small. The result "top tier doesn't bind" depends on
  this. A 10,000-agent run might populate the top bracket and the top rate
  would have material effect. Worth a sensitivity run.
- The state spending package is fixed at UBI 0.4 + employs 0.3 +
  buys 5.0 across all the spend-enabled policies, which is generous. The
  "Zucman = Warren = Piketty" convergence partly reflects the spending
  package doing the heavy lifting.
- Inheritance tax is held constant at 40% across the Zucman variants. A
  cleaner factorial would vary it independently; this one's tangled.

## Scale-up to N=10,000 (2026-05-28, late)

Refactored four O(N²) loops in `step()` to O(N) (rent / interest / debt
write-off / borrowing — accumulate-then-distribute pattern), added a
`population_scale` dial, and ran a focused subset of policies at N=10,000
(180 ticks, 3 seeds) plus a 7×7 wealth-tax sweep. Total runtime ~10 minutes
on 7 cores.

### The headline number: billionaires

| policy | alive | closure | ≥£10M | ≥£100M | **≥£1B** |
|---|---:|---:|---:|---:|---:|
| **uk_tory_2010_24** | 5,862 | 0.061 | 1,438 | 804 | **16** |
| uk_labour_2024 | 5,894 | 0.171 | 1,349 | 392 | 1 |
| zucman_2pct_hoard | 5,847 | 0.278 | 1,389 | 22 | 1 |
| **zucman_2pct_spend** | **7,735** | 0.299 | 1,599 | 69 | **1** |
| zucman_progressive_2_4_8 | 7,726 | 0.303 | 1,599 | 63 | 1 |
| warren_2020 | 7,280 | 0.197 | 1,616 | 672 | 1 |
| piketty_book | 7,297 | 0.288 | 1,364 | 108 | 1 |
| **reform_uk_flavour** | 4,992 | 0.026 | 1,533 | 818 | **100** |

The Tory baseline produces **16 billionaires** out of 10,000 agents — a
plausible scale-down of UK reality (Forbes counts ~50 UK-resident
billionaires in a population of ~67M). The "Reform" prospectus (lower
taxes, no state spending, higher rent extraction) generates **100
billionaires and kills 50% of the population**. **Every wealth-tax
policy** — Zucman flat 2%, Zucman progressive 2/4/8, Warren, Sanders,
Piketty — collapses the billionaire count to ~1.

### Three findings that survive scale-up

**(1) The Zucman top-tier still doesn't bind at N=10k.** Flat 2% above £10M
and stacked-marginal 2/4/8 give identical billionaire counts (1 each) and
near-identical alive (7,735 vs 7,726) and closure (0.299 vs 0.303). The
finding from N=100 — that the 2% lower tier prevents the £1B class from
forming, leaving the higher brackets idle — is **scale-robust**. Publishing
note: this is the *modal* finding to lead with. It directly contradicts the
political instinct that "the slope matters most".

**(2) Threshold dominates rate, confirmed.** Warren and Zucman differ only
in threshold ($50M vs £10M) and both run a state-spending package; both
generate ~1 billionaire. But Warren leaves **672 centi-millionaires (£100M–
£1B)** vs Zucman's **69**. Ten times the difference. The £10M vs £50M
threshold choice determines the fate of the £100M+ class. Sanders' $32M
threshold sits between them and gets a similar count to Zucman.

**(3) The regressive-trap finding (new, only visible at N=10k).** The
sweep `top1_share(threshold, rate)` shows that for *very low* thresholds
(£1M, row 0), top-1 share *rises* from 0.37 (no tax) to **0.84** (8% rate)
— the wealth tax made the top *richer* in relative terms. Mechanism: at
£1M threshold, the middle and upper-middle class get charged 8% of their
wealth annually, can't pay, get wiped out faster than the rentier class
can be drained. The bottom and middle thin out; the top's relative share
grows. **At Zucman's £10M threshold (row 2), the same pattern is much
milder** — top1 share goes 0.37 → 0.62. At £100M threshold and above, the
tax catches so few people the rest of the distribution is unaffected
(top1 ≈ 0.37 throughout).

**Practical reading:** a "tax all wealth above £1M" populist position
backfires within this model. Zucman's £10M floor is, by accident or
design, near the right point on the curve to drain the top without
crushing the middle. This is a finding I would not have predicted from
the N=100 sweep and is now the cleanest political result from the model.

### What changes at N=10k vs N=100

- **`zucman_2pct_hoard` no longer kills more than Tory baseline.** At N=100
  it had 49 alive vs Tory's 52 — within noise. At N=10k it's 5,847 vs
  5,862 — essentially identical. The N=100 result was a small-sample
  artefact; the genuine finding is that *hoarding doesn't help* (closure
  goes from 0.061 to 0.278 — better recycling of credit through the
  lender pool because the state buys rentiers' wealth out and lenders
  re-deposit), but it doesn't actively hurt either. Refine the previous
  claim to: "tax without spending is wasted, not destructive".

- **The state-spending closure boost is more modest at scale.** At N=100,
  `zucman_2pct_spend` gave closure 0.284 vs Tory 0.023 — a 12× ratio.
  At N=10k it's 0.299 vs 0.061 — a 5× ratio. Still substantial but the
  effect attenuates as the productive sector grows large enough to be
  somewhat self-sustaining on its own.

- **The "top tier never binds" finding strengthens.** At N=100 the
  argument was "small populations have no room for the tail to express
  itself, so this might be artefactual". At N=10,000 the tail *can*
  express itself (16 billionaires under Tory; 100 under Reform) — and
  yet under any wealth tax with a £10M-or-lower floor, **the population
  cannot maintain more than ~1 billionaire**. This is now the result
  most worth publishing.

### Caveats specific to N=10k

- "Max wealth" in the sweep table includes the State as an agent, which
  can dominate when revenue piles up. A cleaner re-run would exclude
  the State from percentile statistics. The qualitative findings are
  unaffected.
- 180 ticks is shorter than the 250 used at N=100. Done to fit the
  computational budget. Trajectories appear to be near-equilibrium at
  150 ticks but a longer run would tighten the steady-state claims.
- Three seeds is the minimum for a usable error estimate. A publication
  pass needs 10+.

## Recommended next moves

1. **Read Hordijk & Kauffman 2023 in full** before claiming novelty for the
   autocatalytic-closure metric. They may have an adjacent scalar.
2. **Read Spangler & Sarkar 2022 in full** and write a half-page
   differentiation note. This is the paper to beat in JEIC.
3. **Read Cardoso et al. 2025** — published months ago, same thematic space.
4. **Add a mortality-corrected Gini** (Gini over (alive ∪ recently-starved))
   so the rent_vs_r and inheritance_x_ubi paradoxes don't quietly mislead.
5. **Add a spatial layer** (grid or graph) — turns the model from
   "stylised ABM" into "stylised spatial ABM", which is harder to dismiss.
6. **Fit one scenario to WID / SCF wealth-share data** — having one
   calibrated scenario reduces the "toy model" critique substantially.
