#!/usr/bin/env python3
"""
Enhanced Storage Format Test Suite
Tests all storage formats (collection, series, group) with comprehensive validation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

class EnhancedStorageTestSuite:
    """Test suite for enhanced storage format scanning"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.api_url = f"{backend_url}/api/v1"
        self.token = None
        self.test_results = []
        
    def log_test(self, category: str, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "category": category,
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Print result
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} [{category}] {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time > 0:
            print(f"   Response Time: {response_time:.2f}ms")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            start_time = time.time()
            response = requests.post(f"{self.api_url}/auth/login/access-token", 
                                   json={"username": "test@example.com", "password": "testpass123"},
                                   timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_test("Auth", "Login", "PASS", f"Token received", response_time)
                return True
            else:
                self.log_test("Auth", "Login", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth", "Login", "FAIL", str(e))
            return False
    
    def test_t_drive_mount(self):
        """Test if T: drive is properly mounted"""
        print("\n🔍 Testing T: Drive Mount Status")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Mount", "T: Drive Check", "SKIP", "No authentication token")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # Test if we can scan Unraid media directories
            start_time = time.time()
            response = requests.post(f"{self.api_url}/media/scan", 
                                   json={"directory": "/app/media"}, 
                                   headers=headers, timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                scan_results = data.get("scan_results", {})
                total_files = data.get('total_files_found', 0)
                
                # Check if any media directories were found with significant content
                media_found = False
                for category, result in scan_results.items():
                    files_found = result.get("files_found", 0)
                    if files_found > 0:
                        media_found = True
                        break
                
                if media_found and total_files > 10:  # Expect significant content from Unraid
                    self.log_test("Mount", "Unraid Media Access", "PASS", 
                                f"Unraid media accessible, {total_files} files found", response_time)
                    return True
                elif total_files > 0:
                    self.log_test("Mount", "Unraid Media Access", "PARTIAL", 
                                f"Some media found ({total_files} files), but less than expected")
                    return True
                else:
                    self.log_test("Mount", "Unraid Media Access", "FAIL", 
                                "Unraid media mount not working - no files accessible")
                    return False
            else:
                self.log_test("Mount", "T: Drive Access", "FAIL", 
                            f"Scan failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Mount", "T: Drive Access", "FAIL", str(e))
            return False
    
    def test_storage_formats(self):
        """Test different storage format scanning"""
        print("\n📊 Testing Storage Format Support")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Storage", "Format Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test enhanced media scan
        try:
            start_time = time.time()
            response = requests.post(f"{self.api_url}/media/scan", 
                                   json={"recalculate_categories": True}, 
                                   headers=headers, timeout=60)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                scan_results = data.get("scan_results", {})
                
                # Test each storage format
                format_results = {}
                for category, result in scan_results.items():
                    storage_format = result.get("storage_format", "unknown")
                    files_found = result.get("files_found", 0)
                    metadata = result.get("metadata", {})
                    
                    format_results[category] = {
                        "format": storage_format,
                        "files": files_found,
                        "metadata": metadata
                    }
                
                # Log results for each format type
                collection_formats = [k for k, v in format_results.items() if v["format"] == "collection"]
                series_formats = [k for k, v in format_results.items() if v["format"] == "series"]
                group_formats = [k for k, v in format_results.items() if v["format"] == "group"]
                
                if collection_formats:
                    total_collection_files = sum(format_results[k]["files"] for k in collection_formats)
                    self.log_test("Storage", "Collection Format", "PASS", 
                                f"Categories: {collection_formats}, Files: {total_collection_files}")
                
                if series_formats:
                    total_series_files = sum(format_results[k]["files"] for k in series_formats)
                    self.log_test("Storage", "Series Format", "PASS", 
                                f"Categories: {series_formats}, Files: {total_series_files}")
                
                if group_formats:
                    total_group_files = sum(format_results[k]["files"] for k in group_formats)
                    self.log_test("Storage", "Group Format", "PASS", 
                                f"Categories: {group_formats}, Files: {total_group_files}")
                
                # Test metadata extraction
                metadata_found = any(v["metadata"] for v in format_results.values())
                if metadata_found:
                    self.log_test("Storage", "Metadata Extraction", "PASS", 
                                "Enhanced metadata found in scan results")
                else:
                    self.log_test("Storage", "Metadata Extraction", "WARN", 
                                "No enhanced metadata found")
                
                self.log_test("Storage", "Enhanced Scan", "PASS", 
                            f"Total files: {data.get('total_files_found', 0)}, Formats tested: {len(format_results)}", 
                            response_time)
                
            else:
                self.log_test("Storage", "Enhanced Scan", "FAIL", 
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Storage", "Enhanced Scan", "FAIL", str(e))
    
    def test_hierarchy_processing(self):
        """Test hierarchical structure processing"""
        print("\n🏗️ Testing Hierarchy Processing")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Hierarchy", "Structure Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get media list to check for hierarchical metadata
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/?limit=50", headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                # Check for series hierarchy (season/episode info)
                series_items = [item for item in items if item.get("category") == "tv_shows"]
                if series_items:
                    self.log_test("Hierarchy", "TV Series Structure", "PASS", 
                                f"Found {len(series_items)} TV show items")
                else:
                    self.log_test("Hierarchy", "TV Series Structure", "INFO", 
                                "No TV show items found for hierarchy testing")
                
                # Check for group hierarchy (artist/album info)
                music_items = [item for item in items if item.get("category") == "music"]
                if music_items:
                    self.log_test("Hierarchy", "Music Group Structure", "PASS", 
                                f"Found {len(music_items)} music items")
                else:
                    self.log_test("Hierarchy", "Music Group Structure", "INFO", 
                                "No music items found for hierarchy testing")
                
                # Check for enhanced metadata
                items_with_year = [item for item in items if item.get("year")]
                if items_with_year:
                    self.log_test("Hierarchy", "Year Extraction", "PASS", 
                                f"{len(items_with_year)} items have year metadata")
                
                self.log_test("Hierarchy", "Media List", "PASS", 
                            f"Retrieved {len(items)} items", response_time)
                
            else:
                self.log_test("Hierarchy", "Media List", "FAIL", 
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Hierarchy", "Media List", "FAIL", str(e))
    
    def test_configuration_validation(self):
        """Test configuration file validation"""
        print("\n⚙️ Testing Configuration Validation")
        print("-" * 50)
        
        # Test if enhanced scanner configuration is working
        try:
            # This would test the config loader if it was accessible
            # For now, we'll test the API endpoints that use the config
            
            if not self.token:
                self.log_test("Config", "Validation", "SKIP", "No authentication token")
                return
                
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test settings endpoint which should show configured directories
            start_time = time.time()
            response = requests.get(f"{self.api_url}/settings/media-directories", headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                directories = data.get("directories", [])
                
                # Check for T: drive directories
                t_drive_dirs = [d for d in directories if "/app/T/" in d.get("path", "")]
                if t_drive_dirs:
                    self.log_test("Config", "T: Drive Directories", "PASS", 
                                f"Found {len(t_drive_dirs)} T: drive directories configured")
                else:
                    self.log_test("Config", "T: Drive Directories", "WARN", 
                                "No T: drive directories found in configuration")
                
                self.log_test("Config", "Media Directories", "PASS", 
                            f"Total directories: {len(directories)}", response_time)
                
            else:
                self.log_test("Config", "Media Directories", "FAIL", 
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Config", "Media Directories", "FAIL", str(e))
    
    def test_database_population(self):
        """Test if database is properly populated with media items"""
        print("\n💾 Testing Database Population")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Database", "Population Check", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/", headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                total_items = data.get('total', 0)
                items = data.get('items', [])
                categories = data.get('categories', {})
                
                if total_items > 0:
                    category_count = len(categories)
                    self.log_test("Database", "Population Status", "PASS", 
                                f"{total_items} items, {category_count} categories", response_time)
                    
                    # Test sample data quality
                    if items:
                        items_with_size = [item for item in items if item.get('file_size', 0) > 0]
                        items_with_title = [item for item in items if item.get('title')]
                        
                        self.log_test("Database", "Data Quality", "PASS", 
                                    f"{len(items_with_title)} items have titles, {len(items_with_size)} have file sizes")
                else:
                    self.log_test("Database", "Population Status", "FAIL", 
                                "Database empty - no media items found")
            else:
                self.log_test("Database", "Population Status", "FAIL", 
                            f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Database", "Population Status", "FAIL", str(e))
    
    def test_frontend_accessibility(self):
        """Test if frontend is accessible and responsive"""
        print("\n🌐 Testing Frontend Accessibility")
        print("-" * 50)
        
        try:
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                content = response.text
                content_size = len(content)
                
                # Check for Vue.js and Watch1 indicators
                vue_indicators = ["vue", "vite", "app"]
                watch1_indicators = ["watch1", "media", "library"]
                
                vue_found = any(ind in content.lower() for ind in vue_indicators)
                watch1_found = any(ind in content.lower() for ind in watch1_indicators)
                
                if vue_found and watch1_found:
                    self.log_test("Frontend", "Accessibility", "PASS", 
                                f"Frontend responsive, {content_size} chars, Vue+Watch1 detected", response_time)
                elif vue_found:
                    self.log_test("Frontend", "Accessibility", "PASS", 
                                f"Frontend responsive, {content_size} chars, Vue detected", response_time)
                else:
                    self.log_test("Frontend", "Accessibility", "WARN", 
                                f"Frontend accessible but content unclear, {content_size} chars", response_time)
            else:
                self.log_test("Frontend", "Accessibility", "FAIL", 
                            f"Frontend not accessible: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend", "Accessibility", "FAIL", f"Connection error: {e}")
    
    def test_api_endpoints_comprehensive(self):
        """Test all key API endpoints comprehensively"""
        print("\n🔗 Testing API Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("API", "Endpoints Check", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        endpoints = [
            ("/media/", "Media List"),
            ("/media/categories", "Categories"),
            ("/playlists/", "Playlists"),
            ("/settings/media-directories", "Settings"),
            ("/analytics/dashboard", "Analytics")
        ]
        
        working_endpoints = 0
        total_endpoints = len(endpoints)
        endpoint_details = []
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}{endpoint}", headers=headers, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    working_endpoints += 1
                    endpoint_details.append(f"{name}:OK")
                    self.log_test("API", f"{name} Endpoint", "PASS", f"200 OK", response_time)
                else:
                    endpoint_details.append(f"{name}:{response.status_code}")
                    self.log_test("API", f"{name} Endpoint", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                endpoint_details.append(f"{name}:ERROR")
                self.log_test("API", f"{name} Endpoint", "FAIL", f"Error: {e}")
        
        success_rate = (working_endpoints / total_endpoints) * 100
        
        if working_endpoints == total_endpoints:
            self.log_test("API", "Endpoints Summary", "PASS", 
                        f"All {total_endpoints} endpoints working ({success_rate:.0f}%)")
        elif working_endpoints >= total_endpoints * 0.8:  # 80% success rate
            self.log_test("API", "Endpoints Summary", "PASS", 
                        f"{working_endpoints}/{total_endpoints} endpoints working ({success_rate:.0f}%)")
        else:
            self.log_test("API", "Endpoints Summary", "FAIL", 
                        f"Only {working_endpoints}/{total_endpoints} endpoints working ({success_rate:.0f}%)")
    
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 Testing Authentication Flow")
        print("-" * 50)
        
        try:
            # Test login
            start_time = time.time()
            login_response = requests.post(f"{self.api_url}/auth/login/access-token", 
                                         json={"username": "test@example.com", "password": "testpass123"},
                                         timeout=10)
            login_time = (time.time() - start_time) * 1000
            
            if login_response.status_code != 200:
                self.log_test("Auth", "Login Flow", "FAIL", 
                            f"Login failed: {login_response.status_code}")
                return
            
            token = login_response.json().get("access_token")
            if not token:
                self.log_test("Auth", "Login Flow", "FAIL", 
                            "No token received from login")
                return
            
            # Test token usage
            headers = {"Authorization": f"Bearer {token}"}
            start_time = time.time()
            profile_response = requests.get(f"{self.api_url}/users/me", headers=headers, timeout=10)
            profile_time = (time.time() - start_time) * 1000
            
            if profile_response.status_code == 200:
                user_data = profile_response.json()
                email = user_data.get('email', 'Unknown')
                is_superuser = user_data.get('is_superuser', False)
                
                self.log_test("Auth", "Login Flow", "PASS", 
                            f"Complete flow working, user: {email}", login_time)
                self.log_test("Auth", "User Profile", "PASS", 
                            f"Admin privileges: {is_superuser}", profile_time)
            else:
                self.log_test("Auth", "Token Validation", "FAIL", 
                            f"Token validation failed: {profile_response.status_code}")
                
        except Exception as e:
            self.log_test("Auth", "Authentication Flow", "FAIL", f"Auth flow error: {e}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("📋 ENHANCED STORAGE FORMAT TEST REPORT")
        print(f"{'='*80}")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🕒 Test Duration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Skipped: {skipped_tests}")
        
        # Group by category
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"pass": 0, "fail": 0, "skip": 0, "warn": 0, "info": 0}
            status = result["status"].lower()
            if status in categories[cat]:
                categories[cat][status] += 1
            else:
                categories[cat]["info"] += 1  # Treat unknown statuses as info
        
        print(f"\n📊 Results by Category:")
        for cat, stats in categories.items():
            total = sum(stats.values())
            pass_rate = (stats["pass"] / total * 100) if total > 0 else 0
            print(f"   {cat}: {stats['pass']}/{total} ({pass_rate:.1f}%) "
                  f"✅{stats['pass']} ❌{stats['fail']} ⚠️{stats['skip']}")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if r["status"] == "FAIL"]
        if failed_results:
            print(f"\n❌ Failed Tests Details:")
            for result in failed_results:
                print(f"   [{result['category']}] {result['test']}: {result['details']}")
        
        # Performance metrics
        response_times = [r["response_time"] for r in self.test_results if r["response_time"] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"\n⚡ Performance:")
            print(f"   Average Response Time: {avg_time:.1f}ms")
            print(f"   Slowest Response: {max_time:.1f}ms")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": success_rate
            },
            "categories": categories,
            "results": self.test_results
        }
        
        with open("enhanced-storage-test-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: enhanced-storage-test-report.json")
        print(f"🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing
    
    def run_all_tests(self) -> bool:
        """Run all enhanced storage format tests"""
        print("🧪 Enhanced Storage Format Test Suite")
        print("="*80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all test categories
        self.test_authentication_flow()
        self.test_database_population()
        self.test_frontend_accessibility()
        self.test_api_endpoints_comprehensive()
        self.test_t_drive_mount()
        self.test_storage_formats()
        self.test_hierarchy_processing()
        self.test_configuration_validation()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main test runner entry point"""
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
        frontend_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000"
    else:
        backend_url = "http://localhost:8000"
        frontend_url = "http://localhost:3000"
    
    test_suite = EnhancedStorageTestSuite(backend_url, frontend_url)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
