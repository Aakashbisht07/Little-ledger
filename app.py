"""
Little Ledger — Personal Expense Analysis & Spending Prediction System
Master Application Controller (Unified Single-Page Architecture)
Guarantees:
- Zero left sidebar navigation (clean, wide, editorial layout)
- Sleek centered horizontal segmented navbar
- Editorial Folio views
- CSV fallback when MongoDB is offline; full MongoDB persistence when connected
- Per-user authentication with isolated data per account
"""

import streamlit as st

from config import PALETTE, CUSTOM_CSS
from database import get_db
from views.login import render_login_page
from components.navigation import render_top_navigation, NAV_TABS
from views.overview import render_overview_view
from views.transactions import render_transactions_view
from views.insights import render_insights_view
from views.forecast import render_forecast_view
from views.settings import render_settings_view

st.set_page_config(
    page_title="Little Ledger — Personal Expense & Spending Prediction",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Authentication Gate ────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    render_login_page()
    st.stop()

# ── Authenticated App ──────────────────────────────────────────────────────────

# Show a soft offline warning — do NOT stop the app
db = get_db()
if not db.is_connected:
    st.warning(
        "⚠️ **MongoDB Offline** — Running in read-only mode from CSV data. "
        "Add, edit, and delete operations are disabled until MongoDB reconnects.",
        icon="🔌",
    )

# Render top navigation header bar (returns active tab)
active_tab = render_top_navigation(default_tab="📖 Overview")

# Dispatch to view
if "Transactions" in active_tab:
    render_transactions_view()
elif "Insights" in active_tab:
    render_insights_view()
elif "Forecast" in active_tab:
    render_forecast_view()
elif "Settings" in active_tab:
    render_settings_view()
else:
    render_overview_view()
