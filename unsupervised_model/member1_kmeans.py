"""MEMBER 1 - K-Means clustering (the main model).

Idea: choose k centres, assign every booking to its nearest centre, move each centre to the
mean of its bookings, and repeat until nothing changes. Fast (about 2 seconds for 86,638 rows)
and easy to explain, which is why it is the main model of this part.

The number of clusters k is NOT given: we try k = 3..8 and pick the best by silhouette and
Davies-Bouldin (see ``common.choose_k``). k = 2 is excluded because it only splits off a small
group of repeat / company guests.
"""

import time

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans

from unsupervised_model import common

NAME = "kmeans"


def k_sweep(X, ks):
    """Fit K-Means for every k and collect inertia and the internal scores."""
    rows = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=common.SEED).fit(X)
        m = common.evaluate(X, km.labels_)
        rows.append({"k": k, "inertia": round(float(km.inertia_), 0),
                     "silhouette": m["silhouette"], "davies_bouldin": m["davies_bouldin"],
                     "calinski_harabasz": m["calinski_harabasz"]})
    return pd.DataFrame(rows)


def plot_k_selection(table, best):
    """Three small charts: inertia (elbow), silhouette (higher better), Davies-Bouldin (lower)."""
    common._style()
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, col, title in zip(
            axes, ["inertia", "silhouette", "davies_bouldin"],
            ["Inertia (elbow)", "Silhouette (higher is better)",
             "Davies-Bouldin (lower is better)"]):
        ax.plot(table["k"], table[col], color=common.CLUSTER_COLORS[0], lw=2, marker="o",
                ms=6, markeredgecolor=common.SURFACE)
        ax.axvline(best, color=common.MUTED, ls="--", lw=1)
        ax.set_xlabel("k (number of clusters)")
        ax.set_title(title, fontsize=11)
    axes[0].text(best, axes[0].get_ylim()[1], f" chosen k = {best}", va="top",
                 color=common.INK)
    fig.tight_layout()
    return common.save_chart(fig, NAME, "k_selection")


def run(df=None, fast=False):
    """Choose k, fit K-Means, score it, draw the charts and save the results."""
    started = time.time()
    df = common.load_data() if df is None else df

    # 1. labels removed, features built and standardised
    prep = common.prepare(df, fast)

    # 2. try several k and choose one with the two internal scores
    table = k_sweep(prep.X, range(3, 6) if fast else common.K_RANGE)
    k = common.choose_k(table)
    common.METRICS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(common.METRICS_DIR / "kmeans_k_sweep.csv", index=False)
    plot_k_selection(table, k)

    # 3. final model, scores, stability across random starts
    labels = KMeans(n_clusters=k, n_init=10, random_state=common.SEED).fit_predict(prep.X)
    metrics = common.evaluate(prep.X, labels)
    metrics["stability_ari"] = common.stability(
        lambda s: KMeans(n_clusters=k, n_init=10, random_state=s).fit_predict(prep.X),
        prep.X)

    # 4. describe the clusters (this is where the removed cancellation label is used)
    prof = common.profile(prep.data, labels)
    common.plot_clusters(NAME, f"K-Means with k = {k}", prep.X, labels)
    common.plot_profile(NAME, f"K-Means: what makes each of the {k} clusters different",
                        prep.X, prep.names, labels)

    result = common.make_result(NAME, {"k": k, "n_init": 10}, metrics, started,
                                notes=f"k={k} chosen from 3..{table['k'].max()}")
    common.save_result(result, prof)
    return result
