#!/usr/bin/env python3
"""
Database Status Checker
Verifies database population and API accessibility for all views
"""

import requests
import json
import sys

class DatabaseStatusChecker:
    """Check database status and API accessibility"""
    
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.api_url = f"{backend_url}/api/v1"
        self.token = None
        
    def authenticate(self):
        """Get JWT token for API access"""
        try:
            response = requests.post(f"{self.api_url}/auth/login/access-token", 
                                   json={"username": "test@example.com", "password": "testpass123"},
                                   timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print("SUCCESS: Authentication successful")
                return True
            else:
                print(f"ERROR: Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Authentication error: {e}")
            return False
    
    def check_media_api(self):
        """Check media API endpoints"""
        if not self.token:
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print("\nCHECKING MEDIA API ENDPOINTS")
        print("============================")
        
        # Check media list
        try:
            response = requests.get(f"{self.api_url}/media/", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                total_items = data.get('total', 0)
                items = data.get('items', [])
                categories = data.get('categories', {})
                
                print(f"SUCCESS: Media List - {total_items} total items")
                print(f"SUCCESS: Categories found: {len(categories)}")
                
                # Show category breakdown
                for category, count in categories.items():
                    print(f"  - {category}: {count} items")
                
                # Show sample items
                if items:
                    print(f"\nSAMPLE MEDIA ITEMS:")
                    for i, item in enumerate(items[:5]):
                        title = item.get('title', 'Unknown')
                        category = item.get('category', 'Unknown')
                        file_size = item.get('file_size', 0)
                        size_mb = round(file_size / (1024*1024), 1) if file_size else 0
                        print(f"  {i+1}. {title} [{category}] - {size_mb}MB")
                
                return True
            else:
                print(f"ERROR: Media API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Media API error: {e}")
            return False
    
    def check_categories_api(self):
        """Check categories API"""
        if not self.token:
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.api_url}/media/categories", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS: Categories API - {len(data)} categories")
                
                for category in data:
                    name = category.get('name', 'Unknown')
                    count = category.get('count', 0)
                    print(f"  - {name}: {count} items")
                
                return True
            else:
                print(f"ERROR: Categories API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Categories API error: {e}")
            return False
    
    def check_playlists_api(self):
        """Check playlists API"""
        if not self.token:
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.api_url}/playlists/", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                playlists = data if isinstance(data, list) else data.get('items', [])
                print(f"SUCCESS: Playlists API - {len(playlists)} playlists")
                
                for playlist in playlists[:3]:
                    name = playlist.get('name', 'Unknown')
                    item_count = playlist.get('item_count', 0)
                    print(f"  - {name}: {item_count} items")
                
                return True
            else:
                print(f"ERROR: Playlists API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Playlists API error: {e}")
            return False
    
    def check_settings_api(self):
        """Check settings API"""
        if not self.token:
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.api_url}/settings/media-directories", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                directories = data.get('directories', [])
                print(f"SUCCESS: Settings API - {len(directories)} media directories configured")
                
                for directory in directories:
                    path = directory.get('path', 'Unknown')
                    enabled = directory.get('enabled', False)
                    status = "ENABLED" if enabled else "DISABLED"
                    print(f"  - {path}: {status}")
                
                return True
            else:
                print(f"ERROR: Settings API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Settings API error: {e}")
            return False
    
    def check_analytics_api(self):
        """Check analytics API"""
        if not self.token:
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.api_url}/analytics/dashboard", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS: Analytics API - Dashboard data available")
                
                # Show key metrics
                total_files = data.get('total_files', 0)
                total_size = data.get('total_size_gb', 0)
                categories = data.get('categories', {})
                
                print(f"  - Total Files: {total_files}")
                print(f"  - Total Size: {total_size}GB")
                print(f"  - Categories: {len(categories)}")
                
                return True
            else:
                print(f"ERROR: Analytics API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Analytics API error: {e}")
            return False
    
    def check_frontend_accessibility(self):
        """Check if frontend is accessible"""
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                print("SUCCESS: Frontend accessible at http://localhost:3000")
                return True
            else:
                print(f"ERROR: Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Frontend connection error: {e}")
            return False
    
    def run_comprehensive_check(self):
        """Run comprehensive database and API check"""
        print("DATABASE STATUS CHECKER")
        print("=======================")
        
        # Authentication
        if not self.authenticate():
            return False
        
        # Check all API endpoints
        results = {
            'media_api': self.check_media_api(),
            'categories_api': self.check_categories_api(), 
            'playlists_api': self.check_playlists_api(),
            'settings_api': self.check_settings_api(),
            'analytics_api': self.check_analytics_api(),
            'frontend': self.check_frontend_accessibility()
        }
        
        print("\n" + "=" * 50)
        print("DATABASE STATUS SUMMARY")
        print("=" * 50)
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        for check_name, result in results.items():
            status = "SUCCESS" if result else "FAILED"
            color_indicator = "[OK]" if result else "[FAIL]"
            print(f"{check_name:15} | {status:7} | {color_indicator}")
        
        print(f"\nOVERALL STATUS: {success_count}/{total_count} checks passed")
        
        if success_count == total_count:
            print("SUCCESS: Database is properly populated and all views can access data")
            return True
        else:
            print("WARNING: Some database or API issues detected")
            return False

def main():
    """Main entry point"""
    checker = DatabaseStatusChecker()
    success = checker.run_comprehensive_check()
    
    if success:
        print("\nRESULT: Database and all views are working correctly!")
    else:
        print("\nRESULT: Some issues detected - check individual API endpoints")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
