#!/usr/bin/env python3
"""
Quick test for artwork/thumbnail issues
"""

import requests

def test_artwork():
    print("Testing Artwork/Thumbnail Issues")
    print("=" * 40)
    
    # Login and get media data
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    
    r = requests.get('http://localhost:8000/api/v1/media/', 
                    headers={'Authorization': f'Bearer {token}'})
    
    items = r.json()['items']
    first_item = items[0]
    
    print("First media item artwork fields:")
    print(f"  artwork: {first_item.get('artwork', 'None')}")
    print(f"  poster_path: {first_item.get('poster_path', 'None')}")
    print(f"  thumbnail_path: {first_item.get('thumbnail_path', 'None')}")
    
    print(f"\nIssue: All artwork fields are likely None/empty")
    print(f"Solution needed: Backend artwork generation or frontend placeholder handling")

if __name__ == "__main__":
    test_artwork()
