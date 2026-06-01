# Referee report — JASSS

**Manuscript:** *Unequal Agents: An autocatalytic-closure agent-based model
of wealth inequality, cultural transmission, and the design of progressive
wealth taxes*

**Venue framing (per authors):** lead with the autocatalytic-closure metric
(Φ), the phase portrait, and the state-spending result.

**Recommendation: Major revision.**

---

## 1. Summary and overall assessment

The paper presents a seven-class stock-flow agent-based model of a stylised
economy with production, extraction, credit, taxation, inheritance, and a
wealth-coupled skill-transmission mechanism. It proposes a per-tick scalar,
"autocatalytic closure" Φ = F_prod / (F_prod + F_ext), as a viability gauge;
maps thirteen scenarios into a three-dimensional (Gini, Φ, alive) phase
portrait; and argues that state *spending*, not tax revenue, is what moves the
system from an extractive to a self-sustaining regime.

This is a good fit for JASSS in genre and ambition. The intuition-pump framing
is exactly the journal's house style, the political register is welcome here,
and the Sankey visualisation (Fig. 9) is genuinely the clearest artefact in
the paper. The model is transparent and the code is released. I am broadly
sympathetic and I think a revised version belongs in JASSS.

However, the three contributions the authors choose to lead with here are the
three I have the most serious reservations about, in each case because the
**metric that carries the argument is partly an artefact of its own
construction**. I detail these below. None is fatal; all require work before
the claims can stand.

## 2. Major issues

### 2.1 The closure metric Φ does not measure what the text says it measures

The paper repeatedly describes Φ as the share of "value flow between
productive classes" versus "value flow from productive to extractive classes"
(§3.3, abstract). The code tells a different and inconsistent story
(`sim.py`, `step()`):

- **The numerator (F_prod) is wages + state transfers only.** It is the sum of
  maker→worker wages, employer→worker wages, state→worker wages, and
  state→maker purchases (lines 369, 394, 417, 428). It does **not** include
  the maker's value-add (the `output - inputs` term that feeds
  `metabolic_rate`, line 379), nor the employer's captured markup. So the
  numerator is not "value flow between productive classes"; it is "the wage
  bill plus state purchases." Productive value creation is largely absent from
  the very metric named after it.

- **The denominator's extractive term mixes transfers with pure wealth
  creation.** Rent (line 440) and interest (line 507) are genuine transfers
  from one agent to another. But capital return (line 446–448,
  `gain = r.wealth * d.capital_return`) and speculator gains (line 451–455)
  are *multiplicative wealth creation on an agent's own stock* — they are not
  flows *from* productive classes at all. The paper's own definition ("value
  flow **from productive to extractive** classes") is violated by two of the
  four terms in F_ext. Worse, the maker's analogous wealth creation
  (`metabolic_rate`) is excluded from the numerator while the rentier's
  (`capital_return`) is included in the denominator. The metric is therefore
  asymmetric in exactly the direction that produces the paper's headline
  contrast: production-side creation is invisible, extraction-side creation is
  counted as extraction.

- **Speculator losses are dropped.** Only `delta > 0` is added to F_ext
  (line 454). Negative speculative returns do not net out. This biases F_ext
  upward whenever volatility is high.

**Consequence.** Φ is closer to "wage-and-transfer flow as a share of
(wage-and-transfer flow + rent + interest + gross capital/speculative gains)."
That is a defensible quantity, but it is not the productive-vs-extractive
ratio the paper claims, and the gap between the two is doing rhetorical work.
The "centuries-old productive/extractive distinction" framing (Mazzucato,
Kauffman) is being borrowed for a quantity that does not implement it.

*Required:* either (a) redefine Φ so the numerator and denominator are
treated symmetrically (e.g. count maker value-add as productive creation, or
exclude all pure-creation terms from both sides and keep Φ a ratio of genuine
inter-class *transfers*), or (b) rename the metric and drop the
productive-vs-extractive interpretation, presenting Φ honestly as a
wage-flow-share index. Option (a) is the stronger paper. Whichever is chosen,
the abstract and §3.3 must match the code.

### 2.2 The state-spending result is partly definitional

The flagship JASSS finding is that toggling state spending flips Φ from 0.006
to 0.439 (§5.2). But state→worker wages and state→maker purchases are added
**directly to the numerator** (lines 417, 428). Turning on state spending
mechanically increases F_prod by construction. The finding that "state
spending raises the wage-flow share" is therefore close to a tautology given
how Φ is built.

