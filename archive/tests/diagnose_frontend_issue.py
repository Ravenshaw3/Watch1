#!/usr/bin/env python3
"""
Diagnose specific frontend issues
"""

import requests
import json

def check_frontend_content():
    """Check what the frontend is actually serving"""
    print("🖥️ Checking frontend content...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        
        if response.status_code == 200:
            content = response.text
            print(f"   Content length: {len(content)} characters")
            
            # Check for common issues
            if '<div id="app">' in content:
                print("   ✅ Vue app mount point found")
            else:
                print("   ❌ Vue app mount point missing")
            
            if 'script' in content.lower():
                print("   ✅ JavaScript detected")
            else:
                print("   ❌ No JavaScript found")
            
            if 'error' in content.lower():
                print("   ⚠️ Error text found in content")
            
            # Show first 500 characters
            print(f"\n   First 500 characters:")
            print(f"   {content[:500]}...")
            
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Frontend check failed: {e}")

def check_vite_dev_server():
    """Check if Vite dev server is responding"""
    print("\n⚡ Checking Vite dev server...")
    
    try:
        # Try to access Vite's dev server info
        response = requests.get("http://localhost:3000/@vite/client", timeout=5)
        if response.status_code == 200:
            print("   ✅ Vite dev server responding")
        else:
            print(f"   ⚠️ Vite client returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Vite dev server check failed: {e}")

def check_api_from_frontend_perspective():
    """Check API from frontend's perspective (CORS, etc.)"""
    print("\n🌐 Checking API from frontend perspective...")
    
    # Simulate a browser request from localhost:3000
    headers = {
        'Origin': 'http://localhost:3000',
        'Referer': 'http://localhost:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Test CORS preflight
        response = requests.options(
            "http://localhost:8000/api/v1/media/",
            headers={
                **headers,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'authorization,content-type'
            },
            timeout=5
        )
        
        print(f"   CORS Preflight Status: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        
        if response.status_code == 200:
            print("   ✅ CORS preflight successful")
        else:
            print("   ❌ CORS preflight failed")
            
    except Exception as e:
        print(f"   ❌ CORS check failed: {e}")

def check_common_frontend_issues():
    """Check for common frontend issues"""
    print("\n🔍 Checking for common frontend issues...")
    
    issues_found = []
    
    # Check if backend is accessible from frontend's network
    try:
        response = requests.get("http://localhost:8000/api/v1/settings/test", timeout=5)
        if response.status_code != 200:
            issues_found.append(f"Backend not accessible (status: {response.status_code})")
    except Exception as e:
        issues_found.append(f"Backend connection failed: {e}")
    
    # Check if there are any obvious network issues
    try:
        # Test if we can reach the backend from the same network as frontend
        response = requests.get("http://127.0.0.1:8000/api/v1/settings/test", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend accessible via 127.0.0.1")
        else:
            issues_found.append("Backend not accessible via 127.0.0.1")
    except Exception as e:
        issues_found.append(f"127.0.0.1 connection failed: {e}")
    
    if issues_found:
        print("   ❌ Issues found:")
        for issue in issues_found:
            print(f"      - {issue}")
    else:
        print("   ✅ No obvious network issues detected")

def main():
    """Run all diagnostic checks"""
    print("🎬 Watch1 Frontend Issue Diagnostics")
    print("=" * 50)
    
    check_frontend_content()
    check_vite_dev_server()
    check_api_from_frontend_perspective()
    check_common_frontend_issues()
    
    print("\n" + "=" * 50)
    print("📋 RECOMMENDATIONS")
    print("=" * 50)
    print("1. Check the browser console for JavaScript errors")
    print("2. Verify the frontend is loading at http://localhost:3000")
    print("3. Check if authentication is working properly")
    print("4. Look for any CORS or network connectivity issues")
    print("5. Try refreshing the page or clearing browser cache")
    print("\nIf issues persist, check Docker container logs:")
    print("   docker logs watch1-frontend-dev")
    print("   docker logs watch1-backend-dev")

if __name__ == "__main__":
    main()
