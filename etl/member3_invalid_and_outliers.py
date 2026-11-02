"""MEMBER 3 - Invalid values and outliers.

Remove zero-guest, zero-night and negative-price rows, detect outliers (IQR), cap them.
"""

import numpy as np
import pandas as pd

from etl.common import CAP_RULES, OUTLIER_COLS, _log


def _iqr_bounds(series, k=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1, q3, iqr, q1 - k * iqr, q3 + k * iqr


def member3_invalid_and_outliers(df, log, meta):
    """MEMBER 3: remove impossible records, detect and treat outliers."""
    m = "Member 3"

    # 3.1 Bookings with zero guests
    before = len(df)
    guests = df["adults"] + df["children"] + df["babies"]
    df = df[guests > 0].copy()
    _log(log, m, "Remove bookings with zero guests",
         "A booking for nobody is a data-entry error and breaks per-guest "
         "metrics.",
         before, len(df), f"{before - len(df):,} rows removed")

    # 3.2 Zero-night stays
    before = len(df)
    df = df[(df["weekend_nights"] + df["week_nights"]) > 0].copy()
    _log(log, m, "Remove stays of zero nights",
         "A stay with no nights has no revenue and no duration - invalid for "
         "length-of-stay and revenue analysis.",
         before, len(df), f"{before - len(df):,} rows removed")

    # 3.3 Negative price
    before = len(df)
    df = df[df["avg_daily_rate"] >= 0].copy()
    _log(log, m, "Remove negative average daily rate",
         "A room price cannot be negative. (A rate of exactly 0 is kept - "
         "these are genuine complimentary stays.)",
         before, len(df), f"{before - len(df):,} rows removed")
    df = df.reset_index(drop=True)

    # 3.4 Outlier detection (IQR rule) on the remaining valid rows
    rows = []
    for c in OUTLIER_COLS:
        q1, q3, iqr, lo, hi = _iqr_bounds(df[c])
        n_out = int(((df[c] < lo) | (df[c] > hi)).sum())
        rows.append({
            "column": c, "q1": round(q1, 2), "q3": round(q3, 2),
            "iqr": round(iqr, 2), "lower_fence": round(lo, 2),
            "upper_fence": round(hi, 2), "outliers_iqr_1_5": n_out,
            "outlier_pct": round(100 * n_out / len(df), 2),
            "min_before": df[c].min(), "max_before": df[c].max(),
        })
    outliers = pd.DataFrame(rows)
    _log(log, m, "Detect outliers with the IQR rule (1.5 x IQR fences)",
         "Extreme values (e.g. a 5,400 room rate, 55 adults) distort means "
         "and hurt ML models; we first measure how many there are.",
         len(df), len(df), f"{int(outliers.outliers_iqr_1_5.sum()):,} flagged values "
                           f"in {len(OUTLIER_COLS)} columns")

    # 3.5 Treat outliers by capping (winsorising) - rows are kept
    treat = {}
    for c, (method, p) in CAP_RULES.items():
        s = df[c]
        if method == "iqr":
            _, _, _, _, cap = _iqr_bounds(s, k=p)
        else:
            cap = s.quantile(p / 100.0)
        cap = int(np.floor(cap)) if pd.api.types.is_integer_dtype(s) else round(float(cap), 2)
        n_capped = int((s > cap).sum())
        df[c] = s.clip(upper=cap)
        treat[c] = (f"capped at {'Q3+%gxIQR' % p if method == 'iqr' else 'P%g' % p}",
                    cap, n_capped)
    outliers["treatment"] = outliers["column"].map(
        lambda c: treat[c][0] if c in treat else "kept (genuine values)")
    outliers["cap_value"] = outliers["column"].map(
        lambda c: treat[c][1] if c in treat else "")
    outliers["values_capped"] = outliers["column"].map(
        lambda c: treat[c][2] if c in treat else 0)
    outliers["max_after"] = outliers["column"].map(lambda c: df[c].max())
    meta["outlier_report"] = outliers
    total_capped = sum(v[2] for v in treat.values())
    _log(log, m, "Cap extreme outliers (winsorise) instead of deleting rows",
         "Capping keeps the booking but removes the distortion. Skewed "
         "count columns use percentile caps because their IQR is 0.",
         len(df), len(df), f"{total_capped:,} values capped in {len(treat)} columns")
    return df
