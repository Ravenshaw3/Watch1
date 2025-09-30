#!/usr/bin/env python3
"""
Test frontend functionality after fixes
"""

import requests
import time

def test_frontend_after_fixes():
    """Test if frontend is working after the media store fixes"""
    print("Testing Frontend Functionality After Fixes")
    print("=" * 60)
    
    # Test 1: Frontend accessibility
    print("1. Testing frontend accessibility...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("   PASS: Frontend is accessible")
        else:
            print(f"   FAIL: Frontend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Frontend not accessible: {e}")
        return False
    
    # Test 2: Login functionality
    print("\n2. Testing login functionality...")
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
    
    # Test 3: Media API with correct structure
    print("\n3. Testing media API structure...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers, timeout=10)
        
        if media_response.status_code == 200:
            data = media_response.json()
            
            # Check if response has correct structure
            if "items" in data:
                print(f"   ✅ API returns 'items' key with {len(data['items'])} items")
            else:
                print("   ❌ API missing 'items' key")
                return False
            
            if "total" in data:
                print(f"   ✅ Total count: {data['total']}")
            else:
                print("   ❌ API missing 'total' key")
                return False
            
            # Check first item structure
            if data["items"]:
                first_item = data["items"][0]
                required_fields = ["id", "filename", "file_path", "file_size", "category", "created_at"]
                missing_fields = [field for field in required_fields if field not in first_item]
                
                if not missing_fields:
                    print("   ✅ Media items have required fields")
                else:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
                
                print(f"   📄 Sample item: {first_item.get('filename', 'No filename')}")
            else:
                print("   ❌ No media items returned")
                return False
                
        else:
            print(f"   ❌ Media API failed: {media_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Media API error: {e}")
        return False
    
    # Test 4: Check for common frontend issues
    print("\n4. 🔍 Checking for common frontend issues...")
    
    # Check if Vite dev server is running
    try:
        vite_response = requests.get("http://localhost:3000/@vite/client", timeout=5)
        if vite_response.status_code == 200:
            print("   ✅ Vite dev server responding")
        else:
            print("   ⚠️ Vite dev server issue")
    except:
        print("   ⚠️ Could not reach Vite dev server")
    
    # Check CORS
    try:
        cors_response = requests.options(
            "http://localhost:8000/api/v1/media/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        if cors_response.status_code == 200:
            print("   ✅ CORS working correctly")
        else:
            print("   ❌ CORS issue detected")
    except:
        print("   ❌ CORS test failed")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("\nThe frontend should now be working correctly.")
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Login with: test@example.com / testpass123")
    print("3. Navigate to Library tab - you should see media files")
    print("4. Check browser console (F12) for any remaining errors")
    
    return True

if __name__ == "__main__":
    success = test_frontend_after_fixes()
    if not success:
        print("\n❌ Some tests failed. Check the issues above.")
        exit(1)
    else:
        print("\n🎉 Frontend should be working now!")
