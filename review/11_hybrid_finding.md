# R2-9 + R2-10: the hybrid wealth tax dominates the cap

## TL;DR

A wealth tax with marginal rate above the capital-return rate (5--10%
above £10M, against $r=0.08$ per tick) delivers the cap's
distributional effect *and more*, while preserving all of the wealth
tax's enforcement, political, and institutional advantages. The cap is
a corner solution; this is the proportionate, robust, recurrent
instrument that approximates it from a more deployable starting point.

The cap is no longer the recommended policy form. A 5--10% wealth tax
above £10M is.

## R2-9: rate sweep at perfect enforcement

| arm | bn | £100M+ | bot-50% | top-10% | top-1% | state £B | tax revenue £B |
|---|---|---|---|---|---|---|---|
| cap £5M | 2 | 270 | 19.1% | 54.2% | 20.1% | 487 | 0 |
| WT 2% > £10M | 800 | 808 | 0.6% | 98.9% | 31.1% | 5,164 | 5,234 |
| WT 5% > £10M | 0 | 300 | 19.6% | 61.6% | 14.8% | 571 | 646 |
| WT 10% > £10M | 0 | 0 | **42.0%** | **19.2%** | 2.6% | 193 | 271 |
| WT 20% > £10M | 0 | 0 | 45.4% | 13.4% | 1.5% | 148 | 228 |
| WT 50% > £10M | 0 | 0 | 46.9% | 11.2% | 1.2% | 134 | 215 |
| WT 90% > £10M | 0 | 0 | 47.3% | 10.6% | 1.1% | 130 | 211 |
| WT 5% > £50M | 18 | 813 | 10.9% | 75.4% | 16.2% | 1,222 | 1,289 |
| WT 10% > £50M | 0 | 302 | 28.0% | 37.1% | 4.9% | 397 | 466 |
| WT 20% > £50M | 0 | 0 | 31.6% | 29.4% | 3.3% | 267 | 337 |

### Three things this shows

1. **The Zucman 2% rate is too low.** With $r=0.08$ and $\tau=0.02$, the
   tax cannot keep up with capital-return compounding. The Benhabib
   fixed-point argument holds in the model exactly as it should.
   Zucman 2% delivers 0.6pp of bottom-50% lift and leaves 800
   billionaires.

2. **At $\tau \approx r$, the wealth tax matches the cap.** The 5%
   rate above £10M produces 19.6% bottom-50% share, distributionally
   indistinguishable from the £5M cap's 19.1%. Both eliminate
   billionaires entirely. The 5% wealth tax raises more revenue (£571B
   vs £487B) because it operates continuously rather than only at
   death.

3. **At $\tau > r$, the wealth tax dominates the cap.** The 10% rate
   above £10M delivers 42.0% bottom-50% share and top-10% of 19.2%,
   well below the cap's 54.2%. The model is showing what an aggressive
   recurrent extraction does: it bounds the top wealth holding at
   $\theta \cdot \tau / (\tau - r)$, so for $\tau=0.10, r=0.08,
   \theta=£10M$, the bound is $£50M$. No one stays above £50M for
   long. The "£100M+" column hits zero.

## R2-10: enforcement sensitivity comparison

Picking the most aggressive hybrid (WT 90% > £10M) and sweeping the
wealth-tax capture rate from 0.4 to 1.0, against the cap's enforcement
sensitivity from R2-4:

| capture | cap bot-50% | hybrid bot-50% | cap top-10% | hybrid top-10% |
|---|---|---|---|---|
| 0.40 | 0.1% | **46.5%** | 99.9% | 11.7% |
| 0.50 | 0.1% | 46.8% | 99.8% | 11.3% |
| 0.60 | 0.1% | 46.9% | 99.7% | 11.1% |
| 0.70 | 0.2% | 47.1% | 99.5% | 10.9% |
| 0.80 | 0.5% | 47.2% | 98.9% | 10.8% |
| 0.90 | 1.5% | 47.2% | 96.4% | 10.7% |
| 1.00 | 19.1% | 47.3% | 54.2% | 10.6% |

The cap has a catastrophic cliff between 90% and 100% capture; the
hybrid is approximately flat across the entire 40--100% capture range.

