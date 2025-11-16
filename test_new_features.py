#!/usr/bin/env python3
"""
Test script for Phase A+B features
Tests all new functionality: Training Plans, Predictions, Strava, Charts
"""

import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"
TEST_TOKEN = None

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name: str, passed: bool, message: str = ""):
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    print(f"{status} {name}")
    if message:
        print(f"  └─ {message}")

def print_section(title: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def test_auth():
    """Test registration and login"""
    global TEST_TOKEN
    
    print_section("1. AUTHENTICATION TESTS")
    
    # Register
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        # Might fail if already exists, that's ok
        registered = response.status_code == 200
        print_test("Register user", True, "Email: " + TEST_EMAIL)
    except Exception as e:
        print_test("Register user", False, str(e))
        return False
    
    # Login
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        login_ok = response.status_code == 200
        if login_ok:
            TEST_TOKEN = response.json().get("access_token")
            print_test("Login user", True, f"Token: {TEST_TOKEN[:20]}...")
        else:
            print_test("Login user", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Login user", False, str(e))
        return False
    
    return True

def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {TEST_TOKEN}"}

def test_training_plans():
    """Test training plans endpoints"""
    print_section("2. TRAINING PLANS TESTS")
    
    if not TEST_TOKEN:
        print_test("Training Plans", False, "No auth token")
        return False
    
    # Generate training plan
    try:
        tomorrow = (datetime.now() + timedelta(days=90)).isoformat()
        plan_data = {
            "goal_type": "race",
            "goal_distance": 5000,
            "goal_time": "20:00",
            "race_date": tomorrow,
            "current_weekly_distance": 40,
            "available_training_days": 5
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/training-plans/generate",
            json=plan_data,
            headers=get_headers()
        )
        
        generate_ok = response.status_code == 200
        plan_id = None
        if generate_ok:
            plan_id = response.json().get("id")
            print_test("Generate training plan", True, f"Plan ID: {plan_id}")
        else:
            print_test("Generate training plan", False, f"Status: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print_test("Generate training plan", False, str(e))
        return False
    
    # Get training plans
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/training-plans/",
            headers=get_headers()
        )
        
        list_ok = response.status_code == 200
        if list_ok:
            plans = response.json()
            print_test("Get training plans", True, f"Found {len(plans)} plan(s)")
        else:
            print_test("Get training plans", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get training plans", False, str(e))
        return False
    
    return generate_ok and list_ok

def test_predictions():
    """Test predictions endpoints"""
    print_section("3. PREDICTIONS TESTS")
    
    if not TEST_TOKEN:
        print_test("Predictions", False, "No auth token")
        return False
    
    # Calculate VDOT
    try:
        vdot_data = {
            "distance": 5000,
            "time_seconds": 1200  # 20 minutes
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/predictions/vdot",
            json=vdot_data,
            headers=get_headers()
        )
        
        vdot_ok = response.status_code == 200
        if vdot_ok:
            result = response.json()
            vdot = result.get("vdot", 0)
            print_test("Calculate VDOT", True, f"VDOT: {vdot:.1f}")
        else:
            print_test("Calculate VDOT", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Calculate VDOT", False, str(e))
        return False
    
    # Predict race times
    try:
        race_data = {
            "distance": 5000,
            "time_seconds": 1200,
            "age": 30,
            "gender": "M"
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/predictions/race-times",
            json=race_data,
            headers=get_headers()
        )
        
        race_ok = response.status_code == 200
        if race_ok:
            result = response.json()
            predictions = result.get("race_predictions", {})
            print_test("Predict race times", True, f"Got {len(predictions)} predictions")
        else:
            print_test("Predict race times", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Predict race times", False, str(e))
        return False
    
    # Get training paces
    try:
        vdot_value = 50.0
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/predictions/training-paces/{vdot_value}",
            headers=get_headers()
        )
        
        paces_ok = response.status_code == 200
        if paces_ok:
            result = response.json()
            paces = result.get("training_paces", {})
            print_test("Get training paces", True, f"Got {len(paces)} pace types")
        else:
            print_test("Get training paces", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get training paces", False, str(e))
        return False
    
    return vdot_ok and race_ok and paces_ok

def test_health_metrics():
    """Test health metrics endpoints"""
    print_section("4. HEALTH METRICS TESTS")
    
    if not TEST_TOKEN:
        print_test("Health Metrics", False, "No auth token")
        return False
    
    # Get health history
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/health/history?days=7",
            headers=get_headers()
        )
        
        history_ok = response.status_code == 200
        if history_ok:
            result = response.json()
            metrics = result.get("metrics", []) if isinstance(result, dict) else result
            print_test("Get health history", True, f"Found {len(metrics)} metric(s)")
            
            # Check metric structure
            if metrics:
                metric = metrics[0]
                has_hrv = "hrv_ms" in metric
                has_sleep = "sleep_duration_minutes" in metric
                print_test("  └─ HRV field", has_hrv)
                print_test("  └─ Sleep field", has_sleep)
        else:
            print_test("Get health history", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get health history", False, str(e))
        return False
    
    return history_ok

def test_strava_integration():
    """Test Strava integration endpoints"""
    print_section("5. STRAVA INTEGRATION TESTS")
    
    if not TEST_TOKEN:
        print_test("Strava", False, "No auth token")
        return False
    
    # Init Strava auth
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/integrations/strava/auth",
            headers=get_headers()
        )
        
        auth_ok = response.status_code == 200
        if auth_ok:
            result = response.json()
            auth_url = result.get("authorization_url", "")
            has_url = len(auth_url) > 0
            print_test("Init Strava auth", True, f"Got OAuth URL: {auth_url[:50]}...")
        else:
            print_test("Init Strava auth", False, f"Status: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print_test("Init Strava auth", False, str(e))
        auth_ok = False
    
    return auth_ok

def test_endpoints_exist():
    """Test that all new endpoints exist"""
    print_section("6. ENDPOINT AVAILABILITY TESTS")
    
    endpoints = [
        ("GET", "/api/v1/training-plans/"),
        ("POST", "/api/v1/training-plans/generate"),
        ("POST", "/api/v1/predictions/vdot"),
        ("POST", "/api/v1/predictions/race-times"),
        ("GET", "/api/v1/predictions/training-paces/50"),
        ("GET", "/api/v1/integrations/strava/auth"),
    ]
    
    all_ok = True
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    headers=get_headers()
                )
            else:
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    json={},
                    headers=get_headers()
                )
            
            # 401 Unauthorized is ok if auth required, means endpoint exists
            # 400 Bad Request is ok if validation required, means endpoint exists
            endpoint_exists = response.status_code in [200, 400, 401, 422]
            print_test(f"{method} {endpoint}", endpoint_exists, f"Status: {response.status_code}")
            all_ok = all_ok and endpoint_exists
        except Exception as e:
            print_test(f"{method} {endpoint}", False, str(e))
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print(f"\n{Colors.YELLOW}🚀 PHASE A+B TESTING SUITE{Colors.RESET}")
    print(f"Testing Backend: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = []
    
    # Run tests
    results.append(("Authentication", test_auth()))
    
    if TEST_TOKEN:
        results.append(("Training Plans", test_training_plans()))
        results.append(("Predictions", test_predictions()))
        results.append(("Health Metrics", test_health_metrics()))
        results.append(("Strava Integration", test_strava_integration()))
        results.append(("Endpoint Availability", test_endpoints_exist()))
    else:
        print("\n⚠️  Skipping remaining tests (no auth token)")
    
    # Summary
    print_section("SUMMARY")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if ok else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Result: {passed}/{total} test groups passed")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.RED}✗ SOME TESTS FAILED{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
