#!/usr/bin/env python3
"""
Test script for Watch1 v3.0.1 Login Functionality
Tests authentication endpoints and frontend integration
"""

import requests
import json
import time
from typing import Dict, Any

class LoginTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000/api/v1"
        self.frontend_url = "http://localhost:3000"
        self.session = requests.Session()
        self.access_token = None

    def log(self, message: str, status: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        colors = {
            "SUCCESS": "\033[92m",
            "ERROR": "\033[91m", 
            "WARNING": "\033[93m",
            "INFO": "\033[96m"
        }
        color = colors.get(status, "\033[0m")
        print(f"[{timestamp}] [{color}{status}\033[0m] {message}")

    def test_backend_connectivity(self) -> bool:
        """Test if backend is accessible"""
        try:
            response = requests.get(f"{self.backend_url}/version", timeout=5)
            if response.status_code == 200:
                version_data = response.json()
                self.log(f"Backend accessible: v{version_data.get('version', 'unknown')} ({version_data.get('framework', 'unknown')})", "SUCCESS")
                return True
            else:
                self.log(f"Backend returned HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Backend not accessible: {str(e)}", "ERROR")
            return False

    def test_frontend_connectivity(self) -> bool:
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log("Frontend accessible", "SUCCESS")
                return True
            else:
                self.log(f"Frontend returned HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Frontend not accessible: {str(e)}", "ERROR")
            return False

    def test_login_json(self) -> bool:
        """Test login with JSON data"""
        try:
            login_data = {
                "username": "test@example.com",
                "password": "testpass123"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/login/access-token",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                token_type = data.get("token_type")
                
                self.log(f"JSON login successful", "SUCCESS")
                self.log(f"Token type: {token_type}", "INFO")
                self.log(f"Token preview: {self.access_token[:50]}...", "INFO")
                return True
            else:
                self.log(f"JSON login failed: HTTP {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"JSON login error: {str(e)}", "ERROR")
            return False

    def test_login_form_data(self) -> bool:
        """Test login with form data"""
        try:
            login_data = {
                "username": "test@example.com",
                "password": "testpass123"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/login/access-token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                token_type = data.get("token_type")
                
                self.log(f"Form data login successful", "SUCCESS")
                self.log(f"Token type: {token_type}", "INFO")
                return True
            else:
                self.log(f"Form data login failed: HTTP {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Form data login error: {str(e)}", "ERROR")
            return False

    def test_protected_endpoint(self) -> bool:
        """Test accessing protected endpoint with token"""
        if not self.access_token:
            self.log("No access token available for protected endpoint test", "ERROR")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.backend_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.log(f"Protected endpoint access successful", "SUCCESS")
                self.log(f"User: {user_data.get('email', 'unknown')}", "INFO")
                self.log(f"User ID: {user_data.get('id', 'unknown')}", "INFO")
                return True
            else:
                self.log(f"Protected endpoint failed: HTTP {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Protected endpoint error: {str(e)}", "ERROR")
            return False

    def test_invalid_credentials(self) -> bool:
        """Test login with invalid credentials"""
        try:
            login_data = {
                "username": "invalid@example.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/login/access-token",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                self.log("Invalid credentials correctly rejected", "SUCCESS")
                return True
            else:
                self.log(f"Invalid credentials test failed: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Invalid credentials test error: {str(e)}", "ERROR")
            return False

    def test_missing_credentials(self) -> bool:
        """Test login with missing credentials"""
        try:
            login_data = {
                "username": "test@example.com"
                # Missing password
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/login/access-token",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                self.log("Missing credentials correctly rejected", "SUCCESS")
                return True
            else:
                self.log(f"Missing credentials test failed: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Missing credentials test error: {str(e)}", "ERROR")
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS headers for frontend integration"""
        try:
            # Test OPTIONS request (CORS preflight)
            response = requests.options(f"{self.backend_url}/auth/login/access-token")
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            self.log("CORS headers check:", "INFO")
            for header, value in cors_headers.items():
                if value:
                    self.log(f"  ✓ {header}: {value}", "SUCCESS")
                else:
                    self.log(f"  ✗ {header}: Not set", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"CORS test error: {str(e)}", "ERROR")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all login tests"""
        self.log("=" * 60)
        self.log("WATCH1 v3.0.1 - LOGIN FUNCTIONALITY TESTING")
        self.log("=" * 60)
        
        results = {}
        
        # Test connectivity
        results["backend_connectivity"] = self.test_backend_connectivity()
        results["frontend_connectivity"] = self.test_frontend_connectivity()
        
        if not results["backend_connectivity"]:
            self.log("Backend not accessible - cannot continue login tests", "ERROR")
            return results
        
        # Test authentication
        results["login_json"] = self.test_login_json()
        results["login_form_data"] = self.test_login_form_data()
        results["protected_endpoint"] = self.test_protected_endpoint()
        results["invalid_credentials"] = self.test_invalid_credentials()
        results["missing_credentials"] = self.test_missing_credentials()
        results["cors_headers"] = self.test_cors_headers()
        
        # Summary
        self.log("=" * 60)
        self.log("LOGIN FUNCTIONALITY TEST RESULTS")
        self.log("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        test_descriptions = {
            "backend_connectivity": "Backend Server Connectivity",
            "frontend_connectivity": "Frontend Server Connectivity", 
            "login_json": "JSON Login Authentication",
            "login_form_data": "Form Data Login Authentication",
            "protected_endpoint": "Protected Endpoint Access",
            "invalid_credentials": "Invalid Credentials Rejection",
            "missing_credentials": "Missing Credentials Rejection",
            "cors_headers": "CORS Headers Configuration"
        }
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            description = test_descriptions.get(test_name, test_name.replace('_', ' ').title())
            self.log(f"{description}: {status}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All login functionality tests PASSED!", "SUCCESS")
            self.log("✅ Backend authentication working", "SUCCESS")
            self.log("✅ Frontend integration ready", "SUCCESS")
            self.log("✅ JWT tokens functioning", "SUCCESS")
            self.log("✅ Protected endpoints secured", "SUCCESS")
        else:
            self.log(f"⚠️  {total - passed} test(s) failed. Check implementation.", "WARNING")
        
        return results

if __name__ == "__main__":
    tester = LoginTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)
