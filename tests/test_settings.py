"""
Unit tests for SettingsManager and MongoDB persistence of user preferences.
"""

import pytest
from settings_manager import SettingsManager
from config import DEFAULT_USER_ID


def test_settings_retrieval_and_update():
    mgr = SettingsManager()
    initial_profile = mgr.get_profile(DEFAULT_USER_ID)
    assert isinstance(initial_profile, dict)
    assert "full_name" in initial_profile
    assert "email" in initial_profile

    # Update profile
    test_name = "Test User"
    test_email = "test.user@example.com"
    success = mgr.update_profile(DEFAULT_USER_ID, {
        "full_name": test_name,
        "email": test_email,
    })
    assert success is True

    # Retrieve updated profile
    updated = mgr.get_profile(DEFAULT_USER_ID)
    assert updated["full_name"] == test_name
    assert updated["email"] == test_email

    # Restore initial profile
    mgr.update_profile(DEFAULT_USER_ID, {
        "full_name": initial_profile.get("full_name", "Aarav Sharma"),
        "email": initial_profile.get("email", "aarav.sharma@ledgerfolio.in"),
    })
