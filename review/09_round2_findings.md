# Round 2 findings (in progress)

Document accumulates the experimental results as round 2 runs.

## R2-1: Kill-switch — IHT-plus-spending decomposition

**Result: cap survives. Hunt's critique fails on the data.**

Run: `src/round2_killswitch.py`, N=10k, 4 seeds, joint-calibrated UK
baseline (r=0.08, rent=0.20, sub=0.30). All arms with the same state
spending package (UBI 0.4, state jobs 30%, state buys maker output 5.0)
except A.

| arm | alive | billionaires | bottom-50% | top-10% | top-1% | state £B |
|-----|-------|-------------|-----------|---------|--------|----------|
| A status quo | 82.7% | 804 | 0.0% | 100.0% | 32.7% | 0 |
| B spend only | 84.1% | 804 | 0.0% | 100.0% | 33.0% | 0 |
| C IHT40 + spend | 90.5% | 801 | **0.0%** | 99.9% | 36.8% | **9,815** |
| D cap + spend | 91.3% | 2 | **19.1%** | 54.2% | 20.1% | 487 |
| E cap + IHT40 + spend | 91.4% | 1 | 19.1% | 54.0% | 19.6% | 491 |

Decomposition of the bottom-50% lift:

- Recirculation alone (B − A): +0.0pp
- IHT 40% plus recirculation (C − A): +0.0pp
- Cap plus recirculation (D − A): **+19.1pp**
- Cap-specific lift beyond IHT (D − C): **+19.1pp**

**The cap is doing structural work that no IHT rate plus redistribution
package can replicate.** IHT at 40% raises £9.8T in state revenue (20x
what the cap raises) but leaves the bottom-50% wealth share at 0.0%.

### Why this is the answer to Hunt

Hunt's critique was that the bottom-50% effect is just
"inheritance-tax-plus-redistribution under a different name". The data
falsifies this. The IHT route extracts huge revenue and circulates it
as income (UBI, state wages, maker purchases) which is consumed as
subsistence rather than accumulated as wealth stocks. Top wealth
holders still compound between deaths, dynasties survive, the top-10%
share remains essentially 100%.

The cap, by contrast, breaks dynastic compounding at each generation.
Top wealth resets to £5M per inheritance. The compounding flywheel
that drives the top-10% to 100% under status quo cannot restart. The
released wealth flows into the middle and bottom of the distribution
as asset stocks, raising the bottom-50% share to 19.1%.

### Subtler mechanism

Note that under cap the state captures £487B (small) compared with
£9.8T under IHT40 (large). The cap does not redistribute by
state-capture-then-spend. It redistributes by preventing the
re-concentration that would otherwise dominate household wealth. The
state is a smaller actor in the cap regime, not a bigger one. This is
a meaningful framing point for the paper.

### Implications for paper rewrite

1. Add this decomposition as a new core figure: 5-bar bottom-50%
   share comparison with explicit (D − C) annotation.
2. Reframe the Hunt section of the discussion: cap is not
   "redistribution under another name", it is anti-concentration that
   does not depend on state recirculation working.
3. The £9.8T vs £487B comparison is the cleanest single-number rebuttal
   to "just use IHT" — IHT raises 20x more state revenue and delivers
   0pp of ownership redistribution.

### Caveats this run does not address

- Enforcement friction still assumed at 100% in all arms.
- No flight channel.
- Baseline still has bottom-50% at 0.0% rather than 9%.
- No carve-out for productive business assets.

These are addressed in R2-2 through R2-5.

---

## R2-2: WAS-calibrated baseline

**Result: Stewart's critique sharpens rather than weakens once you
actually try to match UK reality. The cap moves the model towards
UK reality, not away from it.**

Run: `src/round2_was_baseline.py`, same 5 arms as R2-1, augmented with
a £200k housing+pension floor per worker/maker household (ONS WAS
2018-2020: median UK household non-financial wealth around this level).

