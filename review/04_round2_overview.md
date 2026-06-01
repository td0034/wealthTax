# Referee reports — *Unequal Agents*, ROUND 2 (revised manuscript)

The manuscript has been substantially revised and now responds, explicitly and
in good faith, to all three round-1 reports. I checked the revisions against
the source, not just the prose. **The claimed code changes are real**, which is
worth stating plainly up front because it is unusual:

| Round-1 demand | Implemented? | Where (verified) |
|---|---|---|
| Exclude State from Gini/top-share (CC-1) | **Yes** | `sim.py:711–743`; `gini_with_state` retained alongside |
| Make Φ symmetric (CC-2) | **Yes** | maker value-add `sim.py:466`, employer markup `:490`, speculator now excluded from both sides `:538–548` |
| Mortality-corrected metrics | **Yes** | `peak_wealth`/`recent_deaths`, `mortality_corrected_values` `sim.py:358–408` |
| Log-wealth bandwidth, exercised (AL-2) | **Yes** | `sim.py:230–235`; decomposition fig + realised-bandwidth-by-class |
| k-means regimes, not "by inspection" | **Yes** | `clustering.py`; silhouette reported |
| ODD protocol | **Yes** | Appendix A |
| Survival curves | **Yes** | `survival.py`, Fig. (survival_scenarios) |
| Clean tax×spend×inheritance factorial | **Yes** | `factorial.py`, Table 4 |
| Analytical fixed point for top-tier result | **Yes** | `fixed_point.py`, §5.8, w* = τθ/(τ−r) |
| Skill→wealth elasticity quantified | **Yes** | `elasticity.py`, Table 6 |
| Direct Spangler & Sarkar test | **Yes** | `spangler.py`, §5.6 |
| Open-ended skill demo | **Yes** | `open_skills.py`, §5.10 |
| Partial calibration to UK tail | **Yes** | `calibration.py`, §5.9 |
| Regressive-trap retraction | **Yes, fully** | §5.12 |

This is a genuinely improved paper. Several round-1 concerns are resolved
outright. The retraction of the regressive trap and the honest re-test of the
Spangler comparison are to the authors' credit.

## The one blocking problem this round is internal consistency

**The revision updated the tables, the abstract, and the new sections, but left
stale numbers from the previous draft embedded in the prose of at least five
places.** Adjacent paragraphs now contradict each other. I verified against the
regenerated data (`out/data/policies_summary.json`) that the *new tables* carry
the authoritative numbers and the *prose* is the stale part. Concretely:

1. **§5.6 "Three observations"** (the three numbered paragraphs after
   Table 5) state "identical alive (77 vs 77), identical top-10 share (0.88)",
   "zucman_2pct_hoard gives 49 alive ... uk_tory's 52", and reform "lowest
   closure (0.007)". **Table 5 — and the regenerated data — say 80/80, top-10
   0.54; hoard 51 vs tory 57; reform Φ 0.020.** The prose is the old draft
   verbatim.

2. **§5.7 scale-up** has two adjacent paragraphs giving *different numbers for
   the same comparison*: the "properly tested" paragraph reports the Zucman
   flat-vs-progressive contrast as (8053, 0.457) vs (8059, 0.464) at 10 seeds,
   then four lines later the old text reports it as "(7735, 0.299, 69) vs
   (7726, 0.303, 63), indistinguishable within seed noise" and "16
   billionaires ... 100 billionaires" against Table 7's 19 and 97.

3. **The billionaire-count figure caption** still says "mean across 3 seeds"
   and "16 under Tory to 100 under Reform"; Table 7 says 10 seeds, 19, 97.

4. **§5.9 Pareto** prose still uses "16 billionaires ... 600×" and the
   Sankey §5.3 still cites socialist "Φ = 0.81" against Table 2's 0.890.

5. **Conclusion** says "we have identified six findings"; the abstract
   enumerates eight (i–viii).

Until a single numerical-consistency pass reconciles every in-text number with
the regenerated tables, a referee cannot tell which figures are the paper's
actual claims. This is mechanical to fix but it is disqualifying as-is, because
the contradictions sit on the headline policy numbers.

## A second cross-cutting presentational problem

The body of the paper now talks *to the reviewers* rather than to readers. It
contains "A reviewer pointed out," "the JEIC reviewer asked," "the ALIFE
reviewer flagged," and internal revision codes "CC-1," "CC-2," "AL-2." This
scaffolding belongs in a separate response-to-reviewers letter. In the
published manuscript it should be deleted and the improved analysis presented
as the paper's own, not as a rebuttal. (The intellectual honesty is admirable;
the venue is wrong.)

## Files this round

| File | Venue | Round-2 verdict |
|---|---|---|
| `05_round2_JASSS.md` | JASSS | Minor-to-major revision (consistency pass + repositioning) |
| `06_round2_JEIC.md` | JEIC | Major revision (was: reject & resubmit) — large step up |
| `07_round2_ALIFE.md` | Artificial Life / ALIFE | Accept-with-minor-revisions as conference paper; major for journal |

The trajectory is strongly positive. None of the round-2 issues are conceptual
the way round-1's were; they are consistency, presentation, and a few residual
modelling-justification gaps detailed per venue.
