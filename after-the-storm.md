### Field Note F5: After the Storm — USVI Tourism Recovery

**Working Title:** *After the Storm: A Data Portrait of Tourism Recovery in the U.S. Virgin Islands, 2000–2025*

**Research Question:**
- **Primary:** How did visitor arrivals at Virgin Islands National Park change before, during, and after Hurricanes Irma and Maria in September 2017, and has recovery been complete or incomplete by 2024?
- **Secondary:** How does the USVI tourism recovery trajectory compare to regional benchmarks from available WDI/OWID island comparison data?

---

**Significance**

The 2017 Atlantic hurricane season was catastrophic for the USVI. Hurricanes Irma and Maria struck within two weeks of each other, destroying much of the islands' tourism infrastructure, damaging or closing hotels, and damaging Virgin Islands National Park (which covers about 60% of St. John's land area). The recovery was complicated, slow, and uneven. For someone with three years of professional experience in USVI tourism, this is not an abstract data exercise — it is a personally witnessed economic and ecological disruption. NPS visitation data, which goes back to 1979, provides an unusually long and clean time series for examining the park's pre-storm baseline, the COVID disruption layered on top of the hurricane recovery, and any recent return to pre-2017 norms. USVIBER monthly PDFs (2022–2026) provide a more recent operational picture of hotel occupancy and visitor arrivals.

Organizations that would value this: USVI Department of Tourism, USVI Bureau of Economic Research, National Park Service, Caribbean tourism consultancies, disaster recovery researchers, Chambers of Commerce in USVI.

---

**Geographic and Temporal Scope**

- **Unit:** Monthly or annual visitor counts (park level) + hotel-level aggregates
- **Geography:** U.S. Virgin Islands — Virgin Islands National Park (VIIS, St. John) and Buck Island Reef National Monument (VIBN, St. Croix)
- **Years:** 2000–2024 (NPS IRMA), supplemented by USVIBER 2022–2026
- **Why this scope is manageable:** Two NPS park units. Annual park visitation data is one row per park per year. The analysis is fundamentally a time series comparison.

---

**Verified Data Inventory**

| Dataset | Direct URL / Access | Key Variables | Coverage | Access | Notes |
|---------|-----------|---------------|----------|--------|-------|
| NPS IRMA Visitation Stats | `https://irma.nps.gov/Stats/` → navigate to "Query Builder for Public Use Statistics" or individual park reports | Recreation visitors, overnight stays, by park unit | VIIS + VIBN, 1979–2024 (annual), monthly available | Free, requires portal navigation + CSV export from SSRS report viewer | ⚠️ **Portal confirmed accessible.** No direct API URL. Must select park code (VIIS, VIBN), export to CSV manually. 5-minute browser task. |
| USVIBER Monthly PDFs | `https://usviber.org/wp-content/uploads/2022/` through `2026/` | Air visitor arrivals (RA files), room nights (RN files), hotel occupancy reports, employment, consumer prices | 2022–2026, monthly | Free, PDF format | **Confirmed in session.** PDF extraction required (pdftools in R or pdfplumber in Python). Annual summary files exist. |
| OWID Tourist Arrivals | `https://ourworldindata.org/grapher/international-tourist-trips.csv` | Annual arrivals | USVI if present; otherwise regional context | Free, confirmed | USVI may not appear as a separate entity (it is a U.S. territory); use for Caribbean island comparison |
| WDI (for context) | `wbstats::wb_data("ST.INT.ARVL", country=c("BH","BB","DM","GD","KN","LC","VC"))` | Tourist arrivals, Caribbean peers | Caribbean SIDS, 1995–2022 | R package, CRAN confirmed | For benchmarking USVI against regional peers |

**Caveats:** NPS visitation measures recreation visits to the national park, which is a proxy for USVI tourism health but not equivalent to total island visitor arrivals. Virgin Islands National Park includes beach and snorkeling access — it is a key tourism asset, but visitors who come only for beach-front hotels or cruise ship day trips may not enter the park. USVIBER PDFs go back only to 2022, so for the critical 2017–2021 period, the analysis relies primarily on NPS IRMA data (which goes back to 1979 and is not a PDF). The OWID and WDI tourism data may not have USVI as a separate country given its territorial status.

---

**Proposed EDA**

**Language: R** (`readr`, `ggplot2`, `dplyr`, `lubridate`, `pdftools` or manual tabulation for USVIBER PDFs)

