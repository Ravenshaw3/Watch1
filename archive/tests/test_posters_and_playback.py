#!/usr/bin/env python3
"""
Test poster display and movie playback issues
"""

import requests
import time

def test_authentication_and_media():
    print("TESTING POSTERS AND MOVIE PLAYBACK")
    print("=" * 40)
    
    # Step 1: Login
    print("1. Testing authentication...")
    try:
        login_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                     json={'username': 'test@example.com', 'password': 'testpass123'})
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print("   SUCCESS: Login working")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ERROR: Login failed - {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ERROR: Login request failed - {e}")
        return
    
    # Step 2: Get media files
    print("\n2. Getting media files...")
    try:
        media_response = requests.get("http://localhost:8000/api/v1/media/?limit=3", headers=headers)
        if media_response.status_code == 200:
            data = media_response.json()
            items = data.get('items', [])
            print(f"   SUCCESS: Found {len(items)} media items")
            
            if not items:
                print("   ERROR: No media items to test")
                return
                
        else:
            print(f"   ERROR: Media API failed - {media_response.status_code}")
            return
    except Exception as e:
        print(f"   ERROR: Media request failed - {e}")
        return
    
    # Step 3: Test poster URLs
    print("\n3. Testing poster URLs...")
    for i, item in enumerate(items):
        title = item.get('title', 'Unknown')
        media_id = item.get('id')
        
        print(f"   Testing: {title}")
        
        # Test poster endpoint with token in header
        poster_url_header = f"http://localhost:8000/api/v1/media/{media_id}/poster"
        try:
            poster_response = requests.get(poster_url_header, headers=headers, timeout=5)
            print(f"      Header auth: {poster_response.status_code}")
        except Exception as e:
            print(f"      Header auth: ERROR - {e}")
        
        # Test poster endpoint with token in query (for img tags)
        poster_url_query = f"http://localhost:8000/api/v1/media/{media_id}/poster?token={token}"
        try:
            poster_response = requests.get(poster_url_query, timeout=5)
            print(f"      Query auth: {poster_response.status_code}")
            if poster_response.status_code == 200:
                content_type = poster_response.headers.get('Content-Type', 'Unknown')
                print(f"      Content-Type: {content_type}")
        except Exception as e:
            print(f"      Query auth: ERROR - {e}")
    
    # Step 4: Test streaming URLs
    print("\n4. Testing streaming URLs...")
    for i, item in enumerate(items[:2]):  # Test first 2 items
        title = item.get('title', 'Unknown')
        media_id = item.get('id')
        
        print(f"   Testing: {title}")
        
        # Test streaming endpoint with token in header
        stream_url_header = f"http://localhost:8000/api/v1/media/{media_id}/stream"
        try:
            # Use HEAD request to test without downloading
            stream_response = requests.head(stream_url_header, headers=headers, timeout=5)
            print(f"      Header auth: {stream_response.status_code}")
            if stream_response.status_code == 200:
                content_length = stream_response.headers.get('Content-Length', 'Unknown')
                content_type = stream_response.headers.get('Content-Type', 'Unknown')
                print(f"      Size: {content_length}, Type: {content_type}")
        except Exception as e:
            print(f"      Header auth: ERROR - {e}")
        
        # Test streaming endpoint with token in query
        stream_url_query = f"http://localhost:8000/api/v1/media/{media_id}/stream?token={token}"
        try:
            stream_response = requests.head(stream_url_query, timeout=5)
            print(f"      Query auth: {stream_response.status_code}")
        except Exception as e:
            print(f"      Query auth: ERROR - {e}")
    
    print("\n5. DIAGNOSIS:")
    print("   If posters not displaying:")
    print("   - Check if poster endpoints return 200")
    print("   - Verify MediaCardNew.vue uses correct token method")
    print("   - Check browser console for CORS errors")
    print("   ")
    print("   If movies don't play:")
    print("   - Check if streaming endpoints return 200")
    print("   - Verify video player authentication")
    print("   - Check for range request support")
    print("   - Look for CORS issues in browser")
    
    print("\n6. FRONTEND DEBUGGING:")
    print("   Open browser DevTools and check:")
    print("   - Console tab for JavaScript errors")
    print("   - Network tab for failed requests")
    print("   - Look for 401/403 authentication errors")
    print("   - Check if URLs include proper tokens")

if __name__ == "__main__":
    test_authentication_and_media()
