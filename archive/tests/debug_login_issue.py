#!/usr/bin/env python3
"""
Debug the login issue - check user table structure and data
"""

import sys
import os
sys.path.append('/app')

from database_config import get_db_connection

def debug_login_issue():
    print("DEBUGGING LOGIN ISSUE")
    print("=" * 30)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check table structure
        print("1. USERS TABLE STRUCTURE:")
        print("-" * 25)
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   Column: {col['name']} | Type: {col['type']} | Not Null: {col['notnull']}")
        
        # Check user data
        print("\n2. USER DATA:")
        print("-" * 15)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        for i, user in enumerate(users):
            print(f"   User {i+1}:")
            for key in user.keys():
                value = user[key]
                if 'password' in key.lower():
                    value = f"[HIDDEN - Length: {len(str(value)) if value else 0}]"
                print(f"      {key}: {value}")
            print()
        
        # Test the specific query used in login
        print("3. TESTING LOGIN QUERY:")
        print("-" * 25)
        test_email = 'test@example.com'
        cursor.execute('SELECT * FROM users WHERE email = ?', (test_email,))
        user = cursor.fetchone()
        
        if user:
            print(f"   SUCCESS: Found user with email {test_email}")
            print("   Available keys:")
            for key in user.keys():
                print(f"      - {key}")
        else:
            print(f"   ERROR: No user found with email {test_email}")
        
        conn.close()
        
        print("\n4. DIAGNOSIS:")
        print("-" * 15)
        print("   The login error 'no item with that key' likely means:")
        print("   - The code is trying to access user['hashed_password']")
        print("   - But the actual column name might be different")
        print("   - Check the column names above and fix the login code")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_login_issue()
