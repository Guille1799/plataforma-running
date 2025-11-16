"""
test_utils.py - Utilidades compartidas para tests
"""
from typing import Dict, Any
from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str, name: str = "Test User", password: str = "password123") -> Dict[str, Any]:
    """
    Helper function para registrar un usuario rápidamente.
    
    Args:
        client: TestClient de FastAPI
        email: Email del usuario
        name: Nombre del usuario (default: "Test User")
        password: Contraseña (default: "password123")
    
    Returns:
        Response data con tokens y usuario
    """
    data = {
        "name": name,
        "email": email,
        "password": password,
    }
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 201, f"Failed to register user: {response.text}"
    return response.json()


def login_user(client: TestClient, email: str, password: str) -> Dict[str, Any]:
    """
    Helper function para hacer login.
    
    Args:
        client: TestClient de FastAPI
        email: Email del usuario
        password: Contraseña
    
    Returns:
        Response data con tokens y usuario
    """
    data = {
        "email": email,
        "password": password,
    }
    response = client.post("/api/v1/auth/login", json=data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()


def get_auth_headers(access_token: str) -> Dict[str, str]:
    """
    Retorna headers con Bearer token para requests autenticados.
    
    Args:
        access_token: JWT access token
    
    Returns:
        Dict con header Authorization
    """
    return {"Authorization": f"Bearer {access_token}"}
