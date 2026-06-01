# Unequal Agents

Agent-based simulation of wealth inequality. Stylised seven-class
stock-flow ABM (Worker, Maker, Employer, Lender, Rentier, Speculator,
State) with production, extraction, credit, taxation, inheritance, and
a bandwidth-limited cultural-transmission channel.

The project produced four papers (see `papers/`). The headline finding,
formalised in the cap paper, is that an absolute ceiling on
inheritance at around £5--10M is the structural mechanism for raising
the wealth share held by the bottom half of the population from
approximately zero to around one quarter of total household wealth,
without imposing meaningful mortality cost.

## Layout

```
src/                 all Python source: core model + experiments
papers/
  master/            full master paper (30 pp, all findings)
  cap/               Fiscal Studies submission: caps as ownership
  jasss/             JASSS submission: three-lever factorisation
  jeic/              JEIC submission: analytical fixed point + calibration
  alife/             Artificial Life submission: cultural mechanism
docs/                FINDINGS.md, LITERATURE.md, DIALS.md
out/
  data/              JSON summaries + npz arrays
  figures/           PNG outputs by topic
    phase/           3-D phase portrait + shadows + landscapes
    scenarios/       per-scenario plots, survival curves, elasticity
    sweeps/          5 N=100 scenario sweeps
    policies/        11 policies + Sankey + comparison panels
    wealth_tax/      threshold-rate sweeps + fixed-point
    scale_up/        N=10k results
    legacy/          v0 outputs kept for archaeology
review/              referee reports (round 1 and round 2)
```

## Running the simulation

All Python sources live under `src/`. Run from the project root so
that `out/...` paths resolve correctly:

```
python3 src/scenarios.py           # 13 scenarios, ~1 min
python3 src/sweeps.py              # 5 sweeps, ~3 min
python3 src/phase3d.py             # phase portrait, ~30 s
python3 src/policies.py            # 11 policies + switch runs, ~2 min
python3 src/wealth_tax_sweep.py    # 2 wealth-tax sweeps, ~3 min
python3 src/scale_up.py            # N=10k suite + sweep, ~10 min
python3 src/elegant_demo.py        # the headline chart, ~3 min
python3 src/benefits_analysis.py   # ownership + revenue dashboard, ~3 min
python3 src/cap_sweep.py           # cap-value sweep, ~8 min
python3 src/calibration_joint.py   # joint calibration, ~5 min
```

The core library scripts (`sim.py`, `scenarios.py`, `policies.py`) are
imported by everything; the experiment scripts each produce one or two
figures and a JSON summary in `out/`.

## Compiling a paper

```
cd papers/cap
pdflatex paper_cap && bibtex paper_cap && pdflatex paper_cap && pdflatex paper_cap
```

Each paper subfolder is self-contained (its own `paper_*.tex` and
`references.bib`); figures are read from `../../out/figures/`.

## The four-paper split

The same model and the same data underlie all four submissions.  Each
foregrounds a different contribution.

- **cap** (Fiscal Studies). The policy paper. Five interventions
  compared at the joint-calibrated UK baseline. The cap raises the
  bottom-50% wealth share from 0% to 19--25%. Cap and wealth tax are
  complementary instruments serving different goals (revenue vs
  ownership).
- **jasss** (Journal of Artificial Societies and Social Simulation).
  The methodological paper. Productive-flow share metric Φ, Sankey
  visualisation, three-lever factorisation (extended to four-lever
  with the cap).
- **jeic** (Journal of Economic Interaction and Coordination). The
  economic-theory paper. Analytical fixed point
  *w\* = τθ / (τ − r)* and the cap-tax complementarity in revenue
  vs ownership terms. Joint calibration to the UK Sunday Times Rich
  List.
- **alife** (Artificial Life / ALIFE). The cultural-mechanism paper.
  Wealth-coupled cultural-transmission bandwidth, class-specific
  skill-to-wealth elasticity decomposition, open-skill demo, hard
  material constraint as autopoietic check.

The cap paper is the recommended submission target for first
publication.
