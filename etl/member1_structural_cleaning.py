"""MEMBER 1 - Structural cleaning."""

import pandas as pd  # noqa: F401

from etl.common import _log, logger  # noqa: F401


def member1_structural_cleaning(df, log):
    """
    TODO (Member 1):
      1. Rename columns using RENAME_MAP (from etl.common)
      2. Remove exact duplicate rows
      3. Standardise text (strip, lower case, country upper case)
      4. Convert dates: build arrival_date, parse reservation_status_date
      5. Fix data types (compact integers)
    Log every step with _log(...). Return the cleaned DataFrame.
    """
    raise NotImplementedError("member1_structural_cleaning is not written yet")
