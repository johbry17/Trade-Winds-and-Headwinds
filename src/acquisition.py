"""
src/acquisition.py
Data acquisition documentation and helpers.

All raw files are already present in data/raw/.  This module documents their
provenance and provides re-download utilities if files need to be refreshed.
"""

from __future__ import annotations

SOURCES = {
    "fred_sa": {
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SMS78000007000000001",
        "local": "data/raw/fred_SMS78000007000000001.csv",
        "description": "USVI Leisure & Hospitality employment, seasonally adjusted (thousands)",
        "frequency": "monthly",
        "coverage": "1990-01 to 2026-09",
    },
    "fred_nsa": {
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SMU78000007000000001",
        "local": "data/raw/fred_SMU78000007000000001.csv",
        "description": "USVI Leisure & Hospitality employment, not seasonally adjusted (thousands)",
        "frequency": "monthly",
        "coverage": "1990-01 to 2026-09",
    },
    "cpi_us": {
        "url": "https://fred.stlouisfed.org/series/CPIAUCNS",
        "local": "data/raw/CPIAUCNS.csv",
        "description": "U.S. CPI-U, All Items, not seasonally adjusted; BLS source.",
        "frequency": "monthly",
        "coverage": "monthly; downloaded coverage in local file",
        "notes": (
            "Used as a mainland inflation proxy for approximate 2016-dollar "
            "wage measures. Not a USVI-specific price index."
        ),
    },
    "qcew_usvi": {
        "url": "https://www.bls.gov/cew/",
        "local": "data/raw/qcew_usvi_accommodation_food_services_2000_2025.csv",
        "description": (
            "BLS QCEW employment, establishments, payroll, and wages "
            "for USVI accommodation and food services."
        ),
        "frequency": "annual",
        "coverage": "2000–2025",
        "notes": "NAICS 72, 721, and 722.",
    },
    "wb_arrivals": {
        "url": "https://api.worldbank.org/v2/country/VI/indicator/ST.INT.ARVL?format=json&per_page=100",
        "local": "data/raw/VIR.ST.INT.ARVL.json",
        "description": "World Bank: USVI international tourism arrivals",
        "frequency": "annual",
        "coverage": "1995–2020 (non-null)",
        "notes": "2020 value anomalous (8.6M); set to NaN. Local file is single-page export.",
    },
    "wb_receipts": {
        "url": "https://api.worldbank.org/v2/country/VI/indicator/ST.INT.RCPT.CD?format=json&per_page=100",
        "local": "data/raw/VIR.ST.INT.RCPT.CD.json",
        "description": "World Bank: USVI international tourism receipts (current USD)",
        "frequency": "annual",
        "coverage": "1995–2020 (non-null)",
    },
    "tour24": {
        "url": "https://usviber.org/document/usvi-tourism-indicator-2024/",
        "local": "data/raw/TOUR24.pdf",
        "description": "USVIBER Annual Tourism Indicator 2024",
        "frequency": "annual",
        "coverage": "2000, 2010–2024",
    },
    "tour22": {
        "url": "https://usviber.org/wp-content/uploads/2023/12/Tourism-indicator-2022-12-28-23-1.pdf",
        "local": "data/raw/TOUR22.pdf",
        "description": "USVIBER Annual Tourism Indicator 2022",
        "frequency": "annual",
        "coverage": "historical through 2022",
    },
    "tour20": {
        "url": "https://usviber.org/wp-content/uploads/2022/04/TOUR20-revised.pdf",
        "local": "data/raw/TOUR20-revised.pdf",
        "description": "USVIBER Annual Tourism Indicator 2020 (revised)",
        "frequency": "annual",
        "coverage": "historical through 2020",
    },
    "tour10": {
        "url": "https://usviber.org/archived-data/",
        "local": "data/raw/TOUR10.pdf",
        "description": "USVIBER Annual Tourism Indicator 2010.",
        "frequency": "annual",
        "coverage": "historical through 2010",
        "notes": (
            "Used for historical tourism series where later publications "
            "do not provide consistent coverage. Historical figures may "
            "differ from subsequent revisions in TOUR24."
        ),
    },
    "econ21": {
        "url": "https://usviber.org/archived-data/",
        "local": "data/raw/Econ21.pdf",
        "description": "USVIBER Annual Economic Indicators 2021 (includes CPI)",
        "frequency": "annual",
        "coverage": "CPI 2009–2021",
    },
    "hotel_occupancy": {
        "url": "https://usviber.org/archived-data/",
        "local": "data/raw/USVIBER-Hotel/Occupancy/",
        "description": "USVIBER annual hotel occupancy reports.",
        "frequency": "annual",
        "coverage": "2001–2025; gaps in archived reports",
        "notes": "PDF reports; several years have revised editions.",
    },
    "hotel_nights_occupied": {
        "url": "https://usviber.org/archived-data/",
        "local": "data/raw/USVIBER-Hotel/Nights-Occupied/",
        "description": "USVIBER annual hotel room-nights occupied reports.",
        "frequency": "annual",
        "coverage": "2001–2025; gaps in archived reports",
        "notes": "PDF reports; several years have revised editions.",
    },
    "hotel_nights_available": {
        "url": "https://usviber.org/archived-data/",
        "local": "data/raw/USVIBER-Hotel/Nights-Available/",
        "description": "USVIBER annual hotel room-nights available reports.",
        "frequency": "annual",
        "coverage": "2007–2025",
        "notes": "PDF reports; several years have revised editions.",
    },
    "bea_gdp": {
        "url": "https://www.bea.gov/data/gdp/gdp-us-virgin-islands-usvi",
        "local": "data/raw/vigdp0624.xlsx",
        "description": "BEA GDP and industry value added for USVI",
        "frequency": "annual",
        "coverage": "GDP 2002–2022; industry value added 2002–2021",
    },
    "nps_viis_annual": {
        "url": "https://irma.nps.gov/Stats/",
        "local": "data/raw/VIIS Annual Park Recreation Visitation (1904 - Last Calendar Year).csv",
        "description": "NPS annual recreation visitation — Virgin Islands NP (St. John)",
        "frequency": "annual",
        "coverage": "1957–2025",
    },
    "nps_viis_monthly": {
        "url": "https://irma.nps.gov/Stats/",
        "local": "data/raw/VIIS Recreation Visitors By Month (1979 - Last Calendar Year).csv",
        "description": "NPS monthly recreation visitation — Virgin Islands NP (St. John)",
        "frequency": "monthly",
        "coverage": "1979–2026 (partial 2026)",
        "notes": "2026 Jan–Aug show anomalously high counts; investigate before use.",
    },
    "nps_buis_annual": {
        "url": "https://irma.nps.gov/Stats/",
        "local": "data/raw/BUIS Annual Park Recreation Visitation (1904 - Last Calendar Year).csv",
        "description": "NPS annual recreation visitation — Buck Island Reef NM (St. Croix)",
        "frequency": "annual",
        "coverage": "1962–2025 (gap 1999–2001)",
    },
    "nps_buis_monthly": {
        "url": "https://irma.nps.gov/Stats/",
        "local": "data/raw/BUIS Recreation Visitors By Month (1979 - Last Calendar Year).csv",
        "description": "NPS monthly recreation visitation — Buck Island Reef NM (St. Croix)",
        "frequency": "monthly",
        "coverage": "1979–2026 (gap 1999–2001; partial 2026)",
    },
    "census_2007_a01": {
        "url": "https://www.census.gov/data/tables/2007/econ/census/virgin-islands.html",
        "local": "data/raw/2007_IA0700A01_U.S. Virgin Islands/ECN_2007_IA_00A01_with_ann.csv",
        "description": "2007 Economic Census — USVI industry summary (NAICS 2-digit). Also contains 2002.",
        "frequency": "quinquennial",
        "coverage": "2002 and 2007",
    },
    "census_2007_a10": {
        "url": "https://www.census.gov/data/tables/2007/econ/census/virgin-islands.html",
        "local": "data/raw/2007_IA0700A10_U.S. Virgin Islands/ECN_2007_IA_00A10_with_ann.csv",
        "description": "2007 Economic Census — USVI accommodation product breakdown (NAICS 7211). Includes guestrooms.",
        "frequency": "quinquennial",
        "coverage": "2007",
    },
    "census_2012_a02": {
        "url": "https://www.census.gov/data/tables/2012/econ/census/virgin-islands.html",
        "local": "data/raw/IA1200A02/IA1200A02.dat",
        "description": "2012 Economic Census — USVI industry summary (multi-territory pipe-delimited file).",
        "frequency": "quinquennial",
        "coverage": "2012",
    },
    "census_2012_a10": {
        "url": "https://www.census.gov/data/tables/2012/econ/census/virgin-islands.html",
        "local": "data/raw/IA1200A10/",
        "description": ("2012 Economic Census — USVI accommodation industry detail."),
        "frequency": "quinquennial",
        "coverage": "2012",
    },
    "census_2017_basic02": {
        "url": "https://www.census.gov/data/tables/2017/econ/economic-census/virgin-islands.html",
        "local": "data/raw/IA1700BASIC02/IA1700BASIC02.dat",
        "description": "2017 Economic Census — USVI industry summary. Contains both 2012 and 2017.",
        "frequency": "quinquennial",
        "coverage": "2012 and 2017",
        "notes": "2017 data reflects post-hurricane conditions (Sep 2017 hurricanes).",
    },
    "census_2017_napcs02": {
        "url": "https://www.census.gov/data/tables/2017/econ/economic-census/virgin-islands.html",
        "local": "data/raw/IA1700NAPCS02/",
        "description": (
            "2017 Economic Census — USVI accommodation product detail, "
            "including guestroom counts."
        ),
        "frequency": "quinquennial",
        "coverage": "2017",
    },
    "census_2022_basic02": {
        "url": "https://www.census.gov/data/tables/2022/econ/economic-census/virgin-islands.html",
        "local": "data/raw/IA2200BASIC02/IA2200BASIC02.dat",
        "description": "2022 Economic Census — USVI industry summary. Contains both 2017 and 2022.",
        "frequency": "quinquennial",
        "coverage": "2017 and 2022",
    },
    "census_2022_napcs02": {
        "url": "https://www.census.gov/data/tables/2022/econ/economic-census/virgin-islands.html",
        "local": "data/raw/IA2200NAPCS02/",
        "description": (
            "2022 Economic Census — USVI accommodation product detail, "
            "including guestroom counts."
        ),
        "frequency": "quinquennial",
        "coverage": "2022",
    },
}

