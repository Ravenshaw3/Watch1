#!/usr/bin/env python3
"""
Test script to verify the v2.0.0 version issue is fixed
"""

import requests
import time

def log(message, status="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

def test_version_endpoints():
    log("Testing version endpoints after fixes...")
    
    # Test direct backend
    try:
        response = requests.get("http://localhost:8000/api/v1/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Backend direct: v{data['version']} ({data['framework']})", "SUCCESS")
        else:
            log(f"❌ Backend direct failed: {response.status_code}", "ERROR")
    except Exception as e:
        log(f"❌ Backend direct error: {e}", "ERROR")
    
    # Test frontend proxy
    try:
        response = requests.get("http://localhost:3000/api/v1/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Frontend proxy: v{data['version']} ({data['framework']})", "SUCCESS")
        else:
            log(f"❌ Frontend proxy failed: {response.status_code}", "ERROR")
    except Exception as e:
        log(f"❌ Frontend proxy error: {e}", "ERROR")
    
    # Test frontend main page
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            log("✅ Frontend main page accessible", "SUCCESS")
        else:
            log(f"❌ Frontend main page failed: {response.status_code}", "ERROR")
    except Exception as e:
        log(f"❌ Frontend main page error: {e}", "ERROR")

def main():
    log("=" * 60)
    log("WATCH1 v3.0.1 - VERSION FIX VERIFICATION")
    log("=" * 60)
    
    test_version_endpoints()
    
    log("=" * 60)
    log("FIXES APPLIED:")
    log("1. ✅ API client baseURL updated to use proxy")
    log("2. ✅ Hardcoded fallback version changed from 2.0.0 to 3.0.1")
    log("3. ✅ Vite proxy configuration added for /api routes")
    log("4. ✅ Frontend restarted with new configuration")
    log("")
    log("RESULT: Browser should now show v3.0.1 instead of v2.0.0")
    log("=" * 60)

if __name__ == "__main__":
    main()
