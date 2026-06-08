# Unequal Agents

[![CI](https://github.com/td0034/wealthTax/actions/workflows/ci.yml/badge.svg)](https://github.com/td0034/wealthTax/actions/workflows/ci.yml)
[![Licence: MIT (code) / CC BY 4.0 (papers)](https://img.shields.io/badge/licence-MIT_%2F_CC--BY_4.0-blue.svg)](LICENCE)

A playground for simulating wealth taxes.

This repository is an agent-based simulation of a stylised UK-like
economy that you can use to test fiscal policies on three structural
outcomes: who owns the country, what the economy actually does, and
who survives.  Out of the box, the model lets you compare an
inheritance cap, the Zucman 2% wealth tax, a steeper hybrid wealth
tax, an interest ban, and various spending packages, against a
calibrated status-quo baseline.

The simulation is the artefact.  Several papers grew out of it (see
`papers/`), but the headline thing this repository is for is *try
your own policy and see what happens*.  Change a tax rate, change a
threshold, change the capital return, change the demographic
assumptions, see how the wealth distribution, productive output, and
population survival respond.

## What is in here

Seven agent classes (Worker, Maker, Employer, Lender, Rentier,
Speculator, State) move money around each tick by producing,
extracting, lending, renting, taxing, and inheriting.  Skills
transmit imperfectly between generations through a wealth-dependent
bandwidth channel, so wealth concentration narrows the population
skill base over time.  The model is calibrated to UK Wealth and
Assets Survey targets (top-1%, top-10%, Pareto slope, survival
rate).

You can think of it as a digital sandbox where the rules of a
financialised economy are explicit, and where the consequences of
changing those rules can be measured under reproducible conditions.
It is not a forecasting tool.  It is an intuition pump for stylised
mechanisms, calibrated against real distributional data.

## A worked example

The single sharpest finding from the playground:

| arm | bottom-50% wealth share | billionaires | top-10% wealth share |
|---|---|---|---|
| status quo | 0.0% | 800 | 100% |
| Zucman 2% above £10M | 0.6% | 800 | 99% |
| £5M inheritance cap | 19% | 2 | 54% |
| **5% wealth tax above £10M** | **20%** | **0** | **62%** |
| 10% wealth tax above £10M | 42% | 0 | 19% |

The Benhabib fixed-point argument predicts that a wealth tax with
rate $\tau$ above threshold $\theta$ produces a finite ceiling on
top wealth only if $\tau$ exceeds the capital return $r$.  In our
calibration $r = 0.08$.  The Zucman 2% sits below the threshold and
the simulation shows it does not move the structural distribution at
the top, even though it raises substantial revenue.  Cross $\tau = r$
and the wealth tax starts doing structural work.  By 10%, top-10%
share has dropped from 100% to 19%.

You can reproduce this run in about ten minutes on a normal laptop.
Change the rate, the threshold, or the calibration and see what
breaks.

## Quickstart

```bash
git clone git@github.com:td0034/wealthTax.git
cd wealthTax
pip install numpy matplotlib

# Replicate the Zucman-vs-cap-vs-hybrid headline:
python3 src/round2_hybrid.py
python3 src/round2_hybrid_loose_ends.py

# Outputs go to out/data/ (JSON) and out/figures/ (PNG).
```

If you want to try your own policy: copy `src/round2_hybrid.py`,
change the `ARMS` dictionary at the top, run it.  All the dials are
on the `Dials` dataclass in `src/sim.py`.  The most useful ones:

- `capital_return`: the return rate on rentier wealth per tick
- `wealth_tax_tiers`: tuple of (threshold, rate) pairs above which
  the wealth tax bites
- `inheritance_cap`: hard ceiling on bequest size
- `inheritance_tax_rate`: flat clawback at death
- `inheritance_capture_rate`: enforcement effectiveness (0 to 1)
- `wealth_tax_capture_rate`: enforcement on the wealth tax
- `ubi`, `state_employs_fraction`, `state_buys_maker_output`:
  three knobs for state-spending packages

The `Dials` docstring in `src/sim.py` lists everything.

## What grew out of the playground

The simulation produced several papers in `papers/`.  The two that
matter most for someone arriving here cold:

- **`papers/wealth_tax/`**.  The recommendation paper: a recurrent
  wealth tax of 5--10% above £10M, phased in over 5--10 years.
  Dominates the inheritance cap on every metric and is robust to
  enforcement leakage in the range where the cap collapses.
- **`papers/growth/`**.  The methodological paper: the orthodox
  ``wealth tax depresses growth'' result holds only if you measure
  growth in a way that counts the rentier-lender deposit loop as
  growth.  Under any productive-output or capability measure, the
  wealth tax raises growth by 9--15%.

Other papers under `papers/` are technical companions (JEIC, JASSS,
ALIFE) and the historical trail (`cap/`, `cap_v2/`, `master/`)
showing how the wealth-tax recommendation was derived.

For the full project state and the planned next extension (an
endogenous-growth paper) see `PROJECT_STATE.md` and
`docs/PATH_C_PLAN.md`.

## Layout

```
PROJECT_STATE.md     Top-level overview of the intellectual arc
src/                 All Python source code
  INDEX.md           Catalogue of scripts by purpose
  sim.py             The core model: Dials, Agent, step()
  ...                Experiment, analysis, and figure scripts
papers/              Paper drafts (see papers/INDEX.md)
review/              Findings, critiques, strategy memos
docs/                FINDINGS, LITERATURE, DIALS, PATH_C_PLAN
out/                 Generated data (JSON) and figures (PNG)
```

## What this repo is not

- **Not a forecasting model.**  The agents are stylised, the
  population is small (N = 10,000), and many real features are
  absent (firms, banks, monetary policy, international trade,
  housing).  Results are about mechanisms, not predicted GDP next
  year.
- **Not a finished policy proposal.**  The papers make policy
  arguments that go through peer review; the simulation is one
  input among several.
- **Not anti-billionaire vendetta.**  The model is honestly
  symmetric in how it treats all classes.  The wealth tax wins on
  the measures we report because the structural mechanism
  (compounding above a finite ceiling) is robust to the wide range
  of parameter regimes tested, not because the model is rigged
  against the top.

## Honest limitations

Worth knowing before reading the headline numbers as truth:

- The model has no growth term in the orthodox sense (no R&D, no
  capital deepening as a separate sector).  The growth paper makes
  the most it can of the level effects; Path C is the planned
  extension.
- The capital-flight elasticity is a single rate, not a structural
  decision.  The flight stress test is an upper bound on what
  flight could destroy, not a precise estimate.
- The model is closed-economy.  International coordination effects
  are treated qualitatively.
- The calibration is to the UK 2008--2024 case.  Other countries
  may have different parameter regimes (the comparable-country
  test is Path C).

## Contributing

Forks, pull requests, and new policy arms welcome.  If you find a
parameter regime where the headline finding flips, that is
genuinely interesting and worth opening an issue.  If you find a
bug in `sim.py` that changes the headline numbers, that is even
more interesting and worth a pull request.

## Licence

Dual-licenced.

- **Code** (everything outside `papers/`) is MIT-licenced.  See
  `LICENCE`.  You can fork, modify, and use the simulation under
  the standard MIT terms.
- **Papers** (everything inside `papers/`) is CC BY 4.0.  See
  `LICENCE_papers.md`.  You can share and adapt with attribution.

## Acknowledgements

Original inspiration: a Gary Stevenson / Gabriel Zucman discussion
of an inheritance cap.  The framing of the orthodox-vs-alternative
growth measures owes a great deal to Diane Coyle, David Pilling,
Mariana Mazzucato, and the Stiglitz-Sen-Fitoussi Commission.  The
hybrid wealth-tax recommendation builds on Saez and Zucman's G20
framework with the rate level pulled up to the Benhabib analytical
threshold.

If you use this simulation in published work, citation of the
papers in `papers/` is welcome.
