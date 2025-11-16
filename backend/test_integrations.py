"""
test_integrations.py - Test script for device integration endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Test credentials (from onboarding - user 1)
LOGIN_EMAIL = "guillermomartindeoliva@gmail.com"
LOGIN_PASSWORD = "password123"

def test_integrations():
    """Test device integration endpoints."""
    
    print("\n" + "="*60)
    print("[TEST] DEVICE INTEGRATION ENDPOINTS")
    print("="*60)
    
    # Step 1: Login
    print("\n[1] Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    user_id = login_response.json()["user"]["id"]
    print(f"    [OK] Login successful - User ID: {user_id}")
    print(f"    [OK] Token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get current integrations
    print("\n[2] Getting current integrations...")
    get_response = requests.get(
        f"{BASE_URL}/api/v1/profile/integrations",
        headers=headers
    )
    assert get_response.status_code == 200, f"Get integrations failed: {get_response.text}"
    current_integrations = get_response.json()
    print(f"    [OK] Current integrations:")
    print(f"         Primary device: {current_integrations['primary_device']}")
    print(f"         Sync enabled: {current_integrations['devices_enabled']}")
    print(f"         Devices: {len(current_integrations['devices'])} devices")
    for device in current_integrations['devices']:
        print(f"           - {device['device_id']} ({device['device_type']}): {device['device_name']}")
    
    # Step 3: Add a new device (Strava)
    print("\n[3] Adding a new Strava integration...")
    add_response = requests.post(
        f"{BASE_URL}/api/v1/profile/integrations",
        json={
            "device_type": "strava",
            "device_name": "My Strava Account",
            "sync_interval_hours": 2,
            "auto_sync_enabled": True
        },
        headers=headers
    )
    assert add_response.status_code == 201, f"Add integration failed: {add_response.text}"
    new_device = add_response.json()
    print(f"    [OK] Device added successfully!")
    print(f"         Device ID: {new_device['device_id']}")
    print(f"         Type: {new_device['device_type']}")
    print(f"         Name: {new_device['device_name']}")
    print(f"         Sync interval: {new_device['sync_config']['sync_interval_hours']} hours")
    
    # Step 4: Add another device (Apple)
    print("\n[4] Adding an Apple Health integration...")
    add_apple_response = requests.post(
        f"{BASE_URL}/api/v1/profile/integrations",
        json={
            "device_type": "apple",
            "device_name": "Apple Health",
            "sync_interval_hours": 1,
            "auto_sync_enabled": True
        },
        headers=headers
    )
    assert add_apple_response.status_code == 201, f"Add Apple integration failed: {add_apple_response.text}"
    apple_device = add_apple_response.json()
    print(f"    [OK] Apple Health device added!")
    print(f"         Device ID: {apple_device['device_id']}")
    
    # Step 5: Get all integrations again
    print("\n[5] Getting updated integrations...")
    get_updated_response = requests.get(
        f"{BASE_URL}/api/v1/profile/integrations",
        headers=headers
    )
    assert get_updated_response.status_code == 200
    updated_integrations = get_updated_response.json()
    print(f"    [OK] Total devices now: {len(updated_integrations['devices'])}")
    for device in updated_integrations['devices']:
        primary_marker = " [PRIMARY]" if device['is_primary'] else ""
        print(f"         - {device['device_id']}: {device['device_name']}{primary_marker}")
    
    # Step 6: Update device settings
    print(f"\n[6] Updating Strava device settings...")
    update_response = requests.put(
        f"{BASE_URL}/api/v1/profile/integrations/strava",
        json={
            "device_name": "Strava Activities",
            "sync_interval_hours": 4,
            "auto_sync_enabled": False
        },
        headers=headers
    )
    assert update_response.status_code == 200, f"Update failed: {update_response.text}"
    updated_device = update_response.json()
    print(f"    [OK] Device updated!")
    print(f"         New name: {updated_device['device_name']}")
    print(f"         New sync interval: {updated_device['sync_config']['sync_interval_hours']} hours")
    print(f"         Auto sync enabled: {updated_device['sync_config']['auto_sync_enabled']}")
    
    # Step 7: Get sync status
    print(f"\n[7] Getting sync status...")
    sync_status_response = requests.get(
        f"{BASE_URL}/api/v1/profile/integrations/apple/sync-status",
        headers=headers
    )
    assert sync_status_response.status_code == 200
    sync_status = sync_status_response.json()
    print(f"    [OK] Sync status for Apple Health:")
    print(f"         Status: {sync_status['sync_status']}")
    print(f"         Last sync: {sync_status['last_sync']}")
    print(f"         Next sync: {sync_status['next_sync']}")
    
    # Step 8: Set primary device
    print(f"\n[8] Setting Apple Health as primary device...")
    set_primary_response = requests.post(
        f"{BASE_URL}/api/v1/profile/integrations/apple/set-primary",
        headers=headers
    )
    assert set_primary_response.status_code == 200
    print(f"    [OK] Apple Health is now the primary device!")
    
    # Step 9: Verify primary device changed
    print(f"\n[9] Verifying primary device change...")
    verify_response = requests.get(
        f"{BASE_URL}/api/v1/profile/integrations",
        headers=headers
    )
    updated = verify_response.json()
    print(f"    [OK] New primary device: {updated['primary_device']}")
    
    # Step 10: Trigger manual sync
    print(f"\n[10] Triggering manual sync for all devices...")
    sync_all_response = requests.post(
        f"{BASE_URL}/api/v1/profile/integrations/sync-all",
        headers=headers
    )
    assert sync_all_response.status_code == 200
    sync_results = sync_all_response.json()
    print(f"    [OK] Sync initiated!")
    print(f"         Message: {sync_results['message']}")
    print(f"         Results: {sync_results['results']}")
    
    # Step 11: Remove a device
    print(f"\n[11] Removing Strava device...")
    remove_response = requests.delete(
        f"{BASE_URL}/api/v1/profile/integrations/strava",
        headers=headers
    )
    assert remove_response.status_code == 204, f"Remove failed: {remove_response.text}"
    print(f"    [OK] Strava device removed!")
    
    # Step 12: Final verification
    print(f"\n[12] Final integrations list...")
    final_response = requests.get(
        f"{BASE_URL}/api/v1/profile/integrations",
        headers=headers
    )
    final_integrations = final_response.json()
    print(f"    [OK] Remaining devices: {len(final_integrations['devices'])}")
    for device in final_integrations['devices']:
        primary_marker = " [PRIMARY]" if device['is_primary'] else ""
        print(f"         - {device['device_id']}: {device['device_name']}{primary_marker}")
    
    print("\n" + "="*60)
    print("[RESULT] ALL TESTS PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_integrations()
    except AssertionError as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
