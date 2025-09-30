#!/usr/bin/env python3
"""
Watch1 Unraid System Test Suite
Tests the complete Watch1 system running on Unraid with direct media access
"""

import requests
import json
import time
import sys

# Unraid server configuration
UNRAID_IP = "192.168.254.14"
BACKEND_URL = f"http://{UNRAID_IP}:8000"
FRONTEND_URL = f"http://{UNRAID_IP}:3000"

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

class UnraidTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.token = None
        
    def log_test(self, test_name, success, message=""):
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}")
        if message:
            print(f"      {message}")
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
            
    def test_backend_health(self):
        """Test backend health and system info"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                media_count = data.get('media_files_found', 0)
                version = data.get('version', 'Unknown')
                environment = data.get('environment', 'Unknown')
                
                self.log_test("Backend Health", True, 
                            f"Version: {version}, Environment: {environment}, Media: {media_count} files")
                return True
            else:
                self.log_test("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, str(e))
            return False
    
    def test_authentication(self):
        """Test authentication system"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = requests.post(f"{BACKEND_URL}/api/v1/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.log_test("Authentication", True, "JWT token received")
                return True
            else:
                self.log_test("Authentication", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", False, str(e))
            return False
    
    def test_media_api(self):
        """Test media API with direct Unraid access"""
        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
                
            response = requests.get(f"{BACKEND_URL}/api/v1/media/", 
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                total_files = data.get('total', 0)
                items = data.get('items', [])
                
                self.log_test("Media API", True, 
                            f"Retrieved {total_files} files, {len(items)} in response")
                
                # Test sample file data
                if items:
                    sample_file = items[0]
                    filename = sample_file.get('filename', 'Unknown')
                    category = sample_file.get('category', 'Unknown')
                    self.log_test("Media File Data", True, 
                                f"Sample: {filename} ({category})")
                
                return True
            else:
                self.log_test("Media API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Media API", False, str(e))
            return False
    
    def test_categories_api(self):
        """Test categories API"""
        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
                
            response = requests.get(f"{BACKEND_URL}/api/v1/media/categories", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                category_count = len(categories)
                
                category_summary = []
                for cat, count in categories.items():
                    category_summary.append(f"{cat}: {count}")
                
                self.log_test("Categories API", True, 
                            f"{category_count} categories - {', '.join(category_summary)}")
                return True
            else:
                self.log_test("Categories API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Categories API", False, str(e))
            return False
    
    def test_health_endpoint(self):
        """Test health monitoring endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'Unknown')
                environment = data.get('environment', 'Unknown')
                
                self.log_test("Health Endpoint", True, 
                            f"Status: {status}, Environment: {environment}")
                return True
            else:
                self.log_test("Health Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e))
            return False
    
    def test_unraid_media_access(self):
        """Test direct Unraid media access"""
        try:
            # Test that the backend can access Unraid media
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                media_count = data.get('media_files_found', 0)
                
                if media_count > 0:
                    self.log_test("Unraid Media Access", True, 
                                f"Direct access to {media_count} media files")
                    return True
                else:
                    self.log_test("Unraid Media Access", False, "No media files detected")
                    return False
            else:
                self.log_test("Unraid Media Access", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Unraid Media Access", False, str(e))
            return False
    
    def test_docker_containers(self):
        """Test Docker container status (requires SSH access)"""
        # This would require SSH access to test container status
        # For now, we'll test if services are responding
        backend_ok = False
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=5)
            backend_ok = response.status_code == 200
        except:
            pass
        
        if backend_ok:
            self.log_test("Docker Containers", True, "Backend container responding")
            return True
        else:
            self.log_test("Docker Containers", False, "Backend container not responding")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend-backend communication"""
        try:
            # Test preflight request
            headers = {
                'Origin': f'http://{UNRAID_IP}:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{BACKEND_URL}/api/v1/auth/login", 
                                      headers=headers, timeout=5)
            
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            
            if response.status_code in [200, 204] and cors_headers:
                self.log_test("CORS Configuration", True, 
                            f"CORS enabled: {cors_headers}")
                return True
            else:
                self.log_test("CORS Configuration", False, 
                            f"CORS issue: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("CORS Configuration", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("WATCH1 UNRAID SYSTEM TEST SUITE")
        print("=" * 50)
        print(f"Testing Unraid server: {UNRAID_IP}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print("")
        
        # Run tests in order
        self.test_backend_health()
        self.test_health_endpoint()
        self.test_docker_containers()
        self.test_cors_configuration()
        self.test_authentication()
        self.test_media_api()
        self.test_categories_api()
        self.test_unraid_media_access()
        
        # Summary
        print("")
        print("TEST SUMMARY")
        print("=" * 20)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        if self.failed == 0:
            print("")
            print("SUCCESS: All tests passed!")
            print("Watch1 Unraid system is fully operational")
            print(f"Ready for production use at {FRONTEND_URL}")
            return True
        else:
            print("")
            print(f"ISSUES: {self.failed} test(s) failed")
            print("Check the failed tests above for details")
            return False

def main():
    """Main test runner"""
    test_suite = UnraidTestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
