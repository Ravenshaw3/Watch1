#!/usr/bin/env python3
import sys
import os
sys.path.append('/app')

# Read the file and extract just the database initialization part
with open('/app/enhanced_media_main.py', 'r') as f:
    content = f.read()

# Extract the startup_event function and run it to initialize the database
startup_code = content.split('@app.on_event("startup")')[1].split('@app.get("/health")')[0]
exec(startup_code)

print(f"Total media files in database: {len(media_db)}")

# Count by category
categories = {}
for media in media_db.values():
    cat = media.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

print("Categories found:")
for cat, count in categories.items():
    print(f"  {cat}: {count} files")

# Show some sample files
print("\nSample files:")
for i, (id, media) in enumerate(list(media_db.items())[:10]):
    print(f"  {id}: {media.get('filename', 'unknown')} - {media.get('category', 'unknown')}")
