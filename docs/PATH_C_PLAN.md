# Path C: deep research plan for the endogenous-growth extension

Last revised at the close of Phase 3 (Path B, the growth paper).

This document plans the model extensions, empirical claims,
calibration anchors, and paper outlines for Path C.  Path B
established that the choice of growth measure is the choice of
conclusion in the wealth-tax debate.  Path C goes one level deeper:
build microfoundations for endogenous productivity growth so that the
``wealth tax raises real productive growth'' claim is mechanically
identifiable and quantitatively defensible against the orthodox
endogenous-growth literature.

## 1. The current state of the model

The model has the bones of an endogenous-growth framework but the
mechanisms have not been switched on.  We have:

- Endogenous human capital via skill transmission with wealth-
  dependent bandwidth.
- Two productivity channels added in Path B (skill-broadening
  human-capital and capital-deepening employer-wealth) but both are
  level-additive rather than growth-augmenting.
- The `open_skills` experiment (skill-space extension via novelty
  discovery), tested in isolation in `src/open_skills.py` and
  `src/open_skills_longrun.py` but not integrated into the main
  model.

What we are missing for a credible endogenous-growth analysis:

- **C1 endogenous R&D**: a research activity that discovers new
  skill dimensions over time, raising the population skill-space
  dimensionality.  The hypothesis is that wealth tax preserves the
  broad skill base required to sustain R&D, so PT growth becomes
  positive under wealth-tax arms and stays near zero under status
  quo.  This is the core Path-C extension.

- **C2 mission-oriented public investment**: state revenue from the
  wealth tax directed at skill discovery or capability-building
  investment.  Operationalises the Mazzucato mission-orientation
  argument.

- **C3 demand-composition effects**: bottom-50% MPC is higher than
  top-1% MPC; redistribution shifts demand toward broadly-distributed
  productive sectors.  Keynesian multiplier extension.

- **C4 comparable-country calibration**: status-quo calibration
  has been done against the UK only.  A pass at Norway, Sweden,
  Germany, and the US would discipline the worry that the
  multi-anchor coincidence in the tick-year calibration is
  within-jurisdiction overfitting.

## 2. The intellectual context Path C has to engage

### 2.1 The endogenous-growth literature

The relevant analytical traditions:

- **Romer (1990)**: knowledge as a non-rival input; R&D produces
  productivity-augmenting innovations; the rate of growth depends
  on the share of the population engaged in R&D.  Our skill-space
  discovery mechanism is structurally Romerian.

- **Aghion & Howitt (1992)**: creative-destruction Schumpeterian
  growth; new innovations make old skills obsolete; the rate of
  growth depends on the obsolescence rate.  Our skill-loss
  mechanism (knowledge_lost_cum) is structurally Aghion-Howitt.

- **Acemoglu (2002, directed technical change)**: the direction of
  innovation responds to factor scarcity; wealth concentration may
  direct innovation away from labour-augmenting and toward
  capital-augmenting forms.  This is the channel through which
  wealth tax may affect the *direction* of innovation, not just
  the rate.

- **Mazzucato (2013, 2018)**: state-funded mission-oriented R&D
  is the historical engine of breakthrough productivity, not the
  private sector.  The wealth-tax revenue directed at
  mission-oriented investment is the policy-relevant version of
  this argument.

- **Hanushek & Woessmann (2012)**: cognitive-skills measurement
  predicts long-run growth much better than schooling measures.
  Our skill-breadth measure is closer to cognitive skills than to
  schooling-years measures, which makes our human-capital
  channel empirically calibrated to the right magnitude.

The Path-C paper has to engage these literatures explicitly,
not just cite them.  Each tradition has implications for what
mechanisms the model should contain.

### 2.2 The post-Keynesian / heterodox growth tradition

Important and largely absent from the Path-B paper:

- **Kalecki (1939, 1971)**: aggregate demand is determined by the
  distribution of income; redistribution toward wage earners raises
  aggregate demand and growth.  The Kaleckian view is the
  theoretical foundation for C3.

- **Bhaduri & Marglin (1990)**: wage-led vs profit-led growth
  regimes; the model's growth response to redistribution depends
  on whether investment is more responsive to demand or to profit
  share.  Our model is currently silent on investment behaviour,
  which is a gap.

