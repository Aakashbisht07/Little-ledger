"""
Little Ledger - Graceful Empty States & Error Diagnostics
Provides descriptive empty states and connection troubleshooting guides.
"""

import streamlit as st
from config import PALETTE


def render_empty_state(
    title: str = "No Ledger Receipts Found",
    message: str = "No audited expenses have been recorded for the selected cycle.",
    action_label: str = "➕ Add First Expense",
    show_action: bool = True,
):
    """Render an editorial empty state."""
    st.markdown(
        f"""
        <div style="background:{PALETTE['surface']}; border:1px dashed {PALETTE['border']}; border-radius:12px; padding:48px 24px; text-align:center; margin:24px 0;">
            <div style="font-size:36px; margin-bottom:12px;">🌿</div>
            <div style="font-family:'Fraunces', serif; font-size:22px; color:{PALETTE['text_main']}; margin-bottom:8px;">
                {title}
            </div>
            <div style="font-size:13.5px; color:{PALETTE['text_muted']}; max-width:440px; margin:0 auto 20px auto; line-height:1.5;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if show_action:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            if st.button(action_label, type="primary", use_container_width=True):
                st.session_state["show_add_modal"] = True
                st.rerun()


def render_db_offline_banner(error_msg: str):
    """Displays a persistent error banner when MongoDB is unreachable."""
    st.markdown(
        f"""
        <div style="background:#FDF0EE; border:1px solid #F5D0CC; border-radius:10px; padding:18px 22px; margin-bottom:24px;">
            <div style="font-weight:600; color:{PALETTE['error']}; font-size:15px; margin-bottom:6px;">
                ⚠️ MongoDB Connection Offline
            </div>
            <div style="font-size:13px; color:{PALETTE['text_main']}; line-height:1.4;">
                Little Ledger is unable to connect to the persistent database server.<br/>
                <code>{error_msg}</code>
            </div>
            <div style="font-size:12px; color:{PALETTE['text_muted']}; margin-top:8px;">
                Ensure MongoDB is running locally via <code>brew services start mongodb-community@7.0</code> or configure <code>MONGODB_URI</code> in <code>.env</code>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
