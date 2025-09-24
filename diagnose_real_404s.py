#!/usr/bin/env python3
"""
Diagnose the real 404 errors - endpoints should exist
"""

import requests

def diagnose_real_404s():
    print("DIAGNOSING REAL 404 ERRORS")
    print("=" * 35)
    
    # Test without authentication first
    print("1. TESTING ENDPOINTS WITHOUT AUTH")
    print("-" * 35)
    
    endpoints = [
        "/api/v1/media/categories",
        "/api/v1/media/scan-info",
        "/api/v1/playlists/",
        "/api/v1/media/"
    ]
    
    for endpoint in endpoints:
        url = f"http://localhost:8000{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"GET {endpoint} -> {response.status_code}")
            if response.status_code == 401:
                print(f"   ✅ Endpoint exists (needs auth)")
            elif response.status_code == 404:
                print(f"   ❌ Endpoint missing!")
            else:
                print(f"   ⚠️  Unexpected: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
    
    # Test with authentication
    print(f"\n2. TESTING WITH AUTHENTICATION")
    print("-" * 35)
    
    try:
        # Login
        login_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                     json={'username': 'test@example.com', 'password': 'testpass123'})
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
            
            for endpoint in endpoints:
                url = f"http://localhost:8000{endpoint}"
                try:
                    response = requests.get(url, headers=headers, timeout=5)
                    print(f"GET {endpoint} -> {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ Working correctly")
                    elif response.status_code == 404:
                        print(f"   ❌ Still 404 with auth!")
                        # Check if it's a routing issue
                        print(f"   Response: {response.text[:100]}")
                    else:
                        print(f"   ⚠️  Status: {response.status_code}")
                        print(f"   Response: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"   ❌ Request error: {e}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
    
    # Test backend health
    print(f"\n3. TESTING BACKEND HEALTH")
    print("-" * 25)
    
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"GET /health -> {health_response.status_code}")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health issue: {health_response.text}")
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
    
    # Check if backend is actually running the right code
    print(f"\n4. CHECKING BACKEND VERSION")
    print("-" * 25)
    
    try:
        version_response = requests.get("http://localhost:8000/api/v1/version", timeout=5)
        print(f"GET /api/v1/version -> {version_response.status_code}")
        if version_response.status_code == 200:
            data = version_response.json()
            version = data.get('version', 'Unknown')
            framework = data.get('framework', 'Unknown')
            print(f"✅ Version: {version}, Framework: {framework}")
        else:
            print(f"❌ Version check failed: {version_response.text}")
    except Exception as e:
        print(f"❌ Version check error: {e}")
    
    print(f"\n" + "=" * 35)
    print("DIAGNOSIS SUMMARY")
    print("=" * 35)
    
    print(f"\n💡 POSSIBLE CAUSES OF 404s:")
    print(f"   1. Backend container not running updated code")
    print(f"   2. Frontend making requests to wrong URLs")
    print(f"   3. CORS blocking requests")
    print(f"   4. Authentication token issues")
    print(f"   5. Route registration problems in Flask")
    
    print(f"\n🔧 DEBUGGING STEPS:")
    print(f"   1. Check: docker logs watch1-backend-dev")
    print(f"   2. Check: docker ps (container status)")
    print(f"   3. Check: Browser Network tab for actual URLs")
    print(f"   4. Check: Frontend console for auth token")
    
    return True

if __name__ == "__main__":
    diagnose_real_404s()