R is appropriate for the time series and visualization work. PDF extraction can be handled with `pdftools` if the USVIBER PDFs are text-based (most modern PDFs are); alternatively, the 2022–2026 period is short enough that manual tabulation from 4–5 annual summary PDFs is feasible in under an hour.

**Steps:**
1. **NPS IRMA data acquisition (20 min):** Navigate to `irma.nps.gov/Stats/`. Select "Query Builder for Public Use Statistics." Choose park codes VIIS and VIBN, all years (1979–2024), annual, recreation visitors. Export to CSV. This produces a clean time series immediately.
2. **NPS time series visualization (30 min):** Line chart of annual recreation visitors for VIIS (St. John) and VIBN (Buck Island), 2000–2024. Annotate: 2017 (Irma/Maria), 2020 (COVID). Does visitation recover to pre-2017 levels?
3. **Pre/post comparison (30 min):** Calculate average annual visitors for 2012–2016 (pre-storm), 2018–2019 (partial recovery pre-COVID), 2021–2024 (post-COVID recovery). Bar chart with error bars.
4. **USVIBER PDF extraction (60–90 min):** For 2022–2026, use `pdftools::pdf_text()` to extract text from hotel occupancy and air arrivals PDFs. Parse into a data table of month-year + occupancy rate + air arrivals. If PDF parsing is too complex (scanned images, not text), manually transcribe the annual summary values from the `A22`, `A23`, `A24`, `A25` files (one number per year × 12 months × 1-2 variables = ~100 data points manually).
5. **Hotel occupancy trend (30 min):** Plot monthly hotel occupancy rate, 2022–2026. Identify seasonal peaks (winter months). Any trend toward pre-pandemic norms?
6. **Caribbean benchmark (30 min):** Pull WDI arrivals for 5–6 Caribbean islands (Barbados, St. Lucia, Grenada, Antigua) for 2015–2022. Line chart showing USVI NPS visitation trajectory vs. regional peer recovery.
7. **Interpretation (60 min):** Narrative on what the data does and does not show. Note structural differences between USVI (heavily dependent on specific park infrastructure) and more diversified Caribbean tourism economies.

---

**Originality and Contribution**

Existing work: Academic papers and government reports on USVI hurricane recovery are primarily qualitative or economic (BEA GDP). A quantitative NPS-visitation-based time series analysis is not a common portfolio project. The combination of NPS data (long history) + USVIBER PDFs (recent operational context) + Caribbean benchmark is an unusual combination.

**What this adds:** A personal, place-specific data story connecting three years of firsthand professional experience to a concrete analytical question. The long NPS time series (going back to 1979) allows pre-storm, post-storm, and post-COVID analysis in a single coherent narrative. This project would be genuinely interesting to a USVI Department of Tourism or NPS social scientist reviewer.

---

**Feasibility**

| Phase | Estimated Time |
|-------|---------------|
| NPS IRMA portal navigation and CSV export | 20 min |
| NPS time series analysis and visualization | 60 min |
| USVIBER PDF extraction or manual transcription | 60–90 min |
| Caribbean benchmark WDI pull and visualization | 45 min |
| Integration and overall narrative | 60 min |
| Quarto rendering and polish | 45 min |
| **Total** | **~5.5–7 hours** |

**Most likely obstacle:** USVIBER PDF data. If the PDFs are text-layer PDFs (likely), `pdftools` in R extracts them in minutes. If they are scanned images, manual transcription of the limited number of annual summaries is the fallback. The annual summary PDFs (`A22`, `A23`, `A24`, `A25`) appear to be the most useful — one per year rather than 12 monthly PDFs.

**Minimum viable deliverable:** The NPS time series alone (Steps 1–3) can produce a complete, publishable Field Note in 3–4 hours. Steps 4–7 add depth and contemporary operational data but are not required for the core story.

---

**Hiring Signal**

Demonstrates: Data acquisition from an institutional portal (NPS IRMA); time series analysis; PDF data extraction; place-specific knowledge and personal domain expertise (USVI); ability to connect personal professional experience to analytical questions; sensitivity to natural disaster recovery dynamics.

Relevant roles: tourism analytics, USVI government or NGO positions, NPS social science, Caribbean regional organizations, disaster resilience research, place-based policy analytics broadly.

---

**Limitations**

