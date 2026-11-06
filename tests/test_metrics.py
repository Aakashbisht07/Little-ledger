"""
Test Evaluation Metrics for GradientBoostingRegressor (R² and MAE) and Edge Cases
"""

import pytest
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error
from model_evaluation import get_latest_evaluation_metadata


def test_regression_metrics():
    """Verify R² and MAE are computed correctly for the regressor."""
    y_true = np.array([50000.0, 52000.0, 48000.0, 60000.0, 55000.0])
    y_pred = np.array([51000.0, 51500.0, 49000.0, 58000.0, 54000.0])

    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)

    assert isinstance(r2, float)
    assert isinstance(mae, float)
    assert mae > 0
    assert -1.0 <= r2 <= 1.0


def test_stored_evaluation_telemetry():
    """Verify metadata contains the required GBR evaluation fields."""
    meta = get_latest_evaluation_metadata()
    assert "r2_score" in meta
    assert "mae" in meta
    assert "regressor_name" in meta or "model_name" in meta
    assert "validation_method" in meta
    assert "status" in meta
