#!/usr/bin/env python3
import requests
import json

BASE = "http://127.0.0.1:8000"

print("=== Testing API Endpoints ===\n")

# Login first
print("1. Login...")
resp = requests.post(f"{BASE}/auth/login", json={
    "email": "guillermomartindeoliva@gmail.com",
    "password": "password123"
})

print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    token = data.get("access_token")
    print(f"✅ Token received: {token[:20]}..." if token else "❌ No token")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Health today
    print("\n2. GET /api/v1/health/today")
    resp = requests.get(f"{BASE}/api/v1/health/today", headers=headers)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Data received: {str(data)[:100]}...")
    else:
        print(f"   ❌ Error: {resp.text[:150]}")
    
    # Test 2: Readiness
    print("\n3. GET /api/v1/health/readiness")
    resp = requests.get(f"{BASE}/api/v1/health/readiness", headers=headers)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Score: {data.get('score')}, Confidence: {data.get('confidence')}")
    else:
        print(f"   ❌ Error: {resp.text[:150]}")
    
    # Test 3: Workouts
    print("\n4. GET /api/v1/workouts")
    resp = requests.get(f"{BASE}/api/v1/workouts?skip=0&limit=3", headers=headers)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        count = len(data.get('workouts', []))
        print(f"   ✅ Workouts count: {count}")
        if count > 0:
            w = data['workouts'][0]
            print(f"      First: {w.get('sport_type')} - {w.get('distance_meters')}m")
    else:
        print(f"   ❌ Error: {resp.text[:150]}")

else:
    print(f"❌ Login failed: {resp.text}")
