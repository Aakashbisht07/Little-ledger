"""
Test Database Connectivity and Health
"""

import pytest
from database import get_db, serialize_doc
from bson import ObjectId
from datetime import datetime


def test_database_connection():
    db = get_db()
    assert db is not None
    healthy, msg, stats = db.health_check()
    assert healthy is True
    assert "version" in stats
    assert stats["db_name"] == "little_ledger"


def test_serialize_doc():
    sample_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "user_id": "test_user",
        "amount": 420.50,
        "date": datetime(2024, 9, 28, 10, 0, 0),
    }
    serialized = serialize_doc(sample_doc)
    assert serialized["id"] == "507f1f77bcf86cd799439011"
    assert serialized["_id"] == "507f1f77bcf86cd799439011"
    assert isinstance(serialized["date"], str)
    assert serialized["amount"] == 420.50
