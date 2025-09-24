#!/usr/bin/env python3
"""
Test production deployment
"""

import requests

print("TESTING PRODUCTION DEPLOYMENT")
print("=" * 35)

# Test authentication
print("1. Testing authentication...")
try:
    response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                           json={'username': 'test@example.com', 'password': 'testpass123'})
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print("   SUCCESS: Authentication working!")
        
        # Test media endpoint
        print("\n2. Testing media endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        media_response = requests.get("http://localhost:8000/api/v1/media/?limit=3", headers=headers)
        
        if media_response.status_code == 200:
            data = media_response.json()
            items = data.get('items', [])
            print(f"   SUCCESS: Found {len(items)} media items")
            
            if items:
                # Test first item's poster and streaming
                first_item = items[0]
                media_id = first_item.get('id')
                title = first_item.get('title', 'Unknown')
                
                print(f"\n3. Testing poster for: {title}")
                poster_response = requests.get(f"http://localhost:8000/api/v1/media/{media_id}/poster", headers=headers)
                print(f"   Poster status: {poster_response.status_code}")
                
                print(f"\n4. Testing streaming for: {title}")
                stream_response = requests.head(f"http://localhost:8000/api/v1/media/{media_id}/stream", headers=headers)
                print(f"   Streaming status: {stream_response.status_code}")
                
                if stream_response.status_code == 200:
                    content_length = stream_response.headers.get('Content-Length', 'Unknown')
                    print(f"   File size: {content_length} bytes")
        else:
            print(f"   ERROR: Media endpoint failed - {media_response.status_code}")
    else:
        print(f"   ERROR: Authentication failed - {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ERROR: Request failed - {e}")

print(f"\n5. NEXT STEPS:")
print(f"   - Open http://localhost:3000 in browser")
print(f"   - Login with test@example.com / testpass123")
print(f"   - Check if posters and videos work")
print(f"   - All authentication fixes are now in production!")