- **Kumhof, Rancière, Winant (2015) and Carvalho, Rezai (2016)**:
  empirical and theoretical work on rising inequality producing
  higher household debt and reduced aggregate demand.  Our model
  has debt and a debt-writeoff mechanism, providing a natural hook
  for this extension.

The Path-C paper should engage these traditions because the
Keynesian multiplier effects of wealth-tax redistribution are
empirically large and politically important.

### 2.3 The capability and inclusive-wealth tradition

Path B used a Sen-flavoured capability index but did not engage
the literature deeply.

- **Sen (1999, 2009)** and **Nussbaum (2011)**: the capability
  approach as the framework for evaluating economic policy.
- **Dasgupta (2021)**: the inclusive-wealth framework, with formal
  shadow-pricing of human and natural capital.
- **Stiglitz-Sen-Fitoussi (2009)**: the Beyond GDP framework that
  underlies our six-measure portfolio.

Path C should formalise the capability measure under shadow prices
that the inclusive-wealth tradition would recognise.

### 2.4 Empirical anchors for the productivity-stagnation case

The UK 2008--2024 productivity puzzle is the empirical phenomenon
the paper has to explain:

- Output per hour 0.4% per year (vs 2.4% pre-2008).
- Real median wages flat.
- Business R&D intensity below OECD average.
- Investment as share of GDP below OECD average.
- Top-1% wealth share rising; bottom-50% share flat at ~5--10%
  (ONS WAS).
- Financial-sector GVA growing at 5--6% per year.

Path C should produce a model that quantitatively reproduces this
divergent pattern at status quo and that produces a corrective
pattern (productive-output growth rises, financial-sector
compounding falls) under the wealth-tax arms.

## 3. The Path-C mechanism specification

### 3.1 C1 endogenous R&D

**Mechanism design.**  At each tick, each MAKER and EMPLOYER agent
allocates a share of their wealth to ``R&D investment''.  R&D
investment with budget $B$ produces a skill-discovery probability
$p_{\mathrm{disc}}(B, S, D)$ where $S$ is the population mean skill
total, $D$ is the population skill diversity.  When discovery
succeeds, a new skill dimension is added to the population skill
space; the discoverer agent (and a randomly drawn fraction of the
population) acquire the new skill at level $s_0$.

**Calibration anchors.**
- UK R&D intensity 1.8% of GDP (ONS).  This sets the share of MAKER
  and EMPLOYER wealth that flows to R&D.
- UK productivity growth 0.4% per year (post-2008).  This sets the
  $p_{\mathrm{disc}}$ baseline.
- Total factor productivity decomposition: Hanushek-Woessmann
  imply a skill-input elasticity of about 0.3--0.5 of TFP growth.

**Hypothesis.**  Under status quo, R&D is funded by wealthy MAKER
and EMPLOYER agents who have concentrated wealth above subsistence;
the population skill base narrows over generations through cultural
transmission loss, reducing $p_{\mathrm{disc}}$.  Under the wealth
tax, MAKER and EMPLOYER wealth is approximately preserved (they are
mostly below the threshold), the population skill base broadens,
and $p_{\mathrm{disc}}$ rises.  PT growth becomes positive under
the wealth-tax arms and stays near zero under status quo.

**Falsifiability.**  If $p_{\mathrm{disc}}$ depends more strongly
on individual R&D budget than on population skill breadth, then
wealth concentration is growth-favourable (R&D is funded by the
concentrated wealth) and the orthodox prediction is recovered.
The PT-growth differential is therefore a function of the
$p_{\mathrm{disc}}$ functional form.  Path C must specify this form
carefully and calibrate against the empirical productivity
literature.

**Implementation sketch.**
```python
# In sim.py, add to Dials:
rd_share_of_maker_wealth: float = 0.02
rd_share_of_employer_wealth: float = 0.02
rd_discovery_coeff: float = 0.05
rd_skill_breadth_elasticity: float = 0.5

# In step(), after production:
for a in [MAKERs and EMPLOYERs]:
    rd_budget = a.wealth * d.rd_share_of_X
    a.wealth -= rd_budget
    rd_budget_pool += rd_budget

mean_breadth = average worker skill_breadth / SKILL_DIMS
p_disc = d.rd_discovery_coeff * rd_budget_pool *
         (mean_breadth ** d.rd_skill_breadth_elasticity)
if rng.random() < p_disc:
    # Add a new skill dimension; assign to discoverer and
    # a sample of the population
    SKILL_DIMS_global += 1
    ...
```

