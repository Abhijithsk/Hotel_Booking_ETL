"""Tests for Member 2 - missing-value handling."""


def test_no_missing_values_left(stage2):
    df, _, _ = stage2
    assert int(df.isna().sum().sum()) == 0


def test_company_dropped_but_flag_kept(stage2):
    df, _, _ = stage2
    assert "company" not in df.columns
    assert "has_company" in df.columns
    assert df["has_company"].sum() >= 1            # the sample has one company booking


def test_agent_filled_with_zero_and_flagged(stage2):
    df, _, _ = stage2
    assert "has_agent" in df.columns
    assert (df.loc[df["has_agent"] == 0, "agent"] == 0).all()


def test_placeholders_replaced(stage2):
    df, _, _ = stage2
    assert "undefined" not in set(df["meal"])
    assert "undefined" not in set(df["market_segment"])
    assert "undefined" not in set(df["distribution_channel"])
    assert "unknown" in set(df["market_segment"])


def test_country_and_children_filled(stage2):
    df, _, _ = stage2
    assert "UNK" in set(df["country"])
    assert df["children"].min() >= 0


def test_missing_report_is_stored_in_meta(stage2):
    _, _, meta = stage2
    report = meta["missing_report"]
    assert {"column", "missing_before", "treatment"} <= set(report.columns)
    assert report.loc[report["column"] == "company", "missing_before"].iloc[0] > 0
