# Referee report — Artificial Life / ALIFE (Round 2)

**Recommendation: Accept with minor revisions as a conference (ALIFE) paper;
major revision for the *Artificial Life* journal.** The three round-1 concerns
— the closed skill space, the saturating (barely-exercised) bandwidth coupling,
and the asymmetry being structural rather than emergent — are each addressed,
two of them well. The cultural contribution is now the paper's most defensible
novelty.

---

## 1. Round-1 concerns: status

- **AL-1 (closed skill space).** Honestly confronted. The cultural section is
  retitled "cultural *erosion* under economic pressure" (§5.6), explicitly
  disclaims the cumulative-culture framing, and a stand-alone open-ended
  skill-discovery demonstration is added (§5.10, `open_skills.py`) showing the
  active skill pool growing from 5 to ~10 with novelty rate coupled to
  log(parent wealth). This is the right response: reframe the main model as
  erosion, and show the mechanism *can* be opened up. Good.

- **AL-2 (saturating coupling).** Fixed: the linear coupling is replaced with a
  log-wealth form (`sim.py:230–235`), and Fig. (bandwidth_decomp) decomposes
  the breadth response into b0 and bw and shows the realised
  bandwidth-by-class. Verified in code. This was my most concrete round-1 ask
  and it is properly done.

- **AL-3 (structural vs emergent asymmetry).** Addressed with the
  skill→wealth elasticity regression (Table 6): workers/makers have strong
  skill→wealth fits (R² 0.91/0.98), employers/lenders weak (0.05/0.35). This is
  a real, AL-relevant result — the cultural/economic asymmetry is now shown to
  follow from one half of the economy having skill→wealth feedback and the
  other not, rather than from a wiring choice. This is the best new material in
  the paper for this venue.

## 2. The novelty is now honestly a minority contributor — keep it that way

The decomposition (§5.6) shows b0 contributes a breadth range of 2.99 and the
*novel* wealth-coupling bw contributes 0.87. So the wealth coupling explains
roughly a fifth of the breadth variation. The paper is now honest about this
("the b0 axis still dominates"), which is the correct posture — but make sure
the abstract and contribution claims do not drift back toward implying the
coupling is the dominant driver. The honest framing is: *the wealth coupling is
a real, graded, secondary channel, and the AL-novel result is the elasticity
asymmetry it helps reveal*, not the coupling's magnitude.

## 3. Residual issues

### 3.1 The open-skills "wealth-coupled discovery" claim is not yet supported

§5.10 states most novelty events fire on worker parents (because workers are
numerous) but that high-wealth parents "contribute disproportionately to their
numbers." The figure shows the discoverer-wealth distribution, but the claim of
*disproportionate* contribution requires a **per-capita discovery rate by
class** (discoveries per agent-generation, normalised by class size), not a raw
count dominated by worker abundance. As written, "most discoveries are by
workers" is consistent with novelty being purely a function of headcount with
no wealth coupling at all. Add the per-capita rate, or soften the claim to "the
discovery channel is wealth-coupled by construction; whether it concentrates
novelty per capita in wealthy lineages is shown in the right panel" — and make
the right panel actually show that.

### 3.2 Elasticity table is missing two of the seven classes

Table 6 reports WORKER, MAKER, EMPLOYER, LENDER but not RENTIER or SPECULATOR,
even though the surrounding text reasons about "the rentier and lender layers."
For the asymmetry argument the rentier row is the most important one (rentiers
are the archetypal extractive class). Add RENTIER and SPECULATOR rows, or
explain why they are omitted (e.g. too few observations); the argument is
currently making a claim about rentiers without showing them.

### 3.3 The title still leads with "autocatalytic-closure"

For a RAF-literate ALIFE audience this remains the most exposed framing. The
authors have added the correct disclaimer in §3.3 (Φ is not an autocatalytic
set in the Hordijk–Steel sense), which I appreciate, but the *title* and
running framing still foreground "autocatalytic-closure." At this venue
specifically I would retitle around "productive-flow share" (the authors'
own honest alternative) and keep the Kauffman/Hordijk lineage as motivation in
the body. This is a venue-specific recommendation; it would not be my advice for
JASSS.

## 4. Open-endedness of the economic layer (carried over, lower priority)

My round-1 note that the *economic* layer is also closed (fixed agent-type
proportions, no firm formation) stands, but for a conference paper this is an
acceptable minimal-model scope given the open-skills demonstration now present.
For the journal version I would want either the open-skill mechanism folded into
the main economic model, or a clearer minimal-model defence. The authors cite
Taylor (2019) and Banzhaf et al. (2016) for the OEE direction, which is the
right literature; confirm those bib entries compile.

## 5. Minor

- Charbonneau & Bourrat (2021) "grain problem" is now cited (§6.3) — good,
  this was a round-1 gap.
- Remove the reviewer-facing scaffolding ("the ALIFE reviewer flagged,"
  "AL-2") from the manuscript body; it reads as a rebuttal letter.
- The Vaesen et al. (2016) critique of the Tasmanian inference is mentioned
  parenthetically (§5.6); a one-sentence statement of what the critique *is*
  would help the ALIFE reader who knows the Henrich result but not the
  rebuttal.

## 6. Verdict

The cultural contribution is now well-grounded: erosion framing is honest, the
coupling is genuinely exercised, the elasticity asymmetry is a real emergent
result, and the open-skills demo answers the open-endedness concern at
demonstration scale. Subject to the shared consistency pass (see overview), the
per-capita-discovery fix (§3.1), the missing elasticity rows (§3.2), and the
title (§3.3), this is a solid **ALIFE conference accept**. For the *Artificial
Life* journal I would hold at **major revision** pending deeper integration of
the open-ended mechanism.
