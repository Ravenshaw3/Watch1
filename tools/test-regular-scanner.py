#!/usr/bin/env python3
"""
Test Regular Scanner - Check what directories are being scanned
"""

import requests

def test_regular_scanner():
    print("TESTING REGULAR MEDIA SCANNER")
    print("=" * 40)
    
    # Get auth token
    auth_response = requests.post('http://localhost:8000/api/v1/auth/login/access-token', 
                                json={'username': 'test@example.com', 'password': 'testpass123'})
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Test regular scan
    print('Testing regular media scan...')
    scan_response = requests.post('http://localhost:8000/api/v1/media/scan', headers=headers, json={})
    print(f'Status: {scan_response.status_code}')
    
    if scan_response.status_code == 200:
        result = scan_response.json()
        print(f'SUCCESS: Regular scanner working')
        print(f'Total files: {result.get("total_files_found", 0)}')
        print(f'Directories scanned: {result.get("directories_scanned", 0)}')
        
        scan_results = result.get("scan_results", {})
        if scan_results:
            print("\nScan Results:")
            for category, details in scan_results.items():
                files_found = details.get("files_found", 0)
                path = details.get("path", "Unknown")
                print(f"  - {category}: {files_found} files in {path}")
        else:
            print("No scan results returned")
    else:
        print(f'ERROR: {scan_response.status_code}')
        print(f'Response: {scan_response.text[:500]}')

if __name__ == "__main__":
    test_regular_scanner()
