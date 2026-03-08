import plotly.graph_objects as go
import pandas as pd

from core.timeline_engine import DIMENSION_DISPLAY, compute_century_averages

# Color palette — one color per dimension
DIMENSION_COLORS = {
    "norm_rigidity": "#e74c3c",
    "work_access": "#3498db",
    "political_power": "#9b59b6",
    "appearance_pressure": "#e67e22",
    "sexuality_openness": "#1abc9c",
    "domestic_expectation": "#f39c12",
}

HIGHLIGHT_COLOR = "rgba(118, 75, 162, 0.85)"
AVERAGE_COLOR = "rgba(102, 126, 234, 0.55)"
GREEN_2020S_COLOR = "rgba(76, 175, 80, 0.7)"


def create_timeline_chart(all_decades: dict, selected_decade: str) -> go.Figure:
    """
    Multi-line chart showing how each gender norm dimension shifted across all
    decades. The currently selected decade is marked with a vertical dashed line.
    """
    decade_labels = [d["label"] for d in all_decades.values()]
    fig = go.Figure()

    for dim_key, dim_label in DIMENSION_DISPLAY.items():
        values = [
            data.get("dimensions", {}).get(dim_key, 5)
            for data in all_decades.values()
        ]
        fig.add_trace(
            go.Scatter(
                x=decade_labels,
                y=values,
                mode="lines+markers",
                name=dim_label,
                line=dict(color=DIMENSION_COLORS.get(dim_key, "#888"), width=2.5),
                marker=dict(size=7, symbol="circle"),
                hovertemplate=(
                    f"<b>{dim_label}</b><br>"
                    "Decade: %{x}<br>"
                    "Score: %{y}/10<extra></extra>"
                ),
            )
        )

    # Vertical marker for selected decade
    if selected_decade and selected_decade in all_decades:
        selected_label = all_decades[selected_decade]["label"]
        selected_index = decade_labels.index(selected_label)
        fig.add_vline(
            x=selected_index,
            line_dash="dash",
            line_color="rgba(118, 75, 162, 0.6)",
            line_width=2,
            annotation_text=f"  {selected_label}",
            annotation_position="top left",
            annotation_font_color="rgba(118, 75, 162, 0.9)",
        )

    fig.update_layout(
        title=dict(
            text="Gender Norm Dimensions Across a Century",
            font=dict(size=16),
        ),
        xaxis=dict(title="Decade", tickangle=-30),
        yaxis=dict(
            title="Score (0 = Low · 10 = High)",
            range=[0, 10.5],
            dtick=2,
            gridcolor="rgba(200,200,200,0.4)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.45,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        height=420,
        plot_bgcolor="rgba(248,248,252,1)",
        paper_bgcolor="white",
        margin=dict(l=50, r=30, t=60, b=140),
        hovermode="x unified",
    )

    return fig


def create_norm_radar_chart(decade_data: dict) -> go.Figure:
    """
    Radar / spider chart displaying all six gender norm dimension scores for
    the selected decade in one visual.
    """
    dimensions = decade_data.get("dimensions", {})
    labels = list(DIMENSION_DISPLAY.values())
    values = [dimensions.get(k, 5) for k in DIMENSION_DISPLAY]

    # Close the polygon
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor="rgba(118, 75, 162, 0.18)",
            line=dict(color="rgba(118, 75, 162, 0.85)", width=2.5),
            name=decade_data.get("label", "Selected Decade"),
            hovertemplate="<b>%{theta}</b><br>Score: %{r}/10<extra></extra>",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[0, 2, 4, 6, 8, 10],
                tickfont=dict(size=9),
                gridcolor="rgba(180,180,180,0.5)",
            ),
            angularaxis=dict(
                tickfont=dict(size=10),
            ),
            bgcolor="rgba(248,248,252,1)",
        ),
        showlegend=False,
        title=dict(
            text=f"{decade_data.get('label', '')} — Norm Profile",
            font=dict(size=15),
        ),
        height=380,
        paper_bgcolor="white",
        margin=dict(l=60, r=60, t=70, b=40),
    )

    return fig


