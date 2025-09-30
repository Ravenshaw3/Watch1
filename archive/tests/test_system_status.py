#!/usr/bin/env python3
"""
Simple system status test without syntax errors
"""

import requests
import json
import time

def test_system():
    print("WATCH1 v3.0.1 - SYSTEM STATUS CHECK")
    print("=" * 50)
    
    # Test backend version
    try:
        response = requests.get("http://localhost:8000/api/v1/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Backend: v{data['version']} ({data['framework']})")
        else:
            print(f"Backend error: {response.status_code}")
    except Exception as e:
        print(f"Backend error: {e}")
    
    # Test authentication
    try:
        login_data = {
            "username": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login/access-token",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print("Authentication: SUCCESS")
            
            # Test media with token
            headers = {"Authorization": f"Bearer {token}"}
            media_response = requests.get(
                "http://localhost:8000/api/v1/media/",
                headers=headers
            )
            
            if media_response.status_code == 200:
                media_data = media_response.json()
                print(f"Media files: {media_data['total']} total")
                print(f"Current page: {len(media_data['media'])} items")
                
                if media_data['media']:
                    print("Sample movies:")
                    for movie in media_data['media'][:3]:
                        print(f"  - {movie['title']}")
            else:
                print(f"Media error: {media_response.status_code}")
                
        else:
            print(f"Login error: {response.status_code}")
            
    except Exception as e:
        print(f"Auth error: {e}")
    
    # Test frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("Frontend: ACCESSIBLE")
        else:
            print(f"Frontend error: {response.status_code}")
    except Exception as e:
        print(f"Frontend error: {e}")
    
    print("=" * 50)
    print("System check complete")

if __name__ == "__main__":
    test_system()
