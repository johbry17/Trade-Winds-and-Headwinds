# plot_accommodation.R — Fig 3 (capacity), Fig 4 (occupancy), Fig 5 (island hotel indexed)
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")

# ---------------------------------------------------------------------------
# Fig 3 — Accommodation capacity
# ---------------------------------------------------------------------------
plot_capacity <- function(mode = "light") {
  pal      <- tw_palette(mode)
  visitors <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)
  census   <- read_csv("data/processed/census_rooms.csv",    show_col_types = FALSE)

  usviber_df <- visitors |>
    select(year, hotel_rooms) |>
    filter(!is.na(hotel_rooms))

  census_color <- if (mode == "light") "#4a7a53" else "#7ad09a"

  p <- ggplot() +
    geom_line(
      data    = usviber_df,
      aes(x = year, y = hotel_rooms, color = "USVIBER survey"),
      linewidth = 1.1,
      na.rm   = TRUE
    ) +
    geom_point(
      data  = census,
      aes(x = year, y = rooms, color = "Census guestrooms"),
      shape = 18,
      size  = 4.0,
      na.rm = TRUE
    ) +
    geom_text(
      data  = census,
      aes(x = year, y = rooms,
          label = paste0(year, "\n", scales::comma(rooms))),
      vjust = -0.6,
      size  = 2.6,
      color = census_color,
      show.legend = FALSE
    ) +
    scale_color_manual(
      values = c(
        "USVIBER survey"    = pal$rooms,
        "Census guestrooms" = census_color
      )
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2024, 4),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = label_comma(),
      expand = expansion(mult = c(0.02, 0.15))
    ) +
    labs(
      x       = NULL,
      y       = "Hotel / guestrooms",
      title   = "Accommodation Counts Measured by Two Distinct Sources",
      caption = source_note(
        "Source: USVIBER annual survey (continuous line); U.S. Census Economic Census (diamond points, different population)"
      )
    ) +
    theme_tw(mode)

  add_shocks(p, mode = mode)
}

# ---------------------------------------------------------------------------
# Fig 4 — Occupancy
# ---------------------------------------------------------------------------
plot_occupancy <- function(mode = "light") {
  pal      <- tw_palette(mode)
  visitors <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)
  hotel    <- read_csv("data/processed/hotel_annual.csv",    show_col_types = FALSE)

  df_usviber <- visitors |>
    select(year, occupancy_rate_pct) |>
    filter(!is.na(occupancy_rate_pct))

  df_hotel <- hotel |>
    select(year, occupancy_pct, occ_calculated) |>
    filter(!is.na(occupancy_pct) | !is.na(occ_calculated))

  ann_pts <- df_usviber |>
    filter(year %in% c(2016, max(df_usviber$year)))

  occ2_color <- if (mode == "light") "#2a9bab" else "#5ed4e0"

  p <- ggplot() +
    geom_line(
      data      = df_usviber,
      aes(x = year, y = occupancy_rate_pct, color = "USVIBER indicator"),
      linewidth = 1.2,
      na.rm     = TRUE
    ) +
    geom_line(
      data      = df_hotel |> filter(!is.na(occupancy_pct)),
      aes(x = year, y = occupancy_pct, color = "Hotel PDF report"),
      linewidth = 0.9,
      linetype  = "dashed",
      na.rm     = TRUE
    ) +
    geom_line(
      data      = df_hotel |> filter(!is.na(occ_calculated)),
      aes(x = year, y = occ_calculated, color = "Calculated"),
      linewidth = 0.9,
      linetype  = "dotted",
      na.rm     = TRUE
    ) +
    geom_point(
      data  = ann_pts,
      aes(x = year, y = occupancy_rate_pct),
      color = pal$occupancy,
      size  = 2.4,
      na.rm = TRUE
    ) +
    geom_text(
      data  = ann_pts,
      aes(x = year, y = occupancy_rate_pct,
          label = paste0(round(occupancy_rate_pct, 1), "%")),
      vjust  = -0.9,
      size   = 2.8,
      color  = pal$occupancy,
      show.legend = FALSE
    ) +
    scale_color_manual(
      values = c(
        "USVIBER indicator" = pal$occupancy,
        "Hotel PDF report"  = occ2_color,
        "Calculated"        = pal$rooms
      )
    ) +
    coord_cartesian(ylim = c(0, 80)) +
    scale_x_continuous(
      breaks = seq(2000, 2025, 4),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = label_percent(scale = 1),
      expand = expansion(mult = c(0.02, 0.05))
    ) +
    labs(
      x       = NULL,
      y       = "Occupancy (%)",
      title   = "Occupancy Rose on a Smaller Inventory — Three Related Measures",
      caption = source_note(
        "Source: USVIBER annual indicator (solid); USVIBER hotel PDF reports (dashed); calculated from room-nights (dotted)"
      )
    ) +
    theme_tw(mode)

  add_shocks(p, mode = mode)
}

