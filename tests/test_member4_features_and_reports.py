"""Tests for Member 4 - features, reports and load."""

import os

from etl import member4_reports

NEW_COLUMNS = [
    "booking_id", "total_nights", "total_guests", "estimated_revenue", "realized_revenue",
    "lead_time_category", "stay_length_category", "season", "arrival_year_month",
    "guest_group", "room_changed",
]


def test_new_columns_created(transformed):
    df, _ = transformed
    for col in NEW_COLUMNS:
        assert col in df.columns


def test_calculated_columns_are_correct(transformed):
    df, _ = transformed
    assert (df["total_nights"] == df["weekend_nights"] + df["week_nights"]).all()
    assert (df["total_guests"] == df["adults"] + df["children"] + df["babies"]).all()
    assert (df.loc[df["is_cancelled"] == 1, "realized_revenue"] == 0).all()


def test_sorted_and_unique_booking_id(transformed):
    df, _ = transformed
    assert df["arrival_date"].is_monotonic_increasing
    assert df["booking_id"].is_unique
    assert df["booking_id"].min() == 1


def test_categories_and_groups_have_valid_values(transformed):
    df, _ = transformed
    assert set(df["season"]) <= {"winter", "spring", "summer", "autumn"}
    assert set(df["guest_group"]) <= {"solo", "couple", "family", "group"}
    assert set(df["room_changed"]) <= {0, 1}


def test_final_dataset_is_analysis_ready(transformed):
    df, _ = transformed
    assert int(df.isna().sum().sum()) == 0
    assert not df.duplicated().any()


def test_generate_reports_returns_required_reports(transformed):
    df, meta = transformed
    reports = member4_reports.generate_reports(df, meta)
    required = {"summary_statistics", "monthly_report", "hotel_wise_report",
                "market_segment_report", "top10_countries_by_bookings",
                "missing_value_report", "outlier_report", "transformation_log"}
    assert required <= set(reports)
    assert len(reports) >= 3
    assert all(len(report) > 0 for name, report in reports.items()
               if name != "bottom10_countries_by_avg_rate")


def test_load_writes_all_files(transformed, tmp_path, monkeypatch):
    df, meta = transformed
    reports = member4_reports.generate_reports(df, meta)
    out, rep = tmp_path / "output", tmp_path / "reports"
    monkeypatch.setattr(member4_reports, "OUTPUT_DIR", str(out))
    monkeypatch.setattr(member4_reports, "REPORT_DIR", str(rep))
    monkeypatch.setattr(member4_reports, "CHART_DIR", str(out / "charts"))
    member4_reports.load(df, reports)
    assert (out / "analysis_ready_hotel_bookings.csv").exists()
    assert (out / "data_dictionary.csv").exists()
    assert len(os.listdir(rep)) == len(reports)
    assert len(os.listdir(out / "charts")) >= 1
