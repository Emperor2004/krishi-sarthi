"""Session Agent – User authentication and session management.

This module handles user registration, login, and session management
for both vendors and consumers. It provides secure session tokens
and proper user identity management.
"""
import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .utils import load_json, save_json


SESSION_TIMEOUT_HOURS = 24
SESSIONS_FILE = "sessions.json"
USERS_FILE = "users.json"


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


def _is_session_valid(session_data: Dict[str, Any]) -> bool:
    """Check if a session is still valid (not expired)."""
    created_at = session_data.get("created_at", 0)
    expiry_hours = session_data.get("expiry_hours", SESSION_TIMEOUT_HOURS)
    expiry_time = created_at + (expiry_hours * 3600)
    return time.time() < expiry_time


def register_user(phone: str, name: str, role: str, password: str, address: Optional[str] = None) -> Dict[str, Any]:
    """Register a new user (vendor or consumer).

    Returns user data on success, error dict on failure.
    """
    if role not in ["vendor", "consumer"]:
        return {"error": "Invalid role. Must be 'vendor' or 'consumer'."}

    users = load_json(USERS_FILE)

    # Check if phone already exists
    for user in users:
        if user.get("phone") == phone:
            return {"error": "Phone number already registered."}

    # Create new user
    user_id = max((u.get("id", 0) for u in users), default=0) + 1
    user = {
        "id": user_id,
        "phone": phone,
        "name": name,
        "role": role,
        "password_hash": _hash_password(password),
        "address": address or "",
        "created_at": time.time(),
        "is_active": True,
    }

    # Add role-specific data
    if role == "vendor":
        user["shop_name"] = ""
        user["products"] = []
        user["location"] = {"lat": 0.0, "lng": 0.0}
    elif role == "consumer":
        user["orders"] = []
        user["udhar_balance"] = 0.0

    users.append(user)
    save_json(USERS_FILE, users)

    # Create initial session
    session_token = _generate_session_token()
    session = {
        "token": session_token,
        "user_id": user_id,
        "role": role,
        "created_at": time.time(),
        "expiry_hours": SESSION_TIMEOUT_HOURS,
        "last_activity": time.time(),
    }

    sessions = load_json(SESSIONS_FILE)
    sessions.append(session)
    save_json(SESSIONS_FILE, sessions)

    return {
        "user_id": user_id,
        "role": role,
        "session_token": session_token,
        "message": f"Registration successful. Welcome {name}!",
    }


def login_user(phone: str, password: str) -> Dict[str, Any]:
    """Authenticate user and create session.

    Returns session data on success, error dict on failure.
    """
    users = load_json(USERS_FILE)
    password_hash = _hash_password(password)

    # Find user
    user = None
    for u in users:
        if u.get("phone") == phone and u.get("password_hash") == password_hash:
            user = u
            break

    if not user:
        return {"error": "Invalid phone number or password."}

    if not user.get("is_active", True):
        return {"error": "Account is deactivated."}

    # Create session
    session_token = _generate_session_token()
    session = {
        "token": session_token,
        "user_id": user["id"],
        "role": user["role"],
        "created_at": time.time(),
        "expiry_hours": SESSION_TIMEOUT_HOURS,
        "last_activity": time.time(),
    }

    sessions = load_json(SESSIONS_FILE)
    sessions.append(session)
    save_json(SESSIONS_FILE, sessions)

    return {
        "user_id": user["id"],
        "role": user["role"],
        "session_token": session_token,
        "message": f"Login successful. Welcome back {user['name']}!",
    }


def validate_session(session_token: str) -> Optional[Dict[str, Any]]:
    """Validate a session token and return user info if valid.

    Returns user data dict if session is valid, None otherwise.
    """
    sessions = load_json(SESSIONS_FILE)

    for session in sessions:
        if session.get("token") == session_token and _is_session_valid(session):
            # Update last activity
            session["last_activity"] = time.time()
            save_json(SESSIONS_FILE, sessions)

            # Get user data
            user_id = session["user_id"]
            users = load_json(USERS_FILE)
            for user in users:
                if user.get("id") == user_id and user.get("is_active", True):
                    return {
                        "user_id": user_id,
                        "role": session["role"],
                        "name": user.get("name", ""),
                        "phone": user.get("phone", ""),
                        "session_token": session_token,
                    }

    return None


def logout_user(session_token: str) -> bool:
    """Invalidate a session token (logout)."""
    sessions = load_json(SESSIONS_FILE)
    updated_sessions = [s for s in sessions if s.get("token") != session_token]

    if len(updated_sessions) < len(sessions):
        save_json(SESSIONS_FILE, updated_sessions)
        return True

    return False


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user data by ID."""
    users = load_json(USERS_FILE)
    for user in users:
        if user.get("id") == user_id:
            return user
    return None


def update_user_profile(user_id: int, updates: Dict[str, Any]) -> bool:
    """Update user profile information."""
    users = load_json(USERS_FILE)

    for user in users:
        if user.get("id") == user_id:
            # Only allow updating certain fields
            allowed_updates = ["name", "address", "shop_name", "location"]
            for key, value in updates.items():
                if key in allowed_updates:
                    user[key] = value
            save_json(USERS_FILE, users)
            return True

    return False


def cleanup_expired_sessions() -> int:
    """Remove expired sessions. Returns number of sessions cleaned up."""
    sessions = load_json(SESSIONS_FILE)
    active_sessions = [s for s in sessions if _is_session_valid(s)]

    cleaned_count = len(sessions) - len(active_sessions)
    if cleaned_count > 0:
        save_json(SESSIONS_FILE, active_sessions)

    return cleaned_count


# Legacy compatibility functions (for backward compatibility)
def get_vendor_by_id(vendor_id: int) -> Dict[str, Any]:
    """Legacy function - get vendor data by ID."""
    user = get_user_by_id(vendor_id)
    if user and user.get("role") == "vendor":
        # Convert to legacy format
        return {
            "id": user["id"],
            "name": user.get("name", ""),
            "shop_name": user.get("shop_name", ""),
            "phone": user.get("phone", ""),
            "address": user.get("address", ""),
            "location": user.get("location", {}),
            "products": user.get("products", []),
        }
    return {}


def get_consumer_by_id(consumer_id: int) -> Dict[str, Any]:
    """Legacy function - get consumer data by ID."""
    user = get_user_by_id(consumer_id)
    if user and user.get("role") == "consumer":
        # Convert to legacy format
        return {
            "id": user["id"],
            "name": user.get("name", ""),
            "phone": user.get("phone", ""),
            "address": user.get("address", ""),
            "orders": user.get("orders", []),
            "udhar_balance": user.get("udhar_balance", 0.0),
        }
    return {}