This is a substantial change to the model architecture because
SKILL_DIMS is currently a global constant.  Making it dynamic
requires propagating changes through the skill-transmission code,
the bandwidth-limited copy logic, and the metric definitions.

### 3.2 C2 mission-oriented public investment

**Mechanism design.**  When the state collects wealth-tax revenue,
a configurable share is allocated to a ``mission'' fund that
purchases R&D inputs directly.  Mission spending behaves like
private R&D but is targeted at high-priority skill dimensions
(operationalisation: dimensions in which population mean skill is
currently below some threshold).

**Calibration anchor.**
- Historical UK / US public R&D spending: 0.4% of GDP for the UK,
  0.7% for the US (Mazzucato 2018).
- Historical mission cases (Apollo, the human genome project): the
  Mazzucato narrative argues these were the engines of breakthrough
  productivity.  Path C should test whether the mechanism the
  narrative claims is empirically realised in the model.

**Hypothesis.**  Mission-oriented spending raises $p_{\mathrm{disc}}$
through both direct discovery probability and through reducing the
``deprivation'' in priority skill dimensions, which feeds the
human-capital channel.  Under wealth-tax + mission, PT growth is
higher than under wealth-tax alone.

### 3.3 C3 demand-composition effects

**Mechanism design.**  Replace the current simple subsistence-based
worker consumption with a demand function that depends on net
wealth.  Bottom-50% workers have higher MPC than top-1% rentiers;
total demand for MAKER output rises under redistribution.

**Calibration anchor.**
- UK Wealth and Assets Survey: bottom-50% MPC roughly 0.85--0.95,
  top-1% MPC roughly 0.05--0.15.
- Implied Keynesian multiplier from redistribution: 1.5--2.0.

**Hypothesis.**  Under wealth-tax arms, redistribution raises
bottom-50% consumption demand, which raises MAKER output, which
raises productive-flow share, which raises the human-capital
channel via mean worker skill breadth (higher MAKER output supports
higher worker wages, which permits higher cultural-transmission
bandwidth in the next generation).  Net effect: a Keynesian
multiplier on the PT level effect already reported in Path B.

**Implementation sketch.**  Replace the constant `d.subsistence`
with a wealth-dependent `consumption(a)` function.

### 3.4 C4 comparable-country calibration

**Method.**  Re-run the four-anchor tick-year calibration for
Norway, Sweden, Germany, and the US.  For each country:

- Recalibrate $r$ to the long-run national stock-market return.
- Recalibrate lifespan to national life expectancy.
- Recalibrate financial-sector growth rate.
- Recalibrate output-per-hour growth rate.

Check whether the 1 tick = 1 year mapping is invariant across
jurisdictions or whether different countries require different
mappings.  This is the discipline against within-jurisdiction
overfitting.

## 4. Paper structure: `paper_growth_v2.tex`

Target: 25--30 pages.  Target venue: AER (long shot), JEEA
(realistic), or a paired Fiscal Studies + JEEA submission with
v1 as the methodological foundation.

```
1. Introduction
   - The wealth-tax debate has been a level-effect debate; we make
     it a growth-rate debate
   - Three-mechanism Path-C extension is the device
   - Headline finding (TBD, depends on the model output)
2. The endogenous-growth, post-Keynesian, and capability literatures
   - Romer / Aghion-Howitt / Acemoglu (orthodox endogenous growth)
   - Kalecki / Bhaduri-Marglin / Kumhof (heterodox)
   - Sen / Dasgupta / Stiglitz-Sen-Fitoussi (capability /
     inclusive wealth)
3. The UK productivity puzzle as the empirical anchor
4. Model extensions: C1 R&D, C2 mission, C3 demand composition
5. Calibration: UK 2008-2024 reference points + comparable-country
   stress test
6. Headline result: PT growth rates under the five policy arms
7. Decomposition: which mechanism drives the wealth-tax PT-growth
   advantage
8. Comparable-country robustness (UK, Norway, Sweden, Germany, US)
9. Implications for the optimal-taxation framework
10. Discussion: engaging the strongest opposing case
11. Conclusion
```

## 5. Estimated effort

