"""Tests for the shared clustering helpers (team lead)."""

import numpy as np
import pandas as pd
import pytest

from unsupervised_model import common
from um_helpers import make_df


def test_labels_are_removed_from_the_features():
    prep = common.prepare(make_df())
    assert not set(common.LABEL_COLUMNS) & set(prep.names)


def test_changing_the_labels_does_not_change_the_features():
    df = make_df()
    other = df.copy()
    other["is_cancelled"] = 1 - other["is_cancelled"]
    other["realized_revenue"] = 0.0
    a, b = common.prepare(df), common.prepare(other)
    assert np.allclose(a.X, b.X)


def test_features_are_standardised():
    X = common.prepare(make_df()).X
    assert np.allclose(X.mean(axis=0), 0, atol=1e-8)
    assert np.allclose(X.std(axis=0)[X.std(axis=0) > 0], 1, atol=1e-8)


def test_labels_stay_available_for_the_profile():
    prep = common.prepare(make_df())
    assert "is_cancelled" in prep.data.columns


def test_fast_mode_uses_a_sample():
    assert len(common.prepare(make_df(n=5000), fast=True).X) == 3000


def test_evaluate_scores_obvious_groups_highly():
    rng = np.random.RandomState(0)
    X = np.vstack([rng.randn(200, 3), rng.randn(200, 3) + 12])
    labels = np.repeat([0, 1], 200)
    m = common.evaluate(X, labels)
    assert m["n_clusters"] == 2 and m["silhouette"] > 0.8 and m["noise_pct"] == 0


def test_evaluate_ignores_noise_points():
    rng = np.random.RandomState(0)
    X = np.vstack([rng.randn(100, 2), rng.randn(100, 2) + 10, rng.randn(20, 2) * 30])
    labels = np.concatenate([np.zeros(100), np.ones(100), -np.ones(20)]).astype(int)
    m = common.evaluate(X, labels)
    assert m["noise_pct"] == pytest.approx(9.1, abs=0.1) and m["n_clusters"] == 2


def test_evaluate_with_one_cluster_returns_nan():
    m = common.evaluate(np.random.randn(50, 2), np.zeros(50, dtype=int))
    assert np.isnan(m["silhouette"])


def test_choose_k_combines_both_scores():
    t = pd.DataFrame({"k": [3, 4, 5], "silhouette": [0.30, 0.36, 0.35],
                      "davies_bouldin": [1.5, 1.2, 1.4]})
    assert common.choose_k(t) == 4


def test_choose_k_breaks_ties_with_the_smaller_k():
    t = pd.DataFrame({"k": [3, 4], "silhouette": [0.3, 0.3], "davies_bouldin": [1.0, 1.0]})
    assert common.choose_k(t) == 3


def test_stability_of_a_deterministic_clustering_is_one():
    labels = np.array([0, 1, 0, 1, 2, 2])
    assert common.stability(lambda s: labels, None) == 1.0


def test_profile_uses_the_removed_label_only_for_description():
    df = make_df()
    labels = np.random.RandomState(1).randint(0, 3, len(df))
    prof = common.profile(df, labels)
    assert prof["bookings"].sum() == len(df)
    assert prof["share_of_bookings"].sum() == pytest.approx(1.0, abs=0.01)
    assert prof["cancel_rate"].between(0, 1).all()
