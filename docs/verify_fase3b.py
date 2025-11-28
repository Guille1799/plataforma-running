#!/usr/bin/env python3
"""
Fase 3B Verification Script
Verifica que todos los componentes están funcionando
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzMzMDAwMDAwfQ.test"  # Dummy token for testing
}

def test_get_devices():
    """Test GET devices endpoint"""
    print("\n📋 Testing GET /profile/integrations...")
    try:
        response = requests.get(f"{BASE_URL}/profile/integrations", headers=HEADERS)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Devices: {len(data.get('devices', []))} encontrados")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
    return False

def test_add_device():
    """Test POST device endpoint"""
    print("\n➕ Testing POST /profile/integrations...")
    payload = {
        "device_type": "garmin",
        "device_name": "Test Garmin",
        "sync_interval_hours": 6,
        "auto_sync_enabled": True
    }
    try:
        response = requests.post(
            f"{BASE_URL}/profile/integrations",
            headers=HEADERS,
            json=payload
        )
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            device_id = data.get("device_id")
            print(f"   ✓ Device creado: {device_id}")
            return device_id
    except Exception as e:
        print(f"   ✗ Error: {e}")
    return None

def test_set_primary(device_id):
    """Test setting primary device"""
    print(f"\n⭐ Testing POST /profile/integrations/{device_id}/set-primary...")
    try:
        response = requests.post(
            f"{BASE_URL}/profile/integrations/{device_id}/set-primary",
            headers=HEADERS
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Dispositivo {device_id} establecido como primario")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
    return False

def test_sync_all():
    """Test sync all devices"""
    print("\n🔄 Testing POST /profile/integrations/sync-all...")
    try:
        response = requests.post(
            f"{BASE_URL}/profile/integrations/sync-all",
            headers=HEADERS
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Sincronización iniciada")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
    return False

def test_delete_device(device_id):
    """Test DELETE device endpoint"""
    print(f"\n🗑️  Testing DELETE /profile/integrations/{device_id}...")
    try:
        response = requests.delete(
            f"{BASE_URL}/profile/integrations/{device_id}",
            headers=HEADERS
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Dispositivo eliminado")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
    return False

def main():
    print("=" * 60)
    print("🧪 FASE 3B VERIFICATION SCRIPT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Backend URL: {BASE_URL}")
    
    # Test sequence
    results = {
        "GET devices": test_get_devices(),
        "POST device": False,
        "SET primary": False,
        "SYNC all": test_sync_all(),
        "DELETE device": False
    }
    
    # Add device
    device_id = test_add_device()
    if device_id:
        results["POST device"] = True
        
        # Set primary
        results["SET primary"] = test_set_primary(device_id)
        
        # Delete
        results["DELETE device"] = test_delete_device(device_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test}")
    
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡FASE 3B VERIFICADA EXITOSAMENTE!")
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
