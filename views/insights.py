"""
Little Ledger - Spending Insights View
Reproducing PDF Page 4: 50/30/20 Portfolio Allocation, Weekday/Weekend Cadence, Top Merchants, Recurring Subscriptions.
"""

import calendar
from datetime import datetime
import streamlit as st
import pandas as pd

from config import PALETTE, format_inr
from database import get_db
from expense_manager import ExpenseManager
from budget_manager import BudgetManager
from analytics import (
    get_month_date_range,
    compute_portfolio_allocation,
    compute_weekday_weekend_cadence,
    compute_top_merchants,
    compute_recurring_expenses,
)
from components.charts import create_weekday_dispersion_chart


def render_insights_view():
    db = get_db()
    expense_mgr = ExpenseManager()
    budget_mgr = BudgetManager()

    # Determine selected period
    period_str = st.session_state.get("selected_period", "Oct 2026")
    is_all_time = (period_str == "All Time")

    month_names = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }

    if is_all_time:
        selected_month_name = "All"
        selected_year = datetime.utcnow().year
        selected_month = datetime.utcnow().month
        cohort_options = ["All Time Portfolio", "Year to Date"]
    else:
        parts = period_str.split()
        selected_month_name = parts[0]
        selected_year = int(parts[1]) if len(parts) > 1 else 2026
        selected_month = month_names.get(selected_month_name, 10)
        cohort_options = [f"This Month ({selected_month_name} {selected_year})", "Quarterly Review", "Year to Date"]

    # Scope Selector
    scope = st.radio(
        "Observation Cohort",
        cohort_options,
        horizontal=True,
        label_visibility="collapsed",
        key="insights_cohort_radio",
    )

    # Compute date range
    if "All Time" in scope or is_all_time and "Year to Date" not in scope:
        start_dt = None
        end_dt = None
        scope_title = "All Time Ledger"
    elif "Quarterly" in scope:
        # Determine quarter for selected_month
        q_start_mo = ((selected_month - 1) // 3) * 3 + 1
        q_end_mo = q_start_mo + 2
        _, q_last_day = calendar.monthrange(selected_year, q_end_mo)
        start_dt = datetime(selected_year, q_start_mo, 1)
        end_dt = datetime(selected_year, q_end_mo, q_last_day, 23, 59, 59)
        scope_title = f"Quarter {(selected_month - 1)//3 + 1} {selected_year}"
    elif "Year to Date" in scope:
        _, last_day_m = calendar.monthrange(selected_year, selected_month)
        start_dt = datetime(selected_year, 1, 1)
        end_dt = datetime(selected_year, selected_month, last_day_m, 23, 59, 59)
        scope_title = f"Fiscal Year {selected_year} to Date"
    else:
        start_dt, end_dt = get_month_date_range(selected_year, selected_month)
        scope_title = f"{selected_month_name} {selected_year}"

    expenses, _ = expense_mgr.get_expenses(
        user_id=st.session_state.get("user_id", "demo_user"), start_date=start_dt, end_date=end_dt, limit=5000
    )

    monthly_budget = budget_mgr.get_monthly_budget(selected_year, selected_month, st.session_state.get("user_id", "demo_user"))
    if "Quarterly" in scope:
        monthly_budget *= 3
    elif "Year to Date" in scope:
        monthly_budget *= selected_month

    portfolio = compute_portfolio_allocation(expenses, monthly_budget)
    cadence = compute_weekday_weekend_cadence(expenses)
    top_merchants = compute_top_merchants(expenses, top_n=5)
    recurring_items = compute_recurring_expenses(expenses)

    # Header Section (Page 4)
    st.markdown(
        f"""
        <div style="margin-bottom:20px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.12em; color:{PALETTE['text_muted']};">
                INSIGHTS DOSSIER · FASCICLE IV · {scope_title.upper()}
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap;">
                <div>
                    <h1 style="font-family:'Fraunces', serif; font-size:38px; font-weight:400; margin:4px 0 2px 0; color:{PALETTE['text_main']};">
                        Patterns in the ledger.
                    </h1>
                    <div style="font-size:15px; color:{PALETTE['text_muted']};">
                        Macro allocation compliance, temporal cadence analysis, and committed merchant obligations.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # SECTION 01: 50 / 30 / 20 Portfolio Allocation
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin:20px 0 12px 0;">
            <span style="font-family:'Fraunces', serif; font-size:22px; color:{PALETTE['text_main']};">
                Portfolio Allocation (50 / 30 / 20 Philosophy)
            </span>
            <span class="ll-badge ll-badge-neutral">BENCHMARK ALIGNED</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        n_pct = portfolio.get("needs_pct", 50.0)
        n_amt = format_inr(portfolio.get("needs_amount", 0.0))
        n_badge = "ll-badge-green" if n_pct <= 52 else "ll-badge-yellow"
        st.markdown(
            f"""
            <div class="ll-card">
                <div class="ll-card-header">
                    <span>ESSENTIAL LIVING (NEEDS)</span>
                    <span class="ll-badge {n_badge}">{n_pct:.1f}% OF OUTLAY</span>
                </div>
                <div class="ll-metric-value">{n_amt}</div>
                <div class="ll-metric-subtitle">Target: 50.0% · Groceries, Rent, Utilities, Health</div>
                <div style="height:6px; background:#E8E4DA; border-radius:3px; overflow:hidden; margin-top:12px;">
                    <div style="width:{min(100.0, n_pct * 2)}%; height:100%; background:#4F6F52;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        w_pct = portfolio.get("wants_pct", 30.0)
        w_amt = format_inr(portfolio.get("wants_amount", 0.0))
        w_badge = "ll-badge-green" if w_pct <= 32 else "ll-badge-yellow"
        st.markdown(
            f"""
            <div class="ll-card">
                <div class="ll-card-header">
                    <span>DISCRETIONARY (WANTS)</span>
                    <span class="ll-badge {w_badge}">{w_pct:.1f}% OF OUTLAY</span>
                </div>
                <div class="ll-metric-value">{w_amt}</div>
                <div class="ll-metric-subtitle">Target: 30.0% · Dining, Entertainment, Travel, Shopping</div>
                <div style="height:6px; background:#E8E4DA; border-radius:3px; overflow:hidden; margin-top:12px;">
                    <div style="width:{min(100.0, w_pct * 3.33)}%; height:100%; background:#A3B899;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p3:
        s_pct = portfolio.get("buffer_pct", 20.0)
        s_amt = format_inr(portfolio.get("buffer_amount", 0.0))
        s_badge = "ll-badge-green" if s_pct >= 18 else "ll-badge-neutral"
        st.markdown(
            f"""
            <div class="ll-card">
                <div class="ll-card-header">
                    <span>RESERVE &amp; INVEST (SAVINGS)</span>
                    <span class="ll-badge {s_badge}">{s_pct:.1f}% SURPLUS</span>
                </div>
                <div class="ll-metric-value">{s_amt}</div>
                <div class="ll-metric-subtitle">Target: 20.0% · Unallocated Liquid Cushion</div>
                <div style="height:6px; background:#E8E4DA; border-radius:3px; overflow:hidden; margin-top:12px;">
                    <div style="width:{min(100.0, s_pct * 5)}%; height:100%; background:#8E9A82;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # SECTION 02: Temporal Velocity & Merchant Leaderboard
    c_left, c_right = st.columns([1.5, 1.0], gap="medium")

    with c_left:
        pct_diff = cadence.get("weekend_pct_diff", 0.0)
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-family:'Fraunces', serif; font-size:20px; font-weight:500; color:{PALETTE['text_main']};">
                    Temporal Velocity: Weekday vs Weekend
                </span>
                <span style="font-size:12px; color:{PALETTE['text_muted']};">
                    Avg Weekday: {format_inr(cadence.get('weekday_mean', 0.0))} · Weekend: {format_inr(cadence.get('weekend_mean', 0.0))} ({pct_diff:+.1f}%)
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        chart_candence = create_weekday_dispersion_chart(cadence.get("day_of_week_distribution", {i: 0.0 for i in range(7)}))
        st.plotly_chart(chart_candence, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-family:'Fraunces', serif; font-size:20px; font-weight:500; color:{PALETTE['text_main']};">
                    Top Payees by Volume
                </span>
                <span style="font-size:12px; color:{PALETTE['text_muted']};">Concentration</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not top_merchants:
            st.info("No merchant transactions recorded in this scope.")
        else:
            m_rows = []
            for m in top_merchants:
                m_rows.append(
                    f'<tr>'
                    f'<td style="font-weight:600;">{m["merchant"]}</td>'
                    f'<td style="text-align:center;"><span class="ll-badge ll-badge-neutral">{m["count"]}</span></td>'
                    f'<td style="text-align:right; font-weight:600;">{format_inr(m.get("total", 0.0))}</td>'
                    f'</tr>'
                )
            all_m_rows = "\n".join(m_rows)
            m_table = (
                f'<div style="background:{PALETTE["surface"]}; border:1px solid {PALETTE["border"]}; border-radius:12px; overflow:hidden;">\n'
                f'<table class="ll-table" style="width:100%; border-collapse:collapse; table-layout:fixed;">\n'
                f'<thead>\n'
                f'<tr>\n'
                f'<th style="width:60%;">MERCHANT</th>\n'
                f'<th style="width:20%; text-align:center;">COUNT</th>\n'
                f'<th style="width:20%; text-align:right;">SPEND (INR)</th>\n'
                f'</tr>\n'
                f'</thead>\n'
                f'<tbody>\n'
                f'{all_m_rows}\n'
                f'</tbody>\n'
                f'</table>\n'
                f'</div>'
            )
            st.markdown(m_table, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # SECTION 03: Recurring Obligations
    total_recurring_monthly = sum(r.get("average_amount", 0.0) for r in recurring_items)
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin:20px 0 12px 0;">
            <span style="font-family:'Fraunces', serif; font-size:22px; color:{PALETTE['text_main']};">
                Committed Recurring Subscriptions
            </span>
            <span style="font-size:12px; color:{PALETTE['text_muted']};">
                Total Monthly Commitment: <b>{format_inr(total_recurring_monthly)}</b> ({format_inr(total_recurring_monthly * 12)} / yr)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not recurring_items:
        st.info("No recurring commitments flagged in this cycle.")
    else:
        r_rows = []
        for r in recurring_items:
            amt = r.get("average_amount", 0.0)
            r_rows.append(
                f'<tr>'
                f'<td style="font-weight:600;">{r["merchant"]}</td>'
                f'<td><span class="ll-badge ll-badge-neutral">{r["category"]}</span></td>'
                f'<td style="font-size:12px; color:{PALETTE["text_muted"]};">{r["frequency"]}</td>'
                f'<td style="text-align:right; font-weight:600;">{format_inr(amt)}</td>'
                f'<td style="text-align:right; color:{PALETTE["text_muted"]};">{format_inr(amt * 12)}</td>'
                f'</tr>'
            )
        all_r_rows = "\n".join(r_rows)
        r_table = (
            f'<div style="background:{PALETTE["surface"]}; border:1px solid {PALETTE["border"]}; border-radius:12px; overflow:hidden; margin-bottom:20px;">\n'
            f'<table class="ll-table" style="width:100%; border-collapse:collapse; table-layout:fixed;">\n'
            f'<thead>\n'
            f'<tr>\n'
            f'<th style="width:30%;">SERVICE / VENDOR</th>\n'
            f'<th style="width:25%;">CATEGORY</th>\n'
            f'<th style="width:15%;">CADENCE</th>\n'
            f'<th style="width:15%; text-align:right;">OUTLAY (INR)</th>\n'
            f'<th style="width:15%; text-align:right;">ANNUAL RUN-RATE</th>\n'
            f'</tr>\n'
            f'</thead>\n'
            f'<tbody>\n'
            f'{all_r_rows}\n'
            f'</tbody>\n'
            f'</table>\n'
            f'</div>'
        )
        st.markdown(r_table, unsafe_allow_html=True)
