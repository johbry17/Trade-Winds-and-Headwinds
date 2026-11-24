# plot_recovery_alt.R — Experimental two-part recovery alternative
# Additive only. Existing publication recovery figures are unchanged.
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)
library(patchwork)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")


.build_recovery_alt_data <- function() {
  visitors <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)
  fred <- read_csv("data/processed/employment_fred_annual.csv", show_col_types = FALSE)
  af <- read_csv("data/processed/bea_af_real.csv", show_col_types = FALSE)
  nps <- read_csv("data/processed/nps_viis.csv", show_col_types = FALSE)

  index_series <- function(year, value, base_year = 2016) {
    base_row <- value[year == base_year]
    if (length(base_row) == 0 || is.na(base_row[1]) || base_row[1] == 0) {
      return(rep(NA_real_, length(year)))
    }
    value / base_row[1] * 100
  }

  bind_rows(
    data.frame(
      year = visitors$year,
      value = visitors$air_visitors,
      series = "Air visitors",
      group = "Visitor activity"
    ) |> mutate(index = index_series(year, value)),
    data.frame(
      year = visitors$year,
      value = visitors$cruise_passengers,
      series = "Cruise passengers",
      group = "Visitor activity"
    ) |> mutate(index = index_series(year, value)),
    data.frame(
      year = visitors$year,
      value = visitors$hotel_rooms,
      series = "Hotel rooms",
      group = "Accommodation"
    ) |> mutate(index = index_series(year, value)),
    data.frame(
      year = fred$year,
      value = fred$emp_sa_avg,
      series = "L&H employment",
      group = "Labor and industry"
    ) |> mutate(index = index_series(year, value)),
    data.frame(
      year = af$year,
      value = af$af_real,
      series = "A&F value added",
      group = "Labor and industry"
    ) |> mutate(index = index_series(year, value)),
    data.frame(
      year = nps$year,
      value = as.numeric(nps$recreation_visitors),
      series = "NPS recreation visits",
      group = "Recreation"
    ) |> mutate(index = index_series(year, value))
  ) |>
    filter(
      year >= 2012,
      !is.na(index),
      !(series == "L&H employment" & year > 2025)
    )
}


# Experimental Fig 10: grouped trajectories in small multiples plus a compact
# latest-observation dot plot. It makes endpoint-year differences explicit.
plot_recovery_alt <- function(mode = "light") {
  pal <- tw_palette(mode)
  df <- .build_recovery_alt_data()

  series_colors <- c(
    "Air visitors" = pal$air_visitors,
    "Cruise passengers" = pal$cruise,
    "Hotel rooms" = pal$rooms,
    "L&H employment" = pal$employment,
    "A&F value added" = pal$value_added,
    "NPS recreation visits" = pal$nps_viis
  )

  group_order <- c(
    "Visitor activity",
    "Accommodation",
    "Labor and industry",
    "Recreation"
  )
  df <- df |>
    mutate(group = factor(group, levels = group_order))

  trajectory <- ggplot(
    df,
    aes(x = year, y = index, color = series)
  ) +
    geom_hline(
      yintercept = 100,
      color = pal$benchmark,
      linewidth = 0.5
    ) +
    geom_line(linewidth = 0.9, na.rm = TRUE) +
    geom_point(
      data = df |> group_by(group, series) |> filter(year == max(year)) |> ungroup(),
      aes(x = year, y = index, color = series, shape = series),
      size = 1.7,
      na.rm = TRUE
    ) +
    facet_wrap(~ group, ncol = 2, scales = "fixed") +
    scale_color_manual(values = series_colors) +
    scale_shape_manual(
      values = c(
        "Air visitors" = 16,
        "Cruise passengers" = 16,
        "Hotel rooms" = 18,
        "L&H employment" = 15,
        "A&F value added" = 0,
        "NPS recreation visits" = 17
      )
    ) +
    scale_x_continuous(
      breaks = c(2012, 2017, 2020, 2025),
      expand = expansion(mult = c(0.02, 0.08))
    ) +
    coord_cartesian(ylim = c(20, 125)) +
    labs(
      x = NULL,
      y = "Index (2016 = 100)",
      title = "Historical trajectories"
    ) +
    theme_tw(mode) +
    theme(
      legend.position = "bottom",
      legend.box = "vertical",
      panel.spacing = unit(12, "pt"),
      strip.background = element_rect(
        fill = if (mode == "light") "#ece8e0" else "#132535",
        color = pal$grid_major_y
      ),
      strip.text = element_text(
        color = pal$text_primary,
        size = rel(0.82),
        face = "bold"
      )
    )
  trajectory <- add_shocks(trajectory, mode = mode)

  endpoints <- df |>
    group_by(series, group) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(
      label = paste0(series, " · ", year),
      series = factor(series, levels = c(
        "Air visitors",
        "Cruise passengers",
        "Hotel rooms",
        "L&H employment",
        "A&F value added",
        "NPS recreation visits"
      )),
      series_sort = as.integer(series)
    ) |>
    arrange(desc(index)) |>
    mutate(
      label_order = factor(label, levels = rev(label)),
      endpoint_color = recode(
        as.character(series),
        "Air visitors" = pal$air_visitors,
        "Cruise passengers" = pal$cruise,
        "Hotel rooms" = pal$rooms,
        "L&H employment" = pal$employment,
        "A&F value added" = pal$value_added,
        "NPS recreation visits" = pal$nps_viis
      )
    )

  endpoints_plot <- ggplot(
    endpoints,
    aes(x = index, y = label_order, color = endpoint_color)
  ) +
    geom_vline(
      xintercept = 100,
      color = pal$benchmark,
      linewidth = 0.6
    ) +
    geom_segment(
      aes(x = 100, xend = index, y = label_order, yend = label_order),
      linewidth = 0.8,
      na.rm = TRUE
    ) +
    geom_point(size = 3.2, na.rm = TRUE) +
    geom_text(
      aes(label = paste0(round(index), "%")),
      hjust = ifelse(endpoints$index >= 100, -0.35, 1.35),
      size = 2.8,
      show.legend = FALSE
    ) +
    scale_color_identity(guide = "none") +
    scale_x_continuous(
      breaks = seq(80, 120, 20),
      expand = expansion(mult = c(0.12, 0.18))
    ) +
    labs(
      x = "Latest observation, % of 2016",
      y = NULL,
      title = "Latest observations",
      subtitle = "Endpoint years differ; no single common-year comparison"
    ) +
    theme_tw(mode) +
    theme(
      panel.grid.major.y = element_blank(),
      axis.line.y = element_blank(),
      legend.position = "none"
    )

  combined <- trajectory / endpoints_plot +
    plot_layout(heights = c(2.25, 1)) +
    plot_annotation(
      title = "Uneven Recovery: Common Index, Different Concepts and Observation Years",
      caption = source_note(
        "Source: USVIBER, FRED/BLS, BEA, NPS IRLS. Each series is independently indexed to 2016 = 100."
      ),
      theme = theme_tw(mode) +
        theme(
          plot.title = element_text(
            color = tw_palette(mode)$text_title,
            size = rel(1.15),
            face = "bold",
            hjust = 0
          ),
          plot.caption = element_text(
            color = tw_palette(mode)$text_caption,
            size = rel(0.72),
            hjust = 0
          )
        )
    )

  combined
}
