# Unequal Agents

Agent-based simulation of wealth inequality.  Stylised seven-class
stock-flow ABM (Worker, Maker, Employer, Lender, Rentier, Speculator,
State) with production, extraction, credit, taxation, inheritance,
and a bandwidth-limited cultural-transmission channel.

Six papers and counting.  The project has evolved through three
phases: round 1 (cap proposal), round 2 (Stewart/Hunt stress testing,
hybrid wealth-tax derivation), and growth (Path B, the
GDP-is-an-artefact case).  Headline findings, in current form:

1. **A recurrent wealth tax of 5--10% above £10M dominates both
the inheritance cap and the Zucman 2% proposal** on every
distributional metric tested, including in the orthodox-favoured
parameterisations.  Documented in `papers/wealth_tax/`.

2. **The orthodox claim ``wealth tax depresses growth'' is a
measurement artefact.**  Under any growth measure that distinguishes
real production from financial-sector compounding, the wealth tax
raises growth by 3--15%.  The CGDP-style growth in the status quo is
the model's representation of the UK 2008--2024 financialisation
pattern.  Documented in `papers/growth/`.

3. **The inheritance cap is in an unresolvable enforcement bind.**
It needs near-perfect (>95%) capture to deliver any distributional
effect but cannot get that capture politically.  The hybrid wealth
tax bypasses the bind because recurrent flow extraction does not
have the dynastic-recompounding nonlinearity that destroys the cap.
Documented in `papers/cap_v2/`.

For the full project state see `PROJECT_STATE.md`.

## Layout

```
PROJECT_STATE.md     Top-level overview of the intellectual arc and
                     current state of work
src/                 All Python source code
  INDEX.md           Catalogue of scripts by paper and purpose
  sim.py             The core agent-based model
  ...                ~50 experiment, analysis, and figure scripts
papers/              All paper drafts
  INDEX.md           Catalogue with submission strategy
  wealth_tax/        Round-3 lead policy paper for Fiscal Studies
  growth/            Round-3 methodological companion
  jeic/, jasss/,
  alife/             Technical companions (round-2 ready)
  cap_v2/, cap/,
  master/            Intellectual trail (archived for context)
review/              Referee reports, adversarial critiques, findings
  INDEX.md           Catalogue with reading order
docs/                FINDINGS.md, LITERATURE.md, DIALS.md
                     PATH_C_PLAN.md (next research extension)
out/
  data/              JSON summaries from all experiments
  figures/           Figures by topic: round2/, growth/, scenarios/,
                     policies/, etc.
```

## Quickstart: reproducing the headline papers

```
# Wealth-tax paper (5--10% above £10M is the right policy)
python3 src/round2_hybrid.py
python3 src/round2_hybrid_loose_ends.py
python3 src/round2_hybrid_figures.py
cd papers/wealth_tax && pdflatex paper_wealth_tax_v1 && \
    bibtex paper_wealth_tax_v1 && \
    pdflatex paper_wealth_tax_v1 && pdflatex paper_wealth_tax_v1

# Growth paper (the GDP-is-an-artefact case)
python3 src/growth_portfolio.py
python3 src/growth_seeds20.py
python3 src/growth_cis.py
python3 src/growth_robustness.py
python3 src/growth_figures.py
python3 src/growth_robustness_figures.py
cd papers/growth && pdflatex paper_growth_v1 && \
    bibtex paper_growth_v1 && \
    pdflatex paper_growth_v1 && pdflatex paper_growth_v1
```

Outputs go to `out/data/` (JSON) and `out/figures/` (PNG).  The PDF
ships in the paper folder.

## Where to start reading

- **Policy people**: `papers/wealth_tax/paper_wealth_tax_v1.pdf`,
  then `papers/growth/paper_growth_v1.pdf`.
- **Methodology people**: `papers/jeic/`, `papers/jasss/`,
  `papers/alife/`.
- **For the project history**: `PROJECT_STATE.md` and
  `review/INDEX.md`.
- **For what comes next**: `docs/PATH_C_PLAN.md`.
