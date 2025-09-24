#!/usr/bin/env python3
"""
Test script to verify Watch1 backend API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

def test_login():
    """Test login and get access token"""
    print("🔐 Testing login...")
    
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/access-token", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_media_list(token):
    """Test media list endpoint"""
    print("\n📁 Testing media list...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/media/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        media_count = len(data.get("items", []))
        print(f"✅ Media list successful! Found {media_count} media files")
        
        if media_count > 0:
            first_media = data["items"][0]
            media_id = first_media.get("id")
            print(f"📄 First media: {first_media.get('original_filename')} (ID: {media_id})")
            return media_id
    else:
        print(f"❌ Media list failed: {response.status_code} - {response.text}")
    
    return None

def test_media_by_id(token, media_id):
    """Test getting individual media by ID"""
    print(f"\n🎬 Testing media by ID: {media_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/media/{media_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Media by ID successful!")
        print(f"   Title: {data.get('original_filename')}")
        print(f"   File Path: {data.get('file_path')}")
        print(f"   Size: {data.get('file_size', 0) / (1024*1024):.1f} MB")
        return True
    else:
        print(f"❌ Media by ID failed: {response.status_code} - {response.text}")
        return False

def test_media_stream(token, media_id):
    """Test media streaming endpoint"""
    print(f"\n🎥 Testing media stream: {media_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.head(f"{BASE_URL}/media/{media_id}/stream", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Media stream HEAD request successful!")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {response.headers.get('Content-Length')}")
        return True
    else:
        print(f"❌ Media stream failed: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🎬 Watch1 Backend API Test")
    print("=" * 40)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot continue without valid token")
        exit(1)
    
    # Test media list
    media_id = test_media_list(token)
    if not media_id:
        print("❌ Cannot continue without media ID")
        exit(1)
    
    # Test individual media
    success = test_media_by_id(token, media_id)
    if not success:
        print("❌ Individual media test failed")
        exit(1)
    
    # Test streaming
    success = test_media_stream(token, media_id)
    if not success:
        print("❌ Media streaming test failed")
        exit(1)
    
    print("\n🎉 All tests passed! Backend API is working correctly.")
