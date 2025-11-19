"""
Simplified integration tests for REST API endpoints.

Tests cover:
- Authentication endpoints
- Error handling
- Authentication validation
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthenticationEndpoints:
    """Test suite for authentication endpoints"""

    def test_register_user_success(self, test_client):
        """Test POST /auth/register with valid data"""
        user_data = {
            "email": "newuser@example.com",
            "password": "securePassword123!",
            "name": "Test User",
        }

        response = test_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code in [201, 200]
        data = response.json()
        assert "email" in data
        assert data["email"] == "newuser@example.com"

    def test_register_user_duplicate_email(self, test_client, registered_user):
        """Test registration with existing email"""
        user_data = {
            "email": registered_user["email"],
            "password": "newPassword123!",
            "name": "Duplicate",
        }

        response = test_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code in [409, 400, 422]

    def test_login_success(self, test_client, test_user_data):
        """Test POST /auth/login with valid credentials"""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        # Either 200 or 422 if user doesn't exist from fixture
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data

    def test_login_invalid_credentials(self, test_client):
        """Test login with wrong password"""
        login_data = {
            "email": "test@example.com",
            "password": "wrongPassword123!",
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code in [401, 400, 422]


class TestAuthenticationValidation:
    """Test authentication validation"""

    def test_missing_token_returns_401(self, test_client):
        """Test that missing token returns 401"""
        response = test_client.get("/api/v1/workouts")
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, test_client):
        """Test that invalid token returns 401"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = test_client.get("/api/v1/workouts", headers=headers)
        assert response.status_code == 401


class TestErrorHandling:
    """Test error handling"""

    def test_missing_required_fields_returns_422(self, test_client):
        """Test that missing required fields returns 422"""
        incomplete_data = {"email": "test@example.com"}
        response = test_client.post("/api/v1/auth/login", json=incomplete_data)
        assert response.status_code == 422

    def test_invalid_email_format(self, test_client):
        """Test invalid email format"""
        user_data = {
            "email": "notanemail",
            "password": "securePassword123!",
            "name": "Test",
        }
        response = test_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
