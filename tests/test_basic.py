"""Tests for Krishi Saarthi."""
import pytest
import sys
import os
import random

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from krishi.core.conversation_agent import handle_conversation
        from krishi.services.session_agent import register_user, login_user
        from krishi.utils.utils import load_json, save_json
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_session_management():
    """Test basic session management functionality."""
    from krishi.services.session_agent import register_user, login_user, validate_session

    # Test user registration with a unique phone number to avoid shared test state.
    phone = f"9{random.randint(10**8, 10**9 - 1)}"
    result = register_user(phone, "Test User", "vendor", "password123")
    assert "user_id" in result
    assert result["role"] == "vendor"

    # Test login
    login_result = login_user(phone, "password123")
    assert "session_token" in login_result

    # Test session validation
    session_data = validate_session(login_result["session_token"])
    assert session_data is not None
    assert session_data["role"] == "vendor"

def test_conversation_agent():
    """Test conversation agent basic functionality."""
    from krishi.core.conversation_agent import detect_intent

    # Test intent detection
    intent = detect_intent("vendor", "naya product add karo")
    assert intent == "add_product"

    intent = detect_intent("consumer", "mujhe tamatar chahiye")
    assert intent == "search_product"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])