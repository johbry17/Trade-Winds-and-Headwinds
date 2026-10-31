"""
src/charts.py
Reusable Plotly charting functions for Trade Winds & Headwinds.

Design principles
-----------------
- Production-quality from the first exploratory pass.
- Consistent palette, typography, and event annotation across all charts.
- No dual axes.  Use facets or separate charts when scales differ.
- Explicit units, subtitles, and source notes on every chart.
- Monthly data uses monthly resolution; annual data uses annual resolution.
- Save publication figures only when explicitly requested via `save_fig()`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Theme and palette
# ---------------------------------------------------------------------------

PALETTE = {
    "tourists":        "#1a4f72",   # deep ocean blue
    "cruise":          "#c85a1a",   # trade-wind orange
    "air_excursionist":"#2a7a3b",   # green
    "total":           "#4a4e69",   # slate purple
    "employment":      "#c85a1a",
    "rooms":           "#2a7a3b",
    "occupancy":       "#1a4f72",
    "receipts":        "#1a4f72",
    "gdp":             "#4a4e69",
    "value_added":     "#1a4f72",
    "nps_viis":        "#1a4f72",
    "nps_buis":        "#c85a1a",
    "sa":              "#1a4f72",
    "nsa":             "#c85a1a",
    "annotation_line": "#888888",
}

FONT_FAMILY = (
    "Source Sans 3, Source Sans Pro, -apple-system, BlinkMacSystemFont, "
    "Segoe UI, Helvetica, Arial, sans-serif"
)

_BASE_LAYOUT = dict(
    font=dict(family=FONT_FAMILY, size=13, color="#1a1a2e"),
    plot_bgcolor="#fafafa",
    paper_bgcolor="#ffffff",
    margin=dict(l=60, r=30, t=100, b=60),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.02,
        xanchor="right",
        x=1.0,
        bgcolor="rgba(255,255,255,0)",
    ),
    xaxis=dict(showgrid=True, gridcolor="#e8e8e8", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#e8e8e8", zeroline=False),
)

# Register a custom template
pio.templates["tw"] = go.layout.Template(layout=_BASE_LAYOUT)
pio.templates.default = "plotly_white+tw"


# ---------------------------------------------------------------------------
# Shared event annotations
# ---------------------------------------------------------------------------

SHOCK_ANNOTATIONS = [
    dict(
        x="2017-09", type="line",
        label="Hurricanes Irma & Maria",
        color="#b22222", dash="dash",
    ),
    dict(
        x="2020-03", type="line",
        label="COVID-19",
        color="#555555", dash="dot",
    ),
]


def _add_shock_lines(
    fig: go.Figure,
    shock_x_values: Sequence[str | int | float],
    shock_labels: Sequence[str],
    shock_colors: Sequence[str] | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """Add vertical reference lines for major shocks."""
    colors = shock_colors or ["#b22222", "#555555"]
    for x_val, label, color in zip(shock_x_values, shock_labels, colors):
        fig.add_vline(
            x=x_val,
            line=dict(color=color, width=1.5, dash="dash"),
            annotation_text=label,
            annotation_position="top",
            annotation_font=dict(size=10, color=color),
            row=row, col=col,
        )
    return fig


def _source_annotation(source: str) -> dict:
    return dict(
        xref="paper", yref="paper",
        x=0, y=-0.08,
        text=f"<span style='color:#888;font-size:11px'>Source: {source}</span>",
        showarrow=False,
        xanchor="left",
    )


# ---------------------------------------------------------------------------
# Core chart builders
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
    add_shocks: bool = True,
    shock_x: Sequence = ("2017", "2020"),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 480,
    width: int = 900,
    mode: str = "lines+markers",
) -> go.Figure:
    """
    Flexible line chart for one or more series.

    Parameters
    ----------
    df : DataFrame
    x  : column name for x-axis
    y  : single column name or list of column names
    """
    if isinstance(y, str):
        y = [y]
    if colors is None:
        color_seq = list(PALETTE.values())
        colors = color_seq[: len(y)]
    if names is None:
        names = y

    fig = go.Figure()
    for col, color, name in zip(y, colors, names):
        valid = df[[x, col]].dropna()
        fig.add_trace(
            go.Scatter(
                x=valid[x],
                y=valid[col],
                mode=mode,
                name=name,
                line=dict(color=color, width=2.5),
                marker=dict(size=5),
            )
        )

    full_title = title + (f"<br><span style='font-size:13px;color:#555'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(size=17), x=0.0),
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
        width=width,
        annotations=[_source_annotation(source)] if source else [],
    )

    if add_shocks:
        for x_val, label in zip(shock_x, shock_labels):
            fig.add_vline(
                x=x_val,
                line=dict(color="#999999", width=1.5, dash="dash"),
                annotation_text=label,
                annotation_position="top",
                annotation_font=dict(size=10, color="#666"),
            )

    return fig


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
    add_shocks: bool = True,
    shock_x: Sequence = ("2017", "2020"),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 440,
    width: int = 900,
) -> go.Figure:
    """Simple vertical bar chart."""
    bar_color = color or PALETTE["total"]
    valid = df[[x, y]].dropna()

    fig = go.Figure(
        go.Bar(x=valid[x], y=valid[y], marker_color=bar_color, name=y)
    )
    full_title = title + (f"<br><span style='font-size:13px;color:#555'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(size=17), x=0.0),
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
        width=width,
        annotations=[_source_annotation(source)] if source else [],
        bargap=0.25,
    )

    if add_shocks:
        for x_val, label in zip(shock_x, shock_labels):
            fig.add_vline(
                x=x_val,
                line=dict(color="#999999", width=1.5, dash="dash"),
                annotation_text=label,
                annotation_position="top",
                annotation_font=dict(size=10, color="#666"),
            )

    return fig


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
    add_shocks: bool = True,
    shock_x: Sequence = ("2017", "2020"),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 480,
    width: int = 900,
) -> go.Figure:
    """Stacked area chart."""
    if colors is None:
        color_seq = list(PALETTE.values())
        colors = color_seq[: len(y_cols)]
    if names is None:
        names = y_cols

    fig = go.Figure()
    for col, color, name in zip(y_cols, colors, names):
        valid = df[[x, col]].dropna()
        fig.add_trace(
            go.Scatter(
                x=valid[x],
                y=valid[col],
                mode="lines",
                name=name,
                stackgroup="one",
                line=dict(color=color, width=1),
                fillcolor=color.replace(")", ", 0.7)").replace("rgb", "rgba")
                if color.startswith("rgb") else color,
            )
        )

    full_title = title + (f"<br><span style='font-size:13px;color:#555'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(size=17), x=0.0),
        yaxis_title=y_label,
        height=height,
        width=width,
        annotations=[_source_annotation(source)] if source else [],
    )

    if add_shocks:
        for x_val, label in zip(shock_x, shock_labels):
            fig.add_vline(
                x=x_val,
                line=dict(color="#999", width=1.5, dash="dash"),
                annotation_text=label,
                annotation_position="top",
                annotation_font=dict(size=10, color="#666"),
            )

    return fig


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
    add_shocks: bool = True,
    shock_x: Sequence = ("2017", "2020"),
    shock_labels: Sequence = ("Irma & Maria", "COVID-19"),
    height: int = 480,
    width: int = 900,
) -> go.Figure:
    """
    Index chart: re-base each series to base_year = 100.

    Only years with a non-null base-year value are indexed.
    """
    if colors is None:
        color_seq = list(PALETTE.values())
        colors = color_seq[: len(y_cols)]
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
        sub["indexed"] = sub[col] / base_val * 100
        fig.add_trace(
            go.Scatter(
                x=sub[x],
                y=sub["indexed"],
                mode="lines+markers",
                name=name,
                line=dict(color=color, width=2.5),
                marker=dict(size=5),
            )
        )

    # Base-year reference line
    fig.add_hline(
        y=100,
        line=dict(color="#cccccc", width=1, dash="dot"),
        annotation_text=f"{base_year} = 100",
        annotation_position="right",
        annotation_font=dict(size=10, color="#999"),
    )

    full_title = (
        title
        + f" (index, {base_year} = 100)"
        + (f"<br><span style='font-size:13px;color:#555'>{subtitle}</span>" if subtitle else "")
    )
    fig.update_layout(
        title=dict(text=full_title, font=dict(size=17), x=0.0),
        yaxis_title=f"Index ({base_year} = 100)",
        height=height,
        width=width,
        annotations=[_source_annotation(source)] if source else [],
    )

    if add_shocks:
        for x_val, label in zip(shock_x, shock_labels):
            fig.add_vline(
                x=x_val,
                line=dict(color="#999", width=1.5, dash="dash"),
                annotation_text=label,
                annotation_position="top",
                annotation_font=dict(size=10, color="#666"),
            )

    return fig


def monthly_heatmap(
    df: pd.DataFrame,
    year_col: str,
    month_col: str,
    value_col: str,
    title: str,
    subtitle: str = "",
    source: str = "",
    colorscale: str = "Blues",
    height: int = 480,
    width: int = 900,
) -> go.Figure:
    """Year × month heatmap for monthly series (NPS, FRED)."""
    pivot = df.pivot(index=year_col, columns=month_col, values=value_col)
    pivot = pivot.sort_index(ascending=False)  # newest year at top

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    x_labels = [month_labels[i - 1] for i in pivot.columns if 1 <= i <= 12]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=x_labels,
            y=pivot.index.tolist(),
            colorscale=colorscale,
            colorbar=dict(title=value_col),
            hovertemplate="%{y} %{x}: %{z:,.0f}<extra></extra>",
        )
    )
    full_title = title + (f"<br><span style='font-size:13px;color:#555'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(size=17), x=0.0),
        height=height, width=width,
        xaxis=dict(side="top"),
        annotations=[_source_annotation(source)] if source else [],
    )
    return fig


# ---------------------------------------------------------------------------
# Publication export
# ---------------------------------------------------------------------------

PUB_DIR = Path("figures/publication")


def save_fig(
    fig: go.Figure,
    name: str,
    formats: Sequence[str] = ("html", "png"),
    width: int = 1100,
    height: int = 550,
    scale: float = 2.0,
) -> None:
    """
    Save a figure to figures/publication/.

    Use sparingly — only for final publication-ready charts.
    Exploratory charts should remain in-notebook.
    """
    PUB_DIR.mkdir(parents=True, exist_ok=True)
    stem = PUB_DIR / name
    if "html" in formats:
        fig.write_html(str(stem) + ".html", include_plotlyjs="cdn")
    if "png" in formats:
        fig.write_image(str(stem) + ".png", width=width, height=height, scale=scale)
    if "svg" in formats:
        fig.write_image(str(stem) + ".svg", width=width, height=height)
