# plot_accommodation_alt.R — Experimental alternatives for Figures 3-5
# This file is additive: it does not modify or call publication render functions.
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)
library(patchwork)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")


# Alternative to Fig 3: keep USVIBER continuous and separate Census observations
# with shape, marker size, direct labels, and one compact source annotation.
plot_capacity_alt <- function(mode = "light") {
  pal <- tw_palette(mode)
  visitors <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)
  census <- read_csv("data/processed/census_rooms.csv", show_col_types = FALSE)

  census_color <- if (mode == "light") "#4a7a53" else "#7ad09a"
  usviber <- visitors |>
    select(year, hotel_rooms) |>
    filter(!is.na(hotel_rooms))

  census_labels <- census |>
    mutate(
      label = paste0(year, "  ", comma(rooms)),
      nudge_y = ifelse(year == 2017, -230, 220)
    )

  p <- ggplot() +
    geom_line(
      data = usviber,
      aes(x = year, y = hotel_rooms, color = "USVIBER survey"),
      linewidth = 1.15,
      na.rm = TRUE
    ) +
    geom_point(
      data = usviber |> filter(year %% 2 == 0),
      aes(x = year, y = hotel_rooms, color = "USVIBER survey"),
      shape = 16,
      size = 1.5,
      na.rm = TRUE
    ) +
    geom_point(
      data = census,
      aes(x = year, y = rooms, color = "Census guestrooms"),
      shape = 18,
      size = 4.2,
      na.rm = TRUE
    ) +
    geom_text(
      data = census_labels,
      aes(x = year, y = rooms + nudge_y, label = label),
      color = census_color,
      size = 2.7,
      lineheight = 0.9,
      hjust = 0.5,
      show.legend = FALSE
    ) +
    annotate(
      "text",
      x = 2001,
      y = 2400,
      label = "Different populations",
      hjust = 0,
      vjust = 0,
      size = 2.8,
      fontface = "italic",
      color = pal$text_subtitle
    ) +
    scale_color_manual(
      values = c(
        "USVIBER survey" = pal$rooms,
        "Census guestrooms" = census_color
      ),
      breaks = c("USVIBER survey", "Census guestrooms")
    ) +
    scale_x_continuous(
      breaks = seq(2000, 2024, 4),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = comma,
      expand = expansion(mult = c(0.04, 0.12))
    ) +
    labs(
      x = NULL,
      y = "Hotel rooms / guestrooms",
      title = "USVIBER Inventory Fell While Census Guestrooms Were Reported at Discrete Vintages",
      caption = source_note(
        "Source: USVIBER annual survey (continuous); U.S. Census Economic Census (discrete diamond observations)."
      )
    ) +
    theme_tw(mode)

  add_shocks(p, mode = mode)
}


