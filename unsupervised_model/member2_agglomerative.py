"""MEMBER 2 - Agglomerative (hierarchical) clustering.

Idea: start with every booking as its own cluster and repeatedly merge the two closest clusters
until k remain. With ``ward`` linkage the merge that increases the within-cluster variance
least is chosen (similar goal to K-Means).

Limit: the algorithm needs the distance between every pair of bookings (86,638 x 86,638 numbers
is about 60 GB), so we fit it on a random sample of 10,000 bookings and then give every other
booking the cluster of its nearest cluster centre.

We also compare linkage types. Average, complete and single linkage reach a higher silhouette
(0.53-0.64 against 0.37 for ward) but only because they put 95-99 percent of the bookings in
ONE huge cluster and a few outliers in the others - a good lesson that a high score alone
does not mean a useful clustering. The comparison is saved in
``agglomerative_linkage_comparison.csv``.
"""

import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import cdist
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score

from unsupervised_model import common

NAME = "agglomerative"
SAMPLE = 10000


def fit_and_propagate(X, k, seed=common.SEED, linkage_type="ward"):
    """Fit on a random sample, then label ALL rows by the nearest sample-cluster centre."""
    idx = np.random.RandomState(seed).choice(len(X), min(SAMPLE, len(X)), replace=False)
    sample_labels = AgglomerativeClustering(n_clusters=k, linkage=linkage_type).fit_predict(
        X[idx])
    centres = np.vstack([X[idx][sample_labels == c].mean(axis=0) for c in range(k)])
    return cdist(X, centres).argmin(axis=1), idx, sample_labels


def k_sweep(Xs, ks):
    """Score ward clusterings of the sample for every k."""
    rows = []
    for k in ks:
        lab = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xs)
        m = common.evaluate(Xs, lab)
        rows.append({"k": k, "silhouette": m["silhouette"],
                     "davies_bouldin": m["davies_bouldin"],
                     "calinski_harabasz": m["calinski_harabasz"]})
    return pd.DataFrame(rows)


def linkage_comparison(Xs, k):
    """Silhouette AND largest-cluster share for each linkage (shows the misleading ones)."""
    rows = []
    for how in ("ward", "average", "complete", "single"):
        lab = AgglomerativeClustering(n_clusters=k, linkage=how).fit_predict(Xs)
        m = common.evaluate(Xs, lab)
        rows.append({"linkage": how, "silhouette": m["silhouette"],
                     "davies_bouldin": m["davies_bouldin"],
                     "largest_cluster_pct": m["largest_cluster_pct"],
                     "smallest_cluster_pct": m["smallest_cluster_pct"]})
    return pd.DataFrame(rows)


def plot_dendrogram(Xs, k):
    """Dendrogram of a 1,000-booking sample, truncated to the last 12 merges."""
    common._style()
    idx = np.random.RandomState(common.SEED).choice(len(Xs), min(1000, len(Xs)),
                                                    replace=False)
    Z = linkage(Xs[idx], method="ward")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    dendrogram(Z, truncate_mode="lastp", p=12, ax=ax, color_threshold=0,
               above_threshold_color=common.CLUSTER_COLORS[0], leaf_rotation=0)
    cut = Z[-(k - 1), 2]
    ax.axhline(cut, color=common.CLUSTER_COLORS[1], ls="--", lw=1.5)
    ax.text(ax.get_xlim()[0], cut, f"cut at k = {k} ", color=common.INK, va="bottom",
            ha="left")
    ax.set_xlabel("Merged groups (number of bookings in brackets)")
    ax.set_ylabel("Ward distance")
    ax.grid(axis="x", visible=False)
    ax.set_title("Dendrogram (1,000-booking sample): tall branches = very different groups")
    return common.save_chart(fig, NAME, "dendrogram")


def run(df=None, fast=False):
    """Choose k on a sample, cluster all bookings, score, draw and save."""
    started = time.time()
    df = common.load_data() if df is None else df
    prep = common.prepare(df, fast)
    X = prep.X

    # 1. choose k on the sample with the same rule as K-Means
    idx = np.random.RandomState(common.SEED).choice(len(X), min(SAMPLE, len(X)),
                                                    replace=False)
    table = k_sweep(X[idx], range(3, 6) if fast else common.K_RANGE)
    k = common.choose_k(table)
    common.METRICS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(common.METRICS_DIR / "agglomerative_k_sweep.csv", index=False)
    linkage_comparison(X[idx], k).to_csv(
        common.METRICS_DIR / "agglomerative_linkage_comparison.csv", index=False)

    # 2. final clustering of ALL bookings
    labels, _, _ = fit_and_propagate(X, k)
    metrics = common.evaluate(X, labels)
    metrics["stability_ari"] = common.stability(
        lambda s: fit_and_propagate(X, k, seed=s)[0], X)
    km = KMeans(n_clusters=k, n_init=10, random_state=common.SEED).fit_predict(X)
    metrics["ari_vs_kmeans"] = round(float(adjusted_rand_score(km, labels)), 3)

    # 3. charts and profile
    prof = common.profile(prep.data, labels)
    plot_dendrogram(X[idx], k)
    common.plot_clusters(NAME, f"Agglomerative (ward) with k = {k}", X, labels)
    common.plot_profile(NAME, f"Agglomerative: what makes each of the {k} clusters different",
                        X, prep.names, labels)

    result = common.make_result(
        NAME, {"linkage": "ward", "k": k, "fit_sample": len(idx)}, metrics, started,
        notes=f"fitted on {len(idx):,} sampled bookings, others assigned to the nearest centre")
    common.save_result(result, prof)
    return result
