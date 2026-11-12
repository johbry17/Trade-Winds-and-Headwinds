"""
src/validation.py
Cross-source validation checks and data-quality log.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Literal

import pandas as pd


Severity = Literal["HIGH", "MEDIUM", "LOW"]


@dataclass
class DQIssue:
    severity: Severity
    source: str
    variable: str
    evidence: str
    recommended_treatment: str


# ---------------------------------------------------------------------------
# Canonical data-quality log
# ---------------------------------------------------------------------------

DATA_QUALITY_LOG: list[DQIssue] = [
    DQIssue(
        severity="HIGH",
        source="World Bank / VIR.ST.INT.ARVL.json",
        variable="arrivals (2020)",
        evidence=(
            "2020 value = 8,612,000, which is ~4× the normal range (~2M) "
            "and physically impossible in a COVID year when cruise ships were halted. "
            "All other non-null years range 1,741,000–2,814,000."
        ),
        recommended_treatment=(
            "Set to NaN. Do not use for analysis until verified against "
            "World Bank source API or USVIBER. The JSON file is a cached "
            "single-page export (50 records); a data entry error is plausible."
        ),
    ),
    DQIssue(
        severity="HIGH",
        source="VIIS Recreation Visitors By Month (2026)",
        variable="monthly recreation visitors (Jan–Aug 2026)",
        evidence=(
            "Jan–Jun 2026 each show 100,000–170,000 visitors, roughly 3× the "
            "corresponding 2025 months (40,000–55,000). Jul–Aug drop to ~500 and ~366. "
            "The partial-year total column (890,179) would far exceed 2025's full-year "
            "total (471,074) if the Jan–Jun pattern continued. "
            "Likely a methodology change or data entry error."
        ),
        recommended_treatment=(
            "Exclude 2026 from any trend analysis until the source NPS portal "
            "is re-checked for a methodology note. Do not extrapolate 2026 figures."
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="USVIBER TOUR24.pdf vs TOUR10.pdf",
        variable="tourist and air_excursionist series (historical revisions)",
        evidence=(
            "TOUR10 and TOUR24 show material differences for overlapping years. "
            "Year 2000: total_visitors +121k, air_excursionists +135k (81.5→216.7k), "
            "tourists +0.8k (stable), cruise_passengers unchanged. "
            "Year 2010: total_visitors +147k, tourists −14k, excursionists +161k, "
            "air_excursionists +11k, cruise_passengers unchanged. "
            "Accommodation (hotel_rooms, total_rooms, occupancy) is consistent. "
            "Reason for revisions is not established from available source materials."
        ),
        recommended_treatment=(
            "Use TOUR24 for 2000 and 2010–2024; use TOUR10 for 2001–2009 with "
            "a discontinuity flag at 2000/2001 and 2009/2010 boundaries for the "
            "tourist/excursionist/air_visitor series. The accommodation series "
            "(hotel_rooms, occupancy) can be merged seamlessly."
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="NPS VIIS Recreation Visitors By Month",
        variable="counting methodology (three periods)",
        evidence=(
            "2003–2021 method: campground + Trunk Bay multipliers (8.53 persons/boat), "
            "beach and visitor-center counts, percentage-based estimates. "
            "2022–2025 method: revised estimation following the closure of Maho Bay "
            "and Caneel Bay resort; adjustment considered minor by domain experts. "
            "2026+ method: Lind Point traffic counter (vehicles × PPV × factors), "
            "pedestrian/trail counters — fundamentally different inputs and units; "
            "2026 counts are ~3–4× 2025 equivalents, consistent with a methodology break."
        ),
        recommended_treatment=(
            "Exclude 2026 from historical comparisons. The 2022 method change is minor. "
            "Report visitation as 'estimated recreation visits' rather than 'visitors.'"
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="USVIBER TOUR24.pdf",
        variable="air_visitors: do not assume tourists + air_excursionists = air_visitors",
        evidence=(
            "USVIBER reports air_visitors separately; it is not reliably reconstructed "
            "from tourists plus air_excursionists. Year 2024: air_visitors = 884.2k; "
            "tourists = 380.3k; air_excursionists = 527.1k; sum = 907.4k ≠ 884.2k. "
            "The identity is not universally valid in the published data."
        ),
        recommended_treatment=(
            "Use published air_visitors directly. Do not calculate total air-visitor "
            "expenditure per air visitor by combining tourist and air-excursionist spending. "
            "Tourist expenditure is not split by arrival mode. Air_visitors = "
            "not all tourists. Some overnight tourists arrive by private yacht or ferry. "
            "Use air_visitors and cruise_passengers as the modal breakdown; "
            "use tourists and excursionists as the overnight/day-tripper breakdown."
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="Census NAPCS02 (2017, 2022)",
        variable="RMRTRAN (guestrooms) in Total row vs room-product row",
        evidence=(
            "2017 NAPCS02 Total row: RMRTRAN = 8,735. "
            "2017 NAPCS02 product 7003825000 row: RMRTRAN = 2,624. "
            "2022 NAPCS02 Total row: RMRTRAN = 1,958. "
            "2022 NAPCS02 product 7003825000 row: RMRTRAN = 2,039. "
            "The Total row RMRTRAN is inconsistent across vintages and appears "
            "to aggregate differently than the room-specific product row."
        ),
        recommended_treatment=(
            "Use product 7003825000 RMRTRAN for 2017 and 2022 guestroom counts. "
            "For 2007 and 2012, use A10 industry total RMRTRAN. "
            "Document this crosswalk explicitly in the data dictionary."
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="BUIS Annual / Monthly",
        variable="recreation_visitors (1999–2001)",
        evidence=(
            "Years 1999, 2000, and 2001 are absent from both BUIS annual and "
            "monthly files. The monthly file jumps from 1998 to 2002 in annual rows."
        ),
        recommended_treatment=(
            "Note gap in visualisations. Do not interpolate. "
            "The NPS IRMA portal may have data; consider manual re-export."
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="Census 2017 NAPCS02",
        variable="guestrooms (reference date)",
        evidence=(
            "Census guestroom count is as of December 31 of the census year. "
            "For 2017, this is ~3 months after Hurricanes Irma (Sep 6) and "
            "Maria (Sep 19). The count (2,624) reflects post-hurricane room "
            "availability, not the pre-hurricane baseline."
        ),
        recommended_treatment=(
            "Label as 'end-of-2017 (post-hurricane)' in all tables and charts. "
            "Do not use as a pre-hurricane benchmark."
        ),
    ),
    DQIssue(
        severity="MEDIUM",
        source="USVIBER TOUR24.pdf / employment rows",
        variable="emp_tourism_total, emp_hotels, emp_eating_drinking (2023–2024)",
        evidence=(
            "TOUR24 states: 'data on tourism-related employment compiled by the "
            "Department of Labor is currently not available.' Rows show N/A."
        ),
        recommended_treatment=(
            "Use FRED Leisure & Hospitality employment as the primary employment "
            "indicator for post-2022 periods. USVIBER employment series ends 2022."
        ),
    ),
    DQIssue(
        severity="LOW",
        source="FRED SMS78000007000000001 / SMU78000007000000001",
        variable="emp_sa, emp_nsa — units",
        evidence=(
            "Values are in thousands of persons (e.g., 8.0 = 8,000 workers). "
            "This must be labeled clearly to avoid orders-of-magnitude errors "
            "when comparing with Census employment counts."
        ),
        recommended_treatment=(
            "Always label axes as 'thousands of employees' or multiply by 1,000 "
            "before comparing with Census point-in-time employment."
        ),
    ),
    DQIssue(
        severity="LOW",
        source="World Bank JSON (both files)",
        variable="pagination",
        evidence=(
            "Metadata shows pages=2 (total=66 records) but local file contains "
            "only page 1 (50 records). Pre-1995 data is on page 2 but all "
            "non-null values appear on page 1 (1995–2020)."
        ),
        recommended_treatment=(
            "Pre-1995 data is not needed for the 2000–2025 analysis scope. "
            "No action required."
        ),
    ),
    DQIssue(
        severity="LOW",
        source="USVI CPI / Econ21.pdf",
        variable="cpi_2018 value",
        evidence=(
            "The CPI index drops from 130.0 (2017) to 99.8 (2018), a ~23% fall, "
            "which seems implausible as a true price deflation signal. "
            "This may reflect a re-basing, PDF column misalignment, or a real "
            "economic disruption. The 2017 hurricanes could have caused "
            "statistical complications."
        ),
        recommended_treatment=(
            "Flag in data dictionary. Do not use CPI-deflated series spanning "
            "2017–2018 without verifying the 2018 value with USVIBER directly."
        ),
    ),
    DQIssue(
        severity="LOW",
        source="BEA vigdp0624.xlsx",
        variable="industry value-added coverage",
        evidence=(
            "Table 1.x (GDP expenditure accounts): 2002–2022. "
            "Tables 2.x (industry value added): 2002–2021. "
            "The file name suggests 2024 vintage but industry breakdowns "
            "do not extend to 2022."
        ),
        recommended_treatment=(
            "Use Table 1.1 for nominal GDP through 2022. "
            "Use Tables 2.x for accommodation value added through 2021 only. "
            "Label coverage explicitly in charts and tables."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_nps_annual_vs_monthly(
    annual: pd.DataFrame, monthly: pd.DataFrame, park: str
) -> pd.DataFrame:
    """
    Compare annual recreation visitors against the sum of monthly visitors.

    Returns a DataFrame of year-level discrepancies.
    """
    agg = (
        monthly[monthly["park"] == park]
        .groupby("year")["recreation_visitors"]
        .sum()
        .reset_index()
        .rename(columns={"recreation_visitors": "monthly_sum"})
    )
    ann_sub = annual[annual["park"] == park][["year", "recreation_visitors"]].rename(
        columns={"recreation_visitors": "annual_value"}
    )
    merged = ann_sub.merge(agg, on="year", how="outer")
    merged["discrepancy"] = merged["annual_value"] - merged["monthly_sum"]
    merged["discrepancy_pct"] = (
        merged["discrepancy"] / merged["annual_value"] * 100
    ).round(2)
    return merged[merged["discrepancy"].abs() > 0].sort_values("year")


def validate_usviber_arithmetic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check internal arithmetic consistency of USVIBER table.

    Checks (tolerance ±0.5k for visitors, ±0.5M for expenditures):
    - tourists + excursionists == total_visitors
    - air_excursionists + cruise_passengers == excursionists
    - expenditures_tourists + expenditures_excursionists == expenditures_total
    - expenditures_air_excursionists + expenditures_cruise_passengers
        == expenditures_excursionists  (only if both columns present)

    Records where the identity cannot be tested (missing values) are marked
    as 'untestable' rather than passed or failed.
    """
    checks = []
    df = df.copy().set_index("year")
    has_exp_split = (
        "expenditures_air_excursionists" in df.columns and
        "expenditures_cruise_passengers" in df.columns
    )

    for year, row in df.iterrows():
        for lhs, rhs_parts, label in [
            ("total_visitors",
             ["tourists", "excursionists"],
             "total = tourists + excursionists"),
            ("excursionists",
             ["air_excursionists", "cruise_passengers"],
             "excursionists = air + cruise"),
            ("expenditures_total",
             ["expenditures_tourists", "expenditures_excursionists"],
             "expenditures = tourists + excursionists"),
        ]:
            if any(pd.isna(row.get(c)) for c in [lhs] + rhs_parts):
                checks.append({"year": year, "check": label,
                                "actual": None, "expected": None,
                                "diff": None, "status": "untestable"})
                continue
            actual = row[lhs]
            expected = sum(row[c] for c in rhs_parts)
            diff = round(actual - expected, 1)
            checks.append({"year": year, "check": label,
                            "actual": actual, "expected": expected,
                            "diff": diff,
                            "status": "ok" if abs(diff) <= 0.5 else "discrepancy"})

        if has_exp_split:
            lhs_val = row.get("expenditures_excursionists")
            air_val = row.get("expenditures_air_excursionists")
            cru_val = row.get("expenditures_cruise_passengers")
            label = "excursionist_exp = air_exc_exp + cruise_exp"
            if any(pd.isna(v) for v in [lhs_val, air_val, cru_val]):
                checks.append({"year": year, "check": label,
                                "actual": None, "expected": None,
                                "diff": None, "status": "untestable"})
            else:
                diff = round(lhs_val - (air_val + cru_val), 1)
                checks.append({"year": year, "check": label,
                                "actual": lhs_val, "expected": air_val + cru_val,
                                "diff": diff,
                                "status": "ok" if abs(diff) <= 0.5 else "discrepancy"})

    result = pd.DataFrame(checks)
    return result[result["status"] != "ok"].sort_values(["year", "check"])


def print_dq_log(severity_filter: Severity | None = None) -> None:
    """Print the data-quality log, optionally filtered by severity."""
    for issue in DATA_QUALITY_LOG:
        if severity_filter and issue.severity != severity_filter:
            continue
        print(f"[{issue.severity}] {issue.source} — {issue.variable}")
        print(f"  Evidence:   {issue.evidence[:120]}...")
        print(f"  Treatment:  {issue.recommended_treatment[:100]}...")
        print()