# Alternative to Fig 4: retain the three encodings, add endpoint labels and
# source-specific markers rather than relying on a legend or caption.
plot_occupancy_alt <- function(mode = "light") {
  pal <- tw_palette(mode)
  visitors <- read_csv("data/processed/visitors_annual.csv", show_col_types = FALSE)
  hotel <- read_csv("data/processed/hotel_annual.csv", show_col_types = FALSE)

  annual <- visitors |>
    select(year, occupancy_rate_pct) |>
    filter(!is.na(occupancy_rate_pct))

  hotel_pdf <- hotel |>
    select(year, occupancy_pct) |>
    filter(!is.na(occupancy_pct))

  calculated <- hotel |>
    select(year, occ_calculated) |>
    filter(!is.na(occ_calculated))

  annual_end <- annual |> filter(year == 2024)
  pdf_end <- hotel_pdf |> filter(year == 2024)
  calc_end <- calculated |> filter(year == 2024)

  pdf_color <- if (mode == "light") "#2a9bab" else "#5ed4e0"

  p <- ggplot() +
    geom_line(
      data = annual,
      aes(x = year, y = occupancy_rate_pct, color = "USVIBER annual indicator"),
      linewidth = 1.25,
      lineend = "round",
      na.rm = TRUE
    ) +
    geom_point(
      data = annual |> filter(year %in% c(2016, 2024)),
      aes(x = year, y = occupancy_rate_pct, color = "USVIBER annual indicator"),
      shape = 16,
      size = 2.2,
      na.rm = TRUE
    ) +
    geom_line(
      data = hotel_pdf,
      aes(x = year, y = occupancy_pct, color = "Hotel PDF report"),
      linewidth = 0.95,
      linetype = "dashed",
      na.rm = TRUE
    ) +
    geom_point(
      data = pdf_end,
      aes(x = year, y = occupancy_pct, color = "Hotel PDF report"),
      shape = 1,
      size = 2.1,
      na.rm = TRUE
    ) +
    geom_line(
      data = calculated,
      aes(x = year, y = occ_calculated, color = "Calculated from room-nights"),
      linewidth = 0.95,
      linetype = "dotted",
      na.rm = TRUE
    ) +
    geom_point(
      data = calc_end,
      aes(x = year, y = occ_calculated, color = "Calculated from room-nights"),
      shape = 4,
      size = 2.1,
      na.rm = TRUE
    ) +
    geom_text(
      data = annual_end,
      aes(
        x = year,
        y = occupancy_rate_pct + 2.5,
        label = paste0(round(occupancy_rate_pct, 1), "%"),
        color = "USVIBER annual indicator"
      ),
      hjust = 0,
      vjust = 0.5,
      size = 2.8,
      show.legend = FALSE
    ) +
    geom_text(
      data = pdf_end,
      aes(
        x = year + 0.2,
        y = occupancy_pct - 2.5,
        label = paste0(round(occupancy_pct, 1), "%"),
        color = "Hotel PDF report"
      ),
      hjust = 0,
      vjust = 0.5,
      size = 2.7,
      show.legend = FALSE
    ) +
    geom_text(
      data = calc_end,
      aes(
        x = year + 0.2,
        y = occ_calculated - 5.0,
        label = paste0(round(occ_calculated, 1), "%"),
        color = "Calculated from room-nights"
      ),
      hjust = 0,
      vjust = 0.5,
      size = 2.7,
      show.legend = FALSE
    ) +
    scale_color_manual(
      values = c(
        "USVIBER annual indicator" = pal$occupancy,
        "Hotel PDF report" = pdf_color,
        "Calculated from room-nights" = pal$rooms
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
      x = NULL,
      y = "Occupancy (%)",
      title = "Three Occupancy Measures Rose, but They Are Not Interchangeable",
      caption = source_note(
        "Source: USVIBER annual indicator (solid/circles); hotel PDF reports (dashed/open circles); room-night calculation (dotted/crosses)."
      )
    ) +
    theme_tw(mode)

  add_shocks(p, mode = mode)
}


# Experimental Fig 5: two-panel STT / STX small multiples with a shared scale.
plot_island_hotel_alt <- function(mode = "light") {
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
      island = if_else(startsWith(series, "stt"), "St. Thomas–St. John", "St. Croix"),
      measure = if_else(endsWith(series, "_available"), "Available room-nights", "Occupied room-nights")
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
      geom_hline(yintercept = 100, color = pal$benchmark, linewidth = 0.5) +
      geom_line(linewidth = 1.05, na.rm = TRUE) +
      geom_point(
        data = panel_end,
        aes(x = year, y = index, color = measure, shape = measure),
        size = 2.2,
        na.rm = TRUE
      ) +
      geom_text(
        data = panel_end,
        aes(x = year, y = index, label = paste0(round(index), "%")),
        hjust = 1.1,
        vjust = c(-0.7, 1.5),
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

    add_shocks(p, mode = mode)
  }

  p1 <- make_panel(stt, stt_end, "St. Thomas–St. John")
  p2 <- make_panel(stx, stx_end, "St. Croix")

  combined <- (p1 / p2) +
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

  combined
}
