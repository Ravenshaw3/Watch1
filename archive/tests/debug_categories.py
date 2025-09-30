#!/usr/bin/env python3
"""
Debug categories issue in media API
"""

import requests
import json

print("DEBUGGING CATEGORIES ISSUE")
print("=" * 30)

# Test authentication
print("1. Testing authentication...")
try:
    response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                           json={'username': 'test@example.com', 'password': 'testpass123'})
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print("   ✅ Authentication working")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test media endpoint with detailed response
        print("\n2. Testing media endpoint response...")
        media_response = requests.get("http://localhost:8000/api/v1/media/?limit=1", headers=headers)
        
        if media_response.status_code == 200:
            data = media_response.json()
            print("   ✅ Media endpoint working")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Check specifically for categories
            if 'categories' in data:
                print(f"   ✅ Categories found: {data['categories']}")
            else:
                print("   ❌ Categories field missing!")
                print(f"   Available keys: {list(data.keys())}")
        else:
            print(f"   ❌ Media endpoint failed: {media_response.status_code}")
            print(f"   Response: {media_response.text}")
    else:
        print(f"   ❌ Authentication failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

print(f"\n3. EXPECTED VS ACTUAL:")
print(f"   Expected keys: ['items', 'total', 'page', 'page_size', 'categories']")
print(f"   The 'categories' field is required by TypeScript MediaSearchResponse interface")
print(f"   This field should contain category counts like: {{'movies': 10, 'tv_shows': 5}}")
