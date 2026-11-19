# Field Notes Plot Styling Guide

Conventions and R/ggplot2 code for styling charts in the Field Notes publication series.

Each of the six themes has a matched plot palette and ggplot2 theme function. The goal is consistency between page design and chart aesthetics — chart colors should feel deliberate within the page, not accidentally dropped in from a default palette.

---

## Semantic Color Roles

Each theme defines the same six semantic roles, expressed in theme-appropriate colors.

| Role | Meaning | Example use |
|------|---------|------------|
| `col_series1` | Primary data series | Main comparison group |
| `col_series2` | Secondary data series | Comparison group |
| `col_series3` | Tertiary data series | Third group (Caribbean / Pacific / AIMS) |
| `col_accent` | Annotation, highlight | Callout point, reference line annotation |
| `col_muted` | Supporting data | Historical baseline, secondary lines |
| `col_reference` | Reference / zero line | Zero line, threshold |

Do not communicate meaning through color alone. Use shape, label, and position redundantly where possible.

---

## Theme Palettes

```r
# ── Archipelago Light ───────────────────────────────────────────────
pal_archipelago_light <- list(
  series1   = "#1a3a52",   # deep navy
  series2   = "#2d7d8e",   # sea-glass teal
  series3   = "#c0634a",   # muted coral
  accent    = "#c0634a",   # same coral for highlight
  muted     = "#a0968a",   # warm grey
  reference = "#7a7368",   # muted warm
  bg        = "#f4f1eb",   # limestone
  panel     = "#f4f1eb",
  grid      = "#ddd8d0",
  text      = "#252320"
)

# ── Archipelago Dark ────────────────────────────────────────────────
pal_archipelago_dark <- list(
  series1   = "#5bbcc9",   # sea-glass teal
  series2   = "#d4845e",   # warm coral
  series3   = "#7ab8c8",   # lighter teal
  accent    = "#d4845e",   # coral
  muted     = "#7a7068",
  reference = "#5a5248",
  bg        = "#0d1e2b",   # deep ocean night
  panel     = "#132535",
  grid      = "#1f3348",
  text      = "#ddd8d0"
)

# ── Field Journal Light ─────────────────────────────────────────────
pal_field_journal_light <- list(
  series1   = "#2c4a2e",   # forest green
  series2   = "#9b4b1f",   # rust
  series3   = "#5e7a53",   # sage
  accent    = "#b8832a",   # ochre
  muted     = "#9a8a78",
  reference = "#7a6e60",
  bg        = "#f6f1e7",   # parchment
  panel     = "#f6f1e7",
  grid      = "#d8d0c0",
  text      = "#231c10"
)

# ── Field Journal Dark ──────────────────────────────────────────────
pal_field_journal_dark <- list(
  series1   = "#8fbc72",   # sage green
  series2   = "#c8824a",   # ochre/rust
  series3   = "#a8c590",   # lighter sage
  accent    = "#c8824a",   # ochre
  muted     = "#7a6e58",
  reference = "#5a5244",
  bg        = "#18160f",
  panel     = "#221e14",
  grid      = "#2e2920",
  text      = "#e4ddd1"
)

# ── Observatory Light ───────────────────────────────────────────────
pal_observatory_light <- list(
  series1   = "#1e52a0",   # cobalt
  series2   = "#c94820",   # burnt orange
  series3   = "#2a7f52",   # steel green
  accent    = "#c94820",   # burnt orange
  muted     = "#8a9ab0",
  reference = "#6a7a8a",
  bg        = "#f7f8fa",
  panel     = "#f7f8fa",
  grid      = "#dde1e7",
  text      = "#1a1d22"
)

# ── Observatory Dark ────────────────────────────────────────────────
pal_observatory_dark <- list(
  series1   = "#4c8de0",   # medium cobalt
  series2   = "#e56030",   # brighter burnt orange
  series3   = "#4ab87a",   # lighter steel green
  accent    = "#e56030",   # orange
  muted     = "#5a6a7a",
  reference = "#3a4a5a",
  bg        = "#111419",
  panel     = "#191d24",
  grid      = "#252a35",
  text      = "#e2e6ed"
)
```

