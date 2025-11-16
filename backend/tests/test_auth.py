import pytest
from fastapi.testclient import TestClient


class TestAuthRegister:
    """Tests para el endpoint POST /api/v1/auth/register"""

    def test_register_success(self, test_client: TestClient, test_user_data: dict):
        """✅ Registro exitoso retorna 201 con tokens y usuario."""
        response = test_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Verificar datos del usuario
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["name"] == test_user_data["name"]
        assert "password" not in data["user"]  # No retornar contraseña

    def test_register_duplicate_email(self, test_client: TestClient, test_user_data: dict):
        """❌ Registrar con email duplicado retorna error 400."""
        # Primer registro
        response1 = test_client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201
        
        # Intento de registro con mismo email
        response2 = test_client.post("/api/v1/auth/register", json=test_user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()

    def test_register_missing_email(self, test_client: TestClient, test_user_data: dict):
        """❌ Registro sin email retorna error validación."""
        invalid_data = {
            "name": test_user_data["name"],
            "password": test_user_data["password"],
        }
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error

    def test_register_invalid_email(self, test_client: TestClient, test_user_data: dict):
        """❌ Email inválido retorna error validación."""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "notanemail"
        
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_short_password(self, test_client: TestClient, test_user_data: dict):
        """❌ Contraseña muy corta retorna error."""
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "short"
        
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422


class TestAuthLogin:
    """Tests para el endpoint POST /api/v1/auth/login"""

    def test_login_success(self, test_client: TestClient, registered_user: dict, test_user_data: dict):
        """✅ Login exitoso retorna 200 con tokens."""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user_data["email"]

    def test_login_invalid_email(self, test_client: TestClient):
        """❌ Email no registrado retorna 401."""
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword"},
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_wrong_password(self, test_client: TestClient, registered_user: dict, test_user_data: dict):
        """❌ Contraseña incorrecta retorna 401."""
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_missing_credentials(self, test_client: TestClient):
        """❌ Credenciales incompletas retorna 422."""
        response = test_client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422


class TestAuthRefresh:
    """Tests para el endpoint POST /api/v1/auth/refresh"""

    def test_refresh_token_success(self, test_client: TestClient, registered_user: dict):
        """✅ Refresh token válido retorna nuevo access_token."""
        refresh_token = registered_user["refresh_token"]
        
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        # Verify the tokens are valid JWT strings
        assert len(data["access_token"].split(".")) == 3
        assert len(data["refresh_token"].split(".")) == 3

    def test_refresh_invalid_token(self, test_client: TestClient):
        """❌ Token inválido retorna 401."""
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == 401

    def test_refresh_missing_token(self, test_client: TestClient):
        """❌ Sin token retorna 422."""
        response = test_client.post("/api/v1/auth/refresh", json={})
        assert response.status_code == 422


class TestTokenStructure:
    """Tests para validar estructura de JWT tokens"""

    def test_access_token_format(self, registered_user: dict):
        """✅ Access token tiene formato JWT válido (3 partes)."""
        token = registered_user["access_token"]
        parts = token.split(".")
        assert len(parts) == 3, "JWT debe tener 3 partes separadas por puntos"

    def test_refresh_token_format(self, registered_user: dict):
        """✅ Refresh token tiene formato JWT válido."""
        token = registered_user["refresh_token"]
        parts = token.split(".")
        assert len(parts) == 3, "JWT debe tener 3 partes separadas por puntos"

    def test_different_tokens(self, registered_user: dict):
        """✅ Access y refresh tokens son diferentes."""
        access = registered_user["access_token"]
        refresh = registered_user["refresh_token"]
        assert access != refresh, "Access y refresh tokens no deben ser iguales"


class TestUserData:
    """Tests para validar datos de usuario"""

    def test_user_has_required_fields(self, registered_user: dict):
        """✅ Usuario tiene campos requeridos."""
        user = registered_user["user"]
        
        assert "id" in user
        assert "name" in user
        assert "email" in user
        assert user["id"] is not None
        assert user["name"] != ""
        assert user["email"] != ""

    def test_user_no_password_leaked(self, registered_user: dict):
        """✅ Contraseña NO se retorna en respuesta."""
        user = registered_user["user"]
        assert "password" not in user
        assert "hashed_password" not in user

    def test_multiple_users_different_ids(
        self,
        test_client: TestClient,
        registered_user: dict,
        another_registered_user: dict,
    ):
        """✅ Usuarios diferentes tienen IDs diferentes."""
        user1_id = registered_user["user"]["id"]
        user2_id = another_registered_user["user"]["id"]
        
        assert user1_id != user2_id
