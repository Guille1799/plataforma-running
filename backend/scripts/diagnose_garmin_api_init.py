#!/usr/bin/env python
"""
Diagnostic script to investigate how GarminConnectAPI initializes its garth client.

This script will:
1. Load tokens with garth.resume()
2. Create GarminConnectAPI()
3. Verify if api.garth.client is the same object as garth.client
4. Verify if api.garth.client has tokens after creation
5. Compare behavior between get_full_name() and get_activities()

Usage:
    python backend/scripts/diagnose_garmin_api_init.py <user_id>

Example:
    python backend/scripts/diagnose_garmin_api_init.py 6
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
script_dir = Path(__file__).parent.resolve()
backend_dir_abs = script_dir.parent.resolve()
sys.path.insert(0, str(backend_dir_abs))

def diagnose_garmin_api_init(user_id: int):
    """Diagnose how GarminConnectAPI initializes its garth client."""
    print(f"\n{'='*70}")
    print(f"GarminConnectAPI Initialization Diagnostic for User {user_id}")
    print(f"{'='*70}\n")
    
    # Calculate token directory path (same logic as garmin_service.py)
    # backend_dir_abs is already set from global scope
    global backend_dir_abs
    
    if os.name == 'nt':  # Windows
        persistent_dir = os.path.join(backend_dir_abs, "garmin_tokens")
    else:  # Linux/Docker
        persistent_dir = "/app/garmin_tokens"
    
    user_token_dir = os.path.join(persistent_dir, f"user_{user_id}")
    oauth1_path = os.path.join(user_token_dir, "oauth1_token.json")
    oauth2_path = os.path.join(user_token_dir, "oauth2_token.json")
    
    print(f"Token Directory: {user_token_dir}")
    print(f"Directory Exists: {os.path.exists(user_token_dir)}\n")
    
    if not os.path.exists(user_token_dir):
        print("[ERROR] Token directory does not exist!")
        return False
    
    if not os.path.exists(oauth1_path) or not os.path.exists(oauth2_path):
        print("[ERROR] Token files missing!")
        return False
    
    try:
        import garth
        from garminconnect import Garmin as GarminConnectAPI
        
        print("=" * 70)
        print("STEP 1: Configure and resume garth session")
        print("=" * 70)
        
        # Configure garth
        garth.configure(domain="garmin.com", timeout=120)
        print("[OK] garth.configure() completed")
        
        # Check state before resume
        has_client_before = hasattr(garth, 'client') and garth.client is not None
        print(f"garth.client exists before resume: {has_client_before}")
        
        # Resume session
        garth.resume(user_token_dir)
        print("[OK] garth.resume() completed")
        
        # Re-configure after resume
        garth.configure(domain="garmin.com", timeout=120)
        print("[OK] garth.configure() after resume completed")
        
        # Check state after resume
        has_client_after = hasattr(garth, 'client') and garth.client is not None
        has_oauth1_after = has_client_after and hasattr(garth.client, 'oauth1_token') and garth.client.oauth1_token
        has_oauth2_after = has_client_after and hasattr(garth.client, 'oauth2_token') and garth.client.oauth2_token
        
        print(f"\ngarth.client state after resume:")
        print(f"  - Exists: {has_client_after}")
        print(f"  - Has oauth1_token: {has_oauth1_after}")
        print(f"  - Has oauth2_token: {has_oauth2_after}")
        
        if has_client_after:
            oauth1_value = getattr(garth.client, 'oauth1_token', None)
            oauth2_value = getattr(garth.client, 'oauth2_token', None)
            oauth1_str = str(oauth1_value) if oauth1_value else None
            oauth2_str = str(oauth2_value) if oauth2_value else None
            print(f"  - oauth1_token value: {oauth1_str[:50] + '...' if oauth1_str and len(oauth1_str) > 50 else oauth1_str}")
            print(f"  - oauth2_token value: {oauth2_str[:50] + '...' if oauth2_str and len(oauth2_str) > 50 else oauth2_str}")
        
        if not has_client_after or not has_oauth1_after:
            print("\n[ERROR] garth.client does not have tokens after resume!")
            return False
        
        # Store reference to global client
        global_client_before_api = garth.client
        global_client_id_before = id(garth.client)
        print(f"\nglobal garth.client object ID: {global_client_id_before}")
        
        print("\n" + "=" * 70)
        print("STEP 2: Create GarminConnectAPI instance")
        print("=" * 70)
        
        # Create API instance
        api = GarminConnectAPI()
        print("[OK] GarminConnectAPI() created")
        
        # Check if api has garth attribute
        has_api_garth = hasattr(api, 'garth')
        print(f"api has 'garth' attribute: {has_api_garth}")
        
        if has_api_garth:
            has_api_garth_client = hasattr(api.garth, 'client') and api.garth.client is not None
            print(f"api.garth has 'client' attribute: {has_api_garth_client}")
            
            if has_api_garth_client:
                api_client_id = id(api.garth.client)
                global_client_id_after = id(garth.client)
                
                print(f"\napi.garth.client object ID: {api_client_id}")
                print(f"global garth.client object ID: {global_client_id_after}")
                print(f"Are they the same object? {api_client_id == global_client_id_after}")
                
                # Check tokens in api.garth.client
                api_has_oauth1 = hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token
                api_has_oauth2 = hasattr(api.garth.client, 'oauth2_token') and api.garth.client.oauth2_token
                
                print(f"\napi.garth.client token state:")
                print(f"  - Has oauth1_token: {api_has_oauth1}")
                print(f"  - Has oauth2_token: {api_has_oauth2}")
                
                if api_has_oauth1:
                    api_oauth1_value = api.garth.client.oauth1_token
                    api_oauth1_str = str(api_oauth1_value) if api_oauth1_value else None
                    print(f"  - oauth1_token value: {api_oauth1_str[:50] + '...' if api_oauth1_str and len(api_oauth1_str) > 50 else api_oauth1_str}")
                
                # Compare with global
                if api_client_id == global_client_id_after:
                    print("\n[INFO] api.garth.client IS the same object as garth.client")
                else:
                    print("\n[WARNING] api.garth.client is a DIFFERENT object from garth.client!")
                    print("  This means GarminConnectAPI() creates its own client instance")
        
        print("\n" + "=" * 70)
        print("STEP 3: Test API calls")
        print("=" * 70)
        
        # Test get_full_name()
        print("\n3.1 Testing api.get_full_name()...")
        try:
            # Check state before call
            if has_api_garth and has_api_garth_client:
                oauth1_before_call = hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token
                print(f"  api.garth.client.oauth1_token exists before call: {oauth1_before_call}")
            
            user_name = api.get_full_name()
            print(f"  [OK] get_full_name() succeeded: {user_name}")
            
            # Check state after call
            if has_api_garth and has_api_garth_client:
                oauth1_after_call = hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token
                print(f"  api.garth.client.oauth1_token exists after call: {oauth1_after_call}")
        except Exception as e:
            print(f"  [ERROR] get_full_name() failed: {str(e)}")
            import traceback
            print(f"  Traceback:\n{traceback.format_exc()}")
        
        # Test get_activities()
        print("\n3.2 Testing api.get_activities()...")
        try:
            # Check state before call
            if has_api_garth and has_api_garth_client:
                oauth1_before_call = hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token
                print(f"  api.garth.client.oauth1_token exists before call: {oauth1_before_call}")
                if not oauth1_before_call:
                    print(f"  [WARNING] oauth1_token is missing before get_activities()!")
            
            activities = api.get_activities(start=0, limit=10)
            print(f"  [OK] get_activities() succeeded, got {len(activities)} activities")
            
            # Check state after call
            if has_api_garth and has_api_garth_client:
                oauth1_after_call = hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token
                print(f"  api.garth.client.oauth1_token exists after call: {oauth1_after_call}")
        except Exception as e:
            print(f"  [ERROR] get_activities() failed: {str(e)}")
            import traceback
            print(f"  Traceback:\n{traceback.format_exc()}")
            
            # Check state after error
            if has_api_garth and has_api_garth_client:
                oauth1_after_error = hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token
                print(f"  api.garth.client.oauth1_token exists after error: {oauth1_after_error}")
        
        print("\n" + "=" * 70)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        if has_api_garth and has_api_garth_client:
            same_object = id(api.garth.client) == id(garth.client)
            api_has_tokens = (hasattr(api.garth.client, 'oauth1_token') and api.garth.client.oauth1_token) and \
                           (hasattr(api.garth.client, 'oauth2_token') and api.garth.client.oauth2_token)
            
            print(f"✓ api.garth.client is same object as garth.client: {same_object}")
            print(f"✓ api.garth.client has tokens: {api_has_tokens}")
            
            if not same_object:
                print("\n[CONCLUSION] GarminConnectAPI() creates its own client instance")
                print("  Solution: Need to copy tokens from garth.client to api.garth.client")
            elif not api_has_tokens:
                print("\n[CONCLUSION] api.garth.client is same object but tokens are missing")
                print("  Solution: Need to investigate why tokens are lost")
            else:
                print("\n[CONCLUSION] Everything looks correct - issue may be elsewhere")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Diagnostic failed: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_garmin_api_init.py <user_id>")
        print("Example: python diagnose_garmin_api_init.py 6")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: user_id must be an integer")
        sys.exit(1)
    
    success = diagnose_garmin_api_init(user_id)
    sys.exit(0 if success else 1)
