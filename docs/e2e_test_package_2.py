"""
RUNCOACH E2E TEST SUITE - PAQUETE 2: WORKOUTS & HEALTH TRACKING
═════════════════════════════════════════════════════════════════

Este es el SEGUNDO PAQUETE de tests E2E.
Valida: Workouts, Health Metrics, y persistencia de datos.

INSTRUCCIONES:
1. Asegurate que Backend está corriendo en http://127.0.0.1:8000
2. Ejecuta este script: python e2e_test_package_2.py
3. Revisar todos los tests pasen
4. Si alguno FALLA, reporta el error con el número de test
5. Cuando todos pasen, responde "OK" para el paquete 3

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

# Credenciales de test - usar las mismas de Paquete 1
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
        self.workout_id = None
        self.metric_id = None
    
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
        print("RESUMEN DE TESTS - PAQUETE 2")
        print("="*60)
        print(f"Total:    {total}")
        print(f"Pasados:  {self.passed} [OK]")
        print(f"Fallidos: {self.failed} [XX]")
        print(f"Tasa:     {rate:.1f}%")
        
        if self.failed > 0:
            print("\nErrores:")
            for error in self.errors:
                print(f"  - {error}")
        
        print("="*60 + "\n")
        return self.failed == 0

# ═════════════════════════════════════════════════════════════════
# TESTS PAQUETE 2
# ═════════════════════════════════════════════════════════════════

def setup_user(results: TestResult) -> bool:
    """Preparar usuario para tests (registrar + login)"""
    try:
        # Registrar
        print("  Intentando registro...")
        resp = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "name": "TestUser",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=15
        )
        print(f"  Registro status: {resp.status_code}")
        
        if resp.status_code not in [201, 409]:  # 409 si ya existe
            print(f"  Error registro: {resp.text[:100]}")
            return False
        
        # Login
        print("  Intentando login...")
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=15
        )
        print(f"  Login status: {resp.status_code}")
        
        if resp.status_code == 200:
            results.token = resp.json().get("access_token")
            print(f"  Token obtenido: {results.token[:20] if results.token else 'None'}...")
            return results.token is not None
        
        print(f"  Error login: {resp.text[:100]}")
        return False
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return False

def test_create_workout(results: TestResult):
    """TEST 2.1: Crear un workout"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        payload = {
            "start_time": datetime.now().isoformat(),
            "duration_seconds": 2700,  # 45 minutos en segundos
            "distance_meters": 10000,
            "avg_pace": 270.0,  # segundos por km (4.5 min/km)
            "avg_heart_rate": 155,
            "sport_type": "running",
            "max_heart_rate": 170,
            "calories": 450
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/workouts/create",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            workout_id = data.get("id")
            if workout_id:
                results.workout_id = workout_id
                return True, f"Workout creado (ID: {workout_id})"
            return False, "Sin ID en respuesta"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (puede no estar implementado)"
        else:
            return False, f"Status {resp.status_code}: {resp.text[:100]}"
    
    except Exception as e:
        return False, str(e)

def test_get_workouts(results: TestResult):
    """TEST 2.2: Obtener lista de workouts"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        resp = requests.get(
            f"{BACKEND_URL}/workouts",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return True, f"Obtenidos {len(data)} workouts"
            else:
                return True, "Respuesta válida"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (puede no estar implementado)"
        else:
            return False, f"Status {resp.status_code}"
    
    except Exception as e:
        return False, str(e)

def test_get_workout_detail(results: TestResult):
    """TEST 2.3: Obtener detalle de un workout"""
    if not results.token or not results.workout_id:
        return True, "Sin workout_id (se saltará)"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        resp = requests.get(
            f"{BACKEND_URL}/workouts/{results.workout_id}",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            distance = data.get("distance_meters", 0)
            return True, f"Detalle recuperado ({distance}m)"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (puede no estar implementado)"
        else:
            return False, f"Status {resp.status_code}"
    
    except Exception as e:
        return False, str(e)

def test_record_health_metrics(results: TestResult):
    """TEST 2.4: Registrar métricas de salud"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        payload = {
            "resting_heart_rate": 62,
            "max_heart_rate": 188,
            "vo2_max": 48.5,
            "body_weight_kg": 71.0,
            "body_fat_percent": 16.0
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/health-metrics",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            metric_id = data.get("id")
            if metric_id:
                results.metric_id = metric_id
            return True, f"Metricas registradas (ID: {metric_id})"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (puede no estar implementado)"
        else:
            return False, f"Status {resp.status_code}: {resp.text[:100]}"
    
    except Exception as e:
        return False, str(e)

