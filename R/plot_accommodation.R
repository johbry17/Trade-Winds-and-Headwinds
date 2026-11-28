# plot_accommodation.R — Fig 3 (capacity), Fig 4 (occupancy), Fig 5 (island hotel indexed)
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)
library(patchwork)

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
# plot_island_hotel <- function(mode = "light") {
#   pal <- tw_palette(mode)
#   df  <- read_csv("data/processed/hotel_island_annual.csv", show_col_types = FALSE)

#   base <- df |> filter(year == 2016)
#   b_stt_avail <- base$stt_available
#   b_stx_avail <- base$stx_available
#   b_stt_occ   <- base$stt_occupied
#   b_stx_occ   <- base$stx_occupied

#   df_idx <- df |>
#     filter(year >= 2007, year <= 2024) |>
#     mutate(
#       stt_available_idx = stt_available / b_stt_avail * 100,
#       stx_available_idx = stx_available / b_stx_avail * 100,
#       stt_occupied_idx  = stt_occupied  / b_stt_occ   * 100,
#       stx_occupied_idx  = stx_occupied  / b_stx_occ   * 100
#     ) |>
#     select(year, stt_available_idx, stx_available_idx, stt_occupied_idx, stx_occupied_idx) |>
#     pivot_longer(
#       cols      = -year,
#       names_to  = "series",
#       values_to = "index"
#     ) |>
#     filter(!is.na(index)) |>
#     mutate(
#       series = recode(series,
#         stt_available_idx = "STT available",
#         stx_available_idx = "STX available",
#         stt_occupied_idx  = "STT occupied",
#         stx_occupied_idx  = "STX occupied"
#       )
#     )

#   series_colors <- c(
#     "STT available" = pal$air_visitors,
#     "STX available" = pal$cruise,
#     "STT occupied"  = pal$rooms,
#     "STX occupied"  = pal$employment
#   )
#   series_ltype <- c(
#     "STT available" = "solid",
#     "STX available" = "solid",
#     "STT occupied"  = "dashed",
#     "STX occupied"  = "dashed"
#   )

#   # Endpoint labels with manual y nudges to separate overlapping labels
#   endpoints <- df_idx |>
#     group_by(series) |>
#     filter(year == max(year)) |>
#     ungroup() |>
#     mutate(nudge_y = case_when(
#       series == "STT available" ~ -4,
#       series == "STX available" ~  4,
#       series == "STT occupied"  ~ -4,
#       series == "STX occupied"  ~  4,
#       TRUE ~ 0
#     ))

#   p <- ggplot(df_idx, aes(x = year, y = index, color = series, linetype = series)) +
#     geom_hline(
#       yintercept = 100,
#       color      = pal$benchmark,
#       linewidth  = 0.5
#     ) +
#     annotate(
#       "text",
#       x = 2024, y = 100,
#       label = "2016 = 100",
#       hjust = 1.0, vjust = -0.6,
#       size  = 2.6,
#       color = pal$benchmark
#     ) +
#     geom_line(linewidth = 1.0, na.rm = TRUE) +
#     scale_color_manual(values = series_colors) +
#     scale_linetype_manual(values = series_ltype) +
#     geom_text(
#       data  = endpoints,
#       aes(label = series, y = index + nudge_y),
#       hjust = -0.1,
#       size  = 2.7,
#       show.legend = FALSE
#     ) +
#     scale_x_continuous(
#       breaks = seq(2007, 2024, 3),
#       expand = expansion(mult = c(0.01, 0.20))
#     ) +
#     scale_y_continuous(
#       expand = expansion(mult = c(0.05, 0.08))
#     ) +
#     labs(
#       x       = NULL,
#       y       = "Index (2016 = 100)",
#       title   = "STX Room Capacity Largely Recovered; STT Has Not",
#       caption = source_note(
#         "Source: USVIBER hotel PDF reports; island-level series. Index: 2016 = 100."
#       )
#     ) +
#     theme_tw(mode) +
#     theme(legend.position = "none")

#   add_shocks(p, mode = mode)
# }

