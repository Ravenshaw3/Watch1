#!/usr/bin/env python3
"""
Test all endpoints after login fix to see what broke
"""

import requests
import time

def test_all_endpoints():
    print("TESTING ALL ENDPOINTS AFTER LOGIN FIX")
    print("=" * 40)
    
    # Step 1: Login
    print("1. Testing login...")
    try:
        login_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                     json={'username': 'test@example.com', 'password': 'testpass123'})
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print("   SUCCESS: Login working")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ERROR: Login failed - {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ERROR: Login request failed - {e}")
        return
    
    # Step 2: Test endpoints that are failing
    endpoints_to_test = [
        ("/api/v1/media/", "Media Files"),
        ("/api/v1/playlists/", "Playlists"),
        ("/api/v1/users/me", "User Profile"),
        ("/api/v1/media/categories", "Media Categories"),
        ("/api/v1/media/scan-info", "Scan Info"),
        ("/health", "Health Check (no auth)"),
        ("/api/v1/version", "Version (no auth)")
    ]
    
    print("\n2. Testing protected endpoints...")
    working_endpoints = 0
    failed_endpoints = 0
    
    for endpoint, name in endpoints_to_test:
        try:
            # Use auth headers for API endpoints, no auth for health/version
            if endpoint.startswith('/api/v1/') and endpoint not in ['/api/v1/version']:
                response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            
            print(f"   {name}: {response.status_code}")
            
            if response.status_code == 200:
                working_endpoints += 1
                # Show some data for key endpoints
                if endpoint == "/api/v1/media/":
                    data = response.json()
                    items = data.get('items', [])
                    print(f"      -> {len(items)} media items found")
                elif endpoint == "/api/v1/playlists/":
                    data = response.json()
                    print(f"      -> {len(data)} playlists found")
            else:
                failed_endpoints += 1
                print(f"      -> ERROR: {response.text[:100]}...")
                
        except Exception as e:
            failed_endpoints += 1
            print(f"   {name}: ERROR - {e}")
    
    print(f"\n3. SUMMARY:")
    print(f"   Working endpoints: {working_endpoints}")
    print(f"   Failed endpoints: {failed_endpoints}")
    
    if failed_endpoints > 0:
        print(f"\n4. DIAGNOSIS:")
        print(f"   The login fix may have affected:")
        print(f"   - JWT token validation")
        print(f"   - Database queries in other endpoints")
        print(f"   - User ID lookup in protected routes")
        
        print(f"\n5. LIKELY ISSUES:")
        print(f"   - Other endpoints still using old column names")
        print(f"   - JWT identity lookup broken")
        print(f"   - Database connection issues")
        print(f"   - Missing data in database tables")
    else:
        print(f"\n4. ALL ENDPOINTS WORKING!")
        print(f"   The login fix didn't break anything else")

if __name__ == "__main__":
    test_all_endpoints()
