#!/usr/bin/env python3
"""
Test the actual image URLs being generated and their responses
"""

import requests

def test_image_urls():
    print("TESTING MEDIACARD IMAGE URLs")
    print("=" * 35)
    
    # Login first
    try:
        login = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                             json={'username': 'test@example.com', 'password': 'testpass123'})
        token = login.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Get some media items
    media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers)
    if media_response.status_code != 200:
        print(f"❌ Failed to get media: {media_response.status_code}")
        return
    
    items = media_response.json()['items'][:3]  # Test first 3 items
    
    print(f"\nTesting poster URLs for {len(items)} media items:")
    print("-" * 50)
    
    for i, item in enumerate(items, 1):
        media_id = item['id']
        title = item.get('title', 'No title')[:40]
        poster_path = item.get('poster_path')
        
        print(f"\n{i}. {title}")
        print(f"   Media ID: {media_id}")
        print(f"   Database poster_path: {poster_path}")
        
        # Test the poster endpoint URL that frontend would generate
        frontend_url = f"http://localhost:8000/api/v1/media/{media_id}/poster"
        print(f"   Frontend URL: {frontend_url}")
        
        try:
            response = requests.get(frontend_url, timeout=5)
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'Unknown')
                content_length = response.headers.get('Content-Length', 'Unknown')
                print(f"   ✅ SUCCESS! Type: {content_type}, Size: {content_length}")
            elif response.status_code == 404:
                error_data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
                print(f"   ❌ 404 - {error_data}")
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   💥 Request failed: {e}")
    
    print(f"\n" + "=" * 35)
    print("IMAGE URL DIAGNOSIS")
    print("=" * 35)
    
    print(f"\n🔍 FRONTEND URL CONSTRUCTION:")
    print(f"   VITE_API_URL: http://localhost:8000/api/v1")
    print(f"   baseUrl.replace('/api/v1', ''): http://localhost:8000")
    print(f"   Final URL: http://localhost:8000/api/v1/media/{{id}}/poster")
    
    print(f"\n💡 POSSIBLE ISSUES:")
    print(f"   1. Poster files don't exist at database paths")
    print(f"   2. File permissions in container")
    print(f"   3. Windows path mapping issues")
    print(f"   4. Authentication headers missing in frontend")
    
    print(f"\n🔧 DEBUGGING STEPS:")
    print(f"   1. Check browser Network tab for actual requests")
    print(f"   2. Look for CORS errors in browser console")
    print(f"   3. Verify authentication headers in requests")
    print(f"   4. Check if images load when accessed directly")

if __name__ == "__main__":
    test_image_urls()
