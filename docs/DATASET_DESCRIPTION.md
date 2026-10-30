# Dataset Description (Step 2)

## 1. What is your data source?
The **Hotel Booking Demand** dataset, created by Nuno Antonio, Ana de Almeida and Luis Nunes
(2019).

- **Original publication:** Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand
  datasets.* DOI: <https://doi.org/10.1016/j.dib.2018.11.126>
  (free copy: <https://repositorio.iscte-iul.pt/handle/10071/16929>)
- **Direct download used by the pipeline** (TidyTuesday GitHub copy, 11 Feb 2020 release):
  `https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv`

## 2. Why did you choose it?
- **Size:** 119,390 rows x 32 columns - far above the required 10,000 rows and 18 columns.
- **Real-world and messy:** it contains duplicates, hidden missing values ("Undefined"), a column
  that is 94% empty and extreme outliers, so every preprocessing technique has a real use.
- **Clear business problem:** hotels lose revenue from cancellations, so the cleaned data supports
  a meaningful follow-up project (cancellation prediction, revenue and demand analysis).
- **Mixed data types:** numeric, categorical, binary and date information - good for practising
  many kinds of transformations.
- **Free and downloadable** with no API key.

## 3. What information does it contain?
Booking records for two hotels in Portugal - an H1 **Resort Hotel** (Algarve) and an H2 **City Hotel**
(Lisbon) - with arrival dates from July 2015 to August 2017.

| Group | Columns |
|---|---|
| Booking outcome | `is_canceled`, `reservation_status`, `reservation_status_date` |
| Timing | `lead_time`, `arrival_date_year`, `arrival_date_month`, `arrival_date_week_number`, `arrival_date_day_of_month`, `stays_in_weekend_nights`, `stays_in_week_nights` |
| Guests | `adults`, `children`, `babies`, `country`, `is_repeated_guest`, `customer_type` |
| Booking channel | `market_segment`, `distribution_channel`, `agent`, `company` |
| Room and services | `meal`, `reserved_room_type`, `assigned_room_type`, `booking_changes`, `required_car_parking_spaces`, `total_of_special_requests` |
| Money and policy | `adr` (average daily rate), `deposit_type`, `days_in_waiting_list` |
| History | `previous_cancellations`, `previous_bookings_not_canceled` |

After the pipeline the dataset has **46 columns** (see `output/data_dictionary.csv`).

## 4. Is it structured, semi-structured, or unstructured?
**Structured** - fixed rows and columns in a table.

## 5. What format is the data?
**CSV** (comma-separated values), about 17 MB.

## 6. How frequently is the data updated?
It is **not updated**. It is a one-time historical snapshot (arrivals July 2015 - August 2017) that
was published with the research paper and republished by TidyTuesday in February 2020.
Check the licence terms on the DOI page before redistributing the data. Because it is
static, the pipeline can be re-run at any time and will produce identical results, which also makes
the project reproducible.
