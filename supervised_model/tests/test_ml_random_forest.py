"""Tests for Random Forest (Member 4)."""

import os

import pytest

from ml_helpers import make_ml_df, redirect_outputs
from supervised_model import member4_random_forest


@pytest.fixture
def result(monkeypatch, tmp_path):
    redirect_outputs(monkeypatch, tmp_path)
    try:
        res = member4_random_forest.run(make_ml_df(), fast=True)
    except NotImplementedError:
        pytest.skip("Member 4 has not implemented Random Forest yet")
    return res, tmp_path


def test_result_has_the_standard_fields(result):
    res, _ = result
    assert res["model"] == member4_random_forest.NAME
    assert res["task"] == member4_random_forest.TASK
    assert res["seconds"] >= 0


def test_metrics_are_valid_probabilities(result):
    res, _ = result
    for key in ("accuracy", "precision", "recall", "f1", "roc_auc"):
        assert 0 <= res[key] <= 1


def test_model_beats_random_guessing(result):
    res, _ = result
    assert res["roc_auc"] > 0.5


def test_metrics_and_charts_are_saved(result):
    res, out = result
    assert os.path.exists(out / "metrics" / f"{res['model']}.csv")
    assert any((out / "charts").glob(f"{res['model']}_*.png"))
