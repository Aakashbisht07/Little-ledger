"""
Little Ledger - PDF Bank Statement Parser
Specialized for:
  - Slice 5-column tabular bank statements (DATE | DETAILS | REF NO. | AMOUNT | BALANCE)
  - Slice block-style credit card statements
  - Traditional Indian bank statements with tables (HDFC, SBI, ICICI, Axis, Kotak, etc.)
  - Encrypted / password-protected statements
  - Fallback generic line-by-line extractor
"""

import re
import io
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("little_ledger.pdf_parser")

# ──────────────────────────────────────────────
# NORMALIZATION UTILITIES
# ──────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    """Normalize unicode characters, smart punctuation, and whitespace."""
    if not text:
        return ""
    text = re.sub(r"[’‘`´ʼ′']", "'", text)
    text = re.sub(r'[""„“”«»]', '"', text)
    text = re.sub(r"[–—−]", "-", text)
    text = re.sub(r"[•·●▪■*|]", "•", text)
    text = re.sub(r"[\u00a0\u1680\u2000-\u200b\u202f\u205f\u3000\ufeff]", " ", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(lines)


# ──────────────────────────────────────────────
# DATE FORMATS & REGEX
# ──────────────────────────────────────────────

_DATE_FORMATS = [
    "%d %b '%y", "%d %b %Y", "%d %b %y",
    "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y",
    "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d",
    "%d %b '%Y", "%b %d, %Y", "%d %B %Y",
    "%d-%B-%Y", "%d %B '%y", "%d.%m.%Y",
]

_DATE_RE = re.compile(
    r"\b("
    r"\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}"
    r"|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}"
    r"|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?:'?\d{2,4})?"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s*(?:'?\d{2,4})?"
    r"|\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*-(?:\d{2,4})"
    r")\b",
    re.I
)

_SLICE_ROW_DATE_RE = re.compile(r"^(\d{1,2}\s+[A-Za-z]{3}\s*(?:'|’)?\d{2})\b")

_SLICE_HEADER_SKIP_RE = re.compile(
    r"^(slice|\d{1,2}\s+[A-Za-z]{3}\s*(?:'|’)?\d{2}\s*-\s*\d{1,2}\s+[A-Za-z]{3}\s*(?:'|’)?\d{2}|\d+/\d+|DATE\s+DETAILS|Customer ID|Phone|Email|Account|IFSC|MICR|Nominee|Branch|Opening|Closing|Total credits|Total debits|Interest earned)",
    re.I
)

_CURRENCY_AMT_RE = re.compile(
    r"(-?[₹\u20b9]?\s*[\d,]+(?:\.\d+)?)",
    re.I
)


def _parse_date(raw: str) -> Optional[datetime]:
    """Parse date from string with robust fallback handling."""
    if not raw:
        return None
    cleaned = raw.strip()
    cleaned = re.sub(r"[’‘`´ʼ′']", "'", cleaned)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            pass
    # Try replacing 'yy with 20yy
    raw2 = re.sub(r"'\s*(\d{2})$", r"20\1", cleaned)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw2, fmt)
        except ValueError:
            pass
    try:
        dt = datetime.strptime(f"{cleaned} {datetime.now().year}", "%d %b %Y")
        return dt
    except ValueError:
        pass
    return None


def _clean_amount(raw: str) -> Optional[float]:
    """Strip currency symbols, commas, whitespace and return float."""
    if not raw:
        return None
    try:
        cleaned = re.sub(r"[^\d.]", "", str(raw))
        val = float(cleaned)
        return val if val > 0 else None
    except (ValueError, TypeError):
        return None


# ──────────────────────────────────────────────
# CATEGORY INFERENCE (matches config.CATEGORIES)
# ──────────────────────────────────────────────

_CATEGORY_RULES = [
    (re.compile(r"swiggy|zomato|food|cafe|coffee|restaurant|dining|pizza|biryani|burger|kfc|mcdonalds|subway|dominos|barbeque|starbucks|chaayos|chai point|blue tokai|third wave|eatclub|blinkit|zepto|instamart|bakery|bake|sweets|fruit", re.I), "Food & Dining"),
    (re.compile(r"uber|ola|rapido|metro|irctc|railway|redbus|bus|petrol|fuel|bpcl|indian oil|hp gas|parking|toll|fastag|namma metro|ola electric|yulu|bounce|flight|indigo|air india|akasa", re.I), "Transport & Mobility"),
    (re.compile(r"amazon|flipkart|myntra|ajio|nykaa|shopping|mall|mart|retail|dmart|big bazaar|reliance|jiomart|snapdeal|meesho|lenskart|pepperfry|ikea|fabindia|westside|max fashion|zara|h&m|decathlon|croma|vijay sales|vishal mega mart", re.I), "Shopping & Home"),
    (re.compile(r"rent|maintenance|society|electricity|bescom|tneb|water|gas|broadband|jio|airtel|vi\b|bsnl|wifi|internet|tata sky|dish tv|act fibernet|nobroker|mygate", re.I), "Housing & Utilities"),
    (re.compile(r"apollo|medplus|pharma|medical|doctor|hospital|clinic|health|labs|diagnostic|wellness|gym|yoga|fitness|cult\.fit|cure\.fit|1mg|netmeds|practo|pharmacy", re.I), "Health & Wellness"),
    (re.compile(r"netflix|spotify|prime|hotstar|zee5|sonyliv|jiocinema|movie|cinema|pvr|inox|theatre|concert|bookmyshow|paytm insider|event|gaming|steam|playstation|youtube", re.I), "Entertainment & Culture"),
    (re.compile(r"udemy|coursera|skillshare|book|stationery|school|college|tuition|exam|education|learning|byju|unacademy|vedantu|chegg|kindle", re.I), "Books & Learning"),
]


def _infer_category(text: str) -> str:
    for pattern, category in _CATEGORY_RULES:
        if pattern.search(text or ""):
            return category
    return "Discretionary Reserve"


def _infer_payment_method(text: str) -> str:
    t = (text or "").upper()
    if "UPI" in t or "BHIM" in t or "GPAY" in t or "PHONEPE" in t or "PAYTM" in t:
        return "UPI"
    if "NEFT" in t or "RTGS" in t or "IMPS" in t or "NETBANKING" in t or "NET BANKING" in t or "ACCOUNT TRANSFER" in t:
        return "NetBanking"
    if "CREDIT CARD" in t or "CREDIT" in t or "CARD" in t or "CRED" in t:
        return "Credit Card"
    if "DEBIT CARD" in t or "DEBIT" in t or "POS" in t or "ATM" in t:
        return "Debit Card"
    if "AUTO-DEBIT" in t or "AUTO DEBIT" in t or "ACH" in t or "NACH" in t or "MANDATE" in t:
        return "Auto-Debit"
    return "UPI"


def _clean_slice_merchant(details: str) -> str:
    """Extract human-readable merchant/payee name from Slice narration string."""
    details = re.sub(r"\s+", " ", details).strip()

    # Pattern: UPI-Debit-<rrn>-<Merchant Name>-<bank/vpa/etc>
    m = re.match(r"^UPI-(?:Debit|Credit|Refund)-\d+-([^-]+)", details, re.I)
    if m:
        name = m.group(1).strip()
        # Clean up hyphen artifacts
        name = re.sub(r"\s*-\s*$", "", name)
        if len(name) >= 2:
            return name

    # Pattern: NEFT/IMPS Credit/Debit-<Name>-
    m = re.match(r"^(?:NEFT|RTGS|IMPS)\s*(?:Credit|Debit)-([^-]+)", details, re.I)
    if m:
        return m.group(1).strip()

    # Account Transfer
    if "Account Transfer" in details:
        return "Account Transfer"

    # Interest Credit
    if "Interest Cr" in details or "Interest" in details:
        return "Bank Interest"

    # Strip out long numeric codes
    cleaned = re.sub(r"\b\d{8,}\b", "", details)
    cleaned = re.sub(r"[•\-–|/]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:60] if cleaned else "Slice Transaction"


# ──────────────────────────────────────────────
# SLICE 5-COLUMN TABULAR STATEMENT PARSER
# (DATE | DETAILS | REF NO. | AMOUNT | BALANCE)
# ──────────────────────────────────────────────

def _parse_slice_table_statement(text: str) -> List[Dict[str, Any]]:
    """
    Parses Slice bank account statements with 5-column layout:
        DATE | DETAILS | REF NO. | AMOUNT | BALANCE
    Handles wrapped/multiline details cleanly across all pages.
    """
    norm = _normalize_text(text)
    lines = [l.strip() for l in norm.splitlines() if l.strip()]

    # Filter out page headers, summaries, and footers
    filtered_lines = [l for l in lines if not _SLICE_HEADER_SKIP_RE.match(l)]

    # Group each transaction: begins with a line starting with a date
    txns_raw = []
    curr_main = None
    curr_extra = []

    for l in filtered_lines:
        if _SLICE_ROW_DATE_RE.match(l):
            if curr_main:
                txns_raw.append((curr_main, " ".join(curr_extra)))
            curr_main = l
            curr_extra = []
        else:
            if curr_main:
                curr_extra.append(l)

    if curr_main:
        txns_raw.append((curr_main, " ".join(curr_extra)))

    transactions = []
    for main_line, extra_text in txns_raw:
        dm = _SLICE_ROW_DATE_RE.match(main_line)
        if not dm:
            continue
        raw_date_str = dm.group(1)
        tx_date = _parse_date(raw_date_str)
        if not tx_date:
            continue

        # Combine main line rest + extra continuation text
        rest = main_line[dm.end():].strip()
        full_line = f"{rest} {extra_text}".strip() if extra_text else rest

        # ── Parse from the RIGHT end of the full line ──
        # Structure: <DETAILS> <REF_NO (10-20 digits)> <AMOUNT> <BALANCE>
        # Both AMOUNT and BALANCE are at the end; REF_NO is a long pure-digit sequence

        # Extract all numeric tokens (handles -, rupee symbol, commas, decimals)
        num_re = re.compile(r"(-?₹?\s*[\d,]+(?:\.\d+)?)")
        all_nums = list(num_re.finditer(full_line))

        # Need at least 2 numbers: amount + balance
        if len(all_nums) < 2:
            continue

        # Work from right: find balance (last), then amount (second-to-last)
        # Skip any pure-digit sequences longer than 10 digits (those are ref/ID numbers)
        candidate_nums = []
        for m in reversed(all_nums):
            raw_digits = re.sub(r"[^\d]", "", m.group(1))
            # A valid monetary amount: has a decimal, OR has rupee symbol, OR is short (<= 10 digits)
            if "." in m.group(1) or "₹" in m.group(1) or "-₹" in m.group(1) or len(raw_digits) <= 10:
                candidate_nums.append(m)
            if len(candidate_nums) == 2:
                break

        if len(candidate_nums) < 2:
            # Fallback: try accepting up to 12 digit amounts (for large transactions)
            candidate_nums = []
            for m in reversed(all_nums):
                raw_digits = re.sub(r"[^\d]", "", m.group(1))
                if len(raw_digits) <= 12:
                    candidate_nums.append(m)
                if len(candidate_nums) == 2:
                    break
            if len(candidate_nums) < 2:
                continue

        # candidate_nums[0] = BALANCE, candidate_nums[1] = AMOUNT
        balance_match = candidate_nums[0]
        amount_match = candidate_nums[1]
        amount_str = amount_match.group(1).strip()

        # Everything before the amount is: <DETAILS> <REF_NO>
        prefix = full_line[:amount_match.start()].strip()

        # Ref No: trailing long pure-digit sequence before the amount
        ref_m = re.search(r"(\d{10,20})\s*$", prefix)
        if ref_m:
            ref_no = ref_m.group(1)
            details_str = prefix[:ref_m.start()].strip()
        else:
            ref_no = ""
            details_str = prefix

        # ── Debit/Credit detection from narration text ──
        d_upper = (details_str + " " + extra_text).upper()
        is_debit = True  # default: treat as expense/debit
        if re.search(r"UPI-CREDIT|UPI-REFUND|NEFT CREDIT|IMPS CREDIT|RTGS CREDIT|INTEREST CR|INTEREST CREDIT", d_upper):
            is_debit = False
        if re.search(r"UPI-DEBIT|NEFT DEBIT|IMPS DEBIT|ACCOUNT TRANSFER-DEBIT", d_upper):
            is_debit = True
        # Also respect sign on the amount itself
        if amount_str.lstrip().startswith("-") or "-₹" in amount_str:
            is_debit = True

        # Parse amount value (strip all non-numeric except decimal)
        amt_clean = re.sub(r"[^\d.]", "", amount_str)
        if not amt_clean:
            continue
        try:
            amt_val = float(amt_clean)
        except ValueError:
            continue
        if amt_val <= 0:
            continue

        merchant = _clean_slice_merchant(details_str)
        payment_method = _infer_payment_method(details_str)
        category = _infer_category(f"{merchant} {details_str}")

        tx_type_str = "Debit (Spend)" if is_debit else "Credit / Refund"
        notes_str = f"Slice | Ref: {ref_no} | {tx_type_str}" if ref_no else f"Slice | {tx_type_str}"

        transactions.append({
            "date": tx_date,
            "merchant": merchant[:80],
            "amount": round(amt_val, 2),
            "category": category,
            "payment_method": payment_method,
            "description": details_str[:200],
            "notes": notes_str,
            "is_debit": is_debit,
            "ref_no": ref_no,
        })

    return transactions

# ──────────────────────────────────────────────
# TABLE-BASED PARSER (traditional Indian banks)
# ──────────────────────────────────────────────

def _extract_from_tables(pages) -> List[Dict[str, Any]]:
    transactions = []
    for page in pages:
        try:
            tables = page.extract_tables()
        except Exception:
            continue
        for table in tables:
            if not table or len(table) < 2:
                continue
            header = [str(h or "").lower().strip() for h in table[0]]
            joined = " ".join(header)
            if not any(k in joined for k in ["date", "amount", "debit", "dr", "narration", "description", "particulars"]):
                continue
            col = {}
            for i, h in enumerate(header):
                if "date" in h and "value" not in h and "date" not in col:
                    col["date"] = i
                if any(k in h for k in ["narration", "description", "particulars", "remarks", "transaction details"]):
                    col.setdefault("desc", i)
                if any(k in h for k in ["debit", "withdrawal", "dr", "withdrawl"]):
                    col.setdefault("debit", i)
                if any(k in h for k in ["credit", "deposit", "cr"]):
                    col.setdefault("credit", i)
                if h in ["amount"] and "debit" not in col:
                    col.setdefault("debit", i)
            if "date" not in col:
                continue
            for row in table[1:]:
                if not row or all(c is None or str(c).strip() == "" for c in row):
                    continue
                try:
                    raw_date = str(row[col["date"]] or "").strip()
                    tx_date = _parse_date(raw_date)
                    if not tx_date:
                        continue
                    desc = str(row[col.get("desc", 0)] or "").strip() if "desc" in col else ""
                    amount = None
                    is_credit = False
                    if "debit" in col:
                        raw_amt = str(row[col["debit"]] or "").strip()
                        if raw_amt and raw_amt not in ("-", "", "0", "0.00"):
                            amount = _clean_amount(raw_amt)
                    if amount is None and "credit" in col:
                        raw_amt = str(row[col["credit"]] or "").strip()
                        if raw_amt and raw_amt not in ("-", "", "0", "0.00"):
                            amount = _clean_amount(raw_amt)
                            is_credit = True
                    if not amount or amount <= 0:
                        continue
                    merchant = _clean_slice_merchant(desc) if desc else "Disbursement"
                    transactions.append({
                        "date": tx_date,
                        "merchant": merchant[:80],
                        "amount": round(amount, 2),
                        "category": _infer_category(desc),
                        "payment_method": _infer_payment_method(desc),
                        "description": desc,
                        "notes": "Imported from PDF statement",
                        "is_debit": not is_credit,
                        "ref_no": "",
                    })
                except Exception as e:
                    logger.debug(f"Table row error: {e}")
    return transactions


# ──────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────

def parse_bank_statement_pdf(
    pdf_bytes: bytes,
    password: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], str, Optional[str]]:
    """
    Parse a bank statement PDF and return (transactions, method_used, error_message).
    Supports: Slice 5-column statements, HDFC, SBI, ICICI, Axis, Kotak, YES, etc.
    """
    transactions = []
    method = "none"
    error_msg = None

    # Step 1: Check password protection via PyMuPDF
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc.needs_pass or doc.is_encrypted:
            if not password:
                return [], "locked", "🔒 This PDF statement is encrypted. Please enter the password above to unlock it."
            auth_ok = doc.authenticate(password)
            if not auth_ok:
                return [], "locked", "❌ Incorrect PDF password. Please verify and try again."
        doc.close()
    except Exception as e:
        logger.debug(f"PyMuPDF encryption check: {e}")

    # Step 2: Attempt extraction using PyMuPDF (fitz) - high-fidelity text extraction
    mupdf_text = ""
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc.needs_pass and password:
            doc.authenticate(password)
        mupdf_text = "\n".join(page.get_text() for page in doc)
        doc.close()

        if mupdf_text:
            # 1. Try Slice 5-column table parser
            slice_txns = _parse_slice_table_statement(mupdf_text)
            if len(slice_txns) >= 1:
                transactions = slice_txns
                method = "slice_table"
    except Exception as e:
        logger.warning(f"PyMuPDF extraction error: {e}")

    # Step 3: If PyMuPDF found nothing, try pdfplumber
    if not transactions:
        try:
            import pdfplumber
            open_kwargs = {"password": password} if password else {}
            with pdfplumber.open(io.BytesIO(pdf_bytes), **open_kwargs) as pdf:
                pdfplumber_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

                # Try Slice table on pdfplumber text
                slice_txns = _parse_slice_table_statement(pdfplumber_text)
                if len(slice_txns) >= 1:
                    transactions = slice_txns
                    method = "slice_table_pdfplumber"

                if not transactions:
                    # Try traditional grid tables
                    table_txns = _extract_from_tables(pdf.pages)
                    if len(table_txns) >= 1:
                        transactions = table_txns
                        method = "table"
        except Exception as e:
            logger.warning(f"pdfplumber extraction error: {e}")

    # Step 4: Deduplicate by (date, amount, merchant, ref_no)
    seen = set()
    unique = []
    for t in transactions:
        ref = t.get("ref_no") or ""
        key = (t["date"].strftime("%Y-%m-%d"), t["amount"], t["merchant"][:30].lower(), ref)
        if key not in seen:
            seen.add(key)
            unique.append(t)

    # Sort by date descending
    unique.sort(key=lambda x: x["date"], reverse=True)
    return unique, method, error_msg