def create_comparison_bar_chart(all_decades: dict, selected_decade: str) -> go.Figure:
    """
    Grouped bar chart comparing the selected decade's dimension scores to the
    century-wide average across all decades.
    """
    if selected_decade not in all_decades:
        return go.Figure()

    decade_data = all_decades[selected_decade]
    dimensions = decade_data.get("dimensions", {})
    averages = compute_century_averages(all_decades)

    labels = list(DIMENSION_DISPLAY.values())
    selected_vals = [dimensions.get(k, 5) for k in DIMENSION_DISPLAY]
    avg_vals = [averages.get(k, 5) for k in DIMENSION_DISPLAY]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=decade_data.get("label", "Selected"),
            x=labels,
            y=selected_vals,
            marker_color=HIGHLIGHT_COLOR,
            hovertemplate="<b>%{x}</b><br>%{y}/10<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Century Average (1920s–2020s)",
            x=labels,
            y=avg_vals,
            marker_color=AVERAGE_COLOR,
            hovertemplate="<b>%{x}</b><br>Avg: %{y}/10<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        title=dict(
            text=f"{decade_data.get('label', '')} vs. Century Average",
            font=dict(size=15),
        ),
        yaxis=dict(
            range=[0, 11],
            title="Score (0–10)",
            gridcolor="rgba(200,200,200,0.4)",
        ),
        xaxis=dict(tickangle=-25),
        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="center", x=0.5),
        height=380,
        plot_bgcolor="rgba(248,248,252,1)",
        paper_bgcolor="white",
        margin=dict(l=50, r=30, t=60, b=130),
    )

    return fig


def create_era_vs_2020s_chart(all_decades: dict, era_decade_key: str) -> go.Figure:
    """
    Grouped bar chart comparing a specific era decade's dimension scores to the 2020s.
    Shows how much has changed between the user's growing-up era and the present.
    """
    if era_decade_key not in all_decades:
        return go.Figure()

    era_data = all_decades[era_decade_key]
    era_dimensions = era_data.get("dimensions", {})
    era_label = era_data.get("label", era_decade_key)

    data_2020s = all_decades.get("2020s", {})
    dims_2020s = data_2020s.get("dimensions", {})

    labels = list(DIMENSION_DISPLAY.values())
    era_vals = [era_dimensions.get(k, 5) for k in DIMENSION_DISPLAY]
    vals_2020s = [dims_2020s.get(k, 5) for k in DIMENSION_DISPLAY]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=era_label,
            x=labels,
            y=era_vals,
            marker_color=HIGHLIGHT_COLOR,
            hovertemplate="<b>%{x}</b><br>%{y}/10<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="2020s",
            x=labels,
            y=vals_2020s,
            marker_color=GREEN_2020S_COLOR,
            hovertemplate="<b>%{x}</b><br>%{y}/10<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        title=dict(
            text=f"{era_label} vs. 2020s — How Much Has Changed?",
            font=dict(size=15),
        ),
        yaxis=dict(
            range=[0, 11],
            title="Score (0–10)",
            gridcolor="rgba(200,200,200,0.4)",
        ),
        xaxis=dict(tickangle=-25),
        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="center", x=0.5),
        height=380,
        plot_bgcolor="rgba(248,248,252,1)",
        paper_bgcolor="white",
        margin=dict(l=50, r=30, t=60, b=130),
    )

    return fig


def create_progress_timeline(all_decades: dict, dimension_key: str) -> go.Figure:
    """
    Single-dimension line chart with an area fill, useful for tracking one
    specific norm (e.g., 'work_access') across the full century.
    """
    labels = [d["label"] for d in all_decades.values()]
    values = [
        data.get("dimensions", {}).get(dimension_key, 5)
        for data in all_decades.values()
    ]
    dim_label = DIMENSION_DISPLAY.get(dimension_key, dimension_key)
    color = DIMENSION_COLORS.get(dimension_key, "#764ba2")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=values,
            mode="lines+markers",
            fill="tozeroy",
            fillcolor=color.replace(")", ", 0.15)").replace("rgb", "rgba")
            if color.startswith("rgb")
            else color + "26",
            line=dict(color=color, width=3),
            marker=dict(size=9),
            name=dim_label,
            hovertemplate=f"<b>{dim_label}</b><br>%{{x}}<br>Score: %{{y}}/10<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=f"{dim_label}: 1920s → 2020s", font=dict(size=15)),
        xaxis=dict(title="Decade"),
        yaxis=dict(
            title="Score (0–10)",
            range=[0, 10.5],
            gridcolor="rgba(200,200,200,0.4)",
        ),
        height=320,
        plot_bgcolor="rgba(248,248,252,1)",
        paper_bgcolor="white",
        margin=dict(l=50, r=30, t=60, b=60),
    )

    return fig
