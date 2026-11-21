# scales.R — Named color scale helpers
library(ggplot2)

source("R/palette.R")

# Color scale for the arrivals chart (air, cruise, total)
tw_scale_color_arrivals <- function(mode = "light") {
  pal <- tw_palette(mode)
  scale_color_manual(
    values = c(
      "Air visitors"      = pal$air_visitors,
      "Cruise passengers" = pal$cruise,
      "Total visitors"    = pal$total
    )
  )
}

# Color scale for the 6-series recovery chart
tw_scale_color_recovery <- function(mode = "light") {
  pal <- tw_palette(mode)
  scale_color_manual(
    values = c(
      "Air visitors"    = pal$air_visitors,
      "Cruise"          = pal$cruise,
      "Hotel rooms"     = pal$rooms,
      "L&H employment"  = pal$employment,
      "A&F value added" = pal$value_added,
      "NPS visits"      = pal$nps_viis
    )
  )
}
