"""MEMBER 4 - Reports (generate_reports) and Load (load + charts)."""

import os

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # no display needed - charts are saved to files
import matplotlib.pyplot as plt  # noqa: E402

from etl.common import CHART_DIR, OUTPUT_DIR, REPORT_DIR, logger  # noqa: E402


def _group_report(df, by):
    out = df.groupby(by, observed=True).agg(
        total_bookings=("booking_id", "count"),
        cancelled_bookings=("is_cancelled", "sum"),
        avg_daily_rate=("avg_daily_rate", "mean"),
        avg_lead_time=("lead_time", "mean"),
        avg_nights=("total_nights", "mean"),
        realized_revenue=("realized_revenue", "sum"),
    ).reset_index()
    out["cancellation_rate_pct"] = (
        100 * out["cancelled_bookings"] / out["total_bookings"]).round(2)
    for c in ("avg_daily_rate", "avg_lead_time", "avg_nights", "realized_revenue"):
        out[c] = out[c].round(2)
    return out


def generate_reports(df, meta):
    """Build every report as a DataFrame. Returns {file_name: DataFrame}."""
    logger.info("=" * 70)
    logger.info("STEP 3: GENERATE REPORTS")
    logger.info("=" * 70)
    reports = {}

    # Summary statistics
    num = df.select_dtypes(include="number").drop(columns=["booking_id"])
    stats = num.describe().T
    stats["median"] = num.median()
    stats["skewness"] = num.skew()
    reports["summary_statistics"] = stats.round(2).reset_index().rename(
        columns={"index": "column"})

    # Country reports
    country = _group_report(df, "country")
    top = country.sort_values("total_bookings", ascending=False).head(10).copy()
    top.insert(0, "rank", range(1, len(top) + 1))
    reports["top10_countries_by_bookings"] = top
    big = country[country["total_bookings"] >= 100]
    bottom = big.sort_values("avg_daily_rate").head(10).copy()
    bottom.insert(0, "rank", range(1, len(bottom) + 1))
    reports["bottom10_countries_by_avg_rate"] = bottom

    # Highest revenue bookings
    cols = ["booking_id", "hotel", "arrival_date", "country", "market_segment",
            "total_nights", "total_guests", "avg_daily_rate", "realized_revenue"]
    reports["top10_highest_revenue_bookings"] = (
        df.sort_values("realized_revenue", ascending=False)[cols].head(10))

    # Group reports
    reports["monthly_report"] = _group_report(df, "arrival_year_month")
    reports["hotel_wise_report"] = _group_report(df, "hotel")
    reports["market_segment_report"] = _group_report(df, "market_segment").sort_values(
        "total_bookings", ascending=False)
    reports["lead_time_cancellation_report"] = _group_report(df, "lead_time_category")
    reports["deposit_type_report"] = _group_report(df, "deposit_type")
    reports["season_hotel_report"] = _group_report(df, ["hotel", "season"])
    reports["guest_group_report"] = _group_report(df, "guest_group")

    # Data-quality documentation reports
    reports["missing_value_report"] = meta["missing_report"]
    reports["outlier_report"] = meta["outlier_report"]
    reports["transformation_log"] = meta["transformation_log"]

    logger.info("%d reports generated", len(reports))
    return reports


COLUMN_DESCRIPTIONS = {
    "booking_id": "Unique id given by the pipeline",
    "hotel": "resort hotel or city hotel",
    "is_cancelled": "1 = booking was cancelled, 0 = not cancelled (target variable)",
    "arrival_date": "Arrival date (built from year, month, day)",
    "arrival_year": "Year of arrival",
    "arrival_month": "Month of arrival (1-12)",
    "arrival_month_name": "Month name of arrival",
    "arrival_year_month": "Arrival period as YYYY-MM",
    "season": "Season of arrival (northern hemisphere)",
    "lead_time": "Days between booking and arrival (capped)",
    "arrival_week": "ISO week number of arrival",
    "arrival_day": "Day of month of arrival",
    "weekend_nights": "Saturday/Sunday nights stayed (capped)",
    "week_nights": "Monday-Friday nights stayed (capped)",
    "adults": "Number of adults (capped)",
    "children": "Number of children (missing filled with 0)",
    "babies": "Number of babies (capped)",
    "meal": "Meal package: sc/bb/hb/fb",
    "country": "Guest country (ISO code, UNK = unknown)",
    "market_segment": "Market segment of the booking",
    "distribution_channel": "Booking distribution channel",
    "is_repeat_guest": "1 = returning guest",
    "previous_cancellations": "Earlier cancelled bookings by the guest",
    "previous_bookings_kept": "Earlier bookings not cancelled by the guest",
    "reserved_room_type": "Room type reserved (coded)",
    "assigned_room_type": "Room type assigned at check-in (coded)",
    "booking_changes": "Number of changes made to the booking (capped)",
    "deposit_type": "no deposit / refundable / non refund",
    "agent": "Travel agent id (0 = no agent)",
    "waiting_days": "Days on waiting list before confirmation (capped)",
    "customer_type": "contract / group / transient / transient-party",
    "avg_daily_rate": "Average price per night (capped, no negatives)",
    "parking_spaces": "Car parking spaces required",
    "special_requests": "Number of special requests",
    "reservation_status": "Final status (WARNING: leaks the target is_cancelled)",
    "reservation_status_date": "Date the final status was set (leaks the target)",
    "has_company": "1 = booked through a company (replaces dropped 'company')",
    "has_agent": "1 = booked through a travel agent",
    "total_nights": "weekend_nights + week_nights",
    "total_guests": "adults + children + babies",
    "estimated_revenue": "avg_daily_rate x total_nights",
    "realized_revenue": "estimated_revenue for kept bookings, 0 if cancelled",
    "lead_time_category": "Binned lead time",
    "stay_length_category": "Binned stay length",
    "guest_group": "solo / couple / family / group",
    "room_changed": "1 = assigned room differs from reserved room",
}


