"""
Test Data Preprocessing and Feature Engineering Pipeline
"""

import pytest
from datetime import datetime
import pandas as pd
from preprocessing import (
    aggregate_monthly_expenses,
    build_ml_feature_matrix,
    chronological_train_test_split,
    FEATURE_COLUMNS,
)


def test_monthly_aggregation_and_features():
    # Construct synthetic transactions spanning 6 consecutive months
    records = []
    for mo in range(1, 7):
        records.append({
            "date": datetime(2024, mo, 10, 12, 0),
            "amount": 50000.0 + (mo * 1000.0),
            "category": "Food & Dining",
        })
        records.append({
            "date": datetime(2024, mo, 20, 15, 0),
            "amount": 10000.0,
            "category": "Housing & Utilities",
        })

    m_df = aggregate_monthly_expenses(records)
    assert len(m_df) == 6
    assert "total_spend" in m_df.columns
    assert "month_idx" in m_df.columns

    # Feature matrix
    feat_df = build_ml_feature_matrix(m_df)
    assert not feat_df.empty
    for col in FEATURE_COLUMNS:
        assert col in feat_df.columns

    # Verify lag alignment (lag_1 should match previous month's total_spend)
    assert feat_df["lag_1_spend"].iloc[0] == m_df["total_spend"].iloc[0]


def test_chronological_train_test_split():
    df = pd.DataFrame({
        "month_idx": range(1, 21),
        "total_spend": [50000.0] * 20,
    })
    train, test = chronological_train_test_split(df, test_ratio=0.25)
    assert len(train) == 15
    assert len(test) == 5
    # Strict temporal ordering: train max month < test min month
    assert train["month_idx"].max() < test["month_idx"].min()
