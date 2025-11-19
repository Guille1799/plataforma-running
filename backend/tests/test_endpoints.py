"""
Comprehensive integration tests for REST API endpoints.

Tests all 17 endpoints with:
- Authentication verification
- Request/Response validation
- Error handling
- Edge cases
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

# Import from test configuration
from tests.conftest import client, test_user_token, test_user


class TestAuthenticationEndpoints:
    """Test suite for authentication endpoints (3 endpoints)"""

    def test_register_user_success(self, client):
        """Test POST /auth/register with valid data"""
        # Given valid registration data
        user_data = {
            "email": "newuser@example.com",
            "password": "securePassword123!",
            "name": "Test User",
        }

        # When registering
        response = client.post("/auth/register", json=user_data)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == "newuser@example.com"

    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        # Given existing user email
        user_data = {
            "email": test_user["email"],
            "password": "newPassword123!",
            "name": "Duplicate",
        }

        # When trying to register
        response = client.post("/auth/register", json=user_data)

        # Then should fail
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data.get("detail", "").lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        # Given invalid email
        user_data = {
            "email": "notanemail",
            "password": "securePassword123!",
            "name": "Test",
        }

        # When registering
        response = client.post("/auth/register", json=user_data)

        # Then should fail
        assert response.status_code == 422

    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        # Given weak password (less than 8 characters)
        user_data = {
            "email": "test@example.com",
            "password": "weak",
            "name": "Test",
        }

        # When registering
        response = client.post("/auth/register", json=user_data)

        # Then should fail or warn
        assert response.status_code in [422, 400]

    def test_login_success(self, client, test_user):
        """Test POST /auth/login with valid credentials"""
        # Given valid credentials
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
        }

        # When logging in
        response = client.post("/auth/login", json=login_data)

        # Then should succeed
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with wrong password"""
        # Given
        login_data = {"email": "test@example.com", "password": "wrongPassword123!"}

        # When logging in
        response = client.post("/auth/login", json=login_data)

        # Then should fail
        assert response.status_code == 401
        data = response.json()
        assert "credentials" in data.get("detail", "").lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        # Given non-existent user
        login_data = {"email": "nonexistent@example.com", "password": "password123!"}

        # When logging in
        response = client.post("/auth/login", json=login_data)

        # Then should fail
        assert response.status_code == 401

    def test_refresh_token(self, client, test_user_token):
        """Test POST /auth/refresh with valid refresh token"""
        # Given valid refresh token
        headers = {"Authorization": f"Bearer {test_user_token['refresh_token']}"}

        # When refreshing
        response = client.post("/auth/refresh", headers=headers)

        # Then should return new tokens
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != test_user_token["refresh_token"]

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        # Given invalid token
        headers = {"Authorization": "Bearer invalidtoken123"}

        # When trying to refresh
        response = client.post("/auth/refresh", headers=headers)

        # Then should fail
        assert response.status_code == 401


class TestOvertariningEndpoints:
    """Test suite for overtraining detection endpoints (3 endpoints)"""

    def test_get_overtraining_status(self, client, test_user_token):
        """Test GET /api/overtraining/status"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting status
        response = client.get("/api/overtraining/status", headers=headers)

        # Then should return current status
        assert response.status_code == 200
        data = response.json()
        assert "sai_score" in data
        assert "status" in data
        assert "recovery_level" in data

    def test_get_overtraining_history(self, client, test_user_token):
        """Test GET /api/overtraining/history"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting history
        response = client.get("/api/overtraining/history", headers=headers)

        # Then should return history
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Can be empty for new user

    def test_calculate_sai_manually(self, client, test_user_token):
        """Test POST /api/overtraining/calculate-sai"""
        # Given workout metrics
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        metrics = {
            "volume": 10.0,
            "intensity": 0.85,
            "stress_level": 0.7,
            "hrv": 50,
            "recovery": 0.8,
        }

        # When calculating SAI
        response = client.post(
            "/api/overtraining/calculate-sai", json=metrics, headers=headers
        )

        # Then should return SAI score
        assert response.status_code == 200
        data = response.json()
        assert "sai_score" in data
        assert data["sai_score"] > 0
        assert "risk_level" in data


