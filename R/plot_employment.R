# plot_employment.R — Fig 6 (FRED employment) and Fig 7 (employment comparison)
library(ggplot2)
library(dplyr)
library(readr)
library(scales)
library(patchwork)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")

# ---------------------------------------------------------------------------
# Fig 6 — FRED L&H employment
# ---------------------------------------------------------------------------
plot_fred_employment <- function(mode = "light") {
  pal <- tw_palette(mode)
  df  <- read_csv("data/processed/employment_fred_annual.csv", show_col_types = FALSE)

  df_clean <- df |> filter(!is.na(emp_sa_avg))

  ann_pts <- df_clean |>
    filter(year %in% c(2016, max(df_clean$year))) |>
    mutate(
      nudge_y = if_else(year == 2016, 0.15, -0.25),
      vjust = if_else(year == 2016, 0, 0.5)
    )
  
  p <- ggplot(df_clean, aes(x = year, y = emp_sa_avg)) +
    geom_line(
      color     = pal$employment,
      linewidth = 1.2,
      na.rm     = TRUE
    ) +
    geom_point(
      data  = ann_pts,
      color = pal$employment,
      size  = 2.4,
      na.rm = TRUE
    ) +
    geom_text(
      data  = ann_pts,
      aes(label = paste0(year, ":\n", round(emp_sa_avg, 1), "k"),
          y = emp_sa_avg + nudge_y,
          vjust = vjust),
      size   = 2.9,
      color  = pal$employment,
      hjust  = 0.5,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2025, 4),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.05, 0.1))
    ) +
    labs(
      x       = NULL,
      y       = "Employees (thousands)",
      title   = "Broad L&H Employment Recovered Only in Part",
      caption = source_note(
        "Source: FRED/BLS USVI Leisure & Hospitality (NAICS 71+72); annual values are means of monthly SA observations"
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  add_shocks(
    p,
    x_vals = c(1995, 2017, 2020),
    labels = c("Hurricane\nMarilyn\n(1995)", "Hurricanes\nIrma & Maria", "COVID-19"),
    mode = mode
  )
}

# ---------------------------------------------------------------------------
# Fig 7 — Employment comparison (two-panel patchwork)
# ---------------------------------------------------------------------------
# plot_employment_comparison <- function(mode = "light") {
#   pal   <- tw_palette(mode)
#   qcew  <- read_csv("data/processed/employment_qcew.csv",    show_col_types = FALSE)
#   cens  <- read_csv("data/processed/census_naics72.csv",      show_col_types = FALSE)

#   qcew_clean <- qcew |> filter(!is.na(annual_avg_emplvl))
#   cens_72    <- cens  |> filter(naics == "72", !is.na(emp))

#   # Panel A — QCEW continuous
#   pA <- ggplot(qcew_clean, aes(x = year, y = annual_avg_emplvl)) +
#     geom_line(
#       color     = pal$employment,
#       linewidth = 1.1,
#       na.rm     = TRUE
#     ) +
#     scale_x_continuous(
#       breaks = seq(2000, 2025, 4),
#       limits = c(2000, 2025),
#       expand = expansion(mult = c(0.01, 0.03))
#     ) +
#     scale_y_continuous(
#       labels = label_comma(),
#       expand = expansion(mult = c(0.05, 0.1))
#     ) +
#     labs(
#       x        = NULL,
#       y        = "QCEW annual avg. covered jobs",
#       subtitle = "A: QCEW (UI-covered, annual average)"
#     ) +
#     theme_tw(mode) +
#     theme(legend.position = "none")

#   pA <- add_shocks(pA, mode = mode)

#   # Panel B — Census snapshot points with value labels
#   pB <- ggplot(cens_72, aes(x = year, y = emp)) +
#     geom_point(
#       color = pal$employment,
#       size  = 4.0,
#       shape = 16,
#       na.rm = TRUE
#     ) +
#     geom_text(
#       aes(label = paste0(year, "\n", scales::comma(emp))),
#       vjust  = -0.6,
#       size   = 2.8,
#       color  = pal$employment,
#       show.legend = FALSE
#     ) +
#     scale_x_continuous(
#       breaks = seq(2000, 2025, 4),
#       limits = c(2000, 2025),
#       expand = expansion(mult = c(0.01, 0.03))
#     ) +
#     scale_y_continuous(
#       labels = label_comma(),
#       expand = expansion(mult = c(0.1, 0.25))
#     ) +
#     labs(
#       x        = NULL,
#       y        = "Census March payroll jobs",
#       subtitle = "B: Economic Census (March payroll snapshot)"
#     ) +
#     theme_tw(mode) +
#     theme(legend.position = "none")

#   combined <- pA / pB +
#     plot_annotation(
#       title   = "Related Employment Measures: Different Populations and Reference Periods",
#       caption = source_note(
#         "Source: BLS QCEW (UI-covered jobs, annual average); U.S. Census Economic Census (March payroll snapshot)"
#       ),
#       theme = theme_tw(mode) +
#         theme(
#           plot.title   = element_text(
#             color  = tw_palette(mode)$text_title,
#             size   = rel(1.15),
#             face   = "bold",
#             hjust  = 0
#           ),
#           plot.caption = element_text(
#             color = tw_palette(mode)$text_caption,
#             size  = rel(0.72),
#             hjust = 0
#           )
#         )
#     )

#   combined
# }

plot_employment_comparison <- function(mode = "light") {
  pal  <- tw_palette(mode)
  qcew <- read_csv("data/processed/employment_qcew.csv", show_col_types = FALSE)
  cens <- read_csv("data/processed/census_naics72.csv", show_col_types = FALSE)

  qcew_clean <- qcew |>
    filter(!is.na(annual_avg_emplvl))

  cens_72 <- cens |>
    filter(naics == "72", !is.na(emp))

  census_color <- if (mode == "light") "#76568f" else "#bc94db"

  p <- ggplot() +
    geom_line(
      data = qcew_clean,
      aes(
        x = year,
        y = annual_avg_emplvl,
        color = "QCEW annual average"
      ),
      linewidth = 1.1,
      na.rm = TRUE
    ) +
    geom_point(
      data = cens_72,
      aes(
        x = year,
        y = emp,
        color = "Economic Census"
      ),
      shape = 18,
      size = 4.0,
      na.rm = TRUE
    ) +
    geom_text(
      data = cens_72,
      aes(
        x = year,
        y = emp,
        label = paste0(year, "\n", scales::comma(emp)),
        vjust = if_else(
          year %in% range(cens_72$year),
          1.3,
          -0.6
        )
      ),
      size = 2.6,
      color = census_color,
      show.legend = FALSE
    ) +
    scale_color_manual(
      values = c(
        "QCEW annual average" = pal$employment,
        "Economic Census" = census_color
      )
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2025, 4),
      limits = c(2000, 2025),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.05, 0.15))
    ) +
    labs(
      x = NULL,
      y = "Employment (jobs)",
      title = "Two Measures of Leisure & Hospitality Employment",
      caption = source_note(
        "Source: BLS QCEW (UI-covered jobs, annual average); U.S. Census Economic Census, NAICS 72 (March payroll snapshot).\nDifferent populations and reference periods."
      ),
      color = NULL
    ) +
    theme_tw(mode) +
    theme(
      legend.position = "bottom"
    )

  add_shocks(p, mode = mode)
}

