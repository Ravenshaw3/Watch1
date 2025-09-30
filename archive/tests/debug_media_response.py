#!/usr/bin/env python3
"""
Debug media response structure
"""

import requests
import json

def debug_media():
    # Login first
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
        
        # Get media
        headers = {"Authorization": f"Bearer {token}"}
        media_response = requests.get(
            "http://localhost:8000/api/v1/media/",
            headers=headers
        )
        
        print("Media Response Status:", media_response.status_code)
        print("Media Response Headers:", dict(media_response.headers))
        print("Media Response Content:")
        
        if media_response.status_code == 200:
            try:
                data = media_response.json()
                print("JSON Keys:", list(data.keys()))
                print("Total:", data.get('total', 'Not found'))
                print("Media key exists:", 'media' in data)
                if 'media' in data:
                    print("Media count:", len(data['media']))
                else:
                    print("Available keys:", list(data.keys()))
            except Exception as e:
                print("JSON parse error:", e)
                print("Raw content:", media_response.text[:500])
        else:
            print("Error content:", media_response.text)
    else:
        print("Login failed:", response.status_code, response.text)

if __name__ == "__main__":
    debug_media()
