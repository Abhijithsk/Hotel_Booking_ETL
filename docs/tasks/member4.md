# Task card - Member 4: Features, reports and load

**Branch:** `feature/member4-features-and-reports`
**Your files:** `etl/member4_features.py` (`member4_feature_engineering(df, log)`) and
`etl/member4_reports.py` (`generate_reports(df, meta)`, `load(df, reports)`)
**Your tests:** `tests/test_member4_features_and_reports.py`
**Reports you own:** every report except `missing_value_report`, `outlier_report` and `transformation_log`
**Merge position:** last (after Members 1, 2 and 3)

## Goal
Turn the clean data into an analysis-ready dataset with useful features, prove it is valid, then
produce the reports and save everything.

## Steps
- [ ] 1. Calculated columns: `total_nights`, `total_guests`, `estimated_revenue`, `realized_revenue`
- [ ] 2. Categories: `lead_time_category`, `stay_length_category`
- [ ] 3. `season`, `arrival_year_month`, `guest_group` (solo / couple / family / group), `room_changed`
- [ ] 4. Sort by `arrival_date`, add `booking_id`, put the main columns first
- [ ] 5. Final validation checks (no nulls, no duplicates, valid ranges, at least 10,000 rows and 18 columns)
- [ ] 6. `generate_reports()`: ranking, grouping and aggregation reports (at least 3, we have 14)
- [ ] 7. `load()`: save the dataset, every report, the data dictionary and 4 charts
- [ ] 8. Log every step with `_log(...)` including the reason

## Done when
- [ ] `pytest tests/test_member4_features_and_reports.py` passes
- [ ] `python check_member.py 4` prints `PIPELINE FINISHED ... raw 119,390 x 32 -> clean 86,638 x 46`
- [ ] 14 report CSV files are in `reports/` and the dataset and charts are in `output/`
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- Why is `realized_revenue` 0 for cancelled bookings?
- Why sort by date before adding `booking_id`?
- What does the final validation check?
- Why are `reservation_status` and `reservation_status_date` a target-leakage risk?