| stage | effort | risk |
|---|---|---|
| C1 implementation | 2--3 weeks | Substantial: dynamic SKILL_DIMS, propagation through the codebase, calibration |
| C2 implementation | 1 week | Modest: built on C1 |
| C3 implementation | 1 week | Modest |
| C4 comparable-country calibration | 1 week per country, 4 countries | Modest per country, cumulatively material |
| Headline result interpretation | 1--2 weeks | Risk: the model may not produce a sustained PT growth differential |
| Paper writing | 3--4 weeks | Standard |
| Total | 12--16 weeks | -- |

This is a substantial project.  The 12--16 week estimate assumes
the model behaves the way the hypothesis predicts.  If C1 produces
unexpected results (e.g. the orthodox prediction is recovered),
the paper rewrites accordingly and the effort is similar but the
direction of the headline is different.

## 6. Risk register

**Risk 1: C1 may not produce a sustained PT-growth differential.**
If the skill-discovery probability function is highly non-linear
in budget, the wealth-concentration-funded private R&D under
status quo may dominate the broad-base-funded R&D under wealth
tax.  Mitigation: explore the parameter space and report
conditions under which each side wins.  This is the honest paper
either way.

**Risk 2: Dynamic SKILL_DIMS may break existing experiments.**
The current model has SKILL_DIMS=5 baked in.  Making it dynamic
requires careful refactoring.  Mitigation: branch the codebase and
preserve all existing results as a benchmark.

**Risk 3: Comparable-country data may not be available at the
granularity required.**  Some of the four reference points (notably
financial-sector GVA growth) may not be available for all four
comparator countries with consistent methodology.  Mitigation:
fall back to a smaller anchor set (r, lifespan, output-per-hour
growth only) and explain the data gap.

**Risk 4: The orthodox response may attack the model architecture
directly.**  ``Your model has no firm formation, no financial
intermediation, no monetary policy, no exchange rate.  You cannot
make growth-rate claims on this scaffolding.''  Mitigation: this
is a fair critique and the paper must engage it.  The honest
response is that the model captures the channels we claim it
captures and is silent on the others; whether the omitted channels
swamp the included ones is an empirical question we cannot
adjudicate.  This is a real limitation.

**Risk 5: Path C is not the right next move.**  Alternative
priorities: deepen the political-economy work, develop the
communication piece, or accept that the existing two-paper package
(wealth_tax + growth) is the right submission and move on to a new
project.  This is a strategic question for the user, not an
empirical one for the model.

## 7. Strategic recommendation

The Path-C extension is a substantial project (3--4 months) with a
high payoff (the paper would be a serious contribution to the
endogenous-growth literature) but real risk (the model may not
produce the result the hypothesis predicts; the orthodox channels
may dominate).  The right sequencing is:

1. **First, submit Path B (the current growth paper) for review.**
   This generates feedback on the methodological framing and the
   measurement-portfolio argument before we commit to the heavier
   mechanism work.

2. **Concurrently with Path B review, do the C1 implementation as
   a proof-of-concept** without committing to a paper.  Test whether
   the wealth-tax-favourable PT-growth result is recoverable in
   the model.  If yes, scope the Path-C paper.  If no, revise the
   hypothesis honestly.

3. **If C1 confirms, scope and execute C2, C3, C4.**

4. **If C1 disconfirms, write up the negative finding as a short
   note** (the Romer-channel test does not favour the wealth tax)
   and consider whether the Bhaduri-Marglin C3 channel is the
   right substitute mechanism for the paper.

This is the disciplined research strategy.  It also protects against
the project committing 3--4 months to a paper whose mechanism turns
out not to deliver the predicted result.

## 8. Open questions for the user

Before committing to Path C, the user should decide:

1. **Submission timeline.**  Is Path B submitted now, or do we wait
   for Path C to be a paired submission?  My recommendation:
   submit Path B now.

2. **Risk appetite.**  Path C is high-payoff but real-risk.  Are
   we committed to the hypothesis (which makes us vulnerable to
   confirmation bias) or are we genuinely open to a negative finding?
   This shapes the paper-writing posture.

3. **Resource budget.**  3--4 months of model and paper work is a
   substantial commitment.  Is this the right next project or is
   the next project something else (a communication piece, a
   political-engagement programme, a new model architecture)?

4. **Co-authorship and venue strategy.**  AER is a long shot; JEEA
   is realistic; a paired Fiscal Studies submission is the safest.
   Which venue strategy shapes the paper structure most?

The above questions are policy questions, not empirical ones.  The
empirical questions are well-defined once these are answered.
