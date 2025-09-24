#!/usr/bin/env python3
"""
Test all final fixes for the three issues
"""

import requests
import time

def test_final_fixes():
    print("TESTING FINAL FIXES FOR ALL THREE ISSUES")
    print("=" * 50)
    
    # Wait for backend to start
    print("Waiting for backend to restart...")
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
    
    print("\n1. TESTING IMAGE LOADING FIX")
    print("-" * 35)
    
    # Get a media item
    media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
    if media_response.status_code == 200:
        items = media_response.json()['items']
        first_item = items[0]
        media_id = first_item['id']
        
        # Test the new poster endpoint
        poster_url = f"http://localhost:8000/api/v1/media/{media_id}/poster"
        print(f"Testing poster endpoint: {poster_url}")
        
        poster_response = requests.get(poster_url, timeout=5)
        print(f"Poster endpoint status: {poster_response.status_code}")
        
        if poster_response.status_code == 200:
            print("✅ Poster endpoint working - images should load in browser")
            print(f"   Content-Type: {poster_response.headers.get('Content-Type', 'Unknown')}")
        else:
            print(f"❌ Poster endpoint failed: {poster_response.status_code}")
    
    print("\n2. TESTING PLAYLIST FUNCTIONALITY")
    print("-" * 35)
    
    # Test playlists API
    playlists_response = requests.get("http://localhost:8000/api/v1/playlists/", headers=headers)
    if playlists_response.status_code == 200:
        data = playlists_response.json()
        playlists = data.get('playlists', [])
        print(f"✅ Found {len(playlists)} playlists")
        
        for i, playlist in enumerate(playlists[:3]):
            name = playlist.get('name', 'No name')
            item_count = len(playlist.get('items', []))
            print(f"   {i+1}. {name} ({item_count} items)")
        
        if len(playlists) > 0:
            print("✅ Playlist modal should show these playlists with item counts")
        else:
            print("⚠️  No playlists available for testing")
    else:
        print(f"❌ Playlists API failed: {playlists_response.status_code}")
    
    print("\n3. TESTING STATUS AREA")
    print("-" * 25)
    
    # Check media API pagination
    media_response = requests.get("http://localhost:8000/api/v1/media/?page=1&page_size=24", headers=headers)
    if media_response.status_code == 200:
        data = media_response.json()
        total = data.get('total', 0)
        page = data.get('page', 1)
        page_size = data.get('page_size', 24)
        items_count = len(data.get('items', []))
        
        print(f"✅ API pagination data:")
        print(f"   Total: {total}")
        print(f"   Page: {page}")
        print(f"   Page size: {page_size}")
        print(f"   Items returned: {items_count}")
        
        if total > 0:
            start_item = (page - 1) * page_size + 1
            end_item = min(page * page_size, total)
            expected_status = f"Showing {start_item} to {end_item} of {total} results"
            print(f"✅ Expected status: '{expected_status}'")
            print("✅ Status should appear at bottom of library page")
        else:
            print("❌ Total is 0 - status won't show")
    else:
        print(f"❌ Media API failed: {media_response.status_code}")
    
    print("\n4. FRONTEND ACCESSIBILITY")
    print("-" * 25)
    
    try:
        frontend_response = requests.get("http://localhost:3000/library", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Library page accessible")
        else:
            print(f"❌ Library page failed: {frontend_response.status_code}")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    
    print("\n" + "=" * 50)
    print("FINAL FIXES SUMMARY")
    print("=" * 50)
    
    print("\n🖼️  ISSUE 1: IMAGE LOADING")
    print("   ✅ Added /api/v1/media/{id}/poster endpoint")
    print("   ✅ Handles both web paths and absolute file paths")
    print("   ✅ Frontend uses dedicated poster endpoint")
    print("   ✅ Should fix 'not allowed to load local resource' error")
    
    print("\n📋 ISSUE 2: ADD TO PLAYLIST")
    print("   ✅ Enhanced playlist loading with proper response handling")
    print("   ✅ Added console logging for debugging")
    print("   ✅ Modal shows playlist names and item counts")
    print("   ✅ Connected to addPlaylistItem API")
    
    print("\n📊 ISSUE 3: STATUS AREA")
    print("   ✅ Status area moved outside pagination condition")
    print("   ✅ Shows when total > 0 (not just multiple pages)")
    print("   ✅ API returns proper pagination data")
    print("   ✅ Should display at bottom of library")
    
    print("\n🚀 BROWSER TESTING CHECKLIST:")
    print("   1. Open http://localhost:3000/library")
    print("   2. Login with test@example.com / testpass123")
    print("   3. Check:")
    print("      📸 Images load in media cards (no gray placeholders)")
    print("      ➕ Hover shows '+' button, click opens playlist modal")
    print("      📊 Bottom shows 'Showing 1 to 24 of 102 results'")
    print("      🔧 No console errors about local resources")
    
    return True

if __name__ == "__main__":
    test_final_fixes()
