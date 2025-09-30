#!/usr/bin/env python3
"""
System Status Summary
Quick overview of Watch1 system health and database status
"""

import requests
import json
import sys
from datetime import datetime

def get_system_status():
    """Get comprehensive system status"""
    print("WATCH1 SYSTEM STATUS SUMMARY")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test authentication
    try:
        auth_response = requests.post("http://localhost:8000/api/v1/auth/login/access-token", 
                                    json={"username": "test@example.com", "password": "testpass123"},
                                    timeout=5)
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication: WORKING")
        else:
            print("❌ Authentication: FAILED")
            return False
    except:
        print("❌ Backend: NOT ACCESSIBLE")
        return False
    
    # Test database population
    try:
        media_response = requests.get("http://localhost:8000/api/v1/media/", headers=headers, timeout=5)
        if media_response.status_code == 200:
            data = media_response.json()
            total_items = data.get('total', 0)
            categories = data.get('categories', {})
            print(f"✅ Database: {total_items} items, {len(categories)} categories")
            
            # Show category breakdown
            if categories:
                for category, count in categories.items():
                    print(f"   - {category}: {count} items")
        else:
            print("❌ Database: API ERROR")
    except:
        print("❌ Database: CONNECTION ERROR")
    
    # Test frontend
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend: ACCESSIBLE")
        else:
            print("❌ Frontend: NOT ACCESSIBLE")
    except:
        print("❌ Frontend: CONNECTION ERROR")
    
    # Test key API endpoints
    endpoints = [
        ("/api/v1/media/categories", "Categories"),
        ("/api/v1/playlists/", "Playlists"),
        ("/api/v1/settings/media-directories", "Settings"),
        ("/api/v1/analytics/dashboard", "Analytics")
    ]
    
    working_apis = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                working_apis += 1
        except:
            pass
    
    print(f"✅ API Endpoints: {working_apis}/{len(endpoints)} working")
    
    print("\n" + "=" * 50)
    print("QUICK ACCESS:")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:8000")
    print("Login: test@example.com / testpass123")
    print("\nRun enhanced test: python tools\\enhanced-storage-test-suite.py")
    print("Run Unraid scan: python tools\\unified-unraid-scanner.py")
    
    return True

if __name__ == "__main__":
    success = get_system_status()
    sys.exit(0 if success else 1)
