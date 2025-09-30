#!/usr/bin/env python3
"""
Test the current API to see what's actually working
"""

import requests

def test_current_api():
    print("TESTING CURRENT API STATUS")
    print("=" * 30)
    
    # Login
    try:
        login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                             json={'username': 'test@example.com', 'password': 'testpass123'})
        if login.status_code == 200:
            token = login.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {login.status_code}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test playlist items endpoint
    print("\nTesting playlist items...")
    playlists_response = requests.get("http://localhost:8000/api/v1/playlists/", headers=headers)
    if playlists_response.status_code == 200:
        playlists = playlists_response.json()['playlists']
        print(f"✅ Found {len(playlists)} playlists")
        
        if len(playlists) > 0:
            playlist_id = playlists[0]['id']
            playlist_name = playlists[0].get('name', 'No name')
            
            print(f"\nTesting playlist items for: {playlist_name}")
            items_response = requests.get(
                f"http://localhost:8000/api/v1/playlists/{playlist_id}/items",
                headers=headers
            )
            
            if items_response.status_code == 200:
                data = items_response.json()
                media_items = data.get('media', [])
                print(f"✅ Playlist has {len(media_items)} items")
                
                for i, item in enumerate(media_items[:3]):
                    title = item.get('title', 'No title')
                    filename = item.get('filename', 'No filename')
                    print(f"  {i+1}. Title: {title}")
                    print(f"     Filename: {filename}")
            else:
                print(f"❌ Playlist items failed: {items_response.status_code}")
                print(f"    Response: {items_response.text}")
    else:
        print(f"❌ Playlists failed: {playlists_response.status_code}")
    
    print(f"\n" + "=" * 30)
    print("CURRENT STATUS")
    print("=" * 30)
    print("The issue might be:")
    print("1. Database is working (API responds)")
    print("2. But titles are not properly extracted")
    print("3. Names in playlists show filenames instead of clean titles")
    print("\nSolution: Update backend to clean titles on-the-fly")

if __name__ == "__main__":
    test_current_api()