| arm | bot-50 raw | bot-50 +floor | top-10 raw | top-10 +floor |
|-----|-----------|--------------|-----------|---------------|
| A status quo | 0.0% | 0.0% | 100.0% | 100.0% |
| B spend only | 0.0% | 0.0% | 100.0% | 100.0% |
| C IHT40 + spend | 0.0% | 0.0% | 99.9% | 99.9% |
| D cap + spend | 19.1% | 19.5% | 54.2% | 53.7% |
| E cap + IHT40 + spend | 19.1% | 19.4% | 54.0% | 53.5% |

UK reality (WAS 2018-2020): bottom-50% ~9%, top-10% ~57%.

### What this reveals

Adding a £200k household-wealth floor changes the headline by 0.4pp.
The floor is invisible against the dynastic-compounding stock at the
top. The cap arm reproduces a top-10% share (54%) very close to UK
reality (57%), while the status-quo arm sits at 100%, dramatically
more concentrated than reality.

The diagnosis is structural: the model's compounding dynamics at
r=0.08 with no countervailing extraction produce concentration well
beyond what the UK actually has. Adding a housing floor does not
move this. **What does move it is the cap.**

### Implications for paper rewrite

1. The honest framing is that the model captures financial-wealth
   dynamics. Under status quo it over-states top concentration
   relative to UK reality. The cap regularises the dynamics back to
   something close to UK reality at the top (54% vs UK 57%).
2. The "0% to 25%" headline should become "the cap brings the model's
   top-10% share from 100% to 54%, against UK reality of 57%." The
   bottom-50% rise from 0% to 19% is the corresponding stock
   redistribution implied by that top-share compression.
3. We should report both raw and floor-augmented numbers in the paper,
   and acknowledge in the limitations section that the model excludes
   housing equity and pension entitlements as separate wealth classes.
   The floor exercise demonstrates that this exclusion does not
   materially affect the headline.
4. Stewart's "baseline is wrong" critique becomes "model status quo
   is more extreme than UK status quo, and the cap brings it closer
   to UK reality, not further from it." This is a stronger framing
   for the paper.

---

## R2-3: Capital-flight channel

**Result: the cap's effect on the in-country distribution survives
aggressive flight, but country total wealth is meaningfully reduced.
This is the most honest finding so far.**

Run: `src/round2_flight.py`. Same 5 arms with a flight channel:

```
flight_rate_per_tick(w, cap) = base_rate * (w - cap) / cap
```

Flying agents leave the simulation entirely (no state capture). Swept
across base rates {0, 0.005, 0.01, 0.02, 0.05}.

Cap arms only (flight only applies to wealth above the cap; status
quo and IHT arms have no cap so flight does not apply by construction):

| arm | flight | remaining | billionaires | bot-50% | top-10% | flown agents | flown wealth £T |
|-----|-------|-----------|-------------|---------|---------|------------|------------------|
| D cap | 0.000 | 91.3% | 2 | 19.1% | 54.2% | 0 | 0.0 |
| D cap | 0.005 | 55.4% | 0 | 30.3% | 20.5% | 3340 | 0.1 |
| D cap | 0.010 | 42.6% | 0 | 27.3% | 21.8% | 4051 | 0.1 |
| D cap | 0.020 | 31.5% | 0 | 21.9% | 23.7% | 3826 | 0.1 |
| D cap | 0.050 | 16.3% | 0 | 22.3% | 21.8% | 2680 | 0.0 |
| E cap+IHT | 0.005 | 59.0% | 0 | 25.8% | 21.4% | 3192 | 0.1 |
| E cap+IHT | 0.050 | 14.6% | 0 | 17.1% | 31.8% | 2613 | 0.0 |

### What this reveals

1. **In-country distribution stays compressed.** Across all flight
   rates, top-10% remains well below the status-quo 100% (in the
   20-32% range), bottom-50% remains above 13%. The cap's distributional
   effect on residents who stay is preserved.
2. **Total country wealth falls.** £0.1T in flown wealth per arm,
   which is large for the simulated UK scale. This is the legitimate
   cost the paper needs to acknowledge.
3. **The honest pitch is no longer "the cap delivers a one-shot
   ownership transfer at no cost."** It becomes "the cap delivers
   ownership redistribution among residents, at the cost of UHNW
   emigration whose magnitude depends on enforcement of residency
   rules and exit taxation."
