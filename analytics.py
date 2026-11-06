"""
Little Ledger - Financial Analytics Engine
Pure, audited financial calculations computed dynamically from MongoDB records.
"""

import calendar
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from config import CATEGORY_META, CATEGORIES


def get_month_date_range(year: int, month: int) -> Tuple[datetime, datetime]:
    """Return timezone-naive UTC start and end datetimes for a given year and month."""
    _, last_day = calendar.monthrange(year, month)
    start_dt = datetime(year, month, 1, 0, 0, 0)
    end_dt = datetime(year, month, last_day, 23, 59, 59)
    return start_dt, end_dt


def _only_debits(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter records strictly to genuine debits/outlays, excluding incoming deposits and credits."""
    return [e for e in expenses if e.get("is_debit", True) is not False]


def compute_monthly_metrics(
    expenses: List[Dict[str, Any]],
    year: int,
    month: int,
    monthly_budget: float = 65000.0,
    previous_month_expenses: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Computes key executive metrics for the Overview and Budgets screens.
    Returns:
        - total_spent
        - count_transactions
        - previous_spent
        - mom_change_abs
        - mom_change_pct
        - remaining_budget
        - budget_utilization_pct
        - largest_category_name
        - largest_category_amount
        - largest_category_pct
        - daily_average
        - safe_daily_runway
        - single_day_peak (date, amount, merchant)
        - days_in_month
        - days_elapsed
    """
    _, last_day = calendar.monthrange(year, month)
    now = datetime.utcnow()

    # If looking at current month in calendar, compute days elapsed; else full month
    if now.year == year and now.month == month:
        days_elapsed = min(now.day, last_day)
        days_remaining = max(1, last_day - days_elapsed)
    else:
        days_elapsed = last_day
        days_remaining = 0

    if not expenses:
        return {
            "total_spent": 0.0,
            "count_transactions": 0,
            "previous_spent": 0.0,
            "mom_change_abs": 0.0,
            "mom_change_pct": 0.0,
            "remaining_budget": monthly_budget,
            "budget_utilization_pct": 0.0,
            "largest_category_name": "None",
            "largest_category_amount": 0.0,
            "largest_category_pct": 0.0,
            "daily_average": 0.0,
            "safe_daily_runway": round(monthly_budget / max(1, last_day), 2),
            "single_day_peak": {"date": None, "amount": 0.0, "merchant": "None"},
            "days_in_month": last_day,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
        }

    debit_txns = _only_debits(expenses)
    credit_txns = [e for e in expenses if e.get("is_debit", True) is False]

    total_spent = sum(float(e.get("amount", 0.0)) for e in debit_txns)
    total_credited = sum(float(e.get("amount", 0.0)) for e in credit_txns)
    count_transactions = len(debit_txns)

    # Previous month spend
    previous_spent = 0.0
    if previous_month_expenses:
        previous_spent = sum(float(e.get("amount", 0.0)) for e in _only_debits(previous_month_expenses))

    mom_change_abs = total_spent - previous_spent
    if previous_spent > 0:
        mom_change_pct = (mom_change_abs / previous_spent) * 100.0
    else:
        mom_change_pct = 0.0

    remaining_budget = monthly_budget - total_spent
    budget_utilization_pct = (total_spent / monthly_budget * 100.0) if monthly_budget > 0 else 0.0

    # Category breakdown for largest category
    cat_totals: Dict[str, float] = {}
    for e in debit_txns:
        cat = e.get("category", "Other")
        cat_totals[cat] = cat_totals.get(cat, 0.0) + float(e.get("amount", 0.0))

    if cat_totals:
        largest_cat = max(cat_totals.items(), key=lambda x: x[1])
        largest_category_name = largest_cat[0]
        largest_category_amount = largest_cat[1]
        largest_category_pct = (largest_category_amount / total_spent * 100.0) if total_spent > 0 else 0.0
    else:
        largest_category_name = "None"
        largest_category_amount = 0.0
        largest_category_pct = 0.0

    # Daily average
    daily_average = total_spent / max(1, days_elapsed)

    # Safe daily runway for remaining days
    effective_days_left = days_remaining if days_remaining > 0 else 1
    safe_daily_runway = max(0.0, remaining_budget / effective_days_left)

    # Single day peak
    day_spend: Dict[str, Dict[str, Any]] = {}
    for e in debit_txns:
        d = e.get("date")
        if isinstance(d, datetime):
            d_str = d.strftime("%Y-%m-%d")
        elif isinstance(d, str):
            d_str = d[:10]
        else:
            d_str = "Unknown"

        amt = float(e.get("amount", 0.0))
        if d_str not in day_spend:
            day_spend[d_str] = {"amount": 0.0, "top_merchant": e.get("merchant", ""), "top_memo": e.get("description", "")}
        day_spend[d_str]["amount"] += amt
        if amt > day_spend[d_str]["amount"] - amt:
            day_spend[d_str]["top_merchant"] = e.get("merchant", "")
            day_spend[d_str]["top_memo"] = e.get("description", "")

    if day_spend:
        peak_date, peak_info = max(day_spend.items(), key=lambda x: x[1]["amount"])
        single_day_peak = {
            "date": peak_date,
            "amount": peak_info["amount"],
            "merchant": peak_info["top_merchant"],
            "memo": peak_info.get("top_memo", ""),
        }
    else:
        single_day_peak = {"date": None, "amount": 0.0, "merchant": "None", "memo": ""}

    return {
        "total_spent": round(total_spent, 2),
        "count_transactions": count_transactions,
        "previous_spent": round(previous_spent, 2),
        "mom_change_abs": round(mom_change_abs, 2),
        "mom_change_pct": round(mom_change_pct, 1),
        "remaining_budget": round(remaining_budget, 2),
        "budget_utilization_pct": round(budget_utilization_pct, 1),
        "largest_category_name": largest_category_name,
        "largest_category_amount": round(largest_category_amount, 2),
        "largest_category_pct": round(largest_category_pct, 1),
        "daily_average": round(daily_average, 2),
        "safe_daily_runway": round(safe_daily_runway, 2),
        "single_day_peak": single_day_peak,
        "days_in_month": last_day,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
    }


def compute_daily_spending_series(
    expenses: List[Dict[str, Any]], year: int, month: int, monthly_budget: float = 65000.0
) -> pd.DataFrame:
    """
    Generate daily spending and cumulative trajectory for charts.
    Includes daily spend, cumulative spend, and ideal linear budget trajectory.
    """
    _, last_day = calendar.monthrange(year, month)
    days = list(range(1, last_day + 1))
    df = pd.DataFrame({"day": days, "daily_spent": 0.0})
    df.set_index("day", inplace=True)

    for e in _only_debits(expenses):
        d = e.get("date")
        if isinstance(d, datetime):
            day_num = d.day
        elif isinstance(d, str):
            try:
                day_num = int(d[8:10])
            except Exception:
                continue
        else:
            continue
        if 1 <= day_num <= last_day:
            df.loc[day_num, "daily_spent"] += float(e.get("amount", 0.0))

    df.reset_index(inplace=True)
    df["cumulative_spent"] = df["daily_spent"].cumsum()
    df["budget_ceiling_runway"] = (df["day"] / last_day) * monthly_budget
    return df


def compute_category_envelopes(
    expenses: List[Dict[str, Any]], envelope_budgets: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Compute spending against each category envelope.
    Returns list of envelope status dictionaries for Page 2 and Page 7.
    """
    cat_spent: Dict[str, float] = {}
    for e in _only_debits(expenses):
        cat = e.get("category", "Other")
        cat_spent[cat] = cat_spent.get(cat, 0.0) + float(e.get("amount", 0.0))

    all_categories = sorted(list(set(list(envelope_budgets.keys()) + list(cat_spent.keys()))))
    envelopes = []

    for cat in all_categories:
        spent = cat_spent.get(cat, 0.0)
        budget = envelope_budgets.get(cat, 0.0)
        remaining = budget - spent
        pct = (spent / budget * 100.0) if budget > 0 else (100.0 if spent > 0 else 0.0)

        # Status badge definition
        if budget == 0.0:
            status = "NO BUDGET"
            badge_class = "ll-badge-neutral"
        elif pct >= 100.0:
            status = "LIMIT EXCEEDED"
            badge_class = "ll-badge-red"
        elif pct >= 85.0:
            status = "APPROACHING LIMIT"
            badge_class = "ll-badge-amber"
        elif pct >= 60.0:
            status = "STABLE"
            badge_class = "ll-badge-green"
        elif pct > 0:
            status = "ON TRACK"
            badge_class = "ll-badge-green"
        else:
            status = "UNTOUCHED"
            badge_class = "ll-badge-neutral"

        meta = CATEGORY_META.get(cat, {"color": "#657B68", "icon": "💳", "nature": "Discretionary"})

        envelopes.append({
            "category": cat,
            "spent": round(spent, 2),
            "budget": round(budget, 2),
            "remaining": round(remaining, 2),
            "utilization_pct": round(pct, 1),
            "status": status,
            "badge_class": badge_class,
            "icon": meta.get("icon", "💳"),
            "color": meta.get("color", "#657B68"),
            "nature": meta.get("nature", "Discretionary"),
        })

    return envelopes


def compute_weekday_weekend_cadence(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes weekday vs weekend spending patterns (Page 4 Insights).
    """
    if not expenses:
        return {
            "weekday_mean": 0.0,
            "weekend_mean": 0.0,
            "weekend_pct_diff": 0.0,
            "weekday_total": 0.0,
            "weekend_total": 0.0,
            "day_of_week_distribution": {i: 0.0 for i in range(7)},
        }

    weekday_amounts = []
    weekend_amounts = []
    dow_totals: Dict[int, float] = {i: 0.0 for i in range(7)}  # 0=Mon, 6=Sun

    # Group by date first to compute per-day averages accurately
    daily_groups: Dict[str, Tuple[int, float]] = {}
    for e in _only_debits(expenses):
        d = e.get("date")
        if isinstance(d, datetime):
            d_obj = d.date()
        elif isinstance(d, str):
            try:
                d_obj = datetime.fromisoformat(d[:10]).date()
            except Exception:
                continue
        else:
            continue

        amt = float(e.get("amount", 0.0))
        d_str = d_obj.isoformat()
        weekday_idx = d_obj.weekday()
        dow_totals[weekday_idx] += amt

        if d_str not in daily_groups:
            daily_groups[d_str] = (weekday_idx, 0.0)
        daily_groups[d_str] = (weekday_idx, daily_groups[d_str][1] + amt)

    for d_str, (dow, tot) in daily_groups.items():
        if dow < 5:  # Monday to Friday
            weekday_amounts.append(tot)
        else:        # Saturday & Sunday
            weekend_amounts.append(tot)

    weekday_mean = np.mean(weekday_amounts) if weekday_amounts else 0.0
    weekend_mean = np.mean(weekend_amounts) if weekend_amounts else 0.0

    if weekday_mean > 0:
        pct_diff = ((weekend_mean - weekday_mean) / weekday_mean) * 100.0
    else:
        pct_diff = 0.0

    return {
        "weekday_mean": round(float(weekday_mean), 2),
        "weekend_mean": round(float(weekend_mean), 2),
        "weekend_pct_diff": round(float(pct_diff), 1),
        "weekday_total": round(sum(weekday_amounts), 2),
        "weekend_total": round(sum(weekend_amounts), 2),
        "day_of_week_distribution": {k: round(v, 2) for k, v in dow_totals.items()},
    }


def compute_top_merchants(expenses: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """Rank merchants by aggregate spend and frequency."""
    merchants: Dict[str, Dict[str, Any]] = {}
    for e in _only_debits(expenses):
        m = e.get("merchant", "Unknown").strip()
        amt = float(e.get("amount", 0.0))
        cat = e.get("category", "General")
        if m not in merchants:
            merchants[m] = {"merchant": m, "total": 0.0, "count": 0, "category": cat}
        merchants[m]["total"] += amt
        merchants[m]["count"] += 1

    sorted_m = sorted(merchants.values(), key=lambda x: x["total"], reverse=True)
    return sorted_m[:top_n]


def compute_portfolio_allocation(
    expenses: List[Dict[str, Any]], monthly_budget: float = 65000.0
) -> Dict[str, Any]:
    """
    Calculate Needs vs Wants vs Buffer (50/30/20 or custom portfolio rule).
    Needs: Food & Dining (groceries/meals), Housing, Transport, Health
    Wants: Shopping, Entertainment, Books
    Buffer: Unspent monthly liquid reserve
    """
    debits = _only_debits(expenses)
    total_spent = sum(float(e.get("amount", 0.0)) for e in debits)
    needs_spend = 0.0
    wants_spend = 0.0

    for e in debits:
        cat = e.get("category", "Other")
        amt = float(e.get("amount", 0.0))
        nature = CATEGORY_META.get(cat, {}).get("nature", "Wants")
        if nature == "Needs":
            needs_spend += amt
        else:
            wants_spend += amt

    buffer_amount = max(0.0, monthly_budget - total_spent)
    base_denominator = max(monthly_budget, total_spent) if monthly_budget > 0 else total_spent

    needs_pct = (needs_spend / base_denominator * 100.0) if base_denominator > 0 else 0.0
    wants_pct = (wants_spend / base_denominator * 100.0) if base_denominator > 0 else 0.0
    buffer_pct = (buffer_amount / base_denominator * 100.0) if base_denominator > 0 else 0.0

    return {
        "needs_amount": round(needs_spend, 2),
        "needs_pct": round(needs_pct, 1),
        "wants_amount": round(wants_spend, 2),
        "wants_pct": round(wants_pct, 1),
        "buffer_amount": round(buffer_amount, 2),
        "buffer_pct": round(buffer_pct, 1),
    }


def compute_recurring_expenses(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect recurring payments or subscription patterns based on merchant repetition and amounts."""
    patterns: Dict[str, List[float]] = {}
    merch_cats: Dict[str, str] = {}
    for e in expenses:
        m = e.get("merchant", "").strip()
        amt = float(e.get("amount", 0.0))
        cat = e.get("category", "Utilities")
        if not m:
            continue
        if m not in patterns:
            patterns[m] = []
            merch_cats[m] = cat
        patterns[m].append(amt)

    recurring = []
    # Keywords typically indicating recurring bills
    recurring_keywords = ["bescom", "rent", "cult", "netflix", "spotify", "broadband", "airtel", "icici", "prime", "gym", "maintenance"]
    for m, amounts in patterns.items():
        is_keyword = any(k in m.lower() for k in recurring_keywords)
        # Low variance in payment amounts or repetition indicates subscription
        if (len(amounts) >= 2 or is_keyword) and len(amounts) > 0:
            avg_amt = np.mean(amounts)
            recurring.append({
                "merchant": m,
                "category": merch_cats.get(m, "Utilities"),
                "frequency": f"{len(amounts)} cycles logged",
                "average_amount": round(float(avg_amt), 2),
                "last_amount": round(float(amounts[-1]), 2),
            })

    recurring.sort(key=lambda x: x["average_amount"], reverse=True)
    return recurring[:6]
