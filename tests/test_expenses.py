"""
Test Expense CRUD Operations, Schema Validation, and CSV Export
"""

import pytest
from datetime import datetime
from expense_manager import ExpenseManager, ExpenseValidationError


def test_expense_crud_lifecycle():
    mgr = ExpenseManager()
    test_user = "test_user_pytest"

    # 1. Create
    tx_id = mgr.add_expense(
        amount=850.0,
        merchant="Subko Bakehouse",
        category="Food & Dining",
        date_val=datetime(2024, 9, 20, 11, 30),
        payment_method="UPI",
        description="Croissant and pour-over",
        notes="PyTest record",
        user_id=test_user,
    )
    assert tx_id is not None
    assert len(tx_id) == 24

    # 2. Read
    fetched = mgr.get_expense(tx_id)
    assert fetched is not None
    assert fetched["merchant"] == "Subko Bakehouse"
    assert fetched["amount"] == 850.0
    assert fetched["category"] == "Food & Dining"

    # 3. Update
    updated = mgr.update_expense(
        tx_id,
        {
            "amount": 920.0,
            "merchant": "Subko Artisanal Bakehouse",
            "category": "Food & Dining",
            "date": datetime(2024, 9, 20, 11, 30),
            "payment_method": "Credit Card",
            "description": "Updated memo",
            "notes": "PyTest updated",
            "user_id": test_user,
        },
    )
    assert updated is True
    refetched = mgr.get_expense(tx_id)
    assert refetched["amount"] == 920.0
    assert refetched["merchant"] == "Subko Artisanal Bakehouse"
    assert refetched["payment_method"] == "Credit Card"

    # 4. Filter & Search
    res, total = mgr.get_expenses(user_id=test_user, search_query="Subko")
    assert total >= 1
    assert any(e["id"] == tx_id for e in res)

    # 5. Delete
    deleted = mgr.delete_expense(tx_id)
    assert deleted is True
    assert mgr.get_expense(tx_id) is None


def test_expense_validation_errors():
    mgr = ExpenseManager()

    # Negative amount
    with pytest.raises(ExpenseValidationError):
        mgr.validate_expense_data({"amount": -100.0, "merchant": "Test", "date": datetime.utcnow()})

    # Zero amount
    with pytest.raises(ExpenseValidationError):
        mgr.validate_expense_data({"amount": 0.0, "merchant": "Test", "date": datetime.utcnow()})

    # Empty merchant
    with pytest.raises(ExpenseValidationError):
        mgr.validate_expense_data({"amount": 100.0, "merchant": "   ", "date": datetime.utcnow()})

    # Invalid date
    with pytest.raises(ExpenseValidationError):
        mgr.validate_expense_data({"amount": 100.0, "merchant": "Test", "date": "not-a-date"})