# ---------------------------------------------------------------------------
# Fig 7a — Employment comparison — FRED, USVIBER, and QCEW
# ---------------------------------------------------------------------------
plot_employment_sources <- function(mode = "light") {
  pal <- tw_palette(mode)

  fred <- read_csv(
    "data/processed/employment_fred_annual.csv",
    show_col_types = FALSE
  ) |>
    transmute(
      year = as.integer(year),
      employment = emp_sa_avg * 1000,
      source = "FRED/BLS Leisure & Hospitality"
    )

  usviber <- read_csv(
    "data/processed/employment_usviber.csv",
    show_col_types = FALSE
  ) |>
    filter(!is.na(emp_tourism_total)) |>
    transmute(
      year = as.integer(year),
      employment = as.numeric(emp_tourism_total),
      source = "USVIBER tourism employment"
    )

  qcew <- read_csv(
    "data/processed/employment_qcew.csv",
    show_col_types = FALSE
  ) |>
    filter(!is.na(annual_avg_emplvl)) |>
    transmute(
      year = as.integer(year),
      employment = as.numeric(annual_avg_emplvl),
      source = "QCEW Accommodation & Food Services"
    )

  long <- bind_rows(fred, usviber, qcew) |>
    filter(!is.na(year), !is.na(employment))

  # Ensure each source has at most one observation per year.
  duplicates <- long |>
    count(source, year) |>
    filter(n > 1)

  if (nrow(duplicates) > 0) {
    stop(
      "Duplicate source-year observations in employment comparison: ",
      paste(
        paste(duplicates$source, duplicates$year, sep = " / "),
        collapse = "; "
      )
    )
  }

  # Require an observed 2016 baseline for every source.
  baselines <- long |>
    filter(year == 2016) |>
    select(source, baseline = employment)

  missing_baselines <- setdiff(
    unique(long$source),
    baselines$source
  )

  if (length(missing_baselines) > 0) {
    stop(
      "Missing 2016 employment baseline for: ",
      paste(missing_baselines, collapse = ", ")
    )
  }

  long <- long |>
    left_join(baselines, by = "source") |>
    mutate(index = employment / baseline * 100)

  source_order <- c(
    "FRED/BLS Leisure & Hospitality",
    "USVIBER tourism employment",
    "QCEW Accommodation & Food Services"
  )

  long <- long |>
    mutate(source = factor(source, levels = source_order))

  colors <- c(
    "FRED/BLS Leisure & Hospitality" = pal$employment,
    "USVIBER tourism employment" = pal$air_visitors,
    "QCEW Accommodation & Food Services" = pal$value_added
  )

  linetypes <- c(
    "FRED/BLS Leisure & Hospitality" = "solid",
    "USVIBER tourism employment" = "22",
    "QCEW Accommodation & Food Services" = "solid"
  )

  p <- ggplot(
    long,
    aes(
      x = year,
      y = index,
      color = source,
      linetype = source
    )
  ) +
    geom_hline(
      yintercept = 100,
      color = pal$benchmark,
      linewidth = 0.5
    ) +
    geom_line(
      linewidth = 1,
      na.rm = TRUE
    ) +
    scale_color_manual(values = colors) +
    scale_linetype_manual(values = linetypes) +
    scale_x_continuous(
      breaks = seq(2000, 2025, 5),
      limits = c(2000, 2025),
      expand = expansion(mult = c(0.01, 0.02))
    ) +
    scale_y_continuous(
      labels = label_number(suffix = "%"),
      expand = expansion(mult = c(0.05, 0.12))
    ) +
    labs(
      x = NULL,
      y = "Employment index (2016 = 100)",
      title = "Employment Trends Across Three Sources",
      subtitle = "Each series is indexed to its own 2016 employment level",
      caption = source_note(
        paste(
          "Sources: FRED/BLS, USVIBER Annual Tourism Indicators, and BLS QCEW.",
          "FRED: NAICS 71+72, annual mean of seasonally adjusted monthly estimates.",
          "\nUSVIBER: selected tourism-related employment categories.",
          "QCEW: NAICS 72, annual average UI-covered jobs.",
          "\nDefinitions and coverage differ; indexed trends are not directly",
          "equivalent measures of the same employment population."
        )
      ),
      color = NULL,
      linetype = NULL
    ) +
    theme_tw(mode) +
    theme(
      legend.position = "bottom",
      legend.text = element_text(size = rel(0.82))
    )

  add_shocks(p, mode = mode)
}