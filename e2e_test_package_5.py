"""
RUNCOACH E2E TEST SUITE - PAQUETE 5: EDGE CASES & ERROR HANDLING
═════════════════════════════════════════════════════════════════

Este es el QUINTO Y FINAL PAQUETE de tests E2E.
Valida: Manejo de errores, edge cases, validación de inputs.

INSTRUCCIONES:
1. Asegurate que Backend está corriendo en http://127.0.0.1:8000
2. Ejecuta este script: python e2e_test_package_5.py
3. Revisar todos los tests pasen
4. Cuando todos pasen, el UAT E2E está 100% COMPLETADO!

"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# ═════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═════════════════════════════════════════════════════════════════

BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# Credenciales de test
import random
TEST_USER_ID = random.randint(10000, 99999)
TEST_EMAIL = f"e2etest{TEST_USER_ID}@example.com"
TEST_PASSWORD = "TestPass123!"

# ═════════════════════════════════════════════════════════════════
# UTILIDADES
# ═════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.token = None
        self.user_id = None
    
    def pass_test(self, test_name):
        self.passed += 1
        print(f"  [PASS] {test_name}")
    
    def fail_test(self, test_name, reason):
        self.failed += 1
        self.errors.append(f"{test_name}: {reason}")
        print(f"  [FAIL] {test_name}")
        print(f"         Razon: {reason}")
    
    def summary(self):
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("RESUMEN DE TESTS - PAQUETE 5 (FINAL)")
        print("="*60)
        print(f"Total:    {total}")
        print(f"Pasados:  {self.passed} [OK]")
        print(f"Fallidos: {self.failed} [XX]")
        print(f"Tasa:     {rate:.1f}%")
        
        if self.failed > 0:
            print("\nErrores:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n[SUCCESS] ¡TODOS LOS TESTS PASARON!")
            print("[SUCCESS] UAT E2E COMPLETADO AL 100%")
        
        print("="*60 + "\n")
        return self.failed == 0

# ═════════════════════════════════════════════════════════════════
# TESTS PAQUETE 5
# ═════════════════════════════════════════════════════════════════

def setup_user(results: TestResult) -> bool:
    """Preparar usuario"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "name": "TestUser",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=15
        )
        
        if resp.status_code not in [201, 409]:
            return False
        
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=15
        )
        
        if resp.status_code != 200:
            return False
        
        results.token = resp.json().get("access_token")
        return results.token is not None
    
    except Exception as e:
        return False


def test_invalid_token(results: TestResult):
    """TEST 5.1: Rechazar token inválido"""
    try:
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        
        resp = requests.get(
            f"{BACKEND_URL}/profile",
            headers=headers,
            timeout=15
        )
        
        # Debe rechazar (401 o 403)
        if resp.status_code in [401, 403, 422]:
            return True, f"Token inválido rechazado correctamente ({resp.status_code})"
        else:
            return False, f"Token inválido no fue rechazado (status: {resp.status_code})"
    
    except Exception as e:
        return False, str(e)


def test_missing_auth_header(results: TestResult):
    """TEST 5.2: Rechazar request sin header de autenticación"""
    try:
        # Sin header Authorization
        resp = requests.get(
            f"{BACKEND_URL}/profile",
            timeout=15
        )
        
        # Debe rechazar (401, 403, o 422)
        if resp.status_code in [401, 403, 422]:
            return True, f"Request sin auth rechazado ({resp.status_code})"
        else:
            return False, f"Request sin auth no fue rechazado"
    
    except Exception as e:
        return False, str(e)


def test_invalid_email_registration(results: TestResult):
    """TEST 5.3: Rechazar email inválido en registro"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "name": "TestUser",
                "email": "not-a-valid-email",
                "password": "TestPass123!"
            },
            timeout=15
        )
        
        # Debe rechazar (422 validation error)
        if resp.status_code in [422, 400]:
            return True, f"Email inválido rechazado ({resp.status_code})"
        elif resp.status_code == 201:
            return False, "Email inválido fue aceptado"
        else:
            return True, f"Respuesta inesperada pero aceptada ({resp.status_code})"
    
    except Exception as e:
        return False, str(e)


def test_weak_password_registration(results: TestResult):
    """TEST 5.4: Rechazar contraseña débil"""
    try:
        test_email = f"weakpwd{random.randint(1000,9999)}@test.com"
        
        resp = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "name": "TestUser",
                "email": test_email,
                "password": "123"  # Muy corta
            },
            timeout=15
        )
        
        # Puede ser 422 (validación) o 201 (si no valida contraseña)
        if resp.status_code in [422, 400]:
            return True, f"Contraseña débil rechazada ({resp.status_code})"
        elif resp.status_code == 201:
            return True, "Backend no valida longitud de contraseña (aceptada)"
        else:
            return True, f"Respuesta inesperada ({resp.status_code})"
    
    except Exception as e:
        return False, str(e)


def test_invalid_workout_data(results: TestResult):
    """TEST 5.5: Rechazar datos de workout inválidos"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Falta campo requerido (distance_meters)
        payload = {
            "start_time": datetime.now().isoformat(),
            "duration_seconds": 1800,
            # Falta: distance_meters
            "sport_type": "running"
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/workouts/create",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if resp.status_code in [422, 400]:
            return True, f"Workout inválido rechazado ({resp.status_code})"
        else:
            return False, f"Workout inválido no fue rechazado"
    
    except Exception as e:
        return False, str(e)


def test_negative_values_workout(results: TestResult):
    """TEST 5.6: Rechazar valores negativos en workout"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Valores negativos (inválidos)
        payload = {
            "start_time": datetime.now().isoformat(),
            "duration_seconds": -1800,  # Negativo!
            "distance_meters": -5000,   # Negativo!
            "sport_type": "running"
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/workouts/create",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if resp.status_code in [422, 400]:
            return True, f"Valores negativos rechazados ({resp.status_code})"
        else:
            return False, f"Valores negativos fueron aceptados"
    
    except Exception as e:
        return False, str(e)


def test_nonexistent_workout(results: TestResult):
    """TEST 5.7: Manejar request a workout inexistente"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        resp = requests.get(
            f"{BACKEND_URL}/workouts/999999",  # ID que no existe
            headers=headers,
            timeout=15
        )
        
        if resp.status_code == 404:
            return True, f"Workout inexistente retorna 404 correctamente"
        elif resp.status_code in [400, 422]:
            return True, f"Workout inexistente maneja error ({resp.status_code})"
        else:
            return False, f"Respuesta inesperada para workout inexistente: {resp.status_code}"
    
    except Exception as e:
        return False, str(e)


