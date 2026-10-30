# Task card - Member 1: Structural cleaning

**Branch:** `feature/member1-structural-cleaning`
**Your file:** `etl/member1_structural_cleaning.py` (function `member1_structural_cleaning(df, log)`)
**Your tests:** `tests/test_member1_structural_cleaning.py`
**Merge position:** first

## Goal
Take the raw table and make its structure consistent, so every later stage can rely on clear column
names, correct types and no duplicate records.

## Steps
- [ ] 1. Rename columns with `RENAME_MAP` (13 columns), for example `adr` -> `avg_daily_rate`
- [ ] 2. Remove exact duplicate rows (31,994 removed)
- [ ] 3. Standardise text: trim spaces, lower case, country codes upper case
- [ ] 4. Convert dates: build `arrival_date` from year + month + day, parse `reservation_status_date`
- [ ] 5. Change data types to compact integers (`int8` / `int16`)
- [ ] 6. Log every step with `_log(...)` including the reason it was necessary

## Done when
- [ ] `pytest tests/test_member1_structural_cleaning.py` passes
- [ ] `python check_member.py 1` prints `CHECK OK after Member 1: 87,396 rows x 34 columns`
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- Why do duplicates matter for machine learning? (the same row can end up in train and test)
- Why build `arrival_date` from three columns?
- Why use `int8` / `int16` instead of the default `int64`?
