# Literature Review: Unequal Agents

Prepared 2026-05-28. Citations checked via web search; items I could not independently confirm are flagged "(unverified)". The goal is honest positioning, not coverage for its own sake.

---

## 1. Annotated bibliography

### a) Agent-based models of wealth inequality

**Epstein, J. M. & Axtell, R. (1996).** *Growing Artificial Societies: Social Science from the Bottom Up.* Brookings / MIT Press.
The canonical "Sugarscape" book: heterogeneous foragers on a sugar landscape generate skewed wealth distributions, demography, trade, combat, culture transmission.
Relevance: our seven-type fixed-proportion model is a deliberate departure — we hard-code occupational structure rather than letting it emerge from foraging, which is closer to political-economy taxonomy than to Sugarscape minimalism.

**Wilensky, U. (1998).** *NetLogo Wealth Distribution model.* Center for Connected Learning, Northwestern.
Reimplements Epstein & Axtell ch. 2 with Lorenz/Gini reporting; the de facto teaching baseline for inequality ABMs.
Relevance: our Gini reporting and inheritance-cap conventions follow this lineage; we extend by adding non-foraging agent types and explicit extractive flows.

**Drăgulescu, A. & Yakovenko, V. M. (2000).** "Statistical mechanics of money." *European Physical Journal B* 17, 723–729.
Conservative money-exchange in a closed economy yields an exponential (Boltzmann–Gibbs) distribution — the "money temperature" analogy.
Relevance: a baseline; pure exchange already produces strong inequality without rent, debt, or inheritance. Our model adds the extractive channels that explain why empirical distributions have power-law tails the BG model misses.

**Bouchaud, J.-P. & Mézard, M. (2000).** "Wealth condensation in a simple model of economy." *Physica A* 282, 536–545.
Multiplicative wealth dynamics plus pairwise exchange produces Pareto tails; under-exchange the system "condenses" wealth onto a few agents.
Relevance: this is the deep formal result behind our Stevenson worst-case run. The condensation transition is essentially the same phenomenon as our "closure → 0" failure mode; we should cite it explicitly when we report that case.

**Yakovenko, V. M. & Rosser, J. B. (2009).** "Colloquium: Statistical mechanics of money, wealth, and income." *Reviews of Modern Physics* 81, 1703.
Synthesises the econophysics tradition: two-class distributions, exponential bulk + power-law tail.
Relevance: required background; positions our work as ABM-with-mechanisms vs their stylised kinetic models.

**Boghosian, B. M., Devitt-Lee, A., Johnson, M., Li, J., Marcq, J. A. & Wang, H. (2017).** "Oligarchy as a phenomenon of asset exchange." *Physica A* 476, 15–37. The "yard-sale" / extended yard-sale model showing oligarchy is generic under multiplicative exchange, and that wealth-attained-from-loss biases (a la wealth-favoured negotiation) drive condensation.
Relevance: directly relevant prior art on "extractive bias" producing oligarchy without any explicit rent — worth citing as a complementary mechanism (transaction asymmetry) to our channel-based extraction.

**Kumar, S., Anand, K., et al. (2024).** "Wealth distribution on a dynamic complex network." *Physica A* 652, 130067.
Yard-sale style exchange on a rewiring network with a social-protection factor *f*; *f* = 0 reproduces condensation, increasing *f* produces egalitarian outcomes.
Relevance: very close cousin of our "Nordic" finding — a single redistributive parameter flipping the qualitative regime. They do it on a network without occupational types; we do it with channels and types.

**Berman, Y., Ben-Jacob, E. & Shapira, Y. (2016).** "Modeling the origin and possible control of the wealth inequality surge." *PLOS ONE* 11(4): e0154058. ABM where geometric Brownian motion plus rebalancing reproduces the US wealth-share surge since 1980.
Relevance: shows r > g style dynamics as ABM output, which is one of the things you asked about. (Verified via PMC link.)

**Cardoso, B.-H. F., Gonçalves, S. & Iglesias, J. R. (2025).** "Wealth inequality in agent-based economies: the dominant role of social protection over growth." *Physica A* (in press, arXiv:2508.06666).
Yard-sale + growth + social protection: protection (favouring the poor in transactions) dominates redistribution for reducing inequality.
Relevance: published this year. The headline result — that *how* the state intervenes matters more than growth — overlaps thematically with our "state spending vs. tax-only" finding. We should engage with this paper specifically.

