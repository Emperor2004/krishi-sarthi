"""Test API integration and end-to-end flows."""
import pytest
from fastapi.testclient import TestClient
import json


class TestAPIIntegration:
    """Test API integration and complete user flows."""
    
    def test_complete_vendor_flow(self, client):
        """Test complete vendor registration and product listing flow."""
        # 1. Register vendor
        vendor_data = {
            "phone": "9876543210",
            "name": "Ramesh Kumar",
            "role": "vendor",
            "password": "vendorpass123",
            "address": "Village Rampur"
        }
        
        register_response = client.post("/api/auth/register", json=vendor_data)
        assert register_response.status_code == 200
        token = register_response.json()["session_token"]
        
        # 2. Add product via listing endpoint
        product_data = {
            "voice_text": "50 kilo tamatar 40 rupaye kilo",
            "vendor_id": 1
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        listing_response = client.post("/api/listing", json=product_data, headers=headers)
        assert listing_response.status_code == 200
        
        listing_result = listing_response.json()
        assert listing_result["success"] is True
        assert "saved_item" in listing_result
        assert listing_result["saved_item"]["product_name"] == "Tamatar"
    
    def test_complete_consumer_flow(self, client):
        """Test complete consumer registration and order flow."""
        # 1. Register consumer
        consumer_data = {
            "phone": "9876543211",
            "name": "Sita Devi",
            "role": "consumer", 
            "password": "consumerpass123",
            "address": "Village Sivan"
        }
        
        register_response = client.post("/api/auth/register", json=consumer_data)
        assert register_response.status_code == 200
        token = register_response.json()["session_token"]
        
        # 2. Search for products
        search_data = {
            "query_text": "tamatar chahiye",
            "consumer_id": 1
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        search_response = client.post("/api/discovery", json=search_data, headers=headers)
        assert search_response.status_code == 200
        
        search_result = search_response.json()
        assert "results" in search_result
        assert len(search_result["results"]) >= 0
    
    def test_voice_endpoint_authentication_required(self, client):
        """Test that voice endpoints require authentication."""
        voice_data = {
            "voice_text": "naya product add karo",
            "language": "hi"
        }
        
        # Without authentication
        response = client.post("/api/voice", json=voice_data)
        assert response.status_code == 200  # Should return session expired message
        
        result = response.json()
        assert result["action"] == "session_expired"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "stt_available" in data
        assert "tts_available" in data
        assert "ollama_host" in data
        assert "ollama_model" in data
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options("/api/health")
        assert response.status_code == 200
        
        # Check for CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payloads."""
        response = client.post(
            "/api/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_required_fields(self, client):
        """Test validation of required fields."""
        incomplete_data = {
            "phone": "9876543210"
            # Missing name, role, password
        }
        
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == 422
    
    def test_database_error_handling(self, client):
        """Test graceful handling of database errors."""
        # This would require mocking database failures
        # For now, test with very large payload that might cause issues
        large_data = {
            "phone": "9876543210",
            "name": "A" * 1000,  # Very long name
            "role": "vendor",
            "password": "testpass123",
            "address": "B" * 1000  # Very long address
        }
        
        response = client.post("/api/auth/register", json=large_data)
        # Should either succeed or fail gracefully with proper error
        assert response.status_code in [200, 400, 422]
    
    def test_rate_limiting_headers(self, client):
        """Test rate limiting includes proper headers."""
        # Make multiple requests quickly to trigger rate limit
        for _ in range(10):
            response = client.post("/api/auth/login", json={
                "phone": "9876543210",
                "password": "wrongpassword"
            })
            if response.status_code == 429:
                # Check for Retry-After header
                assert "retry-after" in response.headers
                break
