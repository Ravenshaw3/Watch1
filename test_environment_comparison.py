#!/usr/bin/env python3
"""
Watch1 Environment Comparison Test
Compares Docker Desktop vs Unraid environments to validate migration success
"""

import requests
import json
import time
import sys

class EnvironmentComparison:
    def __init__(self):
        self.docker_desktop_url = "http://localhost:8000"
        self.unraid_url = "http://192.168.254.14:8000"
        self.test_credentials = {
            "email": "test@example.com", 
            "password": "testpass123"
        }
        
    def test_endpoint(self, base_url, endpoint, description, auth_token=None):
        """Test a specific endpoint"""
        try:
            headers = {}
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
                
            response = requests.get(f"{base_url}{endpoint}", 
                                  headers=headers, timeout=10)
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None,
                'error': None
            }
        except Exception as e:
            return {
                'status_code': None,
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def get_auth_token(self, base_url):
        """Get authentication token"""
        try:
            response = requests.post(f"{base_url}/api/v1/auth/login", 
                                   json=self.test_credentials, timeout=10)
            if response.status_code == 200:
                return response.json().get('access_token')
        except:
            pass
        return None
    
    def compare_environments(self):
        """Compare Docker Desktop vs Unraid environments"""
        print("WATCH1 ENVIRONMENT COMPARISON")
        print("=" * 50)
        print("Comparing Docker Desktop vs Unraid environments")
        print("")
        
        # Test endpoints to compare
        endpoints = [
            ("/", "System Info"),
            ("/api/v1/health", "Health Check"),
            ("/api/v1/media/", "Media API"),
            ("/api/v1/media/categories", "Categories API")
        ]
        
        # Get auth tokens
        print("Getting authentication tokens...")
        docker_token = self.get_auth_token(self.docker_desktop_url)
        unraid_token = self.get_auth_token(self.unraid_url)
        
        print(f"Docker Desktop token: {'OK' if docker_token else 'FAIL'}")
        print(f"Unraid token: {'OK' if unraid_token else 'FAIL'}")
        print("")
        
        # Compare each endpoint
        results = {}
        
        for endpoint, description in endpoints:
            print(f"Testing: {description} ({endpoint})")
            print("-" * 40)
            
            # Test Docker Desktop
            docker_result = self.test_endpoint(
                self.docker_desktop_url, endpoint, description, docker_token
            )
            
            # Test Unraid
            unraid_result = self.test_endpoint(
                self.unraid_url, endpoint, description, unraid_token
            )
            
            # Compare results
            docker_status = "OK ONLINE" if docker_result['success'] else "FAIL OFFLINE"
            unraid_status = "OK ONLINE" if unraid_result['success'] else "FAIL OFFLINE"
            
            print(f"Docker Desktop: {docker_status}")
            print(f"Unraid:         {unraid_status}")
            
            # Compare data if both are online
            if docker_result['success'] and unraid_result['success']:
                docker_data = docker_result['data']
                unraid_data = unraid_result['data']
                
                if endpoint == "/":
                    docker_media = docker_data.get('media_files_found', 0)
                    unraid_media = unraid_data.get('media_files_found', 0)
                    print(f"Media Files - Docker: {docker_media}, Unraid: {unraid_media}")
                    
                elif endpoint == "/api/v1/media/":
                    docker_total = docker_data.get('total', 0)
                    unraid_total = unraid_data.get('total', 0)
                    print(f"API Response - Docker: {docker_total}, Unraid: {unraid_total}")
                    
                elif endpoint == "/api/v1/media/categories":
                    docker_cats = len(docker_data) if isinstance(docker_data, dict) else 0
                    unraid_cats = len(unraid_data) if isinstance(unraid_data, dict) else 0
                    print(f"Categories - Docker: {docker_cats}, Unraid: {unraid_cats}")
            
            results[endpoint] = {
                'docker': docker_result,
                'unraid': unraid_result
            }
            
            print("")
        
        # Migration assessment
        print("MIGRATION ASSESSMENT")
        print("=" * 30)
        
        unraid_working = all(results[ep]['unraid']['success'] for ep in results)
        docker_working = all(results[ep]['docker']['success'] for ep in results)
        
        if unraid_working and not docker_working:
            print("SUCCESS: SUCCESSFUL MIGRATION")
            print("  - Unraid environment fully operational")
            print("  - Docker Desktop environment deprecated")
            print("  - Migration completed successfully")
            
        elif unraid_working and docker_working:
            print("SUCCESS: DUAL ENVIRONMENT")
            print("  - Both environments operational")
            print("  - Unraid ready for production")
            print("  - Docker Desktop available as backup")
            
        elif not unraid_working and docker_working:
            print("WARNING: MIGRATION INCOMPLETE")
            print("  - Docker Desktop still primary")
            print("  - Unraid environment needs fixes")
            print("  - Migration not yet complete")
            
        else:
            print("ERROR: BOTH ENVIRONMENTS DOWN")
            print("  - Critical system issues")
            print("  - Immediate attention required")
        
        return unraid_working

def main():
    """Main comparison runner"""
    comparison = EnvironmentComparison()
    success = comparison.compare_environments()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
