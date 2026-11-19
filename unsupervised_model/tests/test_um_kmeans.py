"""Tests for K-Means clustering (Member 1)."""

import os

import numpy as np
import pytest

from um_helpers import make_df, redirect_outputs
from unsupervised_model import member1_kmeans


@pytest.fixture
def result(monkeypatch, tmp_path):
    redirect_outputs(monkeypatch, tmp_path)
    try:
        res = member1_kmeans.run(make_df(), fast=True)
    except NotImplementedError:
        pytest.skip("Member 1 has not implemented K-Means yet")
    return res, tmp_path


def test_result_has_the_standard_fields(result):
    res, _ = result
    assert res["model"] == member1_kmeans.NAME
    for key in ("n_clusters", "silhouette", "davies_bouldin", "noise_pct", "seconds"):
        assert key in res


def test_scores_are_in_valid_ranges(result):
    res, _ = result
    assert 0 <= res["noise_pct"] <= 100
    assert res["n_clusters"] >= 1
    if not np.isnan(res["silhouette"]):
        assert -1 <= res["silhouette"] <= 1
        assert res["davies_bouldin"] >= 0


def test_all_bookings_get_a_cluster_and_groups_are_found(result):
    res, _ = result
    assert res["noise_pct"] == 0
    assert 3 <= res["n_clusters"] <= 8
    assert res["silhouette"] > 0.3


def test_results_are_saved(result):
    res, out = result
    assert os.path.exists(out / "metrics" / f"{res['model']}.csv")
    assert os.path.exists(out / "profiles" / f"{res['model']}_profile.csv")
    assert any((out / "charts").glob(f"{res['model']}_*.png"))
