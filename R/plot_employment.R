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
      aes(label = paste0(year, ": ", round(emp_sa_avg, 1), "k"),
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

  add_shocks(p, mode = mode)
}

# ---------------------------------------------------------------------------
# Fig 7 — Employment comparison (two-panel patchwork)
# ---------------------------------------------------------------------------
plot_employment_comparison <- function(mode = "light") {
  pal   <- tw_palette(mode)
  qcew  <- read_csv("data/processed/employment_qcew.csv",    show_col_types = FALSE)
  cens  <- read_csv("data/processed/census_naics72.csv",      show_col_types = FALSE)

  qcew_clean <- qcew |> filter(!is.na(annual_avg_emplvl))
  cens_72    <- cens  |> filter(naics == "72", !is.na(emp))

  # Panel A — QCEW continuous
  pA <- ggplot(qcew_clean, aes(x = year, y = annual_avg_emplvl)) +
    geom_line(
      color     = pal$employment,
      linewidth = 1.1,
      na.rm     = TRUE
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2025, 4),
      limits = c(2000, 2025),
      expand = expansion(mult = c(0.01, 0.03))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.05, 0.1))
    ) +
    labs(
      x        = NULL,
      y        = "QCEW annual avg. covered jobs",
      subtitle = "A: QCEW (UI-covered, annual average)"
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  pA <- add_shocks(pA, mode = mode)

  # Panel B — Census snapshot points with value labels
  pB <- ggplot(cens_72, aes(x = year, y = emp)) +
    geom_point(
      color = pal$employment,
      size  = 4.0,
      shape = 16,
      na.rm = TRUE
    ) +
    geom_text(
      aes(label = paste0(year, "\n", scales::comma(emp))),
      vjust  = -0.6,
      size   = 2.8,
      color  = pal$employment,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2025, 4),
      limits = c(2000, 2025),
      expand = expansion(mult = c(0.01, 0.03))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.1, 0.25))
    ) +
    labs(
      x        = NULL,
      y        = "Census March payroll jobs",
      subtitle = "B: Economic Census (March payroll snapshot)"
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  combined <- pA / pB +
    plot_annotation(
      title   = "Related Employment Measures: Different Populations and Reference Periods",
      caption = source_note(
        "Source: BLS QCEW (UI-covered jobs, annual average); U.S. Census Economic Census (March payroll snapshot)"
      ),
      theme = theme_tw(mode) +
        theme(
          plot.title   = element_text(
            color  = tw_palette(mode)$text_title,
            size   = rel(1.15),
            face   = "bold",
            hjust  = 0
          ),
          plot.caption = element_text(
            color = tw_palette(mode)$text_caption,
            size  = rel(0.72),
            hjust = 0
          )
        )
    )

  combined
}

# plot_employment_comparison <- function(mode = "light") {
#   pal  <- tw_palette(mode)
#   qcew <- read_csv("data/processed/employment_qcew.csv", show_col_types = FALSE)
#   cens <- read_csv("data/processed/census_naics72.csv", show_col_types = FALSE)

#   qcew_clean <- qcew |>
#     filter(!is.na(annual_avg_emplvl))

#   cens_72 <- cens |>
#     filter(naics == "72", !is.na(emp))

#   census_color <- if (mode == "light") "#4a7a53" else "#7ad09a"

#   p <- ggplot() +
#     geom_line(
#       data = qcew_clean,
#       aes(
#         x = year,
#         y = annual_avg_emplvl,
#         color = "QCEW annual average"
#       ),
#       linewidth = 1.1,
#       na.rm = TRUE
#     ) +
#     geom_point(
#       data = cens_72,
#       aes(
#         x = year,
#         y = emp,
#         color = "Economic Census"
#       ),
#       shape = 18,
#       size = 4.0,
#       na.rm = TRUE
#     ) +
#     geom_text(
#       data = cens_72,
#       aes(
#         x = year,
#         y = emp,
#         label = paste0(year, "\n", scales::comma(emp))
#       ),
#       vjust = -0.6,
#       size = 2.6,
#       color = census_color,
#       show.legend = FALSE
#     ) +
#     scale_color_manual(
#       values = c(
#         "QCEW annual average" = pal$employment,
#         "Economic Census" = census_color
#       )
#     ) +
#     scale_x_continuous(
#       breaks = seq(2000, 2025, 4),
#       limits = c(2000, 2025),
#       expand = expansion(mult = c(0.01, 0.05))
#     ) +
#     scale_y_continuous(
#       labels = label_comma(),
#       expand = expansion(mult = c(0.05, 0.15))
#     ) +
#     labs(
#       x = NULL,
#       y = "Employment (jobs)",
#       title = "Two Measures of Leisure & Hospitality Employment",
#       caption = source_note(
#         "Source: BLS QCEW (UI-covered jobs, annual average); U.S. Census Economic Census, NAICS 72 (March payroll snapshot). Different populations and reference periods."
#       ),
#       color = NULL
#     ) +
#     theme_tw(mode) +
#     theme(
#       legend.position = "bottom"
#     )

#   add_shocks(p, mode = mode)
# }

# ---------------------------------------------------------------------------
# Fig 6 — FRED L&H employment
