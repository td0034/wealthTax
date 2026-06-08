# `papers/` catalogue

## Live papers (for submission)

| folder | paper | pages | target venue | status |
|---|---|---|---|---|
| `wealth_tax/` | _Two per cent is not the answer_ | 13 | Fiscal Studies | submission-ready |
| `growth/` | _What you measure is what you conclude_ | 15 | Fiscal Studies / JEEA | submission-ready |
| `jeic/` | Joint calibration and analytical fixed point | ~25 | JEIC | round-2 ready |
| `jasss/` | Three-lever factorisation methodology | ~22 | JASSS | round-2 ready |
| `alife/` | Cultural-transmission mechanism | ~20 | Artificial Life | round-2 ready |

## Archive / intellectual trail

| folder | paper | status |
|---|---|---|
| `cap/` | Round-1 cap paper | Superseded by `cap_v2/`. Kept as the original empirical content. |
| `cap_v2/` | Round-2 cap paper, ``the cap is the mechanism, enforcement is the constraint'' | Superseded by `wealth_tax/`. Kept as the bridge document that derived the hybrid recommendation. |
| `master/` | 30-page kitchen-sink master paper | Archived. The original synthesis before the venue-specific splits. |

## How the papers relate

```
   master (30 pp, archived)
      |
      |--> jeic   (economic-theory technical) ---+
      |--> jasss  (methodology technical)        |
      |--> alife  (cultural-mechanism technical) |
      |                                          |
      +--> cap (round-1 policy) ---> cap_v2 ---> wealth_tax
                                                    |
                                                    +---> growth
                                                          (Path-B methodological
                                                           companion)
```

## Submission strategy

The recommended submission package for the next round is:

1. **`wealth_tax/`** as the lead policy paper for Fiscal Studies.
   It recommends a 5--10% recurrent wealth tax above £10M and
   establishes the empirical case against the inheritance cap.

2. **`growth/`** as the methodological companion to be submitted
   either to Fiscal Studies as a paired submission or to JEEA as
   the methodological foundation.  It shows the wealth-tax case
   is robust to the choice of growth measure and that the orthodox
   growth measure is dominated by financial-sector compounding.

3. **`jeic/`**, **`jasss/`**, **`alife/`** can be submitted in
   parallel as the technical companions documenting the underlying
   model and methodology.

The `cap_v2/` paper does not need separate submission; its content
is incorporated into `wealth_tax/`.

## Compile instructions

Each paper subfolder has `paper_*.tex` and `references.bib`.  To compile:

```
cd papers/wealth_tax
pdflatex paper_wealth_tax_v1 && bibtex paper_wealth_tax_v1 && \
pdflatex paper_wealth_tax_v1 && pdflatex paper_wealth_tax_v1
```

Same pattern for the other papers.  Figures resolve from
`../../out/figures/` via the `\graphicspath` directive.
