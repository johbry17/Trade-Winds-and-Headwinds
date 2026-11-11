"""
src/cleaning.py
Reusable cleaning functions for each data source.
Inputs:  raw file paths
Outputs: clean DataFrames with standardised columns, correct dtypes, and
         documented transformations.  Raw files are never modified.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------
RAW = Path("data/raw")
INTERIM = Path("data/interim")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_commas(s: pd.Series) -> pd.Series:
    """Remove thousands-separator commas from a string Series."""
    return s.astype(str).str.replace(",", "", regex=False)


def _parse_census_flag(flag: str) -> str | None:
    """Return human-readable description for Census suppression flags."""
    mapping = {
        "D": "withheld to avoid disclosing data for individual companies",
        "S": "withheld because estimate did not meet publication standards",
        "X": "not applicable",
        "N": "not available",
        "Z": "less than half unit shown",
        "G": "low relative standard error (< 25%)",
        "H": "high relative standard error (25–50%)",
        "a": "0–19 employees",
        "b": "20–99 employees",
        "c": "100–249 employees",
        "e": "250–499 employees",
        "f": "500–999 employees",
        "g": "1,000–2,499 employees",
        "h": "2,500–4,999 employees",
        "i": "5,000–9,999 employees",
        "j": "10,000–24,999 employees",
        "k": "25,000–49,999 employees",
        "l": "50,000–99,999 employees",
        "m": "100,000+ employees",
    }
    return mapping.get(flag, flag)


# ---------------------------------------------------------------------------
# NPS
# ---------------------------------------------------------------------------

def load_nps_annual(park_code: str) -> pd.DataFrame:
    """
    Load NPS annual recreation-visitation CSV.

    Parameters
    ----------
    park_code : str
        "VIIS" or "BUIS"

    Returns
    -------
    DataFrame with columns: year (int), recreation_visitors (Int64), park (str)
    Rows with non-numeric years or visitor counts are dropped with a warning.
    """
    patterns = {
        "VIIS": "VIIS Annual Park Recreation Visitation*.csv",
        "BUIS": "BUIS Annual Park Recreation Visitation*.csv",
    }
    files = list(RAW.glob(patterns[park_code]))
    if not files:
        raise FileNotFoundError(f"No annual file found for {park_code}")
    path = files[0]

    raw = pd.read_csv(path, skiprows=2, thousands=",")
    raw.columns = raw.columns.str.strip()

    # Keep only Year and RecreationVisitors
    df = raw[["Year", "RecreationVisitors"]].copy()
    df.columns = ["year", "recreation_visitors"]
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["recreation_visitors"] = pd.to_numeric(
        _strip_commas(df["recreation_visitors"]), errors="coerce"
    )
    n_before = len(df)
    df = df.dropna(subset=["year", "recreation_visitors"])
    n_dropped = n_before - len(df)
    if n_dropped:
        warnings.warn(f"{park_code} annual: dropped {n_dropped} non-numeric rows")

    df["year"] = df["year"].astype(int)
    df["recreation_visitors"] = df["recreation_visitors"].astype("Int64")
    df["park"] = park_code
    # 2026 VIIS data is anomalous (Jan–Jun show ~3× normal counts); exclude entirely
    df = df[df["year"] <= 2025]
    return df.sort_values("year").reset_index(drop=True)


def load_nps_monthly(park_code: str) -> pd.DataFrame:
    """
    Load NPS monthly recreation-visitation CSV.

    Returns
    -------
    Long-format DataFrame: date (Period[M]), year (int), month (int),
    recreation_visitors (Int64), park (str).
    The partial-year running-total column (Textbox5) is excluded.
    """
    patterns = {
        "VIIS": "VIIS Recreation Visitors By Month*.csv",
        "BUIS": "BUIS Recreation Visitors By Month*.csv",
    }
    files = list(RAW.glob(patterns[park_code]))
    if not files:
        raise FileNotFoundError(f"No monthly file found for {park_code}")
    path = files[0]

    raw = pd.read_csv(path, skiprows=2, thousands=",")
    raw.columns = raw.columns.str.strip()

    month_cols = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                  "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    existing = [c for c in month_cols if c in raw.columns]
    keep = ["Year"] + existing
    df = raw[keep].copy()
    df.columns = ["year"] + [c.lower() for c in existing]
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    # Melt to long format
    long = df.melt(id_vars="year", var_name="month_abbr", value_name="recreation_visitors")
    month_map = {m.lower(): i + 1 for i, m in enumerate(
        ["jan", "feb", "mar", "apr", "may", "jun",
         "jul", "aug", "sep", "oct", "nov", "dec"]
    )}
    long["month"] = long["month_abbr"].map(month_map)
    long["recreation_visitors"] = pd.to_numeric(
        _strip_commas(long["recreation_visitors"].astype(str)), errors="coerce"
    ).astype("Int64")

    long["date"] = pd.to_datetime(
        long["year"].astype(str) + "-" + long["month"].astype(str).str.zfill(2) + "-01"
    ).dt.to_period("M")

    long["park"] = park_code
    long = long.dropna(subset=["month"])
    long["month"] = long["month"].astype(int)
    # 2026 VIIS data is anomalous (Jan–Jun show ~3× normal counts); exclude entirely
    long = long[long["year"] <= 2025]
    return (
        long[["date", "year", "month", "recreation_visitors", "park"]]
        .sort_values(["year", "month"])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# FRED employment
# ---------------------------------------------------------------------------

def load_fred_employment() -> pd.DataFrame:
    """
    Load both FRED USVI Leisure & Hospitality employment series.

    Values are in thousands of persons.  Returns a wide DataFrame with
    columns: date (Period[M]), year (int), month (int),
    emp_sa (seasonally adjusted, thousands),
    emp_nsa (not seasonally adjusted, thousands).
    """
    sa = pd.read_csv(RAW / "fred_SMS78000007000000001.csv", parse_dates=["observation_date"])
    nsa = pd.read_csv(RAW / "fred_SMU78000007000000001.csv", parse_dates=["observation_date"])
    sa = sa.rename(columns={"observation_date": "date", "SMS78000007000000001": "emp_sa"})
    nsa = nsa.rename(columns={"observation_date": "date", "SMU78000007000000001": "emp_nsa"})

    df = sa.merge(nsa, on="date", how="outer").sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["date"] = df["date"].dt.to_period("M")
    return df[["date", "year", "month", "emp_sa", "emp_nsa"]]


# ---------------------------------------------------------------------------
# World Bank
# ---------------------------------------------------------------------------

def load_worldbank(indicator: str) -> pd.DataFrame:
    """
    Load a World Bank USVI indicator JSON (single-page export).

    Parameters
    ----------
    indicator : str
        "arrivals" (VIR.ST.INT.ARVL) or "receipts" (VIR.ST.INT.RCPT.CD)

    Returns
    -------
    DataFrame with columns: year (int), value (float), indicator (str).
    Null-valued rows are retained with NaN; caller decides on dropping.
    Data quality flag included for known anomalies.
    """
    fname = {
        "arrivals": "VIR.ST.INT.ARVL.json",
        "receipts": "VIR.ST.INT.RCPT.CD.json",
    }[indicator]

    with open(RAW / fname) as f:
        payload = json.load(f)

    records = payload[1]
    df = pd.DataFrame([
        {"year": int(r["date"]), "value": r["value"], "indicator": indicator}
        for r in records
    ])
    df = df.sort_values("year").reset_index(drop=True)

    # Flag known anomalies
    if indicator == "arrivals":
        # 2020 value of 8,612,000 is physically impossible (COVID year, ~2M normal range)
        # Retained as NaN until source is verified; do not use for analysis.
        anomalous = df["value"] > 5_000_000
        if anomalous.any():
            df.loc[anomalous, "dq_flag"] = "anomalous_value"
            df.loc[anomalous, "value"] = np.nan
            warnings.warn(
                "World Bank arrivals: 1 anomalous value (>5M) set to NaN. "
                "Verify source before use."
            )
    return df


# ---------------------------------------------------------------------------
# USVIBER Tourism Indicators (hand-parsed from PDF)
# ---------------------------------------------------------------------------

def load_usviber_tour24() -> pd.DataFrame:
    """
    USVIBER Annual Tourism Indicators from TOUR24.pdf (2-page table).

    Coverage: 2000 and 2010–2024 (gaps in 2001–2009).
    Use load_usviber_combined() to merge with TOUR10 historical data.

    Units
    -----
    Visitor counts        : thousands
    Expenditures          : millions of current USD (nominal)
    Room counts           : units
    Occupancy             : percent (rate, not index)
    Employment            : number of jobs

    Data Quality Notes
    ------------------
    - air_excursionists 2020 = 216.7k: arithmetic reconciles with totals, but
      this value represents 61.6% of 2020 air arrivals as same-day, which is
      implausible for a COVID year. Flag retained; exclude from per-visitor
      expenditure calculations for 2020.
    - air_visitors 2000: air_visitors (604.5) − air_excursionists (216.7) = 387.8k
      implied tourists by air, while total tourists = 546.7k. The difference
      (~159k) would imply tourists arriving by non-air means (ferry, yacht).
      The source does not define air_visitors as the strict sum of tourists-by-air
      + air_excursionists; this identity is not established.
    - Expenditure sub-categories: excursionist_expenditures = air_excursionist_expenditures
      + cruise_expenditures should hold; check validate_usviber_arithmetic().
    - Source publication: USVIBER Annual Tourism Indicator 2024 (TOUR24.pdf).
    """
    years = [2000, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
             2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

    data = {
        # ---- Visitor arrivals (thousands) ----
        "total_visitors":        [2516.9, 2697.7, 2688.4, 2646.3, 2716.5, 2830.4,
                                   2653.3, 2584.5, 1965.1, 1923.3, 2086.9,  792.8,
                                   1053.7, 1793.7, 2349.9, 2507.1],
        "tourists":              [ 546.7,  576.2,  566.9,  619.2,  590.3,  614.8,
                                    641.9,  667.9,  535.0,  380.9,  418.0,  135.6,
                                    396.2,  402.6,  378.0,  380.3],
        "excursionists":         [1970.2, 2121.5, 2121.5, 2027.2, 2126.2, 2215.6,
                                  2011.4, 1916.7, 1430.1, 1542.5, 1668.9,  657.1,
                                   657.5, 1391.2, 1971.9, 2126.8],
        # NOTE: 2020 value = 216.7k is flagged (see air_excursionists_dq_flag)
        "air_excursionists":     [ 216.7,  112.9,  112.5,  122.7,  127.6,  131.7,
                                    132.6,  139.9,  112.9,  111.8,  235.8,  216.7,
                                    422.0,  388.1,  402.6,  527.1],
        "cruise_passengers":     [1768.4, 1858.9, 2009.0, 1904.5, 1998.6, 2083.9,
                                  1878.8, 1776.7, 1317.2, 1430.7, 1433.1,  440.4,
                                   235.5, 1003.1, 1569.3, 1599.8],
        # air_visitors = tourists-by-air + air_excursionists (not identical to
        # total tourists; some tourists may arrive by non-air transport)
        "air_visitors":          [ 604.5,  679.4,  679.4,  741.9,  717.9,  746.5,
                                    774.4,  807.8,  647.8,  492.6,  653.7,  352.4,
                                    818.2,  790.7,  780.7,  884.2],
        "cruise_ships":          [1014,    680,    698,    667,    626,    655,
                                   609,    569,    427,    481,    529,    163,
                                   140,    414,    495,    533],
        # ---- Visitor expenditures (millions of current USD, nominal) ----
        "expenditures_total":    [1186.1, 1568.7, 1642.4, 1732.6, 1742.5, 1853.1,
                                  1826.8, 1872.9, 1491.2, 1263.2, 1453.5,  508.3,
                                  1063.8, 1442.7, 1686.7, 1828.5],
        "expenditures_tourists": [ 714.7,  962.5,  972.5, 1085.1, 1051.8, 1114.1,
                                   1162.0, 1223.9,  997.7,  722.0,  835.9,  268.1,
                                    819.1,  884.3,  862.5,  893.7],
        "expenditures_excursionists": [471.4, 606.1, 669.9, 647.5, 690.7, 739.0,
                                       664.8, 649.0, 493.5, 541.2, 617.6, 240.2,
                                       244.7, 558.4, 824.2, 934.8],
        # Day-trip-by-air excursionist expenditures (from TOUR24 "Day-trip by air")
        "expenditures_air_excursionists": [ 17.4,   31.9,   32.8,   36.6,   39.0,   41.1,
                                             41.3,   44.0,   35.9,   34.1,   79.2,   75.8,
                                            152.1,  148.9,  157.7,  212.7],
        # Cruise passenger expenditures (from TOUR24 "Cruise passengers" expenditure row)
        "expenditures_cruise_passengers": [454.0, 574.2, 637.1, 611.0, 651.7, 697.8,
                                           623.6, 605.0, 457.6, 507.2, 538.5, 164.4,
                                            92.6, 409.5, 666.4, 722.0],
        # ---- Accommodations ----
        "total_rooms":           [5008, 5008, 4889, 5030, 5016, 4974,
                                  5060, 4842, 4886, 3255, 3513, 3291,
                                  2994, 3229, 3400, 3735],
        "hotel_count":           [  49,   47,   47,   46,   44,   44,
                                    41,   42,   41,   33,   34,   23,
                                    22,   23,   23,   24],
        "hotel_rooms":           [3947, 3878, 3759, 3874, 3897, 3856,
                                  3903, 3819, 3820, 2854, 3050, 2554,
                                  2367, 2649, 2788, 3127],
        "condo_units":           [1061, 1131, 1130, 1157, 1120, 1118,
                                  1157, 1023, 1065,  401,  463,  736,
                                   627,  580,  612,  607],
        "occupancy_rate_pct":    [57.7, 57.1, 51.6, 50.9, 53.8, 53.8,
                                  57.1, 56.7, 43.9, 31.3, 39.7, 37.0,
                                  62.4, 63.9, 58.7, 66.3],
        # ---- Employment (number of jobs; N/A for 2023-2024) ----
        "emp_tourism_total":     [None, 8301, 8469, 8339, 8136, 8171,
                                  8159, 8430, 7332, 5093, 6138, 5315,
                                  6221, 6819, None, None],
        "emp_hotels":            [None, 3587, 3549, 3617, 3519, 3575,
                                  3629, 3617, 3329, 1559, 1784, 1664,
                                  2131, 2448, None, None],
        "emp_eating_drinking":   [None, 2793, 2959, 2821, 2784, 2809,
                                  2765, 3170, 2765, 2420, 3039, 2667,
                                  3009, 3075, None, None],
    }

    df = pd.DataFrame(data, index=years)
    df.index.name = "year"
    df = df.reset_index()
    df["source_publication"] = "TOUR24"

    # Flag the suspicious 2020 air_excursionists value
    df.loc[df["year"] == 2020, "air_excursionists_dq_flag"] = (
        "2020 value (216.7k) = 61.6% of air arrivals as same-day; "
        "implausible for COVID year; arithmetic reconciles but value is suspect"
    )

    return df


def load_usviber_tour10() -> pd.DataFrame:
    """
    USVIBER Annual Tourism Indicators from TOUR10.pdf (2-page table).

    Coverage: 1980, 1990, 2000–2010.
    For analysis purposes, use years 2001–2009 as the historical gap-fill;
    use TOUR24 for 2000 and 2010 (revisions documented below).

    Units: same as load_usviber_tour24().

    REVISION WARNING
    ----------------
    TOUR10 and TOUR24 show material differences for the two overlapping years:

    Year 2000 (TOUR10 → TOUR24):
      total_visitors:   2,395.8 → 2,516.9  (+121.1k)
      tourists:           545.9 →   546.7  (+0.8k,  stable)
      air_excursionists:   81.5 →   216.7  (+135.2k, large upward revision)
      cruise_passengers:1,768.4 → 1,768.4  (unchanged)
      expenditures_total:1,205.9→ 1,186.1  (−19.8M)

    Year 2010 (TOUR10 → TOUR24):
      total_visitors:   2,550.5 → 2,697.7  (+147.2k)
      tourists:           589.8 →   576.2  (−13.6k)
      air_excursionists:  101.8 →   112.9  (+11.1k)
      cruise_passengers:1,858.9 → 1,858.9  (unchanged)

    Pattern: cruise_passengers, hotel_rooms, total_rooms, occupancy_rate_pct
    are consistent across publications. Tourist/excursionist totals and air
    excursionist counts were revised, likely reflecting a methodological change
    in how same-day air arrivals are classified. The reason is not established
    in the available source materials.

    Use TOUR24 values for 2000 and 2010. Use TOUR10 values for 2001–2009
    with discontinuity flags at the 2000/2001 and 2009/2010 boundaries.
    Accommodation series (hotel_rooms, total_rooms, occupancy_rate_pct) is
    consistent and may be used without the same discontinuity caveat.

    Source: USVIBER Annual Tourism Indicators 2010 (TOUR10.pdf).
    """
    # Columns: 1980, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010
    # Only 2001-2009 are gap-fill years; 1980, 1990, 2000, 2010 are for reference.
    years_all = [1980, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010]

    data = {
        "total_visitors":        [1217.4, 1811.5, 2395.8, 2497.4, 2336.6, 2392.6,
                                   2619.7, 2601.9, 2570.7, 2606.2, 2435.2, 2246.5, 2550.5],
        "tourists":              [ 380.0,  462.5,  545.9,  527.2,  520.2,  537.9,
                                    566.8,  593.8,  570.6,  587.1,  574.2,  562.6,  589.8],
        "excursionists":         [ 837.4, 1349.0, 1849.9, 1970.2, 1816.4, 1854.4,
                                  2052.9, 2008.1, 2000.1, 2019.1, 1861.0, 1683.9, 1960.7],
        "air_excursionists":     [ 145.9,  229.4,   81.5,   78.8,   77.7,   82.9,
                                    88.2,   95.6,   96.6,  101.2,  104.0,  101.6,  101.8],
        "cruise_passengers":     [ 691.5, 1119.6, 1768.4, 1891.4, 1738.7, 1773.9,
                                  1964.7, 1912.5, 1903.5, 1917.9, 1757.1, 1582.3, 1858.9],
        "air_visitors":          [ 525.9,  691.9,  627.8,  606.0,  598.0,  620.8,
                                    655.0,  689.4,  667.2,  688.3,  678.1,  664.2,  691.6],
        "cruise_ships":          [ 883,   1142,   1014,    976,    845,    888,
                                   924,    818,    782,    752,    687,    621,    680],
        # Expenditures: 2010 is missing from TOUR10; some 2008 tourist values missing
        "expenditures_total":    [293.5,  697.0, 1205.9, 1234.1, 1195.4, 1256.5,
                                  1356.0, 1431.6, 1467.6, 1512.6, 1157.1, 1021.3, None],
        "expenditures_tourists": [221.9,  498.8,  725.9,  722.1,  723.5,  765.4,
                                   789.8,  863.8,  883.2,  929.8,   None,  687.4,  None],
        "expenditures_excursionists": [71.6, 198.2, 480.0, 512.0, 471.9, 491.1,
                                       566.3, 567.8, 584.3, 582.9, 470.7, 333.9, None],
        "expenditures_air_excursionists": [13.5, 30.6, 18.2, 18.6, 18.5, 20.3,
                                           27.6, 27.2, 25.6, 27.7, 29.7, 28.6, None],
        "expenditures_cruise_passengers": [58.1, 167.6, 461.8, 493.4, 453.4, 470.8,
                                           538.6, 540.6, 558.8, 555.2, 441.0, 305.3, None],
        # Accommodation (consistent with TOUR24 for overlapping years)
        "total_rooms":           [5102, 4520, 5008, 5053, 5138, 5045,
                                  4959, 4761, 4812, 4757, 4857, 4948, 5008],
        "hotel_count":           [  65,   60,   49,   48,   47,   46,
                                    48,   47,   47,   46,   47,   46,   47],
        "hotel_rooms":           [3457, 3487, 3947, 3987, 4036, 3985,
                                  3906, 3687, 3739, 3678, 3782, 3809, 3878],
        "condo_units":           [1645, 1033, 1061, 1066, 1102, 1059,
                                  1053, 1075, 1073, 1079, 1075, 1139, 1131],
        "occupancy_rate_pct":    [64.2, 62.5, 57.7, 56.2, 56.6, 57.2,
                                  61.3, 63.8, 60.1, 64.4, 60.0, 54.8, 57.1],
        # Employment
        "emp_tourism_total":     [7200, 8640, 8660, 9020, 8910, 8379,
                                  8723, 8695, 8593, 8778, 8683, 8038, 8316],
    }

    df = pd.DataFrame(data, index=years_all)
    df.index.name = "year"
    df = df.reset_index()
    df["source_publication"] = "TOUR10"
    return df


def load_usviber_combined() -> pd.DataFrame:
    """
    Combine TOUR10 (2001–2009 gap-fill) and TOUR24 (2000, 2010–2024).

    Returns a single DataFrame covering 2000–2024 with a source_publication
    column identifying each row's origin. The accommodation series (hotel_rooms,
    total_rooms, occupancy_rate_pct) is consistent across publications and is
    merged seamlessly. The tourist/excursionist series carries a discontinuity
    flag at the 2010 boundary due to revisions between publications.

    See load_usviber_tour10() for a full description of the revision pattern.
    Rows with year < 2000 from TOUR10 are excluded from the combined series.
    """
    t24 = load_usviber_tour24()
    t10 = load_usviber_tour10()

    # Gap-fill years: 2001-2009 from TOUR10 only
    t10_gap = t10[t10["year"].between(2001, 2009)].copy()
    t10_gap["visitor_series_discontinuity"] = (
        "TOUR10 vintage; material revisions documented at 2000/2001 and 2009/2010 "
        "boundaries for tourist and air_excursionist counts"
    )

    combined = (
        pd.concat([t10_gap, t24], ignore_index=True)
        .sort_values("year")
        .reset_index(drop=True)
    )
    return combined


# ---------------------------------------------------------------------------
# Census Economic Census
# ---------------------------------------------------------------------------

def load_census_2007() -> pd.DataFrame:
    """
    Load 2007 Economic Census A01 table (NAICS 2-digit summary).
    Also contains 2002 comparison data from the same file.
    Returns both years in a long-format DataFrame.

    The CSV has two header-like rows: row 0 is the machine codes,
    row 1 is the verbose label descriptions.  We use row 0 as the header.
    """
    path = RAW / "2007_IA0700A01_U.S. Virgin Islands" / "ECN_2007_IA_00A01_with_ann.csv"
    # Row 0 = column codes; row 1 = verbose labels (skip it); row 2+ = data
    raw = pd.read_csv(path, encoding="latin-1", header=0, skiprows=[1])
    raw.columns = raw.columns.str.strip()

    def _clean_num(s):
        return pd.to_numeric(
            s.astype(str).str.replace(",", "", regex=False), errors="coerce"
        )

    df = raw.rename(columns={
        "NAICS.id": "naics",
        "NAICS.display-label": "naics_label",
        "YEAR.id": "year",
        "ESTAB": "estab",
        "RCPTOT": "rcptot_k",
        "PAYANN": "payann_k",
        "EMP": "emp",
        "RCPTOT_N": "rcptot_noise",
        "PAYANN_N": "payann_noise",
        "EMP_N": "emp_noise",
    }).copy()
    for col in ["estab", "rcptot_k", "payann_k", "emp"]:
        df[col] = _clean_num(df[col])

    df["vintage"] = 2007
    df["table"] = "A01"
    return df[["vintage", "year", "naics", "naics_label",
                "estab", "rcptot_k", "payann_k", "emp",
                "rcptot_noise", "payann_noise", "emp_noise", "table"]]


def _load_dat_usvi(path: Path, year_col: str, naics_col: str,
                   label_col: str, vintage: int, table: str) -> pd.DataFrame:
    """
    Parse a Census pipe-delimited .dat file, filter to USVI territory-level rows.

    USVI data: ST=78.  Files also contain island- and town-level rows (GEOTYPE 3,5).
    We keep only GEOTYPE=2 (territory total) to avoid double-counting.
    If a GEOTYPE column is absent (older format), we fall back to ST=78 only.
    """
    raw = pd.read_csv(path, sep="|", encoding="latin-1", low_memory=False)
    raw.columns = raw.columns.str.lstrip("#").str.strip()

    # Filter to USVI territory-level (GEOTYPE=2)
    if "GEOTYPE" in raw.columns:
        usvi = raw[
            (raw["ST"].astype(str).str.strip() == "78") &
            (raw["GEOTYPE"].astype(str).str.strip() == "2")
        ].copy()
    else:
        usvi = raw[raw["ST"].astype(str).str.strip() == "78"].copy()

    def _n(s):
        return pd.to_numeric(
            s.astype(str).str.replace(",", "", regex=False), errors="coerce"
        )

    out = pd.DataFrame()
    out["vintage"] = vintage
    out["year"] = _n(usvi[year_col])
    out["naics"] = usvi[naics_col].astype(str).str.strip()
    out["naics_label"] = usvi[label_col].astype(str).str.strip()
    out["estab"] = _n(usvi["ESTAB"])
    out["estab_flag"] = usvi["ESTAB_F"].astype(str).str.strip()
    out["rcptot_k"] = _n(usvi["RCPTOT"])
    out["rcptot_flag"] = usvi["RCPTOT_F"].astype(str).str.strip()
    out["payann_k"] = _n(usvi["PAYANN"])
    out["payann_flag"] = usvi["PAYANN_F"].astype(str).str.strip()
    out["emp"] = _n(usvi["EMP"])
    out["emp_flag"] = usvi["EMP_F"].astype(str).str.strip()
    out["table"] = table
    return out.reset_index(drop=True)


def load_census_2012_basic() -> pd.DataFrame:
    return _load_dat_usvi(
        RAW / "IA1200A02" / "IA1200A02.dat",
        year_col="YEAR", naics_col="NAICS2012", label_col="NAICS2012_TTL",
        vintage=2012, table="A02",
    )


def load_census_2017_basic() -> pd.DataFrame:
    """Contains both 2012 and 2017 year rows."""
    return _load_dat_usvi(
        RAW / "IA1700BASIC02" / "IA1700BASIC02.dat",
        year_col="YEAR", naics_col="NAICS2017", label_col="NAICS2017_TTL",
        vintage=2017, table="BASIC02",
    )


def load_census_2022_basic() -> pd.DataFrame:
    """Contains both 2017 and 2022 year rows."""
    return _load_dat_usvi(
        RAW / "IA2200BASIC02" / "IA2200BASIC02.dat",
        year_col="YEAR", naics_col="NAICS2022", label_col="NAICS2022_LABEL",
        vintage=2022, table="BASIC02",
    )


def load_census_rooms() -> pd.DataFrame:
    """
    Extract guestroom counts across Census vintages.

    NOTE ON METHODOLOGY
    -------------------
    2007 and 2012: guestrooms from A10 industry-total row (RMRTRAN, NAICS 7211).
    2017 and 2022: guestrooms from NAPCS02 product code 7003825000
        "Room or unit accommodation for travelers" — the most specific and
        comparable measure.  The NAPCS Total row RMRTRAN is NOT used because it
        shows inconsistent values (8,735 in 2017 vs 1,958 in 2022) suggesting
        it aggregates across product rows rather than counting unique rooms.

    Returns long-format DataFrame with columns:
        year, census_vintage, naics, rooms, estab, rcptot_k, methodology_note
    """
    records = []

    # 2007 A10 — same skiprows fix as A01 (row 0 = codes, row 1 = verbose labels)
    path07 = (
        RAW / "2007_IA0700A10_U.S. Virgin Islands" / "ECN_2007_IA_00A10_with_ann.csv"
    )
    a10 = pd.read_csv(path07, encoding="latin-1", header=0, skiprows=[1])
    a10.columns = a10.columns.str.strip()
    total_row = a10[a10["PSCODE.id"].astype(str).str.strip() == "20000"]
    if not total_row.empty:
        r = total_row.iloc[0]
        records.append({
            "year": 2007, "census_vintage": 2007,
            "naics": "7211", "naics_label": "Traveler accommodation",
            "rooms": pd.to_numeric(str(r.get("RMRTRAN", "")).replace(",", ""), errors="coerce"),
            "estab": pd.to_numeric(str(r.get("ESTAB", "")).replace(",", ""), errors="coerce"),
            "rcptot_k": pd.to_numeric(str(r.get("RCPTOT", "")).replace(",", ""), errors="coerce"),
            "methodology_note": "A10 industry total (PSCODE 20000)",
        })

    # 2012 A10 — filter to USVI territory total row (PSCODE2012 = 20000)
    path12 = RAW / "IA1200A10" / "IA1200A10.dat"
    a10_12 = pd.read_csv(path12, sep="|", encoding="latin-1", low_memory=False)
    a10_12.columns = a10_12.columns.str.lstrip("#").str.strip()
    usvi_12 = a10_12[
        (a10_12["ST"].astype(str).str.strip() == "78") &
        (a10_12["PSCODE2012"].astype(str).str.strip() == "20000")
    ]
    if not usvi_12.empty:
        r = usvi_12.iloc[0]
        records.append({
            "year": 2012, "census_vintage": 2012,
            "naics": "7211", "naics_label": "Traveler accommodation",
            "rooms": pd.to_numeric(str(r.get("RMRTRAN", "")).replace(",", ""), errors="coerce"),
            "estab": pd.to_numeric(str(r.get("ESTAB", "")).replace(",", ""), errors="coerce"),
            "rcptot_k": pd.to_numeric(str(r.get("RCPTOT", "")).replace(",", ""), errors="coerce"),
            "methodology_note": "A10 industry total (PSCODE2012 = 20000)",
        })

    # 2017 NAPCS02 — use NAPCS 7003825000 (room accommodation)
    path17 = RAW / "IA1700NAPCS02" / "IA1700NAPCS02.dat"
    n17 = pd.read_csv(path17, sep="|", encoding="latin-1", low_memory=False)
    n17.columns = n17.columns.str.lstrip("#").str.strip()
    room_row = n17[
        (n17["GEO_ID"].str.contains("78", na=False)) &
        (n17["NAPCS2017"].astype(str).str.strip() == "7003825000")
    ]
    if not room_row.empty:
        r = room_row.iloc[0]
        records.append({
            "year": 2017, "census_vintage": 2017,
            "naics": "7211", "naics_label": "Traveler accommodation",
            "rooms": pd.to_numeric(str(r.get("RMRTRAN", "")).replace(",", ""), errors="coerce"),
            "estab": pd.to_numeric(str(r.get("ESTAB", "")).replace(",", ""), errors="coerce"),
            "rcptot_k": pd.to_numeric(str(r.get("RCPTOT", "")).replace(",", ""), errors="coerce"),
            "methodology_note": (
                "NAPCS02 product 7003825000 (Room or unit accommodation for travelers). "
                "Guestroom reference date = Dec 31, 2017, post-hurricane."
            ),
        })

    # 2022 NAPCS02 — use NAPCS 7003825000
    path22 = RAW / "IA2200NAPCS02" / "IA2200NAPCS02.dat"
    n22 = pd.read_csv(path22, sep="|", encoding="latin-1", low_memory=False)
    n22.columns = n22.columns.str.lstrip("#").str.strip()
    room_row22 = n22[
        (n22["GEO_ID"].str.contains("78", na=False)) &
        (n22["NAPCS2022"].astype(str).str.strip() == "7003825000")
    ]
    if not room_row22.empty:
        r = room_row22.iloc[0]
        records.append({
            "year": 2022, "census_vintage": 2022,
            "naics": "7211", "naics_label": "Traveler accommodation",
            "rooms": pd.to_numeric(str(r.get("RMRTRAN", "")).replace(",", ""), errors="coerce"),
            "estab": pd.to_numeric(str(r.get("ESTAB", "")).replace(",", ""), errors="coerce"),
            "rcptot_k": pd.to_numeric(str(r.get("RCPTOT", "")).replace(",", ""), errors="coerce"),
            "methodology_note": "NAPCS02 product 7003825000 (Room or unit accommodation for travelers)",
        })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# BEA
# ---------------------------------------------------------------------------

def load_bea(sheet_pattern: str = "2.1") -> pd.DataFrame:
    """
    Load a BEA table from vigdp0624.xlsx.

    Finds the sheet whose name contains sheet_pattern.
    Returns a tidy long-format DataFrame with columns:
        year (int), line (str), label (str), value (float),
        vintage_flag (str: '', 'r'=revised, 'p'=preliminary)
    """
    path = RAW / "vigdp0624.xlsx"
    xl = pd.ExcelFile(path)
    match = [s for s in xl.sheet_names if sheet_pattern in s]
    if not match:
        raise ValueError(f"No sheet matching {sheet_pattern!r}. Available: {xl.sheet_names}")
    sheet = match[0]
    raw = xl.parse(sheet, header=None)

    # Find header row (first row with ≥ 5 year-like values)
    header_idx = None

    def _is_year(v) -> bool:
        try:
            yr = int(float(str(v).replace("r", "").replace("p", "")))
            return 2000 <= yr <= 2035
        except (ValueError, TypeError):
            return False

    for i, row in raw.iterrows():
        if sum(1 for v in row if _is_year(v)) >= 5:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("Could not identify year header row")

    year_row = raw.iloc[header_idx]

    # Parse year columns: extract year int and flag
    year_info = {}
    for col_idx, val in enumerate(year_row):
        sv = str(val).strip()
        flag = ""
        if sv.endswith("r"):
            flag = "r"
            sv = sv[:-1]
        elif sv.endswith("p"):
            flag = "p"
            sv = sv[:-1]
        try:
            yr = int(float(sv))
            if 2000 <= yr <= 2035:
                year_info[col_idx] = (yr, flag)
        except (ValueError, TypeError):
            pass

    # Parse data rows (below header, stop at the next table header)
    records = []
    in_first_table = True
    for i in range(header_idx + 1, len(raw)):
        row = raw.iloc[i]
        line = str(row.iloc[0]) if str(row.iloc[0]) != "nan" else ""
        label = str(row.iloc[1]) if str(row.iloc[1]) != "nan" else ""

        # Detect start of a new table (another header row with year columns)
        if i > header_idx + 1 and sum(1 for v in row if _is_year(v)) >= 5:
            break  # Stop at next table's year header

        # Stop at notes/blank lines
        if not label or label in ("nan", "") or line in ("nan", ""):
            if not any(isinstance(row.iloc[ci], (int, float)) and not pd.isna(row.iloc[ci])
                       for ci in year_info):
                continue

        for col_idx, (yr, flag) in year_info.items():
            val = row.iloc[col_idx]
            try:
                fval = float(val)
            except (TypeError, ValueError):
                fval = np.nan
            if not pd.isna(fval):
                records.append({
                    "year": yr, "line": line.strip(),
                    "label": label.replace("\xa0", " ").strip(),
                    "value": fval, "vintage_flag": flag, "sheet": sheet,
                })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# USVI CPI (from Econ21.pdf — parsed manually)
# ---------------------------------------------------------------------------

def load_usvi_cpi() -> pd.DataFrame:
    """
    USVI Consumer Price Index (2009 = 100) from USVIBER Econ21.pdf.

    Coverage: approximately 2009–2021, annual frequency.
    Source: USVIBER Annual Economic Indicators 2021.

    The PDF text extracted for the CPI row:
      "USVI Consumer Price Index (2009=100) - - 104.0 109.7 115.7 118.5 119.3
       121.7 123.8 130.0 99.8 102.8 109.6 115.8"
    Column headers in the Econ21 table were not perfectly parseable; years
    are inferred from context.  The two leading dashes (--) correspond to years
    before data collection (likely 2007, 2008), then 2009–2021.
    IMPORTANT: Treat 2009 as the base (index = 100.0).
    """
    # Hand-transcribed from PDF (Econ21.pdf, page 2)
    # The first dash value is 2009 base year column (would be 100); these dashes
    # appear to be "not available" for 2007-2008 pre-series start.
    # Based on column alignment in the PDF, assigning 2009=100 as base.
    years = list(range(2009, 2022))
    values = [
        100.0,   # 2009 (base)
        104.0,   # 2010
        109.7,   # 2011
        115.7,   # 2012
        118.5,   # 2013
        119.3,   # 2014
        121.7,   # 2015
        123.8,   # 2016
        130.0,   # 2017
         99.8,   # 2018  ← sharp drop; verify interpretation
        102.8,   # 2019
        109.6,   # 2020
        115.8,   # 2021
    ]
    df = pd.DataFrame({"year": years, "cpi_usvi_2009_100": values})
    df["source"] = "USVIBER Econ21.pdf"
    df["note"] = "Hand-parsed; verify 2018 drop against original PDF table layout"
    return df
