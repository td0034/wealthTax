"""
Minimal open-ended skill-space extension (Tier 3 #32).

Demonstrates the cultural side of the model under two regimes:

  CLOSED: skill space is a fixed K=5 vector; no new dimensions can appear
          (the published variant). Cultural breadth has a hard ceiling.
  OPEN:   skill dimensions can be *discovered* at births. The probability
          of a novelty event is proportional to log(parent wealth), so
          discovery itself is wealth-coupled. Once discovered, a dimension
          enters the global pool and can be transmitted (subject to the
          same bandwidth limit).

We track the size of the active skill pool over time and the wealth
distribution of the agents that first discovered each new dimension.

This is a research extension answering the ALIFE reviewer's open-endedness
critique. It does not feed back into the rest of the paper's policy
results; it is a separate demonstration of how the model would behave
under a TAP-style novelty mechanism.

Usage: python3 open_skills.py
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

OUT = Path("out/figures/scenarios")
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Mini ABM with variable skill space
# ---------------------------------------------------------------------------

@dataclass
class MiniAgent:
    id: int
    type: str
    wealth: float
    skills: list[float]                # variable-length skill vector
    age: int = 0
    lifespan: int = 70


N_INIT = 200
INITIAL_K = 5
CLASSES = ["WORKER", "MAKER", "RENTIER"]
CLASS_WEIGHTS = [0.7, 0.2, 0.1]
INITIAL_WEALTH = {"WORKER": 1.0, "MAKER": 5.0, "RENTIER": 30.0}

# Per-tick wealth dynamics, very simple:
#   worker:  wage = 1 * (0.7 + 0.6 * mean(skills present))
#   maker:   wealth grows by 0.1 * sum(skills present)
#   rentier: wealth grows by 0.04 * wealth (compounding)
def step_wealth(a: MiniAgent):
    skill_present = [s for s in a.skills if s > 0]
    if a.type == "WORKER":
        a.wealth += 1.0 * (0.7 + 0.6 * (np.mean(skill_present)
                                         if skill_present else 0.0))
    elif a.type == "MAKER":
        a.wealth += 0.5 + 0.2 * sum(skill_present)
    elif a.type == "RENTIER":
        a.wealth *= 1.04


# Birth mechanism
def make_child(parent: MiniAgent, K_active: int, rng: np.random.Generator,
               b0: float, bw: float,
               novelty_rate: float, K_max: int,
               next_id: list, ) -> tuple[MiniAgent, bool]:
    """Return (child, novelty_event_bool)."""
    parent_skills = np.array(parent.skills, dtype=float)
    # Pad parent skills to K_active length (in case parent was older).
    if len(parent_skills) < K_active:
        parent_skills = np.concatenate(
            [parent_skills, np.zeros(K_active - len(parent_skills))])
    log_w = float(np.log10(max(1.0, parent.wealth))) / 4.0
    bandwidth = max(1, int(round(b0 * K_active + bw * K_active * log_w)))
    bandwidth = min(bandwidth, K_active)
    transmitted = np.zeros(K_active, dtype=float)
    idx = np.argsort(parent_skills)[::-1][:bandwidth]
    transmitted[idx] = parent_skills[idx]
    # Novelty event probability: scales with log(wealth)
    p_novelty = novelty_rate * log_w
    novelty = rng.random() < p_novelty and K_active < K_max
    if novelty:
        # Activate a new dim for the child (and globally on return).
        transmitted = np.append(transmitted, float(rng.beta(2, 2)))
    next_id[0] += 1
    return MiniAgent(
        id=next_id[0], type=parent.type, wealth=parent.wealth * 0.5,
        skills=list(transmitted),
        lifespan=int(rng.normal(70, 12)),
    ), novelty


def init_population(rng: np.random.Generator, K: int) -> list[MiniAgent]:
    agents = []
    types = rng.choice(CLASSES, size=N_INIT, p=CLASS_WEIGHTS)
    for i, t in enumerate(types):
        skills = list(rng.beta(2, 2, K))
        agents.append(MiniAgent(
            id=i, type=str(t),
            wealth=INITIAL_WEALTH[str(t)] * float(rng.lognormal(0, 0.3)),
            skills=skills,
            age=int(rng.uniform(0, 60)),
            lifespan=int(rng.normal(70, 12)),
        ))
    return agents


def run(novelty_rate: float, K_max: int, ticks: int, seed: int):
    rng = np.random.default_rng(seed)
    K_active = INITIAL_K
    agents = init_population(rng, K_active)
    next_id = [N_INIT]
    discovered_log = []
    K_active_history = []
    breadth_history = []
    for t in range(ticks):
        # wealth dynamics
        for a in agents:
            step_wealth(a)
            a.age += 1
        # natural deaths -> children
        new_agents = []
        for a in agents:
            if a.age >= a.lifespan:
                child, novelty = make_child(a, K_active, rng,
                                            b0=0.5, bw=0.5,
                                            novelty_rate=novelty_rate,
                                            K_max=K_max, next_id=next_id)
                if novelty:
                    discovered_log.append({"tick": t,
                                            "parent_type": a.type,
                                            "parent_wealth": a.wealth,
                                            "new_K": K_active + 1})
                    K_active += 1
                    # Extend all existing agents' skills with 0 for the new dim
                    for b in agents:
                        b.skills.append(0.0)
                    for b in new_agents:
                        b.skills.append(0.0)
                new_agents.append(child)
        agents = [a for a in agents if a.age < a.lifespan] + new_agents
        K_active_history.append(K_active)
        breadths = [sum(1 for s in a.skills if s > 0) for a in agents]
        breadth_history.append(np.mean(breadths) if breadths else 0)
    return (np.array(K_active_history), np.array(breadth_history),
            discovered_log)


def main():
    ticks = 400
    seeds = 5

    K_closed = []
    breadth_closed = []
    K_open = []
    breadth_open = []
    discovery_logs = []
    for s in range(seeds):
        ka_c, br_c, _ = run(novelty_rate=0.0, K_max=15,
                            ticks=ticks, seed=s)
        K_closed.append(ka_c); breadth_closed.append(br_c)
        ka_o, br_o, log_o = run(novelty_rate=0.02, K_max=15,
                                ticks=ticks, seed=s + 100)
        K_open.append(ka_o); breadth_open.append(br_o)
        discovery_logs.extend(log_o)

    K_closed = np.stack(K_closed); breadth_closed = np.stack(breadth_closed)
    K_open = np.stack(K_open); breadth_open = np.stack(breadth_open)

    # Discovery wealth distribution
    if discovery_logs:
        wealths = np.array([d["parent_wealth"] for d in discovery_logs])
        types_d = [d["parent_type"] for d in discovery_logs]
        print(f"discoveries: {len(discovery_logs)}; by type:")
        for cls in CLASSES:
            c = sum(1 for t in types_d if t == cls)
            print(f"  {cls}: {c}")
        print(f"  median wealth of discoverer: {np.median(wealths):.1f}")
        print(f"  90th percentile wealth:      {np.percentile(wealths, 90):.1f}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    ticks_x = np.arange(ticks)
    axes[0].plot(ticks_x, K_closed.mean(axis=0), color="#9ca3af",
                 label="closed (no novelty)", lw=2)
    axes[0].fill_between(ticks_x, K_closed.min(axis=0), K_closed.max(axis=0),
                         color="#9ca3af", alpha=0.2)
    axes[0].plot(ticks_x, K_open.mean(axis=0), color="#2563eb",
                 label="open (wealth-biased novelty)", lw=2)
    axes[0].fill_between(ticks_x, K_open.min(axis=0), K_open.max(axis=0),
                         color="#2563eb", alpha=0.2)
    axes[0].set_xlabel("tick"); axes[0].set_ylabel("active skill dimensions")
    axes[0].set_title("Skill-space size over time")
    axes[0].grid(alpha=0.3); axes[0].legend()

    axes[1].plot(ticks_x, breadth_closed.mean(axis=0), color="#9ca3af",
                 label="closed", lw=2)
    axes[1].plot(ticks_x, breadth_open.mean(axis=0), color="#2563eb",
                 label="open", lw=2)
    axes[1].set_xlabel("tick"); axes[1].set_ylabel("mean cultural breadth")
    axes[1].set_title("Cultural breadth (per agent)")
    axes[1].grid(alpha=0.3); axes[1].legend()

    if discovery_logs:
        # Per-capita discovery rate by class: discoveries per agent-generation
        # divided by approximate average class population during the open runs.
        # Class size estimated as N_INIT * CLASS_WEIGHTS (good to first order).
        avg_class_size = {cls: N_INIT * CLASS_WEIGHTS[i]
                          for i, cls in enumerate(CLASSES)}
        # Number of generations elapsed = total ticks / median lifespan
        avg_lifespan = 70
        n_generations_per_run = ticks / avg_lifespan
        # Average over `seeds` runs of the open variant.
        n_runs = seeds
        per_capita_rate = {}
        for cls in CLASSES:
            count = sum(1 for d in discovery_logs if d["parent_type"] == cls)
            agent_generations = avg_class_size[cls] * n_generations_per_run * n_runs
            per_capita_rate[cls] = count / max(agent_generations, 1e-9)
        print()
        print("per-capita discovery rate (discoveries / agent-generation):")
        for cls in CLASSES:
            print(f"  {cls}: {per_capita_rate[cls]:.4f}  "
                  f"(approx {avg_class_size[cls]:.0f} agents/run)")
        axes[2].bar(list(per_capita_rate.keys()),
                    list(per_capita_rate.values()),
                    color=["#9ca3af", "#16a34a", "#dc2626"])
        axes[2].set_ylabel("discoveries / agent-generation")
        axes[2].set_title("Per-capita discovery rate by class\n"
                          "(wealth-biased novelty: rentier > maker > worker)")
        axes[2].grid(alpha=0.3, axis="y")
        for i, (cls, rate) in enumerate(per_capita_rate.items()):
            axes[2].text(i, rate, f"{rate:.3f}", ha="center", va="bottom",
                         fontsize=10)
        axes[2].set_xlabel("class")

    fig.suptitle(
        "Open-ended skill space: closed vs wealth-biased novelty",
        fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "open_skills.png", dpi=120)
    plt.close(fig)
    print(f"saved {OUT / 'open_skills.png'}")


if __name__ == "__main__":
    main()
