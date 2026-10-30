"""Tests for Member 3 - invalid values and outliers."""


def test_invalid_rows_removed(stage2, stage3):
    before, _, _ = stage2
    after, _, _ = stage3
    assert len(after) == len(before) - 3           # zero guests, zero nights, negative price


def test_no_invalid_values_remain(stage3):
    df, _, _ = stage3
    assert ((df["adults"] + df["children"] + df["babies"]) > 0).all()
    assert ((df["weekend_nights"] + df["week_nights"]) > 0).all()
    assert (df["avg_daily_rate"] >= 0).all()


def test_extreme_price_is_capped_not_deleted(stage3):
    df, _, _ = stage3
    assert df["avg_daily_rate"].max() < 5400       # the 5,400 rate was capped ...
    assert (df["avg_daily_rate"] > 200).any()      # ... but the booking was kept


def test_outlier_report_is_stored_in_meta(stage3):
    _, _, meta = stage3
    report = meta["outlier_report"]
    assert {"column", "outliers_iqr_1_5", "treatment", "max_before", "max_after"} <= set(
        report.columns)
    row = report[report["column"] == "avg_daily_rate"].iloc[0]
    assert row["max_after"] < row["max_before"]


def test_steps_are_logged(stage3):
    _, log, _ = stage3
    assert sum(1 for entry in log if entry["member"] == "Member 3") >= 5
