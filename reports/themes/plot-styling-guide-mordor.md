## Mordor Theme Palettes

The Mordor pair carries the Walk to Mordor interface colors into Field Notes:
ember orange, slate blue, moss green, and antique gold. The light palette uses
darker equivalents for legibility on parchment; the dark palette stays close to
the original interface. These are chart colors, not literal page-background
tokens.

```r
# ── Mordor Light ────────────────────────────────────────────────────
pal_mordor_light <- list(
  series1   = "#A65F2E",  # ember / burnt orange
  series2   = "#356779",  # slate blue
  series3   = "#4D7148",  # moss green
  accent    = "#986A22",  # antique gold
  muted     = "#776B5C",
  reference = "#A99D8D",
  bg        = "#EEE7D8",  # aged parchment
  panel     = "#F4EEE2",
  grid      = "#D5CABB",
  text      = "#40382E"
)

# ── Mordor Dark ─────────────────────────────────────────────────────
pal_mordor_dark <- list(
  series1   = "#C17F40",  # ember / burnt orange
  series2   = "#4A7C8E",  # slate blue
  series3   = "#5F8A5A",  # moss green
  accent    = "#D4A853",  # antique gold
  muted     = "#8A7B6A",
  reference = "#51473B",
  bg        = "#0D0B08",  # near-black earth
  panel     = "#13110D",
  grid      = "#2A2520",
  text      = "#D6CBBA"
)
```

## Mordor ggplot2 Theme Functions

Add these alongside the existing theme wrappers. They reuse `make_fn_theme()`
and therefore preserve the same chart layout and semantic color roles.

```r
theme_mordor_light <- function(base_size = 11) {
  make_fn_theme(pal_mordor_light, base_size)
}

theme_mordor_dark <- function(base_size = 11) {
  make_fn_theme(pal_mordor_dark, base_size)
}
```

## Mordor Usage

```r
# Mordor Light
active_pal <- pal_mordor_light
theme_set(theme_mordor_light())

# Mordor Dark
# active_pal <- pal_mordor_dark
# theme_set(theme_mordor_dark())

# Journey colors, if a chart uses the Walk to Mordor journey categories
pal_journeys <- c(
  "Mordor" = active_pal$series1,
  "Return" = active_pal$series2,
  "Hobbit" = active_pal$series3
)
```

For plots with more than three groups, use the three journey colors only for
those named categories. Use a separate qualitative palette for additional
groups rather than assigning extra meanings to these colors.
