#!/usr/bin/env python3
import sqlite3

# Check the production database
conn = sqlite3.connect('/app/watch1.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("PRODUCTION DATABASE (/app/watch1.db):")
print("=" * 40)

tables = ['users', 'media_files', 'playlists', 'playlist_items']
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")
    except Exception as e:
        print(f"{table}: ERROR - {e}")

# Check if there's a user in production db
print("\nUSERS IN PRODUCTION DB:")
try:
    cursor.execute("SELECT email FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"  - {user['email']}")
except Exception as e:
    print(f"ERROR: {e}")

conn.close()
