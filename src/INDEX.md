# `src/` catalogue

All Python sources for the project.  Files live flat in `src/` so the
`from sim import ...` imports work across all scripts.  This file
groups them by purpose.

## Core

| file | role |
|---|---|
| `sim.py` | Core agent-based model. Seven agent classes, the `step` function, all dial parameters, the metric definitions. Imported by everything else. |

## Round-1 experiments (original empirical content)

| file | what it produces |
|---|---|
| `scenarios.py` | 13 named scenarios at $N$=1000; figures and summary JSON |
| `policies.py` | 11 policy interventions at $N$=1000 |
| `policies_30seeds.py` | $N$=10k policy comparison with bootstrap CIs |
| `sweeps.py` | Five parameter sweeps (rent, subsistence, etc.) at $N$=100 |
| `phase3d.py` | 3-D phase portrait + shadows + landscapes |
| `wealth_tax_sweep.py` | Wealth-tax threshold-rate sweep |
| `cap_sweep.py` | Inheritance-cap value sweep $\pounds 1M$ to no-cap |
| `scale_up.py` | $N$=10k validation pass |
| `calibrated_scale_up.py` | Joint-calibrated $N$=10k run |
| `rerun_tax_sweep_n10k.py` | $N$=10k re-run of tax sweep |
| `calibrated_policies.py` | Policy suite at joint-calibrated baseline |
| `calibration.py` | First-pass calibration to UK Pareto slope |
| `calibration_joint.py` | Joint calibration to wealth + mortality targets |
| `dial_sensitivity.py` | One-at-a-time dial sensitivity |
| `factorial.py` | Tax $\times$ spending $\times$ inheritance factorial |

## Phase 1 mechanism studies

| file | what it produces |
|---|---|
| `flows.py` | Sankey diagram of monetary flows by class |
| `flows_cap.py` | Sankey under cap vs status quo |
| `pareto.py` | Pareto-slope analysis on terminal wealth |
| `fixed_point.py` | Analytical fixed-point validation |
| `clustering.py` | k-means clustering of policy-outcome space |
| `survival.py` | Survival curves across policies |
| `elasticity.py` | Skill-to-wealth elasticity decomposition |
| `elasticity_scenarios.py` | Elasticity across all scenarios |
| `bandwidth_decomp.py` | Cultural-transmission bandwidth decomposition |
| `open_skills.py` | Open-skill space (novelty discovery) demo |
| `open_skills_longrun.py` | Long-run cumulative novelty test |
| `material_constraint.py` | Hard material-pool constraint (autopoietic check) |
| `spangler.py` | Spangler & Sarkar comparison arm |
| `elegant_demo.py` | The headline chart of round 1 (now superseded) |
| `benefits_analysis.py` | Revenue and ownership dashboard |

## Round-2 stress tests

All `round2_*.py` scripts test specific Stewart/Hunt critiques.

| file | what it tests |
|---|---|
| `round2_killswitch.py` | R2-1: IHT-plus-spending decomposition vs cap |
| `round2_was_baseline.py` | R2-2: housing/pension floor for ONS WAS baseline |
| `round2_flight.py` | R2-3: capital flight under the cap |
| `round2_enforcement.py` | R2-4: enforcement-friction sweep on the cap |
| `round2_carveout.py` | R2-5: BPR-style productive-class carve-out |
| `round2_equal_revenue.py` | R2-6: equal-revenue wealth-tax vs cap |
| `round2_hybrid.py` | R2-9, R2-10: hybrid wealth-tax rate sweep and enforcement |
| `round2_hybrid_loose_ends.py` | R2-11: hybrid flight, ramp, carve-out, stacked |
| `round2_figures.py` | Round-2 cap-paper figures (decomp, enforcement, equal-revenue) |
| `round2_hybrid_figures.py` | Round-2 wealth-tax paper figures (sweep, enforce, stacked, flight-ramp) |

## Growth-paper scripts (Path B)

| file | what it produces |
|---|---|
| `growth_audit.py` | First-pass four-measure audit (no productivity channels) |
| `growth_portfolio.py` | Headline six-measure $\times$ five-arm $\times$ four-regime sweep |
| `growth_robustness.py` | $\alpha$ sweep and capability composition robustness (post-process) |
| `growth_seeds20.py` | 20-seed baseline for bootstrap CIs |
| `growth_cis.py` | Percentile bootstrap CI computation |
| `growth_figures.py` | Four growth-paper figures |
| `growth_robustness_figures.py` | Robustness figures ($\alpha$, capability) |

## Reproducing the headline papers

```
# Wealth-tax paper:
python3 src/round2_hybrid.py
python3 src/round2_hybrid_loose_ends.py
python3 src/round2_hybrid_figures.py

# Growth paper:
python3 src/growth_portfolio.py
python3 src/growth_seeds20.py
python3 src/growth_cis.py
python3 src/growth_robustness.py
python3 src/growth_figures.py
python3 src/growth_robustness_figures.py
```

Outputs go to `out/data/` (JSON) and `out/figures/` (PNG).
