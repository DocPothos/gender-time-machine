import plotly.graph_objects as go

from core.timeline_engine import DIMENSION_DISPLAY

# Color palette — one color per dimension
DIMENSION_COLORS = {
    "norm_rigidity": "#F26076",
    "work_access": "#3A86FF",
    "political_power": "#8338EC",
    "appearance_pressure": "#FF9760",
    "sexuality_openness": "#458B73",
    "domestic_expectation": "#FFD150",
}

HIGHLIGHT_COLOR = "rgba(69, 139, 115, 0.85)"   # teal
AVERAGE_COLOR = "rgba(242, 96, 118, 0.50)"      # coral
GREEN_2020S_COLOR = "rgba(255, 151, 96, 0.75)"  # peach


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
        legend=dict(orientation="h", yanchor="bottom", y=-0.65, xanchor="center", x=0.5),
        height=420,
        plot_bgcolor="rgba(248,248,252,1)",
        paper_bgcolor="white",
        margin=dict(l=50, r=30, t=60, b=160),
    )

    return fig

