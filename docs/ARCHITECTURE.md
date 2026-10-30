# Architecture

## Data flow
```
raw_data/hotel_bookings_raw.csv  (119,390 x 32)
        |
        v   extract()            pipeline.py
   raw DataFrame
        |
        v   transform()          pipeline.py calls the member modules in this order
 +------------------------------------------------------------------+
 | member1_structural_cleaning(df, log)          -> df   87,396 x 34 |
 | member2_missing_values(df, log, meta)         -> df   87,396 x 35 |
 | member3_invalid_and_outliers(df, log, meta)   -> df   86,638 x 35 |
 | member4_feature_engineering(df, log)          -> df   86,638 x 46 |
 +------------------------------------------------------------------+
        |                      (clean_df, meta)
        v   generate_reports(df, meta)           member4_reports.py
   dict {report_name: DataFrame}   (14 reports)
        |
        v   load(df, reports)                    member4_reports.py
 output/analysis_ready_hotel_bookings.csv, output/data_dictionary.csv, output/charts/*.png
 reports/*.csv
```
`run_etl_pipeline()` in `pipeline.py` runs everything and is only executed when the file is run
directly (`python pipeline.py`).

## The contract between modules
Modules only talk to each other through the DataFrame, the `log` list and the `meta` dictionary.
Keeping these stable is what lets four people work in parallel.

| Function | Receives | Must return | Must also write to |
|---|---|---|---|
| `member1_structural_cleaning(df, log)` | raw DataFrame | cleaned DataFrame with the new column names and an `arrival_date` column | `log` (via `_log`) |
| `member2_missing_values(df, log, meta)` | Member 1 output | DataFrame with **no null values** | `log`, `meta["missing_report"]` |
| `member3_invalid_and_outliers(df, log, meta)` | Member 2 output | DataFrame without invalid rows, outliers capped | `log`, `meta["outlier_report"]` |
| `member4_feature_engineering(df, log)` | Member 3 output | final DataFrame (adds features, sorted, validated) | `log` |
| `generate_reports(df, meta)` | final DataFrame + `meta` | `{file_name: DataFrame}` | - |
| `load(df, reports)` | final DataFrame + reports | nothing | files in `output/` and `reports/` |

`transform()` adds `meta["transformation_log"]` (the `log` list as a DataFrame) at the end.

### Shared helpers (`etl/common.py`)
- Paths: `RAW_DIR`, `REPORT_DIR`, `OUTPUT_DIR`, `CHART_DIR`, `RAW_FILE`.
- Settings: `RENAME_MAP`, `MONTHS`, `CAP_RULES`, `OUTLIER_COLS`, `MIN_ROWS`, `MIN_COLS`.
- `_log(log, member, step, why, rows_before, rows_after, detail)` records one documented step.
- `logger` writes to the console and to `output/pipeline_run.log`.

### Column names used across modules
| Stage | New / changed columns |
|---|---|
| After Member 1 | renamed columns (`is_cancelled`, `avg_daily_rate`, `weekend_nights`, `week_nights`, `waiting_days`, `parking_spaces`, `special_requests`, `previous_bookings_kept`, ...), `arrival_month`, `arrival_date` |
| After Member 2 | `has_company`, `has_agent`; `company` removed |
| After Member 3 | same columns, fewer rows, capped values |
| After Member 4 | `booking_id`, `total_nights`, `total_guests`, `estimated_revenue`, `realized_revenue`, `lead_time_category`, `stay_length_category`, `season`, `arrival_year_month`, `guest_group`, `room_changed` |

## Testing strategy
- `tests/conftest.py` builds a small raw-like table that contains every problem type, so the tests
  run in under two seconds and need no internet.
- Each member has their own test file. Tests that depend on an unfinished earlier stage are
  **skipped**, not failed, so the repository stays green while the team is working.
- `check_member.py N` runs the real data through the pipeline up to stage N for a manual check.
- GitHub Actions (`.github/workflows/ci.yml`) runs `flake8` and `pytest` on Python 3.10, 3.11 and
  3.12 for every push and pull request.

## Design decisions
- **Stages as pure functions of a DataFrame** (apart from `meta` and `log`), so each stage can be
  tested alone.
- **Cap instead of delete** for outliers, to keep valid bookings.
- **One module per member** so pull requests touch different files and never conflict.
- **Raw data is never modified;** a copy is saved in `raw_data/` and all work happens on copies.