def make_charts(df, reports):
    """Save four quick visual checks of the cleaned data."""
    # 1. Bookings per month by hotel
    pivot = df.groupby(["arrival_year_month", "hotel"]).size().unstack(fill_value=0)
    ax = pivot.plot(figsize=(11, 4.5), marker="o")
    ax.set_title("Monthly bookings by hotel")
    ax.set_xlabel("Arrival month")
    ax.set_ylabel("Bookings")
    plt.xticks(rotation=70)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "monthly_bookings_by_hotel.png"), dpi=130)
    plt.close()

    # 2. Cancellation rate by lead time
    lt = reports["lead_time_cancellation_report"]
    plt.figure(figsize=(7, 4.5))
    plt.bar(lt["lead_time_category"].astype(str), lt["cancellation_rate_pct"],
            color="#3b6ea5")
    plt.title("Cancellation rate by lead time")
    plt.xlabel("Lead time")
    plt.ylabel("Cancellation rate (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "cancellation_by_lead_time.png"), dpi=130)
    plt.close()

    # 3. Average daily rate by arrival month and hotel
    adr = df.groupby(["arrival_month", "hotel"])["avg_daily_rate"].mean().unstack()
    ax = adr.plot(figsize=(8, 4.5), marker="o")
    ax.set_title("Average daily rate by arrival month")
    ax.set_xlabel("Month (1-12)")
    ax.set_ylabel("Average daily rate")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "avg_rate_by_month.png"), dpi=130)
    plt.close()

    # 4. Market segment: bookings and cancellation rate
    ms = reports["market_segment_report"].sort_values("total_bookings")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    axes[0].barh(ms["market_segment"], ms["total_bookings"], color="#3b6ea5")
    axes[0].set_title("Bookings")
    axes[1].barh(ms["market_segment"], ms["cancellation_rate_pct"], color="#c8553d")
    axes[1].set_title("Cancellation rate (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "market_segment_overview.png"), dpi=130)
    plt.close()
    logger.info("4 charts saved to %s", CHART_DIR)


def load(df, reports):
    """Save the analysis-ready dataset, every report and the charts."""
    logger.info("=" * 70)
    logger.info("STEP 4: LOAD")
    logger.info("=" * 70)
    for folder in (REPORT_DIR, OUTPUT_DIR, CHART_DIR):
        os.makedirs(folder, exist_ok=True)

    clean_path = os.path.join(OUTPUT_DIR, "analysis_ready_hotel_bookings.csv")
    df.to_csv(clean_path, index=False)
    logger.info("Saved %s (%s rows x %d columns)", clean_path, f"{len(df):,}", df.shape[1])

    for name, report in reports.items():
        path = os.path.join(REPORT_DIR, f"{name}.csv")
        report.to_csv(path, index=False)
        logger.info("Saved report: reports/%s.csv (%d rows)", name, len(report))

    dictionary = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(t) for t in df.dtypes],
        "unique_values": [df[c].nunique() for c in df.columns],
        "description": [COLUMN_DESCRIPTIONS.get(c, "") for c in df.columns],
    })
    dictionary.to_csv(os.path.join(OUTPUT_DIR, "data_dictionary.csv"), index=False)
    logger.info("Saved output/data_dictionary.csv")

    make_charts(df, reports)
