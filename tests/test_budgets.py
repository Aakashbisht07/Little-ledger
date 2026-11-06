"""
Test Budget Management and Category Envelopes
"""

import pytest
from budget_manager import BudgetManager


def test_budget_setting_and_retrieval():
    mgr = BudgetManager()
    user = "pytest_budget_user"

    # Set overall monthly ceiling
    mgr.set_budget(2024, 9, "Total", 68000.0, user_id=user)
    retrieved = mgr.get_monthly_budget(2024, 9, user_id=user)
    assert retrieved == 68000.0

    # Set category envelopes
    mgr.set_budget(2024, 9, "Food & Dining", 18500.0, user_id=user)
    mgr.set_budget(2024, 9, "Shopping & Home", 8500.0, user_id=user)

    cats = mgr.get_category_budgets(2024, 9, user_id=user)
    assert cats["Food & Dining"] == 18500.0
    assert cats["Shopping & Home"] == 8500.0

    # Update existing budget
    mgr.set_budget(2024, 9, "Food & Dining", 19000.0, user_id=user)
    cats_updated = mgr.get_category_budgets(2024, 9, user_id=user)
    assert cats_updated["Food & Dining"] == 19000.0


def test_budget_defaults_fallback():
    mgr = BudgetManager()
    user = "pytest_fallback_user"
    envelopes = mgr.get_all_envelopes_with_defaults(2024, 9, user_id=user)
    assert "Food & Dining" in envelopes
    assert envelopes["Food & Dining"] > 0
    assert "Housing & Utilities" in envelopes
    assert envelopes["Housing & Utilities"] > 0