---

## ggplot2 Theme Functions

One function per theme variant. Each returns a complete `ggplot2::theme()` call.

```r
library(ggplot2)

# ── Helper: apply a full theme from a palette list ─────────────────
make_fn_theme <- function(pal, base_size = 11) {
  theme_minimal(base_size = base_size) +
    theme(
      text             = element_text(color = pal$text),
      plot.background  = element_rect(fill = pal$panel, color = NA),
      panel.background = element_rect(fill = pal$panel, color = NA),
      panel.grid.major = element_line(color = pal$grid, linewidth = 0.5),
      panel.grid.minor = element_blank(),
      axis.text        = element_text(color = pal$text, size = rel(0.85)),
      axis.title       = element_text(color = pal$text, size = rel(0.9)),
      plot.title       = element_text(color = pal$text, face = "bold",
                                      size = rel(1.2), margin = margin(b = 4)),
      plot.subtitle    = element_text(color = pal$muted, size = rel(1.0),
                                      margin = margin(b = 8)),
      plot.caption     = element_text(color = pal$muted, size = rel(0.72),
                                      hjust = 0, margin = margin(t = 8)),
      legend.background = element_rect(fill = pal$panel, color = NA),
      legend.key        = element_rect(fill = pal$panel, color = NA),
      legend.text       = element_text(color = pal$text, size = rel(0.85)),
      legend.title      = element_text(color = pal$text, size = rel(0.85),
                                       face = "bold"),
      strip.text        = element_text(color = pal$text, face = "bold",
                                       size = rel(0.9)),
      strip.background  = element_rect(fill = pal$grid, color = NA),
      plot.margin       = margin(14, 16, 10, 14)
    )
}

# ── Six theme functions ─────────────────────────────────────────────
theme_archipelago_light <- function(base_size = 11)
  make_fn_theme(pal_archipelago_light, base_size)

theme_archipelago_dark <- function(base_size = 11)
  make_fn_theme(pal_archipelago_dark, base_size)

theme_field_journal_light <- function(base_size = 11)
  make_fn_theme(pal_field_journal_light, base_size)

theme_field_journal_dark <- function(base_size = 11)
  make_fn_theme(pal_field_journal_dark, base_size)

theme_observatory_light <- function(base_size = 11)
  make_fn_theme(pal_observatory_light, base_size)

theme_observatory_dark <- function(base_size = 11)
  make_fn_theme(pal_observatory_dark, base_size)
```

---

## Usage in Field Notes Reports

At the top of any .qmd report, set the active palette and theme once:

```r
# In setup chunk — choose one:
# ── ARCHIPELAGO LIGHT (production default) ─────────────────────────
active_pal <- pal_archipelago_light
theme_set(theme_archipelago_light())

# ── FIELD JOURNAL LIGHT ────────────────────────────────────────────
# active_pal <- pal_field_journal_light
# theme_set(theme_field_journal_light())
```

Then reference `active_pal$series1`, `active_pal$series2`, etc. throughout the report.

For Island Time, the existing three-region palette maps to:

```r
# Semantic mapping for the three SIDS regions
pal_regions <- c(
  "Caribbean" = active_pal$series1,
  "Pacific"   = active_pal$series2,
  "AIMS"      = active_pal$series3
)
```

---

## Chart Type Examples

### 1. Categorical Comparison (dot plot / bar)

