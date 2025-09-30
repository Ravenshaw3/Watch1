#!/usr/bin/env python3
"""Basic health monitor for Watch1 development"""
import sys
import requests
import argparse

def check_health():
    services = {
        'Backend': 'http://localhost:8000/health',
        'Frontend': 'http://localhost:3000'
    }
    
    all_healthy = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: Unhealthy (HTTP {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: Unreachable ({e})")
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--continuous', action='store_true')
    args = parser.parse_args()
    
    if args.continuous:
        import time
        while True:
            check_health()
            time.sleep(30)
    else:
        healthy = check_health()
        sys.exit(0 if healthy else 1)
