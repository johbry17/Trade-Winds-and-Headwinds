"""
src/hotel_extraction.py
Extract and clean USVIBER hotel statistics from PDF reports.

Sources
-------
data/raw/USVIBER-Hotel/Occupancy/       — H01–H25 (hotel occupancy rates, %)
data/raw/USVIBER-Hotel/NIghts-Occupied/ — HRN01, HRN03–RN25 (room nights occupied, thousands)
data/raw/USVIBER-Hotel/Nights-Available/— RA07–RA25 (room nights available, thousands)

Each PDF covers two consecutive reporting years.
Three geographies per PDF: ST. THOMAS/ST. JOHN, ST. CROIX, U.S.V.I. TOTAL.

Reporting-period distinctions
------------------------------
Each PDF contains two distinct annual aggregate rows:

  YEAR TO DATE: DECEMBER  — cumulative occupancy for hotels reporting in BOTH
                             the prior and current year (same-property comparison).
                             Labeled reporting_period = "YTD_December".

  ANNUAL TOTAL:            — total room nights occupied / total room nights
                             available across ALL reporting hotels for the full
                             calendar year.  This is the preferred annual summary.
                             Labeled reporting_period = "Annual_Total".

For the **nights** series (occupied and available) these two rows always match —
they are simply two labels for the same cumulative count.

For the **occupancy** series, they can diverge substantially:
  • 2017: YTD=51.3%, Annual Total=44.1%.  The difference arises because the YTD
    row excludes hotels that closed after the September 2017 hurricanes from the
    denominator, inflating the rate.  Annual Total is consistent with USVIBER's
    annual indicator (43.9%) and the nights-based calculation (44.1%).
  • 2012: YTD=58.9%, Annual Total=48.0%.  This divergence also exists in a
    pre-hurricane year, confirming that the two rows measure different things
    regardless of storm damage.

Coverage / population note
---------------------------
The PDF hotel series tracks hotels that submit monthly reports to USVIBER.
This is a subset of all accommodation establishments.  The USVIBER Annual
Tourism Indicator (tour24 series) covers the full accommodation universe
including condominiums and vacation rentals via an annual survey.

In 2016, the two series agree (PDF Annual Total = USVIBER Annual = 56.7%).
Post-hurricane, they diverge: in 2024 the PDF Annual Total is 61.0% while
the USVIBER Annual Indicator is 66.3%.  This is a population/coverage
difference, not an extraction error.  Both figures are retained as separate
measures.

Usage
-----
    from src.hotel_extraction import extract_all_hotel_pdfs, load_hotel_annual
    records = extract_all_hotel_pdfs()
    df = load_hotel_annual()
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pdfplumber

RAW_HOTEL = Path("data/raw/USVIBER-Hotel")
INTERIM_HOTEL = Path("data/interim/hotel")

_NUM = r"[\-]?\d[\d,]*(?:\.\d+)?"  # signed decimal, optional thousands comma


# ---------------------------------------------------------------------------
# Title-year extraction
# ---------------------------------------------------------------------------

def _extract_title_years(text: str) -> tuple[int | None, int | None, str]:
    """Return (prior_year, current_year, final_month) from the PDF title line."""
    patterns = [
        r"(?:January|JANUARY)\s*(\d{4})\s+to\s+"
        r"((?:December|DECEMBER|November|NOVEMBER))\s*(\d{4})",
        r"(?:January|JANUARY)(\d{4})to"
        r"((?:December|DECEMBER|November|NOVEMBER))(\d{4})",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            yr_prior = int(m.group(1))
            yr_current = int(m.group(3))
            final_month = "December" if "dec" in m.group(2).lower() else "November"
            return yr_prior, yr_current, final_month
    return None, None, "December"


# ---------------------------------------------------------------------------
# Row extractors
# ---------------------------------------------------------------------------

def _parse_9_values(group_text: str) -> list[float] | None:
    """
    Extract 9 numbers from a table row group.

    Layout: STJ_prior, STJ_current, STJ_pct,
            STX_prior, STX_current, STX_pct,
            USVI_prior, USVI_current, USVI_pct
    """
    raw = re.findall(_NUM, group_text)[:9]
    if len(raw) == 9:
        return [float(n.replace(",", "")) for n in raw]
    return None


def _extract_ytd_december(text: str) -> list[float] | None:
    """
    Extract the YEAR TO DATE: DECEMBER row (same-property comparison rate).

    This row may appear before or after the month-name label depending on PDF
    vintage.
    """
    nums9 = r"\s+".join([_NUM] * 9)
    patterns = [
        # Classic: label then values
        re.compile(
            r"(?:(?:TOTAL\s+)?YEAR\s+TO\s+DATE[:\s]*\n+)?"
            r"(?:DECEMBER)\s*\n?\s*(" + nums9 + r")",
            re.MULTILINE,
        ),
        # Compact no-space PDFs
        re.compile(r"YEARTODATE[:\s]*\n?\s*(" + nums9 + r")", re.MULTILINE),
        # Newer format: YEAR TO DATE: → values → DECEMBER
        re.compile(
            r"(?:TOTAL\s+)?YEAR\s+TO\s+DATE[:\s]*\n\s*(" + nums9 + r")"
            r"\s*\n\s*(?:DECEMBER)",
            re.MULTILINE,
        ),
    ]
    for pat in patterns:
        m = pat.search(text)
        if m:
            vals = _parse_9_values(m.group(1))
            if vals:
                return vals
    return None


def _extract_annual_total(text: str) -> tuple[list[float] | None, str | None]:
    """
    Extract the ANNUAL TOTAL / ANNUAL TOTALS row (total-market rate).

    Returns (values_9, quality_flag).
    quality_flag is None if values look good, or a warning string if suspect
    (e.g. identical values across all three geography groups, as seen in H01).
    """
    ann_re = re.compile(
        r"ANNUAL\s+TOTALS?[:\s]*\s*(" + r"\s+".join([_NUM] * 9) + r")",
        re.MULTILINE,
    )
    m = ann_re.search(text)
    if not m:
        return None, None

    vals = _parse_9_values(m.group(1))
    if vals is None:
        return None, None

    # Check for the H01 anomaly: all three geo groups are identical
    stj = (vals[0], vals[1])
    stx = (vals[3], vals[4])
    usvi = (vals[6], vals[7])
    if stj == stx == usvi:
        return vals, "SUSPECT: identical values across all three geographies"

    return vals, None


# ---------------------------------------------------------------------------
# Single-PDF extractor
# ---------------------------------------------------------------------------

def _parse_pdf(path: Path, metric: str) -> list[dict]:
    """
    Extract all annual aggregate observations from one PDF.

    For each reporting year, produces up to two records per geography:
      - reporting_period = "YTD_December"   (from the YEAR TO DATE row)
      - reporting_period = "Annual_Total"    (from the ANNUAL TOTAL row)

    Both rows are retained.  The selection step decides which to prefer.
    """
    is_revised = any(t in path.name.lower() for t in ["-revised", "-rev", "revised"])
    vintage = "revised" if is_revised else "original"

    records: list[dict] = []

    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            yr_prior, yr_current, final_month = _extract_title_years(text)
            if yr_prior is None:
                continue

            # --- YTD December row ---
            ytd_vals = _extract_ytd_december(text)
            # --- Annual Total row ---
            ann_vals, ann_flag = _extract_annual_total(text)

            if ytd_vals is None and ann_vals is None:
                for geo in ("STJ", "STX", "USVI_TOTAL"):
                    records.append({
                        "source_file": path.name,
                        "source_dir": metric,
                        "page": page_num + 1,
                        "vintage": vintage,
                        "reporting_period": "PARSE_FAILURE",
                        "year": yr_prior,
                        "geo": geo,
                        "value": None,
                        "note": "Annual rows not parsed",
                    })
                break

            geo_indices = {"STJ": (0, 1), "STX": (3, 4), "USVI_TOTAL": (6, 7)}

            for geo, (i_prior, i_current) in geo_indices.items():
                # YTD December
                if ytd_vals is not None:
                    ytd_note_prior = f"YTD_Dec prior from {path.name}"
                    ytd_note_curr = (
                        f"YTD_Dec current from {path.name}"
                        if final_month == "December"
                        else f"YTD_{final_month} current (partial year) from {path.name}"
                    )
                    records.append({
                        "source_file": path.name,
                        "source_dir": metric,
                        "page": page_num + 1,
                        "vintage": vintage,
                        "reporting_period": "YTD_December" if final_month == "December" else f"YTD_{final_month}",
                        "year": yr_prior,
                        "geo": geo,
                        "value": ytd_vals[i_prior],
                        "note": ytd_note_prior,
                    })
                    records.append({
                        "source_file": path.name,
                        "source_dir": metric,
                        "page": page_num + 1,
                        "vintage": vintage,
                        "reporting_period": "YTD_December" if final_month == "December" else f"YTD_{final_month}",
                        "year": yr_current,
                        "geo": geo,
                        "value": ytd_vals[i_current],
                        "note": ytd_note_curr,
                    })

                # Annual Total
                if ann_vals is not None:
                    base_note = f"Annual_Total from {path.name}"
                    if ann_flag:
                        base_note += f"; {ann_flag}"
                    records.append({
                        "source_file": path.name,
                        "source_dir": metric,
                        "page": page_num + 1,
                        "vintage": vintage,
                        "reporting_period": "Annual_Total",
                        "year": yr_prior,
                        "geo": geo,
                        "value": ann_vals[i_prior],
                        "note": f"{base_note} (prior year)",
                    })
                    records.append({
                        "source_file": path.name,
                        "source_dir": metric,
                        "page": page_num + 1,
                        "vintage": vintage,
                        "reporting_period": "Annual_Total",
                        "year": yr_current,
                        "geo": geo,
                        "value": ann_vals[i_current],
                        "note": base_note + (f"; {ann_flag}" if ann_flag and "SUSPECT" not in base_note else ""),
                    })

            break  # First page contains all data

    return records


# ---------------------------------------------------------------------------
# Full extraction
# ---------------------------------------------------------------------------

def extract_all_hotel_pdfs() -> pd.DataFrame:
    """
    Extract all annual observations from PDFs across the three metric directories.

    Returns a source-observation DataFrame with one row per
    (source_file × year × geography × reporting_period).

    Saves to data/interim/hotel/hotel_source_observations.csv.
    """
    METRIC_DIRS = {
        "occupancy": RAW_HOTEL / "Occupancy",
        "nights_occupied": RAW_HOTEL / "NIghts-Occupied",
        "nights_available": RAW_HOTEL / "Nights-Available",
    }

    all_records: list[dict] = []
    for metric, d in METRIC_DIRS.items():
        for pdf_path in sorted(d.glob("*.pdf")):
            all_records.extend(_parse_pdf(pdf_path, metric))

    df = pd.DataFrame(all_records)
    df = df.sort_values(
        ["source_dir", "geo", "year", "reporting_period", "source_file"]
    ).reset_index(drop=True)

    INTERIM_HOTEL.mkdir(parents=True, exist_ok=True)
    df.to_csv(INTERIM_HOTEL / "hotel_source_observations.csv", index=False)
    return df


# ---------------------------------------------------------------------------
# Selection logic
# ---------------------------------------------------------------------------

def _select_preferred(group: pd.DataFrame) -> pd.Series:
    """
    For a group sharing (metric, geo, year), return the single preferred observation.

    Priority:
    1. reporting_period = "Annual_Total"  (not flagged as SUSPECT)
    2. reporting_period = "YTD_December"
    3. Any other December/partial (fallback)

    Within each tier: revised > original; then most-recent source file.
    """
    # Exclude suspect Annual_Total rows (H01 identical-values anomaly)
    good_annual = group[
        (group["reporting_period"] == "Annual_Total")
        & ~group["note"].str.contains("SUSPECT", na=False)
    ]
    if not good_annual.empty:
        pool = good_annual
    else:
        ytd_dec = group[group["reporting_period"] == "YTD_December"]
        pool = ytd_dec if not ytd_dec.empty else group

    revised = pool[pool["vintage"] == "revised"]
    pool = revised if not revised.empty else pool
    return pool.sort_values("source_file", ascending=False).iloc[0]


def build_selected_dataset(source_obs: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Apply selection rules to produce a clean selected dataset.

    Also builds:
      - hotel_annual_total_vs_ytd.csv: comparison of Annual_Total vs YTD_December
        for the occupancy series only (the two can differ significantly).
      - hotel_conflict_log.csv: year/geo combinations with conflicting values
        among observations of the same reporting_period type.
      - hotel_source_comparison.csv: selected occupancy vs USVIBER annual indicator.

    Saves all outputs to data/interim/hotel/.
    """
    if source_obs is None:
        source_obs = pd.read_csv(INTERIM_HOTEL / "hotel_source_observations.csv")

    source_obs = source_obs[source_obs["value"].notna()].copy()

    # --- Annual Total vs YTD December comparison (occupancy only) ---
    occ = source_obs[source_obs["source_dir"] == "occupancy"].copy()

    ann = (
        occ[occ["reporting_period"] == "Annual_Total"]
        .groupby(["geo", "year"])["value"]
        .first()
        .reset_index()
        .rename(columns={"value": "annual_total_pct"})
    )
    ytd = (
        occ[occ["reporting_period"] == "YTD_December"]
        .groupby(["geo", "year"])["value"]
        .first()
        .reset_index()
        .rename(columns={"value": "ytd_december_pct"})
    )
    comparison = ann.merge(ytd, on=["geo", "year"], how="outer").sort_values(["geo", "year"])
    comparison["diff_ppt"] = (
        comparison["annual_total_pct"] - comparison["ytd_december_pct"]
    ).round(1)
    comparison["note"] = comparison["diff_ppt"].apply(
        lambda d: (
            "" if pd.isna(d) or abs(d) < 0.5
            else f"DISCREPANCY: Annual_Total {d:+.1f}pp vs YTD_December"
        )
    )
    comparison.to_csv(INTERIM_HOTEL / "hotel_annual_total_vs_ytd.csv", index=False)

    # --- Conflict log: distinct values within same reporting_period ---
    conflicts = (
        source_obs.groupby(["source_dir", "geo", "year", "reporting_period"])
        .apply(lambda g: len(g["value"].unique()), include_groups=False)
        .reset_index(name="n_distinct_values")
        .query("n_distinct_values > 1")
    )
    conflicts.to_csv(INTERIM_HOTEL / "hotel_conflict_log.csv", index=False)

    # --- Build selected dataset ---
    rows = []
    for (metric, geo, year), group in source_obs.groupby(["source_dir", "geo", "year"]):
        rows.append(_select_preferred(group))
    selected = pd.DataFrame(rows).reset_index(drop=True)

    selected["is_partial_year"] = (
        (selected["year"] == 2025) & (selected["reporting_period"] != "Annual_Total")
        & ~selected["reporting_period"].str.contains("December", na=False)
    )

    selected.to_csv(INTERIM_HOTEL / "hotel_selected.csv", index=False)
    return selected