# ---------------------------------------------------------------------------
# Fig 5 — Island accommodation indexed (2016 = 100)
# ---------------------------------------------------------------------------
plot_island_hotel <- function(mode = "light") {
  pal <- tw_palette(mode)
  df  <- read_csv("data/processed/hotel_island_annual.csv", show_col_types = FALSE)

  base <- df |> filter(year == 2016)
  b_stt_avail <- base$stt_available
  b_stx_avail <- base$stx_available
  b_stt_occ   <- base$stt_occupied
  b_stx_occ   <- base$stx_occupied

  df_idx <- df |>
    filter(year >= 2007, year <= 2024) |>
    mutate(
      stt_available_idx = stt_available / b_stt_avail * 100,
      stx_available_idx = stx_available / b_stx_avail * 100,
      stt_occupied_idx  = stt_occupied  / b_stt_occ   * 100,
      stx_occupied_idx  = stx_occupied  / b_stx_occ   * 100
    ) |>
    select(year, stt_available_idx, stx_available_idx, stt_occupied_idx, stx_occupied_idx) |>
    pivot_longer(
      cols      = -year,
      names_to  = "series",
      values_to = "index"
    ) |>
    filter(!is.na(index)) |>
    mutate(
      series = recode(series,
        stt_available_idx = "STT available",
        stx_available_idx = "STX available",
        stt_occupied_idx  = "STT occupied",
        stx_occupied_idx  = "STX occupied"
      )
    )

  series_colors <- c(
    "STT available" = pal$air_visitors,
    "STX available" = pal$cruise,
    "STT occupied"  = pal$rooms,
    "STX occupied"  = pal$employment
  )
  series_ltype <- c(
    "STT available" = "solid",
    "STX available" = "solid",
    "STT occupied"  = "dashed",
    "STX occupied"  = "dashed"
  )

  # Endpoint labels with manual y nudges to separate overlapping labels
  endpoints <- df_idx |>
    group_by(series) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(nudge_y = case_when(
      series == "STT available" ~ -4,
      series == "STX available" ~  4,
      series == "STT occupied"  ~ -4,
      series == "STX occupied"  ~  4,
      TRUE ~ 0
    ))

  p <- ggplot(df_idx, aes(x = year, y = index, color = series, linetype = series)) +
    geom_hline(
      yintercept = 100,
      color      = pal$benchmark,
      linewidth  = 0.5
    ) +
    annotate(
      "text",
      x = 2024, y = 100,
      label = "2016 = 100",
      hjust = 1.0, vjust = -0.6,
      size  = 2.6,
      color = pal$benchmark
    ) +
    geom_line(linewidth = 1.0, na.rm = TRUE) +
    scale_color_manual(values = series_colors) +
    scale_linetype_manual(values = series_ltype) +
    geom_text(
      data  = endpoints,
      aes(label = series, y = index + nudge_y),
      hjust = -0.1,
      size  = 2.7,
      show.legend = FALSE
    ) +
    scale_x_continuous(
      breaks = seq(2007, 2024, 3),
      expand = expansion(mult = c(0.01, 0.20))
    ) +
    scale_y_continuous(
      expand = expansion(mult = c(0.05, 0.08))
    ) +
    labs(
      x       = NULL,
      y       = "Index (2016 = 100)",
      title   = "STX Room Capacity Largely Recovered; STT Has Not",
      caption = source_note(
        "Source: USVIBER hotel PDF reports; island-level series. Index: 2016 = 100."
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  add_shocks(p, mode = mode)
}


# ---------------------------------------------------------------------------
# Fig 3 — Accommodation capacity
