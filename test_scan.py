#!/usr/bin/env python3
import requests
import json

# Test the scan endpoint with authentication
base_url = "http://192.168.254.14:8083/api/v1"

# First, login to get a token
login_data = {
    "username": "admin",
    "password": "admin123"
}

print("🔐 Logging in...")
login_response = requests.post(f"{base_url}/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Got token: {token[:20]}...")
    
    # Now try to scan media
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    scan_data = {
        "directory": "/app/media"
    }
    
    print("🔍 Starting media scan...")
    scan_response = requests.post(f"{base_url}/media/scan", json=scan_data, headers=headers)
    print(f"Scan status: {scan_response.status_code}")
    print(f"Scan response: {scan_response.text}")
    
else:
    print(f"❌ Login failed: {login_response.text}")

