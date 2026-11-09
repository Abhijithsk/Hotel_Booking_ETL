"""Tests for Linear Regression (Member 1)."""

import os

import pytest

from ml_helpers import make_ml_df, redirect_outputs
from supervised_model import member1_linear_regression


@pytest.fixture
def result(monkeypatch, tmp_path):
    redirect_outputs(monkeypatch, tmp_path)
    try:
        res = member1_linear_regression.run(make_ml_df(), fast=True)
    except NotImplementedError:
        pytest.skip("Member 1 has not implemented Linear Regression yet")
    return res, tmp_path


def test_result_has_the_standard_fields(result):
    res, _ = result
    assert res["model"] == member1_linear_regression.NAME
    assert res["task"] == member1_linear_regression.TASK
    assert res["seconds"] >= 0


def test_error_metrics_are_sensible(result):
    res, _ = result
    assert res["mae"] >= 0 and res["rmse"] >= res["mae"]


def test_model_beats_predicting_the_mean(result):
    res, _ = result
    assert res["rmse"] < res["baseline_rmse"]
    assert res["r2"] > 0


def test_metrics_and_charts_are_saved(result):
    res, out = result
    assert os.path.exists(out / "metrics" / f"{res['model']}.csv")
    assert any((out / "charts").glob(f"{res['model']}_*.png"))
