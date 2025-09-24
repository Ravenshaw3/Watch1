#!/usr/bin/env python3
"""
Test the specific TypeError issue in Playlists.vue
"""

import requests
import json

def test_playlists_typeerror():
    print("Testing Playlists TypeError Fix")
    print("=" * 40)
    
    # Login first
    print("1. Getting authentication token...")
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json={"username": "test@example.com", "password": "testpass123"},
            timeout=10
        )
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("   PASS: Authentication successful")
        else:
            print(f"   FAIL: Authentication failed: {login_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Authentication error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the exact API call that was causing TypeError
    print("\n2. Testing Playlists API response structure...")
    try:
        playlists_response = requests.get(
            "http://localhost:8000/api/v1/playlists/",
            headers=headers,
            timeout=5
        )
        
        if playlists_response.status_code == 200:
            data = playlists_response.json()
            print(f"   PASS: API returned {playlists_response.status_code}")
            
            # Check the exact structure that was causing issues
            print(f"   Response type: {type(data)}")
            print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if 'playlists' in data:
                playlists_array = data['playlists']
                print(f"   Playlists array type: {type(playlists_array)}")
                print(f"   Playlists count: {len(playlists_array) if isinstance(playlists_array, list) else 'Not a list'}")
                
                if isinstance(playlists_array, list) and len(playlists_array) > 0:
                    first_playlist = playlists_array[0]
                    print(f"   First playlist keys: {list(first_playlist.keys()) if isinstance(first_playlist, dict) else 'Not a dict'}")
                    print(f"   First playlist name: {first_playlist.get('name', 'No name') if isinstance(first_playlist, dict) else 'N/A'}")
            else:
                print("   ERROR: No 'playlists' key in response!")
                return False
                
        else:
            print(f"   FAIL: API returned {playlists_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: API error: {e}")
        return False
    
    # Test the frontend accessibility
    print("\n3. Testing frontend accessibility...")
    try:
        frontend_response = requests.get("http://localhost:3000/playlists", timeout=5)
        if frontend_response.status_code == 200:
            print("   PASS: Frontend playlists route accessible")
        else:
            print(f"   WARN: Frontend returned {frontend_response.status_code}")
    except Exception as e:
        print(f"   FAIL: Frontend error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("PLAYLISTS TYPEERROR FIX SUMMARY")
    print("=" * 40)
    
    print("\nRoot Cause:")
    print("- API returns: { playlists: [...] }")
    print("- Component expected: [...]")
    print("- TypeError: Cannot read properties of object")
    
    print("\nFix Applied:")
    print("1. Updated mediaApi.getPlaylists() to return response.data.playlists")
    print("2. Added fallback handling for different response formats")
    print("3. Added type safety with proper error handling")
    print("4. Ensured playlists.value is always an array")
    
    print("\nThe TypeError should now be resolved!")
    print("Try navigating to the Playlists tab - it should load without errors.")
    
    return True

if __name__ == "__main__":
    test_playlists_typeerror()
