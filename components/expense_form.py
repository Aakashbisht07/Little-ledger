"""
Little Ledger - Expense Entry Component (PDF Page 6 Reference)
Implements audited expense creation and modification with live validation, MongoDB persistence,
and native modal dialog presentation via @st.dialog.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
import streamlit as st

from config import CATEGORIES, PAYMENT_METHODS, PALETTE, format_inr
from expense_manager import ExpenseManager, ExpenseValidationError


@st.dialog("Record an Expense — NEW ENTRY · LEDGER OUTLAY", width="large")
def show_expense_dialog(edit_expense: Optional[Dict[str, Any]] = None):
    """
    Native Streamlit modal dialog reproducing PDF Page 6:
    'Record an Expense - NEW ENTRY - LEDGER OUTLAY'.
    """
    expense_mgr = ExpenseManager()
    is_edit = edit_expense is not None
    title = "Edit Disbursement" if is_edit else "Log Audited Disbursement"

    st.markdown(
        f"""
        <div style="background:{PALETTE['surface_alt']}; padding:14px 20px; border-radius:10px; border:1px solid {PALETTE['border']}; margin-bottom:18px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.12em; color:{PALETTE['text_muted']};">
                Double-Entry Verified Financial Record
            </div>
            <div style="font-family:'Fraunces', serif; font-size:18px; color:{PALETTE['primary_dark']}; margin-top:2px;">
                {title} to your personal ledger.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("modal_expense_form", clear_on_submit=False):
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            default_amount = float(edit_expense.get("amount", 0.0)) if is_edit else 0.0
            amount = st.number_input(
                "TOTAL TRANSACTION AMOUNT (INR)",
                min_value=0.0,
                value=default_amount,
                step=50.0,
                format="%.2f",
                help="Includes applicable taxes and service charges.",
            )

            default_merchant = edit_expense.get("merchant", "") if is_edit else ""
            merchant = st.text_input(
                "MERCHANT / PAYEE NAME",
                value=default_merchant,
                placeholder="e.g. Blue Tokai Artisan Roastery",
            )

            default_cat = edit_expense.get("category", "Food & Dining") if is_edit else "Food & Dining"
            cat_idx = CATEGORIES.index(default_cat) if default_cat in CATEGORIES else 0
            category = st.selectbox("CATEGORY ALLOCATION", CATEGORIES, index=cat_idx)

        with col2:
            # Default date = last day of selected period (so entry lands in correct month)
            period_str = st.session_state.get("selected_period", "Sep 2024")
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
            }
            import calendar
            parts = period_str.split()
            try:
                p_m = month_map.get(parts[0], 9)
                p_y = int(parts[1]) if len(parts) > 1 else 2024
                _, max_d = calendar.monthrange(p_y, p_m)
                now_dt = datetime.now()
                # If selected period is the current actual month, use today's date; else use last day
                if now_dt.year == p_y and now_dt.month == p_m:
                    default_date = now_dt.date()
                else:
                    default_date = date(p_y, p_m, max_d)
            except Exception:
                default_date = datetime.now().date()

            if is_edit and edit_expense.get("date"):
                ed = edit_expense["date"]
                if isinstance(ed, datetime):
                    default_date = ed.date()
                elif isinstance(ed, str):
                    try:
                        default_date = datetime.fromisoformat(ed[:10]).date()
                    except Exception:
                        pass

            tx_date = st.date_input("ENTRY DATE", value=default_date)

            default_pm = edit_expense.get("payment_method", "UPI") if is_edit else "UPI"
            pm_idx = PAYMENT_METHODS.index(default_pm) if default_pm in PAYMENT_METHODS else 0
            payment_method = st.selectbox("PAYMENT RAIL", PAYMENT_METHODS, index=pm_idx)

            default_memo = edit_expense.get("description", "") if is_edit else ""
            description = st.text_input(
                "FIELD MEMO & ANNOTATION",
                value=default_memo,
                placeholder="e.g. Team morning review meeting and pour-over setup",
            )

        notes = st.text_area(
            "OPTIONAL FISCAL NOTES / RECEIPT TAGS",
            value=edit_expense.get("notes", "") if is_edit else "",
            placeholder="Digital slip verified & matched against bank feeds",
            height=60,
        )

        st.markdown(
            f"""
            <div style="font-size:11px; color:{PALETTE['text_muted']}; margin:4px 0 12px 0;">
                🔒 ENCRYPTED &amp; STORED LOCALLY IN MONGODB · DOUBLE-ENTRY BALANCE VALID
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_c1, btn_c2 = st.columns([2, 1])
        with btn_c1:
            saved = st.form_submit_button("💾 Save to Ledger", type="primary", use_container_width=True)
        with btn_c2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if saved:
            if amount <= 0:
                st.error("⚠️ Please specify a positive transaction amount greater than ₹0.00.")
            elif not merchant.strip():
                st.error("⚠️ Merchant / Payee name is required.")
            else:
                try:
                    tx_datetime = datetime.combine(tx_date, datetime.min.time())
                    cycle_period = tx_datetime.strftime("%b %Y")

                    if is_edit:
                        success = expense_mgr.update_expense(
                            edit_expense["id"],
                            {
                                "amount": amount,
                                "merchant": merchant.strip(),
                                "category": category,
                                "date": tx_datetime,
                                "payment_method": payment_method,
                                "description": description.strip(),
                                "notes": notes.strip(),
                            },
                        )
                        if success:
                            st.session_state["selected_period"] = cycle_period
                            st.session_state["toast_message"] = f"Record for {merchant.strip()} (₹{amount:,.2f}) updated successfully in MongoDB!"
                            st.rerun()
                        else:
                            st.error("Failed to update transaction.")
                    else:
                        current_uid = st.session_state.get("user_id", "demo_user")
                        new_id = expense_mgr.add_expense(
                            amount=amount,
                            merchant=merchant.strip(),
                            category=category,
                            date_val=tx_datetime,
                            payment_method=payment_method,
                            description=description.strip(),
                            notes=notes.strip(),
                            user_id=current_uid,
                        )
                        st.session_state["selected_period"] = cycle_period
                        st.session_state["tx_page"] = 1
                        st.session_state["toast_message"] = f"Disbursement of ₹{amount:,.2f} at {merchant.strip()} recorded to Ledger ({cycle_period})!"
                        st.rerun()
                except ExpenseValidationError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Error saving to MongoDB: {str(e)}")

        if cancel:
            st.rerun()


def render_expense_modal(edit_expense: Optional[Dict[str, Any]] = None):
    """Wrapper to invoke the dialog modal."""
    show_expense_dialog(edit_expense=edit_expense)
