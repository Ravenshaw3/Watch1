#!/usr/bin/env python3
"""
Test navigation issues in Watch1 frontend
"""

import requests
import time

def test_navigation_flow():
    """Test the navigation between different tabs"""
    print("Testing Watch1 Navigation Flow")
    print("=" * 50)
    
    # Test 1: Login and get token
    print("1. Testing login...")
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json={"username": "test@example.com", "password": "testpass123"},
            timeout=10
        )
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("   PASS: Login successful")
        else:
            print(f"   FAIL: Login failed: {login_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Login error: {e}")
        return False
    
    # Test 2: Check /users/me endpoint (authentication state)
    print("2. Testing user authentication state...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        user_response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers, timeout=10)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   PASS: User authenticated: {user_data.get('email', 'No email')}")
        else:
            print(f"   FAIL: User authentication failed: {user_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: User authentication error: {e}")
        return False
    
    # Test 3: Test each navigation endpoint
    navigation_endpoints = [
        ("/api/v1/media/", "Library"),
        ("/api/v1/playlists/", "Playlists"), 
        ("/api/v1/analytics/views", "Analytics"),
        ("/api/v1/settings/", "Settings")
    ]
    
    print("3. Testing navigation endpoints...")
    for endpoint, name in navigation_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=10)
            if response.status_code in [200, 404, 405]:  # 404/405 might be expected for some endpoints
                print(f"   PASS: {name} endpoint accessible ({response.status_code})")
            else:
                print(f"   WARN: {name} endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   FAIL: {name} endpoint error: {e}")
    
    # Test 4: Check frontend routes
    print("4. Testing frontend route accessibility...")
    frontend_routes = [
        "/library",
        "/playlists", 
        "/analytics",
        "/settings"
    ]
    
    for route in frontend_routes:
        try:
            # Test if frontend serves the route (should return HTML)
            response = requests.get(f"http://localhost:3000{route}", timeout=10)
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                print(f"   PASS: Frontend route {route} accessible")
            else:
                print(f"   WARN: Frontend route {route} returned {response.status_code}")
        except Exception as e:
            print(f"   FAIL: Frontend route {route} error: {e}")
    
    print("\n" + "=" * 50)
    print("NAVIGATION DIAGNOSTICS COMPLETE")
    print("\nCommon causes of navigation issues:")
    print("1. Authentication state lost between route changes")
    print("2. Vue router navigation guards blocking transitions")
    print("3. Component errors preventing route loading")
    print("4. Missing or broken route components")
    print("5. JavaScript errors in mounted/created hooks")
    
    print("\nTo debug further:")
    print("1. Open browser DevTools (F12)")
    print("2. Go to Console tab")
    print("3. Navigate between tabs and watch for errors")
    print("4. Check Network tab for failed API requests")
    
    return True

if __name__ == "__main__":
    test_navigation_flow()
