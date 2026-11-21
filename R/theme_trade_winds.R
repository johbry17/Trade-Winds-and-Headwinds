# theme_trade_winds.R — ggplot2 theme for Trade Winds & Headwinds
library(ggplot2)

source("R/palette.R")

theme_tw <- function(mode = "light", base_size = 11.5) {
  pal <- tw_palette(mode)

  base <- theme_minimal(base_size = base_size) +
    theme(
      # Backgrounds
      plot.background  = element_rect(fill = pal$background, color = NA),
      panel.background = element_rect(fill = pal$panel_bg, color = NA),

      # Gridlines
      panel.grid.major.y = element_line(color = pal$grid_major_y, linewidth = 0.5),
      panel.grid.major.x = element_blank(),
      panel.grid.minor   = element_blank(),

      # Axes
      axis.line.x  = element_line(color = pal$axis_line, linewidth = 0.5),
      axis.line.y  = element_blank(),
      axis.ticks   = element_blank(),
      axis.text    = element_text(color = pal$text_primary, size = rel(0.88)),
      axis.title   = element_text(color = pal$text_primary, size = rel(0.9), face = "plain"),
      axis.title.x = element_text(margin = margin(t = 6)),
      axis.title.y = element_text(margin = margin(r = 8)),

      # Titles
      plot.title    = element_text(
        color = pal$text_title,
        size  = rel(1.15),
        face  = "bold",
        hjust = 0,
        margin = margin(b = 4)
      ),
      plot.subtitle = element_text(
        color = pal$text_subtitle,
        size  = rel(0.88),
        hjust = 0,
        margin = margin(b = 8)
      ),
      plot.caption  = element_text(
        color  = pal$text_caption,
        size   = rel(0.72),
        hjust  = 0,
        margin = margin(t = 8)
      ),

      # Legend
      legend.position   = "bottom",
      legend.text       = element_text(color = pal$legend_text, size = rel(0.82)),
      legend.title      = element_blank(),
      legend.key.width  = unit(22, "pt"),
      legend.spacing.x  = unit(6, "pt"),
      legend.background = element_rect(fill = pal$background, color = NA),
      legend.key        = element_rect(fill = pal$background, color = NA),

      # Margins
      plot.margin = margin(10, 28, 10, 12)
    )

  base
}
