#!/usr/bin/env python3
"""Run the pipeline only up to one member's stage, so each pull request can be tested.

    python check_member.py 1     # extract + Member 1
    python check_member.py 2     # extract + Members 1-2
    python check_member.py 3     # extract + Members 1-3
    python check_member.py 4     # the full pipeline
"""
import sys

from etl.common import logger, setup_logging
from pipeline import extract, run_etl_pipeline


def main(upto):
    if upto == 4:
        run_etl_pipeline()
        return
    setup_logging()
    df, log, meta = extract(), [], {}
    from etl.member1_structural_cleaning import member1_structural_cleaning
    df = member1_structural_cleaning(df.copy(), log)
    if upto >= 2:
        from etl.member2_missing_values import member2_missing_values
        df = member2_missing_values(df, log, meta)
    if upto >= 3:
        from etl.member3_invalid_and_outliers import member3_invalid_and_outliers
        df = member3_invalid_and_outliers(df, log, meta)
    logger.info("CHECK OK after Member %d: %s rows x %d columns, %d null values",
                upto, f"{len(df):,}", df.shape[1], int(df.isna().sum().sum()))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in "1234":
        sys.exit("usage: python check_member.py <1|2|3|4>")
    main(int(sys.argv[1]))