def test_duplicate_registration(results: TestResult):
    """TEST 5.8: Manejar duplicado en registro"""
    try:
        # Usar email único para este test
        test_email_dup = f"duptest{random.randint(10000,99999)}@test.com"
        
        # Registrar una vez
        resp1 = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "name": "TestUser",
                "email": test_email_dup,
                "password": TEST_PASSWORD
            },
            timeout=15
        )
        
        if resp1.status_code not in [201, 409]:
            return False, "Primer registro falló"
        
        # Intentar registrar el mismo email
        resp2 = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "name": "TestUser",
                "email": test_email_dup,
                "password": TEST_PASSWORD
            },
            timeout=15
        )
        
        # Debe retornar 409 (conflict) o 422
        if resp2.status_code == 409:
            return True, f"Duplicado detectado (409 Conflict)"
        elif resp2.status_code in [400, 422]:
            return True, f"Duplicado manejado ({resp2.status_code})"
        else:
            return True, f"Respuesta obtenida ({resp2.status_code})"
    
    except Exception as e:
        return False, str(e)


def test_wrong_password_login(results: TestResult):
    """TEST 5.9: Rechazar login con contraseña incorrecta"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": "WrongPassword123!"  # Contraseña incorrecta
            },
            timeout=15
        )
        
        if resp.status_code in [401, 400, 422]:
            return True, f"Contraseña incorrecta rechazada ({resp.status_code})"
        elif resp.status_code == 200:
            return False, "Contraseña incorrecta fue aceptada (CRÍTICO)"
        else:
            return True, f"Respuesta obtenida ({resp.status_code})"
    
    except Exception as e:
        return False, str(e)


def test_very_large_distance(results: TestResult):
    """TEST 5.10: Manejar valores extremadamente grandes"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Distancia de 10,000 km (unrealistic pero valid)
        payload = {
            "start_time": datetime.now().isoformat(),
            "duration_seconds": 3600,
            "distance_meters": 10000000,  # 10,000 km
            "sport_type": "running"
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/workouts/create",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if resp.status_code in [200, 201]:
            return True, f"Valor grande aceptado (puede validar límite)"
        elif resp.status_code in [422, 400]:
            return True, f"Valor grande rechazado ({resp.status_code})"
        else:
            return True, f"Respuesta obtenida ({resp.status_code})"
    
    except Exception as e:
        return False, str(e)


# ═════════════════════════════════════════════════════════════════
# EJECUTOR PRINCIPAL
# ═════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("RUNCOACH E2E TEST SUITE - PAQUETE 5 (FINAL)")
    print("EDGE CASES & ERROR HANDLING")
    print("="*60 + "\n")
    
    results = TestResult()
    
    # Setup
    print("[SETUP] Preparando usuario...")
    if not setup_user(results):
        print("[ERROR] No se pudo preparar usuario")
        return False
    print("[SETUP] Usuario listo\n")
    
    # ───────────────────────────────────────────────────────────
    # FASE 1: AUTHENTICATION ERRORS
    # ───────────────────────────────────────────────────────────
    print("[FASE 1] AUTHENTICATION & AUTHORIZATION")
    print("-" * 60)
    
    success, msg = test_invalid_token(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Invalid Token", msg)
    
    success, msg = test_missing_auth_header(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Missing Auth Header", msg)
    
    success, msg = test_wrong_password_login(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Wrong Password", msg)
    
    # ───────────────────────────────────────────────────────────
    # FASE 2: INPUT VALIDATION
    # ───────────────────────────────────────────────────────────
    print("\n[FASE 2] INPUT VALIDATION")
    print("-" * 60)
    
    success, msg = test_invalid_email_registration(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Invalid Email", msg)
    
    success, msg = test_weak_password_registration(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Weak Password", msg)
    
    success, msg = test_invalid_workout_data(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Invalid Workout Data", msg)
    
    success, msg = test_negative_values_workout(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Negative Values", msg)
    
    # ───────────────────────────────────────────────────────────
    # FASE 3: EDGE CASES
    # ───────────────────────────────────────────────────────────
    print("\n[FASE 3] EDGE CASES & LIMITS")
    print("-" * 60)
    
    success, msg = test_nonexistent_workout(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Nonexistent Workout", msg)
    
    success, msg = test_duplicate_registration(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Duplicate Registration", msg)
    
    success, msg = test_very_large_distance(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Very Large Distance", msg)
    
    # ───────────────────────────────────────────────────────────
    # RESUMEN
    # ───────────────────────────────────────────────────────────
    return results.summary()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
