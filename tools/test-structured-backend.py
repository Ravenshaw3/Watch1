#!/usr/bin/env python3
"""
Test script for structured backend endpoints
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:8000'

def test_endpoint(method, path, headers=None, data=None, expect_auth=False):
    """Test an endpoint and return result"""
    url = f"{BASE_URL}{path}"
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
        if expect_auth and response.status_code == 401:
            status = "🔒 AUTH_REQUIRED"
        
        print(f"{status} {method} {path} -> {response.status_code}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                if isinstance(result, dict) and len(result) <= 3:
                    print(f"     Response: {result}")
                elif isinstance(result, list) and len(result) <= 2:
                    print(f"     Response: {result}")
                else:
                    print(f"     Response: {type(result).__name__} with {len(result)} items")
            except:
                print(f"     Response: {response.text[:100]}...")
        
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ ERROR {method} {path} -> {e}")
        return False

def main():
    print("Testing Watch1 Structured Backend Endpoints")
    print("=" * 50)
    
    # Test basic endpoints
    print("\n🏥 Health Endpoints:")
    test_endpoint('GET', '/')
    test_endpoint('GET', '/health')
    test_endpoint('GET', '/api/v1/health')
    
    # Test settings (no auth required for test endpoint)
    print("\n⚙️ Settings Endpoints:")
    test_endpoint('GET', '/api/v1/settings/test')
    test_endpoint('GET', '/api/v1/settings/', expect_auth=True)
    test_endpoint('GET', '/api/v1/settings/media-directories', expect_auth=True)
    
    # Test auth endpoints
    print("\n🔐 Authentication Endpoints:")
    login_data = {"username": "test@example.com", "password": "testpass123"}
    login_success = test_endpoint('POST', '/api/v1/auth/login/access-token', data=login_data)
    
    # Get token for authenticated tests
    token = None
    if login_success:
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/login/access-token", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get('access_token')
                print(f"     🎫 Token obtained: {token[:20]}..." if token else "     ❌ No token in response")
        except Exception as e:
            print(f"     ❌ Token extraction failed: {e}")
    
    # Test authenticated endpoints
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        
        print("\n👤 User Endpoints:")
        test_endpoint('GET', '/api/v1/auth/me', headers=headers)
        
        print("\n📁 Media Endpoints:")
        test_endpoint('GET', '/api/v1/media/', headers=headers)
        test_endpoint('GET', '/api/v1/media/categories', headers=headers)
        
        print("\n📋 Playlist Endpoints:")
        test_endpoint('GET', '/api/v1/playlists/', headers=headers)
        
        print("\n📊 Analytics Endpoints:")
        test_endpoint('GET', '/api/v1/analytics/dashboard', headers=headers)
        
        print("\n⚙️ Authenticated Settings:")
        test_endpoint('GET', '/api/v1/settings/', headers=headers)
        test_endpoint('GET', '/api/v1/settings/media-directories', headers=headers)
        
        print("\n🔧 System Endpoints:")
        test_endpoint('GET', '/api/v1/system/version')
        test_endpoint('GET', '/api/v1/system/health-detailed')
        test_endpoint('GET', '/api/v1/system/database-info', headers=headers)
    else:
        print("\n❌ Skipping authenticated tests - no token available")
    
    print("\n" + "=" * 50)
    print("Structured backend test complete!")

if __name__ == "__main__":
    main()
