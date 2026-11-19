# Field Notes Theme System

Six visual themes for the Field Notes / Studies publication series. Each is independently selectable and comes in light and dark variants.

---

## Themes

| Theme | Variant | Base | Character |
|-------|---------|------|-----------|
| **Archipelago** | Light | cosmo | Warm limestone, deep navy, sea-glass teal |
| **Archipelago** | Dark | darkly | Deep ocean night, teal, warm coral |
| **Field Journal** | Light | cosmo | Parchment, forest green, rust, ochre |
| **Field Journal** | Dark | darkly | Deep charcoal-brown, sage, ochre |
| **Observatory** | Light | cosmo | Cool white, charcoal, cobalt, burnt orange |
| **Observatory** | Dark | darkly | Near-black cool, cobalt, burnt orange |

---

## File Architecture

```
themes/
  _base.scss                   Shared component styles (layout, tables, callouts, etc.)
  archipelago-light.scss       Complete standalone theme — light
  archipelago-dark.scss        Complete standalone theme — dark
  field-journal-light.scss     Complete standalone theme — light
  field-journal-dark.scss      Complete standalone theme — dark
  observatory-light.scss       Complete standalone theme — light
  observatory-dark.scss        Complete standalone theme — dark
  README.md                    This file
  plot-styling-guide.md        Plot style guide for all six themes
```

Each theme file is **self-contained**. It includes:

1. `/*-- scss:defaults --*/` — Bootstrap variable overrides (colors, fonts, border-radius, etc.)
2. `/*-- scss:rules --*/` — Custom CSS rules, followed by `@import 'base'` for shared components

The `_base.scss` partial contains structural rules shared across all themes: figure margins, table formatting, TOC styling, navbar, footer layout, callout adjustments, and mobile responsive footer.

### Bootstrap base selection

| Variant | Bootstrap base | Rationale |
|---------|---------------|-----------|
| Light | `cosmo` | Clean, modern, good grid. Dark-variable overrides are minimal. |
| Dark | `darkly` | Provides Bootstrap dark-mode foundation — dark component backgrounds, correct foreground contrast tokens. Each theme then fine-tunes the palette. |

---

## Switching Themes

### Production site (committed to `docs/`)

Edit `_quarto.yml` → change the `format.html.theme` line:

```yaml
format:
  html:
    theme: 
      light: [cosmo, themes/archipelago-light.scss]   # ← change this line
      dark: [darkly, themes/archipelago-dark.scss]    # ← change this line
```

| To use… | Set theme to… |
|---------|--------------|
| Archipelago Light | `[cosmo, themes/archipelago-light.scss]` |
| Archipelago Dark | `[darkly, themes/archipelago-dark.scss]` |
| Field Journal Light | `[cosmo, themes/field-journal-light.scss]` |
| Field Journal Dark | `[darkly, themes/field-journal-dark.scss]` |
| Observatory Light | `[cosmo, themes/observatory-light.scss]` |
| Observatory Dark | `[darkly, themes/observatory-dark.scss]` |

For only a dark theme, also change `respect-user-color-scheme: false`.

```yaml
format:
  html:
    theme: [darkly, themes/archipelago-dark.scss]    # ← change this line
  respect-user-color-scheme: false
```

---

## Adding a New Theme

1. Create `themes/my-new-theme.scss` with the same `/*-- scss:defaults --*/` and `/*-- scss:rules --*/` structure.
2. Add `@import 'base';` near the top of the `scss:rules` section.

You do **not** need to modify `_base.scss` or any existing theme.

---

## Color Variables Reference

Each theme defines its own private color variables (prefixed `$archi-`, `$fj-`, or `$obs-`). These do not conflict across themes since each file is processed independently.

Key Bootstrap variables overridden in every theme:

| Variable | Purpose |
|---------|---------|
| `$primary` | Primary brand / button color |
| `$body-bg` | Page background |
| `$body-color` | Main body text |
| `$link-color` | Link color |
| `$border-color` | Borders and rules |
| `$headings-font-family` | Heading typeface stack |
| `$headings-color` | Heading color |
| `$navbar-bg` | Navbar background |
| `$card-bg` | Card / panel background |
| `$code-color` | Inline code color |

---

## Plot Palette Coordination

See `plot-styling-guide.md` in this folder for ggplot2 color palettes matched to each theme variant, and practical R code for each chart type.
