"""
src/charts.py — Trade Winds & Headwinds visual system.

Design principles
-----------------
- Editorial and polished: data-first, restrained, legible at publication size.
- Semantic palette: colours carry consistent meaning across all charts.
- Single source of truth for typography, spacing, gridlines, and annotations.
- Shock lines added once per chart; source notes added once per chart.
- No fixed pixel widths — Quarto handles responsive sizing via fig-width.
- Save publication figures with consistent high-res dimensions via save_fig().
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Semantic palette
# ---------------------------------------------------------------------------

PALETTE = {
    # Primary arrival-mode series
    "air_visitors":     "#1b7a8a",   # Caribbean teal   — reported air arrivals
    "cruise":           "#c85a1a",   # trade-wind orange — cruise passengers
    # Secondary visitor-type series
    "tourists":         "#1a4f72",   # deep ocean blue   — overnight tourists
    "air_excursionist": "#2d9e6b",   # sea-green         — air same-day visitors
    "total":            "#4a4e69",   # slate purple      — aggregate totals
    # Context / economic series
    "employment":       "#7b4f9e",   # violet            — L&H employment
    "rooms":            "#2a7a3b",   # dark green        — accommodation inventory
    "occupancy":        "#0d6b7a",   # deep teal
    "value_added":      "#1a4f72",   # shares ocean blue (rarely same chart as tourists)
    "gdp":              "#4a4e69",   # shares slate (rarely same chart as total)
    "receipts":         "#1a4f72",
    # NPS park series
    "nps_viis":         "#2d9e6b",   # sea-green — matches St. John park
    "nps_buis":         "#c85a1a",   # orange    — matches St. Croix / cruise
    # Seasonal adjustment labels
    "sa":               "#1a4f72",
    "nsa":              "#c85a1a",
    # Scorecard status (non-primary series only)
    "above_baseline":   "#2a7a3b",   # dark green  — at or above 2016 level
    "below_baseline":   "#7f8c9a",   # blue-grey   — below 2016 level
}

# ---------------------------------------------------------------------------
# Typography and design tokens
# ---------------------------------------------------------------------------

FONT = (
    "Source Sans 3, Source Sans Pro, -apple-system, BlinkMacSystemFont, "
    "Segoe UI, Helvetica, Arial, sans-serif"
)

_GRID        = "#eeeeee"   # horizontal gridline colour
_AXIS_LINE   = "#d1d5db"   # axis border line colour
_SHOCK_LINE  = "#cccccc"   # vertical event line colour
_SHOCK_LABEL = "#aaaaaa"   # event annotation text colour
_SOURCE_COL  = "#aaaaaa"   # source note text colour

# ---------------------------------------------------------------------------
# Base Plotly template
# ---------------------------------------------------------------------------

_BASE_LAYOUT = dict(
    font=dict(family=FONT, size=12.5, color="#1f2937"),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    margin=dict(l=60, r=34, t=52, b=80),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.22,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0)",
        font=dict(size=10.5),
        itemsizing="constant",
        tracegroupgap=0,
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor=_AXIS_LINE,
        linewidth=1,
        ticks="outside",
        ticklen=4,
        tickcolor=_AXIS_LINE,
        tickfont=dict(size=11),
        title_font=dict(size=12),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=_GRID,
        gridwidth=1,
        zeroline=False,
        showline=False,
        ticks="",
        tickfont=dict(size=11),
        title_font=dict(size=12),
    ),
)

pio.templates["tw"] = go.layout.Template(layout=_BASE_LAYOUT)
pio.templates.default = "plotly_white+tw"

# ---------------------------------------------------------------------------
# Annotation helpers
# ---------------------------------------------------------------------------

def add_shocks(
    fig: go.Figure,
    shock_x: Sequence[int | str] = (2017, 2020),
    shock_labels: Sequence[str] = (" Irma & Maria", " COVID-19"),
) -> go.Figure:
    """
    Add vertical reference lines for major shock events.

    Labels are anchored to yref='paper' at y=1.0 so they always appear at the
    top of the plot area, independent of the y-axis scale, and are never clipped
    by the axis range.  For monthly x-axes, pass ISO date strings, e.g. '2017-09'.
    """
    for x_val, label in zip(shock_x, shock_labels):
        fig.add_vline(x=x_val, line=dict(color=_SHOCK_LINE, width=1.0))
        fig.add_annotation(
            x=x_val, xref="x",
            y=1.0, yref="paper",
            text=f"<i>{label}</i>",
            showarrow=False,
            font=dict(size=9, color=_SHOCK_LABEL),
            xanchor="left",
            yanchor="top",
            xshift=4,
            yshift=-4,
        )
    return fig


# Backward-compatible alias used in older notebook cells.
_add_shock_lines = add_shocks


def source_note(text: str, y: float = -0.09) -> dict:
    """
    Return a source annotation dict for passing to annotations=[].

    Call this exactly once per chart.  The y parameter controls vertical
    position below the x-axis; adjust if the bottom margin differs from default.
    """
    return dict(
        xref="paper", yref="paper",
        x=0.0, y=y,
        text=f"<span style='color:{_SOURCE_COL};font-size:10px'>Source: {text}</span>",
        showarrow=False,
        xanchor="left",
        yanchor="top",
    )


def _source_annotation(text: str) -> dict:
    """Backward-compatible alias for source_note()."""
    return source_note(text)


def _title_text(title: str, subtitle: str = "") -> str:
    if subtitle:
        return (
            f"<b>{title}</b>"
            f"<br><span style='font-size:12px;font-weight:400;color:#6b7280'>{subtitle}</span>"
        )
    return f"<b>{title}</b>"


# ---------------------------------------------------------------------------
# SHOCK_ANNOTATIONS — kept for backward compatibility with older notebooks
# ---------------------------------------------------------------------------

SHOCK_ANNOTATIONS = [
    dict(x="2017-09", label="Irma & Maria"),
    dict(x="2020-03", label="COVID-19"),
]

# ---------------------------------------------------------------------------
# Line chart
# ---------------------------------------------------------------------------

def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str | list[str],
    title: str,
    subtitle: str = "",
    y_label: str = "",
    x_label: str = "",
    colors: list[str] | None = None,
    names: list[str] | None = None,
    source: str = "",
    add_shock_lines: bool = True,
    shock_x: Sequence = (2017, 2020),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 440,
    mode: str = "lines+markers",
    line_widths: list[float] | None = None,
    opacities: list[float] | None = None,
) -> go.Figure:
    """Flexible line chart for one or more series."""
    if isinstance(y, str):
        y = [y]
    n = len(y)
    if colors is None:
        colors = list(PALETTE.values())[:n]
    if names is None:
        names = y
    if line_widths is None:
        line_widths = [2.2] * n
    if opacities is None:
        opacities = [1.0] * n

    fig = go.Figure()
    for col, color, name, lw, op in zip(y, colors, names, line_widths, opacities):
        valid = df[[x, col]].dropna()
        show_markers = len(valid) <= 30
        fig.add_trace(go.Scatter(
            x=valid[x], y=valid[col],
            mode=mode if show_markers else "lines",
            name=name, opacity=op,
            line=dict(color=color, width=lw),
            marker=dict(size=4.5, opacity=op),
        ))

    fig.update_layout(
        title=dict(text=_title_text(title, subtitle), font=dict(size=16), x=0.0, pad=dict(b=4)),
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
        annotations=[source_note(source)] if source else [],
    )
    if add_shock_lines:
        add_shocks(fig, shock_x, shock_labels)
    return fig


# ---------------------------------------------------------------------------
# Bar chart
# ---------------------------------------------------------------------------

def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    subtitle: str = "",
    y_label: str = "",
    x_label: str = "",
    color: str | None = None,
    source: str = "",
    add_shock_lines: bool = True,
    shock_x: Sequence = (2017, 2020),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 420,
) -> go.Figure:
    """Simple vertical bar chart."""
    bar_color = color or PALETTE["total"]
    valid = df[[x, y]].dropna()

    fig = go.Figure(go.Bar(
        x=valid[x], y=valid[y],
        marker_color=bar_color, name=y,
    ))
    fig.update_layout(
        title=dict(text=_title_text(title, subtitle), font=dict(size=16), x=0.0),
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
        bargap=0.28,
        annotations=[source_note(source)] if source else [],
    )
    if add_shock_lines:
        add_shocks(fig, shock_x, shock_labels)
    return fig


# ---------------------------------------------------------------------------
# Stacked area chart
# ---------------------------------------------------------------------------

def stacked_area(
    df: pd.DataFrame,
    x: str,
    y_cols: list[str],
    title: str,
    subtitle: str = "",
    y_label: str = "",
    source: str = "",
    colors: list[str] | None = None,
    names: list[str] | None = None,
    add_shock_lines: bool = True,
    shock_x: Sequence = (2017, 2020),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 440,
) -> go.Figure:
    """Stacked area chart with correct hex-to-rgba fill conversion."""
    n = len(y_cols)
    if colors is None:
        colors = list(PALETTE.values())[:n]
    if names is None:
        names = y_cols

    def _hex_to_rgba(hex_color: str, alpha: float = 0.65) -> str:
        h = hex_color.lstrip("#")
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"
        return hex_color

    fig = go.Figure()
    for col, color, name in zip(y_cols, colors, names):
        valid = df[[x, col]].dropna()
        fig.add_trace(go.Scatter(
            x=valid[x], y=valid[col],
            mode="lines", name=name,
            stackgroup="one",
            line=dict(color=color, width=1.0),
            fillcolor=_hex_to_rgba(color),
        ))

    fig.update_layout(
        title=dict(text=_title_text(title, subtitle), font=dict(size=16), x=0.0),
        yaxis_title=y_label,
        height=height,
        annotations=[source_note(source)] if source else [],
    )
    if add_shock_lines:
        add_shocks(fig, shock_x, shock_labels)
    return fig


# ---------------------------------------------------------------------------
# Index chart
# ---------------------------------------------------------------------------

def index_chart(
    df: pd.DataFrame,
    x: str,
    y_cols: list[str],
    base_year: int,
    title: str,
    subtitle: str = "",
    source: str = "",
    colors: list[str] | None = None,
    names: list[str] | None = None,
    add_shock_lines: bool = True,
    shock_x: Sequence = (2017, 2020),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 440,
) -> go.Figure:
    """Index chart: re-base each series to base_year = 100."""
    n = len(y_cols)
    if colors is None:
        colors = list(PALETTE.values())[:n]
    if names is None:
        names = y_cols

    fig = go.Figure()
    for col, color, name in zip(y_cols, colors, names):
        sub = df[[x, col]].dropna().copy()
        base_rows = sub[sub[x] == base_year]
        if base_rows.empty:
            continue
        base_val = base_rows[col].iloc[0]
        if base_val == 0 or pd.isna(base_val):
            continue
        sub["idx"] = sub[col] / base_val * 100
        show_markers = len(sub) <= 30
        fig.add_trace(go.Scatter(
            x=sub[x], y=sub["idx"],
            mode="lines+markers" if show_markers else "lines",
            name=name,
            line=dict(color=color, width=2.2),
            marker=dict(size=4.5),
        ))

    fig.add_hline(
        y=100,
        line=dict(color="#d1d5db", width=1.0, dash="dot"),
        annotation_text=f"{base_year} = 100",
        annotation_position="right",
        annotation_font=dict(size=9, color="#aaaaaa"),
    )
    fig.update_layout(
        title=dict(text=_title_text(title, subtitle), font=dict(size=16), x=0.0),
        yaxis_title=f"Index ({base_year} = 100)",
        height=height,
        annotations=[source_note(source)] if source else [],
    )
    if add_shock_lines:
        add_shocks(fig, shock_x, shock_labels)
    return fig


# ---------------------------------------------------------------------------
# Monthly heatmap
# ---------------------------------------------------------------------------

def monthly_heatmap(
    df: pd.DataFrame,
    year_col: str,
    month_col: str,
    value_col: str,
    title: str,
    subtitle: str = "",
    source: str = "",
    colorscale: str = "Blues",
    height: int = 500,
) -> go.Figure:
    """Year x month heatmap for monthly series (NPS, FRED)."""
    pivot = df.pivot(index=year_col, columns=month_col, values=value_col)
    pivot = pivot.sort_index(ascending=False)

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    x_labels = [month_labels[i - 1] for i in pivot.columns if 1 <= i <= 12]

    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=x_labels, y=pivot.index.tolist(),
        colorscale=colorscale,
        colorbar=dict(thickness=12, len=0.8),
        hovertemplate="%{y} %{x}: %{z:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=_title_text(title, subtitle), font=dict(size=16), x=0.0),
        height=height,
        margin=dict(l=60, r=24, t=80, b=56),
        xaxis=dict(side="top"),
        annotations=[source_note(source)] if source else [],
    )
    return fig


# ---------------------------------------------------------------------------
# Publication export
# ---------------------------------------------------------------------------

PUB_DIR = Path("figures/publication")


def save_fig(
    fig: go.Figure,
    name: str,
    formats: Sequence[str] = ("png",),
    width: int = 1300,
    height: int | None = None,
    scale: float = 2.0,
) -> None:
    """
    Save a finalised publication figure.

    Width defaults to 1300 px (at scale=2.0 this produces 2600 px effective
    resolution — suitable for high-DPI screens and print).  Height defaults to
    the figure's current layout height.
    Use sparingly: only for the final selection of publication charts.
    """
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    stem = PUB_DIR / name
    fig_height = height or fig.layout.height or 440

    if "html" in formats:
        fig.write_html(str(stem) + ".html", include_plotlyjs="cdn")
    if "png" in formats:
        fig.write_image(str(stem) + ".png", width=width, height=fig_height, scale=scale)
    if "svg" in formats:
        fig.write_image(str(stem) + ".svg", width=width, height=fig_height)

