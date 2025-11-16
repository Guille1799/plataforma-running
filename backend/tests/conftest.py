import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from fastapi.testclient import TestClient


# ============================================================================
# FIXTURES - Configuración de test database y client
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Session:
    """
    Crea una base de datos SQLite en memoria para cada test.
    Se elimina después de cada test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="function")
def test_client(test_db: Session) -> TestClient:
    """
    Crea un TestClient de FastAPI que usa la test database.
    """
    def override_get_db():
        yield test_db
    
    from app.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============================================================================
# FIXTURES - Usuarios de prueba
# ============================================================================

@pytest.fixture
def test_user_data() -> dict:
    """Datos válidos de usuario para tests."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def another_user_data() -> dict:
    """Otro usuario para tests de múltiples usuarios."""
    return {
        "name": "Another User",
        "email": "another@example.com",
        "password": "anotherpassword456",
    }


# ============================================================================
# FIXTURES - Usuarios ya creados en la BD
# ============================================================================

@pytest.fixture
def registered_user(test_client: TestClient, test_user_data: dict):
    """Crea un usuario registrado en la BD y retorna sus datos + tokens."""
    response = test_client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def another_registered_user(test_client: TestClient, another_user_data: dict):
    """Crea otro usuario registrado."""
    response = test_client.post("/api/v1/auth/register", json=another_user_data)
    assert response.status_code == 201
    return response.json()
