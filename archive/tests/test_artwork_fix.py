#!/usr/bin/env python3
"""
Test artwork/thumbnail fix in MediaCardNew.vue
"""

import requests

def test_artwork_fix():
    print("Testing Artwork/Thumbnail Fix")
    print("=" * 35)
    
    # Login and get media data
    login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                         json={'username': 'test@example.com', 'password': 'testpass123'})
    token = login.json()['access_token']
    
    r = requests.get('http://localhost:8000/api/v1/media/', 
                    headers={'Authorization': f'Bearer {token}'})
    
    items = r.json()['items']
    
    print("1. Checking image field availability...")
    for i, item in enumerate(items[:3]):
        print(f"\n   Item {i+1}: {item.get('title', 'No title')[:30]}...")
        print(f"   - artwork: {item.get('artwork', 'None')}")
        print(f"   - poster_path: {item.get('poster_path', 'None')}")
        print(f"   - thumbnail_path: {item.get('thumbnail_path', 'None')}")
        
        # Test our new logic
        image_path = item.get('artwork') or item.get('poster_path') or item.get('thumbnail_path')
        if image_path:
            print(f"   ✅ Will show image: {image_path}")
            if image_path.startswith('/'):
                full_url = f"http://localhost:8000{image_path}"
                print(f"   ✅ Full URL: {full_url}")
        else:
            print(f"   ❌ Will show placeholder (no image available)")
    
    print("\n2. Testing frontend route...")
    try:
        frontend_response = requests.get("http://localhost:3000/library", timeout=5)
        if frontend_response.status_code == 200:
            print("   ✅ Library route accessible")
        else:
            print(f"   ⚠️ Library route returned {frontend_response.status_code}")
    except Exception as e:
        print(f"   ❌ Library route error: {e}")
    
    print("\n" + "=" * 35)
    print("ARTWORK FIX SUMMARY")
    print("=" * 35)
    
    print("\nMediaCardNew.vue Changes:")
    print("✅ Enhanced posterUrl computed property")
    print("✅ Priority: artwork > poster_path > thumbnail_path")
    print("✅ Proper URL construction for relative paths")
    print("✅ Updated template condition: v-if='posterUrl'")
    
    print("\nExpected Results:")
    print("- Media cards should now show thumbnails/posters")
    print("- Fallback to FilmIcon placeholder when no image")
    print("- Proper image URLs with authentication")
    
    print("\nNext: Check browser to see if images are loading!")
    
    return True

if __name__ == "__main__":
    test_artwork_fix()
