"""
K-means clustering of phase-portrait endpoints (J-2).

Replaces the prior "regime assignment by inspection" with a stated rule:
k=3 means on z-normalised (Gini, Phi, alive), labelled by inspection of
centroid coordinates, with silhouette score reported as a robustness check.

Usage: python3 clustering.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

OUT = Path("out/figures/phase")
OUT.mkdir(parents=True, exist_ok=True)
OUT_DATA = Path("out/data")


def kmeans(X, k, n_iter=200, seed=0):
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    idx = rng.choice(n, k, replace=False)
    centres = X[idx].copy()
    for _ in range(n_iter):
        d = np.linalg.norm(X[:, None, :] - centres[None, :, :], axis=2)
        labels = np.argmin(d, axis=1)
        new_centres = np.stack([
            X[labels == c].mean(axis=0) if (labels == c).any() else centres[c]
            for c in range(k)
        ])
        if np.allclose(new_centres, centres):
            break
        centres = new_centres
    return labels, centres


def silhouette(X, labels):
    n = X.shape[0]
    if n < 2:
        return 0.0
    s = np.zeros(n)
    for i in range(n):
        same = labels == labels[i]
        if same.sum() <= 1:
            s[i] = 0
            continue
        a_i = np.linalg.norm(X[same] - X[i], axis=1).sum() / (same.sum() - 1)
        b_i = float("inf")
        for c in set(labels) - {labels[i]}:
            mask = labels == c
            if mask.sum() == 0:
                continue
            d = np.linalg.norm(X[mask] - X[i], axis=1).mean()
            b_i = min(b_i, d)
        s[i] = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0.0
    return float(np.mean(s))


def main():
    summary_path = OUT_DATA / "scenarios_summary.json"
    with open(summary_path) as f:
        summary = json.load(f)

    names, X = [], []
    for name, s in summary.items():
        names.append(name)
        X.append([
            s["final_gini_mean"],
            s["final_autocatalytic_closure"],
            s["final_alive_mean"],
        ])
    X = np.array(X, dtype=float)

    # z-normalise each column
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-9
    Xz = (X - mu) / sd

    # Run kmeans for k in 2..5, pick k=3 (paper's claim) but report silhouette across.
    sils = {}
    for k in range(2, 6):
        labels, _ = kmeans(Xz, k, seed=7)
        sils[k] = silhouette(Xz, labels)
    print("Silhouette scores by k:")
    for k, s in sils.items():
        print(f"  k={k}  silhouette={s:.3f}")

    labels, centres = kmeans(Xz, 3, seed=7)
    centroid_raw = centres * sd + mu
    print("\nCluster centroids (raw scale):")
    for c in range(3):
        print(f"  cluster {c}: Gini={centroid_raw[c, 0]:.2f}  "
              f"Phi={centroid_raw[c, 1]:.3f}  alive={centroid_raw[c, 2]:.1f}")

    # Label clusters by inspection of centroid: viable / extractive / collapse
    # by sorting on Phi (high -> viable, mid -> extractive, near-0 collapse)
    order = np.argsort(-centroid_raw[:, 1])    # high Phi first
    regime_for_cluster = {}
    regime_for_cluster[order[0]] = "viable autocatalytic"
    # Among remaining two, the one with higher alive is extractive, lower is collapse
    rem = list(order[1:])
    if centroid_raw[rem[0], 2] >= centroid_raw[rem[1], 2]:
        regime_for_cluster[rem[0]] = "extractive equilibrium"
        regime_for_cluster[rem[1]] = "collapse"
    else:
        regime_for_cluster[rem[1]] = "extractive equilibrium"
        regime_for_cluster[rem[0]] = "collapse"

    print("\nAssignments:")
    print(f"  {'scenario':<22} {'cluster':>8} {'regime':<25}")
    out_rows = []
    for name, c, x in zip(names, labels, X):
        regime = regime_for_cluster[c]
        print(f"  {name:<22} {c:>8} {regime:<25}")
        out_rows.append({"name": name, "cluster": int(c), "regime": regime,
                         "gini": float(x[0]), "phi": float(x[1]),
                         "alive": float(x[2])})

    with open(OUT_DATA / "phase_clusters.json", "w") as f:
        json.dump({
            "silhouettes": sils,
            "k3_silhouette": sils[3],
            "centroids_raw": centroid_raw.tolist(),
            "regime_for_cluster": {int(k): v for k, v in regime_for_cluster.items()},
            "assignments": out_rows,
        }, f, indent=2)

    # Plot.
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    cluster_colours = {0: "#2563eb", 1: "#ef4444", 2: "#16a34a"}
    label_colours = [cluster_colours[c] for c in labels]
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=label_colours, s=90,
               edgecolors="black", linewidths=0.6)
    for name, x in zip(names, X):
        ax.text(x[0], x[1], x[2], name, fontsize=7)
    # Centroids
    ax.scatter(centroid_raw[:, 0], centroid_raw[:, 1], centroid_raw[:, 2],
               s=400, marker="X", c=[cluster_colours[c] for c in range(3)],
               edgecolors="black", linewidths=1.0, alpha=0.9)
    ax.set_xlabel("Gini")
    ax.set_ylabel("Phi (productive-flow share)")
    ax.set_zlabel("Alive")
    ax.set_title(
        f"K-means clustering (k=3) of scenario endpoints. "
        f"Silhouette score = {sils[3]:.3f}")
    fig.tight_layout()
    fig.savefig(OUT / "phase_clusters.png", dpi=130)
    plt.close(fig)
    print(f"\nsaved {OUT / 'phase_clusters.png'}")


if __name__ == "__main__":
    main()
