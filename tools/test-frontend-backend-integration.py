#!/usr/bin/env python3
"""
Frontend-Backend Integration Test for Watch1 Structured Backend
Tests that frontend can successfully communicate with structured backend
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:3000'

def test_service_availability():
    """Test that both services are running"""
    print("🔍 Testing Service Availability")
    print("-" * 40)
    
    # Test backend
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: Available")
            backend_data = response.json()
            print(f"   Version: {backend_data.get('version', 'unknown')}")
        else:
            print(f"❌ Backend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend: Connection failed - {e}")
        return False
    
    # Test frontend
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Available")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: Connection failed - {e}")
        return False
    
    return True

def test_authentication_flow():
    """Test complete authentication flow"""
    print("\n🔐 Testing Authentication Flow")
    print("-" * 40)
    
    # Test login
    login_data = {
        "username": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/login/access-token", 
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Login: Successful")
            auth_data = response.json()
            token = auth_data.get('access_token')
            user_info = auth_data.get('user', {})
            print(f"   User: {user_info.get('email', 'unknown')}")
            print(f"   Superuser: {user_info.get('is_superuser', False)}")
            
            # Test user profile with token
            headers = {'Authorization': f'Bearer {token}'}
            profile_response = requests.get(f"{BACKEND_URL}/api/v1/auth/me", 
                                          headers=headers, timeout=10)
            
            if profile_response.status_code == 200:
                print("✅ User Profile: Accessible")
                return token
            else:
                print(f"❌ User Profile: HTTP {profile_response.status_code}")
                return None
        else:
            print(f"❌ Login: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication: Failed - {e}")
        return None

def test_api_endpoints(token):
    """Test key API endpoints that frontend uses"""
    print("\n📡 Testing API Endpoints")
    print("-" * 40)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints = [
        ('Media List', 'GET', '/api/v1/media/'),
        ('Media Categories', 'GET', '/api/v1/media/categories'),
        ('Playlists', 'GET', '/api/v1/playlists/'),
        ('Settings', 'GET', '/api/v1/settings/'),
        ('Analytics', 'GET', '/api/v1/analytics/dashboard'),
        ('System Version', 'GET', '/api/v1/system/version')
    ]
    
    results = []
    
    for name, method, path in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f"{BACKEND_URL}{path}", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: Working")
                data = response.json()
                
                # Show relevant data structure
                if 'items' in data:
                    print(f"   Items: {len(data['items'])}")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
                elif isinstance(data, dict) and len(data) > 0:
                    print(f"   Keys: {list(data.keys())[:3]}...")
                
                results.append((name, True, response.status_code))
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results.append((name, False, response.status_code))
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append((name, False, str(e)))
    
    return results

def test_cors_configuration():
    """Test CORS configuration for frontend-backend communication"""
    print("\n🌐 Testing CORS Configuration")
    print("-" * 40)
    
    # Test preflight request
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'authorization,content-type'
    }
    
    try:
        response = requests.options(f"{BACKEND_URL}/api/v1/health", 
                                  headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if any(cors_headers.values()):
            print("✅ CORS: Configured")
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
        else:
            print("⚠️ CORS: No headers found")
            
    except Exception as e:
        print(f"❌ CORS: Test failed - {e}")

def generate_summary_report(auth_success, api_results):
    """Generate integration test summary"""
    print("\n" + "=" * 50)
    print("📋 FRONTEND-BACKEND INTEGRATION SUMMARY")
    print("=" * 50)
    
    # Overall status
    total_tests = len(api_results) + 1  # +1 for auth
    passed_tests = sum(1 for _, success, _ in api_results if success)
    if auth_success:
        passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"🎯 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("✅ Status: EXCELLENT - Frontend fully compatible")
    elif success_rate >= 75:
        print("⚠️ Status: GOOD - Minor issues to address")
    else:
        print("❌ Status: NEEDS WORK - Significant compatibility issues")
    
    # Detailed results
    print(f"\n📊 Detailed Results:")
    print(f"   Authentication: {'✅ Working' if auth_success else '❌ Failed'}")
    
    for name, success, status in api_results:
        status_icon = "✅" if success else "❌"
        print(f"   {name}: {status_icon} {status}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if success_rate >= 90:
        print("   • Frontend is ready for production use")
        print("   • All critical API endpoints are functional")
        print("   • Authentication flow is working correctly")
    else:
        failed_endpoints = [name for name, success, _ in api_results if not success]
        if failed_endpoints:
            print(f"   • Fix failing endpoints: {', '.join(failed_endpoints)}")
        if not auth_success:
            print("   • Resolve authentication issues first")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main integration test function"""
    print("🧪 Watch1 Frontend-Backend Integration Test")
    print("=" * 50)
    
    # Test service availability
    if not test_service_availability():
        print("\n❌ Services not available - cannot continue testing")
        sys.exit(1)
    
    # Test authentication
    token = test_authentication_flow()
    auth_success = token is not None
    
    # Test API endpoints
    api_results = []
    if token:
        api_results = test_api_endpoints(token)
    else:
        print("\n⚠️ Skipping API tests - no authentication token")
    
    # Test CORS
    test_cors_configuration()
    
    # Generate summary
    generate_summary_report(auth_success, api_results)

if __name__ == "__main__":
    main()
