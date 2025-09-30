#!/usr/bin/env python3
"""
Production Deployment Validation Script for Watch1 Structured Backend
Validates that production deployment is working correctly
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

def test_production_services():
    """Test that production services are running"""
    print("🔍 Testing Production Services")
    print("-" * 40)
    
    services = [
        ("Backend", "http://localhost:8000/health"),
        ("Frontend", "http://localhost:3000"),
        ("API Health", "http://localhost:8000/api/v1/health")
    ]
    
    results = []
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Available")
                if 'json' in response.headers.get('content-type', ''):
                    data = response.json()
                    if 'version' in data:
                        print(f"   Version: {data['version']}")
                results.append((name, True, response.status_code))
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results.append((name, False, response.status_code))
        except Exception as e:
            print(f"❌ {name}: Connection failed - {e}")
            results.append((name, False, str(e)))
    
    return results

def test_structured_endpoints():
    """Test structured backend endpoints"""
    print("\n🏗️ Testing Structured Backend Endpoints")
    print("-" * 40)
    
    # Test public endpoints first
    public_endpoints = [
        ("System Version", "GET", "/api/v1/system/version"),
        ("Health Detailed", "GET", "/api/v1/system/health-detailed"),
        ("Settings Test", "GET", "/api/v1/settings/test")
    ]
    
    results = []
    
    for name, method, path in public_endpoints:
        try:
            url = f"http://localhost:8000{path}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: Working")
                data = response.json()
                
                # Show relevant info
                if 'architecture' in data:
                    print(f"   Architecture: {data['architecture']}")
                elif 'framework' in data:
                    print(f"   Framework: {data['framework']}")
                
                results.append((name, True, response.status_code))
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results.append((name, False, response.status_code))
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append((name, False, str(e)))
    
    return results

def test_authentication_system():
    """Test authentication system with default credentials"""
    print("\n🔐 Testing Authentication System")
    print("-" * 40)
    
    # Try to login with default credentials
    login_data = {
        "username": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login/access-token", 
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Authentication: Working")
            auth_data = response.json()
            token = auth_data.get('access_token')
            user_info = auth_data.get('user', {})
            print(f"   User: {user_info.get('email', 'unknown')}")
            print(f"   Superuser: {user_info.get('is_superuser', False)}")
            
            # Test authenticated endpoint
            if token:
                headers = {'Authorization': f'Bearer {token}'}
                profile_response = requests.get("http://localhost:8000/api/v1/auth/me", 
                                              headers=headers, timeout=10)
                
                if profile_response.status_code == 200:
                    print("✅ User Profile: Accessible")
                    return True, token
                else:
                    print(f"❌ User Profile: HTTP {profile_response.status_code}")
                    return False, None
            else:
                print("❌ Authentication: No token received")
                return False, None
        else:
            print(f"❌ Authentication: HTTP {response.status_code}")
            if response.status_code == 500:
                print("   ⚠️ Database may not be initialized")
                print("   Run: docker-compose exec watch1-backend python tools/seed-database.py")
            return False, None
            
    except Exception as e:
        print(f"❌ Authentication: Failed - {e}")
        return False, None

def test_database_connectivity():
    """Test database connectivity and basic operations"""
    print("\n🗄️ Testing Database Connectivity")
    print("-" * 40)
    
    try:
        # Test basic database endpoint
        response = requests.get("http://localhost:8000/api/v1/system/health-detailed", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            db_status = data.get('database', {}).get('status', 'unknown')
            db_type = data.get('database', {}).get('type', 'unknown')
            
            if db_status == 'connected':
                print(f"✅ Database: Connected ({db_type})")
                return True
            else:
                print(f"❌ Database: Status {db_status}")
                return False
        else:
            print(f"❌ Database: Health check failed - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database: Test failed - {e}")
        return False

def test_media_endpoints(token):
    """Test media-related endpoints"""
    print("\n📁 Testing Media Endpoints")
    print("-" * 40)
    
    if not token:
        print("⚠️ Skipping media tests - no authentication token")
        return []
    
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints = [
        ("Media Categories", "GET", "/api/v1/media/categories"),
        ("Media List", "GET", "/api/v1/media/"),
        ("Analytics Dashboard", "GET", "/api/v1/analytics/dashboard")
    ]
    
    results = []
    
    for name, method, path in endpoints:
        try:
            url = f"http://localhost:8000{path}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: Working")
                data = response.json()
                
                # Show relevant data
                if isinstance(data, dict):
                    if 'items' in data:
                        print(f"   Items: {len(data['items'])}")
                    elif len(data) > 0:
                        print(f"   Keys: {list(data.keys())[:3]}...")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
                
                results.append((name, True, response.status_code))
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results.append((name, False, response.status_code))
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append((name, False, str(e)))
    
    return results

def check_production_configuration():
    """Check production configuration settings"""
    print("\n⚙️ Checking Production Configuration")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/system/health-detailed", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            env_info = data.get('environment', {})
            
            flask_env = env_info.get('flask_env', 'unknown')
            debug_mode = env_info.get('debug_mode', True)
            
            print(f"Flask Environment: {flask_env}")
            print(f"Debug Mode: {debug_mode}")
            
            # Check configuration
            config_issues = []
            
            if flask_env != 'production':
                config_issues.append("Flask environment should be 'production'")
            
            if debug_mode:
                config_issues.append("Debug mode should be disabled in production")
            
            if config_issues:
                print("⚠️ Configuration Issues:")
                for issue in config_issues:
                    print(f"   • {issue}")
                return False
            else:
                print("✅ Production configuration looks good")
                return True
        else:
            print(f"❌ Configuration check failed - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration check failed - {e}")
        return False

def generate_production_report(service_results, endpoint_results, auth_success, media_results, db_success, config_success):
    """Generate production validation report"""
    print("\n" + "=" * 60)
    print("📋 PRODUCTION DEPLOYMENT VALIDATION REPORT")
    print("=" * 60)
    
    # Calculate overall success rate
    all_results = service_results + endpoint_results + media_results
    total_tests = len(all_results) + 3  # +3 for auth, db, config
    passed_tests = sum(1 for _, success, _ in all_results if success)
    
    if auth_success:
        passed_tests += 1
    if db_success:
        passed_tests += 1
    if config_success:
        passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Deployment status
    if success_rate >= 95:
        print("✅ Status: EXCELLENT - Production ready")
        status = "PRODUCTION_READY"
    elif success_rate >= 85:
        print("⚠️ Status: GOOD - Minor issues to address")
        status = "MOSTLY_READY"
    elif success_rate >= 70:
        print("⚠️ Status: NEEDS WORK - Several issues to fix")
        status = "NEEDS_WORK"
    else:
        print("❌ Status: CRITICAL - Major issues prevent production use")
        status = "NOT_READY"
    
    # Detailed results
    print(f"\n📊 Detailed Test Results:")
    
    print(f"   Services:")
    for name, success, result in service_results:
        icon = "✅" if success else "❌"
        print(f"     {icon} {name}: {result}")
    
    print(f"   Structured Endpoints:")
    for name, success, result in endpoint_results:
        icon = "✅" if success else "❌"
        print(f"     {icon} {name}: {result}")
    
    print(f"   Core Systems:")
    print(f"     {'✅' if auth_success else '❌'} Authentication: {'Working' if auth_success else 'Failed'}")
    print(f"     {'✅' if db_success else '❌'} Database: {'Connected' if db_success else 'Failed'}")
    print(f"     {'✅' if config_success else '❌'} Configuration: {'Valid' if config_success else 'Issues'}")
    
    if media_results:
        print(f"   Media Endpoints:")
        for name, success, result in media_results:
            icon = "✅" if success else "❌"
            print(f"     {icon} {name}: {result}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if status == "PRODUCTION_READY":
        print("   • Deployment is ready for production use")
        print("   • All critical systems are operational")
        print("   • Consider setting up monitoring and backups")
    elif status == "MOSTLY_READY":
        print("   • Address minor issues before production deployment")
        print("   • Most functionality is working correctly")
        print("   • Review failed tests and fix issues")
    else:
        print("   • Fix critical issues before production deployment")
        print("   • Review logs for detailed error information")
        print("   • Consider re-running database initialization")
        
        if not auth_success:
            print("   • Initialize database: docker-compose exec watch1-backend python tools/seed-database.py")
        if not config_success:
            print("   • Review production environment variables in docker-compose.yml")
    
    print(f"\n🕒 Validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return status

def main():
    """Main validation function"""
    print("🧪 Watch1 Production Deployment Validation")
    print("=" * 60)
    
    # Test services
    service_results = test_production_services()
    
    # Test structured endpoints
    endpoint_results = test_structured_endpoints()
    
    # Test authentication
    auth_success, token = test_authentication_system()
    
    # Test database
    db_success = test_database_connectivity()
    
    # Test media endpoints (if authenticated)
    media_results = test_media_endpoints(token)
    
    # Check production configuration
    config_success = check_production_configuration()
    
    # Generate report
    status = generate_production_report(
        service_results, endpoint_results, auth_success, 
        media_results, db_success, config_success
    )
    
    # Exit with appropriate code
    if status == "PRODUCTION_READY":
        sys.exit(0)
    elif status in ["MOSTLY_READY", "NEEDS_WORK"]:
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