**Pagliarini, A. (2017).** "An agent-based model of the observed distribution of wealth in the United States." *Journal of Economic Interaction and Coordination* 12, 599–631. ABM calibrated to match US wealth distribution including Pareto upper tail.
Relevance: shows the JEIC venue accepts calibrated ABMs of wealth distribution; useful methodological precedent.

### b) Ikegami lab and adjacent alife on society/economy

**Hashimoto, Y., Oka, M. & Ikegami, T. (2019).** "Open-ended evolution and a mechanism of novelties in web services." *Artificial Life* 25(2), 168–177.
Tags-as-species in social tagging systems; novelty emerges from tag combinations, not new tags.
Relevance: this is the closest published Ikegami-lab work to a "social/economic" ABM. It's not about inequality. The wider lab focus is open-endedness and emergence rather than economy per se.

**Takahashi, K., Suzuki, R. & Ikegami, T. (cited on the Ikegami lab publications page).** Various papers on alife agent communities, swarm and Lenia-style continuous CA. (Unverified for any economic content.)
Relevance: the user's framing of "Ikegami-style" is more about methodological aesthetic — open-ended, generative, willing to be qualitative — than about specific economic models. There does not appear to be a published Ikegami-lab paper on wealth inequality. Be honest about this in framing.

**Nishimura, S. & Ikegami, T. (1997).** "Emergence of collective strategies in a prey-predator game model." *Artificial Life* 3(4), 243–260. (Verified via search.)
Relevance: an older example of Ikegami-lab evolutionary game ABM; not on economy but on emergent strategy ecologies. Useful citation for the "alife sensibility" the project claims.

### c) Cultural transmission with finite bandwidth / fidelity

**Cavalli-Sforza, L. L. & Feldman, M. W. (1981).** *Cultural Transmission and Evolution: A Quantitative Approach.* Princeton.
Foundational: vertical/horizontal/oblique transmission as a coupled dynamical system.
Relevance: our vertical, bandwidth-limited skill transmission sits squarely in this framework. They do not couple transmission probability to wealth.

**Boyd, R. & Richerson, P. J. (1985).** *Culture and the Evolutionary Process.* Chicago. And **Henrich, J. (2015).** *The Secret of Our Success.* Princeton.
Cumulative culture depends on high-fidelity social learning; population size and connectivity bound cultural complexity.
Relevance: the *population* version of our individual mechanism — they argue size/connectivity sets the ceiling; we argue intra-population wealth dispersion does so via bandwidth allocation. Complementary, not competing.

**Henrich, J. (2004).** "Demography and cultural evolution: how adaptive cultural processes can produce maladaptive losses — the Tasmanian case." *American Antiquity* 69(2), 197–214. The formal model behind "Tasmania lost technology when population shrank".
Relevance: directly relevant template for the *knowledge_lost* metric. Note the substantial criticism in Vaesen et al. (2016, PNAS) — worth acknowledging.

**Lewis, H. M. & Laland, K. N. (2012).** "Transmission fidelity is the key to the build-up of cumulative culture." *Phil. Trans. R. Soc. B* 367, 2171–2180.
Small fidelity changes have outsize effects on cumulative culture.
Relevance: theoretical justification for why bandwidth-limited transmission should matter at all. We should cite this as the "fidelity drives accumulation" prior.

**Henrich, J. & Gil-White, F. J. (2001).** "The evolution of prestige." *Evolution and Human Behavior* 22, 165–196. Prestige bias: copy successful/prestigious models.
Relevance: in our model wealth determines *whose* skill survives via bandwidth; this is a structural cousin of prestige bias acting on the transmission channel rather than the learner's choice. Worth naming the distinction.

**Charbonneau, M. & Bourrat, P. (2021).** "Fidelity and the grain problem in cultural evolution." *Synthese* 199, 5815–5836.
"Fidelity" only makes sense relative to a chosen grain of description.
Relevance: methodological caveat — our "5-dimensional skill vector" is a grain choice and we should justify it as such, not present it as natural.

I could **not** find a published ABM in which cultural-transmission bandwidth is itself coupled to *wealth* (as opposed to status, group size, or generic noise). Closest neighbours: prestige-bias models (Henrich & Gil-White), the wealth-and-skill ABM of Galor & Tsiddon or Galor & Moav (intergenerational human capital — *theoretical*, not agent-based), and Velardi (2022, undergraduate thesis, unverified peer-review). This thread looks **clearly novel** in the ABM literature.

