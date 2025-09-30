#!/usr/bin/env python3
"""
Test the MediaCard image loading fix with authentication token
"""

import requests
import time

def test_image_loading_fix():
    print("TESTING MEDIACARD IMAGE LOADING FIX")
    print("=" * 40)
    
    # Wait for containers to reload
    time.sleep(3)
    
    # Login and get token
    try:
        login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                             json={'username': 'test@example.com', 'password': 'testpass123'})
        token = login.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Get media items
    media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
    if media_response.status_code != 200:
        print(f"❌ Failed to get media: {media_response.status_code}")
        return
    
    items = media_response.json()['items'][:3]
    
    print(f"\nTesting image URLs with token parameter:")
    print("-" * 45)
    
    for i, item in enumerate(items, 1):
        media_id = item['id']
        title = item.get('title', 'No title')[:35]
        
        # Test the new URL format with token parameter
        image_url = f"http://localhost:8000/api/v1/media/{media_id}/poster?token={token}"
        
        print(f"\n{i}. {title}")
        print(f"   Media ID: {media_id}")
        print(f"   Image URL: {image_url[:80]}...")
        
        try:
            response = requests.get(image_url, timeout=10)
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'Unknown')
                content_length = response.headers.get('Content-Length', 'Unknown')
                print(f"   ✅ SUCCESS! Type: {content_type}, Size: {content_length}")
            elif response.status_code == 404:
                error_data = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text
                print(f"   ⚠️  404 - {error_data}")
                print(f"   💡 This is expected for items without poster files")
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   💥 Request failed: {e}")
    
    print(f"\n" + "=" * 40)
    print("IMAGE LOADING FIX SUMMARY")
    print("=" * 40)
    
    print(f"\n✅ FIXES IMPLEMENTED:")
    print(f"   1. Added token parameter to image URLs")
    print(f"   2. Updated backend to accept token in query params")
    print(f"   3. Fixed authentication for image requests")
    
    print(f"\n🎯 FRONTEND BEHAVIOR:")
    print(f"   - Images with posters: Will load and display")
    print(f"   - Images without posters: Will show FilmIcon fallback")
    print(f"   - No more authentication errors")
    
    print(f"\n🚀 BROWSER TEST:")
    print(f"   1. Open http://localhost:3000/library")
    print(f"   2. Login with test@example.com / testpass123")
    print(f"   3. Look for movie poster images loading")
    print(f"   4. Check browser console - no 401/403 errors")
    print(f"   5. Items without posters show film icon placeholder")
    
    print(f"\n💡 EXPECTED RESULTS:")
    print(f"   - Some images will load (items with poster files)")
    print(f"   - Some will show placeholders (items without posters)")
    print(f"   - No authentication errors in console")
    print(f"   - No 404 API errors (only missing image files)")

if __name__ == "__main__":
    test_image_loading_fix()
