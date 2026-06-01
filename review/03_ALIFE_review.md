# Referee report — Artificial Life / ALIFE

**Manuscript:** *Unequal Agents: An autocatalytic-closure agent-based model
of wealth inequality, cultural transmission, and the design of progressive
wealth taxes*

**Venue framing (per authors):** lead with the wealth-coupled
cultural-transmission bandwidth mechanism and the cultural-vs-economic-equality
asymmetry.

**Recommendation:** Major revision for *Artificial Life* (journal); weak
accept for the *ALIFE conference* proceedings as an 8-page version, conditional
on reframing. The cultural-transmission contribution is the most original in
the paper and the best fit for this venue's editorial profile, but the model
as built sits in tension with the journal's core commitment to open-endedness,
and the central "novel mechanism" is thinner than its billing.

---

## 1. Overall assessment

Of the three target venues this is where the paper's *sensibility* fits best,
and the authors are right that the wealth-coupled bandwidth mechanism and the
cultural/economic-equality asymmetry are the contributions most consonant with
ALIFE. The asymmetry result — equalising cultural transmission at birth does
*not* equalise wealth, because cultural concentration is downstream of economic
concentration — is a genuinely nice negative result and the kind of
counterintuitive systemic finding ALIFE likes. The honesty of the writing is a
credit to the authors.

That said, an ALIFE referee will press hardest on two things the paper is
currently weak on: **open-endedness** and **mechanistic depth of the novel
coupling**. Both need work.

## 2. Major issues

### 2.1 The cultural model is explicitly closed, which sits awkwardly at ALIFE

The paper concedes (§7.2) that "no skill dimension can appear that did not
exist at t=0": skills are a fixed K=5 vector, transmission can only subset and
mutate existing dimensions, and `skill_mutation_rate` resets a dimension to a
fresh Beta(2,2) draw rather than introducing genuine novelty (`sim.py`,
lines 231–234). For most venues this is a routine limitation. For *Artificial
Life* it is closer to a category problem: the journal's defining concern is
open-ended evolution and the emergence of novelty, and this model has neither
by construction. The "cumulative culture" framing (Henrich, Lewis & Laland) is
about the *build-up* of complexity over time — but nothing can build up here;
breadth can only erode from an initial endowment toward a floor set by the
mutation rate.

This needs to be confronted head-on, not relegated to a limitations
paragraph. Two honest routes:

- **Reframe** the contribution as *cultural erosion / loss* under economic
  pressure rather than cultural *evolution*. That is what the model actually
  does (the `memory_starved` and `feudal` collapse-of-breadth results), it
  connects cleanly to Henrich's Tasmania case (already cited), and it is a
  legitimate ALIFE topic. The Tasmania/Vaesen-critique debate
  (`LITERATURE.md` flags Vaesen et al. 2016) should be engaged here.
- **Or extend** the mechanism so new skill dimensions can appear
  (recombination of existing dims, a TAP-style adjacent-possible expansion à
  la Hordijk & Kauffman 2023, which you already cite). This would make it a
  true open-ended-culture paper and would be the stronger ALIFE contribution,
  but it is a research extension, not a revision.

For the conference paper I would accept the reframing route; for the journal I
would want to see at least a serious discussion of why a closed skill space is
the right idealisation.

### 2.2 The novel coupling saturates and so is barely exercised

The headline mechanism is "the number of skill dimensions a child inherits
scales with the parent's wealth." In code (`make_agent`, lines 221–225):

```
bandwidth_dims = clip(b0·5 + bw·(parent_wealth/100), 1, 5)
```

With the defaults used in most runs (b0 = 0.5, bw = 0.5), the base term is
already 2.5 dimensions, and the wealth term reaches the remaining 2.5
dimensions at `parent_wealth = 500` units — i.e. *any* parent above that is
clamped to the full 5 dimensions. Since rentiers, employers and successful
makers routinely exceed this, the wealth-coupling is effectively a step
function that is saturated for the wealthy and only graded across the poor. The
"bandwidth scales with wealth" story is, mechanically, "the poor lose a
dimension or two; everyone else keeps all five." That is a much weaker and more
brittle mechanism than the framing implies, and the fourfold breadth range
reported in the `memory` sweep (§5.5) is being driven mostly by the *base*
parameter b0, not by the wealth coupling that is claimed as the novelty.

*Required:* report the breadth response decomposed into the b0 effect and the
bw effect separately (the sweep data already supports this), and show the
realised distribution of `bandwidth_dims` across classes in a representative
run. If the wealth coupling turns out to contribute little once b0 is
controlled, the novelty claim must be scaled back accordingly. If it
contributes a lot in some regime, show that regime. Right now the mechanism's
actual bite is undocumented.

