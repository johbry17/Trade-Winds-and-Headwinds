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
# FigOV — Visitor arrivals
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
# Fig 01 — Visitor arrivals: USVIBER and World Bank
# ---------------------------------------------------------------------------
plot_arrivals_comparison <- function(mode = "light") {
  pal <- tw_palette(mode)

  usviber <- read_csv(
    "data/processed/visitors_annual.csv",
    show_col_types = FALSE
  )

  worldbank <- read_csv(
    "data/interim/worldbank_arrivals.csv",
    show_col_types = FALSE
  ) |>
    filter(year <= 2019, !is.na(value)) |>
    transmute(
      year,
      series = "World Bank international arrivals",
      value = value / 1000
    )

  arrivals <- usviber |>
    select(year, air_visitors, cruise_passengers, total_visitors) |>
    pivot_longer(
      cols = c(air_visitors, cruise_passengers, total_visitors),
      names_to = "series",
      values_to = "value"
    ) |>
    mutate(
      series = recode(
        series,
        air_visitors = "Air visitors",
        cruise_passengers = "Cruise passengers",
        total_visitors = "Total visitors"
      )
    )

  long <- bind_rows(arrivals, worldbank)

  series_order <- c(
    "Air visitors",
    "Cruise passengers",
    "Total visitors",
    "World Bank international arrivals"
  )

  long <- long |>
    mutate(series = factor(series, levels = series_order))

  endpoints <- long |>
    filter(!is.na(value)) |>
    group_by(series) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(
      nudge_y = case_when(
        series == "Air visitors" ~ 80,
        series == "Cruise passengers" ~ -80,
        series == "Total visitors" ~ 60,
        series == "World Bank international arrivals" ~ 45,
        TRUE ~ 0
      )
    )

  colors <- c(
    "Air visitors" = pal$air_visitors,
    "Cruise passengers" = pal$cruise,
    "Total visitors" = pal$total,
    "World Bank international arrivals" = pal$benchmark
  )

  widths <- c(
    "Air visitors" = 1.1,
    "Cruise passengers" = 1.1,
    "Total visitors" = 0.8,
    "World Bank international arrivals" = 0.9
  )

  linetypes <- c(
    "Air visitors" = "solid",
    "Cruise passengers" = "solid",
    "Total visitors" = "solid",
    "World Bank international arrivals" = "22"
  )

  p <- ggplot(
    long,
    aes(x = year, y = value, color = series)
  ) +
    geom_line(
      aes(linewidth = series, linetype = series),
      na.rm = TRUE
    ) +
    scale_color_manual(values = colors) +
    scale_linewidth_manual(values = widths, guide = "none") +
    scale_linetype_manual(values = linetypes, guide = "none") +
    geom_text(
      data = endpoints,
      aes(
        label = as.character(series),
        y = value + nudge_y
      ),
      hjust = -0.08,
      size = 2.8,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2024, 4),
      expand = expansion(mult = c(0.01, 0.24))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.02, 0.08))
    ) +
    labs(
      x = NULL,
      y = "Annual arrivals (thousands)",
      title = "Visitor Arrivals Across Two Statistical Sources",
      subtitle = "World Bank international arrivals are a distinct measure, not a direct equivalent of USVIBER total visitors",
      caption = source_note(
        paste(
          "Sources: USVIBER Annual Tourism Indicators (TOUR24, TOUR10);",
          "World Bank international tourism arrivals.",
          "\nWorld Bank series ends in 2019; anomalous 2020 observation excluded."
        )
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  add_shocks(p, mode = mode)
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

  # Label each line near its 2024 value
  mid_labels <- long |> filter(year == 2024, !is.na(value))

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
      data = mid_labels,
      aes(label = series, y = value,),
      hjust = 0.62,
      vjust = -0.35,
      size = 2.9,
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
