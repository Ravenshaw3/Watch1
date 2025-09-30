#!/usr/bin/env python3
"""
Comprehensive frontend interface diagnostic
"""

import requests
import json
import time

def test_authentication():
    """Test the authentication flow"""
    print("🔐 Testing Authentication...")
    
    try:
        # Test login
        login_data = {
            "username": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("  ✅ Login API: Working")
            print(f"  📝 Token length: {len(token) if token else 0}")
            
            # Test user info endpoint
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get(
                "http://localhost:8000/api/v1/users/me",
                headers=headers,
                timeout=5
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(f"  ✅ User info: {user_data.get('email', 'Unknown')}")
                return token
            else:
                print(f"  ❌ User info failed: {user_response.status_code}")
                return token
        else:
            print(f"  ❌ Login failed: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Authentication error: {e}")
        return None

def test_api_endpoints(token):
    """Test all main API endpoints"""
    print("\n🔌 Testing API Endpoints...")
    
    if not token:
        print("  ❌ No token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/media/", "Library"),
        ("/playlists/", "Playlists"),
        ("/analytics/dashboard", "Analytics"),
        ("/settings/", "Settings")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1{endpoint}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {name}: Working")
                
                # Show key info
                if name == "Library":
                    total = data.get("total", 0)
                    media_count = len(data.get("media", []))
                    print(f"    📊 Total: {total}, Current page: {media_count}")
                elif name == "Settings":
                    categories = list(data.keys())
                    print(f"    📊 Categories: {len(categories)} ({', '.join(categories[:3])}...)")
                elif name == "Analytics":
                    keys = list(data.keys())
                    print(f"    📊 Data keys: {len(keys)} ({', '.join(keys[:3])}...)")
                
                results[name] = True
            else:
                print(f"  ❌ {name}: Error {response.status_code}")
                print(f"    📄 Response: {response.text[:100]}")
                results[name] = False
                
        except Exception as e:
            print(f"  ❌ {name}: Failed - {e}")
            results[name] = False
    
    return results

def test_frontend_accessibility():
    """Test frontend page accessibility"""
    print("\n🌐 Testing Frontend Accessibility...")
    
    pages = [
        ("/", "Home"),
        ("/library", "Library"),
        ("/playlists", "Playlists"),
        ("/analytics", "Analytics"),
        ("/settings", "Settings")
    ]
    
    for path, name in pages:
        try:
            response = requests.get(
                f"http://localhost:3000{path}",
                timeout=5,
                allow_redirects=False
            )
            
            if response.status_code == 200:
                print(f"  ✅ {name} ({path}): Accessible")
            elif response.status_code in [301, 302, 307, 308]:
                print(f"  🔄 {name} ({path}): Redirects")
            else:
                print(f"  ❌ {name} ({path}): Error {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {name} ({path}): Failed - {e}")

def test_cors_and_proxy():
    """Test CORS and proxy configuration"""
    print("\n🔗 Testing CORS and Proxy...")
    
    try:
        # Test direct backend call
        response = requests.get(
            "http://localhost:8000/api/v1/version",
            timeout=5
        )
        
        if response.status_code == 200:
            print("  ✅ Direct backend: Accessible")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            print(f"  📋 CORS headers: {cors_headers}")
        else:
            print(f"  ❌ Direct backend: Error {response.status_code}")
            
        # Test proxy through frontend
        proxy_response = requests.get(
            "http://localhost:3000/api/v1/version",
            timeout=5
        )
        
        if proxy_response.status_code == 200:
            print("  ✅ Frontend proxy: Working")
        else:
            print(f"  ❌ Frontend proxy: Error {proxy_response.status_code}")
            
    except Exception as e:
        print(f"  ❌ CORS/Proxy test failed: {e}")

def main():
    print("🔍 WATCH1 v3.0.1 - FRONTEND INTERFACE DIAGNOSTIC")
    print("=" * 60)
    
    # Test authentication
    token = test_authentication()
    
    # Test API endpoints
    api_results = test_api_endpoints(token)
    
    # Test frontend accessibility
    test_frontend_accessibility()
    
    # Test CORS and proxy
    test_cors_and_proxy()
    
    # Summary
    print("\n📋 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    if token:
        print("✅ Authentication: Working")
    else:
        print("❌ Authentication: Failed")
    
    if api_results:
        working_apis = sum(api_results.values())
        total_apis = len(api_results)
        print(f"📊 API Endpoints: {working_apis}/{total_apis} working")
        
        for name, status in api_results.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {name}")
    
    print("\n🎯 RECOMMENDATIONS:")
    if not token:
        print("  1. Check backend server is running on port 8000")
        print("  2. Verify login credentials")
    
    if api_results and not all(api_results.values()):
        print("  3. Check API endpoint implementations")
        print("  4. Verify JWT token handling")
    
    print("  5. Check browser console for JavaScript errors")
    print("  6. Verify frontend build has no compilation errors")
    print("  7. Test with browser developer tools network tab")

if __name__ == "__main__":
    main()
