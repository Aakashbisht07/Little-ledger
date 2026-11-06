"""
Little Ledger - Settings & Personal Financial Preferences View
Reproducing PDF Page 1: Account architecture, regional units, botanical palette, data export, and security posture.
Full persistence via SettingsManager into MongoDB settings collection.
"""

import json
from datetime import datetime
import streamlit as st
import pandas as pd

from config import PALETTE, format_inr
from database import get_db
from expense_manager import ExpenseManager
from settings_manager import SettingsManager


def render_settings_view():
    db = get_db()
    expense_mgr = ExpenseManager()
    settings_mgr = SettingsManager()

    # Fetch persisted profile and preferences from MongoDB
    profile = settings_mgr.get_profile(st.session_state.get("user_id", "demo_user"))

    # Header Section (Page 1)
    st.markdown(
        f"""<div style="margin-bottom:24px;">
<div style="font-size:11px; text-transform:uppercase; letter-spacing:0.12em; color:{PALETTE['text_muted']};">PREFERENCES & PERSONAL GOVERNANCE</div>
<div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap;">
<div>
<h1 style="font-family:'Fraunces', serif; font-size:38px; font-weight:400; margin:4px 0 2px 0; color:{PALETTE['text_main']};">Account & Ledger Architecture.</h1>
<div style="font-size:15px; color:{PALETTE['text_muted']};">Calibrate your regional currency, editorial density, security posture, and data portability.</div>
</div>
<div style="margin-top:8px;">
<span class="ll-badge ll-badge-green" style="font-size:12px; padding:6px 12px;">FOLIO N° 284 · LOCAL JOURNAL MODE</span>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Layout: Left folio sidebar + Right sections
    c_left, c_right = st.columns([1.0, 2.4], gap="large")

    with c_left:
        st.markdown(
            f"""<div class="ll-card" style="background:#FAF8F3; border:1px solid {PALETTE['border']};">
<div style="font-size:10px; text-transform:uppercase; letter-spacing:0.12em; color:{PALETTE['text_muted']}; margin-bottom:8px;">ACTIVE FOLIO</div>
<div style="font-family:'Fraunces', serif; font-size:20px; font-weight:600; color:{PALETTE['text_main']}; margin-bottom:4px;">{profile.get('ledger_identifier', 'FOLIO-BLR-2024-098')}</div>
<div style="font-size:12px; color:{PALETTE['primary_dark']}; font-weight:500; margin-bottom:16px;">🔒 Encrypted Vault Rail</div>
<div style="border-top:1px solid #E8E4DA; padding-top:14px; margin-bottom:14px;">
<div style="font-size:11px; font-weight:600; color:{PALETTE['text_muted']}; text-transform:uppercase; margin-bottom:6px;">THE LEDGER PHILOSOPHY</div>
<div style="font-size:12.5px; font-style:italic; color:{PALETTE['text_main']}; line-height:1.5;">"A clean balance is not an outcome of thrift, but of conscious rhythm and clarity."</div>
<div style="font-size:11px; color:{PALETTE['text_muted']}; margin-top:6px;">Binding Edition v4.8 · BLR-CORP-SEC</div>
</div>
<div style="border-top:1px solid #E8E4DA; padding-top:14px;">
<div style="font-size:11px; font-weight:600; color:{PALETTE['text_muted']}; text-transform:uppercase; margin-bottom:8px;">CONNECTED FINANCIAL RAILS</div>
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; font-size:12.5px;"><span>UPI Rails (NPCI)</span><span class="ll-badge ll-badge-green" style="font-size:10px;">LIVE</span></div>
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; font-size:12.5px;"><span>Account Aggregator (RBI)</span><span class="ll-badge ll-badge-neutral" style="font-size:10px;">SYNCED</span></div>
<div style="display:flex; justify-content:space-between; align-items:center; font-size:12.5px;"><span>MongoDB Local Vault</span><span class="ll-badge ll-badge-green" style="font-size:10px;">ACTIVE (PORT 27017)</span></div>
</div>
</div>""",
            unsafe_allow_html=True,
        )

    with c_right:
        # SECTION 01: User Folio & Identity
        st.markdown(
            f"""<div class="ll-card">
<div class="ll-card-header">
<span>SECTION 01 · USER FOLIO &amp; IDENTITY</span>
<span class="ll-badge ll-badge-neutral">PRIMARY ADMINISTRATOR</span>
</div>""",
            unsafe_allow_html=True,
        )

        u_col1, u_col2 = st.columns(2)
        with u_col1:
            full_name = st.text_input("Full Name", value=profile.get("full_name", "Aarav Sharma"), key="set_name_input")
            email = st.text_input("Primary Email", value=profile.get("email", "aarav.sharma@ledgerfolio.in"), key="set_email_input")
        with u_col2:
            st.text_input("Ledger Identifier", value=profile.get("ledger_identifier", "FOLIO-BLR-2024-098"), disabled=True)
            st.text_input("Member Since", value=profile.get("member_since", "January 2023 (Active Ledger)"), disabled=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Save Profile Adjustments", type="primary", key="save_profile_btn"):
            if not full_name.strip():
                st.error("Full Name cannot be empty.")
            else:
                success = settings_mgr.update_profile(
                    st.session_state.get("user_id", "demo_user"),
                    {
                        "full_name": full_name.strip(),
                        "email": email.strip(),
                    },
                )
                if success:
                    st.session_state["display_name"] = full_name.strip()
                    st.success(f"Profile saved to MongoDB! Welcome, {full_name.strip()}.")
                    st.rerun()
                else:
                    st.error("Failed to persist profile adjustments to MongoDB.")

        st.markdown("</div>", unsafe_allow_html=True)

        # SECTION 02: Regional & Financial Units
        curr_options = ["Indian Rupee (INR ₹)", "US Dollar (USD $)", "Euro (EUR €)"]
        curr_idx = curr_options.index(profile.get("base_currency")) if profile.get("base_currency") in curr_options else 0

        fisc_options = ["Indian Financial Year (Apr - Mar)", "Calendar Year (Jan - Dec)"]
        fisc_idx = fisc_options.index(profile.get("fiscal_calendar")) if profile.get("fiscal_calendar") in fisc_options else 0

        num_options = ["Indian Lakhs & Crores (1,00,000.00)", "International Western (100,000.00)"]
        num_idx = num_options.index(profile.get("number_format")) if profile.get("number_format") in num_options else 0

        date_options = ["Mon DD, YYYY (Sep 20, 2024)", "DD/MM/YYYY (20/09/2024)"]
        date_idx = date_options.index(profile.get("date_format")) if profile.get("date_format") in date_options else 0

        st.markdown(
            f"""<div class="ll-card">
<div class="ll-card-header">
<span>SECTION 02 · REGIONAL &amp; FINANCIAL UNITS</span>
<span class="ll-badge ll-badge-green">INR RAIL DEFAULT</span>
</div>""",
            unsafe_allow_html=True,
        )

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            base_curr = st.selectbox("Base Currency", curr_options, index=curr_idx, key="set_curr")
            fiscal_cal = st.selectbox("Fiscal Calendar", fisc_options, index=fisc_idx, key="set_fisc")
        with r_col2:
            num_fmt = st.selectbox("Number Formatting", num_options, index=num_idx, key="set_numfmt")
            date_fmt = st.selectbox("Date Display Format", date_options, index=date_idx, key="set_datefmt")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Save Regional Units", type="secondary", key="save_units_btn"):
            settings_mgr.update_profile(
                st.session_state.get("user_id", "demo_user"),
                {
                    "base_currency": base_curr,
                    "fiscal_calendar": fiscal_cal,
                    "number_format": num_fmt,
                    "date_format": date_fmt,
                },
            )
            st.success("Regional currency and formatting units synchronized to MongoDB!")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # SECTION 03: Aesthetic & Editorial Mode
        theme_options = ["Botanical Linen (Warm Cream)", "Graphite Dark Mode (Midnight Folio)"]
        theme_idx = theme_options.index(profile.get("theme")) if profile.get("theme") in theme_options else 0

        dens_options = ["Comfortable Editorial", "Compact Technical Ledger"]
        dens_idx = dens_options.index(profile.get("typography_density")) if profile.get("typography_density") in dens_options else 0

        st.markdown(
            f"""<div class="ll-card">
<div class="ll-card-header">
<span>SECTION 03 · AESTHETIC &amp; EDITORIAL MODE</span>
<span class="ll-badge ll-badge-neutral">BOTANICAL CREAM</span>
</div>""",
            unsafe_allow_html=True,
        )

        a_col1, a_col2 = st.columns(2)
        with a_col1:
            theme_choice = st.radio("Editorial Color Theme", theme_options, index=theme_idx, key="set_theme")
        with a_col2:
            dens_choice = st.radio("Typography Density", dens_options, index=dens_idx, key="set_dens")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Save Editorial Mode", type="secondary", key="save_theme_btn"):
            settings_mgr.update_profile(
                st.session_state.get("user_id", "demo_user"),
                {
                    "theme": theme_choice,
                    "typography_density": dens_choice,
                },
            )
            st.success("Editorial theme preferences saved to MongoDB!")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # SECTION 04: Data Portability & Archive
        st.markdown(
            f"""<div class="ll-card">
<div class="ll-card-header">
<span>SECTION 04 · DATA PORTABILITY &amp; ARCHIVE</span>
<span class="ll-badge ll-badge-neutral">MONGODB VAULT</span>
</div>
<div style="font-size:13px; color:{PALETTE['text_muted']}; margin-bottom:16px;">
Export your complete transaction history, budget allocations, and model telemetry into an uncompressed JSON archive.
</div>""",
            unsafe_allow_html=True,
        )

        all_expenses, _ = expense_mgr.get_expenses(user_id=st.session_state.get("user_id", "demo_user"), limit=5000)
        json_export = json.dumps(all_expenses, default=str, indent=2)
        st.download_button(
            "📥 Export Full Vault (JSON)",
            data=json_export,
            file_name=f"little_ledger_vault_backup_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            key="dl_vault_json_btn",
        )

        st.markdown("</div>", unsafe_allow_html=True)
