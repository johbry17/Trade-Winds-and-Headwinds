# Trade Winds & Headwinds
## Twenty-Five Years of Tourism and Economic Change in the U.S. Virgin Islands (2000–2025)

A rigorous, reproducible exploratory data analysis of the USVI tourism economy, tracing the territory through two major shocks — Hurricanes Irma and Maria (2017) and COVID-19 (2020) — and the recoveries that followed.

---

## Research Question

> **How has the USVI tourism economy changed over approximately 25 years, how did it respond to two major shocks, and what does the subsequent recovery look like across visitor activity, employment, business capacity, and economic output?**

---

## Project Structure

```
trade-winds-headwinds/
├── README.md
├── requirements.txt          # Python dependencies
├── _quarto.yml               # Quarto website configuration
├── data/
│   ├── raw/                  # Immutable source files — do not modify
│   ├── interim/              # Clean intermediate datasets (generated)
│   └── processed/            # Final analytical datasets (generated)
├── notebooks/
│   ├── 01_data_inventory.ipynb   # Phase 1: audit, profiling, validation
│   ├── 02_tourism.ipynb          # Phase 3: visitor activity EDA
│   ├── 03_employment.ipynb       # Phase 3: employment EDA
│   ├── 04_accommodation_capacity.ipynb
│   ├── 05_economic_context.ipynb
│   └── 06_recovery_comparisons.ipynb
├── src/
│   ├── acquisition.py        # Source provenance and download helpers
│   ├── cleaning.py           # Per-source data loaders and cleaners
│   ├── validation.py         # Cross-source checks and data-quality log
│   └── charts.py             # Reusable Plotly charting functions
├── reports/
│   ├── index.qmd             # Field Note (public-facing)
│   ├── eda.qmd               # Analytical companion
│   ├── data-dictionary.qmd
│   ├── methodology.qmd
│   └── custom.scss
├── figures/
│   └── publication/          # Final charts only (not every exploratory figure)
└── docs/                     # Quarto website output
```

---

## Data Sources

| Source | File(s) | Coverage | Notes |
|---|---|---|---|
| USVIBER Tourism Indicators | `TOUR20-revised.pdf`, `TOUR22.pdf`, `TOUR24.pdf` | 2000–2024, annual | Primary tourism statistics source |
| FRED Employment | `fred_SMS*.csv`, `fred_SMU*.csv` | 1990–2026, monthly | Leisure & Hospitality, thousands |
| NPS IRMA | `VIIS_*.csv`, `BUIS_*.csv` | 1957/1962–2025, annual + monthly | Park visitation, not territory-wide arrivals |
| World Bank | `VIR.ST.INT.*.json` | 1995–2020, annual | Secondary cross-check; 2020 anomaly flagged |
| U.S. Census | `2007_IA*`, `IA12*`, `IA17*`, `IA22*` | 2002, 2007, 2012, 2017, 2022 | Establishments, employment, payroll, guestrooms |
| BEA | `vigdp0624.xlsx` | 2002–2022 (GDP), 2002–2021 (industry) | GDP and accommodation value added |
| USVIBER CPI | `Econ21.pdf` | 2009–2021 | **Coverage gap post-2021; no reliable deflator beyond 2021** |

---

## Key Data Quality Issues

| Severity | Issue |
|---|---|
| HIGH | World Bank arrivals 2020 = 8.6M (set to NaN; physically impossible) |
| HIGH | VIIS monthly 2026 data anomalously high (100k+/month vs. 40–55k in 2025) |
| MEDIUM | USVIBER 2020 air excursionists = 2000 value (identical; verify) |
| MEDIUM | Census 2017 guestroom count reflects Dec 31, 2017 post-hurricane conditions |
| MEDIUM | Census RMRTRAN inconsistent in NAPCS Total vs. room-product rows |
| MEDIUM | USVIBER excursionists ≠ sum of air + cruise for 2000 and 2010 (rounding or definition) |
| LOW | USVI CPI 2018 drop anomalous (130.0 → 99.8); verify before deflating |

See `notebooks/01_data_inventory.ipynb` and `src/validation.py` for the full data-quality log.

---

## Environment

**Python 3.10** via conda (`dev` environment).

```bash
pip install -r requirements.txt
```

**Quarto** (for publication): [install from quarto.org](https://quarto.org/docs/get-started/).

```bash
quarto preview   # live preview at localhost
quarto render    # build to docs/
```

---

## Analysis Phases

| Phase | Status | Description |
|---|---|---|
| 1 — Audit & Setup | ✅ Complete | Data inventory, quality log, interim datasets, project scaffolding |
| 2 — Data Preparation | 🔲 Next | Cleaning scripts, Census crosswalk, aggregation validation |
| 3 — Exploratory Analysis | 🔲 | Six-section EDA notebooks |
| 4 — Publication Foundation | 🔲 | Quarto site, styling, navigation |
| 5 — Findings & Field Note | 🔲 | Selected charts, concise narrative |

---

## Data Links

- [FRED: L&H Employment SA](https://fred.stlouisfed.org/series/SMS78000007000000001)
- [FRED: L&H Employment NSA](https://fred.stlouisfed.org/series/SMU78000007000000001)
- [BLS: Quarterly Census of Employment and Wages (QCEW)](https://www.bls.gov/cew/) — Annual employment, establishments, payroll, and wage data for USVI accommodation and food services (NAICS 72, 721, 722), 2000–2025.
- [USVIBER Tourism Indicator 2024](https://usviber.org/document/usvi-tourism-indicator-2024/)
- [USVIBER Tourism Indicator 2022](https://usviber.org/wp-content/uploads/2023/12/Tourism-indicator-2022-12-28-23-1.pdf)
- [USVIBER Tourism Indicator 2020](https://usviber.org/wp-content/uploads/2022/04/TOUR20-revised.pdf)
- [USVIBER Archived Data (CPI)](https://usviber.org/archived-data/)
- [Economic Census 2022](https://www.census.gov/data/tables/2022/econ/economic-census/virgin-islands.html)
- [Economic Census 2017](https://www.census.gov/data/tables/2017/econ/economic-census/virgin-islands.html)
- [Economic Census 2012](https://www.census.gov/data/tables/2012/econ/census/virgin-islands.html)
- [Economic Census 2007](https://www.census.gov/data/tables/2007/econ/census/virgin-islands.html)
- [BEA GDP for USVI](https://www.bea.gov/data/gdp/gdp-us-virgin-islands-usvi)
- [World Bank Tourism Receipts](https://api.worldbank.org/v2/country/VI/indicator/ST.INT.RCPT.CD?format=json)
- [World Bank Tourism Arrivals](https://api.worldbank.org/v2/country/VI/indicator/ST.INT.ARVL?format=json)
- [NPS Visitor Use Stats](https://irma.nps.gov/Stats/)
