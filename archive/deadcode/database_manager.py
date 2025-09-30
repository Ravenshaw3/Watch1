#!/usr/bin/env python3
"""
Database Manager - Utility for managing Watch1 databases
"""

import sys
import os
import argparse
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database_config import db_config

def show_database_info():
    """Display comprehensive database information"""
    print("📊 DATABASE INFORMATION")
    print("=" * 40)
    
    info = db_config.get_database_info()
    
    print(f"🔧 Configuration:")
    print(f"   Environment: {info.get('environment', 'Unknown')}")
    print(f"   Database Path: {info.get('path', 'Unknown')}")
    print(f"   File Exists: {'✅ Yes' if info.get('exists') else '❌ No'}")
    
    if info.get('exists'):
        file_size = info.get('file_size', 0)
        print(f"   File Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"   Readable: {'✅ Yes' if info.get('readable') else '❌ No'}")
        print(f"   Writable: {'✅ Yes' if info.get('writable') else '❌ No'}")
    
    if 'tables' in info:
        print(f"\n📋 Table Information:")
        tables = info['tables']
        for table_name, count in tables.items():
            print(f"   {table_name}: {count:,} records")
    
    if 'error' in info:
        print(f"\n❌ Error: {info['error']}")

def test_connection():
    """Test database connection"""
    print("🔌 TESTING DATABASE CONNECTION")
    print("=" * 35)
    
    try:
        conn = db_config.get_connection()
        print("✅ Connection successful")
        
        # Test a simple query
        cursor = conn.cursor()
        result = cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()
        table_count = result[0] if result else 0
        print(f"📋 Found {table_count} tables in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def initialize_database():
    """Initialize database with required tables"""
    print("🔧 INITIALIZING DATABASE")
    print("=" * 30)
    
    try:
        success = db_config.initialize_database()
        if success:
            print("✅ Database initialization completed")
        else:
            print("❌ Database initialization failed")
        return success
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def backup_database(backup_path=None):
    """Create database backup"""
    print("💾 CREATING DATABASE BACKUP")
    print("=" * 30)
    
    try:
        backup_file = db_config.backup_database(backup_path)
        print(f"✅ Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def scan_media():
    """Run media scanner"""
    print("🔍 RUNNING MEDIA SCANNER")
    print("=" * 25)
    
    try:
        from media_scanner import MediaScanner
        scanner = MediaScanner()
        results = scanner.scan_all_directories()
        
        print(f"✅ Scan completed:")
        print(f"   📁 Directories: {results.get('directories_scanned', 0)}")
        print(f"   📄 Files found: {results.get('total_files_found', 0)}")
        print(f"   🆕 New files: {results.get('new_files', 0)}")
        print(f"   🔄 Updated: {results.get('updated_files', 0)}")
        print(f"   🖼️  Posters: {results.get('posters_loaded', 0)}")
        
        return results
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        return None

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Watch1 Database Manager')
    parser.add_argument('command', choices=['info', 'test', 'init', 'backup', 'scan'], 
                       help='Command to execute')
    parser.add_argument('--backup-path', help='Custom backup file path')
    
    args = parser.parse_args()
    
    print("🎬 WATCH1 DATABASE MANAGER")
    print("=" * 30)
    print()
    
    if args.command == 'info':
        show_database_info()
    elif args.command == 'test':
        test_connection()
    elif args.command == 'init':
        initialize_database()
    elif args.command == 'backup':
        backup_database(args.backup_path)
    elif args.command == 'scan':
        scan_media()
    
    print()
    print("🎯 GLOBAL DATABASE PATHS:")
    print(f"   Development: {db_config.database_paths['development']}")
    print(f"   Production: {db_config.database_paths['production']}")
    print(f"   Active: {db_config.get_path()}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show interactive menu
        print("🎬 WATCH1 DATABASE MANAGER")
        print("=" * 30)
        print()
        print("Available commands:")
        print("  info   - Show database information")
        print("  test   - Test database connection")
        print("  init   - Initialize database tables")
        print("  backup - Create database backup")
        print("  scan   - Run media scanner")
        print()
        print("Usage: python database_manager.py <command>")
        print("Example: python database_manager.py info")
        print()
        
        # Show current status
        show_database_info()
    else:
        main()
