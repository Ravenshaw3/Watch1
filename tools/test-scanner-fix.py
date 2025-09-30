#!/usr/bin/env python3
"""
Test Scanner Fix - Verify admin scanner button is working
"""

import requests
import time
import sys

def test_scanner_fix():
    """Test that the scanner button fix is working"""
    print("TESTING ADMIN SCANNER BUTTON FIX")
    print("=" * 40)
    
    # Wait for containers to be ready
    print("Waiting for containers to be ready...")
    time.sleep(5)
    
    # Test frontend is accessible
    try:
        frontend_response = requests.get('http://localhost:3000', timeout=10)
        if frontend_response.status_code == 200:
            print("✅ Frontend: Accessible")
        else:
            print(f"❌ Frontend: Not accessible ({frontend_response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend: Connection error - {e}")
        return False
    
    # Test backend is accessible
    try:
        backend_response = requests.get('http://localhost:8000/api/v1/health', timeout=10)
        if backend_response.status_code == 200:
            print("✅ Backend: Accessible")
        else:
            print(f"❌ Backend: Not accessible ({backend_response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend: Connection error - {e}")
        return False
    
    # Test authentication
    try:
        auth_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                    json={'username': 'test@example.com', 'password': 'testpass123'},
                                    timeout=10)
        if auth_response.status_code == 200:
            token = auth_response.json().get('access_token')
            print("✅ Authentication: Working")
        else:
            print(f"❌ Authentication: Failed ({auth_response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Authentication: Error - {e}")
        return False
    
    # Test admin privileges
    try:
        headers = {'Authorization': f'Bearer {token}'}
        profile_response = requests.get('http://localhost:8000/api/v1/users/me', headers=headers, timeout=10)
        if profile_response.status_code == 200:
            user_data = profile_response.json()
            if user_data.get('is_superuser'):
                print("✅ Admin Privileges: Confirmed")
            else:
                print("❌ Admin Privileges: User is not admin")
                return False
        else:
            print(f"❌ Admin Privileges: Check failed ({profile_response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Admin Privileges: Error - {e}")
        return False
    
    # Test media scan endpoint
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        scan_response = requests.post('http://localhost:8000/api/v1/media/scan', 
                                    headers=headers, json={}, timeout=30)
        if scan_response.status_code == 200:
            scan_data = scan_response.json()
            print("✅ Media Scan: Endpoint working")
            print(f"   - Files found: {scan_data.get('total_files_found', 0)}")
            print(f"   - Directories: {scan_data.get('directories_scanned', 0)}")
        else:
            print(f"❌ Media Scan: Failed ({scan_response.status_code})")
            print(f"   Response: {scan_response.text}")
            return False
    except Exception as e:
        print(f"❌ Media Scan: Error - {e}")
        return False
    
    print("\n" + "=" * 40)
    print("SCANNER FIX VERIFICATION: SUCCESS")
    print("=" * 40)
    print("✅ All backend components working")
    print("✅ Authentication and admin privileges confirmed")
    print("✅ Media scan endpoint responding correctly")
    print("\nFRONTEND TESTING:")
    print("1. Open http://localhost:3000 in browser")
    print("2. Login with test@example.com / testpass123")
    print("3. Navigate to Admin tab")
    print("4. Click 'Scan Media Directories' button")
    print("5. Check browser console (F12) for any errors")
    print("6. Verify scan results appear on the page")
    
    return True

if __name__ == "__main__":
    success = test_scanner_fix()
    sys.exit(0 if success else 1)