### d) Autocatalytic sets applied to economy / society

**Kauffman, S. A. (1988).** "The evolution of economic webs." In *The Economy as an Evolving Complex System* (SFI proceedings). Earliest articulation of "the economy as autocatalytic set" — goods catalysing production of other goods, subcritical vs supracritical economies.
Relevance: parent of our central metaphor. Kauffman uses the framework as a generative story for diversity and growth, not as a measurable health metric.

**Hordijk, W. & Steel, M. (2004).** "Detecting autocatalytic, self-sustaining sets in chemical reaction systems." *J. Theor. Biol.* 227, 451–461. The RAF algorithm and formalism.
Relevance: the technical formalism that gives "autocatalytic closure" a precise meaning; we use the *spirit* but not the algorithm.

**Hordijk, W. & Kauffman, S. A. (2023).** "Emergence of autocatalytic sets in a simple model of technological evolution." *Journal of Evolutionary Economics* 33, 1287–1305 (arXiv:2204.01059).
Combines TAP (Theory of the Adjacent Possible) combinatorial innovation with RAF detection; shows production-function networks contain RAF sets with high probability.
Relevance: the most directly comparable recent work. They detect autocatalytic structure in a production graph. They do **not** define an "autocatalytic closure" *ratio* metric for an ongoing simulated economy. Our metric is a different object — flow-based, not network-topological. This is partial overlap, not pre-emption.

**Hordijk, W. (2013).** "Autocatalytic Sets: From the origin of life to the economy." *BioScience* 63(11), 877–881.
Accessible review extending RAF to economy.
Relevance: the canonical citation for "autocatalytic sets, applied to economy". Use as anchor.

**Koppl, R., Devereaux, A., Herriot, J. & Kauffman, S. (2021/2023).** Related work on TAP-process and the economy — "Adjacent possible" combinatorial models. (Several arXiv preprints; book *Emergent Goods* in development.)
Relevance: same intellectual cluster; mostly about *how* novelty enters, not about *whether* the existing economy is autocatalytic. Different question to ours.

I found **no** published work that operationalises autocatalytic-set thinking as a per-tick scalar *health metric* for a simulated economy — i.e. nothing equivalent to our productive_flow / (productive_flow + extractive_flow). The closest is the binary RAF-present/absent diagnosis in Hordijk & Kauffman 2023. Our metric is therefore likely **clearly novel as a measurement device**, though the underlying *idea* (productive-vs-extractive accounting) is old (Stiglitz, Mazzucato, classical political economy).

### e) Inheritance, dynastic wealth, computational

**Piketty, T. (2014).** *Capital in the Twenty-First Century.* Belknap.
The r > g framework and the empirical case for rising wealth concentration.
Relevance: the political framing our model dramatises.

**Piketty, T. & Saez, E. (2013).** "A theory of optimal inheritance taxation." *Econometrica* 81(5), 1851–1886. And **Saez, E. & Zucman, G. (2016).** "Wealth inequality in the United States since 1913." *QJE* 131(2), 519–578. Empirical and optimal-tax theory.
Relevance: source for inheritance-tax parameter ranges; benchmarks for the wealth distributions we should be able to reproduce.

**Wold, H. & Whittle, P. (1957).** "A model explaining the Pareto distribution of wealth." *Econometrica* 25, 591–595. (Classical: bequest + multiplicative wealth growth gives Pareto.)
Relevance: oldest reference for "inheritance generates Pareto tails" — a result we recover.

**Benhabib, J., Bisin, A. & Zhu, S. (2011).** "The distribution of wealth and fiscal policy in economies with finitely lived agents." *Econometrica* 79(1), 123–157. (Verified via standard references — heterogeneous-agent macro with bequests; estate taxation reduces tail inequality.)
Relevance: rigorous version of our inheritance-tax findings, in a DSGE rather than ABM frame.