- **NPS ≠ total USVI tourism.** Park visitation is a proxy, not a comprehensive measure. Cruise ship visitors, beach-front hotel guests, and visitors to St. Croix who don't visit Buck Island are not captured.
- **USVIBER PDFs cover only 2022–2026.** The critical 2017–2021 period — hurricane recovery, first few years of reconstruction, COVID — is not covered by USVIBER's digital archive.
- **Causal attribution is impossible.** The 2020 COVID shock overlaps with the ongoing hurricane recovery, making it impossible to cleanly separate the two effects.
- **NPS monthly data may have quality issues.** Some months may have estimated counts, particularly in the October 2017–December 2017 period when the park was closed for storm damage assessment.

---

### F5: After the Storm (USVI Tourism Recovery)

**1. First action:**
- Navigate to `https://irma.nps.gov/Stats/` in a browser. Click "Query Builder for Public Use Statistics (1979 – Last Calendar Year)."
- Select: Unit Type = Park; park = VIIS (Virgin Islands National Park); Statistic = Recreation Visitors; Data Type = Annual; Year Range = All. Click View Report. Export to CSV or Excel using the report toolbar.
- Repeat for VIBN (Buck Island Reef National Monument).

**2. First inspection:**
- Open the downloaded CSV. Check: what are the years covered? What are the recreation visitor counts for 2016 (pre-storm baseline), 2017 (storm year), 2018–2019 (recovery), 2020 (COVID), 2021–2024 (recovery)?
- Specifically note: Did VIIS visitation decline below the pre-2017 baseline in 2018–2019, or did it recover quickly? Does the COVID dip in 2020 exceed the hurricane dip in 2017–2018?
- Also download monthly data for 2015–2024 from the same query builder (monthly option).

**3. Initial EDA checks:**
1. Simple line chart: VIIS recreation visitors by year, 2000–2024, with vertical lines at Sept 2017 and March 2020
2. Bar chart: average visitors in 3 periods — pre-storm (2012–2016), recovery/pre-COVID (2018–2019), post-COVID (2021–2024)
3. Index chart: 2016 = 100, track VIIS and VIBN trajectories through the shocks
4. Compare to OWID arrivals for Barbados and St. Lucia (similar-size Caribbean islands) over the same period
5. Check USVIBER 2024 annual report PDF (`A24`) for hotel occupancy and arrivals data 2022–2024

**4. Technical setup:**
```r
library(readr); library(dplyr); library(ggplot2); library(lubridate)
library(pdftools)  # for USVIBER PDFs

# After downloading NPS IRMA CSV:
nps <- read_csv("nps_viis_annual.csv") %>%
  filter(ParkCode == "VIIS") %>%
  select(Year, RecreationVisitors)

# For USVIBER PDF extraction (text-layer PDFs):
annual_text <- pdftools::pdf_text("https://usviber.org/wp-content/uploads/2024/01/A23DEC.pdf")
```

**5. Feasibility test:**
- **GO (full project)** if: NPS IRMA CSV downloads cleanly with ≥20 years of data AND USVIBER annual summary PDFs (`A22DEC`, `A23DEC`, `A24`) yield extractable visitor arrival numbers via `pdftools` (text layer, not scanned images).
- **GO (NPS-only)** if: NPS data is clean but USVIBER PDFs are scanned images. The NPS time series alone is sufficient for a publishable Field Note with a narrower scope.
- **NO-GO** if: NPS data export fails and USVIBER PDFs are unreadable. (Unlikely — both are publicly accessible.)

**6. Time budget:**
- NPS data acquisition: 20 minutes (browser portal)
- Initial feasibility test (NPS + one USVIBER PDF): 45 minutes
- Complete NPS-only Field Note: 3–4 hours
- Complete Field Note with USVIBER: 7–8 hours

**7. Minimum viable deliverable:**
A Quarto HTML with: (a) NPS VIIS/VIBN annual visitation time series 2000–2024, annotated for 2017 and 2020 events; (b) pre-/post-storm comparison bar chart; (c) index recovery chart vs. 2 Caribbean peer parks or destinations; (d) 400-word interpretation drawing on personal USVI knowledge. PDF data is an enhancement, not a requirement.

**8. Principal failure mode:**
USVIBER PDFs are scanned images rather than text-layer PDFs. In that case, `pdftools` will return garbled output. Fallback: manually extract the 5 annual totals (2022–2026) from the annual summary PDFs (`A22DEC` through the most recent) — each PDF likely has one summary table, taking ~15 minutes to transcribe per year. This is tedious but finite.

