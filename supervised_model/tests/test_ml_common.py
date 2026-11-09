"""Tests for the shared machine-learning helpers (team lead)."""

import numpy as np
import pytest

from supervised_model import common
from ml_helpers import make_ml_df


def test_no_leakage_columns_are_used():
    for task in ("regression", "classification"):
        numeric, categorical = common.feature_lists(task)
        assert not set(numeric + categorical) & set(common.LEAKAGE)
        assert common.TARGETS[task] not in numeric + categorical


def test_price_is_input_only_for_classification():
    assert "avg_daily_rate" in common.feature_lists("classification")[0]
    assert "avg_daily_rate" not in common.feature_lists("regression")[0]


def test_unknown_task_is_rejected():
    with pytest.raises(ValueError):
        common.feature_lists("clustering")


def test_split_is_80_20_and_reproducible():
    df = make_ml_df()
    a = common.prepare(df, "classification")
    b = common.prepare(df, "classification")
    assert len(a[1]) == pytest.approx(0.2 * len(df), abs=1)
    assert a[0].index.equals(b[0].index)


def test_classification_split_keeps_class_ratio():
    df = make_ml_df()
    _, _, y_train, y_test = common.prepare(df, "classification")
    assert y_train.mean() == pytest.approx(y_test.mean(), abs=0.02)


def test_fast_mode_uses_a_small_sample():
    df = make_ml_df(n=5000)
    X_train, X_test, _, _ = common.prepare(df, "regression", fast=True)
    assert len(X_train) + len(X_test) == 3000


def test_preprocessor_output_is_numeric_and_has_no_nan():
    df = make_ml_df()
    X_train, X_test, _, _ = common.prepare(df, "classification")
    prep = common.build_preprocessor("classification")
    out = prep.fit(X_train).transform(X_test)
    assert out.shape[0] == len(X_test)
    assert not np.isnan(out).any()


def test_metric_helpers():
    y = np.array([0, 0, 1, 1])
    m = common.classification_metrics(y, y, y)
    assert m["accuracy"] == m["f1"] == m["roc_auc"] == 1.0
    r = common.regression_metrics(np.array([1.0, 2.0]), np.array([1.0, 2.0]), 1.5)
    assert r["mae"] == 0 and r["r2"] == 1.0
