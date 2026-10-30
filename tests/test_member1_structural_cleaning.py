"""Tests for Member 1 - structural cleaning."""

import pandas as pd


def test_duplicates_removed(raw_sample, stage1):
    df, _ = stage1
    assert len(df) == len(raw_sample) - 1          # exactly one duplicate in the sample
    assert not df.duplicated().any()


def test_columns_renamed(stage1):
    df, _ = stage1
    for new in ("is_cancelled", "avg_daily_rate", "weekend_nights", "week_nights",
                "waiting_days", "parking_spaces", "special_requests"):
        assert new in df.columns
    for old in ("is_canceled", "adr", "stays_in_week_nights"):
        assert old not in df.columns


def test_text_is_standardised(stage1):
    df, _ = stage1
    assert set(df["hotel"].unique()) <= {"city hotel", "resort hotel"}
    assert df["country"].dropna().str.isupper().all()
    assert df["meal"].str.islower().all()


def test_dates_are_real_dates(stage1):
    df, _ = stage1
    assert pd.api.types.is_datetime64_any_dtype(df["arrival_date"])
    assert pd.api.types.is_datetime64_any_dtype(df["reservation_status_date"])
    assert df["arrival_month"].between(1, 12).all()


def test_integer_columns_downcast(stage1):
    df, _ = stage1
    assert str(df["is_cancelled"].dtype) == "int8"
    assert str(df["lead_time"].dtype) == "int16"


def test_every_step_is_logged(stage1):
    _, log = stage1
    assert len(log) >= 5
    assert {entry["member"] for entry in log} == {"Member 1"}
    assert all(entry["why_it_was_needed"] for entry in log)
