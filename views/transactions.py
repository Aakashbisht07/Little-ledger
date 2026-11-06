"""
Little Ledger - Transactions & Audited Ledger View
Reproducing PDF Page 3: Audited double-entry ledger table, filters, pagination, CSV import/export, and in-place Edit/Delete.
"""

import json
from datetime import datetime
import streamlit as st
import pandas as pd

from config import PALETTE, CATEGORIES, PAYMENT_METHODS, format_inr
from database import get_db
from expense_manager import ExpenseManager
from analytics import get_month_date_range
from components.empty_states import render_empty_state
from components.expense_form import show_expense_dialog


@st.dialog("Edit Expense Record", width="large")
def show_edit_expense_dialog(expense: dict):
    """
    Modal dialog allowing the user to edit an existing expense directly in MongoDB.
    """
    st.markdown(
        f"""
        <div style="font-size:13px; color:{PALETTE['text_muted']}; margin-bottom:16px;">
            Modify details for <b>{expense.get('merchant', 'Expense')}</b>. Updates persist to MongoDB immediately.
        </div>
        """,
        unsafe_allow_html=True,
    )

    exp_id = expense.get("id") or str(expense.get("_id", ""))

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        merchant = st.text_input("Merchant / Payee", value=expense.get("merchant", ""), key=f"edit_m_{exp_id}")
    with c2:
        amount = st.number_input(
            "Amount (INR ₹)",
            value=float(expense.get("amount", 0.0)),
            min_value=0.01,
            step=10.0,
            format="%.2f",
            key=f"edit_a_{exp_id}",
        )

    c3, c4 = st.columns(2)
    with c3:
        cat_idx = CATEGORIES.index(expense.get("category")) if expense.get("category") in CATEGORIES else 0
        category = st.selectbox("Category", CATEGORIES, index=cat_idx, key=f"edit_c_{exp_id}")
    with c4:
        pm_idx = PAYMENT_METHODS.index(expense.get("payment_method")) if expense.get("payment_method") in PAYMENT_METHODS else 0
        payment_method = st.selectbox("Payment Rail", PAYMENT_METHODS, index=pm_idx, key=f"edit_pm_{exp_id}")

    raw_date = expense.get("date")
    if isinstance(raw_date, datetime):
        d_val = raw_date.date()
    elif isinstance(raw_date, str):
        try:
            d_val = datetime.fromisoformat(raw_date[:10]).date()
        except Exception:
            d_val = datetime.now().date()
    else:
        d_val = datetime.now().date()

    c5, c6 = st.columns(2)
    with c5:
        date_val = st.date_input("Transaction Date", value=d_val, key=f"edit_d_{exp_id}")
    with c6:
        is_rec = st.checkbox("Recurring Subscription", value=bool(expense.get("is_recurring", False)), key=f"edit_rec_{exp_id}")

    description = st.text_area("Memo / Description", value=expense.get("description", ""), height=70, key=f"edit_desc_{exp_id}")

    col_save, col_cancel = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Changes", type="primary", use_container_width=True, key=f"save_btn_{exp_id}"):
            mgr = ExpenseManager()
            update_data = {
                "merchant": merchant.strip(),
                "amount": float(amount),
                "category": category,
                "payment_method": payment_method,
                "date": datetime.combine(date_val, datetime.min.time()),
                "description": description.strip(),
                "is_recurring": is_rec,
            }
            try:
                success = mgr.update_expense(exp_id, update_data)
                if success:
                    st.session_state["toast_message"] = f"Record for {merchant.strip()} (₹{amount:,.2f}) updated successfully in MongoDB!"
                    st.rerun()
                else:
                    st.error("Update failed. Transaction could not be found.")
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

    with col_cancel:
        if st.button("Cancel", use_container_width=True, key=f"cancel_btn_{exp_id}"):
            st.rerun()


