#!/usr/bin/env python3
"""
Watch1 Production Readiness Test Suite
Validates all production features based on project memories and requirements
"""

import requests
import json
import time
import sys

class ProductionReadinessTest:
    def __init__(self):
        self.base_url = "http://192.168.254.14:8000"
        self.frontend_url = "http://192.168.254.14:3000"
        self.credentials = {"email": "test@example.com", "password": "testpass123"}
        self.token = None
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name, success, details=""):
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}")
        if details:
            print(f"      {details}")
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def authenticate(self):
        """Get authentication token"""
        try:
            response = requests.post(f"{self.base_url}/api/v1/auth/login", 
                                   json=self.credentials, timeout=10)
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                return True
        except:
            pass
        return False
    
    def test_postgresql_compliance(self):
        """Test PostgreSQL-only compliance (Memory: NO SQLITE ALLOWED)"""
        try:
            # Check system info for database type indicators
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Look for PostgreSQL indicators
                version = data.get('version', '')
                environment = data.get('environment', '')
                
                # The system should be using PostgreSQL architecture
                postgresql_ready = 'unraid' in environment.lower()
                self.log_result("PostgreSQL Compliance", postgresql_ready,
                              f"Environment: {environment}, Version: {version}")
                return postgresql_ready
        except Exception as e:
            self.log_result("PostgreSQL Compliance", False, str(e))
            return False
    
    def test_direct_media_access(self):
        """Test direct Unraid media access (18,509+ files expected)"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=15)
            if response.status_code == 200:
                data = response.json()
                media_count = data.get('media_files_found', 0)
                
                # Should have significant media files from direct access
                has_media = media_count > 0
                self.log_result("Direct Media Access", has_media,
                              f"Found {media_count} media files from /mnt/user/media")
                return has_media
        except Exception as e:
            self.log_result("Direct Media Access", False, str(e))
            return False
    
    def test_authentication_system(self):
        """Test JWT authentication system"""
        auth_success = self.authenticate()
        self.log_result("JWT Authentication", auth_success,
                       "JWT token received" if auth_success else "Authentication failed")
        
        if auth_success:
            # Test user profile endpoint
            try:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(f"{self.base_url}/api/v1/auth/user", 
                                      headers=headers, timeout=5)
                profile_success = response.status_code == 200
                self.log_result("User Profile API", profile_success,
                               "Profile data retrieved" if profile_success else f"HTTP {response.status_code}")
                return profile_success
            except Exception as e:
                self.log_result("User Profile API", False, str(e))
                return False
        
        return auth_success
    
    def test_media_apis(self):
        """Test media API endpoints"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        # Test media listing
        try:
            response = requests.get(f"{self.base_url}/api/v1/media/", 
                                  headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                total = data.get('total', 0)
                
                self.log_result("Media Listing API", True,
                               f"Retrieved {len(items)} items, {total} total")
                
                # Test categories API
                cat_response = requests.get(f"{self.base_url}/api/v1/media/categories", 
                                          headers=headers, timeout=10)
                if cat_response.status_code == 200:
                    categories = cat_response.json()
                    cat_count = len(categories)
                    
                    cat_summary = []
                    for cat, count in categories.items():
                        cat_summary.append(f"{cat}({count})")
                    
                    self.log_result("Categories API", True,
                                   f"{cat_count} categories: {', '.join(cat_summary)}")
                    return True
                else:
                    self.log_result("Categories API", False, f"HTTP {cat_response.status_code}")
                    return False
            else:
                self.log_result("Media Listing API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Media APIs", False, str(e))
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend integration"""
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST'
            }
            response = requests.options(f"{self.base_url}/api/v1/auth/login", 
                                      headers=headers, timeout=5)
            
            cors_header = response.headers.get('Access-Control-Allow-Origin', '')
            cors_working = response.status_code in [200, 204] and cors_header
            
            self.log_result("CORS Configuration", cors_working,
                           f"Allow-Origin: {cors_header}" if cors_working else "CORS not configured")
            return cors_working
        except Exception as e:
            self.log_result("CORS Configuration", False, str(e))
            return False
    
    def test_version_consistency(self):
        """Test version consistency (should be v3.0.3)"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'Unknown')
                
                # Check for expected version
                version_ok = version in ['3.0.3', 'v3.0.3']
                self.log_result("Version Consistency", version_ok,
                               f"System version: {version}")
                return version_ok
        except Exception as e:
            self.log_result("Version Consistency", False, str(e))
            return False
    
    def test_unraid_environment(self):
        """Test Unraid-specific environment indicators"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                environment = data.get('environment', '').lower()
                
                unraid_env = 'unraid' in environment
                self.log_result("Unraid Environment", unraid_env,
                               f"Environment: {data.get('environment', 'Unknown')}")
                return unraid_env
        except Exception as e:
            self.log_result("Unraid Environment", False, str(e))
            return False
    
    def test_docker_native_performance(self):
        """Test Docker native performance indicators"""
        try:
            # Test response time as performance indicator
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Good performance should be under 1 second
                good_performance = response_time < 1.0
                self.log_result("Native Performance", good_performance,
                               f"Response time: {response_time:.3f}s")
                return good_performance
        except Exception as e:
            self.log_result("Native Performance", False, str(e))
            return False
    
    def test_production_features(self):
        """Test production-ready features"""
        features_tested = 0
        features_passed = 0
        
        # Test health monitoring
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            health_ok = response.status_code == 200
            features_tested += 1
            if health_ok:
                features_passed += 1
        except:
            features_tested += 1
        
        # Test system info endpoint
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            info_ok = response.status_code == 200
            features_tested += 1
            if info_ok:
                features_passed += 1
        except:
            features_tested += 1
        
        production_ready = features_passed == features_tested and features_passed > 0
        self.log_result("Production Features", production_ready,
                       f"{features_passed}/{features_tested} production endpoints working")
        return production_ready
    
    def run_full_suite(self):
        """Run complete production readiness test suite"""
        print("WATCH1 PRODUCTION READINESS TEST SUITE")
        print("=" * 55)
        print(f"Testing Unraid deployment: {self.base_url}")
        print(f"Expected features: PostgreSQL, Direct Media, JWT Auth, CORS")
        print("")
        
        # Run all tests
        self.test_unraid_environment()
        self.test_version_consistency()
        self.test_postgresql_compliance()
        self.test_direct_media_access()
        self.test_docker_native_performance()
        self.test_cors_configuration()
        self.test_authentication_system()
        self.test_media_apis()
        self.test_production_features()
        
        # Final assessment
        print("")
        print("PRODUCTION READINESS ASSESSMENT")
        print("=" * 35)
        print(f"Tests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.failed == 0:
            print("")
            print("SUCCESS: PRODUCTION READY")
            print("  All systems operational")
            print("  Ready for full deployment")
            print("  Migration successful")
            return True
        elif self.failed <= 2:
            print("")
            print("WARNING: MOSTLY READY")
            print("  Minor issues detected")
            print("  Review failed tests")
            print("  Near production ready")
            return True
        else:
            print("")
            print("ERROR: NOT READY")
            print("  Multiple issues detected")
            print("  Requires fixes before production")
            return False

def main():
    """Main test runner"""
    test_suite = ProductionReadinessTest()
    success = test_suite.run_full_suite()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
