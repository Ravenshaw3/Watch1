#!/usr/bin/env python3
import sqlite3

# Check what paths are actually in the database
conn = sqlite3.connect('/app/watch1.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("CHECKING UNRAID SERVER PATHS IN DATABASE")
print("=" * 45)

cursor.execute("SELECT file_path FROM media_files LIMIT 10")
files = cursor.fetchall()

print("Sample file paths from database:")
for i, file in enumerate(files, 1):
    print(f"{i:2d}. {file['file_path']}")

# Check for common Unraid patterns
cursor.execute("SELECT DISTINCT substr(file_path, 1, 20) as path_prefix, COUNT(*) as count FROM media_files GROUP BY path_prefix")
prefixes = cursor.fetchall()

print(f"\nPath prefixes found:")
for prefix in prefixes:
    print(f"   {prefix['path_prefix']}... ({prefix['count']} files)")

conn.close()
