"""MEMBER 2 - Missing-value handling."""

import pandas as pd  # noqa: F401

from etl.common import _log, logger  # noqa: F401


def member2_missing_values(df, log, meta):
    """
    TODO (Member 2):
      1. Audit missing values (NaN + hidden 'undefined' text)
      2. Replace 'undefined' in meal, market_segment, distribution_channel
      3. Drop company, keep has_company flag
      4. Fill agent with 0, add has_agent flag
      5. Fill children with 0, fill country with 'UNK'
    Store the audit table in meta['missing_report']. Return the DataFrame.
    """
    raise NotImplementedError("member2_missing_values is not written yet")
