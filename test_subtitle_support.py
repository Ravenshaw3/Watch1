#!/usr/bin/env python3
"""
Test script for Watch1 v3.0.1 Subtitle Support
Tests the new subtitle functionality and advanced player features
"""

import requests
import json
import os
import time
from typing import Dict, List, Any

class SubtitleTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.session = requests.Session()
        self.access_token = None

    def log(self, message: str, status: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")

    def authenticate(self) -> bool:
        """Authenticate with the API"""
        try:
            login_data = {
                "username": "test@example.com",
                "password": "testpass123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login/access-token",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                self.log("Authentication successful", "SUCCESS")
                return True
            else:
                self.log(f"Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Authentication error: {str(e)}", "ERROR")
            return False

    def test_subtitle_endpoints(self) -> bool:
        """Test subtitle API endpoints"""
        try:
            self.log("Testing subtitle endpoints...")
            
            # Get media files first
            response = self.session.get(f"{self.base_url}/media")
            if response.status_code != 200:
                self.log(f"Failed to get media files: {response.status_code}", "ERROR")
                return False
            
            media_data = response.json()
            media_files = media_data.get("media", [])
            
            if not media_files:
                self.log("No media files found for subtitle testing", "WARNING")
                return True
            
            # Test with first media file
            test_media = media_files[0]
            media_id = test_media["id"]
            media_title = test_media.get("original_filename", "Unknown")
            
            self.log(f"Testing subtitles for: {media_title} (ID: {media_id})")
            
            # Test get subtitles endpoint
            subtitle_response = self.session.get(f"{self.base_url}/media/{media_id}/subtitles")
            
            if subtitle_response.status_code == 200:
                subtitles = subtitle_response.json()
                self.log(f"Found {len(subtitles)} subtitle files", "SUCCESS")
                
                for subtitle in subtitles:
                    self.log(f"  - {subtitle['filename']} ({subtitle['language']}, {subtitle['format']})")
                
                # Test subtitle file access if subtitles exist
                if subtitles:
                    test_subtitle = subtitles[0]
                    subtitle_filename = test_subtitle["filename"]
                    
                    file_response = self.session.get(
                        f"{self.base_url}/media/{media_id}/subtitles/{subtitle_filename}"
                    )
                    
                    if file_response.status_code == 200:
                        self.log(f"Successfully accessed subtitle file: {subtitle_filename}", "SUCCESS")
                        
                        # Check content type
                        content_type = file_response.headers.get("content-type", "")
                        self.log(f"Subtitle content type: {content_type}")
                        
                        # Check file size
                        content_length = len(file_response.content)
                        self.log(f"Subtitle file size: {content_length} bytes")
                        
                    else:
                        self.log(f"Failed to access subtitle file: {file_response.status_code}", "ERROR")
                        return False
                
                return True
                
            elif subtitle_response.status_code == 404:
                self.log("No subtitles found for this media file", "INFO")
                return True
            else:
                self.log(f"Subtitle endpoint failed: {subtitle_response.status_code} - {subtitle_response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Subtitle endpoint test error: {str(e)}", "ERROR")
            return False

    def test_media_with_subtitles(self) -> bool:
        """Find and test media files that have subtitle files"""
        try:
            self.log("Searching for media files with subtitle support...")
            
            response = self.session.get(f"{self.base_url}/media")
            if response.status_code != 200:
                return False
            
            media_data = response.json()
            media_files = media_data.get("media", [])
            
            media_with_subtitles = []
            
            for media in media_files[:5]:  # Test first 5 media files
                media_id = media["id"]
                subtitle_response = self.session.get(f"{self.base_url}/media/{media_id}/subtitles")
                
                if subtitle_response.status_code == 200:
                    subtitles = subtitle_response.json()
                    if subtitles:
                        media_with_subtitles.append({
                            "media": media,
                            "subtitles": subtitles
                        })
            
            self.log(f"Found {len(media_with_subtitles)} media files with subtitles")
            
            for item in media_with_subtitles:
                media = item["media"]
                subtitles = item["subtitles"]
                self.log(f"  📹 {media.get('original_filename', 'Unknown')}")
                for sub in subtitles:
                    self.log(f"    📝 {sub['filename']} ({sub['language']})")
            
            return True
            
        except Exception as e:
            self.log(f"Media with subtitles test error: {str(e)}", "ERROR")
            return False

    def test_frontend_integration(self) -> bool:
        """Test frontend integration points"""
        try:
            self.log("Testing frontend integration...")
            
            # Test if frontend is accessible
            frontend_response = requests.get("http://localhost:3000", timeout=5)
            if frontend_response.status_code == 200:
                self.log("Frontend is accessible", "SUCCESS")
            else:
                self.log(f"Frontend not accessible: {frontend_response.status_code}", "WARNING")
            
            # Test CORS headers on subtitle endpoints
            response = self.session.get(f"{self.base_url}/media")
            if response.status_code == 200:
                media_data = response.json()
                media_files = media_data.get("media", [])
                
                if media_files:
                    test_media_id = media_files[0]["id"]
                    
                    # Test OPTIONS request (CORS preflight)
                    options_response = self.session.options(
                        f"{self.base_url}/media/{test_media_id}/subtitles"
                    )
                    
                    cors_headers = {
                        "Access-Control-Allow-Origin": options_response.headers.get("Access-Control-Allow-Origin"),
                        "Access-Control-Allow-Methods": options_response.headers.get("Access-Control-Allow-Methods"),
                        "Access-Control-Allow-Headers": options_response.headers.get("Access-Control-Allow-Headers")
                    }
                    
                    self.log("CORS headers check:")
                    for header, value in cors_headers.items():
                        if value:
                            self.log(f"  ✅ {header}: {value}")
                        else:
                            self.log(f"  ❌ {header}: Not set")
            
            return True
            
        except Exception as e:
            self.log(f"Frontend integration test error: {str(e)}", "ERROR")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all subtitle tests"""
        self.log("=" * 60)
        self.log("WATCH1 v3.0.1 - SUBTITLE SUPPORT TESTING")
        self.log("=" * 60)
        
        results = {}
        
        # Authentication
        if not self.authenticate():
            self.log("Authentication failed - cannot continue tests", "ERROR")
            return {"authentication": False}
        
        results["authentication"] = True
        
        # Test subtitle endpoints
        results["subtitle_endpoints"] = self.test_subtitle_endpoints()
        
        # Test media with subtitles
        results["media_with_subtitles"] = self.test_media_with_subtitles()
        
        # Test frontend integration
        results["frontend_integration"] = self.test_frontend_integration()
        
        # Summary
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All subtitle tests PASSED! Advanced player features ready.", "SUCCESS")
        else:
            self.log(f"⚠️  {total - passed} test(s) failed. Check implementation.", "WARNING")
        
        return results

if __name__ == "__main__":
    tester = SubtitleTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)