4. **Flight removes the top so dramatically that the cap arm's
   in-country top-10% under flight (20-32%) is *more equal* than
   the cap arm without flight (54%).** This is true but is a mostly
   mechanical artefact of removing top holders. It does not
   strengthen the case for the policy because the country has lost
   the wealth in absolute terms.

### Caveats

- The flight model is not applied to IHT40 (arm C), which is also
  flight-sensitive in reality. If flight were also applied to high-IHT
  arms, those would similarly bleed. The honest comparison would have
  flight in both, which would shrink the bot-50% gap further.
- The "alive_rate" reported here conflates death-by-starvation with
  emigration. The remaining-rate is the correct headline.
- The flight elasticity is uncalibrated. Young et al. would suggest a
  base rate of 0.001-0.005 is the empirically defensible range. The
  0.05 row is included as a stress test.

### Implications for paper rewrite

The cap paper must acknowledge that the headline 0% to 19% lift is
the no-flight upper bound. Under empirically plausible flight rates
(0.001-0.005), the cap delivers ownership compression among residents
but loses substantial wealth to emigration. The defensible claim is:

  "Under an enforcement regime with G20-coordinated residency rules,
   exit taxation, and unilateral asset-attaching provisions sufficient
   to keep flight below 0.5% per tick per cap-multiple of wealth, the
   cap raises bottom-50% wealth share among residents by approximately
   10-19 percentage points. Without those provisions, residents still
   benefit but the country loses substantial wealth to emigration."

This is a much weaker claim than the current paper. It is also a
defensible one.

---

## R2-4: Enforcement friction

**Result: this is the deepest blow to the paper. Stewart's enforcement
critique kills the headline at any realistic UK enforcement level.**

Run: `src/round2_enforcement.py`. Modified `sim.py` to add a
`inheritance_capture_rate` dial: fraction of the above-cap excess that
the state actually captures. The rest leaks to the heir. Swept across
0.4-1.0 with the £5M cap arm.

| capture | billionaires | £100M+ | bottom-50% | top-10% | top-1% | state £B |
|---------|-------------|--------|-----------|---------|--------|----------|
| 0.40 | 800 | 826 | 0.1% | 99.9% | 35.7% | 10,569 |
| 0.50 | 800 | 819 | 0.1% | 99.8% | 37.4% | 9,356 |
| 0.60 | 800 | 812 | 0.1% | 99.7% | 38.7% | 8,197 |
| 0.70 | 800 | 806 | 0.2% | 99.5% | 40.8% | 6,106 |
| 0.80 | 800 | 803 | 0.5% | 98.9% | 42.8% | 4,116 |
| 0.90 | 584 | 802 | 1.5% | 96.4% | 45.1% | 2,049 |
| 1.00 | 2 | 270 | 19.1% | 54.2% | 20.1% | 487 |

### What this reveals

The cap's effect is *highly* discontinuous in enforcement quality.
At 90% capture (already optimistic relative to current UK IHT
effective capture, which most estimates put at 30-50% of the
theoretical base), the bottom-50% ownership lift drops from 19.1pp
to 1.5pp. At 80% it is 0.5pp. At 70% and below it is essentially
zero.

The mechanism is dynastic recompounding. Even small leakage means the
heir starts with significantly more than £5M, and at r=0.08 over a
lifespan a £14.5M start (the 90%-capture case for a £100M holder)
compounds to £3B+ by death. The cap then captures most of that, but
the next generation starts at £14.5M again, and the cycle continues.
Billionaires are converted into centi-millionaires but the bottom-50%
share stays at zero.

### Why this is the deepest blow

The paper proposes implementation with "explicit carve-outs for
primary residences and small productive-business assets". Carve-outs
are exactly the mechanism by which enforcement leaks in current UK
IHT (BPR, APR, trust structures, valuation discounts). The cap is
in an unresolvable bind:

- **Carve-outs broad enough to be politically viable** (BPR-style
  productive-business exemption, primary-residence exemption, agricultural
  exemption) bring effective capture rate to the 0.4-0.6 range. At
  those rates the policy delivers nothing on its ownership claim.
- **Carve-outs narrow enough to preserve the policy** (no BPR/APR,
  hard residency, full trust transparency, mark-to-market valuation)
  require institutional and political capacity that no comparable
  polity has demonstrated.