```r
# Tourism dependence ranking — Archipelago Light example
library(ggplot2)
library(scales)

active_pal <- pal_archipelago_light
theme_set(theme_archipelago_light())

pal_regions <- c(
  "Caribbean" = active_pal$series1,
  "Pacific"   = active_pal$series2,
  "AIMS"      = active_pal$series3
)

ggplot(plot_data,
       aes(x = vspend_mean_1519, y = reorder(label, vspend_mean_1519),
           color = sids_region)) +
  geom_vline(xintercept = 0, color = active_pal$reference, linewidth = 0.4) +
  geom_segment(aes(x = 0, xend = vspend_mean_1519, yend = label),
               linewidth = 0.5) +
  geom_point(size = 3) +
  scale_color_manual(values = pal_regions, name = "Region") +
  scale_x_continuous(labels = label_number(suffix = "%")) +
  labs(
    title   = "Pre-Pandemic Tourism Dependence",
    x       = "Visitor spending (% of GDP, 2015–2019 avg.)",
    y       = NULL,
    caption = "Source: OWID / UN Tourism."
  ) +
  theme(
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = active_pal$grid)
  )
```

### 2. Time Series (line chart)

```r
# Real GDP recovery trajectories — Observatory Light example
active_pal <- pal_observatory_light
theme_set(theme_observatory_light())

pal_regions <- c(
  "Caribbean" = active_pal$series1,
  "Pacific"   = active_pal$series2,
  "AIMS"      = active_pal$series3
)

ggplot(ridx |> filter(!is.na(gdp_index)),
       aes(x = year, y = gdp_index, group = iso3)) +
  geom_hline(yintercept = 100,
             color = active_pal$reference, linewidth = 0.8) +
  geom_line(aes(color = sids_region), alpha = 0.65, linewidth = 0.65) +
  geom_point(data = ridx |> filter(year == 2020, !is.na(gdp_index)),
             aes(color = sids_region), size = 1.8) +
  scale_color_manual(values = pal_regions, name = "Region") +
  scale_x_continuous(breaks = c(2015, 2017, 2019, 2021, 2023, 2025)) +
  scale_y_continuous(limits = c(50, 165), breaks = seq(60, 160, by = 20)) +
  facet_wrap(~sids_region, ncol = 1, scales = "fixed") +
  labs(
    title    = "Real GDP Trajectories, 2015–2025",
    subtitle = "Index: 2019 = 100",
    x        = NULL,
    y        = "Real GDP Index (2019 = 100)",
    caption  = "Source: WDI NY.GDP.MKTP.KD (constant 2015 USD)."
  ) +
  theme(
    legend.position = "none",
    strip.text = element_text(face = "bold")
  )
```

### 3. Scatter Plot with Regression Line

```r
# Tourism dependence vs. 2020 GDP growth — Field Journal Light example
active_pal <- pal_field_journal_light
theme_set(theme_field_journal_light())

pal_regions <- c(
  "Caribbean" = active_pal$series1,
  "Pacific"   = active_pal$series2,
  "AIMS"      = active_pal$series3
)

ggplot(shock_data,
       aes(x = vspend_mean_1519, y = gdp_growth_pct_2020,
           color = sids_region)) +
  geom_hline(yintercept = 0, color = active_pal$reference, linewidth = 0.5) +
  geom_smooth(method = "lm", formula = y ~ x, se = TRUE,
              color = active_pal$muted,
              fill  = paste0(active_pal$muted, "40"),   # ~25% opacity
              linewidth = 0.8, alpha = 0.4,
              show.legend = FALSE) +
  geom_point(size = 3, alpha = 0.9) +
  scale_color_manual(values = pal_regions, name = "Region") +
  scale_x_continuous(labels = label_number(suffix = "%")) +
  scale_y_continuous(labels = label_number(suffix = "%")) +
  labs(
    title   = "Tourism Dependence and the 2020 Shock",
    x       = "Visitor spending (% GDP, 2015–2019 avg.)",
    y       = "GDP growth, 2020 (%)",
    caption = "Sources: OWID / UN Tourism; WDI NY.GDP.MKTP.KD.ZG."
  )
```

### 4. Annotated Chart

