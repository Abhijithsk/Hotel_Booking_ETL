# Task card - Member 2: Missing-value handling

**Branch:** `feature/member2-missing-values`
**Your file:** `etl/member2_missing_values.py` (function `member2_missing_values(df, log, meta)`)
**Your tests:** `tests/test_member2_missing_values.py`
**Report you own:** `reports/missing_value_report.csv` (stored in `meta["missing_report"]`)
**Merge position:** second (after Member 1)

## Goal
Make sure the dataset has **no missing values**, using the right strategy for each column, and
document what was done.

## Steps
- [ ] 1. Audit missing data, including hidden `undefined` text (7 columns affected)
- [ ] 2. Replace `undefined` in `meal` (-> `sc`), `market_segment` and `distribution_channel` (-> `unknown`)
- [ ] 3. Drop `company` (94% missing) and keep a `has_company` flag
- [ ] 4. Fill `agent` with 0 and add a `has_agent` flag
- [ ] 5. Fill `children` with 0 and `country` with `UNK`
- [ ] 6. Raise an error if any null value is left; store the audit table in `meta["missing_report"]`
- [ ] 7. Log every step with `_log(...)` including the reason

## Done when
- [ ] `pytest tests/test_member2_missing_values.py` passes
- [ ] `python check_member.py 2` prints `CHECK OK after Member 2: 87,396 rows x 35 columns, 0 null values`
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- Why drop `company` but keep a flag?
- Why is a missing `agent` filled with 0 instead of the most common agent?
- What are "hidden" missing values and why does `isna()` miss them?
- Why fill `country` with `UNK` instead of the most common country?
