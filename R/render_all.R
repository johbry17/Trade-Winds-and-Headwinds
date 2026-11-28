# render_all.R — Generate all publication figures (light + dark variants)
# Run from project root: Rscript R/render_all.R

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(tidyr)
  library(scales)
  library(patchwork)
  library(ragg)
})

# Source all modules
source("R/palette.R")
source("R/theme_trade_winds.R")
source("R/annotations.R")
source("R/scales.R")
source("R/plot_visitors.R")
source("R/plot_accommodation.R")
source("R/plot_employment.R")
source("R/plot_economy.R")
source("R/plot_recovery.R")

# Ensure output directory exists
dir.create("figures/publication", recursive = TRUE, showWarnings = FALSE)

# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------
save_fig <- function(plot_obj, name, mode,
                     width = 9, height = 5.5, dpi = 300) {
  path <- file.path("figures", "publication",
                    paste0(name, "_", mode, ".png"))
  ggsave(
    filename = path,
    plot     = plot_obj,
    device   = ragg::agg_png,
    width    = width,
    height   = height,
    units    = "in",
    dpi      = dpi
  )
  cat("  Saved:", path, "\n")
  path
}

# ---------------------------------------------------------------------------
# Figure registry: list(name, fn, width, height)
# ---------------------------------------------------------------------------
figures <- list(
  list(name = "figOV_arrivals",             fn = plot_arrivals),
  list(name = "fig01_arrivals",             fn = plot_arrivals_comparison),
  list(name = "fig02_expenditure",          fn = plot_expenditure),
  list(name = "fig03_capacity",             fn = plot_capacity),
  list(name = "fig04_occupancy",            fn = plot_occupancy),
  list(name = "fig05_island_hotel",         fn = plot_island_hotel, height = 9),
  list(name = "fig06_fred_employment",      fn = plot_fred_employment, height = 4.5),
  list(name = "fig07_employment_comparison", fn = plot_employment_comparison),
  list(name = "fig07a_employment_sources", fn = plot_employment_sources),
  list(name = "fig08_gdp_af",              fn = plot_gdp_af),
  list(name = "fig09_af_share",            fn = plot_af_share),
  list(name = "fig10_recovery",            fn = plot_recovery, height = 10),
  list(name = "figOV_recovery",            fn = plot_overview_recovery)
)

# ---------------------------------------------------------------------------
# Render all figures × both modes
# ---------------------------------------------------------------------------
saved_paths <- character(0)

for (fig in figures) {
  w <- if (!is.null(fig$width))  fig$width  else 9
  h <- if (!is.null(fig$height)) fig$height else 5.5

  for (mode in c("light", "dark")) {
    cat("Rendering", fig$name, "-", mode, "...\n")
    tryCatch({
      p    <- fig$fn(mode)
      path <- save_fig(p, fig$name, mode, width = w, height = h)
      saved_paths <- c(saved_paths, path)
    }, error = function(e) {
      cat("  ERROR in", fig$name, mode, ":", conditionMessage(e), "\n")
    })
  }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
cat("\n=== Render complete ===\n")
cat(length(saved_paths), "figures saved to figures/publication/\n\n")
for (p in saved_paths) cat(" ", p, "\n")
