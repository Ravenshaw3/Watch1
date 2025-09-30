#!/usr/bin/env python3
"""
Check production database for all frontend-backend compatibility issues
"""

import sqlite3
import requests
import json

def check_database_schema():
    """Check database schema and structure"""
    print("1. CHECKING DATABASE SCHEMA")
    print("=" * 35)
    
    try:
        # Connect to production database
        conn = sqlite3.connect('/app/watch1.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check users table structure
        print("Users table structure:")
        cursor.execute("PRAGMA table_info(users)")
        user_columns = cursor.fetchall()
        user_column_names = [col['name'] for col in user_columns]
        
        for col in user_columns:
            print(f"  {col['name']}: {col['type']}")
        
        # Check for authentication-related columns
        auth_columns = ['email', 'username', 'full_name', 'hashed_password', 'password_hash']
        missing_auth = [col for col in auth_columns if col not in user_column_names]
        present_auth = [col for col in auth_columns if col in user_column_names]
        
        print(f"\nAuthentication columns present: {present_auth}")
        if missing_auth:
            print(f"Authentication columns missing: {missing_auth}")
        
        # Check media_files table structure
        print(f"\nMedia files table structure:")
        cursor.execute("PRAGMA table_info(media_files)")
        media_columns = cursor.fetchall()
        media_column_names = [col['name'] for col in media_columns]
        
        for col in media_columns:
            print(f"  {col['name']}: {col['type']}")
        
        # Check for required media columns
        required_media = ['id', 'filename', 'file_path', 'file_size', 'category', 'created_at']
        missing_media = [col for col in required_media if col not in media_column_names]
        
        if missing_media:
            print(f"Missing required media columns: {missing_media}")
        else:
            print("✅ All required media columns present")
        
        # Check for problematic columns we had issues with
        problematic_columns = ['is_deleted', 'poster_data']
        present_problematic = [col for col in problematic_columns if col in media_column_names]
        if present_problematic:
            print(f"⚠️ Problematic columns present: {present_problematic}")
        
        conn.close()
        return user_column_names, media_column_names
        
    except Exception as e:
        print(f"❌ Database schema check failed: {e}")
        return [], []

def check_user_authentication():
    """Check user authentication compatibility"""
    print("\n2. CHECKING USER AUTHENTICATION")
    print("=" * 35)
    
    try:
        conn = sqlite3.connect('/app/watch1.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user details
        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if user:
            print("User found:")
            for key in user.keys():
                if 'password' in key.lower():
                    print(f"  {key}: [HIDDEN - Length: {len(str(user[key]))}]")
                else:
                    print(f"  {key}: {user[key]}")
            
            # Check password hash type
            if 'hashed_password' in user.keys():
                password_hash = user['hashed_password']
                print(f"\nPassword hash analysis:")
                print(f"  Length: {len(password_hash)}")
                print(f"  Starts with $2: {password_hash.startswith('$2')}")
                print(f"  Hash type: {'bcrypt' if password_hash.startswith('$2') else 'unknown'}")
            elif 'password_hash' in user.keys():
                password_hash = user['password_hash']
                print(f"\nPassword hash analysis:")
                print(f"  Length: {len(password_hash)}")
                print(f"  Hash type: {'SHA256' if len(password_hash) == 64 else 'unknown'}")
        else:
            print("❌ No users found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ User authentication check failed: {e}")

def check_media_data():
    """Check media data compatibility"""
    print("\n3. CHECKING MEDIA DATA")
    print("=" * 25)
    
    try:
        conn = sqlite3.connect('/app/watch1.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get media count
        cursor.execute("SELECT COUNT(*) as count FROM media_files")
        total_count = cursor.fetchone()['count']
        print(f"Total media files: {total_count}")
        
        # Get categories
        cursor.execute("SELECT category, COUNT(*) as count FROM media_files GROUP BY category")
        categories = cursor.fetchall()
        
        print("Categories:")
        for cat in categories:
            print(f"  {cat['category']}: {cat['count']} files")
        
        # Check sample media file
        cursor.execute("SELECT * FROM media_files LIMIT 1")
        sample = cursor.fetchone()
        
        if sample:
            print(f"\nSample media file:")
            for key in sample.keys():
                print(f"  {key}: {sample[key]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Media data check failed: {e}")

def test_api_endpoints():
    """Test API endpoints for compatibility"""
    print("\n4. TESTING API ENDPOINTS")
    print("=" * 30)
    
    try:
        # Test authentication
        print("Testing authentication...")
        auth_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                    json={'username': 'test@example.com', 'password': 'testpass123'})
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access_token']
            print("✅ Authentication working")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test user profile endpoint
            print("Testing user profile...")
            profile_response = requests.get('http://localhost:8000/api/v1/users/me', headers=headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ User profile working")
                print(f"  User keys: {list(profile_data.keys())}")
            else:
                print(f"❌ User profile failed: {profile_response.status_code}")
            
            # Test media endpoint
            print("Testing media endpoint...")
            media_response = requests.get('http://localhost:8000/api/v1/media/?limit=2', headers=headers)
            if media_response.status_code == 200:
                media_data = media_response.json()
                print("✅ Media endpoint working")
                print(f"  Response keys: {list(media_data.keys())}")
                
                # Check TypeScript compatibility
                required_keys = ['items', 'total', 'page', 'page_size', 'categories']
                missing_keys = [key for key in required_keys if key not in media_data]
                if missing_keys:
                    print(f"❌ Missing TypeScript keys: {missing_keys}")
                else:
                    print("✅ All TypeScript keys present")
                    
                if media_data.get('items'):
                    item_keys = list(media_data['items'][0].keys())
                    print(f"  Media item keys: {item_keys}")
            else:
                print(f"❌ Media endpoint failed: {media_response.status_code}")
            
            # Test categories endpoint
            print("Testing categories endpoint...")
            cat_response = requests.get('http://localhost:8000/api/v1/media/categories', headers=headers)
            if cat_response.status_code == 200:
                print("✅ Categories endpoint working")
            else:
                print(f"❌ Categories endpoint failed: {cat_response.status_code}")
            
            # Test scan-info endpoint
            print("Testing scan-info endpoint...")
            scan_response = requests.get('http://localhost:8000/api/v1/media/scan-info', headers=headers)
            if scan_response.status_code == 200:
                print("✅ Scan-info endpoint working")
            else:
                print(f"❌ Scan-info endpoint failed: {scan_response.status_code}")
                
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")

def main():
    print("PRODUCTION DATABASE COMPATIBILITY CHECK")
    print("=" * 45)
    print("Checking for all frontend-backend issues we fixed in development...")
    
    user_columns, media_columns = check_database_schema()
    check_user_authentication()
    check_media_data()
    test_api_endpoints()
    
    print(f"\n5. SUMMARY OF COMPATIBILITY ISSUES")
    print("=" * 40)
    
    issues = []
    
    # Check authentication compatibility
    if 'hashed_password' not in user_columns and 'password_hash' not in user_columns:
        issues.append("❌ No password hash column found")
    
    if 'username' not in user_columns:
        issues.append("⚠️ No username column (will use email)")
    
    if 'full_name' not in user_columns:
        issues.append("⚠️ No full_name column (will use email)")
    
    # Check media compatibility
    required_media = ['id', 'filename', 'file_path', 'category']
    missing_media = [col for col in required_media if col not in media_columns]
    if missing_media:
        issues.append(f"❌ Missing media columns: {missing_media}")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No compatibility issues found!")
        print("✅ Production database is compatible with frontend!")
    
    print(f"\n6. NEXT STEPS")
    print("=" * 15)
    print("- Test frontend at http://localhost:3000")
    print("- Login with test@example.com / testpass123")
    print("- Verify all features work without errors")
    print("- Check browser console for any remaining issues")

if __name__ == "__main__":
    main()
