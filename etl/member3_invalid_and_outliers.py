"""MEMBER 3 - Invalid values and outliers."""

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401

from etl.common import _log, logger  # noqa: F401


def member3_invalid_and_outliers(df, log, meta):
    """
    TODO (Member 3):
      1. Remove zero-guest bookings
      2. Remove zero-night stays
      3. Remove negative avg_daily_rate
      4. Detect outliers with the IQR rule on OUTLIER_COLS
      5. Cap outliers using CAP_RULES (rows are kept)
    Store the outlier table in meta['outlier_report']. Return the DataFrame.
    """
    raise NotImplementedError("member3_invalid_and_outliers is not written yet")
