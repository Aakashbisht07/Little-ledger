"""
Little Ledger — Login & Register View
Botanical-themed authentication page matching the app's design system.
"""

import streamlit as st
from auth import register_user, login_user
from config import PALETTE


_AUTH_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600&family=Inter:wght@400;500&display=swap');

.auth-shell {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {PALETTE['bg_main']};
}}

.auth-card {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 20px;
    padding: 48px 52px;
    max-width: 440px;
    width: 100%;
    box-shadow: 0 4px 32px rgba(41,45,41,0.07);
    margin: 0 auto;
}}

.auth-brand {{
    font-family: 'Fraunces', serif;
    font-size: 28px;
    font-weight: 600;
    color: {PALETTE['primary_dark']};
    letter-spacing: -0.5px;
    text-align: center;
    margin-bottom: 4px;
}}

.auth-tagline {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: {PALETTE['text_muted']};
    text-align: center;
    margin-bottom: 32px;
}}

.auth-divider {{
    border: none;
    border-top: 1px solid {PALETTE['border']};
    margin: 24px 0;
}}

.auth-switch {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: {PALETTE['text_muted']};
    text-align: center;
    margin-top: 20px;
}}

.auth-switch b {{
    color: {PALETTE['primary_green']};
    cursor: pointer;
}}

/* Override Streamlit input styles inside auth card */
div[data-testid="stTextInput"] label {{
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: {PALETTE['text_muted']};
}}

div[data-testid="stTextInput"] input {{
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    background: {PALETTE['bg_main']};
    color: {PALETTE['text_main']};
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    padding: 10px 14px;
}}

div[data-testid="stTextInput"] input:focus {{
    border-color: {PALETTE['primary_green']};
    box-shadow: 0 0 0 3px rgba(101,123,104,0.12);
}}

div[data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
}}

div[data-testid="stButton"] button,
div[data-testid="stFormSubmitButton"] button {{
    background: {PALETTE['primary_dark']};
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    padding: 12px 0;
    width: 100%;
    cursor: pointer;
    transition: background 0.2s ease;
}}

div[data-testid="stButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:hover {{
    background: {PALETTE['primary_green']};
}}
</style>
"""


def render_login_page():
    """Render the full-page login / register screen."""
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    # Initialize tab state
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    # Center the card using columns
    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        st.markdown(
            f"""
            <div style="text-align:center; margin-bottom: 8px;">
                <span style="font-size: 36px;">🌿</span>
            </div>
            <div class="auth-brand">Little Ledger</div>
            <div class="auth-tagline">Your money has a story. Make it easier to understand.</div>
            """,
            unsafe_allow_html=True,
        )

        # Tab switcher
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        # ── LOGIN TAB ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="your_username",
                    key="login_username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    key="login_password",
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign In →", use_container_width=True)

            if submit_login:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    with st.spinner("Authenticating…"):
                        success, msg, user = login_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.display_name = user["display_name"]
                        st.rerun()
                    else:
                        st.error(msg)

        # ── REGISTER TAB ───────────────────────────────────────────────────────
        with tab_register:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            with st.form("register_form", clear_on_submit=False):
                new_display = st.text_input(
                    "Full Name",
                    placeholder="e.g. Rahul Sharma",
                    key="reg_display",
                )
                new_username = st.text_input(
                    "Username",
                    placeholder="e.g. rahul_sharma  (letters, numbers, _)",
                    key="reg_username",
                )
                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="At least 6 characters",
                    key="reg_password",
                )
                new_password2 = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Repeat password",
                    key="reg_password2",
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("Create Account & Sign In →", use_container_width=True)

            if submit_reg:
                if not new_username or not new_password or not new_password2:
                    st.error("Please fill in all required fields.")
                elif new_password != new_password2:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating your account…"):
                        success, msg = register_user(new_username, new_password, new_display)
                    if success:
                        clean_uid = new_username.strip().lower()
                        clean_name = new_display.strip() or clean_uid
                        st.session_state.authenticated = True
                        st.session_state.user_id = clean_uid
                        st.session_state.display_name = clean_name
                        st.rerun()
                    else:
                        st.error(msg)

        # Footer
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:28px;
                        font-family:'Inter',sans-serif; font-size:12px;
                        color:{PALETTE['text_light']};">
                🔒 Your data is private and securely stored per account.
            </div>
            """,
            unsafe_allow_html=True,
        )