This does not make the result uninteresting — the *shape* of the
tax_vs_ubi surface (closure peaking at moderate UBI ≈ 0.2, not maximum UBI) is
a real and non-obvious feature, because UBI is *not* in the numerator and yet
moderate UBI raises Φ via induced maker purchases. That is the genuinely
informative part and it should be promoted. But the headline "spending not
revenue flips the regime" needs to be stated with the caveat that spending
channels are partly constitutive of the metric, and the interesting claim
restated as: *which* spending modes raise Φ beyond their direct contribution.
The state_action sweep (purchases dominate employment) is the right evidence
for that and is currently under-used.

### 2.3 The phase portrait rests on a contaminated Gini axis and on "inspection"

Two problems with Fig. 3 / Table 2:

1. **The Gini axis includes the State**, which is the richest agent in most
   scenarios (e.g. socialist Φ = 0.811 but Gini = 0.81; the state holds the
   redistributed wealth). A "socialist" regime reporting Gini 0.81 is a red
   flag that the metric is measuring state accumulation, not household
   dispersion. Since Gini is one of the three phase-space axes, the geometry
   of the portrait — and the claim of "three clearly separated regions" — is
   not interpretable until the State is removed from the distribution. (See
   the cross-cutting note in `00_overview.md`.)

2. **Regime assignment is "by inspection of Figure 3"** (Table 2 caption).
   For a JASSS methods contribution this is too informal. Three clusters in a
   3-D scatter of 13 points should be established with an actual clustering
   procedure (even k-means with a silhouette score, or a stated threshold rule
   applied uniformly). As it stands `pure_speculation` is labelled
   "extractive/collapse" — an admission that the partition is not clean. The
   Φ ≈ 0.05 "death threshold" (§5.1) is asserted from the same eyeballing and
   needs to be shown, e.g. as survival vs Φ across all runs.

### 2.4 Reproducibility and the ODD protocol

JASSS effectively expects an ODD (or ODD+D) description. The paper has a
prose mechanics section and a dial appendix, which is a good start, but there
is no ODD, no statement of scheduling/update order as a protocol, and the
seed counts are thin for the headline claims (8 seeds at N=100, but only **3
seeds** for the N=10k policy table and **2 seeds** for the scale-up sweep).
Several "indistinguishable" and "identical" claims (§5.7) are made with no
dispersion reported. Please add: an ODD section; IQR or CI bands on the policy
tables; and a minimum of the JASSS-conventional seed count for any claim of
equivalence or separation.

## 3. Minor issues

- **Gini formula** (line 275–283) clips net worth to ≥ 0 before computing,
  so indebted agents register as zero-wealth rather than negative. State the
  convention; it matters in the credit-stressed regimes.
- **§5.1** "follows into collapse within ≈100 ticks" — show the survival
  curves; this is currently an assertion.
- **Fig. 9 (Sankey)** is excellent and under-sold. I would move it earlier and
  use it as the reader's first encounter with Φ. Please give the flow
  percentages error bars or note they are single-summary-window means.
- **Scenario count inflation.** Thirteen scenarios is a lot to carry; several
  (creditless, pure_speculation) are mentioned once. Consider demoting the
  marginal ones to an appendix to sharpen the portrait.
- **Terminology.** "autocatalytic closure" borrows heavily from Kauffman /
  Hordijk but Φ is not an autocatalytic-set closure in their technical sense
  (no catalysis graph, no RAF). The paper is honest about this in §6.1, but
  the *name* will mislead JASSS readers who know the RAF literature. Consider
  "productive-flow share" as the primary term, with the autocatalysis
  lineage as motivation.

## 4. References

Coverage is good and the positioning against Cardoso et al. (2025) and
Spangler & Sarkar (2022) is appropriate. For a JASSS audience I would add:
- A NetLogo/Sugarscape lineage citation in the *model* section, not just the
  bib — readers will want to place the seven-class design against
  Epstein & Axtell (1996) / Wilensky (1998), both already in `references.bib`
  but uncited in the text.
- The kinetic-tax ABM line (Bertotti & Modanese) is discussed in the project's
  `LITERATURE.md` but **not cited in the paper** despite being the closest
  precedent for the state-spending claim. This is a notable omission given §5.2
  is a lead result here; please cite and differentiate.
- `dragulescu2000statistical`, `wold1957model`, `benhabib2011distribution`,
  `saez2016wealth`, and `hashimoto2019open` are in the `.bib` but never cited.
  Either cite or prune.

## 5. Verdict

A revised paper that (i) makes Φ internally consistent and renames or
recaptions it to match the code, (ii) re-runs all distributional metrics with
the State excluded, (iii) reframes the state-spending result around the
non-definitional part (spending *mode*), and (iv) replaces "by inspection"
clustering with a stated rule, would be a solid JASSS paper. The model is
honest, the visualisations (Sankey especially) are strong, and the political
relevance is real. The work to get there is substantial but mechanical, not
conceptual. **Major revision.**
