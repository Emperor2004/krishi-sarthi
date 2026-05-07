"""Test authentication endpoints and security features."""
import pytest
from fastapi.testclient import TestClient
from src.krishi.database import UserCRUD
from src.krishi.security import SecurityManager
from src.krishi.exceptions import AuthenticationError, RateLimitError


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_user_registration_success(self, client, sample_vendor_data):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=sample_vendor_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "session_token" in data
        assert data["role"] == "vendor"
        assert "message" in data
    
    def test_user_registration_duplicate_phone(self, client, sample_vendor_data):
        """Test registration with duplicate phone number."""
        # First registration
        client.post("/api/auth/register", json=sample_vendor_data)
        
        # Second registration with same phone
        response = client.post("/api/auth/register", json=sample_vendor_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    def test_user_login_success(self, client, sample_vendor_data):
        """Test successful user login."""
        # Register user first
        register_response = client.post("/api/auth/register", json=sample_vendor_data)
        assert register_response.status_code == 200
        
        # Login
        login_data = {
            "phone": sample_vendor_data["phone"],
            "password": sample_vendor_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "session_token" in data
        assert data["role"] == "vendor"
    
    def test_user_login_invalid_credentials(self, client, sample_vendor_data):
        """Test login with invalid credentials."""
        login_data = {
            "phone": sample_vendor_data["phone"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert "error" in data
    
    def test_session_validation_success(self, client, sample_vendor_data):
        """Test successful session validation."""
        # Register and login
        register_response = client.post("/api/auth/register", json=sample_vendor_data)
        token = register_response.json()["session_token"]
        
        # Validate session
        response = client.get(f"/api/auth/validate?session_token={token}")
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "role" in data
        assert "name" in data
    
    def test_session_validation_invalid_token(self, client):
        """Test session validation with invalid token."""
        response = client.get("/api/auth/validate?session_token=invalid_token")
        assert response.status_code == 401
    
    def test_logout_success(self, client, sample_vendor_data):
        """Test successful logout."""
        # Register and login
        register_response = client.post("/api/auth/register", json=sample_vendor_data)
        token = register_response.json()["session_token"]
        
        # Logout
        response = client.post("/api/auth/logout", json={"session_token": token})
        assert response.status_code == 200
        
        # Try to use token after logout
        validate_response = client.get(f"/api/auth/validate?session_token={token}")
        assert validate_response.status_code == 401


class TestSecurityFeatures:
    """Test security features."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "testpassword123"
        hashed = SecurityManager.get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
        # Verification should work
        assert SecurityManager.verify_password(password, hashed) is True
        assert SecurityManager.verify_password("wrongpassword", hashed) is False
    
    def test_jwt_token_creation_and_verification(self):
        """Test JWT token creation and verification."""
        payload = {"sub": 1, "role": "vendor", "name": "Test User"}
        token = SecurityManager.create_access_token(payload)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verification should return original payload
        verified_payload = SecurityManager.verify_token(token)
        assert verified_payload is not None
        assert verified_payload["sub"] == 1
        assert verified_payload["role"] == "vendor"
        assert verified_payload["name"] == "Test User"
    
    def test_jwt_token_verification_invalid(self):
        """Test JWT verification with invalid token."""
        invalid_token = "invalid.jwt.token"
        verified_payload = SecurityManager.verify_token(invalid_token)
        assert verified_payload is None
    
    def test_rate_limiting_login(self, client, sample_vendor_data):
        """Test login rate limiting."""
        # Try multiple failed logins quickly
        login_data = {
            "phone": sample_vendor_data["phone"],
            "password": "wrongpassword"
        }
        
        # First few attempts should work (but fail authentication)
        for i in range(3):
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 401
        
        # Subsequent attempts should be rate limited
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 429  # Too Many Requests
        
        data = response.json()
        assert "Rate limit exceeded" in data["detail"]
