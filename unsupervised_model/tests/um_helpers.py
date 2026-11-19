"""Helpers shared by the clustering tests (a small fake dataset, no real data needed)."""

import numpy as np
import pandas as pd

from unsupervised_model import common


def make_df(n=1500, seed=0):
    """A fake analysis-ready table with three obvious groups of bookings."""
    rng = np.random.RandomState(seed)
    g = rng.choice(3, n, p=[0.6, 0.25, 0.15])
    lead = np.where(g == 0, 90, np.where(g == 1, 20, 150)) + rng.randint(0, 20, n)
    df = pd.DataFrame({
        "lead_time": lead,
        "total_nights": np.where(g == 1, 2, np.where(g == 2, 6, 3)) + rng.randint(0, 2, n),
        "avg_daily_rate": np.where(g == 2, 160, np.where(g == 1, 70, 105)) + rng.randn(n) * 8,
        "total_guests": np.where(g == 2, 4, 2),
        "children": (g == 2).astype(int),
        "babies": 0,
        "special_requests": rng.randint(0, 3, n),
        "booking_changes": rng.randint(0, 2, n),
        "previous_cancellations": 0,
        "previous_bookings_kept": np.where(g == 1, 3, 0),
        "is_repeat_guest": (g == 1).astype(int),
        "has_agent": (g != 1).astype(int),
        "has_company": (g == 1).astype(int),
        "waiting_days": 0,
        "hotel": rng.choice(["city hotel", "resort hotel"], n),
        # labelled / outcome columns that must be removed before clustering
        "is_cancelled": (rng.rand(n) < 0.3).astype(int),
        "reservation_status": rng.choice(["check-out", "canceled"], n),
        "reservation_status_date": "2016-01-01",
        "realized_revenue": rng.rand(n) * 300,
        "estimated_revenue": rng.rand(n) * 300,
    })
    return df


def redirect_outputs(monkeypatch, tmp_path):
    """Make a test write its results to a temp folder instead of the repository."""
    monkeypatch.setattr(common, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(common, "METRICS_DIR", tmp_path / "metrics")
    monkeypatch.setattr(common, "CHARTS_DIR", tmp_path / "charts")
    monkeypatch.setattr(common, "PROFILES_DIR", tmp_path / "profiles")
