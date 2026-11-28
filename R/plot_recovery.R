# plot_recovery.R — Fig 10 (full recovery) and figOV (overview recovery)
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)
library(patchwork)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")
source("R/scales.R")

# ---------------------------------------------------------------------------
# Internal helper: build the indexed recovery data frame
# ---------------------------------------------------------------------------
.build_recovery_data <- function(series_names) {
  visitors   <- read_csv("data/processed/visitors_annual.csv",         show_col_types = FALSE)
  fred_emp   <- read_csv("data/processed/employment_fred_annual.csv",  show_col_types = FALSE)
  bea_af     <- read_csv("data/processed/bea_af_real.csv",             show_col_types = FALSE)
  nps        <- read_csv("data/processed/nps_viis.csv",                show_col_types = FALSE)

  base_year <- 2016
  series_list <- list()

  if ("Air visitors" %in% series_names) {
    base_v <- visitors |> filter(year == base_year) |> pull(air_visitors)
    series_list[["Air visitors"]] <- visitors |>
      select(year, value = air_visitors) |>
      mutate(index = value / base_v * 100)
  }
  if ("Cruise" %in% series_names) {
    base_c <- visitors |> filter(year == base_year) |> pull(cruise_passengers)
    series_list[["Cruise"]] <- visitors |>
      select(year, value = cruise_passengers) |>
      mutate(index = value / base_c * 100)
  }
  if ("Hotel rooms" %in% series_names) {
    base_r <- visitors |> filter(year == base_year) |> pull(hotel_rooms)
    series_list[["Hotel rooms"]] <- visitors |>
      select(year, value = hotel_rooms) |>
      mutate(index = value / base_r * 100)
  }
  if ("L&H employment" %in% series_names) {
    base_e <- fred_emp |> filter(year == base_year) |> pull(emp_sa_avg)
    series_list[["L&H employment"]] <- fred_emp |>
      select(year, value = emp_sa_avg) |>
      mutate(index = value / base_e * 100)
  }
  if ("A&F value added" %in% series_names) {
    base_a <- bea_af |> filter(year == base_year) |> pull(af_real)
    series_list[["A&F value added"]] <- bea_af |>
      select(year, value = af_real) |>
      mutate(index = value / base_a * 100)
  }
  if ("NPS visits" %in% series_names) {
    base_n <- as.numeric(nps |> filter(year == base_year) |> pull(recreation_visitors))
    series_list[["NPS visits"]] <- nps |>
      mutate(recreation_visitors = as.numeric(recreation_visitors)) |>
      select(year, value = recreation_visitors) |>
      mutate(index = value / base_n * 100)
  }

  bind_rows(
    lapply(names(series_list), function(nm) {
      series_list[[nm]] |> mutate(series = nm)
    })
  ) |>
    filter(!is.na(index))
}

