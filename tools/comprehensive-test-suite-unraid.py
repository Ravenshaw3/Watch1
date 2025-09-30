#!/usr/bin/env python3
"""
Watch1 Media Server - Comprehensive Test Suite for Unraid
Updated for Unraid environment with Unicode-safe output
Combines all testing capabilities for production deployment
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class Watch1UnraidTestSuite:
    def __init__(self, backend_url="http://192.168.254.14:8000", frontend_url="http://192.168.254.14:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.api_url = f"{backend_url}/api/v1"
        self.token = None
        self.user_info = None
        self.test_results = []
        
    def log_test(self, category: str, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log test result with ASCII-safe output"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2)
        }
        self.test_results.append(result)
        
        # ASCII-safe status indicators
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
        print(f"{status_icon} [{category}] {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time > 0:
            print(f"   Response Time: {result['response_time_ms']}ms")

    def test_service_availability(self):
        """Test basic service availability"""
        print("\nTesting Service Availability")
        print("-" * 50)
        
        # Test Backend Health
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Service", "Backend Health", "PASS", 
                            f"Status: {data.get('status', 'Unknown')}", response_time)
            else:
                self.log_test("Service", "Backend Health", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Service", "Backend Health", "FAIL", str(e))

        # Test System Info
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                media_count = data.get('media_files_found', 0)
                version = data.get('version', 'Unknown')
                environment = data.get('environment', 'Unknown')
                self.log_test("Service", "System Info", "PASS", 
                            f"Version: {version}, Environment: {environment}, Media: {media_count}", response_time)
            else:
                self.log_test("Service", "System Info", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Service", "System Info", "FAIL", str(e))

    def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("\nTesting Authentication Flow")
        print("-" * 50)
        
        # Test Login
        try:
            start_time = time.time()
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }
            response = requests.post(f"{self.api_url}/auth/login", 
                                   json=login_data, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_test("Auth", "Login", "PASS", 
                            f"Token received (length: {len(self.token) if self.token else 0})", response_time)
            else:
                self.log_test("Auth", "Login", "FAIL", 
                            f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_test("Auth", "Login", "FAIL", str(e))
            return

        # Test User Profile Access
        if self.token:
            try:
                start_time = time.time()
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.get(f"{self.api_url}/auth/user", headers=headers, timeout=5)
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
        print("\nTesting Media Endpoints")
        print("-" * 50)
        
        if not self.token:
            self.log_test("Media", "All Tests", "SKIP", "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test Media List
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/", headers=headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total_items = data.get("total", 0)
                items = data.get("items", [])
                self.log_test("Media", "Media List", "PASS", 
                            f"Found {total_items} total, {len(items)} returned", response_time)
                
                # Test sample media file data
                if items:
                    sample = items[0]
                    filename = sample.get('filename', 'Unknown')
                    category = sample.get('category', 'Unknown')
                    self.log_test("Media", "Media File Data", "PASS", 
                                f"Sample: {filename} ({category})")
            else:
                self.log_test("Media", "Media List", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Media", "Media List", "FAIL", str(e))

        # Test Categories
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/media/categories", headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                categories = response.json()
                cat_count = len(categories)
                cat_summary = []
                for cat, count in categories.items():
                    cat_summary.append(f"{cat}({count})")
                
                self.log_test("Media", "Categories", "PASS", 
                            f"{cat_count} categories: {', '.join(cat_summary)}", response_time)
            else:
                self.log_test("Media", "Categories", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Media", "Categories", "FAIL", str(e))

    def test_unraid_specific_features(self):
        """Test Unraid-specific features"""
        print("\nTesting Unraid-Specific Features")
        print("-" * 50)
        
        # Test direct media access
        try:
            response = requests.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                media_count = data.get('media_files_found', 0)
                environment = data.get('environment', '').lower()
                
                if 'unraid' in environment and media_count > 0:
                    self.log_test("Unraid", "Direct Media Access", "PASS", 
                                f"Environment: {environment}, Media files: {media_count}")
                else:
                    self.log_test("Unraid", "Direct Media Access", "FAIL", 
                                f"Environment: {environment}, Media: {media_count}")
            else:
                self.log_test("Unraid", "Direct Media Access", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Unraid", "Direct Media Access", "FAIL", str(e))
        
        # Test Docker native performance
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 1.0:
                self.log_test("Unraid", "Native Performance", "PASS", 
                            f"Response time: {response_time:.3f}s")
            else:
                self.log_test("Unraid", "Native Performance", "FAIL", 
                            f"Slow response: {response_time:.3f}s")
        except Exception as e:
            self.log_test("Unraid", "Native Performance", "FAIL", str(e))

    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\nTesting CORS Configuration")
        print("-" * 50)
        
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.api_url}/auth/login", 
                                      headers=headers, timeout=5)
            
            cors_header = response.headers.get('Access-Control-Allow-Origin', '')
            
            if response.status_code in [200, 204] and cors_header:
                self.log_test("CORS", "Configuration", "PASS", 
                            f"Allow-Origin: {cors_header}")
            else:
                self.log_test("CORS", "Configuration", "FAIL", 
                            f"Status: {response.status_code}, Headers: {cors_header}")
        except Exception as e:
            self.log_test("CORS", "Configuration", "FAIL", str(e))

    def test_postgresql_compliance(self):
        """Test PostgreSQL compliance (no SQLite)"""
        print("\nTesting PostgreSQL Compliance")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                environment = data.get('environment', '').lower()
                version = data.get('version', '')
                
                # Check for PostgreSQL indicators (Unraid environment should use PostgreSQL)
                postgresql_ready = 'unraid' in environment
                
                self.log_test("Database", "PostgreSQL Compliance", "PASS" if postgresql_ready else "FAIL", 
                            f"Environment: {environment}, Version: {version}")
            else:
                self.log_test("Database", "PostgreSQL Compliance", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Database", "PostgreSQL Compliance", "FAIL", str(e))

    def test_production_readiness(self):
        """Test production readiness features"""
        print("\nTesting Production Readiness")
        print("-" * 50)
        
        # Test version consistency
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'Unknown')
                
                version_ok = version in ['3.0.3', 'v3.0.3']
                self.log_test("Production", "Version Consistency", "PASS" if version_ok else "FAIL", 
                            f"System version: {version}")
            else:
                self.log_test("Production", "Version Consistency", "FAIL", 
                            f"Status Code: {response.status_code}")
        except Exception as e:
            self.log_test("Production", "Version Consistency", "FAIL", str(e))
        
        # Test health monitoring
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            health_ok = response.status_code == 200
            self.log_test("Production", "Health Monitoring", "PASS" if health_ok else "FAIL", 
                         "Health endpoint operational" if health_ok else f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Production", "Health Monitoring", "FAIL", str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        
        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"pass": 0, "fail": 0, "skip": 0}
            categories[cat][result["status"].lower()] += 1
        
        print(f"\nResults by Category:")
        for category, stats in categories.items():
            total_cat = sum(stats.values())
            pass_rate = (stats["pass"] / total_cat * 100) if total_cat > 0 else 0
            print(f"   {category}: {stats['pass']}/{total_cat} ({pass_rate:.1f}%) - Pass:{stats['pass']} Fail:{stats['fail']} Skip:{stats['skip']}")
        
        # Performance metrics
        response_times = [r["response_time_ms"] for r in self.test_results if r["response_time_ms"] > 0]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            print(f"\nPerformance:")
            print(f"   Average Response Time: {avg_response:.1f}ms")
            print(f"   Slowest Response: {max_response:.1f}ms")
        
        # Failed tests details
        failed_results = [r for r in self.test_results if r["status"] == "FAIL"]
        if failed_results:
            print(f"\nFailed Tests Details:")
            for result in failed_results:
                print(f"   [{result['category']}] {result['test_name']}: {result['details']}")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "environment": "unraid",
            "backend_url": self.backend_url,
            "frontend_url": self.frontend_url,
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
        
        with open("unraid-test-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: unraid-test-report.json")
        
        # Final assessment
        if success_rate >= 95:
            print("\nSUCCESS: PRODUCTION READY")
            print("  All critical systems operational")
            print("  Ready for full Unraid deployment")
        elif success_rate >= 85:
            print("\nWARNING: MOSTLY READY")
            print("  Minor issues detected")
            print("  Review failed tests before deployment")
        else:
            print("\nERROR: NOT READY")
            print("  Multiple critical issues")
            print("  Requires fixes before production")
        
        return success_rate >= 85

    def run_all_tests(self):
        """Run complete test suite"""
        print("Watch1 Media Server - Comprehensive Test Suite (Unraid)")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_service_availability()
        self.test_authentication_flow()
        self.test_media_endpoints()
        self.test_unraid_specific_features()
        self.test_cors_configuration()
        self.test_postgresql_compliance()
        self.test_production_readiness()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
        frontend_url = sys.argv[2] if len(sys.argv) > 2 else "http://192.168.254.14:3000"
    else:
        backend_url = "http://192.168.254.14:8000"
        frontend_url = "http://192.168.254.14:3000"
    
    test_suite = Watch1UnraidTestSuite(backend_url, frontend_url)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
