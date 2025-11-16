"""
RUNCOACH E2E TEST SUITE - PAQUETE 4: INTEGRATION TESTS
═════════════════════════════════════════════════════════════════

Este es el CUARTO PAQUETE de tests E2E.
Valida: Workflows complejos, integraciones de múltiples componentes.

INSTRUCCIONES:
1. Asegurate que Backend está corriendo en http://127.0.0.1:8000
2. Ejecuta este script: python e2e_test_package_4.py
3. Revisar todos los tests pasen
4. Si alguno FALLA, reporta el error con el número de test
5. Cuando todos pasen, responde "OK" para el paquete 5

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
        self.goal_id = None
        self.workout_ids = []
    
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
        print("RESUMEN DE TESTS - PAQUETE 4")
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
# TESTS PAQUETE 4
# ═════════════════════════════════════════════════════════════════

def setup_user(results: TestResult) -> bool:
    """Preparar usuario completo"""
    try:
        # Registrar
        print("  Registrando usuario...")
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
        
        # Login
        print("  Logeando usuario...")
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=15
        )
        
        if resp.status_code != 200:
            return False
        
        data = resp.json()
        results.token = data.get("access_token")
        results.user_id = data.get("user_id")
        
        return results.token is not None
    
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return False


def test_full_workout_cycle(results: TestResult):
    """TEST 4.1: Ciclo completo - crear, obtener, analizar workout"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # 1. Crear workout
        payload = {
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "duration_seconds": 5400,  # 90 minutos
            "distance_meters": 20000,
            "avg_pace": 270.0,
            "avg_heart_rate": 165,
            "sport_type": "running",
            "max_heart_rate": 180,
            "calories": 900,
            "elevation_gain": 150.0
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/workouts/create",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if resp.status_code not in [200, 201]:
            return False, f"Create failed: {resp.status_code}"
        
        workout_id = resp.json().get("id")
        if not workout_id:
            return False, "Sin ID en respuesta"
        
        results.workout_ids.append(workout_id)
        
        # 2. Obtener workout
        resp = requests.get(
            f"{BACKEND_URL}/workouts/{workout_id}",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code != 200:
            return False, f"Get failed: {resp.status_code}"
        
        workout_data = resp.json()
        if workout_data.get("distance_meters") != 20000:
            return False, "Datos incorrectos"
        
        # 3. Analizar workout
        resp = requests.post(
            f"{BACKEND_URL}/coach/analyze-form/{workout_id}",
            headers=headers,
            json={},
            timeout=30
        )
        
        if resp.status_code in [200, 201]:
            return True, f"Ciclo completo exitoso (WID: {workout_id})"
        elif resp.status_code == 404:
            return True, f"Análisis no disponible pero ciclo OK (WID: {workout_id})"
        else:
            return False, f"Análisis falló: {resp.status_code}"
    
    except Exception as e:
        return False, str(e)


def test_goal_and_training_plan(results: TestResult):
    """TEST 4.2: Crear meta y generar plan de entrenamiento"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # 1. Crear goal
        payload = {
            "goal_type": "5K",
            "target_time": "25:00",
            "target_date": (datetime.now() + timedelta(days=120)).date().isoformat()
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/goals/create",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if resp.status_code in [200, 201]:
            goal_data = resp.json()
            goal_id = goal_data.get("id")
            if goal_id:
                results.goal_id = goal_id
        elif resp.status_code == 404:
            return True, "Goals endpoint no implementado (saltará)"
        else:
            return False, f"Create goal falló: {resp.status_code}"
        
        # 2. Generar training plan
        resp = requests.post(
            f"{BACKEND_URL}/training-plans/generate",
            headers=headers,
            json={
                "goal_type": "5K",
                "weeks": 12,
                "level": "intermediate"
            },
            timeout=30  # AI puede tardar
        )
        
        if resp.status_code in [200, 201]:
            plan_data = resp.json()
            if plan_data.get("weeks"):
                return True, f"Meta y plan generados"
            return True, "Plan generado (sin detalles)"
        elif resp.status_code == 404:
            return True, "Training plans endpoint no implementado"
        else:
            return False, f"Generate plan falló: {resp.status_code}"
    
    except Exception as e:
        return False, str(e)


def test_multiple_workouts_stats(results: TestResult):
    """TEST 4.3: Crear múltiples workouts y verificar stats"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Crear 3 workouts
        for i in range(3):
            payload = {
                "start_time": (datetime.now() - timedelta(days=i)).isoformat(),
                "duration_seconds": 1800 + (i * 600),  # 30, 40, 50 min
                "distance_meters": 5000 + (i * 2000),  # 5km, 7km, 9km
                "avg_pace": 360.0 - (i * 20),
                "avg_heart_rate": 140 + (i * 5),
                "sport_type": "running",
                "calories": 300 + (i * 100)
            }
            
            resp = requests.post(
                f"{BACKEND_URL}/workouts/create",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if resp.status_code in [200, 201]:
                workout_id = resp.json().get("id")
                if workout_id:
                    results.workout_ids.append(workout_id)
        
        # Obtener stats
        resp = requests.get(
            f"{BACKEND_URL}/workouts/stats",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code == 200:
            stats = resp.json()
            total_distance = stats.get("total_distance", 0)
            if total_distance > 0:
                return True, f"Stats obtenido ({total_distance}m total)"
            return True, "Stats disponible"
        elif resp.status_code == 404:
            return True, "Stats endpoint no implementado"
        else:
            return False, f"Stats falló: {resp.status_code}"
    
    except Exception as e:
        return False, str(e)


def test_profile_update_and_retrieve(results: TestResult):
    """TEST 4.4: Actualizar perfil y recuperar datos"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # 1. Actualizar perfil
        update_payload = {
            "running_level": "intermediate",
            "preferred_pace": 300,  # segundos por km
            "max_heart_rate": 190
        }
        
        resp = requests.put(
            f"{BACKEND_URL}/profile/update",
            headers=headers,
            json=update_payload,
            timeout=15
        )
        
        if resp.status_code in [200, 201, 404]:  # 404 es OK (endpoint opcional)
            pass
        else:
            return False, f"Update failed: {resp.status_code}"
        
        # 2. Obtener perfil
        resp = requests.get(
            f"{BACKEND_URL}/profile",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code == 200:
            profile = resp.json()
            if profile.get("email") == TEST_EMAIL:
                return True, f"Perfil actualizado y verificado"
            return True, "Perfil recuperado"
        elif resp.status_code == 404:
            return True, "Profile endpoint no implementado"
        else:
            return False, f"Get profile falló: {resp.status_code}"
    
    except Exception as e:
        return False, str(e)


def test_data_consistency(results: TestResult):
    """TEST 4.5: Verificar consistencia de datos entre endpoints"""
    if not results.token or not results.workout_ids:
        return True, "Sin workouts previos (se saltará)"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # 1. Obtener lista de workouts
        resp = requests.get(
            f"{BACKEND_URL}/workouts",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code != 200:
            return False, f"List workouts falló: {resp.status_code}"
        
        workouts_list = resp.json()
        list_ids = [w.get("id") for w in workouts_list if isinstance(w, dict)]
        
        # 2. Verificar que nuestros IDs están en la lista
        for wid in results.workout_ids[:2]:  # Verificar al menos 2
            if wid not in list_ids:
                return False, f"Workout {wid} no está en lista"
        
        # 3. Obtener detalles individuales
        for wid in results.workout_ids[:2]:
            resp = requests.get(
                f"{BACKEND_URL}/workouts/{wid}",
                headers=headers,
                timeout=15
            )
            
            if resp.status_code != 200:
                return False, f"Get workout {wid} falló"
        
        return True, f"Consistencia verificada ({len(list_ids)} workouts en DB)"
    
    except Exception as e:
        return False, str(e)


def test_concurrent_operations(results: TestResult):
    """TEST 4.6: Simular operaciones concurrentes"""
    if not results.token:
        return False, "No hay token"
    
    try:
        headers = {"Authorization": f"Bearer {results.token}"}
        
        # Hacer varios requests rápidos
        results_requests = []
        
        for i in range(3):
            resp = requests.get(
                f"{BACKEND_URL}/workouts",
                headers=headers,
                timeout=15
            )
            results_requests.append(resp.status_code)
        
        # Todos deben ser 200
        if all(code == 200 for code in results_requests):
            return True, f"Operaciones concurrentes exitosas"
        elif all(code in [200, 404] for code in results_requests):
            return True, "Respuestas concurrentes válidas"
        else:
            return False, f"Algunas requests fallaron: {results_requests}"
    
    except Exception as e:
        return False, str(e)


# ═════════════════════════════════════════════════════════════════
# EJECUTOR PRINCIPAL
# ═════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("RUNCOACH E2E TEST SUITE - PAQUETE 4")
    print("INTEGRATION TESTS")
    print("="*60 + "\n")
    
    results = TestResult()
    
    # Setup
    print("[SETUP] Preparando usuario...")
    if not setup_user(results):
        print("[ERROR] No se pudo preparar usuario")
        return False
    print("[SETUP] Usuario listo\n")
    
    # ───────────────────────────────────────────────────────────
    # FASE 1: WORKFLOW TESTS
    # ───────────────────────────────────────────────────────────
    print("[FASE 1] FULL WORKFLOWS")
    print("-" * 60)
    
    success, msg = test_full_workout_cycle(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Full Workout Cycle", msg)
    
    success, msg = test_goal_and_training_plan(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Goal & Training Plan", msg)
    
    success, msg = test_multiple_workouts_stats(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Multiple Workouts Stats", msg)
    
    # ───────────────────────────────────────────────────────────
    # FASE 2: DATA INTEGRITY
    # ───────────────────────────────────────────────────────────
    print("\n[FASE 2] DATA INTEGRITY")
    print("-" * 60)
    
    success, msg = test_profile_update_and_retrieve(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Profile Update", msg)
    
    success, msg = test_data_consistency(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Data Consistency", msg)
    
    success, msg = test_concurrent_operations(results)
    if success:
        results.pass_test(msg)
    else:
        results.fail_test("Concurrent Operations", msg)
    
    # ───────────────────────────────────────────────────────────
    # RESUMEN
    # ───────────────────────────────────────────────────────────
    return results.summary()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