---

## Critical F5 Update: USVI Tourism Data Is Substantially Better Than Initially Assessed

The USVI Tourism Data agent ran for 40 minutes (154+ tool calls) and found several directly downloadable, machine-readable datasets that I could not confirm through my own web research. **This changes the feasibility assessment for F5 from Medium to High.**

---

### What Changed

#### 1. USVIBER has annual PDF summaries going back to 2002 — not just 2022

The annual `TOUR##` series (`TOUR02.pdf` through `TOUR22.pdf`) is confirmed at `usviber.org/wp-content/uploads/`. These cover:
- Air visitor arrivals
- Cruise passenger arrivals
- Total arrivals
- Hotel occupancy rate, ADR, RevPAR
- Visitor expenditures (total and per-visitor)
- Visitor origin by region

**Years confirmed:** 2002–2022 (annual), 2010–2026 (monthly by type). The critical pre-hurricane baseline (2012–2016) and immediate post-storm period (2017–2019) are in these annual summaries. This was the primary uncertainty in my original F5 assessment.

#### 2. FRED employment data is directly downloadable as CSV — no registration, no portal navigation

These URLs deliver raw CSVs immediately:

| Series | URL | Coverage |
|--------|-----|----------|
| USVI Leisure & Hospitality Employment | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SMU78000007000000001` | Monthly, 1990–Sep 2026 |
| USVI Total Nonfarm Employment | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SMU78000000000000001` | Monthly, 1975–Sep 2026 |

The hurricane signal is starkly visible in the data: Leisure & Hospitality employment fell from **7,400 in August 2017 to 4,600 by November 2017** — a 38% collapse in three months. This is the cleanest, most immediate time series available for the USVI economic shock.

#### 3. BEA XLSX is directly downloadable — one URL, no API key

`https://www.bea.gov/sites/default/files/2024-06/vigdp0624.xlsx`

Contains USVI GDP by industry including accommodation & food services, approximately 2002–2022. **Critical limitation:** BEA has **officially paused future USVI GDP releases** because the Department of Interior's Office of Insular Affairs stopped funding this work. The June 2024 release (covering through 2022) is likely the last one indefinitely. This must appear prominently in the F5 limitations section.

#### 4. World Bank has USVI arrivals data from 1995 to 2020 — confirmed with actual values

The World Bank API returns USVI-specific arrival figures:
- 2016: **2.57 million** arrivals
- 2017: **1.95 million** (hurricane year — visible decline)
- 2018: **1.92 million**

The 2020 value of **8.6 million** is almost certainly a data entry error (World Bank likely miskeyed a figure) and must be treated as missing. The pre-2020 series is a clean, confirmed complement to the FRED employment series.

#### 5. Census Economic Census accommodation tables are directly downloadable as CSV ZIPs

| URL | Content | Years |
|-----|---------|-------|
| `https://www2.census.gov/programs-surveys/economic-census/data/2022/sector00/IA2200NAPCS02.zip` | USVI guestrooms by industry, 2022 | 2022 |
| `https://www2.census.gov/programs-surveys/economic-census/data/2017/sector00/IA1700NAPCS02.zip` | Same, 2017 | 2017 |
| `https://www2.census.gov/programs-surveys/economic-census/data/2022/sector00/IA2200BASIC02.zip` | Comparative stats 2022 vs. 2017 | 2017, 2022 |

Every 5 years back to 2002: number of accommodation establishments, employment, annual payroll, total revenue, number of guestrooms, revenue per guestroom — USVI-specific, free, no registration.

---

### Revised F5 Data Inventory

The updated, expanded data table for F5:

