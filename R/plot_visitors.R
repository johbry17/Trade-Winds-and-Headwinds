# plot_visitors.R — Fig 1 (arrivals) and Fig 2 (expenditure)
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")
source("R/scales.R")

# ---------------------------------------------------------------------------
# Fig 1 — Visitor arrivals
# ---------------------------------------------------------------------------
plot_arrivals <- function(mode = "light") {
  pal  <- tw_palette(mode)
  df   <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)

  long <- df |>
    select(year, air_visitors, cruise_passengers, total_visitors) |>
    pivot_longer(
      cols      = c(air_visitors, cruise_passengers, total_visitors),
      names_to  = "series",
      values_to = "value"
    ) |>
    mutate(
      series = recode(series,
        air_visitors      = "Air visitors",
        cruise_passengers = "Cruise passengers",
        total_visitors    = "Total visitors"
      )
    )

  # Endpoint labels at last year with data
  endpoints <- long |>
    filter(!is.na(value)) |>
    group_by(series) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(nudge_y = case_when(
      series == "Air visitors"      ~  80,
      series == "Cruise passengers" ~ -80,
      series == "Total visitors"    ~  60,
      TRUE ~ 0
    ))

  lw_map <- c(
    "Air visitors"      = 1.2,
    "Cruise passengers" = 1.2,
    "Total visitors"    = 0.8
  )

  p <- ggplot(long, aes(x = year, y = value, color = series)) +
    geom_line(aes(linewidth = series), na.rm = TRUE) +
    scale_linewidth_manual(
      values = lw_map,
      guide  = "none"
    ) +
    tw_scale_color_arrivals(mode) +
    geom_text(
      data  = endpoints,
      aes(label = series, y = value + nudge_y),
      hjust = -0.08,
      size  = 2.9,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2024, 4),
      expand = expansion(mult = c(0.01, 0.16))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.02, 0.08))
    ) +
    labs(
      x       = NULL,
      y       = "Annual arrivals (thousands)",
      title   = "Arrival Modes Moved on Separate Trajectories",
      caption = source_note(
        "Source: USVIBER, published annual tourism indicators (TOUR24, TOUR10 historical gap-fill)"
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  p <- add_shocks(p, mode = mode)
  p
}

# ---------------------------------------------------------------------------
# Fig 2 — Visitor expenditure
# ---------------------------------------------------------------------------
plot_expenditure <- function(mode = "light") {
  pal <- tw_palette(mode)
  df  <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)

  long <- df |>
    select(year, expenditures_total, expenditures_total_real) |>
    pivot_longer(
      cols      = c(expenditures_total, expenditures_total_real),
      names_to  = "series",
      values_to = "value"
    ) |>
    mutate(
      series = recode(series,
        expenditures_total      = "Nominal",
        expenditures_total_real = "Approx. 2016 USD"
      )
    )

  # Label each line near its 2010 value
  mid_labels <- long |>
    filter(year == 2010, !is.na(value)) |>
    mutate(nudge_y = case_when(
      series == "Nominal" ~ 80,
      TRUE ~ -80
    ))

  p <- ggplot(long, aes(x = year, y = value, color = series, linetype = series)) +
    geom_line(linewidth = 1.1, na.rm = TRUE) +
    scale_linetype_manual(
      values = c("Nominal" = "solid", "Approx. 2016 USD" = "dashed"),
      guide  = "none"
    ) +
    scale_color_manual(
      values = c(
        "Nominal"          = pal$total,
        "Approx. 2016 USD" = pal$total
      ),
      guide = "none"
    ) +
    geom_text(
      data  = mid_labels,
      aes(label = series, y = value + nudge_y),
      hjust = 0.5,
      size  = 2.9,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2024, 4),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = label_dollar(suffix = "M"),
      expand = expansion(mult = c(0.02, 0.1))
    ) +
    labs(
      x       = NULL,
      y       = "Expenditure (millions USD, nominal)",
      title   = "Total Visitor Expenditure: Nominal and Approximate 2016 Dollars",
      caption = source_note(
        "Source: USVIBER; mainland CPI-U used as an inflation proxy. Real values are approximate."
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  p <- add_shocks(p, mode = mode)
  p
}


# ---------------------------------------------------------------------------
# Fig 1 — Visitor arrivals
