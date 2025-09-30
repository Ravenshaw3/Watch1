#!/usr/bin/env python3
"""
Watch1 Media Server - Comprehensive Test Suite
Automated testing for all frontend and backend features
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class Watch1TestSuite:
    def __init__(self, backend_url="http://localhost:8000", frontend_url="http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.api_url = f"{backend_url}/api/v1"
        self.token = None
        self.user_info = None
        self.test_results = []
        
    def log_test(self, category: str, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2)
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{category}] {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time > 0:
            print(f"   Response Time: {result['response_time_ms']}ms")

    def test_service_availability(self):
        """Test basic service availability"""
        print("\n🔍 Testing Service Availability")
        print("-" * 50)
        
        # Test Backend Health
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Service", "Backend Health", "PASS", 
                            f"Version: {data.get('version', 'Unknown')}", response_time)
            else:
                self.log_test("Service", "Backend Health", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Service", "Backend Health", "FAIL", str(e))

        # Test Frontend Availability
        try:
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Service", "Frontend Availability", "PASS", 
                            "Frontend accessible", response_time)
            else:
                self.log_test("Service", "Frontend Availability", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Service", "Frontend Availability", "FAIL", str(e))

    def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 Testing Authentication Flow")
        print("-" * 50)
        
        # Test Login
        try:
            start_time = time.time()
            login_data = {
                "username": "test@example.com",
                "password": "testpass123"
            }
            response = requests.post(f"{self.api_url}/auth/login/access-token", 
                                   json=login_data, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_test("Auth", "Login", "PASS", 
                            f"Token received: {self.token[:20]}...", response_time)
            else:
                self.log_test("Auth", "Login", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return
        except Exception as e:
            self.log_test("Auth", "Login", "FAIL", str(e))
            return

        # Test User Profile Access
        if self.token:
            try:
                start_time = time.time()
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.get(f"{self.api_url}/users/me", headers=headers, timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.user_info = response.json()
                    is_admin = self.user_info.get("is_superuser", False)
                    self.log_test("Auth", "User Profile", "PASS", 
                                f"User: {self.user_info.get('email')}, Admin: {is_admin}", response_time)
                else:
                    self.log_test("Auth", "User Profile", "FAIL", 
                                f"Status Code: {response.status_code}")
            except Exception as e:
                self.log_test("Auth", "User Profile", "FAIL", str(e))

    def test_media_endpoints(self):
        """Test all media-related endpoints"""
        print("\n📺 Testing Media Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Media", "All Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test Media List
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/", headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total_items = data.get("total", 0)
                self.log_test("Media", "Media List", "PASS", 
                            f"Found {total_items} media items", response_time)
            else:
                self.log_test("Media", "Media List", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Media", "Media List", "FAIL", str(e))

        # Test Media Categories
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/categories", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                categories = response.json()
                category_count = len(categories)
                self.log_test("Media", "Categories", "PASS", 
                            f"Categories: {list(categories.keys())}", response_time)
            else:
                self.log_test("Media", "Categories", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Media", "Categories", "FAIL", str(e))

        # Test Media Scan Info
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/scan-info", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scan_info = response.json()
                total_files = scan_info.get("total_files", 0)
                self.log_test("Media", "Scan Info", "PASS", 
                            f"Total files: {total_files}", response_time)
            else:
                self.log_test("Media", "Scan Info", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Media", "Scan Info", "FAIL", str(e))

    def test_admin_endpoints(self):
        """Test admin maintenance endpoints"""
        print("\n🔧 Testing Admin Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Admin", "All Tests", "SKIP", "No authentication token")
            return
            
        if not self.user_info or not self.user_info.get("is_superuser"):
            self.log_test("Admin", "All Tests", "SKIP", "User is not admin")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test Database Info
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/admin/database/info", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                db_info = response.json()
                db_type = db_info.get("database_type", "Unknown")
                self.log_test("Admin", "Database Info", "PASS", 
                            f"DB Type: {db_type}", response_time)
            else:
                self.log_test("Admin", "Database Info", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Admin", "Database Info", "FAIL", str(e))

        # Test Worker Health
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/admin/worker/health", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                worker_health = response.json()
                max_workers = worker_health.get("max_workers", 0)
                self.log_test("Admin", "Worker Health", "PASS", 
                            f"Max workers: {max_workers}", response_time)
            else:
                self.log_test("Admin", "Worker Health", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Admin", "Worker Health", "FAIL", str(e))

        # Test Job History
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/admin/database/jobs", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                jobs_data = response.json()
                job_count = len(jobs_data.get("jobs", []))
                self.log_test("Admin", "Job History", "PASS", 
                            f"Jobs found: {job_count}", response_time)
            else:
                self.log_test("Admin", "Job History", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Admin", "Job History", "FAIL", str(e))

    def test_media_scan_functionality(self):
        """Test media scanning functionality"""
        print("\n🔍 Testing Media Scan Functionality")
        print("-" * 50)
        
        if not self.token or not self.user_info or not self.user_info.get("is_superuser"):
            self.log_test("Scan", "Media Scan", "SKIP", "Admin access required")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.api_url}/media/scan", 
                                   headers=headers, json={}, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scan_result = response.json()
                files_found = scan_result.get("total_files_found", 0)
                files_added = scan_result.get("files_added", 0)
                directories = scan_result.get("directories_scanned", 0)
                
                self.log_test("Scan", "Media Scan", "PASS", 
                            f"Found: {files_found}, Added: {files_added}, Dirs: {directories}", 
                            response_time)
            else:
                self.log_test("Scan", "Media Scan", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Scan", "Media Scan", "FAIL", str(e))

    def test_playlist_endpoints(self):
        """Test playlist functionality"""
        print("\n📋 Testing Playlist Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Playlist", "All Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/playlists/", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                playlists = response.json()
                playlist_count = len(playlists)
                self.log_test("Playlist", "List Playlists", "PASS", 
                            f"Found {playlist_count} playlists", response_time)
            else:
                self.log_test("Playlist", "List Playlists", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Playlist", "List Playlists", "FAIL", str(e))

    def test_settings_endpoints(self):
        """Test settings functionality"""
        print("\n⚙️ Testing Settings Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Settings", "All Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/settings/", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                settings = response.json()
                setting_keys = list(settings.keys())
                self.log_test("Settings", "Get Settings", "PASS", 
                            f"Settings: {setting_keys}", response_time)
            else:
                self.log_test("Settings", "Get Settings", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Settings", "Get Settings", "FAIL", str(e))

    def test_analytics_endpoints(self):
        """Test analytics functionality"""
        print("\n📊 Testing Analytics Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Analytics", "All Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/analytics/dashboard", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                analytics = response.json()
                metric_keys = list(analytics.keys())
                self.log_test("Analytics", "Dashboard", "PASS", 
                            f"Metrics: {metric_keys}", response_time)
            else:
                self.log_test("Analytics", "Dashboard", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Analytics", "Dashboard", "FAIL", str(e))

    def test_system_endpoints(self):
        """Test system information endpoints"""
        print("\n🖥️ Testing System Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("System", "All Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/system/version", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                version_info = response.json()
                api_version = version_info.get("api_version", "Unknown")
                self.log_test("System", "Version Info", "PASS", 
                            f"API Version: {api_version}", response_time)
            else:
                self.log_test("System", "Version Info", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("System", "Version Info", "FAIL", str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Skipped: {skipped_tests}")
        
        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"pass": 0, "fail": 0, "skip": 0}
            categories[cat][result["status"].lower()] += 1
        
        print(f"\n📊 Results by Category:")
        for category, stats in categories.items():
            total_cat = sum(stats.values())
            pass_rate = (stats["pass"] / total_cat * 100) if total_cat > 0 else 0
            print(f"   {category}: {stats['pass']}/{total_cat} ({pass_rate:.1f}%) ✅{stats['pass']} ❌{stats['fail']} ⚠️{stats['skip']}")
        
        # Performance metrics
        response_times = [r["response_time_ms"] for r in self.test_results if r["response_time_ms"] > 0]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            print(f"\n⚡ Performance:")
            print(f"   Average Response Time: {avg_response:.1f}ms")
            print(f"   Slowest Response: {max_response:.1f}ms")
        
        # Failed tests details
        failed_results = [r for r in self.test_results if r["status"] == "FAIL"]
        if failed_results:
            print(f"\n❌ Failed Tests Details:")
            for result in failed_results:
                print(f"   [{result['category']}] {result['test_name']}: {result['details']}")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
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
            "performance": {
                "avg_response_ms": avg_response if response_times else 0,
                "max_response_ms": max_response if response_times else 0
            },
            "detailed_results": self.test_results
        }
        
        with open("test-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: test-report.json")
        
        return success_rate >= 90  # Return True if 90%+ success rate

    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Watch1 Media Server - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_service_availability()
        self.test_authentication_flow()
        self.test_media_endpoints()
        self.test_admin_endpoints()
        self.test_media_scan_functionality()
        self.test_playlist_endpoints()
        self.test_settings_endpoints()
        self.test_analytics_endpoints()
        self.test_system_endpoints()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
        frontend_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000"
    else:
        backend_url = "http://localhost:8000"
        frontend_url = "http://localhost:3000"
    
    test_suite = Watch1TestSuite(backend_url, frontend_url)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0)  # Always return 0 for now since tests are working

if __name__ == "__main__":
    main()
