#!/usr/bin/env python3
"""
Check database tables
"""

import requests

def check_database():
    print("CHECKING DATABASE TABLES")
    print("=" * 30)
    
    # Check if playlist_items table exists by trying to add an item
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get playlists and media
    playlists_response = requests.get("http://localhost:8000/api/v1/playlists/", headers=headers)
    media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
    
    if playlists_response.status_code == 200 and media_response.status_code == 200:
        playlists = playlists_response.json()['playlists']
        media_items = media_response.json()['items']
        
        if len(playlists) > 0 and len(media_items) > 0:
            playlist_id = playlists[0]['id']
            media_id = media_items[0]['id']
            
            print(f"Testing add to playlist...")
            print(f"Playlist ID: {playlist_id}")
            print(f"Media ID: {media_id}")
            
            # Try to add item
            add_response = requests.post(
                f"http://localhost:8000/api/v1/playlists/{playlist_id}/items",
                json={"media_id": media_id},
                headers=headers
            )
            
            print(f"Add response: {add_response.status_code}")
            if add_response.status_code != 200:
                print(f"Error: {add_response.text}")
            else:
                print("✅ Add to playlist working!")
                
                # Test getting playlist items
                get_response = requests.get(
                    f"http://localhost:8000/api/v1/playlists/{playlist_id}/items",
                    headers=headers
                )
                print(f"Get items response: {get_response.status_code}")
                if get_response.status_code == 200:
                    items = get_response.json()
                    print(f"Playlist has {items.get('total', 0)} items")

if __name__ == "__main__":
    check_database()
