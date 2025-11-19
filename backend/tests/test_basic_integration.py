"""
Simplified Backend Tests
Tests core functionality without complex service imports
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def setup_test_db():
    """Create tables for testing"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db(setup_test_db):
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_db):
    """Create test client"""
    return TestClient(app)


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test user authentication endpoints"""
    
    def test_register_user_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "john@example.com"
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "name": "User 1",
                "email": "dup@example.com",
                "password": "Pass123!"
            }
        )
        
        # Try register same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "User 2",
                "email": "dup@example.com",
                "password": "Pass456!"
            }
        )
        assert response.status_code == 400
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register
        client.post(
            "/api/v1/auth/register",
            json={
                "name": "Login Test",
                "email": "login@example.com",
                "password": "Password123!"
            }
        )
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "Password123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_invalid_password(self, client):
        """Test login with wrong password"""
        # Register
        client.post(
            "/api/v1/auth/register",
            json={
                "name": "User",
                "email": "test@example.com",
                "password": "Password123!"
            }
        )
        
        # Try login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client):
        """Test getting current user info"""
        # Register
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Current User",
                "email": "current@example.com",
                "password": "Pass123!"
            }
        )
        token = reg.json()["access_token"]
        
        # Get me
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"
    
    def test_protected_endpoint_no_auth(self, client):
        """Test accessing protected endpoint without auth"""
        response = client.get(
            "/api/v1/auth/me"
        )
        assert response.status_code in [401, 403]


# ============================================================================
# WORKOUT TESTS
# ============================================================================

class TestWorkouts:
    """Test workout endpoints"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Create and return auth token"""
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Workout User",
                "email": "workouts@example.com",
                "password": "Pass123!"
            }
        )
        return reg.json()["access_token"]
    
    def test_create_workout(self, client, auth_token):
        """Test creating a workout"""
        response = client.post(
            "/api/v1/workouts/create",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "sport_type": "running",
                "start_time": "2025-01-15T10:00:00",
                "duration_seconds": 1800,
                "distance_meters": 5000,
                "avg_pace": 360,
                "avg_heart_rate": 145,
                "max_heart_rate": 170
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["sport_type"] == "running"
    
    def test_get_workouts(self, client, auth_token):
        """Test getting workouts list"""
        # Create workout
        client.post(
            "/api/v1/workouts/create",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "sport_type": "cycling",
                "start_time": "2025-01-16T14:30:00",
                "duration_seconds": 3600,
                "distance_meters": 40000,
                "avg_pace": 200,
                "avg_heart_rate": 140
            }
        )
        
        # Get list
        response = client.get(
            "/api/v1/workouts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_workout_stats(self, client, auth_token):
        """Test getting workout stats"""
        # Create workout
        client.post(
            "/api/v1/workouts/create",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "sport_type": "running",
                "start_time": "2025-01-17T08:00:00",
                "duration_seconds": 2400,
                "distance_meters": 8000,
                "avg_pace": 300,
                "avg_heart_rate": 150
            }
        )
        
        # Get stats
        response = client.get(
            "/api/v1/workouts/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200


# ============================================================================
# COACH TESTS
# ============================================================================

class TestCoach:
    """Test AI coach endpoints"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Create and return auth token"""
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Coach User",
                "email": "coach@example.com",
                "password": "Pass123!"
            }
        )
        return reg.json()["access_token"]
    
    def test_chat_message(self, client, auth_token):
        """Test sending message to coach"""
        response = client.post(
            "/api/v1/coach/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": "¿Cómo puedo mejorar mi ritmo?"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Response should have message or chat content
        assert "assistant_message" in data or "response" in data or "chat" in data
    
    def test_chat_history(self, client, auth_token):
        """Test getting chat history"""
        # Send message
        client.post(
            "/api/v1/coach/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": "Hola coach"
            }
        )
        
        # Get history
        response = client.get(
            "/api/v1/coach/chat/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# INTEGRATION SCENARIOS
# ============================================================================

class TestIntegration:
    """Test complete user workflows"""
    
    def test_register_create_workout_chat(self, client):
        """Test complete flow: register -> create workout -> chat"""
        # 1. Register
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Flow Test",
                "email": "flow@example.com",
                "password": "Pass123!"
            }
        )
        assert reg.status_code in [200, 201]
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create workout
        workout = client.post(
            "/api/v1/workouts/create",
            headers=headers,
            json={
                "sport_type": "running",
                "start_time": "2025-01-18T06:00:00",
                "duration_seconds": 3600,
                "distance_meters": 10000,
                "avg_pace": 360,
                "avg_heart_rate": 150
            }
        )
        assert workout.status_code in [200, 201]
        
        # 3. Chat about workout
        chat = client.post(
            "/api/v1/coach/chat",
            headers=headers,
            json={
                "message": "¿Cómo fue mi carrera?",
                "include_workout_context": True
            }
        )
        assert chat.status_code == 200
    
    def test_multiple_users_isolation(self, client):
        """Test user data isolation"""
        # User 1
        reg1 = client.post(
            "/api/v1/auth/register",
            json={
                "name": "User 1",
                "email": "user1@example.com",
                "password": "Pass123!"
            }
        )
        token1 = reg1.json()["access_token"]
        
        # User 2
        reg2 = client.post(
            "/api/v1/auth/register",
            json={
                "name": "User 2",
                "email": "user2@example.com",
                "password": "Pass456!"
            }
        )
        token2 = reg2.json()["access_token"]
        
        # User 1 creates workout
        client.post(
            "/api/v1/workouts/create",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "sport_type": "running",
                "start_time": "2025-01-19T10:00:00",
                "duration_seconds": 1800,
                "distance_meters": 5000,
                "avg_pace": 360,
                "avg_heart_rate": 140
            }
        )
        
        # User 2 gets workouts (should be empty or not see User 1's)
        workouts_u2 = client.get(
            "/api/v1/workouts",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert workouts_u2.status_code == 200
        data_u2 = workouts_u2.json()
        # User 2 should only see their own workouts
        assert len(data_u2) == 0 or all(w.get("user_id") != 1 for w in data_u2 if "user_id" in w)