plot_island_hotel <- function(mode = "light") {
  pal <- tw_palette(mode)
  df <- read_csv("data/processed/hotel_island_annual.csv", show_col_types = FALSE)

  base <- df |> filter(year == 2016)

  df_idx <- df |>
    filter(year >= 2007, year <= 2024) |>
    mutate(
      stt_available = stt_available / base$stt_available * 100,
      stt_occupied = stt_occupied / base$stt_occupied * 100,
      stx_available = stx_available / base$stx_available * 100,
      stx_occupied = stx_occupied / base$stx_occupied * 100
    ) |>
    select(year, stt_available, stt_occupied, stx_available, stx_occupied) |>
    pivot_longer(
      cols = -year,
      names_to = "series",
      values_to = "index"
    ) |>
    filter(!is.na(index)) |>
    mutate(
      island = if_else(
        startsWith(series, "stt"),
        "St. Thomas–St. John",
        "St. Croix"
      ),
      measure = if_else(
        endsWith(series, "_available"),
        "Available room-nights",
        "Occupied room-nights"
      )
    )

  series_colors <- c(
    "Available room-nights" = pal$air_visitors,
    "Occupied room-nights" = pal$rooms
  )

  series_linetypes <- c(
    "Available room-nights" = "solid",
    "Occupied room-nights" = "dashed"
  )

  endpoints <- df_idx |>
    group_by(island, measure) |>
    filter(year == max(year)) |>
    ungroup()

  stt <- df_idx |> filter(island == "St. Thomas–St. John")
  stx <- df_idx |> filter(island == "St. Croix")

  stt_end <- endpoints |> filter(island == "St. Thomas–St. John")
  stx_end <- endpoints |> filter(island == "St. Croix")

  make_panel <- function(panel_df, panel_end, panel_title) {
    p <- ggplot(
      panel_df,
      aes(x = year, y = index, color = measure, linetype = measure)
    ) +
      geom_hline(
        yintercept = 100,
        color = pal$benchmark,
        linewidth = 0.5
      ) +
      geom_line(linewidth = 1.05, na.rm = TRUE) +
      geom_point(
        data = panel_end,
        aes(x = year, y = index, color = measure, shape = measure),
        size = 2.2,
        na.rm = TRUE
      ) +
      geom_text(
        data = panel_end,
        aes(
          x = year,
          y = index,
          label = paste0(round(index), "%"),
          vjust = if_else(
            measure == "Occupied room-nights",
            -1.5,
            2.5
          )
        ),
        hjust = 0.25,
        size = 2.7,
        show.legend = FALSE
      ) +
      scale_color_manual(values = series_colors) +
      scale_linetype_manual(values = series_linetypes) +
      scale_shape_manual(values = c(
        "Available room-nights" = 16,
        "Occupied room-nights" = 1
      )) +
      coord_cartesian(ylim = c(25, 120)) +
      scale_x_continuous(
        breaks = c(2007, 2012, 2017, 2020, 2024),
        expand = expansion(mult = c(0.02, 0.08))
      ) +
      scale_y_continuous(labels = function(x) paste0(x, "%")) +
      labs(
        x = NULL,
        y = "Index (2016 = 100)",
        title = panel_title
      ) +
      theme_tw(mode) +
      theme(
        legend.position = "bottom",
        axis.text.x = if (panel_title == "St. Thomas–St. John") {
          element_blank()
        } else {
          element_text()
        },
        axis.ticks.x = if (panel_title == "St. Thomas–St. John") {
          element_blank()
        } else {
          element_line()
        }
      )

    p <- add_benchmark(p, y = 100, label = "2016 level", mode = mode)
    add_shocks(p, mode = mode)
  }

  p1 <- make_panel(stt, stt_end, "St. Thomas–St. John")
  p2 <- make_panel(stx, stx_end, "St. Croix")

  (p1 / p2) +
    plot_layout(
      ncol = 1,
      guides = "collect",
      heights = c(1, 1)
    ) +
    plot_annotation(
      title = "STX Capacity Recovered; STT Capacity Has Not",
      caption = source_note(
        "Source: USVIBER hotel PDF reports; available and occupied room-nights indexed separately to 2016 = 100."
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
}

# ---------------------------------------------------------------------------
# Fig 3 — Accommodation capacity
