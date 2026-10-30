# Task card - Member 3: Invalid values and outliers

**Branch:** `feature/member3-invalid-and-outliers`
**Your file:** `etl/member3_invalid_and_outliers.py` (function `member3_invalid_and_outliers(df, log, meta)`)
**Your tests:** `tests/test_member3_invalid_and_outliers.py`
**Report you own:** `reports/outlier_report.csv` (stored in `meta["outlier_report"]`)
**Merge position:** third (after Members 1 and 2)

## Goal
Remove records that are impossible and tame extreme values, without throwing away valid bookings.

## Steps
- [ ] 1. Remove bookings with zero guests (166 rows)
- [ ] 2. Remove stays of zero nights (591 rows)
- [ ] 3. Remove negative `avg_daily_rate` (1 row); keep rates of exactly 0 (complimentary stays)
- [ ] 4. Detect outliers with the IQR rule (1.5 x IQR) on `OUTLIER_COLS` and build the outlier table
- [ ] 5. Cap outliers using `CAP_RULES` (IQR cap or percentile cap), do not delete rows (1,088 values capped)
- [ ] 6. Store the outlier table in `meta["outlier_report"]`; log every step with the reason

## Done when
- [ ] `pytest tests/test_member3_invalid_and_outliers.py` passes
- [ ] `python check_member.py 3` prints `CHECK OK after Member 3: 86,638 rows x 35 columns, 0 null values`
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- What is the IQR rule (outside Q1 - 1.5 x IQR or Q3 + 1.5 x IQR)?
- Why cap (winsorise) instead of delete? Why keep zero-price rows?
- Why do `adults`, `children` and `babies` use percentile caps? (their IQR is 0, so the IQR rule flags 10-26% of rows)
- What is the difference between an invalid value and an extreme-but-valid value?
