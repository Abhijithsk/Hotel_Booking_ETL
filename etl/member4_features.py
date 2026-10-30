"""MEMBER 4 - Feature engineering and final validation."""

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401

from etl.common import _log, logger  # noqa: F401


def member4_feature_engineering(df, log):
    """
    TODO (Member 4):
      1. total_nights, total_guests, estimated_revenue, realized_revenue
      2. lead_time_category, stay_length_category
      3. season, arrival_year_month, guest_group, room_changed
      4. Sort by arrival_date, add booking_id, reorder columns
      5. Final validation checks (nulls, duplicates, ranges, size)
    Return the final DataFrame.
    """
    raise NotImplementedError("member4_feature_engineering is not written yet")
