#!/usr/bin/env python3
"""
Debug thumbnail backend endpoint
"""

import requests

def debug_thumbnail_backend():
    print("Debugging Thumbnail Backend")
    print("=" * 30)
    
    # Test the endpoint with detailed error info
    test_url = "http://localhost:8000/thumbnails/c31a561c042447929f1166_poster.jpg"
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text[:200]}...")
        
        if response.status_code == 500:
            print("Server error - check backend logs")
        elif response.status_code == 404:
            print("Not found - checking if file exists in database")
            
            # Login and check database
            login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                 json={'username': 'test@example.com', 'password': 'testpass123'})
            token = login.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get media item
            media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
            items = media_response.json()['items']
            first_item = items[0]
            
            print(f"Database poster_path: {first_item.get('poster_path')}")
            print(f"Database thumbnail_path: {first_item.get('thumbnail_path')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_thumbnail_backend()
