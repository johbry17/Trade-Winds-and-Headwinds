# render_experimental.R — Render original and experimental priority charts
# Run from project root: Rscript R/render_experimental.R
# Outputs only to figures/experimental/; never writes publication figures.

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(tidyr)
  library(scales)
  library(patchwork)
  library(ragg)
})

source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")
source("R/scales.R")

# Original publication functions
source("R/plot_accommodation.R")
source("R/plot_recovery.R")

# Experimental alternatives
source("archive/experimental-plots/plot_accommodation_alt.R")
source("archive/experimental-plots/plot_recovery_alt.R")

dir.create("archive/experimental-plots/figures", recursive = TRUE, showWarnings = FALSE)

save_png <- function(plot_obj, name, mode, width, height) {
  path <- file.path(
    "archive",
    "experimental-plots",
    "figures",
    paste0(name, "_", mode, ".png")
  )
  ggsave(
    filename = path,
    plot = plot_obj,
    device = ragg::agg_png,
    width = width,
    height = height,
    units = "in",
    dpi = 300
  )
  cat("Saved:", path, "\n")
  invisible(path)
}

for (mode in c("light", "dark")) {
  cat("Rendering experimental comparisons -", mode, "...\n")

  # Fig 3: capacity
  capacity_original <- plot_capacity(mode)
  capacity_alt <- plot_capacity_alt(mode)
  save_png(capacity_original, "fig03_capacity_original", mode, 9, 5.5)
  save_png(capacity_alt, "fig03_capacity_alt", mode, 9, 5.5)
  save_png(
    capacity_original + capacity_alt,
    "fig03_capacity_comparison",
    mode,
    18,
    5.5
  )

  # Fig 4: occupancy
  occupancy_original <- plot_occupancy(mode)
  occupancy_alt <- plot_occupancy_alt(mode)
  save_png(occupancy_original, "fig04_occupancy_original", mode, 9, 5.5)
  save_png(occupancy_alt, "fig04_occupancy_alt", mode, 9, 5.5)
  save_png(
    occupancy_original + occupancy_alt,
    "fig04_occupancy_comparison",
    mode,
    18,
    5.5
  )

  # Fig 5: island accommodation
  island_original <- plot_island_hotel(mode)
  island_alt <- plot_island_hotel_alt(mode)
  save_png(island_original, "fig05_island_hotel_original", mode, 9, 6.5)
  save_png(island_alt, "fig05_island_hotel_alt", mode, 9, 9)
  save_png(
    island_original + island_alt,
    "fig05_island_hotel_comparison",
    mode,
    18,
    6.5
  )

  # Fig 10: recovery
  recovery_original <- plot_recovery(mode)
  recovery_alt <- plot_recovery_alt(mode)
  save_png(recovery_original, "fig10_recovery_original", mode, 9, 5.5)
  save_png(recovery_alt, "fig10_recovery_alt", mode, 9, 10)
  save_png(
    recovery_original + recovery_alt,
    "fig10_recovery_comparison",
    mode,
    18,
    10
  )
}

cat("\nExperimental render complete.\n")
