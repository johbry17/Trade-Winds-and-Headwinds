"""
src/export_report_data.py
Deterministic export of curated report-ready datasets to data/processed/.

This script imports existing loaders from src/cleaning.py and
src/hotel_extraction.py to generate the CSVs consumed by the R
visualization pipeline.  Raw source files are never modified.
Interim exports (data/interim/) are preserved and not overwritten.

Usage (from project root):
    python src/export_report_data.py

Outputs (data/processed/):
    visitors_annual.csv          USVIBER combined, 2000–2024, with CPI-deflated expenditure
    hotel_annual.csv             USVIBER hotel room-nights and occupancy, 2001–2025
    hotel_island_annual.csv      Island-level hotel stats (STT / STX)
    island_arrivals.csv          Island-level air and cruise arrivals
    employment_fred_annual.csv   FRED L&H annual means, 2000–2025
    employment_usviber.csv    USVIBER tourism-related employment, 2000–2024
    employment_qcew.csv          QCEW NAICS 72 territory-level, 2000–2025
    census_naics72.csv           Census Economic Census snapshots (2007, 2012, 2017, 2022)
    bea_gdp_real.csv             BEA real GDP, 2002–2022
    bea_af_real.csv              BEA real A&F value added, 2002–2021
    bea_af_share.csv             Approximate A&F share of nominal GDP
    census_rooms.csv             Guestroom counts across Census vintages
    nps_viis.csv                 NPS VIIS annual recreation visits
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED = PROJECT_ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

from src.cleaning import (
    load_usviber_combined,
    load_fred_employment,
    load_bea,
    load_nps_annual,
    load_census_rooms,
    load_qcew,
    load_usviber_island_arrivals,
    load_hotel_island,
    load_census_2007,
    load_census_2012_basic,
    load_census_2017_basic,
    load_census_2022_basic,
)
from src.hotel_extraction import build_hotel_annual, load_hotel_annual


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save(df: pd.DataFrame, name: str) -> None:
    path = PROCESSED / name
    df.to_csv(path, index=False)
    print(f"  Saved {name}  ({len(df)} rows, {len(df.columns)} cols)")


def _index_to_base(df: pd.DataFrame, col: str, base_year: int = 2016) -> pd.Series:
    """Return col / col[base_year] * 100 as a new Series."""
    base = df.loc[df["year"].eq(base_year), col]
    if base.empty or pd.isna(base.iloc[0]):
        return pd.Series([pd.NA] * len(df), dtype="Float64")
    return (df[col] / base.iloc[0] * 100).round(2)


# ---------------------------------------------------------------------------
# 1. USVIBER combined — visitors_annual.csv
# ---------------------------------------------------------------------------

def export_visitors():
    df = load_usviber_combined(deflate=True, cpi_base_year=2016)
    keep = [
        "year",
        "air_visitors",
        "cruise_passengers",
        "total_visitors",
        "tourists",
        "hotel_rooms",
        "occupancy_rate_pct",
        "expenditures_total",
        "expenditures_total_real",
        "source_publication",
        "visitor_series_discontinuity",
    ]
    out = df[keep].copy()
    # Annotate CPI base year for downstream use
    out.insert(out.columns.get_loc("expenditures_total_real") + 1,
               "expenditure_cpi_base_year", 2016)
    _save(out, "visitors_annual.csv")
    return out


# ---------------------------------------------------------------------------
# 2. Hotel annual — hotel_annual.csv
# ---------------------------------------------------------------------------

def export_hotel_annual():
    hotel = build_hotel_annual()
    # keep the full output from hotel_extraction.py
    _save(hotel, "hotel_annual.csv")
    return hotel


# ---------------------------------------------------------------------------
# 3. Island-level hotel — hotel_island_annual.csv
# ---------------------------------------------------------------------------

def export_hotel_island():
    df = load_hotel_island()
    _save(df, "hotel_island_annual.csv")
    return df


# ---------------------------------------------------------------------------
# 4. Island arrivals — island_arrivals.csv
# ---------------------------------------------------------------------------

def export_island_arrivals():
    df = load_usviber_island_arrivals()
    _save(df, "island_arrivals.csv")
    return df


# ---------------------------------------------------------------------------
# 5. FRED employment annual means — employment_fred_annual.csv
# ---------------------------------------------------------------------------

def export_fred_employment():
    fred = load_fred_employment()
    ann = (
        fred.groupby("year", as_index=False)[["emp_sa", "emp_nsa"]]
        .mean()
        .rename(columns={"emp_sa": "emp_sa_avg", "emp_nsa": "emp_nsa_avg"})
    )
    ann["emp_sa_avg"] = ann["emp_sa_avg"].round(3)
    ann["emp_nsa_avg"] = ann["emp_nsa_avg"].round(3)
    _save(ann, "employment_fred_annual.csv")
    return ann


# ---------------------------------------------------------------------------
# 6. USVIBER tourism employment — employment_usviber.csv
# ---------------------------------------------------------------------------

def export_usviber_employment():
    """
    Export USVIBER tourism-related employment indicators.

    Uses the combined TOUR10/TOUR24 series:
      - 2001–2009: TOUR10
      - 2000 and 2010–2024: TOUR24

    Employment is reported as number of jobs. TOUR24 provides hotel and
    eating/drinking employment components; TOUR10 provides only the total.
    Employment observations for 2023–2024 are unavailable.
    """
    df = load_usviber_combined(deflate=False)

    keep = [
        "year",
        "emp_tourism_total",
        "emp_hotels",
        "emp_eating_drinking",
        "source_publication",
    ]

    out = (
        df.loc[df["year"].between(2000, 2024), keep]
        .sort_values("year")
        .reset_index(drop=True)
    )

    _save(out, "employment_usviber.csv")
    return out


# ---------------------------------------------------------------------------
# 7. QCEW territory NAICS 72 — employment_qcew.csv
# ---------------------------------------------------------------------------

def export_qcew():
    qcew = load_qcew(deflate=True, cpi_base_year=2016)
    # Territory total, NAICS 72 only
    out = qcew.query("area_fips == '78000' and naics == '72'").copy()
    keep = [
        "year", "naics", "naics_label", "disclosure_code",
        "annual_avg_estabs", "annual_avg_emplvl",
        "total_annual_wages", "annual_avg_wkly_wage", "avg_annual_pay",
        "avg_annual_pay_real", "total_annual_wages_real", "cpi_base_year",
    ]
    _save(out[keep].reset_index(drop=True), "employment_qcew.csv")
    return out


# ---------------------------------------------------------------------------
# 8. Census Economic Census NAICS 72 — census_naics72.csv
# ---------------------------------------------------------------------------

def export_census_naics72():
    """
    Combine NAICS-72-equivalent rows across Census vintages.

    2007 vintage: A01 file, top-level NAICS 72 row (naics='72' or similar label).
    2012 vintage: BASIC02 .dat file.
    2017 and 2022 vintages: BASIC02 .dat files (contain both vintage years).

    We retain the vintage year as the year of publication; the data year is
    embedded in the YEAR column of each file.
    """
    frames = []

    # 2007 (A01)
    try:
        c07 = load_census_2007()
        # NAICS 72 — look for label containing "Accommodation and food"
        c07_72 = c07[c07["naics_label"].str.contains("ccommodation and food", na=False)].copy()
        if not c07_72.empty:
            row = c07_72.iloc[0].copy()
            frames.append({
                "year": int(row["year"]),
                "census_vintage": 2007,
                "naics": "72",
                "naics_label": row["naics_label"],
                "estab": row["estab"],
                "emp": row["emp"],
            })
    except Exception as e:
        print(f"    Warning: 2007 Census A01 skipped: {e}")

    # 2012 BASIC02
    try:
        c12 = load_census_2012_basic()
        c12_72 = c12[c12["naics"].astype(str).str.strip() == "72"].copy()
        for _, row in c12_72.iterrows():
            frames.append({
                "year": int(row["year"]),
                "census_vintage": 2012,
                "naics": "72",
                "naics_label": row["naics_label"],
                "estab": row["estab"],
                "emp": row["emp"],
            })
    except Exception as e:
        print(f"    Warning: 2012 Census BASIC02 skipped: {e}")

    # 2017 BASIC02 (contains 2012 and 2017 year rows — keep only 2017)
    try:
        c17 = load_census_2017_basic()
        c17_72 = c17[
            (c17["naics"].astype(str).str.strip() == "72") &
            (c17["year"] == 2017)
        ].copy()
        for _, row in c17_72.iterrows():
            frames.append({
                "year": int(row["year"]),
                "census_vintage": 2017,
                "naics": "72",
                "naics_label": row["naics_label"],
                "estab": row["estab"],
                "emp": row["emp"],
            })
    except Exception as e:
        print(f"    Warning: 2017 Census BASIC02 skipped: {e}")

    # 2022 BASIC02 (contains 2017 and 2022 year rows — keep only 2022)
    try:
        c22 = load_census_2022_basic()
        c22_72 = c22[
            (c22["naics"].astype(str).str.strip() == "72") &
            (c22["year"] == 2022)
        ].copy()
        for _, row in c22_72.iterrows():
            frames.append({
                "year": int(row["year"]),
                "census_vintage": 2022,
                "naics": "72",
                "naics_label": row["naics_label"],
                "estab": row["estab"],
                "emp": row["emp"],
            })
    except Exception as e:
        print(f"    Warning: 2022 Census BASIC02 skipped: {e}")

    if not frames:
        print("    Warning: No Census NAICS 72 data loaded. Exporting empty file.")
        df = pd.DataFrame(columns=["year", "census_vintage", "naics", "naics_label",
                                    "estab", "emp"])
    else:
        df = pd.DataFrame(frames).drop_duplicates(["year", "census_vintage"])
        df = df.sort_values("year").reset_index(drop=True)

    _save(df, "census_naics72.csv")
    return df


# ---------------------------------------------------------------------------
# 9. BEA real GDP — bea_gdp_real.csv
# ---------------------------------------------------------------------------

def export_bea_gdp_real():
    # BEA table 1.2 is the real (chained-dollar) GDP table.
    # The first data row (line == '1') is the aggregate real GDP series.
    # The label reads "Gross domestic product" (not "Real...") — that is
    # the row's label within the real-dollar table.
    bea = load_bea("1.2")
    df = (
        bea[
            (bea["label"].str.contains("Gross domestic product", case=False, na=False)) &
            (bea["line"].astype(str).str.strip() == "1")
        ]
        .drop_duplicates("year")[["year", "value"]]
        .rename(columns={"value": "gdp_real"})
        .sort_values("year")
        .reset_index(drop=True)
    )
    _save(df, "bea_gdp_real.csv")
    return df


# ---------------------------------------------------------------------------
# 10. BEA real A&F value added — bea_af_real.csv
# ---------------------------------------------------------------------------

def export_bea_af_real():
    bea = load_bea("2.3")
    df = (
        bea[bea["label"].str.contains("ccommodation", case=False, na=False)]
        .drop_duplicates("year")[["year", "value"]]
        .rename(columns={"value": "af_real"})
        .sort_values("year")
        .reset_index(drop=True)
    )
    _save(df, "bea_af_real.csv")
    return df


# ---------------------------------------------------------------------------
# 11. BEA A&F share of nominal GDP — bea_af_share.csv
# ---------------------------------------------------------------------------

def export_bea_af_share():
    bea_nom = load_bea("2.1")
    bea_gdp = load_bea("1.1")

    af_nom = (
        bea_nom[bea_nom["label"].str.contains("ccommodation", case=False, na=False)]
        .drop_duplicates("year")[["year", "value"]]
        .rename(columns={"value": "af_nom"})
    )
    gdp_nom = (
        bea_gdp[bea_gdp["label"].str.contains("Gross domestic product", case=False, na=False)]
        .drop_duplicates("year")[["year", "value"]]
        .rename(columns={"value": "gdp_nom"})
    )

    share = af_nom.merge(gdp_nom, on="year")
    share["af_pct_gdp"] = (share["af_nom"] / share["gdp_nom"] * 100).round(2)
    share = share.sort_values("year").reset_index(drop=True)
    _save(share, "bea_af_share.csv")
    return share


# ---------------------------------------------------------------------------
# 12. Census guestrooms — census_rooms.csv
# ---------------------------------------------------------------------------

def export_census_rooms():
    df = load_census_rooms()
    _save(df, "census_rooms.csv")
    return df


# ---------------------------------------------------------------------------
# 13. NPS VIIS annual — nps_viis.csv
# ---------------------------------------------------------------------------

def export_nps_viis():
    df = load_nps_annual("VIIS")
    # Restrict to report period
    df = df[df["year"] >= 2000][["year", "recreation_visitors"]].copy()
    _save(df, "nps_viis.csv")
    return df


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(
    visitors: pd.DataFrame,
    fred: pd.DataFrame,
    hotel: pd.DataFrame,
) -> None:
    """
    Spot-check key values against known report figures.
    Prints discrepancies without raising errors.
    """
    checks = [
        # (description, actual, expected, tolerance_pct)
        ("Air visitors 2024 (thousands)",
         visitors.loc[visitors["year"] == 2024, "air_visitors"].iloc[0],
         884.2, 0.1),
        ("Cruise passengers 2024 (thousands)",
         visitors.loc[visitors["year"] == 2024, "cruise_passengers"].iloc[0],
         1599.8, 0.1),
        ("Total visitors 2024 (thousands)",
         visitors.loc[visitors["year"] == 2024, "total_visitors"].iloc[0],
         2507.1, 0.1),
        ("Hotel rooms 2016",
         visitors.loc[visitors["year"] == 2016, "hotel_rooms"].iloc[0],
         3819, 1),
        ("Hotel rooms 2024",
         visitors.loc[visitors["year"] == 2024, "hotel_rooms"].iloc[0],
         3127, 1),
        ("Occupancy rate 2016 (%)",
         visitors.loc[visitors["year"] == 2016, "occupancy_rate_pct"].iloc[0],
         56.7, 0.1),
        ("Occupancy rate 2024 (%)",
         visitors.loc[visitors["year"] == 2024, "occupancy_rate_pct"].iloc[0],
         66.3, 0.1),
        ("Nominal expenditure 2024 ($M)",
         visitors.loc[visitors["year"] == 2024, "expenditures_total"].iloc[0],
         1828.5, 0.1),
        ("FRED L&H annual mean 2024 (thousands)",
         fred.loc[fred["year"] == 2024, "emp_sa_avg"].iloc[0],
         6.98, 0.1),
        ("Hotel available room-nights 2016 (thousands)",
         hotel.loc[hotel["year"] == 2016, "nights_available_k"].iloc[0],
         1742.8, 1),
    ]

    print("\nValidation:")
    all_ok = True
    for desc, actual, expected, tol in checks:
        try:
            pct_diff = abs(float(actual) - expected) / expected * 100
            status = "PASS" if pct_diff <= tol else "FAIL"
            if pct_diff > tol:
                all_ok = False
            print(f"  [{status}] {desc}: {actual:.1f} (expected {expected}, diff {pct_diff:.2f}%)")
        except (IndexError, TypeError, ValueError) as e:
            print(f"  [ERR ] {desc}: check failed ({e})")
            all_ok = False

    if all_ok:
        print("  All checks passed.")
    else:
        print("  One or more checks failed - review before publishing.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Exporting report-ready datasets to data/processed/\n")
    import os
    os.chdir(PROJECT_ROOT)

    visitors = export_visitors()
    hotel = export_hotel_annual()
    export_hotel_island()
    export_island_arrivals()
    fred_ann = export_fred_employment()
    export_usviber_employment()
    export_qcew()
    export_census_naics72()
    export_bea_gdp_real()
    export_bea_af_real()
    export_bea_af_share()
    export_census_rooms()
    export_nps_viis()

    validate(visitors, fred_ann, hotel)

    print(f"\nAll exports complete -> {PROCESSED}")


if __name__ == "__main__":
    main()
