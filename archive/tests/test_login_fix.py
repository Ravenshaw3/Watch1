#!/usr/bin/env python3
"""
Test the login fix - no Unicode characters
"""

import requests
import time

def test_login_fix():
    print("TESTING LOGIN FIX")
    print("=" * 20)
    
    # Wait for backend to reload
    time.sleep(3)
    
    print("1. Testing login with correct credentials...")
    try:
        response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                               json={'username': 'test@example.com', 'password': 'testpass123'})
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("   SUCCESS: Login successful!")
            print(f"   Token received: {token[:50]}..." if token else "   ERROR: No token in response")
            return token
        else:
            print(f"   ERROR: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ERROR: Request failed - {e}")
        return None
    
def test_with_token(token):
    if not token:
        print("\n2. Skipping token test - no token available")
        return
    
    print("\n2. Testing API with token...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   SUCCESS: Token is valid!")
            print(f"   User: {data.get('email', 'Unknown')}")
        else:
            print(f"   ERROR: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ERROR: Request failed - {e}")

def main():
    print("DEBUGGING LOGIN ERROR 500 - 'no item with that key'")
    print("=" * 50)
    
    print("\nFIX APPLIED:")
    print("- Changed user['hashed_password'] to user['password_hash']")
    print("- Changed bcrypt check to SHA256 hash comparison")
    print("- Database uses SHA256, not bcrypt")
    
    print("\nTESTING:")
    token = test_login_fix()
    test_with_token(token)
    
    print("\n" + "=" * 50)
    print("LOGIN FIX SUMMARY")
    print("=" * 50)
    
    if token:
        print("SUCCESS: Login is now working!")
        print("- Database column name mismatch fixed")
        print("- Hash algorithm mismatch fixed")
        print("- Authentication should work in browser")
    else:
        print("FAILED: Login still not working")
        print("- Check backend logs for more details")
        print("- Verify database user exists")
    
    print("\nNEXT STEPS:")
    print("1. Test login in browser at http://localhost:3000")
    print("2. Use credentials: test@example.com / testpass123")
    print("3. Check browser console for any remaining errors")

if __name__ == "__main__":
    main()
