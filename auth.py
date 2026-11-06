"""
Little Ledger — Authentication Module
Handles user registration, login, and session management.
Passwords are hashed with SHA-256 + per-user salt and stored in MongoDB.
"""

import hashlib
import os
import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from database import get_db


def _hash_password(password: str, salt: str) -> str:
    """Return SHA-256 hex digest of password + salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def _generate_salt() -> str:
    return os.urandom(16).hex()


def _validate_username(username: str) -> Tuple[bool, str]:
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 30:
        return False, "Username must be at most 30 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""


def _validate_password(password: str) -> Tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


def register_user(username: str, password: str, display_name: str = "") -> Tuple[bool, str]:
    """
    Register a new user.
    Returns (success, message).
    """
    username = username.strip().lower()
    display_name = display_name.strip() or username

    ok, msg = _validate_username(username)
    if not ok:
        return False, msg

    ok, msg = _validate_password(password)
    if not ok:
        return False, msg

    db = get_db()
    if not db.is_connected:
        return False, "Database is offline. Cannot register."

    # Check duplicate
    if db.db["users"].find_one({"username": username}):
        return False, "Username already taken. Please choose another."

    salt = _generate_salt()
    hashed = _hash_password(password, salt)

    user_doc: Dict[str, Any] = {
        "username": username,
        "display_name": display_name,
        "password_hash": hashed,
        "salt": salt,
        "created_at": datetime.utcnow(),
        "last_login": None,
    }
    db.db["users"].insert_one(user_doc)
    return True, "Account created successfully!"


def login_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate a user.
    Returns (success, message, user_doc_or_None).
    """
    username = username.strip().lower()

    db = get_db()
    if not db.is_connected:
        return False, "Database is offline. Cannot log in.", None

    user = db.db["users"].find_one({"username": username})
    if not user:
        return False, "No account found with that username.", None

    expected = _hash_password(password, user["salt"])
    if expected != user["password_hash"]:
        return False, "Incorrect password. Please try again.", None

    # Update last login timestamp
    db.db["users"].update_one(
        {"username": username},
        {"$set": {"last_login": datetime.utcnow()}},
    )

    return True, "Welcome back!", {
        "user_id": username,
        "display_name": user.get("display_name", username),
        "username": username,
    }

