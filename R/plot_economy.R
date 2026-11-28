# plot_economy.R — Fig 8 (GDP & A&F indexed) and Fig 9 (A&F share)
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(scales)

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")

# ---------------------------------------------------------------------------
# Fig 8 — GDP and A&F indexed to 2016 = 100
# ---------------------------------------------------------------------------
plot_gdp_af <- function(mode = "light") {
  pal <- tw_palette(mode)

  gdp <- read_csv("data/processed/bea_gdp_real.csv", show_col_types = FALSE) |>
    select(year, gdp_real) |>
    filter(!is.na(gdp_real))

  af  <- read_csv("data/processed/bea_af_real.csv",  show_col_types = FALSE) |>
    select(year, af_real) |>
    filter(!is.na(af_real))

  base_gdp <- gdp |> filter(year == 2016) |> pull(gdp_real)
  base_af  <- af  |> filter(year == 2016) |> pull(af_real)

  gdp_idx <- gdp |> mutate(index = gdp_real / base_gdp * 100, series = "Real GDP")
  af_idx  <- af  |> mutate(index = af_real  / base_af  * 100, series = "Real A&F value added")

  combined <- bind_rows(gdp_idx, af_idx)

  # Endpoint labels — different final years, manual nudges
  endpoints <- combined |>
    group_by(series) |>
    filter(year == max(year)) |>
    ungroup() |>
    mutate(nudge_y = case_when(
      series == "Real GDP" ~ 4,
      TRUE ~ -4
    ))

  p <- ggplot(combined, aes(x = year, y = index, color = series, linetype = series)) +
    geom_line(linewidth = 1.1, na.rm = TRUE) +
    scale_color_manual(
      values = c(
        "Real GDP"              = pal$gdp,
        "Real A&F value added"  = pal$value_added
      ),
      guide = "none"
    ) +
    scale_linetype_manual(
      values = c(
        "Real GDP"             = "solid",
        "Real A&F value added" = "dashed"
      ),
      guide = "none"
    ) +
    geom_text(
      data  = endpoints,
      aes(label = paste0(series, " (", year, ")"),
          y = index + nudge_y),
      hjust = -0.08,
      size  = 2.8,
      show.legend = FALSE
    ) +
    coord_cartesian(ylim = c(50, 180)) +
    scale_x_continuous(
      breaks = seq(2002, 2022, 4),
      expand = expansion(mult = c(0.01, 0.30))
    ) +
    scale_y_continuous(
      labels = function(x) paste0(x, "%"),
      expand = expansion(mult = c(0.02, 0.05))
    ) +
    labs(
      x       = NULL,
      y       = "Index (2016 = 100)",
      title   = "Territorial GDP and Industry Output Diverged After 2017",
      caption = source_note(paste0(
        "Source: BEA USVI GDP and industry tables; both series in real chained dollars. ",
        "GDP through 2022; A&F value added through 2021."
      ))
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  p <- add_benchmark(p, y = 100, label = "2016 level", mode = mode)
  add_shocks(p, mode = mode)
}

# ---------------------------------------------------------------------------
# Fig 9 — A&F share of nominal GDP
# ---------------------------------------------------------------------------
plot_af_share <- function(mode = "light") {
  pal <- tw_palette(mode)
  df  <- read_csv("data/processed/bea_af_share.csv", show_col_types = FALSE) |>
    filter(!is.na(af_pct_gdp))

  ref_val <- df |> filter(year == 2016) |> pull(af_pct_gdp)

  p <- ggplot(df, aes(x = year, y = af_pct_gdp)) +
    geom_hline(
      yintercept = ref_val,
      color      = pal$benchmark,
      linewidth  = 0.5,
      linetype   = "solid"
    ) +
    annotate(
      "text",
      x = 2004, y = ref_val,
      label = paste0("2016: ", round(ref_val, 1), "%"),
      hjust = 0, vjust = -0.6,
      size  = 2.6,
      color = pal$benchmark
    ) +
    geom_line(
      color     = pal$value_added,
      linewidth = 1.2,
      na.rm     = TRUE
    ) +
    coord_cartesian(ylim = c(0, 16)) +
    scale_x_continuous(
      breaks = seq(2002, 2022, 4),
      expand = expansion(mult = c(0.01, 0.05))
    ) +
    scale_y_continuous(
      labels = label_percent(scale = 1, accuracy = 0.1),
      expand = expansion(mult = c(0.02, 0.05))
    ) +
    labs(
      x       = NULL,
      y       = "Approximate share of nominal GDP (%)",
      title   = "Accommodation and Food Services as a Share of Nominal GDP",
      caption = source_note(
        "Source: BEA nominal A&F value added divided by nominal GDP; approximate industry share only"
      )
    ) +
    theme_tw(mode) +
    theme(legend.position = "none")

  add_shocks(p, mode = mode)
}


# ---------------------------------------------------------------------------
# Fig 8 — GDP and A&F indexed to 2016 = 100
