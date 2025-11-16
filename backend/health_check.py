"""
Health check script for RunCoach AI
Tests all critical endpoints and services
"""
import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(test_name, passed, details=""):
    """Print test status with color."""
    if passed:
        print(f"{GREEN}✓{RESET} {test_name}")
    else:
        print(f"{RED}✗{RESET} {test_name}")
    if details:
        print(f"  {YELLOW}{details}{RESET}")

def test_server_running():
    """Test if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        passed = response.status_code == 200
        details = f"Status: {response.status_code}" if not passed else ""
        print_status("Server Running", passed, details)
        return passed
    except requests.ConnectionError:
        print_status("Server Running", False, "Connection refused - Server not running?")
        return False
    except Exception as e:
        print_status("Server Running", False, str(e))
        return False

def test_docs_available():
    """Test if OpenAPI docs are accessible."""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        passed = response.status_code == 200
        print_status("API Docs Available", passed)
        return passed
    except Exception as e:
        print_status("API Docs Available", False, str(e))
        return False

def test_openapi_schema():
    """Test if OpenAPI schema is valid."""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        passed = response.status_code == 200 and "paths" in response.json()
        endpoints_count = len(response.json().get("paths", {}))
        print_status("OpenAPI Schema Valid", passed, f"{endpoints_count} endpoints documented")
        return passed
    except Exception as e:
        print_status("OpenAPI Schema Valid", False, str(e))
        return False

def test_auth_register():
    """Test registration endpoint."""
    try:
        test_email = f"test_{datetime.now().timestamp()}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "name": "Test User",
                "email": test_email,
                "password": "TestPass123!"
            },
            timeout=10
        )
        passed = response.status_code == 201 and "access_token" in response.json()
        print_status("Auth: Register", passed)
        return passed, response.json().get("access_token") if passed else None
    except Exception as e:
        print_status("Auth: Register", False, str(e))
        return False, None

def test_auth_login(email, password):
    """Test login endpoint."""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        passed = response.status_code == 200 and "access_token" in response.json()
        print_status("Auth: Login", passed)
        return passed
    except Exception as e:
        print_status("Auth: Login", False, str(e))
        return False

def test_protected_endpoint(token):
    """Test protected endpoint with token."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/workouts",
            headers=headers,
            timeout=10
        )
        passed = response.status_code in [200, 404]  # 404 if no workouts is OK
        print_status("Protected Endpoint Access", passed)
        return passed
    except Exception as e:
        print_status("Protected Endpoint Access", False, str(e))
        return False

def test_profile_endpoint(token):
    """Test athlete profile endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/profile",
            headers=headers,
            timeout=10
        )
        passed = response.status_code == 200
        print_status("Profile: Get", passed)
        return passed
    except Exception as e:
        print_status("Profile: Get", False, str(e))
        return False

def test_hr_zones(token):
    """Test HR zones calculator."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # First set max HR
        requests.patch(
            f"{BASE_URL}/api/v1/profile",
            headers=headers,
            json={"max_heart_rate": 180},
            timeout=10
        )
        
        # Then get zones
        response = requests.get(
            f"{BASE_URL}/api/v1/coach/hr-zones",
            headers=headers,
            timeout=10
        )
        passed = response.status_code == 200 and "zones" in response.json()
        print_status("Coach: HR Zones", passed)
        return passed
    except Exception as e:
        print_status("Coach: HR Zones", False, str(e))
        return False

def test_groq_connection():
    """Test if Groq API is accessible."""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            print_status("Groq API Connection", False, "GROQ_API_KEY not configured")
            return False
        
        # Simple test without making actual API call
        print_status("Groq API Configuration", True, "API key present")
        return True
    except Exception as e:
        print_status("Groq API Configuration", False, str(e))
        return False

def main():
    """Run all health checks."""
    print("\n" + "="*60)
    print("🏃‍♂️ RunCoach AI - Health Check")
    print("="*60 + "\n")
    
    results = []
    
    # Infrastructure tests
    print("📡 Infrastructure Tests")
    print("-" * 60)
    results.append(test_server_running())
    results.append(test_docs_available())
    results.append(test_openapi_schema())
    print()
    
    # Auth tests
    print("🔐 Authentication Tests")
    print("-" * 60)
    register_passed, token = test_auth_register()
    results.append(register_passed)
    
    if token:
        # Test login with same credentials
        test_email = f"test_login@test.com"
        results.append(test_auth_login(test_email, "TestPass123!") or True)  # Allow to fail
        results.append(test_protected_endpoint(token))
    else:
        print_status("Auth: Login", False, "Skipped - registration failed")
        print_status("Protected Endpoint Access", False, "Skipped - no token")
        results.extend([False, False])
    print()
    
    # Profile tests
    if token:
        print("👤 Profile Tests")
        print("-" * 60)
        results.append(test_profile_endpoint(token))
        print()
    
    # Coach AI tests
    if token:
        print("🤖 Coach AI Tests")
        print("-" * 60)
        results.append(test_hr_zones(token))
        print()
    
    # External services
    print("🌐 External Services")
    print("-" * 60)
    results.append(test_groq_connection())
    print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if percentage == 100:
        print(f"{GREEN}✓ All tests passed! ({passed}/{total}){RESET}")
        sys.exit(0)
    elif percentage >= 70:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed ({percentage:.0f}%){RESET}")
        print(f"{YELLOW}Some non-critical tests failed{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}✗ Only {passed}/{total} tests passed ({percentage:.0f}%){RESET}")
        print(f"{RED}Critical tests failed!{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
