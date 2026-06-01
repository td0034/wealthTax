# Referee reports — *Unequal Agents* working paper

Three independent critical reviews, one per target venue, written in each
journal's idiom and leading with the contributions the paper itself proposes
to foreground there (paper §6.3, "Positioning for publication").

| File | Venue | Lead contributions reviewed | Verdict (this referee) |
|---|---|---|---|
| `01_JASSS_review.md` | Journal of Artificial Societies and Social Simulation | autocatalytic-closure metric, phase portrait, state-spending result | Major revision |
| `02_JEIC_review.md` | Journal of Economic Interaction and Coordination | inheritance trapdoor, top-tier-does-not-bind, wealth-tax design factorisation | Reject and resubmit |
| `03_ALIFE_review.md` | Artificial Life / ALIFE | wealth-coupled cultural-transmission bandwidth, cultural-vs-economic-equality asymmetry | Major revision (weak accept as conference paper) |

All three reviews were prepared with access to the source (`sim.py`,
`scenarios.py`, `policies.py`, `wealth_tax_sweep.py`, `scale_up.py`) and the
project docs. Where a critique turns on a modelling detail I cite the
mechanism in the code, because all three venues expect a code release and a
referee is entitled to read it.

A cross-cutting finding shared by all three reports, stated once here:

> **The State agent is included in the Gini and top-share statistics and is
> the single richest agent in most policy runs (state wealth 16,300–39,700
> model units vs a top private agent around 270–4,200).** The paper concedes
> this in §7.2 as a "practical near-term limitation" with "qualitative
> findings unaffected." Every referee below disputes the "unaffected" claim
> for at least one headline result. This is the single most important fix and
> it is cheap: re-run percentile/Gini metrics with the State excluded before
> resubmission to any venue. Until that is done, the distributional results
> are not assessable.
