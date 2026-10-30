# Hotel Booking Demand - ETL Pipeline

[![CI](https://github.com/Abhijithsk/Hotel_Booking_ETL/actions/workflows/ci.yml/badge.svg)](https://github.com/Abhijithsk/Hotel_Booking_ETL/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A team mini-project that builds an automated **Extract - Transform - Load (ETL)** pipeline. It turns
the raw *Hotel Booking Demand* data (**119,390 rows x 32 columns**, with duplicates, hidden missing
values and outliers) into a clean, documented, **analysis-ready dataset (86,638 rows x 46 columns)**
for future Data Science projects such as cancellation prediction, revenue analysis and demand
forecasting.

## Contents
- [Objective](#objective)
- [Data source](#data-source)
- [ETL workflow](#etl-workflow)
- [Project structure](#project-structure)
- [Quick start](#quick-start)
- [Team and responsibilities](#team-and-responsibilities)
- [Transformations](#transformations)
- [Reports generated](#reports-generated)
- [Key findings](#key-findings)
- [Challenges faced](#challenges-faced)
- [Learning outcomes](#learning-outcomes)
- [Future improvements](#future-improvements)
- [Contributing](#contributing)

## Objective
Prepare one trustworthy, well-documented dataset so that later projects can start with modelling
instead of cleaning. Every transformation is logged with the reason it was needed
(`reports/transformation_log.csv`).

## Data source
| Item | Detail |
|---|---|
| Dataset | Hotel Booking Demand - two hotels in Portugal (resort and city hotel) |
| Original publication | Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets.* [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126) |
| Direct download | [`hotels.csv` (TidyTuesday GitHub copy)](https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv) |
| Format / type | CSV, structured, about 17 MB |
| Period | Arrivals July 2015 - August 2017 |
| Updates | Static historical snapshot, never updated |

Details: [docs/DATASET_DESCRIPTION.md](docs/DATASET_DESCRIPTION.md). Check the licence terms on the
DOI page before redistributing the data.

## ETL workflow
```
        Data Source (CSV on GitHub)
                  |
                  v
   +------------------------------+
   | EXTRACT  extract()           |  download, save raw copy in raw_data/,
   |                              |  show rows/columns, validate schema and size
   +------------------------------+
                  |
                  v
   +------------------------------+
   | TRANSFORM  transform()       |
   |  Member 1  structural clean  |  rename, duplicates, text, dates, dtypes
   |  Member 2  missing values    |  placeholders, drop / flag / impute
   |  Member 3  invalid + outliers|  business rules, IQR detection, capping
   |  Member 4  features + checks |  new columns, categories, sort, validation
   +------------------------------+
                  |
                  v
   +------------------------------+
   | GENERATE REPORTS  (Member 4) |  14 report tables
   +------------------------------+
                  |
                  v
   +------------------------------+
   | LOAD  load()      (Member 4) |  CSV files -> reports/ and output/, charts
   +------------------------------+
```
More detail and the interface between the modules: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Project structure
```
Hotel_Booking_ETL/
├── .github/
│   ├── workflows/ci.yml             lint + tests on every push and pull request
│   ├── ISSUE_TEMPLATE/              task and bug templates
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
├── docs/
│   ├── ARCHITECTURE.md              data flow and the contract between modules
│   ├── DATASET_DESCRIPTION.md
│   ├── GIT_WORKFLOW.md              step-by-step Git commands for the team
│   └── tasks/                       one task card per member
├── etl/                             the pipeline code, one module per member
│   ├── common.py                    shared config, paths, logging helper
│   ├── member1_structural_cleaning.py
│   ├── member2_missing_values.py
│   ├── member3_invalid_and_outliers.py
│   ├── member4_features.py
│   └── member4_reports.py           generate_reports() + load()
├── tests/                           automated tests, one file per member
├── raw_data/                        untouched copy of the source file
├── reports/                         generated report CSVs
├── output/                          analysis-ready dataset, data dictionary, charts, log
├── screenshots/                     run screenshots
├── pipeline.py                      extract(), transform(), run_etl_pipeline()
├── check_member.py                  run the pipeline up to one member's stage
├── requirements.txt / requirements-dev.txt
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Quick start
```bash
git clone https://github.com/Abhijithsk/Hotel_Booking_ETL.git
cd Hotel_Booking_ETL
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python pipeline.py            # run the full ETL (about 5 seconds, needs internet the first time)
pytest                        # run the tests
flake8 .                      # check code style
```
`python check_member.py 1|2|3|4` runs the pipeline only up to that member's stage.
If the download fails but `raw_data/hotel_bookings_raw.csv` exists, the pipeline uses that copy.

## Team and responsibilities
| Member | GitHub | Module(s) | Task card |
|---|---|---|---|
| Member 1 | _add username_ | `etl/member1_structural_cleaning.py` | [docs/tasks/member1.md](docs/tasks/member1.md) |
| Member 2 | _add username_ | `etl/member2_missing_values.py` | [docs/tasks/member2.md](docs/tasks/member2.md) |
| Member 3 | _add username_ | `etl/member3_invalid_and_outliers.py` | [docs/tasks/member3.md](docs/tasks/member3.md) |
| Member 4 | _add username_ | `etl/member4_features.py`, `etl/member4_reports.py` | [docs/tasks/member4.md](docs/tasks/member4.md) |
| Team lead | [@Abhijithsk](https://github.com/Abhijithsk) | `pipeline.py`, `etl/common.py`, docs, CI | - |

Each member works on their own branch and in their own files, so merges do not conflict. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

## Transformations
23 documented steps (the assignment required at least 8). Each step is also saved with its reason
in `reports/transformation_log.csv`.

| # | Member | Transformation | Why it was necessary |
|---|---|---|---|
| 1 | 1 | Rename columns (`adr` -> `avg_daily_rate`, ...) | Cryptic names slow analysis (13 renamed) |
| 2 | 1 | Remove exact duplicate rows | Duplicates inflate counts and leak between train/test (31,994 removed) |
| 3 | 1 | Standardise text | Avoid fake categories such as `City Hotel` vs `city hotel` |
| 4 | 1 | Convert dates (build `arrival_date`) | Enables sorting and time series |
| 5 | 1 | Change data types | Lower memory, correct semantics |
| 6 | 2 | Missing-value audit incl. hidden `Undefined` | Measure before fixing (7 columns affected) |
| 7 | 2 | Replace `undefined` placeholders | `meal` Undefined means SC (no package); others become `unknown` |
| 8 | 2 | Drop `company` (94% missing), keep `has_company` | Too empty to impute; the signal is kept as a flag |
| 9 | 2 | Fill `agent` with 0 + `has_agent` | Missing agent means a direct booking (12,193 rows) |
| 10 | 2 | Fill `children` with 0 | Only 4 rows missing, 0 is the mode |
| 11 | 2 | Fill `country` with `UNK` | Do not guess a country (452 rows) |
| 12 | 3 | Remove zero-guest bookings | Data-entry error (166 rows) |
| 13 | 3 | Remove zero-night stays | No duration or revenue (591 rows) |
| 14 | 3 | Remove negative room rates | A price cannot be negative (1 row) |
| 15 | 3 | Detect outliers (IQR, 1.5 x IQR) | Measure extremes first |
| 16 | 3 | Cap outliers (winsorise) | Keeps the row, removes the distortion (1,088 values) |
| 17 | 4 | Calculated columns (nights, guests, revenue) | Analysts report totals and revenue |
| 18 | 4 | Categories (`lead_time_category`, `stay_length_category`) | Easier comparison, stable features |
| 19 | 4 | `season` and `arrival_year_month` | Hotel demand is seasonal |
| 20 | 4 | `guest_group` (solo / couple / family / group) | One behavioural segment |
| 21 | 4 | `room_changed` flag | Known cancellation driver |
| 22 | 4 | Sort by date + `booking_id` | Time-based splits, unique key |
| 23 | 4 | Final validation checks | Prove the data is analysis-ready |

## Reports generated
All reports are saved in `reports/`; the full dataset, a data dictionary and 4 charts are saved in `output/`.

| File | Content |
|---|---|
| `summary_statistics.csv` | count, mean, std, quartiles, median, skewness of every numeric column |
| `top10_countries_by_bookings.csv` | Top 10 countries with ranking, cancellation rate, revenue |
| `bottom10_countries_by_avg_rate.csv` | 10 cheapest countries (at least 100 bookings) |
| `top10_highest_revenue_bookings.csv` | 10 highest-revenue bookings |
| `monthly_report.csv` | Bookings, cancellations, rate, revenue per month |
| `hotel_wise_report.csv` | City hotel vs resort hotel |
| `market_segment_report.csv` | Category-wise report |
| `lead_time_cancellation_report.csv` | Cancellation rate by lead-time bucket |
| `deposit_type_report.csv` | Cancellation by deposit type |
| `season_hotel_report.csv` | Season x hotel |
| `guest_group_report.csv` | Solo / couple / family / group |
| `missing_value_report.csv` | Missing values before/after with the treatment used |
| `outlier_report.csv` | IQR fences, counts and caps applied |
| `transformation_log.csv` | All 23 steps with reasons |

## Key findings
- Overall cancellation rate is **27.7%** (city hotel 30.2%, resort hotel 23.7%).
- Cancellations rise with lead time: **8.5%** (0-7 days) up to **39.9%** (180+ days).
- Online travel agents make 59% of bookings and cancel at **35.6%**; corporate bookings cancel at 12.2%.
- Non-refundable deposits show a **94.7%** cancellation rate (1,038 bookings), a surprising pattern worth investigating.
- Portugal (PRT) is the biggest source market (26,864 bookings) and also cancels the most (36.4%).

## Challenges faced
- **Hidden missing values:** `meal`, `market_segment` and `distribution_channel` use the text
  "Undefined" instead of blanks, so a plain null check misses them.
- **Heavy missingness:** `company` is 94% empty and `agent` 14% empty, so deleting rows was not an option.
- **Many duplicates:** 31,994 duplicate rows (27% of the file) and no booking id to identify them.
- **Outliers in count columns:** for `adults`, `children`, `babies` and `booking_changes` the IQR is 0,
  so the IQR rule flags 10-26% of rows; percentile caps were used for these.
- **Valid vs invalid values:** zero room rates are real complimentary stays (kept), zero-guest and
  zero-night bookings are errors (removed).
- **Target leakage:** `reservation_status` and `reservation_status_date` reveal whether a booking was
  cancelled and must be excluded when training a cancellation model.
- **Team collaboration:** splitting one pipeline into independent modules that merge without
  conflicts, with tests that skip until a teammate's module exists.

## Learning outcomes
- Designing an ETL pipeline with separate, testable stages and a single entry point.
- Auditing data quality (missing values, duplicates, outliers) before cleaning.
- Choosing the right missing-value strategy per column (drop, flag, impute, label).
- Telling invalid values (remove) from extreme-but-valid values (cap).
- Feature engineering and documenting every transformation with its reason.
- Spotting data-science pitfalls such as target leakage.
- Team Git workflow: branches, pull requests, code review, CI checks.

## Future improvements
- Load the cleaned data into a database (SQLite / PostgreSQL) and save it also as Parquet.
- Add schema validation (for example `pandera`) and command-line options for `pipeline.py`.
- Schedule the pipeline (cron / Airflow) for datasets that update regularly.
- Add a dashboard (Streamlit / Power BI) on top of the reports.
- Extend the project with a cancellation-prediction model (drop the leakage columns first).

## Contributing
Read [CONTRIBUTING.md](CONTRIBUTING.md) first. In short: one branch per member, small commits with
clear messages, open a pull request, wait for green CI and one review before merging.

## License
Code: [MIT](LICENSE). The dataset has its own terms, see the publication linked above.