### 2.3 The asymmetry result is good but the causal claim is over-stated

The conclusion "cultural inequality is downstream of economic inequality; the
causal arrow does not run the other way *in this model*" (§5.5) is well hedged
with "in this model," which I appreciate. But note that the model *cannot*
produce the reverse arrow by construction: skills feed wealth only weakly
(worker wage scales with skills 0–1; maker multiplier scales with generative
skill, lines 351, 376), while wealth feeds skills directly through the
bandwidth gate. The architecture builds in the asymmetry's direction. So the
result "culture doesn't equalise wealth" is partly a consequence of how thin
the skill→wealth channel is, not only an emergent finding. Please show the
strength of the skill→wealth channel (e.g. wage and output elasticity to
skill) so the reader can judge how much of the asymmetry is mechanism vs
assumption. An ALIFE referee will not accept a structural asymmetry being
reported as an emergent one without this.

### 2.4 Open-endedness of the *economic* layer is also absent — and that's the ALIFE-relevant gap

ALIFE's interest in this model is as a coupled cultural-economic system. But
the economic layer is itself non-open-ended in ways that matter for the
cultural result: fixed agent-type proportions, fixed employer count (no firm
formation), no new occupational categories. So the only thing that can
"evolve" is the wealth distribution and the skill subset, within fixed slots.
For a *JASSS* or *JEIC* audience that is fine; for ALIFE it undercuts the
framing of the system as alife. I would either lean into a minimal-model
defence (cite the alife tradition of deliberately closed minimal worlds) or
acknowledge that the alife contribution is the *metric and the coupling*, not
the system's open-endedness.

## 3. Minor issues

- **`cultural_diversity` vs `cultural_breadth`.** The paper reports breadth
  (mean count of non-zero skills) but the code also computes diversity
  (per-dimension variance, line 286–292). The variance measure is arguably the
  more alife-relevant one (homogenisation of a population). Consider reporting
  both; a collapse in *diversity* under wealth concentration would be a
  stronger statement than a collapse in mean breadth.
- **Knowledge-lost metric** (line 609–610) is the parent's untransmitted skill
  mass, but mutation can *add* mass back in the child, so the metric is a noisy
  net rather than a true loss. Define it precisely.
- **The autocatalytic-closure metric** (Φ) is presented as a second
  contribution and pitched partly to ALIFE via the Kauffman/Hordijk lineage.
  Be careful: the metric is *not* an autocatalytic-set property in the RAF
  sense (no catalysis graph), and an ALIFE audience is exactly the audience
  that knows the RAF literature (Hordijk & Steel 2004; Hordijk & Kauffman
  2023, both cited). Using "autocatalytic closure" for a flow ratio will draw
  fire here more than at the other venues. Rename or heavily caveat. (See also
  the closure-metric construction critique in the JASSS report, which applies
  identically: F_prod excludes maker value-add while F_ext counts capital
  return — an asymmetry an ALIFE reader will spot.)
- **Hashimoto, Oka & Ikegami (2019)** is cited as a methodological cousin.
  Good — and the `LITERATURE.md` honesty about there being *no* Ikegami-lab
  economic-inequality work should be carried into the paper so no reviewer
  feels the alife lineage is being oversold.

## 4. References

The cultural-evolution coverage is appropriate (Cavalli-Sforza & Feldman;
Boyd & Richerson; Henrich; Lewis & Laland; Henrich & Gil-White). Two additions
an ALIFE referee would expect:
- **Charbonneau & Bourrat (2021)** on the "grain problem" — the 5-dimensional
  skill vector is a grain choice and should be defended as such (this is noted
  in `LITERATURE.md` but not in the paper).
- A genuine open-ended-evolution citation (beyond Hashimoto et al.) if the
  alife framing is kept — e.g. the OEE / novelty-search literature — so the
  closed skill space is positioned against the open-ended ideal explicitly.

## 5. Verdict

The cultural-transmission contribution is the freshest thing in the paper and
the right thing to lead with here, but it is currently (i) built on a closed
skill space that an *Artificial Life* audience will challenge on principle,
(ii) carried by a coupling that saturates and so is barely exercised at default
parameters, and (iii) reporting a structurally built-in asymmetry as an
emergent one. All three are addressable. Reframed as *cultural erosion under
economic pressure*, with the bandwidth coupling's actual bite documented and
the skill→wealth channel quantified, this is a good ALIFE conference paper and
a plausible *Artificial Life* journal paper. **Major revision (journal); weak
accept (conference, 8-page reframed version).**
