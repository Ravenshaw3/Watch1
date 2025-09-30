#!/usr/bin/env python3
"""
Simple backend connectivity test to identify the exact issue
"""

import requests
import json

def test_backend_connectivity():
    print("SIMPLE BACKEND CONNECTIVITY TEST")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Health check: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Backend is reachable")
        else:
            print("   ❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Cannot reach backend: {e}")
        return False
    
    print("\n2. Testing authentication...")
    try:
        auth_data = {
            "username": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login/access-token",
            json=auth_data,
            timeout=10
        )
        
        print(f"   Login request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print("   ✅ Authentication successful")
                print(f"   Token length: {len(token)} characters")
                return token
            else:
                print("   ❌ No token in response")
                print(f"   Response: {data}")
                return None
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return None
    
def test_endpoints_with_token(token):
    print("\n3. Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        ("/api/v1/media/categories", "Categories"),
        ("/api/v1/media/scan-info", "Scan Info"),
        ("/api/v1/media/", "Media List"),
        ("/api/v1/playlists/", "Playlists")
    ]
    
    all_success = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            print(f"   {name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                data_keys = list(data.keys()) if isinstance(data, dict) else "Array"
                print(f"      ✅ Success - Data: {data_keys}")
            else:
                print(f"      ❌ Failed - Response: {response.text[:100]}")
                all_success = False
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
            all_success = False
    
    return all_success

def check_cors_headers():
    print("\n4. Checking CORS headers...")
    
    try:
        response = requests.options("http://localhost:8000/api/v1/media/categories")
        print(f"   OPTIONS request: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print("   CORS Headers:")
        for header, value in cors_headers.items():
            print(f"      {header}: {value or 'Not set'}")
            
        if cors_headers['Access-Control-Allow-Origin']:
            print("   ✅ CORS appears to be configured")
        else:
            print("   ⚠️ CORS headers might be missing")
            
    except Exception as e:
        print(f"   ❌ CORS check error: {e}")

def main():
    print("🔍 Diagnosing why debug tool tests 1 and 2 failed...")
    print()
    
    # Test backend connectivity
    token = test_backend_connectivity()
    
    if token:
        # Test endpoints with authentication
        endpoints_ok = test_endpoints_with_token(token)
        
        # Check CORS
        check_cors_headers()
        
        print(f"\n" + "=" * 40)
        print("DIAGNOSIS SUMMARY")
        print("=" * 40)
        
        if endpoints_ok:
            print("✅ Backend is working perfectly!")
            print("🔍 The issue is likely in the frontend debug tool:")
            print("   - CORS restrictions from file:// protocol")
            print("   - Browser security blocking cross-origin requests")
            print("   - Debug tool running from wrong origin")
            print()
            print("💡 SOLUTIONS:")
            print("   1. Run debug tool from http://localhost:3000 (same origin)")
            print("   2. Use browser console debug script instead")
            print("   3. Check browser console for CORS errors")
            
        else:
            print("❌ Backend has issues that need fixing")
            
    else:
        print("❌ Authentication is failing - backend has problems")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. If backend works: Use browser console debug script")
    print(f"   2. If backend fails: Check backend logs and database")
    print(f"   3. Open http://localhost:3000 and check browser console")

if __name__ == "__main__":
    main()