**Spangler, J. F. & Sarkar, S. (2022).** "The distribution of wealth: an agent-based approach to examine the effect of estate taxation, skill inheritance, and the Carnegie Effect." *Journal of Economic Interaction and Coordination* 17, 833–862 (DOI 10.1007/s11403-022-00372-7).
ABM with estate tax + skill inheritance + Carnegie Effect (high inheritance reduces heir's labour). Finds skill inheritance raises inequality; Carnegie Effect lowers everyone's wealth via revenue loss.
Relevance: **the closest single paper to our project**. They have estate tax, skill inheritance, and an ABM. They do **not** have wealth-coupled transmission *bandwidth*, autocatalytic-closure metric, or multi-channel extraction. We should cite and differentiate carefully.

**Cordoba, J. C. & Verani, S. (2017).** "Bequests and the distribution of wealth across generations." (Unverified — could not confirm exact venue.) Adjacent OLG-with-bequest work.

### f) State-as-hoarder critique

I searched explicitly for "ABM where tax without state spending concentrates wealth in the state". I could not find a paper that frames the result that way. Closest matches:

**Bertotti, M. L. & Modanese, G. (2018, 2019).** Kinetic models of wealth distribution with taxation and redistribution (multiple papers in *Physica A* and *J. Stat. Phys.*). Show that *how* tax revenue is redistributed matters for the steady state.
Relevance: implicit version of our finding but without the framing we use.

**Cardoso et al. 2025** (cited above) makes the structurally similar point that *social protection* dominates over *growth-driven redistribution*.

**Castaldi, C. & Milakovic, M. (2007, J. Econ. Behav. Organ.).** (Unverified.) Earlier kinetic models of wealth with tax.

**Hu, K. et al. (2024, MDPI Entropy / 2023).** "A wealth distribution agent model based on a few universal assumptions" — finds taxation on annual income alone cannot prevent extreme concentration; wealth-based tax can.
Relevance: directly relevant — they isolate the *kind* of tax. Doesn't make the "state-as-hoarder" point explicitly.

**Bottom line for thread f:** the *finding* (tax alone is insufficient; the spending side matters) appears in scattered form across the kinetic-tax-ABM literature, but the *framing* ("the state becomes a hoarder") is, as far as I can tell, our own. **Partial novelty: framing yes, mechanism no.**

---

## 2. Novelty assessment

**Claim 1: autocatalytic_closure metric (productive_flow / (productive_flow + extractive_flow)) as a system-health indicator.**
**Partial novelty.** The underlying productive-vs-extractive distinction is old (Smith, Marx, Veblen, Stiglitz, Mazzucato 2018 *The Value of Everything*). Operationalising autocatalysis in an economic model has been done topologically (Hordijk & Kauffman 2023). What does not appear in the published literature is a continuous, per-tick scalar of this exact ratio form, derived from agent-level cash flows, in a stock-flow-style ABM. Treat it as a *new measurement* of an *old idea*. Defensible novelty — but lead with the metric, not the concept.

**Claim 2: wealth-coupled cultural-transmission bandwidth.**
**Clearly novel** in the ABM-of-economy literature, to the best of public-source evidence. Adjacent work: prestige-bias models (transmission target chosen by status, Henrich & Gil-White 2001), population-size–capped fidelity (Henrich 2004, Lewis & Laland 2012), and the wealth-and-human-capital theoretical models of Galor & Zeira / Galor & Moav (these are analytical, not agent-based, and they make *children's investment* depend on wealth rather than the *number of skill dimensions transmitted*). The specific mechanism "wealthier parents pass more skill dimensions" is, as far as public sources go, your supervisor's. The closest precedent in any ABM is Spangler & Sarkar (2022) where skill is inherited binarily and Carnegie effects on labour are included — but bandwidth is not wealth-coupled there.

**Claim 3: state spending (not tax) is what flips the system from extractive to autocatalytic.**
**Already done in spirit — see Cardoso, Gonçalves & Iglesias 2025; Bertotti & Modanese; Hu et al.** The qualitative result that *what the state does with revenue* matters more than the tax rate is a recurring finding. The *specific* finding that closure goes 0.006 → 0.44 when you toggle state spending, and that this is the metric that matters, is a fresh quantitative angle but not a discovery. Frame it as a sharper measurement of a known phenomenon, not as a new finding.

**Claim 4: inheritance reform requires UBI / safety net to avoid collapse.**
**Partial novelty.** Optimal-inheritance-tax theory (Piketty & Saez 2013) discusses precisely this trade-off analytically. ABMs of estate taxes (Spangler & Sarkar 2022; Velardi 2022 unverified) note revenue interactions. The catastrophic-collapse demonstration ("100% inheritance tax with no safety net wipes out the population") is dramatic but predictable from the analytical literature. Useful pedagogically; not a research contribution on its own.

---

## 3. Venue shortlist

### Rank 1 — **Journal of Artificial Societies and Social Simulation (JASSS)**
- Open-access, indexed, well respected in social ABM. Typical paper 6,000–10,000 words, ODD protocol expected, full code release standard.
- High acceptance of simulation-as-method, low requirement for closed-form results.
- Openness to political/critical framing: high — explicitly publishes work on inequality, segregation, governance.
- Representative recent paper: Bertotti, M. L. et al. on kinetic-and-ABM hybrid tax models; numerous wealth-inequality ABMs through 2023–2025.
- Why it fits: the project's intuition-pump framing is exactly JASSS's house style, and the Nordic-vs-Stevenson contrast is the kind of policy-relevant result they like.

### Rank 2 — **Journal of Economic Interaction and Coordination (JEIC)**
- Springer; Springer's economics ABM home. Typical 6,000–12,000 words. Mathematical/economics audience.
- Acceptance of simulation: very high but they want quantitative calibration or clean stylised-facts comparison.
- Openness to political framing: moderate — heterodox-friendly but framed in econ language.
- Representative recent paper: Spangler & Sarkar (2022, on estate tax and skill inheritance) — *literally our closest neighbour*.
- Why it fits: directly competitive ground with the closest prior art; submitting here forces sharp differentiation but maximises citation impact.

### Rank 3 — **Artificial Life** (MIT Press) *or* the ALIFE 2026 conference proceedings
- Artificial Life: 12–20 pages, MIT Press. ALIFE conference: 8 pages, double-blind, papers accepted to journal are accepted to conference automatically.
- Acceptance of simulation: complete.
- Openness to political/critical/qualitative framing: very high — the journal launched a *Societal Impact* section, and ALIFE Special Sessions on "ALife and Society" are recurring.
- Representative paper: Hashimoto, Oka & Ikegami 2019 on open-ended evolution in web services. Also the 2018 *ALife and Society* special issue.
- Why it fits: aligns with the project's Ikegami-style framing; the autocatalytic-closure metric reads as an alife contribution more than an economics one. ALIFE 2026 proceedings would be the fastest route to a citable record.

**Honourable mentions / not recommended for first submission:**
- *Physica A* / *EPJ B*: easy fit methodologically but the journals want a physics result (a phase transition, a scaling law) more than a political point. Possible follow-up venue if you can frame the state-spending flip as a transition.
- *Review of Political Economy* / *Cambridge Journal of Economics* / *Ecological Economics*: ideologically welcoming, but they want narrative argument over simulation results. They'd be skeptical of "the model says so". Consider a companion essay, not the primary venue.
- *Complexity* (Wiley): broad scope but uneven reputation; doesn't add much over JASSS.

---

## 4. Open questions

1. **Hordijk & Kauffman 2023 full text.** I could not retrieve the full paper through public abstracts. I do not know whether they define any scalar measure of autocatalytic structure that would compete with productive/(productive+extractive). If they do, the novelty of our metric weakens. **Action: read the full paper.**

2. **Whether your supervisor's unpublished work has been described in talks, posters, or technical reports indexed somewhere public.** I deliberately did not chase this. But if a slide deck is online, reviewers will find it and you should know.

3. **Velardi (2022) undergraduate thesis** on taxes-and-wealth ABM — I could not assess its peer-review status or methodological quality. Probably safe to ignore but worth a 5-minute check given the topic overlap.

4. **Galor & Moav (2002, QJE) "Natural selection and the origin of economic growth"** and the wider Galor human-capital-and-inheritance literature — I did not verify whether they make the bandwidth-of-transmission point in any form. They are analytical, not agent-based, but the conceptual prior may be there. **Action: a focused read of Galor & Moav and Galor & Zeira (1993, REStud).**

5. **Bertotti & Modanese** kinetic-tax-ABM series — I cited from search summaries but did not read the originals. If they explicitly identify "tax without spending = state concentration", that *reduces* the novelty of our Claim 3 framing further. **Action: spot-check 1–2 of those papers.**

6. **The Ikegami connection is weaker than the project's framing suggests.** There is no published Ikegami-lab paper on economic inequality. The framing should be "alife sensibility" generally rather than "extending Ikegami's economic work", because that work does not exist in the form implied.

7. **Boghosian's yard-sale oligarchy result** is recent and high-profile; I cited the 2017 Physica A paper, but his subsequent *Science Advances* and *Nature Physics*-adjacent venues writeups should be checked — they may have appeared in a "general science" venue that would strengthen related-work coverage but also raise the bar for our framing.

---

*Word count: approximately 2,350.*
