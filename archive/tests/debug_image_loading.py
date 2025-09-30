#!/usr/bin/env python3
"""
Debug image loading issues
"""

import requests

def debug_image_loading():
    print("DEBUGGING IMAGE LOADING ISSUES")
    print("=" * 35)
    
    # Login and get media data
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    r = requests.get('http://localhost:8000/api/v1/media/', headers=headers)
    items = r.json()['items']
    
    print("Checking image paths in database:")
    for i, item in enumerate(items[:3]):
        print(f"\nItem {i+1}: {item.get('title', 'No title')[:40]}...")
        artwork = item.get('artwork')
        poster_path = item.get('poster_path')
        thumbnail_path = item.get('thumbnail_path')
        
        print(f"  artwork: {artwork}")
        print(f"  poster_path: {poster_path}")
        print(f"  thumbnail_path: {thumbnail_path}")
        
        # Check what type of paths we have
        if poster_path:
            if poster_path.startswith('/thumbnails/'):
                print(f"  → Relative web path: {poster_path}")
                test_url = f"http://localhost:8000{poster_path}"
                print(f"  → Testing: {test_url}")
                try:
                    resp = requests.head(test_url, timeout=3)
                    print(f"  → Status: {resp.status_code}")
                except Exception as e:
                    print(f"  → Error: {e}")
            elif poster_path.startswith('T:'):
                print(f"  → Absolute file path (PROBLEM): {poster_path}")
                print(f"  → Browsers cannot load local file paths!")
            else:
                print(f"  → Unknown path format: {poster_path}")

if __name__ == "__main__":
    debug_image_loading()