class TestHRVEndpoints:
    """Test suite for HRV analysis endpoints (4 endpoints)"""

    def test_analyze_hrv(self, client, test_user_token):
        """Test POST /api/hrv/analyze"""
        # Given RR intervals
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        hrv_data = {
            "rr_intervals": [
                800,
                810,
                795,
                820,
                805,
                815,
                800,
                810,
                795,
                825,
            ],
            "timestamp": datetime.now().isoformat(),
        }

        # When analyzing
        response = client.post("/api/hrv/analyze", json=hrv_data, headers=headers)

        # Then should return analysis
        assert response.status_code == 200
        data = response.json()
        assert "sdnn" in data
        assert "rmssd" in data
        assert "pnn50" in data
        assert "classification" in data

    def test_get_hrv_history(self, client, test_user_token):
        """Test GET /api/hrv/history"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting history
        response = client.get("/api/hrv/history", headers=headers)

        # Then should return history
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_hrv_trends(self, client, test_user_token):
        """Test GET /api/hrv/trends"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting trends
        response = client.get("/api/hrv/trends", headers=headers)

        # Then should return trends
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_hrv_recommendations(self, client, test_user_token):
        """Test GET /api/hrv/recommendations"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting recommendations
        response = client.get("/api/hrv/recommendations", headers=headers)

        # Then should return recommendations
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        if "recommendations" in data:
            assert isinstance(data["recommendations"], list)


class TestRacePredictionEndpoints:
    """Test suite for race prediction endpoints (4 endpoints)"""

    def test_predict_race_performance(self, client, test_user_token):
        """Test POST /api/race-prediction/predict"""
        # Given race metrics
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        race_data = {
            "current_distance_m": 10000,
            "current_time_seconds": 2400,
            "target_distance_m": 21100,
            "temperature": 15,
            "humidity": 50,
            "wind_speed": 0,
            "altitude": 0,
        }

        # When predicting
        response = client.post(
            "/api/race-prediction/predict", json=race_data, headers=headers
        )

        # Then should return prediction
        assert response.status_code == 200
        data = response.json()
        assert "predicted_time_seconds" in data
        assert "predicted_pace" in data
        assert "confidence_score" in data
        assert data["predicted_time_seconds"] > 0

    def test_calculate_vdot(self, client, test_user_token):
        """Test POST /api/race-prediction/calculate-vdot"""
        # Given recent race
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        vdot_data = {"distance_m": 10000, "time_seconds": 2400}

        # When calculating VDOT
        response = client.post(
            "/api/race-prediction/calculate-vdot", json=vdot_data, headers=headers
        )

        # Then should return VDOT
        assert response.status_code == 200
        data = response.json()
        assert "vdot" in data
        assert data["vdot"] > 0

    def test_get_race_predictions_history(self, client, test_user_token):
        """Test GET /api/race-prediction/history"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting history
        response = client.get("/api/race-prediction/history", headers=headers)

        # Then should return history
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_race_predictions_insights(self, client, test_user_token):
        """Test GET /api/race-prediction/insights"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting insights
        response = client.get("/api/race-prediction/insights", headers=headers)

        # Then should return insights
        assert response.status_code in [200, 400]  # Might not have predictions yet


class TestTrainingRecommendationEndpoints:
    """Test suite for training recommendation endpoints"""

    def test_get_training_recommendations(self, client, test_user_token):
        """Test GET /api/training/recommendations"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting recommendations
        response = client.get("/api/training/recommendations", headers=headers)

        # Then should return recommendations
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_weekly_plan(self, client, test_user_token):
        """Test GET /api/training/weekly-plan"""
        # Given authenticated user
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        # When getting plan
        response = client.get("/api/training/weekly-plan", headers=headers)

        # Then should return plan
        assert response.status_code in [200, 400]  # Depends on user setup


class TestAuthenticationValidation:
    """Test authentication validation across endpoints"""

    def test_missing_token_returns_401(self, client):
        """Test that missing token returns 401"""
        # Given no auth header
        response = client.get("/api/overtraining/status")

        # Then should return 401
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client):
        """Test that invalid token returns 401"""
        # Given invalid token
        headers = {"Authorization": "Bearer invalid_token_xyz"}

        response = client.get("/api/overtraining/status", headers=headers)

        # Then should return 401
        assert response.status_code == 401

    def test_expired_token_returns_401(self, client):
        """Test that expired token returns 401 or 422"""
        # Given expired token (created far in past)
        import jwt
        import os

        secret_key = os.getenv("SECRET_KEY", "test-secret-key")
        expired_token = jwt.encode(
            {
                "sub": "test@example.com",
                "exp": datetime.utcnow() - timedelta(hours=1),
            },
            secret_key,
            algorithm="HS256",
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/overtraining/status", headers=headers)

        # Then should fail
        assert response.status_code in [401, 422]


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_json_returns_422(self, client, test_user_token):
        """Test that invalid JSON returns 422"""
        # Given invalid JSON
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}

        response = client.post(
            "/api/overtraining/calculate-sai",
            data="not valid json",
            headers=headers,
        )

        # Then should return 422
        assert response.status_code == 422

    def test_missing_required_fields_returns_422(self, client, test_user_token):
        """Test that missing required fields returns 422"""
        # Given incomplete data
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        incomplete_data = {
            "volume": 10.0,
            # missing intensity, stress_level, hrv, recovery
        }

        response = client.post(
            "/api/overtraining/calculate-sai",
            json=incomplete_data,
            headers=headers,
        )

        # Then should return 422
        assert response.status_code == 422

    def test_invalid_data_types_returns_422(self, client, test_user_token):
        """Test that invalid data types return 422"""
        # Given wrong data types
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        wrong_types = {
            "volume": "not a number",  # Should be float
            "intensity": 0.85,
            "stress_level": 0.7,
            "hrv": 50,
            "recovery": 0.8,
        }

        response = client.post(
            "/api/overtraining/calculate-sai",
            json=wrong_types,
            headers=headers,
        )

        # Then should return 422
        assert response.status_code == 422

    def test_out_of_range_values(self, client, test_user_token):
        """Test handling of out-of-range values"""
        # Given intensity > 1.0 (invalid)
        headers = {"Authorization": f"Bearer {test_user_token['access_token']}"}
        invalid_range = {
            "volume": 10.0,
            "intensity": 1.5,  # Should be 0-1
            "stress_level": 0.7,
            "hrv": 50,
            "recovery": 0.8,
        }

        response = client.post(
            "/api/overtraining/calculate-sai",
            json=invalid_range,
            headers=headers,
        )

        # Then should fail validation
        assert response.status_code in [422, 400]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
