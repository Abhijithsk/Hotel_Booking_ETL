"""Shared configuration, paths, logging helpers (used by every member module)."""

import logging
import os

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")

DATA_URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/"
    "master/data/2020/2020-02-11/hotels.csv"
)
RAW_FILE = os.path.join(RAW_DIR, "hotel_bookings_raw.csv")

MIN_ROWS = 10000
MIN_COLS = 18

REQUIRED_COLUMNS = [
    "hotel", "is_canceled", "lead_time", "arrival_date_year",
    "arrival_date_month", "arrival_date_week_number",
    "arrival_date_day_of_month", "stays_in_weekend_nights",
    "stays_in_week_nights", "adults", "children", "babies", "meal",
    "country", "market_segment", "distribution_channel",
    "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "reserved_room_type",
    "assigned_room_type", "booking_changes", "deposit_type", "agent",
    "company", "days_in_waiting_list", "customer_type", "adr",
    "required_car_parking_spaces", "total_of_special_requests",
    "reservation_status", "reservation_status_date",
]

RENAME_MAP = {
    "is_canceled": "is_cancelled",
    "adr": "avg_daily_rate",
    "is_repeated_guest": "is_repeat_guest",
    "arrival_date_year": "arrival_year",
    "arrival_date_month": "arrival_month_name",
    "arrival_date_week_number": "arrival_week",
    "arrival_date_day_of_month": "arrival_day",
    "stays_in_weekend_nights": "weekend_nights",
    "stays_in_week_nights": "week_nights",
    "days_in_waiting_list": "waiting_days",
    "required_car_parking_spaces": "parking_spaces",
    "total_of_special_requests": "special_requests",
    "previous_bookings_not_canceled": "previous_bookings_kept",
}

MONTHS = {
    m: i for i, m in enumerate(
        ["january", "february", "march", "april", "may", "june", "july",
         "august", "september", "october", "november", "december"], start=1)
}

# column -> (method, parameter).  iqr = Q3 + k*IQR ; pct = percentile cap
CAP_RULES = {
    "avg_daily_rate": ("iqr", 3.0),
    "lead_time": ("iqr", 3.0),
    "weekend_nights": ("pct", 99.9),
    "week_nights": ("pct", 99.9),
    "adults": ("pct", 99.9),
    "children": ("pct", 99.9),
    "babies": ("pct", 99.9),
    "booking_changes": ("pct", 99.9),
    "waiting_days": ("pct", 99.5),
}

OUTLIER_COLS = [
    "lead_time", "avg_daily_rate", "weekend_nights", "week_nights", "adults",
    "children", "babies", "previous_cancellations", "previous_bookings_kept",
    "booking_changes", "waiting_days", "parking_spaces", "special_requests",
]

logger = logging.getLogger("etl")


def setup_logging():
    """Log to the console and to output/pipeline_run.log."""
    for folder in (RAW_DIR, REPORT_DIR, OUTPUT_DIR, CHART_DIR):
        os.makedirs(folder, exist_ok=True)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(message)s", "%H:%M:%S")
    for handler in (
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(OUTPUT_DIR, "pipeline_run.log"),
                            mode="w", encoding="utf-8"),
    ):
        handler.setFormatter(fmt)
        logger.addHandler(handler)


def _log(log, member, step, why, rows_before, rows_after, detail=""):
    """Append one documented transformation step to the transformation log."""
    log.append({
        "step_no": len(log) + 1,
        "member": member,
        "transformation": step,
        "why_it_was_needed": why,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "details": detail,
    })
    logger.info("  [%s] %s | rows %s -> %s | %s",
                member, step, f"{rows_before:,}", f"{rows_after:,}", detail)
