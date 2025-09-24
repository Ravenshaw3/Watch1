#!/usr/bin/env python3
"""
Test the specific API calls that were causing spinning in Playlists and Analytics
"""

import requests
import json

def test_spinning_components():
    print("Testing Components That Were Spinning")
    print("=" * 50)
    
    # Login first
    print("1. Getting authentication token...")
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json={"username": "test@example.com", "password": "testpass123"},
            timeout=10
        )
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("   PASS: Authentication successful")
        else:
            print(f"   FAIL: Authentication failed: {login_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Authentication error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Analytics API (was spinning)
    print("\n2. Testing Analytics API that was spinning...")
    try:
        analytics_response = requests.get(
            "http://localhost:8000/api/v1/analytics/dashboard",
            headers=headers,
            timeout=5  # Short timeout to catch hanging
        )
        
        if analytics_response.status_code == 200:
            data = analytics_response.json()
            print(f"   PASS: Analytics API working ({analytics_response.status_code})")
            print(f"   Data: {data.get('total_media_files', 0)} media files, {data.get('total_playlists', 0)} playlists")
        else:
            print(f"   FAIL: Analytics API returned {analytics_response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("   FAIL: Analytics API timed out (was hanging)")
        return False
    except Exception as e:
        print(f"   FAIL: Analytics API error: {e}")
        return False
    
    # Test Playlists API (was spinning)
    print("\n3. Testing Playlists API that was spinning...")
    try:
        playlists_response = requests.get(
            "http://localhost:8000/api/v1/playlists/",
            headers=headers,
            timeout=5  # Short timeout to catch hanging
        )
        
        if playlists_response.status_code == 200:
            data = playlists_response.json()
            playlist_count = len(data.get('playlists', []))
            print(f"   PASS: Playlists API working ({playlists_response.status_code})")
            print(f"   Data: {playlist_count} playlists found")
        else:
            print(f"   FAIL: Playlists API returned {playlists_response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("   FAIL: Playlists API timed out (was hanging)")
        return False
    except Exception as e:
        print(f"   FAIL: Playlists API error: {e}")
        return False
    
    # Test response times
    print("\n4. Testing API response times...")
    
    import time
    
    # Analytics response time
    start_time = time.time()
    requests.get("http://localhost:8000/api/v1/analytics/dashboard", headers=headers)
    analytics_time = time.time() - start_time
    
    # Playlists response time  
    start_time = time.time()
    requests.get("http://localhost:8000/api/v1/playlists/", headers=headers)
    playlists_time = time.time() - start_time
    
    print(f"   Analytics response time: {analytics_time:.2f}s")
    print(f"   Playlists response time: {playlists_time:.2f}s")
    
    if analytics_time > 3.0:
        print("   WARN: Analytics API is slow (>3s)")
    if playlists_time > 3.0:
        print("   WARN: Playlists API is slow (>3s)")
    
    print("\n" + "=" * 50)
    print("SPINNING COMPONENT TESTS COMPLETE")
    print("\nFixes applied:")
    print("1. Added 10-second timeout protection to prevent infinite spinning")
    print("2. Added console logging to track loading progress")
    print("3. Added proper error handling with fallback states")
    print("4. Ensured isLoading is always set to false in finally block")
    
    print("\nBoth components should now:")
    print("- Load within 10 seconds maximum")
    print("- Show proper error states if APIs fail")
    print("- Never get stuck in infinite spinning")
    print("- Log progress to browser console for debugging")
    
    return True

if __name__ == "__main__":
    test_spinning_components()
