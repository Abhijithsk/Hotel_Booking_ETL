"""MEMBER 1 - Structural cleaning.

Rename columns, remove duplicates, standardise text, build dates, fix data types.
"""

import pandas as pd

from etl.common import MONTHS, RENAME_MAP, _log


def member1_structural_cleaning(df, log):
    """MEMBER 1: rename columns, remove duplicates, standardise text,
    convert dates and data types."""
    m = "Member 1"
    n = len(df)

    # 1.1 Rename columns
    df = df.rename(columns=RENAME_MAP)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    _log(log, m, "Rename columns to clear, consistent names",
         "Original names such as 'adr' or 'stays_in_week_nights' are cryptic "
         "or long; clear names make later analysis code readable.",
         n, len(df), f"{len(RENAME_MAP)} columns renamed")

    # 1.2 Remove duplicate records
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    _log(log, m, "Remove exact duplicate records",
         "Duplicate bookings inflate counts and revenue and leak identical "
         "rows between train and test sets in ML.",
         before, len(df), f"{before - len(df):,} duplicate rows removed")

    # 1.3 Standardise text
    text_cols = [c for c in df.columns
                 if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    for c in text_cols:
        df[c] = df[c].str.strip().str.lower()
    df["country"] = df["country"].str.upper()   # ISO country codes are upper case
    _log(log, m, "Standardise text (trim spaces, lower case, ISO codes upper)",
         "Mixed case or stray spaces create fake categories "
         "('City Hotel' vs 'city hotel').",
         len(df), len(df), f"{len(text_cols)} text columns standardised")

    # 1.4 Convert dates
    df["arrival_month"] = df["arrival_month_name"].map(MONTHS)
    if df["arrival_month"].isna().any():
        raise ValueError("Unknown month name found in arrival_month_name")
    parts = df[["arrival_year", "arrival_month", "arrival_day"]].rename(
        columns={"arrival_year": "year", "arrival_month": "month",
                 "arrival_day": "day"})
    df["arrival_date"] = pd.to_datetime(parts)
    df["reservation_status_date"] = pd.to_datetime(
        df["reservation_status_date"], errors="coerce")
    _log(log, m, "Convert dates (build arrival_date, parse status date)",
         "Year, month name and day were in 3 separate columns; a real "
         "datetime enables sorting, monthly grouping and time-series work.",
         len(df), len(df), "arrival_date created; reservation_status_date parsed")

    # 1.5 Fix data types
    int8_cols = ["is_cancelled", "is_repeat_guest", "arrival_month",
                 "arrival_week", "arrival_day"]
    int16_cols = ["arrival_year", "lead_time", "weekend_nights", "week_nights",
                  "adults", "babies", "previous_cancellations",
                  "previous_bookings_kept", "booking_changes", "waiting_days",
                  "parking_spaces", "special_requests"]
    for c in int8_cols:
        df[c] = df[c].astype("int8")
    for c in int16_cols:
        df[c] = df[c].astype("int16")
    _log(log, m, "Change data types (compact integers)",
         "Default int64 wastes memory; correct types also document that "
         "flags are binary and counts are whole numbers.",
         len(df), len(df), f"{len(int8_cols) + len(int16_cols)} columns down-cast")
    return df
