#!/usr/bin/env python3
"""
Debug poster endpoint 500 error
"""

import requests

def debug_poster_endpoint():
    print("DEBUGGING POSTER ENDPOINT 500 ERROR")
    print("=" * 40)
    
    # Login
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get media item
    media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
    if media_response.status_code == 200:
        items = media_response.json()['items']
        
        for i, item in enumerate(items[:3]):
            media_id = item['id']
            title = item.get('title', 'No title')[:30]
            poster_path = item.get('poster_path')
            thumbnail_path = item.get('thumbnail_path')
            
            print(f"\nItem {i+1}: {title}")
            print(f"  Media ID: {media_id}")
            print(f"  poster_path: {poster_path}")
            print(f"  thumbnail_path: {thumbnail_path}")
            
            # Test poster endpoint
            poster_url = f"http://localhost:8000/api/v1/media/{media_id}/poster"
            print(f"  Testing: {poster_url}")
            
            try:
                poster_response = requests.get(poster_url, timeout=5)
                print(f"  Response: {poster_response.status_code}")
                
                if poster_response.status_code != 200:
                    error_text = poster_response.text[:200]
                    print(f"  Error: {error_text}")
                else:
                    content_type = poster_response.headers.get('Content-Type', 'Unknown')
                    content_length = poster_response.headers.get('Content-Length', 'Unknown')
                    print(f"  ✅ Success! Type: {content_type}, Size: {content_length}")
                    
            except Exception as e:
                print(f"  ❌ Request failed: {e}")
    
    # Check backend logs for more details
    print(f"\n💡 Check backend logs with:")
    print(f"   docker logs watch1-backend-dev --tail 20")

if __name__ == "__main__":
    debug_poster_endpoint()
