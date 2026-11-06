"""
Little Ledger - Top Navigation & Folio Header
Renders the horizontal segmented navbar, period controls, Add Expense modal trigger, and user avatar.
Guarantees NO left sidebar navigation.
"""

from datetime import datetime
import streamlit as st
from config import PALETTE, CUSTOM_CSS
from components.expense_form import show_expense_dialog
from database import get_db

NAV_TABS = [
    "📖 Overview",
    "🧾 Transactions",
    "📊 Insights",
    "🧠 Forecast Lab",
    "⚙ Settings",
]


def render_top_navigation(default_tab: str = "📖 Overview") -> str:
    """
    Renders the persistent editorial header and horizontal segmented navigation bar.
    Returns the currently active tab name.
    """
    # Inject styling
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Display pending toast notifications
    if "toast_message" in st.session_state and st.session_state["toast_message"]:
        msg = st.session_state.pop("toast_message")
        st.toast(msg, icon="✅")

    # Initialize navigation session states
    if "selected_period" not in st.session_state:
        st.session_state["selected_period"] = "Sep 2026"
    if "active_nav_tab" not in st.session_state:
        # Check query param first if available
        query_tab = st.query_params.get("tab", None)
        matched_tab = default_tab
        if query_tab:
            for tab in NAV_TABS:
                if query_tab.lower() in tab.lower():
                    matched_tab = tab
                    break
        st.session_state["active_nav_tab"] = matched_tab

    # Top Navigation Row (Symmetrical columns: Left 2.4 | Center 5.2 | Right 2.4)
    c_brand, c_nav, c_controls = st.columns([2.4, 5.2, 2.4], gap="small", vertical_alignment="center")

    with c_brand:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:34px; height:34px; background:#EDF1EC; border:1px solid #DCE3DB; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:17px; flex-shrink:0;">
                    🌿
                </div>
                <div>
                    <div style="font-family:'Fraunces', serif; font-size:17px; font-weight:600; color:{PALETTE['text_main']}; line-height:1.1; letter-spacing:-0.01em; white-space:nowrap;">
                        Little Ledger
                    </div>
                    <div style="font-size:8.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:{PALETTE['text_muted']}; white-space:nowrap;">
                        EDITORIAL FOLIO
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_nav:
        curr_selection = st.session_state.get("active_nav_tab", default_tab)
        if curr_selection not in NAV_TABS:
            curr_selection = default_tab

        selected = st.segmented_control(
            "Navigation Menu",
            options=NAV_TABS,
            default=curr_selection,
            label_visibility="collapsed",
            key="_top_nav_segmented_control",
        )
        if selected and selected != st.session_state.get("active_nav_tab"):
            st.session_state["active_nav_tab"] = selected
            clean_name = selected.split()[-1]
            st.query_params["tab"] = clean_name
            st.rerun()

    with c_controls:
        rc1, rc2, rc3 = st.columns([1.8, 1.6, 1.1], gap="small", vertical_alignment="center")

        with rc1:            # Build periods dynamically from MongoDB for the active user
            curr_uid = st.session_state.get("user_id", "")
            try:
                db = get_db()
                pipeline = [
                    {"$match": {"user_id": curr_uid}},
                    {"$group": {
                        "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}}
                    }},
                    {"$sort": {"_id.year": -1, "_id.month": -1}}
                ]
                month_names_inv = {
                    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
                }
                raw_periods = list(db.expenses.aggregate(pipeline))
                periods = []
                for rp in raw_periods:
                    yr = rp["_id"]["year"]
                    mo = rp["_id"]["month"]
                    periods.append(f"{month_names_inv[mo]} {yr}")
                if not periods:
                    periods = ["May 2026", "Sep 2026"]
            except Exception:
                periods = ["May 2026", "Sep 2026", "Sep 2024"]

            # Add "All Time" option
            periods_list = ["All Time"] + periods

            current_sel = st.session_state.get("selected_period")
            if not current_sel or current_sel not in periods_list:
                current_sel = periods_list[1] if len(periods_list) > 1 else "All Time"
                st.session_state["selected_period"] = current_sel

            curr_idx = periods_list.index(current_sel) if current_sel in periods_list else 0

            new_period = st.selectbox(
                "Cycle Period",
                periods_list,
                index=curr_idx,
                label_visibility="collapsed",
            )
            if new_period != current_sel:
                st.session_state["selected_period"] = new_period
                st.rerun()



        with rc2:
            if st.button("➕ Outlay", key="nav_btn_add_expense", type="primary", use_container_width=True):
                show_expense_dialog()

        # User avatar + logout
        _uid = st.session_state.get("user_id", "")
        _display = st.session_state.get("display_name", _uid)
        name_parts = _display.strip().split()
        initials = "".join(p[0].upper() for p in name_parts[:2]) if name_parts else "LL"
        first_name = name_parts[0] if name_parts else "User"

        with rc3:
            if st.button(
                initials,
                key="nav_btn_avatar",
                help=f"Signed in as {_display} · Click to sign out",
                use_container_width=True,
            ):
                for key in ["authenticated", "user_id", "display_name"]:
                    st.session_state.pop(key, None)
                st.rerun()

    # Subtitle Folio Strip
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin:12px 0 20px 0; padding-bottom:10px; border-bottom:1px solid #E8E4DA; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; color:{PALETTE['text_muted']};">
            <div>
                <span style="color:{PALETTE['primary_dark']}; font-weight:600;">•</span> LEDGER VOL. IV 
                <span style="color:#C5BFB0; margin:0 6px;">•</span> PERSONAL FOLIO 
                <span style="color:#C5BFB0; margin:0 6px;">•</span> {first_name.upper()}'S ACCOUNT
            </div>
            <div style="font-weight:500;">
                ACTIVE CYCLE: <b style="color:{PALETTE['text_main']};">{st.session_state.get('selected_period', 'All Time').upper()}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return st.session_state.get("active_nav_tab", default_tab)
