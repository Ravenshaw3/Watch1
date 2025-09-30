#!/usr/bin/env python3
"""
Simple Database Check - Verify database population and frontend access
"""

import requests
import json
import sys

def test_database_population():
    """Test if database is properly populated"""
    print("DATABASE POPULATION CHECK")
    print("========================")
    
    # Authenticate
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login/access-token", 
                               json={"username": "test@example.com", "password": "testpass123"},
                               timeout=10)
        if response.status_code != 200:
            print(f"ERROR: Authentication failed: {response.status_code}")
            return False
            
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("SUCCESS: Authentication successful")
        
    except Exception as e:
        print(f"ERROR: Authentication error: {e}")
        return False
    
    # Check media endpoint
    try:
        response = requests.get("http://localhost:8000/api/v1/media/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_items = data.get('total', 0)
            items = data.get('items', [])
            categories = data.get('categories', {})
            
            print(f"\nMEDIA DATABASE STATUS:")
            print(f"  - Total Items: {total_items}")
            print(f"  - Items in Response: {len(items)}")
            print(f"  - Categories: {len(categories)}")
            
            if categories:
                print(f"  - Category Breakdown:")
                for category, count in categories.items():
                    print(f"    * {category}: {count} items")
            
            if items:
                print(f"\n  - Sample Media Items:")
                for i, item in enumerate(items[:5]):
                    title = item.get('title', 'Unknown')
                    category = item.get('category', 'Unknown')
                    file_size = item.get('file_size', 0)
                    size_mb = round(file_size / (1024*1024), 1) if file_size else 0
                    print(f"    {i+1}. {title} [{category}] - {size_mb}MB")
            
            return total_items > 0
        else:
            print(f"ERROR: Media API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Media API error: {e}")
        return False

def test_frontend_access():
    """Test if frontend is accessible"""
    print("\nFRONTEND ACCESS CHECK")
    print("====================")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for Vue.js indicators
            vue_indicators = ["vue", "vite", "app", "main"]
            found_indicators = [ind for ind in vue_indicators if ind in content.lower()]
            
            print(f"SUCCESS: Frontend accessible at http://localhost:3000")
            print(f"  - Response size: {len(content)} characters")
            print(f"  - Vue indicators found: {', '.join(found_indicators) if found_indicators else 'None'}")
            
            # Check for specific Watch1 content
            watch1_indicators = ["watch1", "media", "library", "login"]
            found_watch1 = [ind for ind in watch1_indicators if ind in content.lower()]
            
            if found_watch1:
                print(f"  - Watch1 content detected: {', '.join(found_watch1)}")
            
            return True
        else:
            print(f"ERROR: Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Frontend connection error: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    print("\nAPI ENDPOINTS CHECK")
    print("==================")
    
    # Authenticate
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login/access-token", 
                               json={"username": "test@example.com", "password": "testpass123"},
                               timeout=10)
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
    except:
        print("ERROR: Could not authenticate for API tests")
        return False
    
    endpoints = [
        ("/api/v1/media/", "Media List"),
        ("/api/v1/media/categories", "Categories"),
        ("/api/v1/playlists/", "Playlists"),
        ("/api/v1/settings/media-directories", "Settings"),
        ("/api/v1/analytics/dashboard", "Analytics")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"SUCCESS: {name} - 200 OK")
                results[name] = True
            else:
                print(f"ERROR: {name} - {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"ERROR: {name} - {e}")
            results[name] = False
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"\nAPI ENDPOINTS: {success_count}/{total_count} working")
    return success_count == total_count

def main():
    """Main test runner"""
    print("WATCH1 DATABASE AND FRONTEND CHECK")
    print("==================================")
    
    # Run all tests
    database_ok = test_database_population()
    frontend_ok = test_frontend_access()
    api_ok = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("OVERALL SYSTEM STATUS")
    print("=" * 50)
    
    tests = {
        "Database Population": database_ok,
        "Frontend Access": frontend_ok,
        "API Endpoints": api_ok
    }
    
    for test_name, result in tests.items():
        status = "SUCCESS" if result else "FAILED"
        indicator = "[OK]" if result else "[FAIL]"
        print(f"{test_name:20} | {status:7} | {indicator}")
    
    success_count = sum(1 for result in tests.values() if result)
    total_count = len(tests)
    
    print(f"\nOVERALL: {success_count}/{total_count} systems working")
    
    if success_count == total_count:
        print("\nRESULT: Database is populated and all views can access the data!")
        print("ACTION: Open http://localhost:3000 in your browser")
        print("LOGIN: test@example.com / testpass123")
    else:
        print("\nRESULT: Some issues detected - check individual components")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
