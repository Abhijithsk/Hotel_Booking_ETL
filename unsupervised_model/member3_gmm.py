"""MEMBER 3 - Gaussian Mixture Model (soft clustering).

Idea: assume the data is a mixture of k bell-shaped (Gaussian) groups and learn each group's
centre, spread and weight (EM algorithm). Unlike K-Means, every booking gets a PROBABILITY of
belonging to each cluster; we label it with the most probable one and also report the average
confidence of that choice.

The number of components is chosen with the same rule as K-Means. We also plot BIC (an
information score, lower is better); on this large data set BIC keeps falling as k grows, so
it cannot be used alone.
"""

import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from unsupervised_model import common

NAME = "gmm"


def make(k, seed=common.SEED):
    return GaussianMixture(n_components=k, covariance_type="full", random_state=seed)


def k_sweep(X, ks):
    rows = []
    for k in ks:
        gm = make(k).fit(X)
        m = common.evaluate(X, gm.predict(X))
        rows.append({"k": k, "bic": round(float(gm.bic(X)), 0),
                     "silhouette": m["silhouette"], "davies_bouldin": m["davies_bouldin"],
                     "calinski_harabasz": m["calinski_harabasz"]})
    return pd.DataFrame(rows)


def plot_bic(table, best):
    common._style()
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(table["k"], table["bic"], color=common.CLUSTER_COLORS[0], lw=2, marker="o", ms=6,
            markeredgecolor=common.SURFACE)
    ax.axvline(best, color=common.MUTED, ls="--", lw=1)
    ax.text(best, ax.get_ylim()[1], f" chosen k = {best}", va="top", color=common.INK)
    ax.set_xlabel("Number of components")
    ax.set_ylabel("BIC (lower is better)")
    ax.set_title("GMM: BIC keeps falling, so it is not used alone")
    return common.save_chart(fig, NAME, "bic")


def run(df=None, fast=False):
    """Choose the number of components, fit the mixture, score, draw and save."""
    started = time.time()
    df = common.load_data() if df is None else df
    prep = common.prepare(df, fast)
    X = prep.X

    table = k_sweep(X, range(3, 6) if fast else common.K_RANGE)
    k = common.choose_k(table)
    common.METRICS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(common.METRICS_DIR / "gmm_k_sweep.csv", index=False)
    plot_bic(table, k)

    gm = make(k).fit(X)
    labels = gm.predict(X)
    metrics = common.evaluate(X, labels)
    metrics["stability_ari"] = common.stability(lambda s: make(k, s).fit(X).predict(X), X)
    metrics["avg_confidence"] = round(float(np.mean(gm.predict_proba(X).max(axis=1))), 3)

    prof = common.profile(prep.data, labels)
    common.plot_clusters(NAME, f"Gaussian Mixture with {k} components", X, labels)
    common.plot_profile(NAME, f"GMM: what makes each of the {k} clusters different",
                        X, prep.names, labels)

    result = common.make_result(NAME, {"components": k, "covariance": "full"}, metrics,
                                started, notes="soft clustering; label = most probable "
                                               "component")
    common.save_result(result, prof)
    return result
