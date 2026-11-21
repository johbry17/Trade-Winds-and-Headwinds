# annotations.R — Reusable annotation helpers
library(ggplot2)

source("R/palette.R")

# Add vertical shock lines with italic labels at the top.
# p        : a ggplot object
# x_vals   : numeric vector of x positions
# labels   : character vector of matching labels
# mode     : "light" or "dark"
# y_label  : y-coordinate for the text annotation (data coordinates)
add_shocks <- function(p, x_vals = c(2017, 2020),
                       labels = c("Irma & Maria", "COVID\u201319"),
                       mode = "light", y_label = NULL) {
  pal <- tw_palette(mode)

  for (i in seq_along(x_vals)) {
    p <- p +
      geom_vline(
        xintercept = x_vals[i],
        color      = pal$shock_line,
        linewidth  = 0.5,
        linetype   = "solid",
        alpha      = 0.7
      )
  }

  # Text labels — placed via annotate so y_label can be computed from built plot
  for (i in seq_along(x_vals)) {
    p <- p +
      annotate(
        "text",
        x      = x_vals[i] + 0.15,
        y      = Inf,
        label  = labels[i],
        vjust  = 1.4,
        hjust  = 0,
        size   = 2.6,
        color  = pal$shock_label,
        fontface = "italic"
      )
  }

  p
}

# Add a horizontal benchmark line (default y = 100) with a right-margin label.
# p     : a ggplot object
# y     : numeric y position
# label : annotation text
# mode  : "light" or "dark"
add_benchmark <- function(p, y = 100, label = "2016 = 100", mode = "light") {
  pal <- tw_palette(mode)

  p +
    geom_hline(
      yintercept = y,
      color      = pal$benchmark,
      linewidth  = 0.5,
      linetype   = "solid"
    ) +
    annotate(
      "text",
      x      = Inf,
      y      = y,
      label  = label,
      hjust  = 1.05,
      vjust  = -0.5,
      size   = 2.6,
      color  = pal$benchmark
    )
}

# Format a caption string for labs(caption = source_note(...))
source_note <- function(text) {
  paste0(text)
}
