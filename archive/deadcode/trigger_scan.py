#!/usr/bin/env python3
import requests
import json

# Login and get token
login_data = {"username": "admin", "password": "admin123"}
login_response = requests.post("http://192.168.254.14:8083/api/v1/auth/login", json=login_data)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Login successful, token: {token[:20]}...")
    
    # Start scan
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    scan_data = {"directory": "/app/media"}
    
    scan_response = requests.post("http://192.168.254.14:8083/api/v1/media/scan", json=scan_data, headers=headers)
    print(f"🔍 Scan status: {scan_response.status_code}")
    print(f"📄 Response: {scan_response.text}")
    
    if scan_response.status_code == 200:
        print("✅ Scan started successfully!")
    else:
        print("❌ Scan failed to start")
else:
    print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")

