# palette.R — Trade Winds & Headwinds color system
# Semantic colors match Python charts.py PALETTE

TW_PALETTE_LIGHT <- list(
  # Semantic series colors
  air_visitors  = "#1b7a8a",
  cruise        = "#c85a1a",
  total         = "#4a4e69",
  employment    = "#7b4f9e",
  rooms         = "#2a7a3b",
  occupancy     = "#0d6b7a",
  value_added   = "#1a4f72",
  gdp           = "#4a4e69",
  nps_viis      = "#2d9e6b",

  # Structural / annotation colors
  shock_line    = "#a09890",
  shock_label   = "#77736a",
  source_note   = "#77736a",
  benchmark     = "#b0a898",

  # Layout
  background    = "#f4f1eb",
  panel_bg      = "#fafaf8",
  grid_major_y  = "#dbd7cf",
  axis_line     = "#a09890",
  text_primary  = "#3d3933",
  text_title    = "#1a3a52",
  text_subtitle = "#6b6559",
  text_caption  = "#77736a",
  legend_text   = "#3d3933"
)

TW_PALETTE_DARK <- list(
  # Semantic series colors — lightened ~25% for dark backgrounds
  air_visitors  = "#35b8cc",
  cruise        = "#e88050",
  total         = "#7a7ea0",
  employment    = "#b07fd0",
  rooms         = "#52b86a",
  occupancy     = "#2eaabf",
  value_added   = "#3a80b0",
  gdp           = "#7a7ea0",
  nps_viis      = "#4dcf90",

  # Structural / annotation colors
  shock_line    = "#6a7a85",
  shock_label   = "#8b8077",
  source_note   = "#8b8077",
  benchmark     = "#4a6070",

  # Layout
  background    = "#0d1e2b",
  panel_bg      = "#0d1e2b",
  grid_major_y  = "#233548",
  axis_line     = "#3d5068",
  text_primary  = "#bbb6ae",
  text_title    = "#7dd4de",
  text_subtitle = "#8b8077",
  text_caption  = "#8b8077",
  legend_text   = "#bbb6ae"
)

tw_palette <- function(mode = "light") {
  if (mode == "dark") TW_PALETTE_DARK else TW_PALETTE_LIGHT
}
