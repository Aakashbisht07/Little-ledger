"""
Little Ledger - Reusable Metric Cards & Badges
Displays financial indicators with Fraunces serif values and botanical styling.
"""

from typing import Optional
import streamlit as st
from config import PALETTE


def render_metric_card(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    badge_text: Optional[str] = None,
    badge_class: Optional[str] = None,
    badge_type: Optional[str] = None,
):
    """Render an editorial card with title, large value, and optional badge."""
    if badge_class is None:
        if badge_type:
            badge_class = f"ll-badge-{badge_type}" if not badge_type.startswith("ll-badge-") else badge_type
        else:
            badge_class = "ll-badge-green"

    badge_html = f"<span class='ll-badge {badge_class}'>{badge_text}</span>" if badge_text else ""
    sub_html = f"<div class='ll-metric-subtitle'>{subtitle}</div>" if subtitle else ""

    st.markdown(
        f"""
        <div class="ll-card">
            <div class="ll-card-header">
                <span>{title}</span>
                {badge_html}
            </div>
            <div class="ll-metric-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_runway_progress_bar(
    absorbed_amount: float,
    ceiling_amount: float,
    days_elapsed: int = 20,
    total_days: int = 30,
):
    """Renders the horizontal runway bar showing Absorbed Spend vs Available Runway."""
    pct = (absorbed_amount / ceiling_amount * 100.0) if ceiling_amount > 0 else 0.0
    pct_clamped = min(100.0, max(0.0, pct))
    runway_pct = max(0.0, 100.0 - pct_clamped)

    st.markdown(
        f"""
        <div style="background:{PALETTE['surface_alt']}; padding:16px 20px; border-radius:10px; border:1px solid {PALETTE['border']}; margin:16px 0;">
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:8px; font-weight:500;">
                <span style="color:{PALETTE['primary_dark']};">● Absorbed Spend ({pct:.1f}%)</span>
                <span style="color:{PALETTE['warning']};">● Available Runway ({runway_pct:.1f}%)</span>
                <span style="color:{PALETTE['text_muted']};">Target Cap: 100% (₹{ceiling_amount:,.0f})</span>
            </div>
            <div style="height:12px; border-radius:6px; background:#E8E4DA; overflow:hidden; display:flex;">
                <div style="width:{pct_clamped}%; background:{PALETTE['primary_green']}; transition:width 0.4s ease;"></div>
                <div style="width:{runway_pct}%; background:{PALETTE['butter_yellow']};"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:{PALETTE['text_muted']}; margin-top:6px;">
                <span>DAY 1</span>
                <span>{days_elapsed} of {total_days} Days Elapsed</span>
                <span>CYCLE END</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