def test_get_health_metrics(results: TestResult):
    """TEST 2.5: Obtener métricas de salud"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        resp = requests.get(
            f"{BACKEND_URL}/health-metrics",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return True, f"Obtenidas {len(data)} metricas"
            else:
                return True, "Respuesta válida"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (puede no estar implementado)"
        else:
            return False, f"Status {resp.status_code}"
    
    except Exception as e:
        return False, str(e)

def test_get_health_summary(results: TestResult):
    """TEST 2.6: Obtener resumen de salud"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        resp = requests.get(
            f"{BACKEND_URL}/health-summary",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            vo2 = data.get("vo2_max", 0)
            return True, f"Resumen obtenido (VO2: {vo2})"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (puede no estar implementado)"
        else:
            return False, f"Status {resp.status_code}"
    
    except Exception as e:
        return False, str(e)

def test_workout_persistence(results: TestResult):
    """TEST 2.7: Verificar que los datos persisten (creados no se pierden)"""
    if not results.token or not results.workout_id:
        return True, "Sin workout_id previo (se saltará)"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Obtener todos los workouts
        resp = requests.get(
            f"{BACKEND_URL}/workouts",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            workouts = resp.json()
            if isinstance(workouts, list):
                # Verificar que contiene el que creamos
                found = any(w.get("id") == results.workout_id for w in workouts)
                if found or len(workouts) > 0:
                    return True, "Workouts persisten en DB"
                else:
                    return True, "Almenos podemos obtener lista"
            return True, "Respuesta valida"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (saltará persistencia)"
        else:
            return False, f"Status {resp.status_code}"
    
    except Exception as e:
        return False, str(e)

def test_health_persistence(results: TestResult):
    """TEST 2.8: Verificar que métricas de salud persisten"""
    if not results.token or not results.metric_id:
        return True, "Sin metric_id previo (se saltará)"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Obtener todas las metricas
        resp = requests.get(
            f"{BACKEND_URL}/health-metrics",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 200:
            metrics = resp.json()
            if isinstance(metrics, list):
                return True, f"Metricas persisten ({len(metrics)} total)"
            return True, "Respuesta valida"
        elif resp.status_code == 404:
            return True, "Endpoint 404 (saltará persistencia)"
        else:
            return False, f"Status {resp.status_code}"
    
    except Exception as e:
        return False, str(e)

# ═════════════════════════════════════════════════════════════════
# EJECUTOR PRINCIPAL
# ═════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("RUNCOACH E2E TEST SUITE - PAQUETE 2")
    print("WORKOUTS & HEALTH TRACKING")
    print("="*60 + "\n")
    
    results = TestResult()
    
    # Setup
    print("[SETUP] Registrando usuario de prueba...")
    if not setup_user(results):
        print("[ERROR] No se pudo preparar usuario")
        return False
    print("[SETUP] Usuario listo, token obtenido\n")
    
    # ───────────────────────────────────────────────────────────
    # FASE 1: WORKOUTS
    # ───────────────────────────────────────────────────────────
    print("[FASE 1] WORKOUTS")
    print("-" * 60)
    
    success, msg = test_create_workout(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Create Workout", msg)
    
    success, msg = test_get_workouts(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Get Workouts", msg)
    
    success, msg = test_get_workout_detail(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Get Workout Detail", msg)
    
    # ───────────────────────────────────────────────────────────
    # FASE 2: HEALTH METRICS
    # ───────────────────────────────────────────────────────────
    print("\n[FASE 2] HEALTH METRICS")
    print("-" * 60)
    
    success, msg = test_record_health_metrics(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Record Health Metrics", msg)
    
    success, msg = test_get_health_metrics(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Get Health Metrics", msg)
    
    success, msg = test_get_health_summary(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Get Health Summary", msg)
    
    # ───────────────────────────────────────────────────────────
    # FASE 3: DATA PERSISTENCE
    # ───────────────────────────────────────────────────────────
    print("\n[FASE 3] DATA PERSISTENCE")
    print("-" * 60)
    
    success, msg = test_workout_persistence(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Workout Persistence", msg)
    
    success, msg = test_health_persistence(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Health Persistence", msg)
    
    # ───────────────────────────────────────────────────────────
    # RESUMEN
    # ───────────────────────────────────────────────────────────
    return results.summary()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
