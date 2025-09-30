#!/usr/bin/env python3
"""
Test if backend serves thumbnail files
"""

import requests

def test_thumbnail_endpoint():
    print("Testing Thumbnail Endpoint")
    print("=" * 30)
    
    # Login
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test thumbnail URL
    test_url = "http://localhost:8000/thumbnails/c31a561c042447929f1166_poster.jpg"
    
    print(f"Testing: {test_url}")
    
    # Test without auth
    response1 = requests.get(test_url, timeout=5)
    print(f"Without auth: {response1.status_code}")
    
    # Test with auth header
    response2 = requests.get(test_url, headers=headers, timeout=5)
    print(f"With auth header: {response2.status_code}")
    
    # Test with token as query param
    response3 = requests.get(f"{test_url}?token={token}", timeout=5)
    print(f"With token param: {response3.status_code}")
    
    if response2.status_code == 404:
        print("\n❌ PROBLEM: Backend not serving /thumbnails/ endpoint")
        print("   Need to implement thumbnail serving in Flask backend")
    elif response2.status_code == 401:
        print("\n❌ PROBLEM: Authentication required but not working")
        print("   Need to fix thumbnail authentication")
    elif response2.status_code == 200:
        print("\n✅ Thumbnails working!")
    else:
        print(f"\n❓ Unexpected response: {response2.status_code}")

if __name__ == "__main__":
    test_thumbnail_endpoint()
