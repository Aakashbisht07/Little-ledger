"""
Little Ledger - Interactive Visualization Components
Plotly charts themed with the botanical pastel palette, Fraunces typography, and editorial styling.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from config import PALETTE, CATEGORY_META, format_inr

# Standard chart layout configuration
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=PALETTE["text_main"], size=12),
    margin=dict(l=20, r=20, t=30, b=20),
    hoverlabel=dict(
        bgcolor=PALETTE["surface"],
        bordercolor=PALETTE["border"],
        font=dict(family="Inter, sans-serif", color=PALETTE["text_main"], size=12),
    ),
)


def create_daily_spending_chart(df: pd.DataFrame, monthly_budget: float = 65000.0) -> go.Figure:
    """
    Creates 'THE BIG PICTURE: Daily Spending Rhythm & Horizon' chart.
    Displays daily spending bars alongside cumulative spend and linear budget ceiling runway.
    """
    fig = go.Figure()

    # 1. Daily spend bars
    fig.add_trace(
        go.Bar(
            x=df["day"],
            y=df["daily_spent"],
            name="Daily Outflow",
            marker=dict(
                color=PALETTE["primary_green"],
                line=dict(color=PALETTE["primary_dark"], width=1),
                opacity=0.85,
            ),
            hovertemplate="Day %{x}: ₹%{y:,.2f}<extra></extra>",
            yaxis="y1",
        )
    )

    # 2. Cumulative actual spend line
    fig.add_trace(
        go.Scatter(
            x=df["day"],
            y=df["cumulative_spent"],
            name="Cumulative Spend",
            mode="lines+markers",
            line=dict(color=PALETTE["dusty_peach"], width=2.5),
            marker=dict(size=5, color=PALETTE["dusty_peach"]),
            hovertemplate="Cumulative Day %{x}: ₹%{y:,.2f}<extra></extra>",
            yaxis="y2",
        )
    )

    # 3. Target linear ceiling runway
    fig.add_trace(
        go.Scatter(
            x=df["day"],
            y=df["budget_ceiling_runway"],
            name="Target Ceiling Pace",
            mode="lines",
            line=dict(color=PALETTE["text_muted"], width=1.5, dash="dash"),
            hovertemplate="Linear Pace Day %{x}: ₹%{y:,.2f}<extra></extra>",
            yaxis="y2",
        )
    )

    fig.update_layout(
        **PLOTLY_THEME,
        height=320,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            title="Day of Month",
            showgrid=True,
            gridcolor=PALETTE["border_subtle"],
            zeroline=False,
            dtick=2,
        ),
        yaxis=dict(
            title="Daily Outflow (₹)",
            showgrid=True,
            gridcolor=PALETTE["border_subtle"],
            zeroline=False,
            side="left",
        ),
        yaxis2=dict(
            title="Cumulative (₹)",
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
        ),
    )
    return fig


def create_category_allocation_chart(envelopes: List[Dict[str, Any]]) -> go.Figure:
    """Horizontal stacked / bar chart showing category spending against budget envelopes."""
    df = pd.DataFrame(envelopes)
    if df.empty:
        return go.Figure()

    df = df[df["spent"] > 0].sort_values("spent", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df["category"],
            x=df["spent"],
            orientation="h",
            marker=dict(
                color=[CATEGORY_META.get(c, {}).get("color", PALETTE["primary_green"]) for c in df["category"]],
                line=dict(color=PALETTE["border"], width=1),
            ),
            text=[f"₹{amt:,.0f} ({pct}%)" for amt, pct in zip(df["spent"], df["utilization_pct"])],
            textposition="auto",
            hovertemplate="%{y}: ₹%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        **PLOTLY_THEME,
        height=280,
        xaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["border_subtle"],
            zeroline=False,
            title="Outlay (₹)",
        ),
        yaxis=dict(showgrid=False, zeroline=False),
        showlegend=False,
    )
    return fig


def create_forecast_trajectory_chart(
    recent_history: List[Dict[str, Any]],
    predicted_spend: float,
    lower_bound: float,
    upper_bound: float,
    budget_ceiling: float = 65000.0,
    forecast_period: Optional[str] = None,
) -> go.Figure:
    """
    Creates Trajectory Analysis Chart matching Page 5 (May - Nov 2026).
    Empirical Ledger vs ML Horizon Inferences with forward forecast cone.
    Gracefully handles empty or initial ledger state.
    """
    fig = go.Figure()

    if not recent_history:
        # Graceful empty chart with target ceiling and clear guidance
        fig.add_trace(
            go.Scatter(
                x=["Current Ceiling"],
                y=[budget_ceiling],
                mode="markers+text",
                name=f"Ceiling (₹{budget_ceiling:,.0f})",
                text=[f"Target Ceiling: ₹{budget_ceiling:,.0f}"],
                textposition="bottom center",
                marker=dict(size=10, color=PALETTE["primary_green"]),
            )
        )
        fig.update_layout(
            **PLOTLY_THEME,
            height=300,
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(
                title="Monthly Outlay (₹)",
                showgrid=True,
                gridcolor=PALETTE["border_subtle"],
                range=[0, max(budget_ceiling * 1.3, 80000)],
            ),
            annotations=[
                dict(
                    text="<b>No Historical Spend Cycles Recorded Yet</b><br>Record transactions across monthly cycles to see empirical spend vs ML forecast trajectory.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    align="center",
                    font=dict(size=13, color=PALETTE["text_muted"]),
                )
            ],
        )
        return fig

    periods = [h["period"] for h in recent_history]
    spends = [h["total_spend"] for h in recent_history]
    last_period = periods[-1]
    last_spend = spends[-1]

    # Resolve a valid chronological next_period (e.g. "2026-11") matching date format
    if forecast_period:
        next_period = forecast_period
    else:
        try:
            dt = datetime.strptime(last_period, "%Y-%m")
            m = dt.month + 1
            y = dt.year
            if m > 12:
                m = 1
                y += 1
            next_period = f"{y:04d}-{m:02d}"
        except Exception:
            next_period = f"{last_period}+1"

    # 1. Historical empirical line
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=spends,
            mode="lines+markers",
            name="Empirical Ledger",
            line=dict(color=PALETTE["primary_dark"], width=2.5),
            marker=dict(size=7, color=PALETTE["primary_green"]),
            hovertemplate="%{x}: ₹%{y:,.2f} [Actual]<extra></extra>",
        )
    )

    # 2. Stochastic Forecast Cone (shaded area from last month to upper & lower bounds)
    cone_x = [last_period, next_period, next_period, last_period]
    cone_y = [last_spend, upper_bound, lower_bound, last_spend]
    fig.add_trace(
        go.Scatter(
            x=cone_x,
            y=cone_y,
            fill="toself",
            fillcolor="rgba(231, 194, 192, 0.30)",
            line=dict(color="rgba(255,255,255,0)"),
            name="±Stochastic Band",
            hoverinfo="skip",
            showlegend=True,
        )
    )

    # 3. Next projection dotted line extending into the next month
    fig.add_trace(
        go.Scatter(
            x=[last_period, next_period],
            y=[last_spend, predicted_spend],
            mode="lines+markers",
            name="ML Projection",
            line=dict(color=PALETTE["warning"], width=2.5, dash="dot"),
            marker=dict(size=9, color=PALETTE["warning"], symbol="diamond"),
            hovertemplate="%{x}: ₹%{y:,.2f} [ML Projected]<extra></extra>",
        )
    )

    # 4. Vertical error bar at next_period for confidence span
    fig.add_trace(
        go.Scatter(
            x=[next_period, next_period],
            y=[lower_bound, upper_bound],
            mode="lines+markers",
            name="Confidence Interval",
            line=dict(color=PALETTE["warning"], width=4),
            marker=dict(size=5, color=PALETTE["warning"]),
            showlegend=False,
            hovertemplate=f"Confidence Interval: {format_inr(lower_bound)} – {format_inr(upper_bound)}<extra></extra>",
        )
    )

    # 5. Monthly budget ceiling line spanning all past and future periods
    all_x = periods + [next_period]
    fig.add_trace(
        go.Scatter(
            x=all_x,
            y=[budget_ceiling] * len(all_x),
            mode="lines",
            name=f"Ceiling ({format_inr(budget_ceiling, decimals=0)})",
            line=dict(color=PALETTE["error"], width=1.5, dash="dash"),
            hovertemplate="Target Ceiling: ₹%{y:,.2f}<extra></extra>",
        )
    )

    all_vals = spends + [predicted_spend, lower_bound, upper_bound, budget_ceiling]
    y_min = max(0.0, min(all_vals) * 0.8)
    y_max = max(all_vals) * 1.15

    fig.update_layout(
        **PLOTLY_THEME,
        height=320,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["border_subtle"],
            type="category",
        ),
        yaxis=dict(
            title="Monthly Outlay (₹)",
            showgrid=True,
            gridcolor=PALETTE["border_subtle"],
            range=[y_min, y_max],
        ),
    )
    return fig


def create_weekday_dispersion_chart(dow_distribution: Dict[int, float]) -> go.Figure:
    """Spending dispersion across Monday to Sunday (Page 4 Insights)."""
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    values = [dow_distribution.get(i, 0.0) for i in range(7)]
    colors = [
        PALETTE["powder_blue"] if i < 4 else (PALETTE["dusty_peach"] if i == 4 else PALETTE["primary_green"])
        for i in range(7)
    ]

    fig = go.Figure(
        go.Bar(
            x=dow_names,
            y=values,
            marker=dict(color=colors, line=dict(color=PALETTE["border"], width=1)),
            text=[f"₹{v:,.0f}" if v > 0 else "" for v in values],
            textposition="outside",
            hovertemplate="%{x}: ₹%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        **PLOTLY_THEME,
        height=260,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=PALETTE["border_subtle"], title="Total Outlay (₹)"),
        showlegend=False,
    )
    return fig