There is no middle. Either the cap works (perfect enforcement, no
carve-outs, political miracle) or it does not work (realistic
enforcement, normal carve-outs, business as usual).

### Implications for paper rewrite

This is too damning to gloss over. Two honest paths:

**Path 1: Pull back the claim.**

  "The cap delivers its ownership effect only under enforcement
   conditions that are not historically achievable in any large
   democracy. We document the policy mechanism in the limit; the
   feasibility of approaching that limit is a separate question of
   institutional capacity and political economy that the model
   cannot adjudicate."

  This is honest but weakens the paper dramatically. Fiscal Studies
  reviewers will say "so what?"

**Path 2: Make enforcement the central object.**

  Reposition the paper around the enforcement question. The contribution
  becomes: "Identify the structural mechanism by which an inheritance
  cap could deliver ownership redistribution, and demonstrate that this
  mechanism is uniquely sensitive to enforcement quality. The policy
  proposal then becomes a proposal about institutional capacity, not
  about tax rates."

  This is a stronger paper because it foregrounds the issue every
  serious reader will see, and it engages directly with the most
  damaging critique. The Fiscal Studies submission becomes a paper
  about why structural fiscal instruments work or fail as a function
  of enforcement, with the inheritance cap as a vivid case.

I recommend Path 2. It is more interesting, it survives Stewart's
attack rather than dodging it, and it gives the paper a question
that has not been addressed in the existing literature. The "why no
country has done this" question (R2-7) gets a partial answer: because
no country has had the enforcement capacity to make it work.

---

## R2-5: Productive-class carve-out

**Result: a class-conditional cap (productive exempt, extractive
capped) delivers a *larger* bottom-50% lift than the universal cap.
This defuses Hunt's "captures every family business" attack — under
the model's mechanism.**

Run: `src/round2_carveout.py`. Three cap variants:
- cap_all: £5M cap on every class
- cap_extract: £5M cap only on RENTIER/LENDER/SPECULATOR
- cap_extract_strict: as above plus £50M soft cap on productive classes

| arm | billionaires | £100M+ | bottom-50% | top-10% | top-1% | state £B |
|-----|-------------|--------|-----------|---------|--------|----------|
| baseline | 804 | 841 | 0.0% | 100.0% | 33.0% | 0 |
| cap_all | 2 | 270 | 19.1% | 54.2% | 20.1% | 487 |
| cap_extract | 2 | 328 | **26.2%** | 42.2% | 13.8% | 416 |
| cap_extract_strict | 2 | 328 | 26.2% | 42.2% | 13.8% | 416 |

### What this reveals

In the model, EMPLOYER and MAKER class wealth never reaches the £5M
threshold organically because their wealth comes from wage/markup
accruals rather than capital-return compounding. Exempting them from
the cap costs essentially nothing, but it allows employer wealth to
propagate within productive lineages, which in turn generates more
wage flow to workers and more bottom-50% accumulation.

The cap_extract arm produces a *more equal* distribution than cap_all
(top-10% 42% vs 54%, top-1% 14% vs 20%) while still eliminating
billionaires. The dominant flow that produces concentration is the
RENTIER capital-return compounding. Capping that suffices.

### Caveats this run does not address

- In reality, EMPLOYER wealth does reach £5M+ (mid-sized family
  businesses, founders of regional manufacturers). The model under-
  represents this tail. A more realistic version would put 5-15% of
  EMPLOYER class wealth above £5M.
- The class-conditional cap requires HMRC to distinguish "extractive"
  from "productive" wealth at death. In current practice this is the
  BPR/APR test, which is highly gamed (private-equity holdings dressed
  as "businesses", financial assets held in productive-business
  wrappers).
- The R2-4 enforcement finding still applies. Even with carve-outs,
  the cap requires near-perfect enforcement on the capped classes.

### Implications for paper rewrite

The class-conditional carve-out is a real answer to the family-business
critique. The paper should adopt this as the policy form rather than
the universal cap, and acknowledge:

1. The carve-out preserves family-business succession.
2. The carve-out delivers larger bottom-50% lift than the universal cap
   (counterintuitive but robust in the model).
