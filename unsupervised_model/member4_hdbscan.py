"""MEMBER 4 - HDBSCAN (density-based clustering).

Idea: find dense regions of bookings; the number of clusters is NOT chosen by us, and bookings
that do not belong to any dense region are labelled noise (-1). Good at ignoring outliers and
at finding clusters of any shape.

On this data it finds a few dense groups and labels a share of the bookings as noise (12
percent in our run, and 10-40 percent with other settings), because guests form a continuous
cloud rather than separate islands. That makes it a poor choice for splitting ALL guests into
segments and a good illustration of when density-based clustering does not fit. It runs on a
random sample of 15,000 bookings (the full data takes about 2.5 minutes) and is scored on that
sample.
"""

import time
import warnings

import numpy as np
from sklearn.cluster import HDBSCAN

from unsupervised_model import common

NAME = "hdbscan"
SAMPLE = 15000


def run(df=None, fast=False):
    """Cluster a sample with HDBSCAN, score the non-noise points, draw and save."""
    started = time.time()
    df = common.load_data() if df is None else df
    prep = common.prepare(df, fast)

    idx = np.random.RandomState(common.SEED).choice(len(prep.X), min(SAMPLE, len(prep.X)),
                                                    replace=False)
    Xs = prep.X[idx]
    data = prep.data.iloc[idx].reset_index(drop=True)
    min_cluster_size = max(20, int(0.02 * len(Xs)))      # a cluster needs >= 2% of the sample

    with warnings.catch_warnings():          # newer scikit-learn versions warn about `copy`
        warnings.simplefilter("ignore", FutureWarning)
        labels = HDBSCAN(min_cluster_size=min_cluster_size, n_jobs=-1).fit_predict(Xs)
    metrics = common.evaluate(Xs, labels)

    prof = common.profile(data, labels)
    common.plot_clusters(NAME, f"HDBSCAN found {metrics['n_clusters']} dense clusters",
                         Xs, labels)
    if metrics["n_clusters"] >= 1:
        common.plot_profile(NAME, "HDBSCAN: what makes each dense cluster different",
                            Xs, prep.names, labels)

    result = common.make_result(
        NAME, {"min_cluster_size": min_cluster_size, "sample": len(Xs)}, metrics, started,
        notes=f"scored on a {len(Xs):,}-booking sample; noise points are not clustered")
    common.save_result(result, prof)
    return result
