"""
Test Spending Predictions and Scenario Simulator
"""

import pytest
from predict import SpendingPredictor


def test_spending_predictor_pipeline():
    predictor = SpendingPredictor()
    forecast = predictor.predict_next_month("rahulkala013")

    assert forecast["status"] == "success"
    assert "projected_total" in forecast
    assert forecast["projected_total"] > 0
    assert "lower_bound" in forecast
    assert "upper_bound" in forecast
    assert forecast["lower_bound"] <= forecast["projected_total"] <= forecast["upper_bound"]
    assert "category_projections" in forecast
    assert len(forecast["category_projections"]) > 0


def test_scenario_simulation():
    predictor = SpendingPredictor()
    base_forecast = {
        "status": "success",
        "projected_total": 50000.0,
        "budget_ceiling": 65000.0,
        "category_projections": {
            "Food & Dining": 15000.0,
            "Shopping & Home": 9000.0,
        },
    }

    # Test reducing dining by 20%
    sim = predictor.simulate_scenario(
        baseline_forecast=base_forecast,
        dining_pct=-20.0,
        travel_festive_pct=0.0,
        custom_budget_ceiling=65000.0,
    )
    assert sim["status"] == "success"
    assert sim["net_variance"] == -3000.0
    assert sim["adjusted_total"] == 47000.0
    assert sim["ceiling_buffer"] == 18000.0
    assert sim["is_overrun"] is False

    # Test increasing dining and shopping to cause overrun
    sim_overrun = predictor.simulate_scenario(
        baseline_forecast=base_forecast,
        dining_pct=50.0,
        travel_festive_pct=60.0,
        custom_budget_ceiling=55000.0,
    )
    assert sim_overrun["is_overrun"] is True
    assert sim_overrun["ceiling_buffer"] < 0
