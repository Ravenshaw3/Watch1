#!/usr/bin/env python3
"""
Test script to diagnose frontend-backend connection issues
"""

import requests
import json

def test_backend_health():
    """Test if backend is responding"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/settings/test", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    print("\n🌐 Testing CORS headers...")
    
    try:
        response = requests.options("http://localhost:8000/api/v1/media/", 
                                  headers={
                                      "Origin": "http://localhost:3000",
                                      "Access-Control-Request-Method": "GET",
                                      "Access-Control-Request-Headers": "Authorization"
                                  })
        
        print(f"   Status: {response.status_code}")
        print(f"   CORS Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"   CORS Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        print(f"   CORS Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
        
        if response.status_code == 200:
            print("✅ CORS preflight successful")
            return True
        else:
            print("❌ CORS preflight failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_login_endpoint():
    """Test login endpoint"""
    print("\n🔐 Testing login endpoint...")
    
    try:
        login_data = {
            "username": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post("http://localhost:8000/api/v1/auth/login/access-token", 
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login successful")
            print(f"   Token: {token[:20]}..." if token else "   No token received")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_users_me_endpoint(token):
    """Test /users/me endpoint"""
    print("\n👤 Testing /users/me endpoint...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/api/v1/users/me", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ /users/me successful")
            print(f"   User: {data.get('email', 'No email')}")
            return True
        else:
            print(f"❌ /users/me failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ /users/me request failed: {e}")
        return False

def test_media_endpoint(token):
    """Test media endpoint"""
    print("\n📁 Testing media endpoint...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/api/v1/media/", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"✅ Media endpoint successful - {len(items)} items")
            return True
        else:
            print(f"❌ Media endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Media request failed: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🖥️ Testing frontend accessibility...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🎬 Watch1 Frontend-Backend Connection Diagnostics")
    print("=" * 60)
    
    results = {}
    
    # Test backend health
    results['backend_health'] = test_backend_health()
    
    # Test frontend accessibility
    results['frontend_access'] = test_frontend_accessibility()
    
    # Test CORS
    results['cors'] = test_cors_headers()
    
    # Test login
    token = test_login_endpoint()
    results['login'] = token is not None
    
    # Test authenticated endpoints
    if token:
        results['users_me'] = test_users_me_endpoint(token)
        results['media'] = test_media_endpoint(token)
    else:
        results['users_me'] = False
        results['media'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Frontend should be working.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        
        if not results['backend_health']:
            print("   - Backend is not responding")
        if not results['frontend_access']:
            print("   - Frontend is not accessible")
        if not results['cors']:
            print("   - CORS configuration issue")
        if not results['login']:
            print("   - Authentication endpoint issue")
        if not results['users_me']:
            print("   - User profile endpoint issue")
        if not results['media']:
            print("   - Media API endpoint issue")

if __name__ == "__main__":
    main()
