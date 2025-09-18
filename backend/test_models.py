#!/usr/bin/env python3
"""
Test script to identify the metadata issue
"""

from app.core.database import Base
from app.models import user, media

print("Testing model imports...")

try:
    # Try to create all tables
    print("Models imported successfully")
    print("Available tables:", list(Base.metadata.tables.keys()))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
