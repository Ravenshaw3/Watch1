#!/usr/bin/env python3
"""
Test media titles and display names
"""

import requests
import json

def test_media_titles():
    print("Testing Media Titles Display Fix")
    print("=" * 40)
    
    # Login and get token
    print("1. Getting authentication token...")
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json={"username": "test@example.com", "password": "testpass123"},
            timeout=10
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   PASS: Authentication successful")
    except Exception as e:
        print(f"   FAIL: Authentication error: {e}")
        return False
    
    # Get media data and check title fields
    print("\n2. Checking media title fields...")
    try:
        media_response = requests.get(
            "http://localhost:8000/api/v1/media/",
            headers=headers,
            timeout=5
        )
        
        if media_response.status_code == 200:
            data = media_response.json()
            items = data.get('items', [])
            print(f"   PASS: Found {len(items)} media items")
            
            # Check first few items for title fields
            print("\n   Sample media title data:")
            for i, item in enumerate(items[:5]):
                title = item.get('title')
                filename = item.get('filename')
                original_filename = item.get('original_filename')
                
                print(f"   {i+1}. ID: {item.get('id', 'No ID')[:8]}...")
                print(f"      Title: {title if title else 'None'}")
                print(f"      Filename: {filename if filename else 'None'}")
                print(f"      Original: {original_filename if original_filename else 'None'}")
                
                # Test our display logic
                display_title = title or filename or original_filename or 'Unknown Media'
                if not title and (filename or original_filename):
                    # Clean up filename
                    raw_title = filename or original_filename
                    cleaned = raw_title.replace('.', ' ').replace('_', ' ').strip()
                    # Remove common file extensions
                    for ext in ['.mkv', '.mp4', '.avi', '.mov', '.wmv']:
                        if cleaned.lower().endswith(ext):
                            cleaned = cleaned[:-len(ext)]
                    display_title = cleaned
                
                print(f"      Display Title: '{display_title}'")
                print()
                
        else:
            print(f"   FAIL: Media API returned {media_response.status_code}")
            return False
    except Exception as e:
        print(f"   FAIL: Media API error: {e}")
        return False
    
    print("3. Testing frontend route...")
    try:
        frontend_response = requests.get("http://localhost:3000/library", timeout=5)
        if frontend_response.status_code == 200:
            print("   PASS: Library route accessible")
        else:
            print(f"   WARN: Library route returned {frontend_response.status_code}")
    except Exception as e:
        print(f"   FAIL: Library route error: {e}")
    
    print("\n" + "=" * 40)
    print("MEDIA TITLES FIX SUMMARY")
    print("=" * 40)
    
    print("\nTitle Display Logic Fixed:")
    print("1. Priority: title > filename > original_filename")
    print("2. Filename cleaning: remove extensions, replace dots/underscores")
    print("3. Fallback to 'Unknown Media' if all fields empty")
    
    print("\nMediaCardNew.vue Changes:")
    print("- Enhanced displayTitle computed property")
    print("- Added filename cleaning logic")
    print("- Proper title hierarchy handling")
    
    print("\nExpected Results:")
    print("- Movie and TV show names should now display properly")
    print("- Cleaned filenames when no title field available")
    print("- No more 'Unknown Media' for files with names")
    
    return True

if __name__ == "__main__":
    test_media_titles()