# ---------------------------------------------------------------------------
# figOV — Overview recovery (4-series)
# ---------------------------------------------------------------------------
plot_overview_recovery <- function(mode = "light") {
  pal <- tw_palette(mode)

  ov_series <- c("Air visitors", "Cruise", "Hotel rooms", "L&H employment")

  df <- .build_recovery_data(ov_series) |>
    filter(year >= 2012)

  series_colors <- c(
    "Air visitors"   = pal$air_visitors,
    "Cruise"         = pal$cruise,
    "Hotel rooms"    = pal$rooms,
    "L&H employment" = pal$employment
  )

  endpoints <- df |>
    group_by(series) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(
      ep_label = paste0(series, " (", year, ")"),
      nudge_y  = case_when(
        series == "Air visitors"   ~  4,
        series == "Cruise"         ~ -4,
        series == "Hotel rooms"    ~ -4,
        series == "L&H employment" ~  3,
        TRUE ~ 0
      )
    )

  p <- ggplot(df, aes(x = year, y = index, color = series)) +
    geom_line(linewidth = 1.1, na.rm = TRUE) +
    scale_color_manual(values = series_colors, guide = "none") +
    geom_text(
      data  = endpoints,
      aes(label = ep_label, y = index + nudge_y),
      hjust = -0.06,
      size  = 2.9,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2012, 2024, 2),
      expand = expansion(mult = c(0.01, 0.28))
    ) +
    scale_y_continuous(
      labels = function(x) paste0(x, "%"),
      expand = expansion(mult = c(0.03, 0.05))
    ) +
    labs(
      x       = NULL,
      y       = "Index (2016 = 100)",
      title   = "Visitor Recovery Outran Capacity and Employment",
      caption = source_note(
        "Source: USVIBER, FRED/BLS; annual means for employment"
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  p <- add_benchmark(p, y = 100, label = "2016 level", mode = mode)
  add_shocks(p, mode = mode)
}

# # ---------------------------------------------------------------------------
# # Fig 10 — Full 6-series recovery chart
# # ---------------------------------------------------------------------------
# plot_recovery <- function(mode = "light") {
#   pal <- tw_palette(mode)

#   all_series <- c("Air visitors", "Cruise", "Hotel rooms",
#                   "L&H employment", "A&F value added", "NPS visits")

#   df <- .build_recovery_data(all_series) |>
#     filter(year >= 2012)

#   series_colors <- c(
#     "Air visitors"    = pal$air_visitors,
#     "Cruise"          = pal$cruise,
#     "Hotel rooms"     = pal$rooms,
#     "L&H employment"  = pal$employment,
#     "A&F value added" = pal$value_added,
#     "NPS visits"      = pal$nps_viis
#   )

#   # Endpoint labels — manually stagger y positions to avoid overlap
#   endpoints <- df |>
#     group_by(series) |>
#     filter(year == max(year)) |>
#     ungroup() |>
#     mutate(
#       ep_label = paste0(series, " (", year, ")"),
#       # Nudge based on approximate endpoint values
#       nudge_y = case_when(
#         series == "Air visitors"    ~  5,
#         series == "NPS visits"      ~  3,
#         series == "Cruise"          ~ -3,
#         series == "L&H employment"  ~  3,
#         series == "Hotel rooms"     ~ -3,
#         series == "A&F value added" ~ -5,
#         TRUE ~ 0
#       )
#     )

#   p <- ggplot(df, aes(x = year, y = index, color = series)) +
#     geom_line(linewidth = 1.0, na.rm = TRUE) +
#     scale_color_manual(values = series_colors, guide = "none") +
#     geom_text(
#       data  = endpoints,
#       aes(label = ep_label, y = index + nudge_y),
#       hjust = -0.06,
#       size  = 2.7,
#       show.legend = FALSE
#     ) +
#     scale_x_continuous(
#       breaks = seq(2012, 2024, 2),
#       expand = expansion(mult = c(0.01, 0.30))
#     ) +
#     scale_y_continuous(
#       expand = expansion(mult = c(0.03, 0.05))
#     ) +
#     labs(
#       x       = NULL,
#       y       = "Index (2016 = 100)",
#       title   = "An Uneven Recovery: Arrivals Outpaced Capacity, Employment, and Output",
#       caption = source_note(
#         "Source: USVIBER, FRED/BLS, BEA, NPS IRLS. Series indexed independently to 2016 = 100. Latest years differ."
#       )
#     ) +
#     theme_tw(mode) +
#     theme(legend.position = "none")

#   p <- add_benchmark(p, y = 100, label = "2016 = 100", mode = mode)
#   add_shocks(p, mode = mode)
# }

# ---------------------------------------------------------------------------
# Internal helper: build grouped, indexed recovery data for Fig 10
# ---------------------------------------------------------------------------
.build_recovery_alt_data <- function() {
  visitors <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)
  fred <- read_csv("data/processed/employment_fred_annual.csv", show_col_types = FALSE)
  af <- read_csv("data/processed/bea_af_real.csv", show_col_types = FALSE)
  nps <- read_csv("data/processed/nps_viis.csv", show_col_types = FALSE)

  index_series <- function(year, value, base_year = 2016) {
    base_row <- value[year == base_year]

    if (
      length(base_row) == 0 ||
      is.na(base_row[1]) ||
      base_row[1] == 0
    ) {
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


# ---------------------------------------------------------------------------
# Fig 10 — Grouped recovery trajectories and latest observations
# ---------------------------------------------------------------------------
plot_recovery <- function(mode = "light") {
  pal <- tw_palette(mode)
  df <- .build_recovery_alt_data()

  series_colors <- c(
    "Air visitors"          = pal$air_visitors,
    "Cruise passengers"     = pal$cruise,
    "Hotel rooms"            = pal$rooms,
    "L&H employment"         = pal$employment,
    "A&F value added"        = pal$value_added,
    "NPS recreation visits"  = pal$nps_viis
  )

  group_order <- c(
    "Visitor activity",
    "Accommodation",
    "Recreation",
    "Labor and industry"
  )

  df <- df |>
    mutate(group = factor(group, levels = group_order))

  # Historical trajectories, grouped by concept
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
      data = df |>
        group_by(group, series) |>
        filter(year == max(year)) |>
        ungroup(),
      aes(x = year, y = index, color = series, shape = series),
      size = 1.7,
      na.rm = TRUE
    ) +
    facet_wrap(~group, ncol = 2, scales = "fixed") +
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
    scale_y_continuous(labels = function(x) paste0(x, "%")) +
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
      panel.spacing = grid::unit(12, "pt"),
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

  # Latest available observation for each series.
  # Endpoint years are retained explicitly rather than implying a common year.
  endpoints <- df |>
    group_by(series, group) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(
      label = paste0(series, " · ", year),
      series = factor(
        series,
        levels = c(
          "Air visitors",
          "Cruise passengers",
          "Hotel rooms",
          "L&H employment",
          "A&F value added",
          "NPS recreation visits"
        )
      )
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
      aes(
        x = 100,
        xend = index,
        y = label_order,
        yend = label_order
      ),
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

  trajectory / endpoints_plot +
    plot_layout(heights = c(2.25, 1)) +
    plot_annotation(
      title = "Uneven Recovery: Common Index, Different Concepts and Observation Years",
      caption = source_note(
        "Source: USVIBER, FRED/BLS, BEA, NPS IRLS. Each series is independently indexed to 2016 = 100."
      ),
      theme = theme_tw(mode) +
        theme(
          plot.title = element_text(
            color = pal$text_title,
            size = rel(1.15),
            face = "bold",
            hjust = 0
          ),
          plot.caption = element_text(
            color = pal$text_caption,
            size = rel(0.72),
            hjust = 0
          )
        )
    )
}

# ---------------------------------------------------------------------------
# Internal helper: build the indexed recovery data frame
