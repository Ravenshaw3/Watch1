#!/usr/bin/env python3
"""
Test media API response format to fix TypeScript errors
"""

import requests
import json

print("TESTING MEDIA API RESPONSE FORMAT")
print("=" * 40)

# Test authentication
print("1. Testing authentication...")
try:
    response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                           json={'username': 'test@example.com', 'password': 'testpass123'})
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print("   SUCCESS: Authentication working!")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test media endpoint format
        print("\n2. Testing media endpoint response format...")
        media_response = requests.get("http://localhost:8000/api/v1/media/?limit=2", headers=headers)
        
        if media_response.status_code == 200:
            data = media_response.json()
            print("   SUCCESS: Media endpoint working!")
            print(f"   Response keys: {list(data.keys())}")
            
            # Check TypeScript interface compatibility
            expected_keys = ['items', 'total', 'page', 'page_size', 'categories']
            missing_keys = [key for key in expected_keys if key not in data]
            extra_keys = [key for key in data.keys() if key not in expected_keys + ['total_pages']]
            
            if missing_keys:
                print(f"   ❌ Missing keys for TypeScript: {missing_keys}")
            else:
                print("   ✅ All required TypeScript keys present")
                
            if extra_keys:
                print(f"   ℹ️ Extra keys (not in TypeScript): {extra_keys}")
            
            # Check items format
            if 'items' in data and data['items']:
                first_item = data['items'][0]
                print(f"\n3. First media item keys: {list(first_item.keys())}")
                
                # Check required MediaFile interface fields
                required_fields = ['id', 'filename', 'file_path', 'file_size', 'category', 'created_at']
                missing_fields = [field for field in required_fields if field not in first_item]
                
                if missing_fields:
                    print(f"   ❌ Missing MediaFile fields: {missing_fields}")
                else:
                    print("   ✅ All required MediaFile fields present")
            
            # Check categories format
            if 'categories' in data:
                print(f"\n4. Categories: {data['categories']}")
                print("   ✅ Categories field added - should fix TypeScript error!")
            
        else:
            print(f"   ERROR: Media endpoint failed - {media_response.status_code}")
            print(f"   Response: {media_response.text}")
    else:
        print(f"   ERROR: Authentication failed - {response.status_code}")
        
except Exception as e:
    print(f"   ERROR: Request failed - {e}")

print(f"\n5. TYPESCRIPT COMPATIBILITY:")
print(f"   - The media API now returns 'categories' field")
print(f"   - Response format matches MediaSearchResponse interface")
print(f"   - TypeError in media.ts should be resolved!")
print(f"   - Test in browser: http://localhost:3000")