# ---------------------------------------------------------------------------
# Convenience loader
# ---------------------------------------------------------------------------

def load_hotel_annual(
    geo: str = "USVI_TOTAL",
    exclude_partial: bool = True,
) -> pd.DataFrame:
    """
    Load the selected annual hotel dataset in wide format.

    Parameters
    ----------
    geo : str
        'USVI_TOTAL', 'STJ', or 'STX'.
    exclude_partial : bool
        If True, exclude 2025 partial-year observations.

    Returns
    -------
    DataFrame with columns: year, occupancy_pct, nights_occupied_k,
    nights_available_k, occ_calculated, reporting_period_occupancy.

    occupancy_pct is from the Annual_Total row where available; YTD_December
    otherwise.  reporting_period_occupancy records which row was used.

    occ_calculated = nights_occupied_k / nights_available_k × 100.
    It is derived independently and may differ from occupancy_pct because the
    two series measure slightly different sets of properties.
    """
    sel_path = INTERIM_HOTEL / "hotel_selected.csv"
    if not sel_path.exists():
        raw = extract_all_hotel_pdfs()
        build_selected_dataset(raw)
    df = pd.read_csv(sel_path)

    df = df[df["geo"] == geo].copy()
    if exclude_partial:
        df = df[~df["is_partial_year"].fillna(False)]

    # Pivot — keep reporting_period for occupancy as a diagnostic column
    occ_df = df[df["source_dir"] == "occupancy"][["year", "value", "reporting_period"]].rename(
        columns={"value": "occupancy_pct", "reporting_period": "reporting_period_occupancy"}
    )
    nights_occ = df[df["source_dir"] == "nights_occupied"][["year", "value"]].rename(
        columns={"value": "nights_occupied_k"}
    )
    nights_avail = df[df["source_dir"] == "nights_available"][["year", "value"]].rename(
        columns={"value": "nights_available_k"}
    )

    wide = (
        occ_df
        .merge(nights_occ, on="year", how="outer")
        .merge(nights_avail, on="year", how="outer")
        .sort_values("year")
        .reset_index(drop=True)
    )

    if "nights_occupied_k" in wide.columns and "nights_available_k" in wide.columns:
        wide["occ_calculated"] = (
            wide["nights_occupied_k"] / wide["nights_available_k"] * 100
        ).round(1)

    return wide

