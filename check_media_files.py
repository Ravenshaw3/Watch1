#!/usr/bin/env python3
import sqlite3
import os

# Check media file paths in database
conn = sqlite3.connect('/app/watch1.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("CHECKING MEDIA FILE PATHS:")
print("=" * 30)

cursor.execute("SELECT id, title, file_path FROM media_files LIMIT 5")
files = cursor.fetchall()

for file in files:
    title = file['title']
    file_path = file['file_path']
    media_id = file['id']
    
    print(f"\nTitle: {title}")
    print(f"ID: {media_id}")
    print(f"Original path: {file_path}")
    
    # Convert Windows path to container path
    container_path = file_path
    if file_path.startswith('T:'):
        container_path = file_path.replace('T:', '/app/T').replace('\\', '/')
    elif file_path.startswith('C:'):
        container_path = file_path.replace('C:', '/app/C').replace('\\', '/')
    else:
        container_path = file_path.replace('\\', '/')
    
    print(f"Container path: {container_path}")
    print(f"File exists: {os.path.exists(container_path)}")
    
    if os.path.exists(container_path):
        size = os.path.getsize(container_path)
        print(f"File size: {size} bytes")

conn.close()
