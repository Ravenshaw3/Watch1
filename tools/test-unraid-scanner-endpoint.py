#!/usr/bin/env python3
"""
Test Unraid Scanner Endpoint
"""

import requests
import json

def test_unraid_scanner():
    print("TESTING UNRAID SCANNER ENDPOINT")
    print("=" * 40)
    
    # Authenticate
    auth_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                json={'username': 'test@example.com', 'password': 'testpass123'})
    
    if auth_response.status_code != 200:
        print(f"Auth failed: {auth_response.status_code}")
        return False
        
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test the new Unraid scanner endpoint
    print('Testing Unraid scanner endpoint...')
    scan_response = requests.post('http://localhost:8000/api/v1/media/scan-unraid', 
                                headers=headers, 
                                json={'scan_method': 'direct_t_drive'},
                                timeout=60)
    
    print(f'Status: {scan_response.status_code}')
    
    if scan_response.status_code == 200:
        result = scan_response.json()
        print(f'SUCCESS: Unraid scanner working!')
        print(f'Total files: {result.get("total_files_found", 0)}')
        print(f'Categories: {len(result.get("scan_results", {}))}')
        print(f'Message: {result.get("message", "No message")}')
        
        # Show scan results
        scan_results = result.get("scan_results", {})
        if scan_results:
            print("\nScan Results by Category:")
            for category, count in scan_results.items():
                print(f"  - {category}: {count} files")
        
        return True
    else:
        print(f'ERROR: {scan_response.status_code}')
        print(f'Response: {scan_response.text[:500]}')
        return False

if __name__ == "__main__":
    test_unraid_scanner()
