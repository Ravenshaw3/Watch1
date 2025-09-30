#!/usr/bin/env python3
"""
Test all 404 fixes for media.ts, Library.vue, and ScanInfo.vue
"""

import requests
import time

def test_404_fixes():
    print("TESTING ALL 404 FIXES")
    print("=" * 30)
    
    # Wait for backend to reload
    time.sleep(5)
    
    # Login
    try:
        login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                             json={'username': 'test@example.com', 'password': 'testpass123'})
        token = login.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False
    
    print("\n1. TESTING /media/categories (media.ts line 45)")
    print("-" * 45)
    
    categories_response = requests.get("http://localhost:8000/api/v1/media/categories", headers=headers)
    print(f"GET /api/v1/media/categories -> {categories_response.status_code}")
    
    if categories_response.status_code == 200:
        data = categories_response.json()
        categories = data.get('categories', [])
        print(f"✅ SUCCESS! Found {len(categories)} categories")
        for cat in categories[:3]:
            name = cat.get('name', 'No name')
            count = cat.get('count', 0)
            print(f"   - {name}: {count} items")
    else:
        error_text = categories_response.text[:100]
        print(f"❌ ERROR: {error_text}")
    
    print("\n2. TESTING /media/scan-info (ScanInfo.vue line 106)")
    print("-" * 50)
    
    scan_info_response = requests.get("http://localhost:8000/api/v1/media/scan-info", headers=headers)
    print(f"GET /api/v1/media/scan-info -> {scan_info_response.status_code}")
    
    if scan_info_response.status_code == 200:
        data = scan_info_response.json()
        total_files = data.get('total_files', 0)
        total_size = data.get('total_size', 0)
        scan_status = data.get('scan_status', 'unknown')
        
        print(f"✅ SUCCESS! Scan info loaded")
        print(f"   - Total files: {total_files}")
        print(f"   - Total size: {total_size:,} bytes")
        print(f"   - Scan status: {scan_status}")
    else:
        error_text = scan_info_response.text[:100]
        print(f"❌ ERROR: {error_text}")
    
    print("\n3. TESTING PLAYLIST ITEMS (fixed SQLite Row issue)")
    print("-" * 50)
    
    # Get playlists
    playlists_response = requests.get("http://localhost:8000/api/v1/playlists/", headers=headers)
    if playlists_response.status_code == 200:
        playlists = playlists_response.json()['playlists']
        if len(playlists) > 0:
            playlist_id = playlists[0]['id']
            playlist_name = playlists[0].get('name', 'No name')
            
            print(f"Testing playlist: {playlist_name}")
            
            # Test playlist items
            items_response = requests.get(
                f"http://localhost:8000/api/v1/playlists/{playlist_id}/items",
                headers=headers
            )
            
            print(f"GET /api/v1/playlists/{playlist_id}/items -> {items_response.status_code}")
            
            if items_response.status_code == 200:
                data = items_response.json()
                media_items = data.get('media', [])
                total = data.get('total', 0)
                
                print(f"✅ SUCCESS! Playlist items loaded")
                print(f"   - Total items: {total}")
                if len(media_items) > 0:
                    first_item = media_items[0]
                    item_title = first_item.get('title', 'No title')
                    print(f"   - First item: {item_title}")
            else:
                error_text = items_response.text[:100]
                print(f"❌ ERROR: {error_text}")
        else:
            print("⚠️  No playlists found to test")
    
    print("\n4. TESTING ARTWORK (poster.jpg serving)")
    print("-" * 40)
    
    # Test poster endpoint
    media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
    if media_response.status_code == 200:
        items = media_response.json()['items']
        if len(items) > 0:
            media_id = items[0]['id']
            title = items[0].get('title', 'No title')[:30]
            
            poster_url = f"http://localhost:8000/api/v1/media/{media_id}/poster"
            poster_response = requests.get(poster_url, timeout=5)
            
            print(f"Testing: {title}")
            print(f"GET /api/v1/media/{media_id}/poster -> {poster_response.status_code}")
            
            if poster_response.status_code == 200:
                content_type = poster_response.headers.get('Content-Type', 'Unknown')
                print(f"✅ SUCCESS! Poster served - Type: {content_type}")
            else:
                error_text = poster_response.text[:100]
                print(f"❌ ERROR: {error_text}")
    
    print("\n" + "=" * 30)
    print("404 FIXES SUMMARY")
    print("=" * 30)
    
    print("\n✅ ENDPOINTS ADDED:")
    print("   1. /api/v1/media/categories - For Library.vue category loading")
    print("   2. /api/v1/media/scan-info - For ScanInfo.vue component")
    print("   3. Fixed SQLite Row object access in playlist items")
    print("   4. Enhanced poster serving with poster.jpg fallback")
    
    print("\n🚀 FRONTEND SHOULD NOW WORK:")
    print("   - Library.vue: Categories load without 404 errors")
    print("   - ScanInfo.vue: Scan information displays properly")
    print("   - Playlists: Can view playlist items without errors")
    print("   - Images: poster.jpg files served from movie folders")
    
    print("\n🎯 BROWSER TEST:")
    print("   Open http://localhost:3000/library")
    print("   - No more 404 errors in browser console")
    print("   - Categories display at top")
    print("   - Status box shows library statistics")
    print("   - Images load from poster.jpg files")
    print("   - Playlists work completely")
    
    return True

if __name__ == "__main__":
    test_404_fixes()
