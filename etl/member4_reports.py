"""MEMBER 4 - Reports (generate_reports) and Load (load + charts)."""

import os  # noqa: F401

import pandas as pd  # noqa: F401

from etl.common import CHART_DIR, OUTPUT_DIR, REPORT_DIR, logger  # noqa: F401


def generate_reports(df, meta):
    """
    TODO (Member 4): build every report as a DataFrame and return {file_name: DataFrame}.
    Needs: summary statistics, top10 / bottom10, monthly, hotel-wise, market segment,
    lead-time, deposit, season and guest-group reports, plus meta['missing_report'],
    meta['outlier_report'] and meta['transformation_log'].
    """
    raise NotImplementedError("generate_reports is not written yet")


def load(df, reports):
    """
    TODO (Member 4): save the analysis-ready CSV + every report CSV + data dictionary + charts
    into output/ and reports/.
    """
    raise NotImplementedError("load is not written yet")