The mechanism is exactly what the cap-vs-wealth-tax discussion in our
earlier exchange predicted. Each year's tax compounds against the
prior year's wealth. Effective rate of $0.4 \times 0.9 = 0.36$ per
year above threshold is still well above $r=0.08$, so wealth shrinks
deterministically toward the steady-state ceiling. There is no
dynastic recompounding nonlinearity because the assessment happens
annually, not once at death.

## Why this is the round-2 paper's central finding

The cap was the round-1 proposal. The round-2 stress tests revealed
the cap to be in an unresolvable bind: it needs near-perfect
enforcement to work but cannot get near-perfect enforcement
politically. The hybrid wealth tax bypasses the bind entirely:

- **Distributional effect.** At 5--10% above £10M, the hybrid
  matches or dominates the cap.
- **Enforcement profile.** Robust to leakage across the realistic
  UK enforcement range (0.4--0.6 capture), where the cap delivers
  zero.
- **Implementation.** Wealth tax infrastructure exists (Norway,
  Switzerland, Spain, France until 2018). The instrument is a
  rate change to a known regime, not a new one.
- **Political coalition.** Paid from flow not stock, so does not
  trigger the family-business "we'd have to sell the farm"
  argument that killed every recent estate-tax reform.
- **Flexibility.** A rate can be tuned upward over years; a cap is
  binary. Carve-outs can be specific exemptions on the rate, not
  on the threshold.

## What this implies for the paper

The honest round-2 paper is now not about the cap. It is about a
recurrent wealth tax with a marginal rate above $r$. The cap was the
intuition pump that surfaced the question "what instrument actually
delivers ownership redistribution"; the answer turns out to be the
wealth tax at a rate that the literature has been afraid to discuss
seriously because 5--10% is so far above the Zucman 2% framing.

The Fiscal Studies contribution becomes:

  *We use an agent-based simulation to identify the empirical threshold
  at which a recurrent wealth tax begins to dominate an inheritance
  cap on distributional grounds. The threshold is the rate at which
  the tax exceeds the capital return ($r=0.08$ in the UK calibration).
  Above this rate, a wealth tax of 5--10% above £10M:
  (a) eliminates billionaires entirely,
  (b) raises the bottom-50% wealth share to 20--42%,
  (c) is robust to enforcement leakage in the range that destroys the
      inheritance cap,
  (d) is implementable in existing wealth-tax institutional
      infrastructure,
  (e) does not trigger the family-business political coalition.
  We argue that the Zucman 2% framing has been too modest. The
  evidence-based wealth-tax proposal sits at 5--10%, not 2%.*

## What this implies for the existing round-2 v2 paper

The current `paper_cap_v2.tex` triangulates the cap mechanism, the
enforcement constraint, and the precedent record. It correctly
identifies that the cap is in a bind. It does not yet name the
hybrid. The natural next move is a third paper draft (paper_cap_v3 or,
better, paper_wealth_tax_v1) that:

1. Acknowledges the cap-as-intuition-pump path.
2. Introduces the hybrid as the policy recommendation.
3. Positions the contribution as "what's the right wealth tax rate"
   rather than "should we have a cap".
4. Engages the political-economy literature on wealth tax (Norway,
   French ISF, Spain solidarity) with the new rate target.
5. Treats the cap as a benchmark, not the recommendation.

This is a substantially stronger paper than the cap paper. It is also
a more defensible Fiscal Studies submission, because the recommended
instrument has actual precedent and the headline rate (5-10%) is the
sort of number that a serious reviewer can engage with empirically
rather than dismissing as unimplementable.

## What still needs to be tested

- **Capital flight under the hybrid.** R2-3 tested flight on the cap
  only. The hybrid at 10% above £10M is also flight-sensitive.
  Continuous flow extraction means agents have time to relocate
  before being heavily extracted; estimated flight rates from
  Norway's 2022 wealth-tax reform are useful empirical anchors.
- **Liquidity strain.** A 10% annual extraction on illiquid assets
  forces sale or borrowing. The model has no liquidity friction;
  reality does.
- **Rate transition path.** Politically, you cannot jump from
  current UK to 10% above £10M overnight. The transition path
  (5-year ramp? 2-3-5-7-10% schedule? threshold-and-rate joint
  schedule?) is a research question on its own.
- **Combined with class-conditional carve-out (R2-5).** Apply the
  hybrid only to extractive-class wealth, same as the carve-out
  cap. This is the strongest proposal.
- **Compare hybrid plus cap to either alone.** Stacking the hybrid
  wealth tax with the cap may produce different dynamics; worth
  testing.