@st.dialog("Confirm Deletion")
def show_delete_expense_dialog(expense: dict):
    """
    Modal dialog confirming deletion of an expense from MongoDB.
    """
    exp_id = expense.get("id") or str(expense.get("_id", ""))
    amt_fmt = format_inr(expense.get("amount", 0.0))
    merchant = expense.get("merchant", "this entry")

    st.markdown(
        f"""
        <div style="font-size:14px; color:{PALETTE['text_main']}; margin-bottom:16px;">
            Are you sure you want to permanently delete the verified entry for <b>{merchant}</b> of <b>{amt_fmt}</b>?
        </div>
        <div style="font-size:12px; color:#A84030; margin-bottom:20px;">
            ⚠️ This action cannot be undone and will update your monthly totals immediately.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True, key=f"confirm_del_{exp_id}"):
            mgr = ExpenseManager()
            try:
                success = mgr.delete_expense(exp_id)
                if success:
                    st.success("Entry removed from ledger.")
                    st.rerun()
                else:
                    st.error("Delete failed: Transaction could not be found.")
            except Exception as e:
                st.error(f"Delete failed: {e}")
    with c2:
        if st.button("Cancel", use_container_width=True, key=f"cancel_del_{exp_id}"):
            st.rerun()


@st.dialog("⚠️ Reset All Ledger Data", width="small")
def show_reset_data_dialog():
    """
    Confirmation modal prompting the user before wiping all data
    and resetting to the clean state of a fresh login.
    """
    st.markdown(
        f"""
        <div style="font-size:15px; font-weight:600; color:{PALETTE['text_main']}; margin-bottom:8px;">
            Are you sure you want to remove all your data?
        </div>
        <div style="font-size:13px; color:{PALETTE['text_muted']}; line-height:1.5; margin-bottom:14px;">
            This will permanently delete all your recorded expenses, custom monthly budget ceilings, envelope targets, and predictive models.
        </div>
        <div style="font-size:12px; color:{PALETTE['error']}; background:#FDF0EE; border:1px solid #F5D0CC; border-radius:8px; padding:10px 12px; margin-bottom:18px;">
            ⚠️ <b>Note:</b> Your workspace will be reset to a completely fresh state, exactly as when you first logged in. This action cannot be undone.
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("Cancel", use_container_width=True, key="reset_dialog_cancel"):
            st.rerun()
    with col_d:
        if st.button("🗑️ Yes, Reset All", type="primary", use_container_width=True, key="reset_dialog_confirm"):
            uid = st.session_state.get("user_id", "")
            if uid:
                db = get_db()
                if db.is_connected and db.db is not None:
                    db.expenses.delete_many({"user_id": uid})
                    db.budgets.delete_many({"user_id": uid})
                    db.predictions.delete_many({"user_id": uid})
                    db.settings.delete_many({"user_id": uid})
                # Reset pagination and period state
                st.session_state.pop("selected_period", None)
                st.session_state["tx_page"] = 1
                st.success("All data has been wiped. Reset to fresh state!")
                st.rerun()


@st.dialog("📥 Add JSON Transaction Data", width="medium")
def show_import_json_dialog():
    """
    Modal allowing the user to import transactions via JSON upload or raw JSON paste.
    """
    st.markdown(
        f"""
        <div style="font-size:13.5px; color:{PALETTE['text_main']}; margin-bottom:6px;">
            Import receipts directly into your MongoDB ledger using JSON.
        </div>
        <div style="font-size:12px; color:{PALETTE['text_muted']}; line-height:1.4; margin-bottom:16px;">
            Supported format: a JSON array of objects, e.g.<br/>
            <code>[{{"date": "2026-09-15", "merchant": "Swiggy", "amount": 420, "category": "Food & Dining", "payment_method": "UPI"}}]</code>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_json = st.file_uploader(
        "Upload JSON file (.json)",
        type=["json"],
        key="tx_json_uploader",
    )
    json_text = st.text_area(
        "Or paste JSON payload",
        height=140,
        placeholder='[\n  {\n    "date": "2026-09-15",\n    "merchant": "Blue Tokai",\n    "amount": 280,\n    "category": "Food & Dining",\n    "payment_method": "UPI"\n  }\n]',
        key="tx_json_paste_area",
    )

    col_j1, col_j2 = st.columns(2)
    with col_j1:
        if st.button("Cancel", use_container_width=True, key="tx_json_cancel_btn"):
            st.rerun()
    with col_j2:
        if st.button("📥 Import Records", type="primary", use_container_width=True, key="tx_json_submit_btn"):
            payload_str = ""
            if uploaded_json is not None:
                try:
                    payload_str = uploaded_json.getvalue().decode("utf-8")
                except Exception as e:
                    st.error(f"Failed to read uploaded file: {e}")
            elif json_text and json_text.strip():
                payload_str = json_text.strip()

            if not payload_str:
                st.error("Please upload a JSON file or paste JSON data.")
            else:
                mgr = ExpenseManager()
                uid = st.session_state.get("user_id", "demo_user")
                with st.spinner("Importing JSON receipts into MongoDB..."):
                    res = mgr.import_from_json(payload_str, user_id=uid)

                imported = res.get("imported", 0)
                skipped = res.get("skipped", 0)
                errs = res.get("errors", [])
                if imported > 0:
                    st.session_state.pop("selected_period", None)
                    st.session_state["tx_page"] = 1
                    msg = f"Successfully imported {imported} transaction{'s' if imported > 1 else ''}!"
                    if skipped > 0:
                        msg += f" ({skipped} skipped)"
                    st.success(msg)
                    st.rerun()
                else:
                    err_msg = errs[0].get("error", "Unknown validation error") if errs else "No valid transactions found."
                    st.error(f"Import failed: {err_msg}")


def render_transactions_view():
    db = get_db()
    expense_mgr = ExpenseManager()

    # Determine selected period
    period_str = st.session_state.get("selected_period", "Sep 2026")
    if period_str == "All Time":
        start_dt = None
        end_dt = None
        selected_month_name = "All"
        selected_year = "Time"
    else:
        month_names = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
        }
        parts = period_str.split()
        selected_month_name = parts[0]
        selected_year = int(parts[1]) if len(parts) > 1 else 2026
        selected_month = month_names.get(selected_month_name, 9)
        start_dt, end_dt = get_month_date_range(selected_year, selected_month)

    # Header Section (Page 3)
    header_subtitle = f"PERSONAL LEDGER COLLECTION · FASCICLE IX · {selected_month_name.upper()} {selected_year}" if period_str != "All Time" else "PERSONAL LEDGER COLLECTION · ALL AUDITED RECORDS"
    st.markdown(
        f"""
        <div style="margin-bottom:16px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.12em; color:{PALETTE['text_muted']};">
                {header_subtitle}
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap;">
                <div>
                    <h1 style="font-family:'Fraunces', serif; font-size:36px; font-weight:400; margin:4px 0 2px 0; color:{PALETTE['text_main']};">
                        The Ledger
                    </h1>
                    <div style="font-size:14px; color:{PALETTE['text_muted']};">
                        Folio N° 284 · Double-entry verified records matching statements and bank rails.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search & Filter Toolbar
    f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2, 2, 2])
    with f_col1:
        search_query = st.text_input("Search", placeholder="Search merchant, tag, or memo...", label_visibility="collapsed", key="tx_search_in")
    with f_col2:
        cat_options = ["All Categories"] + CATEGORIES
        selected_category = st.selectbox("Category Filter", cat_options, label_visibility="collapsed", key="tx_cat_sel")
    with f_col3:
        pm_options = ["All Payment Rails"] + PAYMENT_METHODS
        selected_pm = st.selectbox("Rail Filter", pm_options, label_visibility="collapsed", key="tx_pm_sel")
    with f_col4:
        sort_options = ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"]
        selected_sort = st.selectbox("Sort Order", sort_options, label_visibility="collapsed", key="tx_sort_sel")

    # Map filters to MongoDB query
    category_filter = None if selected_category == "All Categories" else selected_category
    pm_filter = None if selected_pm == "All Payment Rails" else selected_pm

    sort_field = "date"
    sort_desc = True
    if selected_sort == "Oldest First":
        sort_desc = False
    elif selected_sort == "Highest Amount":
        sort_field = "amount"
        sort_desc = True
    elif selected_sort == "Lowest Amount":
        sort_field = "amount"
        sort_desc = False

    # Pagination state
    if "tx_page" not in st.session_state:
        st.session_state["tx_page"] = 1

    page_size = 10
    skip = (st.session_state["tx_page"] - 1) * page_size

    expenses, total_matching = expense_mgr.get_expenses(
        user_id=st.session_state.get("user_id", "demo_user"),
        start_date=start_dt,
        end_date=end_dt,
        category=category_filter,
        payment_method=pm_filter,
        search_query=search_query,
        sort_by=sort_field,
        sort_descending=sort_desc,
        limit=page_size,
        skip=skip,
    )

    # Summary strip & Action Controls (Export CSV, Add JSON, Record Expense, Reset)
    summary_col1, col_btn_csv, col_btn_json, col_btn_add, col_btn_reset = st.columns(
        [3.0, 1.8, 1.8, 1.8, 1.3], gap="small", vertical_alignment="center"
    )
    with summary_col1:
        st.markdown(
            f"""
            <div style="font-size:13px; color:{PALETTE['text_muted']};">
                Showing <b>{min(total_matching, skip + 1) if total_matching > 0 else 0} — {min(total_matching, skip + len(expenses))}</b> of <b>{total_matching}</b> verified entries logged for <b style="color:{PALETTE['text_main']};">{period_str}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_btn_csv:
        all_period_expenses, _ = expense_mgr.get_expenses(
            user_id=st.session_state.get("user_id", "demo_user"), start_date=start_dt, end_date=end_dt, limit=1000
        )
        csv_data = expense_mgr.export_to_csv(all_period_expenses)
        st.download_button(
            "📥 Export CSV",
            data=csv_data,
            file_name=f"little_ledger_{selected_month_name}_{selected_year}.csv",
            mime="text/csv",
            use_container_width=True,
            key="tx_dl_csv_btn",
        )

    with col_btn_json:
        if st.button("📥 Add JSON Data", use_container_width=True, key="tx_add_json_btn"):
            show_import_json_dialog()

    with col_btn_add:
        if st.button("➕ Record Expense", use_container_width=True, type="primary", key="tx_add_top_btn"):
            show_expense_dialog()

    with col_btn_reset:
        if st.button("⚠️ Reset", use_container_width=True, key="tx_reset_data_btn", help="Wipe all data and reset to fresh login state"):
            show_reset_data_dialog()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Transaction Table or Empty State
    if not expenses:
        render_empty_state(
            title=f"No Transactions for {period_str}",
            message=f"No entries logged for {period_str}. Record a new outlay, upload a statement PDF below, or click <b>Add JSON Data</b> above to import receipts.",
            action_label="➕ Log New Outlay",
        )

    else:
        # Table Header
        h_c1, h_c2, h_c3, h_c4, h_c5, h_c6 = st.columns([1.5, 3.2, 1.8, 1.5, 1.5, 1.5], gap="small")
        with h_c1:
            st.markdown("<div style='font-size:11px; font-weight:600; color:#7C8375; text-transform:uppercase;'>ENTRY DATE</div>", unsafe_allow_html=True)
        with h_c2:
            st.markdown("<div style='font-size:11px; font-weight:600; color:#7C8375; text-transform:uppercase;'>MERCHANT / MEMO</div>", unsafe_allow_html=True)
        with h_c3:
            st.markdown("<div style='font-size:11px; font-weight:600; color:#7C8375; text-transform:uppercase;'>CATEGORY</div>", unsafe_allow_html=True)
        with h_c4:
            st.markdown("<div style='font-size:11px; font-weight:600; color:#7C8375; text-transform:uppercase;'>PAYMENT RAIL</div>", unsafe_allow_html=True)
        with h_c5:
            st.markdown("<div style='font-size:11px; font-weight:600; color:#7C8375; text-transform:uppercase; text-align:right;'>AMOUNT (INR)</div>", unsafe_allow_html=True)
        with h_c6:
            st.markdown("<div style='font-size:11px; font-weight:600; color:#7C8375; text-transform:uppercase; text-align:center;'>ACTIONS</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border:none; border-top:1px solid #E8E4DA; margin:6px 0 10px 0;'/>", unsafe_allow_html=True)

        # Transaction Rows with Interactive Edit/Delete
        for exp in expenses:
            d = exp.get("date")
            if isinstance(d, datetime):
                d_fmt = d.strftime("%b %d, %Y")
            elif isinstance(d, str):
                try:
                    d_fmt = datetime.fromisoformat(d[:10]).strftime("%b %d, %Y")
                except Exception:
                    d_fmt = d[:10]
            else:
                d_fmt = "Unknown"

            amt_fmt = format_inr(exp.get("amount", 0.0))
            memo_str = exp.get("description", "")
            exp_id = exp.get("id") or str(exp.get("_id", ""))
            # Determine debit/credit with multiple fallbacks:
            # 1. Explicit stored field, 2. notes text, 3. description keywords, 4. default debit
            if "is_debit" in exp:
                is_debit = bool(exp["is_debit"])
            else:
                notes = (exp.get("notes") or "").lower()
                desc = (exp.get("description") or "").lower()
                if "credit / refund" in notes or "upi-credit" in desc or "neft credit" in desc or "interest cr" in desc:
                    is_debit = False
                else:
                    is_debit = True
            amt_color = "#D94F4F" if is_debit else "#27AE60"
            amt_sign = "− " if is_debit else "+ "

            r_c1, r_c2, r_c3, r_c4, r_c5, r_c6 = st.columns([1.5, 3.2, 1.8, 1.5, 1.5, 1.5], gap="small", vertical_alignment="center")

            with r_c1:
                st.markdown(f"<div style='font-weight:500; font-size:13px; color:#292D29;'>{d_fmt}</div>", unsafe_allow_html=True)
            with r_c2:
                memo_html = f"<div style='font-size:11px; color:#7C8375;'>{memo_str}</div>" if memo_str else ""
                st.markdown(f"<div style='font-weight:600; font-size:13.5px; color:#292D29;'>{exp.get('merchant')}</div>{memo_html}", unsafe_allow_html=True)
            with r_c3:
                st.markdown(f"<span class='ll-badge ll-badge-neutral' style='font-size:11px;'>{exp.get('category')}</span>", unsafe_allow_html=True)
            with r_c4:
                st.markdown(f"<div style='font-size:12px; color:#7C8375;'>{exp.get('payment_method')}</div>", unsafe_allow_html=True)
            with r_c5:
                st.markdown(f"<div style='text-align:right; font-weight:700; font-size:13.5px; color:{amt_color};'>{amt_sign}{amt_fmt}</div>", unsafe_allow_html=True)
            with r_c6:
                act_c1, act_c2 = st.columns(2, gap="small")
                with act_c1:
                    if st.button("✏️", key=f"edit_row_{exp_id}", help=f"Edit {exp.get('merchant')}"):
                        show_edit_expense_dialog(exp)
                with act_c2:
                    if st.button("🗑️", key=f"del_row_{exp_id}", help=f"Delete {exp.get('merchant')}"):
                        show_delete_expense_dialog(exp)

            st.markdown("<hr style='border:none; border-top:1px solid #F0ECE1; margin:6px 0;'/>", unsafe_allow_html=True)

    # Pagination Controls
    total_pages = max(1, (total_matching + page_size - 1) // page_size)
    if total_pages > 1:
        p_col1, p_col2, p_col3, p_col4 = st.columns([2, 1, 1, 2])
        with p_col2:
            if st.button("← Previous", disabled=(st.session_state["tx_page"] <= 1), use_container_width=True, key="tx_prev_page"):
                st.session_state["tx_page"] -= 1
                st.rerun()
        with p_col3:
            if st.button("Next →", disabled=(st.session_state["tx_page"] >= total_pages), use_container_width=True, key="tx_next_page"):
                st.session_state["tx_page"] += 1
                st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # PDF Bank Statement Import Expander
    with st.expander("📄 Import Bank Statement (PDF)", expanded=False):
        st.markdown(
            f"""
            <div style="background:{PALETTE['surface_alt']}; border:1px solid {PALETTE['border']}; border-radius:10px; padding:14px 18px; margin-bottom:14px;">
                <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.1em; color:{PALETTE['text_muted']}; margin-bottom:6px;">
                    SUPPORTED BANKS &amp; CARDS
                </div>
                <div style="font-size:13px; color:{PALETTE['text_main']};">
                    Slice · SBI · HDFC · ICICI · Axis · Kotak · YES Bank · IndusInd · Federal · IDFC First
                </div>
                <div style="font-size:12px; color:{PALETTE['text_muted']}; margin-top:6px;">
                    Upload your monthly e-statement PDF. All spend transactions are extracted automatically —
                    categories and payment rails are inferred from merchant names.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_up, col_pw = st.columns([3, 2])
        with col_up:
            uploaded_pdf = st.file_uploader(
                "Choose PDF bank statement",
                type=["pdf"],
                label_visibility="collapsed",
                key="tx_pdf_uploader",
            )
        with col_pw:
            pdf_password = st.text_input(
                "Password (if PDF is protected)",
                type="password",
                placeholder="e.g. DDMM / mobile / PAN",
                key="tx_pdf_password",
                help="Official statements downloaded directly from bank apps are often encrypted.",
            )

        if uploaded_pdf is not None:
            pdf_bytes = uploaded_pdf.getvalue()

            with st.spinner("Parsing PDF statement…"):
                from pdf_parser import parse_bank_statement_pdf
                parsed_txns, method_used, error_msg = parse_bank_statement_pdf(
                    pdf_bytes, password=pdf_password.strip() if pdf_password else None
                )

                # Also grab raw text for debug view
                raw_text = ""
                try:
                    import pdfplumber, io as _io
                    open_kw = {"password": pdf_password.strip()} if pdf_password else {}
                    with pdfplumber.open(_io.BytesIO(pdf_bytes), **open_kw) as _pdf:
                        raw_text = "\n".join(p.extract_text() or "" for p in _pdf.pages)
                except Exception:
                    try:
                        import fitz
                        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                        if pdf_password and doc.is_encrypted:
                            doc.authenticate(pdf_password.strip())
                        raw_text = "\n".join(page.get_text() for page in doc)
                    except Exception:
                        raw_text = ""

            method_labels = {
                "slice_table": "✦ Slice Account Statement — 5-Column Table Mode",
                "slice_table_pdfplumber": "✦ Slice Account Statement — 5-Column Table Mode",
                "slice_text": "✦ Slice Statement — Block Mode",
                "block_text": "✦ Block Mode — High Recall",
                "slice_fallback": "✦ Slice Statement — Block Mode",
                "pymupdf_blocks": "✦ Slice Statement — PyMuPDF Engine",
                "pymupdf_slice": "✦ Slice Statement — PyMuPDF",
                "table": "✦ Table Mode — High Accuracy",
                "text": "✦ Text Mode — Standard",
                "pymupdf_text": "✦ Text Mode — PyMuPDF",
            }
            method_label = method_labels.get(method_used, f"✦ {method_used}")

            if error_msg:
                st.warning(error_msg)
            elif not parsed_txns:
                st.warning(
                    "⚠️ No spend transactions could be extracted from this PDF. "
                    "If this statement is password-protected, please enter your password in the box above. "
                    "If it is a scanned image PDF, text cannot be read directly."
                )
                if raw_text:
                    with st.expander("🔍 View Raw Extracted Text (for debugging)", expanded=False):
                        st.text(raw_text[:3000])

            else:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                        <span style="font-size:14px; color:{PALETTE['text_main']}; font-weight:600;">
                            Found <b>{len(parsed_txns)}</b> verified transactions
                        </span>
                        <span style="font-size:11px; background:{PALETTE['surface_alt']}; border:1px solid {PALETTE['border']}; border-radius:20px; padding:2px 10px; color:{PALETTE['text_muted']};">
                            {method_label}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Show ALL transactions (no cap)
                preview_df = pd.DataFrame([
                    {
                        "Date": t["date"].strftime("%d %b %Y"),
                        "Merchant / Payee": t["merchant"],
                        "Type": "Debit (Spend)" if t.get("is_debit", True) else "Credit / Refund",
                        "Amount (₹)": f"₹{t['amount']:,.2f}",
                        "Category": t["category"],
                        "Payment Rail": t["payment_method"],
                        "Full Narration": t["description"][:60],
                    }
                    for t in parsed_txns
                ])
                st.dataframe(preview_df, use_container_width=True, hide_index=True, height=min(400, 40 + len(parsed_txns) * 35))


                # Debug raw text toggle
                with st.expander("🔍 View Raw Extracted Text (debug)", expanded=False):
                    st.text(raw_text[:4000] if raw_text else "No raw text available.")

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                imp_col1, imp_col2 = st.columns([2, 1])
                with imp_col1:
                    if st.button(
                        f"💾 Import All {len(parsed_txns)} Transactions to Ledger",
                        type="primary",
                        use_container_width=True,
                        key="tx_pdf_import_btn",
                    ):
                        imported = 0
                        skipped = 0
                        current_uid = st.session_state.get("user_id", "demo_user")
                        for txn in parsed_txns:
                            try:
                                expense_mgr.add_expense(
                                    amount=txn["amount"],
                                    merchant=txn["merchant"],
                                    category=txn["category"],
                                    date_val=txn["date"],
                                    payment_method=txn["payment_method"],
                                    description=txn["description"],
                                    notes=txn["notes"],
                                    is_debit=txn.get("is_debit", True),
                                    user_id=current_uid,
                                )
                                imported += 1
                            except Exception:
                                skipped += 1

                        st.session_state["tx_page"] = 1
                        month_names_inv = {
                            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
                        }
                        from collections import Counter
                        period_counts = Counter([f"{month_names_inv[t['date'].month]} {t['date'].year}" for t in parsed_txns])
                        dominant_period = period_counts.most_common(1)[0][0] if period_counts else "Sep 2026"
                        st.session_state["selected_period"] = dominant_period
                        st.session_state["toast_message"] = (
                            f"PDF import complete — {imported} transactions recorded to Ledger ({dominant_period}), {skipped} skipped."
                        )
                        st.rerun()
                with imp_col2:
                    if st.button("✕ Cancel", use_container_width=True, key="tx_pdf_cancel_btn"):
                        st.rerun()