```r
# Annotated scatter — Archipelago Dark example
active_pal <- pal_archipelago_dark
theme_set(theme_archipelago_dark())

# Annotation text in accent color
ann_text <- "Each point = one island economy\nSlope: −0.31 | R² = 0.41"

ggplot(shock_data,
       aes(x = vspend_mean_1519, y = gdp_growth_pct_2020)) +
  geom_hline(yintercept = 0,
             color = active_pal$reference, linewidth = 0.6,
             linetype = "dashed") +
  geom_smooth(method = "lm", formula = y ~ x, se = TRUE,
              color = active_pal$muted,
              fill = paste0(active_pal$muted, "50"),
              linewidth = 0.7, alpha = 0.3,
              show.legend = FALSE) +
  geom_point(aes(color = sids_region), size = 3, alpha = 0.9) +
  # Highlight Maldives as influential observation
  geom_point(data = shock_data |> filter(iso3 == "MDV"),
             color = active_pal$accent, size = 4.5, shape = 1,
             stroke = 1.5) +
  annotate("text",
           x = max(shock_data$vspend_mean_1519, na.rm = TRUE),
           y = max(shock_data$gdp_growth_pct_2020, na.rm = TRUE),
           label = ann_text,
           hjust = 1, vjust = 1.2,
           size = 2.8, color = active_pal$muted) +
  scale_color_manual(
    values = c(
      "Caribbean" = active_pal$series1,
      "Pacific"   = active_pal$series2,
      "AIMS"      = active_pal$series3
    ),
    name = "Region"
  ) +
  scale_x_continuous(labels = label_number(suffix = "%")) +
  scale_y_continuous(labels = label_number(suffix = "%")) +
  labs(
    title   = "Tourism Dependence and the 2020 Economic Shock",
    x       = "Visitor spending (% GDP, 2015–2019 avg.)",
    y       = "GDP growth, 2020 (%)",
    caption = "Circle = Maldives (most influential obs.)."
  )
```

---

## Export Settings

```r
# Standard Field Notes export dimensions

# Full-width chart (default)
ggsave("fig.png", width = 8.5, height = 5.5, dpi = 300, bg = active_pal$bg)
ggsave("fig.svg", width = 8.5, height = 5.5,            bg = active_pal$bg)

# Narrow / half-width
ggsave("fig.png", width = 5.5, height = 4.5, dpi = 300, bg = active_pal$bg)

# Tall (e.g. ranking dot plot with many countries)
ggsave("fig.png", width = 8.5, height = 9.0, dpi = 300, bg = active_pal$bg)

# Faceted / multi-panel
ggsave("fig.png", width = 11.0, height = 6.0, dpi = 300, bg = active_pal$bg)
```

**Key rule:** Always pass `bg = active_pal$bg` to `ggsave()`. This ensures the saved file matches the page background, especially for dark themes where transparent backgrounds look jarring in dark-mode pages.

For Quarto inline figures, set `plot.background = element_rect(fill = "transparent", color = NA)` if you want the page CSS background to show through. This works well for light themes; for dark themes, prefer the opaque `active_pal$panel` background.

---

## Accessibility Notes

- All six themes target WCAG AA contrast (≥ 4.5:1) for normal body text.
- Do not communicate data categories through color alone — use shape, pattern, or direct labels where possible.
- For color-blind accessibility, the `pal_archipelago_light` palette avoids red/green confusion. Other palettes may use similar hues; add shapes or direct labels for critical distinctions.
- Dark themes require extra care with chart text color. Use `active_pal$text` for all annotation text.

---

## Quick Reference: Active Palette in .qmd Reports

```r
# In setup chunk — set once, use everywhere
active_pal <- pal_archipelago_light   # match _quarto.yml theme
theme_set(theme_archipelago_light())

# Region palette
pal_reg <- c(Caribbean = active_pal$series1,
             Pacific   = active_pal$series2,
             AIMS      = active_pal$series3)
```

Replace `archipelago_light` with the active theme name when switching.
