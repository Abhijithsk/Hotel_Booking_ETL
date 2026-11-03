"""MEMBER 4 - Feature engineering and final validation.

Totals, revenue, categories, season, guest group, room-changed flag, sorting, final checks.
"""

import numpy as np
import pandas as pd

from etl.common import MIN_COLS, MIN_ROWS, _log


def member4_feature_engineering(df, log):
    """MEMBER 4: calculated columns, categories, sorting, final validation."""
    m = "Member 4"
    n = len(df)

    # 4.1 Calculated columns
    df["total_nights"] = (df["weekend_nights"] + df["week_nights"]).astype("int16")
    df["total_guests"] = (df["adults"] + df["children"] + df["babies"]).astype("int16")
    df["estimated_revenue"] = (df["avg_daily_rate"] * df["total_nights"]
                               * 1.0).round(2)
    df["realized_revenue"] = np.where(df["is_cancelled"] == 0,
                                      df["estimated_revenue"], 0.0)
    _log(log, m, "Create calculated columns (nights, guests, revenue)",
         "Raw data only has parts; totals and revenue are what analysts "
         "actually report on.",
         n, len(df), "total_nights, total_guests, estimated_revenue, realized_revenue")

    # 4.2 Lead-time categories
    df["lead_time_category"] = pd.cut(
        df["lead_time"], bins=[-1, 7, 30, 90, 180, np.inf],
        labels=["0-7d", "8-30d", "31-90d", "91-180d", "180d+"])
    df["stay_length_category"] = pd.cut(
        df["total_nights"], bins=[0, 2, 5, 9, np.inf],
        labels=["short (1-2)", "medium (3-5)", "long (6-9)", "extended (10+)"])
    _log(log, m, "Create categories (lead time, stay length)",
         "Binning continuous values makes patterns easy to compare and "
         "gives models stable categorical features.",
         n, len(df), "lead_time_category, stay_length_category")

    # 4.3 Season
    season_map = {12: "winter", 1: "winter", 2: "winter", 3: "spring",
                  4: "spring", 5: "spring", 6: "summer", 7: "summer",
                  8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"}
    df["season"] = df["arrival_month"].map(season_map)
    df["arrival_year_month"] = df["arrival_date"].dt.strftime("%Y-%m")
    _log(log, m, "Create season and year-month columns",
         "Hotel demand is highly seasonal; these allow monthly and "
         "seasonal reports.",
         n, len(df), "season, arrival_year_month")

    # 4.4 Guest group type
    kids = df["children"] + df["babies"]
    df["guest_group"] = np.select(
        [kids > 0, (df["adults"] == 1) & (kids == 0),
         (df["adults"] == 2) & (kids == 0)],
        ["family", "solo", "couple"], default="group")
    _log(log, m, "Create guest_group (solo / couple / family / group)",
         "A single behavioural segment is easier to analyse than three "
         "separate guest-count columns.",
         n, len(df), "guest_group")

    # 4.5 Room changed flag
    df["room_changed"] = (df["reserved_room_type"] != df["assigned_room_type"]).astype("int8")
    _log(log, m, "Create room_changed flag",
         "Whether the guest got a different room than booked is a known "
         "driver of cancellations and complaints.",
         n, len(df), "room_changed")

    # 4.6 Sort + unique id
    df = df.sort_values(["arrival_date", "hotel"]).reset_index(drop=True)
    df.insert(0, "booking_id", np.arange(1, len(df) + 1))
    front = ["booking_id", "hotel", "is_cancelled", "arrival_date",
             "arrival_year", "arrival_month", "arrival_month_name",
             "arrival_year_month", "season"]
    df = df[front + [c for c in df.columns if c not in front]]
    _log(log, m, "Sort chronologically and add booking_id",
         "Time order is needed for time-series and time-based train/test "
         "splits; booking_id gives every row a unique key.",
         n, len(df), "sorted by arrival_date")

    # 4.7 Final validation checks
    problems = []
    if df.isna().sum().sum() != 0:
        problems.append("null values present")
    if df.duplicated().sum() != 0:
        problems.append("duplicate rows present")
    if (df["total_nights"] <= 0).any():
        problems.append("non-positive total_nights")
    if (df["total_guests"] <= 0).any():
        problems.append("non-positive total_guests")
    if (df["avg_daily_rate"] < 0).any():
        problems.append("negative rates")
    if len(df) < MIN_ROWS or df.shape[1] < MIN_COLS:
        problems.append("dataset smaller than required size")
    if problems:
        raise ValueError("Final validation failed: " + "; ".join(problems))
    _log(log, m, "Final validation checks (nulls, duplicates, ranges, size)",
         "Proves the output really is analysis-ready before it is saved.",
         len(df), len(df), f"all checks passed; final shape {df.shape[0]:,} x {df.shape[1]}")
    return df
