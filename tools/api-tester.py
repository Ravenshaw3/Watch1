#!/usr/bin/env python3
"""Basic API tester for Watch1"""
import requests
import sys

def test_api():
    base_url = 'http://localhost:8000/api/v1'
    
    tests = [
        ('Health Check', f'{base_url}/health', 'GET'),
        ('Media List', f'{base_url}/media', 'GET'),
    ]
    
    passed = 0
    for name, url, method in tests:
        try:
            response = requests.request(method, url, timeout=10)
            if response.status_code < 400:
                print(f"✅ {name}: PASS")
                passed += 1
            else:
                print(f"❌ {name}: FAIL (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: ERROR ({e})")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
