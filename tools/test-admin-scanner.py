#!/usr/bin/env python3
"""
Test Admin Scanner Button Functionality
Debug the admin page scanner button issue
"""

import requests
import json
import sys

def test_admin_scanner():
    """Test the admin scanner functionality"""
    print("ADMIN SCANNER BUTTON TEST")
    print("=" * 40)
    
    # Step 1: Authenticate
    print("1. Testing authentication...")
    try:
        auth_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                    json={'username': 'test@example.com', 'password': 'testpass123'},
                                    timeout=10)
        
        if auth_response.status_code != 200:
            print(f"ERROR: Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return False
            
        auth_data = auth_response.json()
        token = auth_data.get('access_token')
        
        if not token:
            print("ERROR: No access token in response")
            print(f"Auth response: {auth_data}")
            return False
            
        print(f"SUCCESS: Got token (length: {len(token)})")
        
    except Exception as e:
        print(f"ERROR: Authentication exception: {e}")
        return False
    
    # Step 2: Test user profile (admin check)
    print("\n2. Testing admin privileges...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        profile_response = requests.get('http://localhost:8000/api/v1/users/me', 
                                      headers=headers, timeout=10)
        
        if profile_response.status_code != 200:
            print(f"ERROR: Profile check failed: {profile_response.status_code}")
            return False
            
        profile_data = profile_response.json()
        is_superuser = profile_data.get('is_superuser', False)
        
        if not is_superuser:
            print(f"ERROR: User is not admin: {profile_data}")
            return False
            
        print(f"SUCCESS: User has admin privileges")
        
    except Exception as e:
        print(f"ERROR: Profile check exception: {e}")
        return False
    
    # Step 3: Test media scan endpoint
    print("\n3. Testing media scan endpoint...")
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        scan_response = requests.post('http://localhost:8000/api/v1/media/scan', 
                                    headers=headers, 
                                    json={}, 
                                    timeout=30)
        
        print(f"Scan response status: {scan_response.status_code}")
        
        if scan_response.status_code == 200:
            scan_data = scan_response.json()
            print(f"SUCCESS: Scan completed")
            print(f"  - Total files found: {scan_data.get('total_files_found', 0)}")
            print(f"  - Files added: {scan_data.get('files_added', 0)}")
            print(f"  - Directories scanned: {scan_data.get('directories_scanned', 0)}")
            print(f"  - Scan results: {len(scan_data.get('scan_results', {}))}")
            return True
        else:
            print(f"ERROR: Scan failed: {scan_response.status_code}")
            print(f"Response: {scan_response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Scan exception: {e}")
        return False

def test_frontend_token_storage():
    """Test what token would be stored in frontend localStorage"""
    print("\n4. Testing frontend token format...")
    
    # Get a fresh token
    auth_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                json={'username': 'test@example.com', 'password': 'testpass123'})
    
    if auth_response.status_code == 200:
        token = auth_response.json().get('access_token')
        print(f"Token format check:")
        print(f"  - Length: {len(token)}")
        print(f"  - Starts with: {token[:20]}...")
        print(f"  - Contains dots: {token.count('.')}")
        
        # Test if this token works
        headers = {'Authorization': f'Bearer {token}'}
        test_response = requests.get('http://localhost:8000/api/v1/users/me', headers=headers)
        print(f"  - Token validation: {'SUCCESS' if test_response.status_code == 200 else 'FAILED'}")
        
        return token
    else:
        print("ERROR: Could not get token for frontend test")
        return None

def main():
    """Main test runner"""
    print("Testing Admin Scanner Button Functionality")
    print("=" * 50)
    
    # Test backend functionality
    backend_ok = test_admin_scanner()
    
    # Test frontend token format
    token = test_frontend_token_storage()
    
    print("\n" + "=" * 50)
    print("ADMIN SCANNER TEST SUMMARY")
    print("=" * 50)
    
    if backend_ok:
        print("✅ Backend: Media scan endpoint working correctly")
        print("✅ Authentication: Admin privileges confirmed")
        print("✅ API: All endpoints responding properly")
        
        if token:
            print("✅ Token: Valid JWT token generated")
            print("\nPOSSIBLE FRONTEND ISSUES:")
            print("1. Token not being stored in localStorage correctly")
            print("2. Token being corrupted during storage/retrieval")
            print("3. CORS issues preventing request from reaching backend")
            print("4. Frontend error handling masking the real issue")
            
            print(f"\nDEBUGGING STEPS:")
            print("1. Open browser dev tools (F12)")
            print("2. Go to Admin page and click scanner button")
            print("3. Check Console tab for JavaScript errors")
            print("4. Check Network tab for failed requests")
            print("5. Check Application > Local Storage for 'access_token'")
            
            print(f"\nEXPECTED TOKEN IN LOCALSTORAGE:")
            print(f"Key: 'access_token'")
            print(f"Value: {token[:50]}...")
        else:
            print("❌ Token: Could not generate test token")
    else:
        print("❌ Backend: Media scan endpoint has issues")
        print("❌ Check backend logs and API connectivity")
    
    return backend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