# ---------------------------------------------------------------------------
# Data gaps and recommended additional collection
# ---------------------------------------------------------------------------

GAPS = [
    {
        "gap": "USVI CPI 2022–2025",
        "impact": "Cannot deflate monetary series (visitor expenditures, BEA value added) post-2021",
        "suggested_action": (
            "Contact USVIBER directly (340-693-4375) for updated CPI tables. "
            "As fallback, investigate using U.S. national CPI with explicit caveats."
        ),
    },
    {
        "gap": "BUIS annual/monthly 1999–2001",
        "impact": "Three years of data missing from Buck Island Reef NM series",
        "suggested_action": "No action required; the data does not exist in the source.",
    },
    {
        "gap": "VIIS 2026 methodology changed",
        "impact": "Cannot use 2026 partial-year data for trend analysis",
        "suggested_action": ("Exclude 2026; use prior years for trend analysis."),
    },
    {
        "gap": "BEA industry data 2022+",
        "impact": "Industry value-added breakdown ends 2021; GDP totals end 2022",
        "suggested_action": (
            "BEA discontinued regular territory GDP updates in 2022 when ODI funding ended. "
            "No further data expected without new federal appropriation."
        ),
    },
    {
        "gap": "World Bank arrivals/receipts 2021+",
        "impact": "Secondary cross-check series ends 2020",
        "suggested_action": "No action required; USVIBER is the primary source.",
    },
]