3. The carve-out shifts the enforcement target from "all wealth above
   £5M" to "extractive wealth above £5M", which is a narrower base
   to assess but a more contested one to classify.

The honest pitch becomes: **a cap on extractive bequest above £5M,
combined with G20-coordinated enforcement of asset classification**.
This is a more specific and more defensible proposal than the current
paper's "universal cap with explicit carve-outs".

---

## R2-6: Equal-revenue wealth-tax head-to-head

**Result: at equal revenue, the cap dominates the wealth tax
decisively on every distributional metric. Even at 10x revenue, the
wealth tax fails to break top concentration.**

Run: `src/round2_equal_revenue.py`. Wealth-tax rates above £10M
threshold swept across 0.01%-2% per tick, compared against the £5M
cap on ending state wealth.

| arm | billionaires | £100M+ | bottom-50% | top-10% | state £B |
|-----|-------------|--------|-----------|---------|----------|
| cap | 2 | 270 | 19.1% | 54.2% | 487 |
| WT 0.01% (equal rev) | 804 | 845 | 0.0% | 100.0% | 374 |
| WT 0.05% | 804 | 848 | 0.0% | 99.9% | 1,884 |
| WT 0.1% | 803 | 847 | 0.0% | 99.9% | 3,543 |
| WT 0.2% | 802 | 846 | 0.0% | 99.9% | 6,173 |
| WT 0.5% | 803 | 840 | 0.1% | 99.9% | 10,085 |
| WT 1% | 800 | 824 | 0.1% | 99.7% | 9,976 |
| WT 2% (Zucman) | 800 | 808 | 0.6% | 98.9% | 5,164 |

### What this reveals

The wealth tax is a flow-extraction instrument. It cannot keep up with
compounding at r=0.08 per tick. Even at the Zucman 2% rate (which raises
10x the cap's revenue), the wealth tax leaves the top concentration
essentially unchanged (top-10% = 98.9% vs status quo 100%).

The cap is a stock-resetting instrument. It does not trickle-extract;
it interrupts the dynastic compounding at the boundary of each
generation. The resulting break in the flywheel is what redistributes
ownership.

These are categorically different mechanisms operating on different
sides of the wealth-dynamics equation. The Hunt critique "use the
wealth tax instead" misses this distinction.

### The Hunt steel-man under R2-4 + R2-6

R2-4 showed the cap collapses under enforcement friction. R2-6 shows
the wealth tax never matched the cap at any rate even under perfect
enforcement. So the steel-man Hunt argument is:

  "Both instruments work only under enforcement. The wealth tax has
   continuous valuation that HMRC can administer to a 60-70% capture
   rate (the realistic UK figure). The cap has once-in-a-lifetime
   valuation that requires near-perfect capture to deliver any
   distributional effect. Under realistic UK institutional capacity,
   the wealth tax raises real revenue and the cap raises essentially
   nothing. The cap looks better on paper because the model assumes
   away the enforcement asymmetry. The wealth tax wins in practice."

This is a serious argument. The paper rewrite must address it.

### Implications for paper rewrite

The honest framing now becomes a triangulation between three claims:

1. **At perfect enforcement, the cap dominates the wealth tax on every
   distributional metric, including at 10x revenue parity.** This is
   the model's clean mechanical finding (R2-6).
2. **The cap is uniquely sensitive to enforcement quality.** Even small
   leakage destroys the distributional effect because of dynastic
   recompounding (R2-4).
3. **The wealth tax is less sensitive to enforcement quality** because
   it is a continuous extraction whose effects accumulate over
   collections rather than depending on a once-in-a-lifetime event.

The policy prescription then becomes conditional:

  "If a country can build the institutional capacity to enforce an
   inheritance cap at >95% capture, the cap will deliver ownership
   redistribution that no wealth tax can match at any rate. If
   enforcement capture is in the realistic 50-70% range, the cap
   delivers nothing and the wealth tax is the only working instrument.
   The choice between them is therefore not a choice between policy
   mechanisms but a choice about what level of institutional capacity
   the proposer believes can be achieved."

This is a paper-defining triangulation. It is also the honest reading
of the data.

