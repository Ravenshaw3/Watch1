#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/app/watch1_dev.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("USERS TABLE STRUCTURE:")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col['name']} ({col['type']})")

print("\nUSERS DATA:")
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print("User keys:", list(user.keys()))
    for key in user.keys():
        if 'password' in key.lower():
            print(f"  {key}: [HIDDEN]")
        else:
            print(f"  {key}: {user[key]}")

conn.close()
