"""
Little Ledger - Overview View
Reproducing PDF Page 7: Executive Cards, 30-Day Spending Rhythm, Category Allocation, Recent Entries.
"""

from datetime import datetime
import streamlit as st
import pandas as pd

from config import PALETTE, format_inr
from database import get_db
from expense_manager import ExpenseManager
from budget_manager import BudgetManager
from analytics import (
    get_month_date_range,
    compute_monthly_metrics,
    compute_daily_spending_series,
    compute_category_envelopes,
)
from components.metrics import render_metric_card
from components.charts import (
    create_daily_spending_chart,
    create_category_allocation_chart,
)
from components.empty_states import render_empty_state
from components.expense_form import show_expense_dialog


def render_overview_view():
    db = get_db()
    expense_mgr = ExpenseManager()
    budget_mgr = BudgetManager()

    # Parse selected period
    period_str = st.session_state.get("selected_period", "Oct 2026")
    is_all_time = (period_str == "All Time")

    month_names = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }

    if is_all_time:
        start_dt = None
        end_dt = None
        selected_month_name = "All"
        selected_year = datetime.utcnow().year
        selected_month = datetime.utcnow().month
        prev_start_dt = None
        prev_end_dt = None
        prev_expenses = []
    else:
        parts = period_str.split()
        selected_month_name = parts[0]
        selected_year = int(parts[1]) if len(parts) > 1 else 2026
        selected_month = month_names.get(selected_month_name, 10)

        # Previous month for MoM comparison
        prev_month = 12 if selected_month == 1 else selected_month - 1
        prev_year = selected_year - 1 if selected_month == 1 else selected_year

        start_dt, end_dt = get_month_date_range(selected_year, selected_month)
        prev_start_dt, prev_end_dt = get_month_date_range(prev_year, prev_month)

        prev_expenses, _ = expense_mgr.get_expenses(
            user_id=st.session_state.get("user_id", "demo_user"), start_date=prev_start_dt, end_date=prev_end_dt, limit=1000
        )

    # Fetch expenses from MongoDB
    current_expenses, current_count = expense_mgr.get_expenses(
        user_id=st.session_state.get("user_id", "demo_user"), start_date=start_dt, end_date=end_dt, limit=5000
    )

    monthly_budget = budget_mgr.get_monthly_budget(selected_year, selected_month, st.session_state.get("user_id", "demo_user"))
    envelopes_map = budget_mgr.get_all_envelopes_with_defaults(selected_year, selected_month, st.session_state.get("user_id", "demo_user"))

    metrics = compute_monthly_metrics(current_expenses, selected_year, selected_month, monthly_budget, prev_expenses)
    category_envelopes = compute_category_envelopes(current_expenses, envelopes_map)

    # Overview Title & Subtitle (Page 7)
    st.markdown(
        f"""
        <div style="margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap;">
                <div>
                    <h1 style="font-family:'Fraunces', serif; font-size:38px; font-weight:400; margin:0 0 4px 0; color:{PALETTE['text_main']};">
                        Overview
                    </h1>
                    <div style="font-size:15px; color:{PALETTE['text_muted']};">
                        A mindful accounting of personal outlays, envelope runways, and behavioral rhythms.
                    </div>
                </div>
                <div style="margin-top:8px;">
                    <span class="ll-badge ll-badge-neutral" style="font-size:11.5px; padding:6px 12px;">
                        RECONCILED · {metrics.get('count_transactions', len(current_expenses))} VERIFIED ENTRIES
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Executive Metric Cards (Page 7)
    c1, c2, c3 = st.columns(3)

    with c1:
        card_title = "TOTAL CUMULATIVE OUTLAY" if is_all_time else "TOTAL MONTHLY OUTLAY"
        card_sub = "Combined debits across all recorded statement cycles" if is_all_time else f"{metrics.get('mom_change_pct', 0.0):+.1f}% vs previous cycle ({format_inr(metrics.get('previous_spent', 0.0))})"
        render_metric_card(
            title=card_title,
            value=format_inr(metrics["total_spent"]),
            subtitle=card_sub,
            badge_text="ALL TIME" if is_all_time else "AUDITED",
            badge_type="neutral",
        )

    with c2:
        rem_budget = metrics["remaining_budget"]
        budget_pct = metrics["budget_utilization_pct"]
        badge_type = "green" if budget_pct <= 80 else ("yellow" if budget_pct <= 100 else "red")
        badge_text = "BALANCED" if budget_pct <= 80 else ("ATTENTION" if budget_pct <= 100 else "DEFICIT")
        render_metric_card(
            title="LIQUID BUDGET RUNWAY",
            value=format_inr(rem_budget),
            subtitle=f"{budget_pct:.1f}% absorbed of {format_inr(monthly_budget)} target ceiling",
            badge_text=badge_text,
            badge_type=badge_type,
        )

    with c3:
        from predict import SpendingPredictor
        try:
            predictor = SpendingPredictor()
            pred_res = predictor.predict_next_month(st.session_state.get("user_id", "demo_user"))
        except Exception:
            pred_res = None

        if pred_res and pred_res.get("status") == "success":
            period_raw = pred_res.get("forecast_period", "")
            try:
                p_dt = datetime.strptime(period_raw, "%Y-%m")
                period_lbl = p_dt.strftime("%b %Y")
            except Exception:
                period_lbl = period_raw

            proj_total = pred_res.get("projected_total", 0.0)
            mae_val = pred_res.get("mae", 0.0)
            is_overrun = pred_res.get("is_overrun_predicted", False)

            badge_txt = "OVERRUN RISK" if is_overrun else "GBR ESTIMATE"
            badge_cls = "red" if is_overrun else "green"

            render_metric_card(
                title="NEXT MONTH PROJECTED (ML)",
                value=format_inr(proj_total),
                subtitle=f"{period_lbl} estimate · ± {format_inr(mae_val)} margin",
                badge_text=badge_txt,
                badge_type=badge_cls,
            )
        else:
            render_metric_card(
                title="NEXT MONTH PROJECTED (ML)",
                value="Awaiting Data",
                subtitle="Add outlays & calibrate in Forecast Lab",
                badge_text="STANDBY",
                badge_type="neutral",
            )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Two Main Analytics Charts
    col_left, col_right = st.columns([1.6, 1.0], gap="medium")

    with col_left:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-family:'Fraunces', serif; font-size:20px; font-weight:500; color:{PALETTE['text_main']};">
                    Spending Rhythm
                </span>
                <span style="font-size:12px; color:{PALETTE['text_muted']};">
                    Daily Velocity · Avg {format_inr(metrics.get('daily_average', 0.0))}/day
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        daily_series = compute_daily_spending_series(current_expenses, selected_year, selected_month)
        chart_rhythm = create_daily_spending_chart(daily_series)
        st.plotly_chart(chart_rhythm, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-family:'Fraunces', serif; font-size:20px; font-weight:500; color:{PALETTE['text_main']};">
                    Category Allocation
                </span>
                <span style="font-size:12px; color:{PALETTE['text_muted']};">
                    {len(category_envelopes)} Envelopes
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        chart_alloc = create_category_allocation_chart(category_envelopes)
        st.plotly_chart(chart_alloc, use_container_width=True, config={"displayModeBar": False})

    # Recent Ledger Entries Table
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin:24px 0 12px 0;">
            <div>
                <span style="font-family:'Fraunces', serif; font-size:22px; font-weight:500; color:{PALETTE['text_main']};">
                    Recent Verified Receipts
                </span>
                <span style="font-size:12px; color:{PALETTE['text_muted']}; margin-left:8px;">
                    Latest entries recorded in {selected_month_name} {selected_year}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recent_expenses, _ = expense_mgr.get_expenses(
        user_id=st.session_state.get("user_id", "demo_user"),
        start_date=start_dt,
        end_date=end_dt,
        sort_by="date",
        sort_descending=True,
        limit=6,
    )

    if not recent_expenses:
        render_empty_state(
            title=f"No Receipts Found for {selected_month_name} {selected_year}",
            message="No transactions have been logged for this billing period yet.",
            action_label="➕ Log an Expense",
        )
    else:
        rows_html = []
        for exp in recent_expenses:
            d = exp.get("date")
            d_fmt = d.strftime("%b %d, %Y") if isinstance(d, datetime) else str(d)[:10]
            amt_fmt = format_inr(exp.get("amount", 0.0))
            memo = exp.get("description", "")
            memo_html = f"<div style='font-size:11px; color:{PALETTE['text_muted']}; margin-top:2px;'>{memo}</div>" if memo else ""
            cat_badge = exp.get("category", "Other")

            row = (
                f'<tr>'
                f'<td style="font-weight:500; white-space:nowrap;">{d_fmt}</td>'
                f'<td><div style="font-weight:600; color:{PALETTE["text_main"]};">{exp.get("merchant", "")}</div>{memo_html}</td>'
                f'<td><span class="ll-badge ll-badge-neutral">{cat_badge}</span></td>'
                f'<td style="font-size:12px; color:{PALETTE["text_muted"]};">{exp.get("payment_method", "")}</td>'
                f'<td style="text-align:right; font-weight:600; white-space:nowrap;">{amt_fmt}</td>'
                f'</tr>'
            )
            rows_html.append(row)

        all_rows = "\n".join(rows_html)
        table_html = (
            f'<div style="background:{PALETTE["surface"]}; border:1px solid {PALETTE["border"]}; border-radius:12px; overflow:hidden; margin-bottom:24px; box-shadow:{PALETTE["card_shadow"]};">\n'
            f'<table class="ll-table" style="width:100%; border-collapse:collapse; table-layout:fixed;">\n'
            f'<thead>\n'
            f'<tr>\n'
            f'<th style="width:15%;">DATE</th>\n'
            f'<th style="width:38%;">MERCHANT &amp; MEMO</th>\n'
            f'<th style="width:20%;">CATEGORY</th>\n'
            f'<th style="width:13%;">PAYMENT RAIL</th>\n'
            f'<th style="width:14%; text-align:right;">OUTLAY (INR)</th>\n'
            f'</tr>\n'
            f'</thead>\n'
            f'<tbody>\n'
            f'{all_rows}\n'
            f'</tbody>\n'
            f'</table>\n'
            f'</div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)
