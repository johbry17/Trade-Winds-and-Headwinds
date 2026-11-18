# Archived USVIBER Hotel PDF Extraction

This folder preserves an earlier automated workflow for extracting annual hotel statistics from USVIBER PDF reports.

## Contents

- `hotel_extraction.py` — original PDF extraction, parsing, and selection code.
- `hotel_source_observations.csv` — extracted observations from individual PDF reports.
- `hotel_selected.csv` — observations selected by the original automated selection rules.
- `hotel_annual_total_vs_ytd.csv` — comparison of Annual Total and Year-to-Date observations.
- `hotel_conflict_log.csv` — conflicting values identified across report vintages.

## Superseded workflow

This extraction workflow has been retired. Its outputs are retained for reference and provenance, but are no longer the authoritative hotel dataset.

The automated extraction and selection process proved insufficiently reliable for a small collection of reports with changing layouts, overlapping reporting years, revised historical values, and differences between annual aggregate rows.

In particular, the selection logic could not reliably establish which observation represented the preferred annual value. Some extracted observations also required manual verification against the source PDFs.

## Current data

The replacement datasets are manually curated CSVs stored in:

`data/raw/USVIBER-Hotel/`

- `raw_available.csv` — annual room nights available.
- `raw_occupied.csv` — annual room nights occupied.
- `raw_occupancy.csv` — annual reported occupancy rates.

These files retain the source PDF filename, reporting year, prior-year value, and current-year value.

The current analysis uses the manually curated files through `load_hotel_annual()` in `src/hotel_extraction.py`. The archived extraction script should not be used to regenerate or overwrite the current datasets.

## Important caveats

- The archived CSVs contain extracted observations, not a verified final dataset.
- Report vintages sometimes revise previously reported annual values. Differences between a report's current-year value and a subsequent report's prior-year value should not automatically be treated as transcription errors.
- Annual Total and Year-to-Date December occupancy figures are distinct measures. The archived script's explanations of their underlying methodology should not be treated as established facts without supporting documentation.
- The PDF hotel series and the USVIBER Annual Tourism Indicator are retained as separate measures. Their differences should be described without assuming an undocumented explanation for the difference in coverage or methodology.

**Status:** Archived and superseded by manually curated annual CSVs.