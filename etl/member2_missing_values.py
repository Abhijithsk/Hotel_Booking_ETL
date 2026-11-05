"""MEMBER 2 - Missing-value handling.

Replace 'undefined' placeholders, drop company (keep flag), fill agent, children, country.
"""

import pandas as pd

from etl.common import _log


def member2_missing_values(df, log, meta):
    """MEMBER 2: placeholders, drop / flag / impute missing values."""
    m = "Member 2"
    n = len(df)

    # 2.1 Audit (also count hidden 'undefined' placeholders as missing)
    hidden = {
        "meal": int((df["meal"] == "undefined").sum()),
        "market_segment": int((df["market_segment"] == "undefined").sum()),
        "distribution_channel": int((df["distribution_channel"] == "undefined").sum()),
    }
    audit = []
    for c in df.columns:
        miss = int(df[c].isna().sum()) + hidden.get(c, 0)
        audit.append({"column": c, "missing_before": miss,
                      "missing_pct_before": round(100 * miss / n, 2)})
    audit = pd.DataFrame(audit)
    _log(log, m, "Missing-value audit (NaN + hidden 'undefined' placeholders)",
         "You cannot fix what you have not measured; some missing data is "
         "hidden behind text like 'Undefined'.",
         n, n, f"{int((audit.missing_before > 0).sum())} columns have missing data")

    # 2.2 Replace placeholder text
    df["meal"] = df["meal"].replace("undefined", "sc")          # SC = no meal package
    df["market_segment"] = df["market_segment"].replace("undefined", "unknown")
    df["distribution_channel"] = df["distribution_channel"].replace("undefined", "unknown")
    _log(log, m, "Replace 'undefined' placeholders",
         "Dataset documentation says meal 'Undefined' equals 'SC' (no meal "
         "package); the others become an explicit 'unknown' category.",
         n, n, f"meal={hidden['meal']}, market_segment={hidden['market_segment']}, "
               f"distribution_channel={hidden['distribution_channel']} values fixed")

    # 2.3 company: ~94% missing -> flag then drop
    df["has_company"] = df["company"].notna().astype("int8")
    df = df.drop(columns=["company"])
    _log(log, m, "Drop 'company' column, keep has_company flag",
         "Over 90% empty - imputing would invent data. The useful signal "
         "(booked through a company or not) is kept as a 0/1 flag.",
         n, len(df), "column dropped, flag has_company added")

    # 2.4 agent: missing = booked without an agent
    df["has_agent"] = df["agent"].notna().astype("int8")
    df["agent"] = df["agent"].fillna(0).astype("int32")
    _log(log, m, "Fill missing 'agent' with 0 and add has_agent flag",
         "A missing agent id means the guest booked directly; 0 = no agent.",
         n, len(df), "missing agent -> 0")

    # 2.5 children: only a handful missing -> mode (0)
    df["children"] = df["children"].fillna(0).astype("int16")
    _log(log, m, "Fill missing 'children' with 0 (mode)",
         "Only a few rows are missing and the vast majority of bookings have "
         "no children, so 0 is the safest imputation.",
         n, len(df), "missing children -> 0")

    # 2.6 country: unknown
    df["country"] = df["country"].fillna("UNK")
    _log(log, m, "Fill missing 'country' with 'UNK'",
         "Guessing a country (e.g. the most common) would bias country-wise "
         "analysis; an explicit unknown label is honest.",
         n, len(df), "missing country -> UNK")

    if int(df.isna().sum().sum()) != 0:
        raise ValueError("Missing values remain after Member 2 treatment")

    treatments = {
        "company": "Dropped (>90% missing); has_company flag created",
        "agent": "Filled with 0 (no agent); has_agent flag created",
        "children": "Filled with 0 (mode)",
        "country": "Filled with 'UNK'",
        "meal": "'undefined' replaced with 'sc'",
        "market_segment": "'undefined' replaced with 'unknown'",
        "distribution_channel": "'undefined' replaced with 'unknown'",
    }
    audit["treatment"] = audit["column"].map(treatments).fillna("No action needed")
    audit["missing_after"] = audit["column"].apply(
        lambda c: "column dropped" if c == "company" else 0)
    meta["missing_report"] = audit
    return df
