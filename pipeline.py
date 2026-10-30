#!/usr/bin/env python3
"""
Hotel Booking Demand - ETL Pipeline (orchestrator)
==================================================
Extract -> Transform (4 member modules) -> Generate Reports -> Load

Work split (each member owns files inside the etl/ package):
    Member 1 - etl/member1_structural_cleaning.py
    Member 2 - etl/member2_missing_values.py
    Member 3 - etl/member3_invalid_and_outliers.py
    Member 4 - etl/member4_features.py and etl/member4_reports.py

Run:  python pipeline.py
"""

import os
import time

import pandas as pd
import requests

from etl.common import (DATA_URL, MIN_COLS, MIN_ROWS, RAW_DIR, RAW_FILE,
                        REQUIRED_COLUMNS, logger, setup_logging)
from etl.member1_structural_cleaning import member1_structural_cleaning
from etl.member2_missing_values import member2_missing_values
from etl.member3_invalid_and_outliers import member3_invalid_and_outliers
from etl.member4_features import member4_feature_engineering
from etl.member4_reports import generate_reports, load  # noqa: F401  (load() lives here)


# ============================================================================
# STEP 1 - EXTRACT
# ============================================================================
def validate_raw_data(df):
    """Fail early if the file is not what we expect."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Raw data is missing expected columns: {missing}")
    if len(df) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows, got {len(df)}")
    if df.shape[1] < MIN_COLS:
        raise ValueError(f"Need at least {MIN_COLS} columns, got {df.shape[1]}")
    logger.info("Validation passed: expected schema, >= %d rows, >= %d columns",
                MIN_ROWS, MIN_COLS)


def extract():
    """Download the dataset, save a raw copy, show its size and return it."""
    logger.info("=" * 70)
    logger.info("STEP 1: EXTRACT")
    logger.info("=" * 70)
    os.makedirs(RAW_DIR, exist_ok=True)
    try:
        logger.info("Connecting to source: %s", DATA_URL)
        response = requests.get(DATA_URL, timeout=60)
        response.raise_for_status()
        with open(RAW_FILE, "wb") as f:
            f.write(response.content)
        logger.info("Downloaded %.1f MB and saved raw copy to %s",
                    len(response.content) / 1e6, RAW_FILE)
    except requests.RequestException as exc:
        if os.path.exists(RAW_FILE):
            logger.warning("Download failed (%s). Using existing raw copy: %s",
                           exc, RAW_FILE)
        else:
            raise RuntimeError(
                "Could not download the dataset and no local copy exists in "
                "raw_data/. Check your internet connection.") from exc

    # "NULL" / "NA" strings in the file are read as real missing values (NaN)
    df = pd.read_csv(RAW_FILE)
    logger.info("Number of records : %s", f"{len(df):,}")
    logger.info("Number of columns : %d", df.shape[1])
    validate_raw_data(df)
    return df


# ============================================================================
# STEP 2 - TRANSFORM (calls the four member modules in order)
# ============================================================================
def transform(df):
    """Run the four member modules in order. Returns (clean_df, meta)."""
    logger.info("=" * 70)
    logger.info("STEP 2: TRANSFORM")
    logger.info("=" * 70)
    log, meta = [], {"raw_rows": len(df), "raw_cols": df.shape[1]}
    df = member1_structural_cleaning(df.copy(), log)
    df = member2_missing_values(df, log, meta)
    df = member3_invalid_and_outliers(df, log, meta)
    df = member4_feature_engineering(df, log)
    meta["transformation_log"] = pd.DataFrame(log)
    logger.info("Transform finished: %s rows x %d columns (from %s x %d)",
                f"{len(df):,}", df.shape[1],
                f"{meta['raw_rows']:,}", meta["raw_cols"])
    return df, meta


# ============================================================================
# STEP 3 - FULL PIPELINE  (generate_reports() and load() come from Member 4)
# ============================================================================
def run_etl_pipeline():
    """Extract -> Transform -> (Generate Reports) -> Load."""
    setup_logging()
    start = time.time()
    logger.info("HOTEL BOOKING ETL PIPELINE STARTED")
    raw = extract()
    clean, meta = transform(raw)
    reports = generate_reports(clean, meta)
    load(clean, reports)
    logger.info("=" * 70)
    logger.info("PIPELINE FINISHED in %.1f seconds | raw %s x %d -> clean %s x %d",
                time.time() - start, f"{meta['raw_rows']:,}", meta["raw_cols"],
                f"{len(clean):,}", clean.shape[1])
    logger.info("=" * 70)
    return clean


if __name__ == "__main__":
    run_etl_pipeline()
