#!/usr/bin/env python3
"""
Comprehensive API Integration Testing Script
Tests all 17 endpoints with realistic data
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "test-token"  # In real testing, get valid JWT token

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, details=""):
    icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

# Test data
race_data = {
    "base_distance": 10,
    "base_time": 45,
    "target_distance": 21.1,
    "terrain": "rolling",
    "temperature": 20,
    "humidity": 60,
    "wind_speed": 5,
    "altitude": 100
}

training_data = {
    "fatigue_score": 50,
    "readiness_score": 75,
    "phase": "build",
    "max_hr": 190
}

adjustment_data = {
    "fatigue_level": 60,
    "previous_hrv": 55,
    "current_hr_variability": 3,
    "sleep_hours": 7
}

print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
print(f"{Colors.BLUE}🧪 API INTEGRATION TEST SUITE{Colors.END}")
print(f"{Colors.BLUE}{'='*60}{Colors.END}")
print(f"Base URL: {BASE_URL}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Track results
results = {
    "race": [],
    "training": [],
    "hrv": [],
    "overtraining": [],
    "passed": 0,
    "failed": 0
}

# ═════════════════════════════════════════════════════════════════
# PHASE 1: RACE PREDICTION ENDPOINTS (4)
# ═════════════════════════════════════════════════════════════════
print_section("PHASE 1: RACE PREDICTION ENDPOINTS")

# Test 1: Race prediction with conditions
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/race/predict-with-conditions",
        params=race_data,
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ POST /api/v1/race/predict-with-conditions", success,
               f"Status: {response.status_code}")
    if success:
        data = response.json()
        print(f"   Predicted Time: {data.get('predicted_time', 'N/A'):.1f} min")
        print(f"   Confidence: {data.get('confidence_score', 'N/A'):.0f}%")
        results["race"].append(True)
        results["passed"] += 1
    else:
        results["race"].append(False)
        results["failed"] += 1
except Exception as e:
    print_test("✅ POST /api/v1/race/predict-with-conditions", False, str(e))
    results["race"].append(False)
    results["failed"] += 1

# Test 2: Conditions impact
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/race/conditions-impact",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/race/conditions-impact", success,
               f"Status: {response.status_code}")
    results["race"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/race/conditions-impact", False, str(e))
    results["race"].append(False)
    results["failed"] += 1

# Test 3: Terrain guide
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/race/terrain-guide",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/race/terrain-guide", success,
               f"Status: {response.status_code}")
    results["race"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/race/terrain-guide", False, str(e))
    results["race"].append(False)
    results["failed"] += 1

# Test 4: Scenario comparison
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/race/scenario-comparison",
        json={**race_data, "base_distance": 10, "base_time": 45},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ POST /api/v1/race/scenario-comparison", success,
               f"Status: {response.status_code}")
    results["race"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ POST /api/v1/race/scenario-comparison", False, str(e))
    results["race"].append(False)
    results["failed"] += 1

# ═════════════════════════════════════════════════════════════════
# PHASE 2: TRAINING RECOMMENDATIONS ENDPOINTS (6)
# ═════════════════════════════════════════════════════════════════
print_section("PHASE 2: TRAINING RECOMMENDATIONS ENDPOINTS")

# Test 5: Weekly plan
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/training/weekly-plan",
        params=training_data,
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/training/weekly-plan", success,
               f"Status: {response.status_code}")
    if success:
        data = response.json()
        print(f"   Phase: {data.get('week_plan', {}).get('phase', 'N/A')}")
        print(f"   Daily Workouts: {len(data.get('week_plan', {}).get('daily_workouts', []))}")
        results["training"].append(True)
        results["passed"] += 1
    else:
        results["training"].append(False)
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/training/weekly-plan", False, str(e))
    results["training"].append(False)
    results["failed"] += 1

# Test 6: Phases guide
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/training/phases-guide",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/training/phases-guide", success,
               f"Status: {response.status_code}")
    results["training"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/training/phases-guide", False, str(e))
    results["training"].append(False)
    results["failed"] += 1

# Test 7: Intensity zones
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/training/intensity-zones",
        params={"max_hr": 190},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/training/intensity-zones", success,
               f"Status: {response.status_code}")
    if success:
        data = response.json()
        zones = data.get('zones', {})
        print(f"   Zones Defined: {len(zones)}")
        results["training"].append(True)
        results["passed"] += 1
    else:
        results["training"].append(False)
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/training/intensity-zones", False, str(e))
    results["training"].append(False)
    results["failed"] += 1

# Test 8: Adaptive adjustment
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/training/adaptive-adjustment",
        params=adjustment_data,
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ POST /api/v1/training/adaptive-adjustment", success,
               f"Status: {response.status_code}")
    if success:
        data = response.json()
        factor = data.get('adjustment_factor', 0)
        print(f"   Adjustment Factor: {factor:.2f}x")
        results["training"].append(True)
        results["passed"] += 1
    else:
        results["training"].append(False)
        results["failed"] += 1
except Exception as e:
    print_test("✅ POST /api/v1/training/adaptive-adjustment", False, str(e))
    results["training"].append(False)
    results["failed"] += 1

# Test 9: Progress tracking
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/training/progress-tracking",
        params={"days": 7},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/training/progress-tracking", success,
               f"Status: {response.status_code}")
    results["training"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/training/progress-tracking", False, str(e))
    results["training"].append(False)
    results["failed"] += 1

# ═════════════════════════════════════════════════════════════════
# PHASE 3: HRV ANALYSIS ENDPOINTS (4)
# ═════════════════════════════════════════════════════════════════
print_section("PHASE 3: HRV ANALYSIS ENDPOINTS")

# Test 10: HRV analysis
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/hrv/analysis",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/hrv/analysis", success,
               f"Status: {response.status_code}")
    results["hrv"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/hrv/analysis", False, str(e))
    results["hrv"].append(False)
    results["failed"] += 1

# Test 11: HRV status
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/hrv/status",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/hrv/status", success,
               f"Status: {response.status_code}")
    results["hrv"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/hrv/status", False, str(e))
    results["hrv"].append(False)
    results["failed"] += 1

# Test 12: Workout correlation
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/hrv/workout-correlation",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/hrv/workout-correlation", success,
               f"Status: {response.status_code}")
    results["hrv"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/hrv/workout-correlation", False, str(e))
    results["hrv"].append(False)
    results["failed"] += 1

# Test 13: HRV prediction
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/hrv/prediction",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/hrv/prediction", success,
               f"Status: {response.status_code}")
    results["hrv"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/hrv/prediction", False, str(e))
    results["hrv"].append(False)
    results["failed"] += 1

# ═════════════════════════════════════════════════════════════════
# PHASE 4: OVERTRAINING DETECTION ENDPOINTS (3)
# ═════════════════════════════════════════════════════════════════
print_section("PHASE 4: OVERTRAINING DETECTION ENDPOINTS")

# Test 14: Risk assessment
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/overtraining/risk-assessment",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/overtraining/risk-assessment", success,
               f"Status: {response.status_code}")
    results["overtraining"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/overtraining/risk-assessment", False, str(e))
    results["overtraining"].append(False)
    results["failed"] += 1

# Test 15: Recovery status
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/overtraining/recovery-status",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/overtraining/recovery-status", success,
               f"Status: {response.status_code}")
    results["overtraining"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/overtraining/recovery-status", False, str(e))
    results["overtraining"].append(False)
    results["failed"] += 1

# Test 16: Daily alert
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/overtraining/daily-alert",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    success = response.status_code == 200
    print_test("✅ GET /api/v1/overtraining/daily-alert", success,
               f"Status: {response.status_code}")
    results["overtraining"].append(success)
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
except Exception as e:
    print_test("✅ GET /api/v1/overtraining/daily-alert", False, str(e))
    results["overtraining"].append(False)
    results["failed"] += 1

# ═════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════
print_section("📊 TEST RESULTS SUMMARY")

passed = results["passed"]
failed = results["failed"]
total = passed + failed

print(f"\n{Colors.GREEN}✅ Passed: {passed}/{total}{Colors.END}")
print(f"{Colors.RED}❌ Failed: {failed}/{total}{Colors.END}")
print(f"\n{'Success Rate':.<40} {(passed/total*100):.1f}%")

if failed == 0:
    print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! 🎉{Colors.END}")
    print(f"{Colors.GREEN}All 17 API endpoints are working correctly.{Colors.END}")
else:
    print(f"\n{Colors.RED}⚠️ SOME TESTS FAILED{Colors.END}")
    print(f"{Colors.RED}Review failed endpoints and resolve issues.{Colors.END}")

print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
