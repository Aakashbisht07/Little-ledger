"""
Little Ledger - Budget & Fiscal Envelope Management
Maintains overall monthly budget ceilings and granular category envelopes.
Falls back to sensible defaults when MongoDB is offline.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from database import get_db, serialize_doc
from config import DEFAULT_USER_ID, DEFAULT_CURRENCY, CATEGORIES

logger = logging.getLogger("little_ledger.budget_manager")

DEFAULT_TOTAL_BUDGET = 65000.0
DEFAULT_CATEGORY_BUDGETS = {
    "Food & Dining": 18000.0,
    "Housing & Utilities": 14000.0,
    "Shopping & Home": 8000.0,
    "Transport & Mobility": 7500.0,
    "Entertainment & Culture": 5000.0,
    "Health & Wellness": 4500.0,
    "Books & Learning": 3500.0,
    "Discretionary Reserve": 5000.0,
}


class BudgetManager:
    """Manages monthly and category budgets persisted in MongoDB, with offline fallback."""

    def __init__(self):
        self.db = get_db()
        if not self.db.is_connected:
            logger.warning("BudgetManager: MongoDB offline — using default budget values.")

    def _is_online(self) -> bool:
        return self.db.is_connected and getattr(self.db, "budgets", None) is not None

    def _ensure_db(self):
        if not self._is_online():
            raise ConnectionError(
                "MongoDB is offline. Budget write operations are disabled."
            )

    def set_budget(
        self,
        year: int,
        month: int,
        category: str,
        amount: float,
        user_id: str = DEFAULT_USER_ID,
        currency: str = DEFAULT_CURRENCY,
    ) -> bool:
        """Create or update a budget envelope for a given month and category."""
        self._ensure_db()
        amount = max(0.0, float(amount))
        now = datetime.utcnow()
        filter_query = {
            "user_id": user_id,
            "year": int(year),
            "month": int(month),
            "category": category,
        }
        update_doc = {
            "$set": {
                "budget_amount": round(amount, 2),
                "currency": currency,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        }
        res = self.db.budgets.update_one(filter_query, update_doc, upsert=True)
        return res.acknowledged

    def set_monthly_envelopes(
        self,
        year: int,
        month: int,
        total_ceiling: float,
        category_allocations: Optional[Dict[str, float]] = None,
        user_id: str = DEFAULT_USER_ID,
    ):
        """Set both overall ceiling and individual category envelopes for a month."""
        self.set_budget(year, month, "Total", total_ceiling, user_id)
        if category_allocations:
            for cat, amt in category_allocations.items():
                self.set_budget(year, month, cat, amt, user_id)

    def get_monthly_budget(
        self, year: int, month: int, user_id: str = DEFAULT_USER_ID
    ) -> float:
        """Retrieve overall budget ceiling for a specific month. Defaults to 65000.0 if not found."""
        if not self._is_online():
            return DEFAULT_TOTAL_BUDGET
        doc = self.db.budgets.find_one(
            {"user_id": user_id, "year": int(year), "month": int(month), "category": "Total"}
        )
        if doc:
            return float(doc.get("budget_amount", DEFAULT_TOTAL_BUDGET))
        return DEFAULT_TOTAL_BUDGET

    def get_category_budgets(
        self, year: int, month: int, user_id: str = DEFAULT_USER_ID
    ) -> Dict[str, float]:
        """Retrieve category envelope targets for a month."""
        if not self._is_online():
            return dict(DEFAULT_CATEGORY_BUDGETS)
        cursor = self.db.budgets.find({
            "user_id": user_id,
            "year": int(year),
            "month": int(month),
            "category": {"$ne": "Total"},
        })
        envelopes = {}
        for doc in cursor:
            envelopes[doc["category"]] = float(doc.get("budget_amount", 0.0))
        return envelopes

    def get_all_envelopes_with_defaults(
        self, year: int, month: int, user_id: str = DEFAULT_USER_ID
    ) -> Dict[str, float]:
        """
        Return category envelope targets, falling back to sensible default ratios if unset.
        """
        stored = self.get_category_budgets(year, month, user_id)
        for cat, default_val in DEFAULT_CATEGORY_BUDGETS.items():
            if cat not in stored:
                stored[cat] = default_val
        return stored

    def get_historical_budgets(
        self, user_id: str = DEFAULT_USER_ID
    ) -> Dict[str, float]:
        """Return dict of 'YYYY-MM' -> budget ceiling."""
        if not self._is_online():
            return {}  # Empty → preprocessing uses 65000.0 default per month
        cursor = self.db.budgets.find({"user_id": user_id, "category": "Total"})
        history = {}
        for doc in cursor:
            key = f"{doc['year']:04d}-{doc['month']:02d}"
            history[key] = float(doc.get("budget_amount", DEFAULT_TOTAL_BUDGET))
        return history
