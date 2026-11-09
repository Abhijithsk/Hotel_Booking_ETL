"""Tests for Logistic Regression (Member 2)."""

import os

import pytest

from ml_helpers import make_ml_df, redirect_outputs
from supervised_model import member2_logistic_regression


@pytest.fixture
def result(monkeypatch, tmp_path):
    redirect_outputs(monkeypatch, tmp_path)
    try:
        res = member2_logistic_regression.run(make_ml_df(), fast=True)
    except NotImplementedError:
        pytest.skip("Member 2 has not implemented Logistic Regression yet")
    return res, tmp_path


def test_result_has_the_standard_fields(result):
    res, _ = result
    assert res["model"] == member2_logistic_regression.NAME
    assert res["task"] == member2_logistic_regression.TASK
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
