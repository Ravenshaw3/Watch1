#!/usr/bin/env python3
"""
Comprehensive diagnosis of the three remaining issues
"""

import requests
import json

def diagnose_all_issues():
    print("COMPREHENSIVE DIAGNOSIS OF THREE ISSUES")
    print("=" * 50)
    
    # Login first
    print("🔐 Authenticating...")
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json={"username": "test@example.com", "password": "testpass123"},
            timeout=10
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✅ Authentication successful")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return False
    
    # Issue 1: Artwork/Thumbnails
    print("\n📸 ISSUE 1: ARTWORK/THUMBNAILS NOT SHOWING")
    print("-" * 45)
    
    try:
        media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers, timeout=5)
        if media_response.status_code == 200:
            items = media_response.json()['items']
            print(f"   ✅ Media API working: {len(items)} items")
            
            # Check first 3 items for image data
            for i, item in enumerate(items[:3]):
                print(f"\n   Item {i+1}: {item.get('title', 'No title')[:40]}...")
                artwork = item.get('artwork')
                poster_path = item.get('poster_path')
                thumbnail_path = item.get('thumbnail_path')
                
                print(f"      artwork: {artwork}")
                print(f"      poster_path: {poster_path}")
                print(f"      thumbnail_path: {thumbnail_path}")
                
                # Test which image would be used
                image_path = artwork or poster_path or thumbnail_path
                if image_path:
                    print(f"      🎯 Would use: {image_path}")
                    
                    # Test if image URL is accessible
                    if image_path.startswith('/'):
                        test_url = f"http://localhost:8000{image_path}"
                        try:
                            img_response = requests.head(test_url, headers=headers, timeout=3)
                            print(f"      🌐 URL test: {test_url} -> {img_response.status_code}")
                        except Exception as e:
                            print(f"      ❌ URL test failed: {e}")
                    elif image_path.startswith('T:'):
                        print(f"      ⚠️  Absolute path (may not be accessible via web): {image_path}")
                else:
                    print(f"      ❌ No image available - will show placeholder")
        else:
            print(f"   ❌ Media API failed: {media_response.status_code}")
    except Exception as e:
        print(f"   ❌ Artwork test failed: {e}")
    
    # Issue 2: Add to Playlist
    print("\n📋 ISSUE 2: ADD TO PLAYLIST FUNCTIONALITY")
    print("-" * 42)
    
    try:
        # Check if playlists exist
        playlists_response = requests.get("http://localhost:8000/api/v1/playlists/", headers=headers, timeout=5)
        if playlists_response.status_code == 200:
            playlists_data = playlists_response.json()
            playlists = playlists_data.get('playlists', [])
            print(f"   ✅ Playlists API working: {len(playlists)} playlists available")
            
            if len(playlists) > 0:
                first_playlist = playlists[0]
                print(f"   📝 First playlist: {first_playlist.get('name', 'No name')}")
                playlist_id = first_playlist.get('id')
                
                # Test add to playlist API
                if playlist_id and len(items) > 0:
                    first_media_id = items[0].get('id')
                    print(f"   🎬 First media ID: {first_media_id}")
                    
                    # Test the add playlist item endpoint (don't actually add, just test structure)
                    test_payload = {"media_id": first_media_id}
                    print(f"   🧪 Would POST to: /api/v1/playlists/{playlist_id}/items")
                    print(f"   📦 Payload: {test_payload}")
                    print(f"   ❌ UI MISSING: No 'Add to Playlist' button in MediaCard component")
            else:
                print(f"   ⚠️  No playlists available to add to")
        else:
            print(f"   ❌ Playlists API failed: {playlists_response.status_code}")
    except Exception as e:
        print(f"   ❌ Playlist test failed: {e}")
    
    # Issue 3: Media Library Status Area
    print("\n📊 ISSUE 3: MEDIA LIBRARY STATUS AREA")
    print("-" * 37)
    
    try:
        # Check pagination data from API
        media_response = requests.get("http://localhost:8000/api/v1/media/?page=1&page_size=24", headers=headers, timeout=5)
        if media_response.status_code == 200:
            data = media_response.json()
            total = data.get('total', 0)
            page = data.get('page', 1)
            page_size = data.get('page_size', 24)
            items_count = len(data.get('items', []))
            
            print(f"   ✅ Pagination API working")
            print(f"   📊 API Response:")
            print(f"      total: {total}")
            print(f"      page: {page}")
            print(f"      page_size: {page_size}")
            print(f"      items_count: {items_count}")
            
            # Calculate what status should show
            start_item = (page - 1) * page_size + 1
            end_item = min(page * page_size, total)
            expected_status = f"Showing {start_item} to {end_item} of {total} results"
            print(f"   🎯 Expected status: {expected_status}")
            
            if total == 0:
                print(f"   ❌ PROBLEM: total is 0, status area won't show meaningful data")
            elif items_count == 0:
                print(f"   ❌ PROBLEM: no items returned, status area may not render")
            else:
                print(f"   ✅ Data looks good for status area")
        else:
            print(f"   ❌ Media API failed: {media_response.status_code}")
    except Exception as e:
        print(f"   ❌ Status area test failed: {e}")
    
    # Frontend accessibility test
    print(f"\n🌐 FRONTEND ACCESSIBILITY TEST")
    print("-" * 32)
    try:
        frontend_response = requests.get("http://localhost:3000/library", timeout=5)
        if frontend_response.status_code == 200:
            print("   ✅ Library page accessible")
        else:
            print(f"   ❌ Library page returned: {frontend_response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
    
    print(f"\n" + "=" * 50)
    print("DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    print("\n🔧 REQUIRED FIXES:")
    print("1. 📸 Artwork: Check image URL accessibility and authentication")
    print("2. 📋 Playlist: Implement 'Add to Playlist' UI in MediaCard component")
    print("3. 📊 Status: Verify frontend is using correct API response fields")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Test actual frontend in browser: http://localhost:3000/library")
    print("2. Check browser console (F12) for JavaScript errors")
    print("3. Implement missing UI components")
    
    return True

if __name__ == "__main__":
    diagnose_all_issues()
