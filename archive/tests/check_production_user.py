#!/usr/bin/env python3
import sqlite3
import hashlib

# Check the production database user
conn = sqlite3.connect('/app/watch1.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("PRODUCTION DATABASE USER CHECK:")
print("=" * 35)

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

for user in users:
    print("User details:")
    for key in user.keys():
        if 'password' in key.lower():
            print(f"  {key}: [HIDDEN - Length: {len(str(user[key]))}]")
        else:
            print(f"  {key}: {user[key]}")
    
    # Test if this is a bcrypt hash or SHA256
    password_hash = user['password_hash']
    print(f"\nPassword hash analysis:")
    print(f"  Length: {len(password_hash)}")
    print(f"  Starts with $2: {password_hash.startswith('$2') if password_hash else False}")
    
    # Test SHA256 of testpass123
    test_sha256 = hashlib.sha256("testpass123".encode()).hexdigest()
    print(f"  Matches SHA256 of 'testpass123': {password_hash == test_sha256}")

conn.close()
