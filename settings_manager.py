"""
Little Ledger - User Profile & Application Settings Manager
Handles MongoDB persistence for profile adjustments, regional rails, and editorial preferences.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from database import get_db
from config import DEFAULT_USER_ID

DEFAULT_PROFILE = {
    "user_id": DEFAULT_USER_ID,
    "full_name": "Aarav Sharma",
    "email": "aarav.sharma@ledgerfolio.in",
    "ledger_identifier": "FOLIO-BLR-2024-098",
    "member_since": "January 2023 (Active Ledger)",
    "base_currency": "Indian Rupee (INR ₹)",
    "fiscal_calendar": "Indian Financial Year (Apr - Mar)",
    "number_format": "Indian Lakhs & Crores (1,00,000.00)",
    "date_format": "Mon DD, YYYY (Sep 20, 2024)",
    "theme": "Botanical Linen (Warm Cream)",
    "typography_density": "Comfortable Editorial",
    "updated_at": datetime.utcnow(),
}


class SettingsManager:
    """Manages reading and writing user profile & configuration to MongoDB."""

    def __init__(self):
        self.db = get_db()

    def get_profile(self, user_id: str = DEFAULT_USER_ID) -> Dict[str, Any]:
        """Fetch profile settings from MongoDB, falling back to default."""
        if not self.db.is_connected or self.db.settings is None:
            prof = dict(DEFAULT_PROFILE)
            prof["user_id"] = user_id
            return prof

        doc = self.db.settings.find_one({"user_id": user_id})
        if not doc:
            # Look up display name if registered via auth
            display_name = user_id.capitalize()
            try:
                if self.db.db is not None:
                    u = self.db.db["users"].find_one({"username": user_id})
                    if u and u.get("display_name"):
                        display_name = u["display_name"]
            except Exception:
                pass

            new_profile = {
                "user_id": user_id,
                "full_name": display_name,
                "email": f"{user_id}@ledgerfolio.in",
                "ledger_identifier": f"FOLIO-{user_id.upper()[:6]}-2026",
                "member_since": datetime.utcnow().strftime("%B %Y (Active Ledger)"),
                "base_currency": "Indian Rupee (INR ₹)",
                "fiscal_calendar": "Indian Financial Year (Apr - Mar)",
                "number_format": "Indian Lakhs & Crores (1,00,000.00)",
                "date_format": "Mon DD, YYYY (Sep 20, 2024)",
                "theme": "Botanical Linen (Warm Cream)",
                "typography_density": "Comfortable Editorial",
                "updated_at": datetime.utcnow(),
            }
            try:
                self.db.settings.update_one(
                    {"user_id": user_id},
                    {"$setOnInsert": new_profile},
                    upsert=True,
                )
            except Exception:
                pass
            return new_profile

        profile = dict(DEFAULT_PROFILE)
        profile.update(doc)
        profile["user_id"] = user_id
        return profile

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update and persist profile adjustments to MongoDB."""
        if not self.db.is_connected or self.db.settings is None:
            return False

        updates["updated_at"] = datetime.utcnow()
        self.db.settings.update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True,
        )
        return True
