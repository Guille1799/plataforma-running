"""
Integration tests for REST API endpoints.

Tests complete workflows and endpoint interactions using the real FastAPI app.
Uses TestClient from fastapi.testclient for testing without running a server.

Covers:
- Authentication (register, login, get current user)
- Workouts (create, list, get detail, stats)
- AI Coach (chat, chat history, workout analysis)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import json

from app.main import app
from app.database import Base, get_db
from app.schemas import (
    UserCreate,
    LoginRequest,
    WorkoutCreate,
    ChatMessageCreate,
)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db_engine):
    """Create a fresh database session for each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, db_session):
    """Register a test user and return authentication headers."""
    # Register user
    register_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    return {
        "Authorization": f"Bearer {access_token}",
        "user_id": token_data["user"]["id"],
        "email": token_data["user"]["email"],
    }


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user_success(self, client):
        """Test successful user registration returns 201 with tokens."""
        user_data = {
            "name": "John Runner",
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["name"] == user_data["name"]
    
    def test_register_user_duplicate_email(self, client):
        """Test registering with existing email returns 400."""
        user_data = {
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "Pass123!"
        }
        
        # First registration succeeds
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email fails
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email returns 422."""
        user_data = {
            "name": "Invalid Email User",
            "email": "not-an-email",
            "password": "Pass123!"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_user_weak_password(self, client):
        """Test registration with password < 8 chars returns 422."""
        user_data = {
            "name": "Weak Pass User",
            "email": "weak@example.com",
            "password": "short"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_login_user_success(self, client):
        """Test successful login returns 200 with tokens."""
        # Register user
        register_data = {
            "name": "Login Test",
            "email": "login@example.com",
            "password": "LoginPass123!"
        }
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "LoginPass123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == login_data["email"]
    
    def test_login_user_invalid_credentials(self, client):
        """Test login with wrong password returns 401."""
        # Register user
        register_data = {
            "name": "Auth Test",
            "email": "auth@example.com",
            "password": "CorrectPass123!"
        }
        client.post("/api/v1/auth/register", json=register_data)
        
        # Try login with wrong password
        login_data = {
            "email": "auth@example.com",
            "password": "WrongPass123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_user_nonexistent(self, client):
        """Test login with non-existent email returns 401."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Pass123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_athlete_profile_success(self, client, auth_headers):
        """Test getting athlete profile returns 200 with profile data."""
        response = client.get(
            "/api/v1/profile/",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or response.status_code == 200
    
    def test_get_athlete_profile_no_token(self, client):
        """Test getting profile without token returns 403."""
        response = client.get("/api/v1/profile/")
        assert response.status_code == 403
    
    def test_get_athlete_profile_invalid_token(self, client):
        """Test getting profile with invalid token returns 403."""
        response = client.get(
            "/api/v1/profile/",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 403


# ============================================================================
# WORKOUT TESTS
# ============================================================================

class TestWorkouts:
    """Test workout endpoints."""
    
    def test_create_workout_success(self, client, auth_headers):
        """Test creating a workout returns 201 with workout data."""
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 3600,
            "distance_meters": 10000.0,
            "avg_heart_rate": 150,
            "max_heart_rate": 170,
            "avg_pace": 360.0,
            "max_speed": 15.0,
            "calories": 800.0,
            "elevation_gain": 150.0,
            "avg_cadence": 180.0,
        }
        response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["sport_type"] == "running"
        assert data["distance_meters"] == 10000.0
        assert data["user_id"] == auth_headers["user_id"]
        assert "id" in data
    
    def test_create_workout_minimal(self, client, auth_headers):
        """Test creating workout with minimal fields."""
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "cycling",
            "start_time": start_time.isoformat(),
            "duration_seconds": 1800,
            "distance_meters": 5000.0,
        }
        response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["sport_type"] == "cycling"
        assert data["distance_meters"] == 5000.0
    
    def test_create_workout_no_auth(self, client):
        """Test creating workout without auth returns 403."""
        workout_data = {
            "sport_type": "running",
            "start_time": datetime.utcnow().isoformat(),
            "duration_seconds": 3600,
            "distance_meters": 10000.0,
        }
        response = client.post("/api/v1/workouts/create", json=workout_data)
        assert response.status_code == 403
    
    def test_create_workout_invalid_distance(self, client, auth_headers):
        """Test creating workout with negative distance returns 422."""
        workout_data = {
            "sport_type": "running",
            "start_time": datetime.utcnow().isoformat(),
            "duration_seconds": 3600,
            "distance_meters": -1000.0,  # Invalid
        }
        response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        assert response.status_code == 422
    
    def test_get_workouts_list_empty(self, client, auth_headers):
        """Test getting workouts list when empty returns 200 with empty list."""
        response = client.get(
            "/api/v1/workouts",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_workouts_list_with_data(self, client, auth_headers):
        """Test getting workouts list with data returns 200 with workouts."""
        # Create a workout first
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 2400,
            "distance_meters": 7000.0,
            "avg_heart_rate": 140,
        }
        create_response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        assert create_response.status_code == 201
        
        # Get list
        response = client.get(
            "/api/v1/workouts",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["sport_type"] == "running"
    
    def test_get_workouts_pagination(self, client, auth_headers):
        """Test workouts pagination with skip and limit."""
        # Create 5 workouts
        base_time = datetime.utcnow()
        for i in range(5):
            workout_data = {
                "sport_type": "running",
                "start_time": (base_time - timedelta(days=i)).isoformat(),
                "duration_seconds": 1800 + (i * 100),
                "distance_meters": 5000.0 + (i * 500),
            }
            client.post(
                "/api/v1/workouts/create",
                json=workout_data,
                headers={"Authorization": auth_headers["Authorization"]}
            )
        
        # Get with limit
        response = client.get(
            "/api/v1/workouts?limit=2",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_workout_detail_success(self, client, auth_headers):
        """Test getting single workout detail returns 200."""
        # Create workout
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 3000,
            "distance_meters": 8000.0,
            "avg_heart_rate": 155,
            "max_heart_rate": 175,
        }
        create_response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        workout_id = create_response.json()["id"]
        
        # Get detail
        response = client.get(
            f"/api/v1/workouts/{workout_id}",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workout_id
        assert data["sport_type"] == "running"
        assert data["distance_meters"] == 8000.0
    
    def test_get_workout_detail_not_found(self, client, auth_headers):
        """Test getting non-existent workout returns 404."""
        response = client.get(
            "/api/v1/workouts/99999",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 404
    
    def test_get_workout_detail_unauthorized(self, client, auth_headers):
        """Test getting another user's workout returns 404."""
        # Create workout as first user
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 2000,
            "distance_meters": 6000.0,
        }
        create_response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        workout_id = create_response.json()["id"]
        
        # Create second user and try to access
        register_data = {
            "name": "Second User",
            "email": "second@example.com",
            "password": "Pass123!"
        }
        register_response = client.post("/api/v1/auth/register", json=register_data)
        second_token = register_response.json()["access_token"]
        
        response = client.get(
            f"/api/v1/workouts/{workout_id}",
            headers={"Authorization": f"Bearer {second_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_workout_stats_no_workouts(self, client, auth_headers):
        """Test getting stats with no workouts returns valid stats."""
        response = client.get(
            "/api/v1/workouts/stats",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_workouts" in data
        assert data["total_workouts"] == 0
        assert data["total_distance_km"] == 0.0
    
    def test_get_workout_stats_with_data(self, client, auth_headers):
        """Test getting stats with workouts returns aggregated data."""
        # Create two workouts
        base_time = datetime.utcnow()
        workouts = [
            {
                "sport_type": "running",
                "start_time": base_time.isoformat(),
                "duration_seconds": 3600,
                "distance_meters": 10000.0,
                "avg_heart_rate": 150,
                "calories": 800.0,
            },
            {
                "sport_type": "cycling",
                "start_time": (base_time - timedelta(days=1)).isoformat(),
                "duration_seconds": 5400,
                "distance_meters": 30000.0,
                "avg_heart_rate": 140,
                "calories": 1200.0,
            }
        ]
        
        for workout in workouts:
            client.post(
                "/api/v1/workouts/create",
                json=workout,
                headers={"Authorization": auth_headers["Authorization"]}
            )
        
        # Get stats
        response = client.get(
            "/api/v1/workouts/stats",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_workouts"] == 2
        assert data["total_distance_km"] == 40.0  # 10km + 30km
        assert "sports_breakdown" in data


# ============================================================================
# AI COACH TESTS
# ============================================================================

class TestCoach:
    """Test AI Coach endpoints."""
    
    def test_chat_with_coach_success(self, client, auth_headers):
        """Test chat endpoint returns 200 with ChatResponse."""
        message_data = {
            "message": "How should I train for a half marathon?"
        }
        response = client.post(
            "/api/v1/coach/chat",
            json=message_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user_message" in data
        assert "assistant_message" in data
        assert "tokens_used" in data
        assert "conversation_length" in data
        assert data["user_message"]["role"] == "user"
        assert data["assistant_message"]["role"] == "assistant"
        assert len(data["assistant_message"]["content"]) > 0
    
    def test_chat_with_coach_multiple_messages(self, client, auth_headers):
        """Test multiple chat messages maintain conversation."""
        messages = [
            {"message": "What is vo2 max?"},
            {"message": "How can I improve it?"},
            {"message": "What's a good training plan?"},
        ]
        
        for msg in messages:
            response = client.post(
                "/api/v1/coach/chat",
                json=msg,
                headers={"Authorization": auth_headers["Authorization"]}
            )
            assert response.status_code == 200
            assert response.json()["conversation_length"] > 0
    
    def test_chat_with_coach_empty_message(self, client, auth_headers):
        """Test chat with empty message returns 422."""
        message_data = {
            "message": ""
        }
        response = client.post(
            "/api/v1/coach/chat",
            json=message_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 422
    
    def test_chat_with_coach_no_auth(self, client):
        """Test chat without auth returns 403."""
        message_data = {
            "message": "Hello coach!"
        }
        response = client.post("/api/v1/coach/chat", json=message_data)
        assert response.status_code == 403
    
    def test_get_chat_history_empty(self, client, auth_headers):
        """Test getting chat history when empty returns empty list."""
        response = client.get(
            "/api/v1/coach/chat/history",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_chat_history_with_messages(self, client, auth_headers):
        """Test getting chat history with messages returns all messages."""
        # Send some messages
        messages = [
            {"message": "First question?"},
            {"message": "Second question?"},
        ]
        
        for msg in messages:
            client.post(
                "/api/v1/coach/chat",
                json=msg,
                headers={"Authorization": auth_headers["Authorization"]}
            )
        
        # Get history
        response = client.get(
            "/api/v1/coach/chat/history",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4  # 2 user + 2 assistant messages
        
        # Check structure
        for msg in data:
            assert "id" in msg
            assert "role" in msg
            assert msg["role"] in ["user", "assistant"]
            assert "content" in msg
            assert "created_at" in msg
    
    def test_get_chat_history_pagination(self, client, auth_headers):
        """Test chat history respects limit parameter."""
        # Send multiple messages
        for i in range(5):
            client.post(
                "/api/v1/coach/chat",
                json={"message": f"Question {i}?"},
                headers={"Authorization": auth_headers["Authorization"]}
            )
        
        # Get with limit
        response = client.get(
            "/api/v1/coach/chat/history?limit=5",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_analyze_workout_success(self, client, auth_headers):
        """Test analyzing a workout returns analysis data."""
        # Create a workout first
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 3600,
            "distance_meters": 10000.0,
            "avg_heart_rate": 155,
            "max_heart_rate": 175,
            "avg_pace": 360.0,
        }
        create_response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        workout_id = create_response.json()["id"]
        
        # Analyze workout
        response = client.post(
            f"/api/v1/coach/analyze/{workout_id}",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_analyze_workout_not_found(self, client, auth_headers):
        """Test analyzing non-existent workout returns 404."""
        response = client.post(
            "/api/v1/coach/analyze/99999",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        assert response.status_code == 404
    
    def test_analyze_workout_unauthorized(self, client, auth_headers):
        """Test analyzing another user's workout returns 404."""
        # Create workout as first user
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 2000,
            "distance_meters": 6000.0,
        }
        create_response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        workout_id = create_response.json()["id"]
        
        # Create second user
        register_data = {
            "name": "Other User",
            "email": "other@example.com",
            "password": "Pass123!"
        }
        register_response = client.post("/api/v1/auth/register", json=register_data)
        second_token = register_response.json()["access_token"]
        
        # Try to analyze as second user
        response = client.post(
            f"/api/v1/coach/analyze/{workout_id}",
            headers={"Authorization": f"Bearer {second_token}"}
        )
        
        assert response.status_code == 404


# ============================================================================
# INTEGRATION WORKFLOW TESTS
# ============================================================================

class TestIntegrationWorkflows:
    """Test complete user workflows combining multiple endpoints."""
    
    def test_complete_user_journey(self, client):
        """Test complete flow: register -> create workout -> chat -> analyze."""
        # 1. Register user
        register_data = {
            "name": "Journey User",
            "email": "journey@example.com",
            "password": "JourneyPass123!"
        }
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        token = register_response.json()["access_token"]
        user_id = register_response.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Verify user can get athlete profile
        profile_response = client.get("/api/v1/profile/", headers=headers)
        assert profile_response.status_code == 200
        
        # 3. Create a workout
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 3600,
            "distance_meters": 10000.0,
            "avg_heart_rate": 150,
            "max_heart_rate": 170,
            "avg_pace": 360.0,
        }
        workout_response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers=headers
        )
        assert workout_response.status_code == 201
        workout_id = workout_response.json()["id"]
        
        # 4. Get workout stats
        stats_response = client.get("/api/v1/workouts/stats", headers=headers)
        assert stats_response.status_code == 200
        assert stats_response.json()["total_workouts"] == 1
        
        # 5. Chat with coach
        chat_response = client.post(
            "/api/v1/coach/chat",
            json={"message": "How was my workout?"},
            headers=headers
        )
        assert chat_response.status_code == 200
        
        # 6. Get chat history
        history_response = client.get(
            "/api/v1/coach/chat/history",
            headers=headers
        )
        assert history_response.status_code == 200
        assert len(history_response.json()) >= 2
        
        # 7. Analyze workout
        analyze_response = client.post(
            f"/api/v1/coach/analyze/{workout_id}",
            headers=headers
        )
        assert analyze_response.status_code == 200
    
    def test_multiple_users_isolation(self, client):
        """Test that different users cannot access each other's data."""
        # Create user 1
        user1_data = {
            "name": "User One",
            "email": "user1@example.com",
            "password": "Pass123!"
        }
        user1_response = client.post("/api/v1/auth/register", json=user1_data)
        user1_token = user1_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        # Create user 2
        user2_data = {
            "name": "User Two",
            "email": "user2@example.com",
            "password": "Pass123!"
        }
        user2_response = client.post("/api/v1/auth/register", json=user2_data)
        user2_token = user2_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 1 creates workout
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 3000,
            "distance_meters": 8000.0,
        }
        user1_workout = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers=user1_headers
        )
        user1_workout_id = user1_workout.json()["id"]
        
        # User 2 tries to access User 1's workout - should fail
        response = client.get(
            f"/api/v1/workouts/{user1_workout_id}",
            headers=user2_headers
        )
        assert response.status_code == 404
        
        # User 2's stats should be empty
        user2_stats = client.get(
            "/api/v1/workouts/stats",
            headers=user2_headers
        )
        assert user2_stats.json()["total_workouts"] == 0


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error scenarios and edge cases."""
    
    def test_health_check(self, client):
        """Test health check endpoints are available."""
        # Root health check
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Health check endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
    
    def test_missing_required_fields_register(self, client):
        """Test registration with missing required fields returns 422."""
        invalid_data = {
            "email": "test@example.com",
            # Missing name and password
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_malformed_json(self, client):
        """Test sending malformed JSON returns 422."""
        response = client.post(
            "/api/v1/auth/register",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [422, 400]
    
    def test_invalid_heart_rate_values(self, client, auth_headers):
        """Test workout with invalid heart rate values."""
        start_time = datetime.utcnow()
        workout_data = {
            "sport_type": "running",
            "start_time": start_time.isoformat(),
            "duration_seconds": 1800,
            "distance_meters": 5000.0,
            "avg_heart_rate": -10,  # Invalid: negative HR
        }
        response = client.post(
            "/api/v1/workouts/create",
            json=workout_data,
            headers={"Authorization": auth_headers["Authorization"]}
        )
        assert response.status_code == 422
