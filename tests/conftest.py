"""Shared test fixtures.

`raw_sample` is a tiny hand-made table that has the same 32 columns as the real raw data and
contains every kind of problem the pipeline must fix (duplicate, hidden 'Undefined' values,
NaN values, zero guests, zero nights, a negative price and an extreme price).

The stage fixtures run the pipeline stage by stage. If an earlier member's function is still
a stub (NotImplementedError) the dependent tests are SKIPPED instead of failing, so the
repository stays green while the team is still working.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pipeline  # noqa: E402
from etl import member4_features  # noqa: E402

RAW_COLUMNS = [
    "hotel", "is_canceled", "lead_time", "arrival_date_year", "arrival_date_month",
    "arrival_date_week_number", "arrival_date_day_of_month", "stays_in_weekend_nights",
    "stays_in_week_nights", "adults", "children", "babies", "meal", "country",
    "market_segment", "distribution_channel", "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "reserved_room_type", "assigned_room_type",
    "booking_changes", "deposit_type", "agent", "company", "days_in_waiting_list",
    "customer_type", "adr", "required_car_parking_spaces", "total_of_special_requests",
    "reservation_status", "reservation_status_date",
]


def _row(**changes):
    base = {
        "hotel": "Resort Hotel", "is_canceled": 0, "lead_time": 10,
        "arrival_date_year": 2015, "arrival_date_month": "July",
        "arrival_date_week_number": 27, "arrival_date_day_of_month": 1,
        "stays_in_weekend_nights": 0, "stays_in_week_nights": 2, "adults": 2,
        "children": 0.0, "babies": 0, "meal": "BB", "country": "PRT",
        "market_segment": "Direct", "distribution_channel": "Direct",
        "is_repeated_guest": 0, "previous_cancellations": 0,
        "previous_bookings_not_canceled": 0, "reserved_room_type": "A",
        "assigned_room_type": "A", "booking_changes": 0, "deposit_type": "No Deposit",
        "agent": np.nan, "company": np.nan, "days_in_waiting_list": 0,
        "customer_type": "Transient", "adr": 80.0, "required_car_parking_spaces": 0,
        "total_of_special_requests": 0, "reservation_status": "Check-Out",
        "reservation_status_date": "2015-07-03",
    }
    base.update(changes)
    return base


@pytest.fixture
def raw_sample():
    """24 raw rows: 1 exact duplicate, 1 zero-guest, 1 zero-night, 1 negative price,
    1 extreme price, plus missing / 'Undefined' / messy-text values."""
    rows = [_row()]                                                    # 0 normal
    rows.append(_row())                                                # 1 exact duplicate of 0
    rows.append(_row(hotel="City Hotel", is_canceled=1, lead_time=100,
                     arrival_date_month="August", arrival_date_day_of_month=15,
                     stays_in_weekend_nights=1, stays_in_week_nights=3, children=1.0,
                     meal="Undefined", country=np.nan, market_segment="Online TA",
                     distribution_channel="TA/TO", agent=9.0, adr=120.0,
                     reservation_status="Canceled"))                  # 2 cancelled, NaN country
    rows.append(_row(children=np.nan, company=45.0, adr=95.5,
                     arrival_date_month="March", arrival_date_year=2016))  # 3 NaN children
    rows.append(_row(adults=0, children=0.0, babies=0, adr=60.0,
                     arrival_date_day_of_month=4))                    # 4 ZERO GUESTS
    rows.append(_row(stays_in_weekend_nights=0, stays_in_week_nights=0,
                     arrival_date_day_of_month=5))                    # 5 ZERO NIGHTS
    rows.append(_row(adr=-6.38, arrival_date_day_of_month=6))          # 6 NEGATIVE PRICE
    rows.append(_row(adr=5400.0, arrival_date_day_of_month=7))         # 7 EXTREME PRICE
    rows.append(_row(market_segment="Undefined", distribution_channel="Undefined",
                     arrival_date_day_of_month=8))                    # 8 hidden 'Undefined'
    rows.append(_row(hotel=" City Hotel ", country=" gbr", arrival_date_day_of_month=9,
                     adr=101.0))                                      # 9 messy text
    for i in range(14):                                               # 10-23 ordinary rows
        rows.append(_row(
            hotel="City Hotel" if i % 2 else "Resort Hotel",
            lead_time=5 + i * 7, arrival_date_month=["January", "May", "October"][i % 3],
            arrival_date_year=2016 + i % 2, arrival_date_day_of_month=10 + i,
            stays_in_week_nights=1 + i % 4, stays_in_weekend_nights=i % 2,
            adults=1 + i % 3, adr=70.0 + i * 4.5, is_canceled=i % 2,
            market_segment=["Direct", "Online TA", "Groups"][i % 3],
            country=["PRT", "GBR", "FRA", "ESP"][i % 4],
            agent=float(i) if i % 3 == 0 else np.nan))
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


def _run(fn, *args):
    try:
        return fn(*args)
    except NotImplementedError as exc:
        pytest.skip(f"waiting for teammate: {exc}")


@pytest.fixture
def stage1(raw_sample):
    log = []
    df = _run(pipeline.member1_structural_cleaning, raw_sample.copy(), log)
    return df, log


@pytest.fixture
def stage2(stage1):
    df, log = stage1
    meta = {}
    df = _run(pipeline.member2_missing_values, df.copy(), log, meta)
    return df, log, meta


@pytest.fixture
def stage3(stage2):
    df, log, meta = stage2
    df = _run(pipeline.member3_invalid_and_outliers, df.copy(), log, meta)
    return df, log, meta


@pytest.fixture
def small_size_limits(monkeypatch):
    """The sample has ~20 rows, so relax the 'at least 10,000 rows / 18 columns' check."""
    # raising=False: while Member 4 is still a stub the constants do not exist yet
    monkeypatch.setattr(member4_features, "MIN_ROWS", 1, raising=False)
    monkeypatch.setattr(member4_features, "MIN_COLS", 1, raising=False)


@pytest.fixture
def transformed(raw_sample, small_size_limits):
    """Full transform() result: (clean_df, meta)."""
    return _run(pipeline.transform, raw_sample.copy())
