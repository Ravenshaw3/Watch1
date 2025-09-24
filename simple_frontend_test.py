#!/usr/bin/env python3
"""
Simple frontend test without emojis
"""

import requests

def test_frontend():
    print("Testing Frontend Functionality After Fixes")
    print("=" * 50)
    
    # Test login
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
    
    # Test media API
    print("2. Testing media API...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers, timeout=10)
        
        if media_response.status_code == 200:
            data = media_response.json()
            
            if "items" in data:
                print(f"   PASS: API returns 'items' key with {len(data['items'])} items")
            else:
                print("   FAIL: API missing 'items' key")
                return False
            
            if "total" in data:
                print(f"   PASS: Total count: {data['total']}")
            else:
                print("   FAIL: API missing 'total' key")
                return False
            
            if data["items"]:
                first_item = data["items"][0]
                print(f"   PASS: Sample item: {first_item.get('filename', 'No filename')}")
            else:
                print("   FAIL: No media items returned")
                return False
                
        else:
            print(f"   FAIL: Media API failed: {media_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Media API error: {e}")
        return False
    
    # Test frontend
    print("3. Testing frontend accessibility...")
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
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("\nThe frontend should now be working correctly.")
    print("Open http://localhost:3000 and login with test@example.com / testpass123")
    
    return True

if __name__ == "__main__":
    test_frontend()
