"""
Little Ledger - Data Preprocessing & Feature Engineering Pipeline
Constructs time-aware monthly aggregates and features with strict zero-leakage temporal validation.
Uses GradientBoostingRegressor for monthly spending prediction.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger("little_ledger.preprocessing")

FEATURE_COLUMNS = [
    "month_idx",
    "month_of_year",
    "quarter",
    "lag_1_spend",
    "lag_2_spend",
    "lag_3_spend",
    "rolling_mean_3",
    "rolling_std_3",
    "monthly_budget",
]


def aggregate_monthly_expenses(
    expenses: List[Dict[str, Any]],
    budgets_map: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """
    Aggregate raw transactions into monthly summaries.
    Ensures continuous timeline and derives category subtotals.
    """
    if not expenses:
        return pd.DataFrame()

    records = []
    for e in expenses:
        # Skip credit transactions (income, transfers, refunds) - only predict outlays (debits)
        if e.get("is_debit", True) is False:
            continue

        d = e.get("date")
        if isinstance(d, datetime):
            dt = d
        elif isinstance(d, str):
            try:
                dt = datetime.fromisoformat(d.replace("Z", "+00:00")[:19])
            except Exception:
                continue
        else:
            continue

        records.append({
            "year": dt.year,
            "month": dt.month,
            "period": f"{dt.year:04d}-{dt.month:02d}",
            "amount": float(e.get("amount", 0.0)),
            "category": e.get("category", "Other"),
        })

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Group by year, month
    monthly_rows = []
    grouped = df.groupby(["year", "month"])

    # Determine date range to create continuous monthly index
    min_year, min_month = df["year"].min(), df[df["year"] == df["year"].min()]["month"].min()
    max_year, max_month = df["year"].max(), df[df["year"] == df["year"].max()]["month"].max()

    curr_y, curr_m = min_year, min_month
    month_idx = 1

    while (curr_y < max_year) or (curr_y == max_year and curr_m <= max_month):
        period_key = f"{curr_y:04d}-{curr_m:02d}"
        if (curr_y, curr_m) in grouped.groups:
            sub_df = grouped.get_group((curr_y, curr_m))
            total_spend = sub_df["amount"].sum()
            tx_count = len(sub_df)

            # Category breakdowns
            cat_sums = sub_df.groupby("category")["amount"].sum().to_dict()
            dining_spend = cat_sums.get("Food & Dining", 0.0)
            utilities_spend = cat_sums.get("Housing & Utilities", 0.0)
            shopping_spend = cat_sums.get("Shopping & Home", 0.0)
            mobility_spend = cat_sums.get("Transport & Mobility", 0.0)
        else:
            total_spend = 0.0
            tx_count = 0
            dining_spend = 0.0
            utilities_spend = 0.0
            shopping_spend = 0.0
            mobility_spend = 0.0

        budget_val = (budgets_map.get(period_key, 65000.0)) if budgets_map else 65000.0

        monthly_rows.append({
            "year": curr_y,
            "month": curr_m,
            "period": period_key,
            "month_idx": month_idx,
            "month_of_year": curr_m,
            "quarter": (curr_m - 1) // 3 + 1,
            "total_spend": round(total_spend, 2),
            "tx_count": tx_count,
            "dining_spend": round(dining_spend, 2),
            "utilities_spend": round(utilities_spend, 2),
            "shopping_spend": round(shopping_spend, 2),
            "mobility_spend": round(mobility_spend, 2),
            "monthly_budget": round(budget_val, 2),
        })

        month_idx += 1
        if curr_m == 12:
            curr_y += 1
            curr_m = 1
        else:
            curr_m += 1

    return pd.DataFrame(monthly_rows)


def build_ml_feature_matrix(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs temporal lag and rolling features.
    Strictly uses information available BEFORE the target month.
    """
    if len(monthly_df) < 4:
        # Need at least 4 months to compute lag 3
        return pd.DataFrame()

    df = monthly_df.sort_values(["year", "month"]).copy().reset_index(drop=True)

    # 1. Spending lags (fill initial missing lags with available prior values)
    df["lag_1_spend"] = df["total_spend"].shift(1)
    df["lag_2_spend"] = df["total_spend"].shift(2).fillna(df["lag_1_spend"])
    df["lag_3_spend"] = df["total_spend"].shift(3).fillna(df["lag_2_spend"])

    # 2. Rolling stats over past 3 months (using shift(1) to avoid target leakage)
    df["rolling_mean_3"] = df["total_spend"].shift(1).rolling(window=3, min_periods=1).mean()
    df["rolling_std_3"] = df["total_spend"].shift(1).rolling(window=3, min_periods=1).std().fillna(0.0)

    # 3. Category & transaction count lags
    df["tx_count_lag_1"] = df["tx_count"].shift(1)
    df["dining_spend_lag_1"] = df["dining_spend"].shift(1)
    df["utilities_spend_lag_1"] = df["utilities_spend"].shift(1)
    df["shopping_spend_lag_1"] = df["shopping_spend"].shift(1)
    df["mobility_spend_lag_1"] = df["mobility_spend"].shift(1)

    # Target: next month's total spending
    df["target_next_month_spend"] = df["total_spend"]

    # Drop rows with NaN caused by shifting (row 0 has no lag_1)
    feature_df = df.dropna().reset_index(drop=True)
    return feature_df


def chronological_train_test_split(
    df: pd.DataFrame, test_ratio: float = 0.25
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits dataset chronologically to avoid future lookahead bias.
    Earlier periods for training, latest periods for held-out evaluation.
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    n = len(df)
    test_size = max(1, int(n * test_ratio)) if n < 8 else max(2, int(n * test_ratio))
    train_size = n - test_size

    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()

    return train_df, test_df