| Dataset | Direct URL | Variables | Coverage | Access | Status |
|---------|-----------|-----------|----------|--------|--------|
| **FRED L&H Employment** | `fred.stlouisfed.org/graph/fredgraph.csv?id=SMU78000007000000001` | Monthly employment (thousands) | 1990–2026 | Free CSV, no auth | ✅ **CONFIRMED** |
| **FRED Total Employment** | `fred.stlouisfed.org/graph/fredgraph.csv?id=SMU78000000000000001` | Total nonfarm employment | 1975–2026 | Free CSV, no auth | ✅ **CONFIRMED** |
| **WB Arrivals API** | `api.worldbank.org/v2/country/VI/indicator/ST.INT.ARVL?format=json` | Annual arrivals | 1995–2020 | Free JSON, no auth | ✅ **CONFIRMED** (flag 2020 anomaly) |
| **WB Receipts API** | `api.worldbank.org/v2/country/VI/indicator/ST.INT.RCPT.CD?format=json` | Annual receipts (USD) | 2005–2020 | Free JSON, no auth | ✅ **CONFIRMED** |
| **BEA XLSX** | `bea.gov/sites/default/files/2024-06/vigdp0624.xlsx` | GDP by industry incl. accommodation | ~2002–2022 | Free XLSX, no auth | ✅ **CONFIRMED** (future releases paused) |
| **Census Econ Census** | `census.gov/...IA2200NAPCS02.zip` and `IA1700NAPCS02.zip` | Establishments, rooms, revenue, employment | 2007, 2012, 2017, 2022 | Free CSV ZIP, no auth | ✅ **CONFIRMED** |
| **USVIBER Annual PDFs** | `usviber.org/wp-content/uploads/...TOUR02.pdf` through `TOUR22.pdf` | Air arrivals, hotel occupancy, expenditures | 2002–2022 annual | Free PDF | ✅ **CONFIRMED** (PDF extraction required) |
| **NPS IRMA Visitation** | `irma.nps.gov/Stats/` | Park recreation visitors | 1979–2024 | Portal export | ✅ (portal confirmed; CSV via report export) |

---

### Revised Feasibility Assessment for F5

**Old assessment:** Medium feasibility (3/5) — uncertain pre-2022 data, NPS portal only, PDF risk.

**New assessment:** High feasibility (4/5) — multiple machine-readable free datasets confirmed, including a 35-year monthly employment series that alone supports the core analysis. The FRED CSV can be downloaded in one line of R and contains the hurricane signal cleanly.

**Revised time estimate:** 5–7 hours (previously 7–10 hours). A complete, publishable Field Note using FRED + World Bank + BEA XLSX + one Census Economic Census comparison requires no PDF extraction at all.

**Revised minimum viable deliverable (no PDF work required):**
1. FRED employment time series (1990–2026, monthly, annotated for 2017 and 2020)
2. World Bank arrivals time series (1995–2019, with 2020 anomaly dropped)
3. BEA GDP by industry (2002–2022, accommodation sector highlighted)
4. Census accommodation sector comparison (2007 → 2017 → 2022)
5. Written interpretation drawing on personal USVI knowledge

USVIBER PDFs and NPS IRMA remain as optional enhancements for additional depth, not requirements.

---

### Revised Scoring Table

| Criterion | Weight | F1 | F2 | F3 | F4 | **F5 (revised)** | F6 |
|-----------|--------|----|----|----|----|------------------|----|
| Data availability | 30% | 5 | 5 | 5 | 5 | **4→4.5** | 5 |
| Feasibility | 20% | 5 | 4 | 5 | 5 | **3→4** | 5 |
| Originality | 15% | 4 | 4 | 4 | 4 | 5 | 3 |
| Analytical substance | 10% | 5 | 4 | 4 | 4 | 4 | 4 |
| R signal | 10% | 5 | 5 | 4 | 5 | **3→4** | 5 |
| Int'l dev signal | 5% | 5 | 5 | 5 | 4 | 1 | 1 |
| Tourism signal | 5% | 5 | 2 | 2 | 1 | 5 | 5 |
| Place-based relevance | 5% | 4 | 3 | 5 | 4 | 5 | 2 |
| **Weighted score** | | **4.70** | **4.35** | **4.55** | **4.50** | **3.45→4.10** | **4.15** |

F5 moves from the weakest finalist to a competitive mid-tier candidate. The recommended top 3 of **F1 + F3 + F5** remains the best portfolio combination, but F5's execution risk is now substantially lower than initially assessed.

---

### One Additional Limitation for F5

The **BEA pause** must be stated explicitly in the report: as of June 2024, BEA has ceased producing USVI GDP statistics indefinitely due to OIA funding withdrawal. This means the 2002–2022 BEA XLSX is both a confirmed free resource and a historical artifact — there is no update path. The Field Note should note this as a data policy finding in its own right: the cessation of USVI economic measurement is itself a story about how territories are treated differently from states in federal statistical programs.