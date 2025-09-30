#!/usr/bin/env python3
"""
Debug playlist 404 error
"""

import requests

def debug_playlist_404():
    print("DEBUGGING PLAYLIST 404 ERROR")
    print("=" * 35)
    
    # Login
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get playlists
    print("1. Testing playlists endpoint...")
    playlists_response = requests.get("http://localhost:8000/api/v1/playlists/", headers=headers)
    print(f"   GET /api/v1/playlists/ -> {playlists_response.status_code}")
    
    if playlists_response.status_code == 200:
        data = playlists_response.json()
        playlists = data.get('playlists', [])
        print(f"   Found {len(playlists)} playlists")
        
        if len(playlists) > 0:
            first_playlist = playlists[0]
            playlist_id = first_playlist.get('id')
            playlist_name = first_playlist.get('name', 'No name')
            print(f"   First playlist: {playlist_name} (ID: {playlist_id})")
            
            # Get media item
            media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
            if media_response.status_code == 200:
                media_items = media_response.json()['items']
                first_media = media_items[0]
                media_id = first_media['id']
                media_title = first_media.get('title', 'No title')
                print(f"   First media: {media_title} (ID: {media_id})")
                
                # Test add to playlist endpoint
                print(f"\n2. Testing add to playlist endpoint...")
                add_url = f"http://localhost:8000/api/v1/playlists/{playlist_id}/items"
                payload = {"media_id": media_id}
                
                print(f"   POST {add_url}")
                print(f"   Payload: {payload}")
                
                add_response = requests.post(add_url, json=payload, headers=headers)
                print(f"   Response: {add_response.status_code}")
                
                if add_response.status_code != 200:
                    print(f"   Error: {add_response.text}")
                    
                    # Check if endpoint exists
                    print(f"\n3. Checking available endpoints...")
                    # Try to get Flask routes
                    try:
                        routes_response = requests.get("http://localhost:8000/", timeout=3)
                        print(f"   Root endpoint: {routes_response.status_code}")
                    except:
                        print("   Could not check routes")
                else:
                    print("   ✅ Add to playlist working!")
            else:
                print(f"   ❌ Media API failed: {media_response.status_code}")
        else:
            print("   ❌ No playlists found")
    else:
        print(f"   ❌ Playlists API failed: {playlists_response.status_code}")

if __name__ == "__main__":
    debug_playlist_404()
