#!/usr/bin/env python3
"""
Watch1 Test Suite Runner
Runs all available test suites for the Unraid environment
"""

import subprocess
import sys
import os
import time

class TestRunner:
    def __init__(self):
        self.test_files = [
            ("test_unraid_system.py", "Unraid System Test"),
            ("test_environment_comparison.py", "Environment Comparison"), 
            ("test_production_readiness.py", "Production Readiness"),
            ("tools/comprehensive-test-suite-unraid.py", "Comprehensive Test Suite")
        ]
        
    def run_test_file(self, filename, description):
        """Run a single test file"""
        print(f"\n{'='*60}")
        print(f"RUNNING: {description}")
        print(f"FILE: {filename}")
        print('='*60)
        
        if not os.path.exists(filename):
            print(f"❌ Test file not found: {filename}")
            return False
        
        try:
            # Run the test file
            result = subprocess.run([sys.executable, filename], 
                                  capture_output=True, text=True, timeout=60)
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Check result
            success = result.returncode == 0
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\nResult: {status} (exit code: {result.returncode})")
            
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Test timed out after 60 seconds")
            return False
        except Exception as e:
            print(f"❌ Error running test: {e}")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print("WATCH1 COMPREHENSIVE TEST SUITE")
        print("="*60)
        print("Running all test suites for Unraid environment")
        print(f"Total test suites: {len(self.test_files)}")
        
        results = {}
        start_time = time.time()
        
        for filename, description in self.test_files:
            success = self.run_test_file(filename, description)
            results[description] = success
        
        # Summary
        total_time = time.time() - start_time
        passed = sum(1 for success in results.values() if success)
        failed = len(results) - passed
        
        print(f"\n{'='*60}")
        print("COMPREHENSIVE TEST SUMMARY")
        print('='*60)
        
        for description, success in results.items():
            status = "PASS" if success else "FAIL"
            print(f"[{status}] {description}")
        
        print(f"\nOverall Results:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Total:  {len(results)}")
        print(f"  Time:   {total_time:.1f}s")
        
        if failed == 0:
            print(f"\nSUCCESS: ALL TESTS PASSED!")
            print("OK: Watch1 Unraid system is fully operational")
            print("OK: Ready for production deployment")
            print("OK: Migration from Docker Desktop successful")
            return True
        else:
            print(f"\nWARNING: {failed} TEST SUITE(S) FAILED")
            print("FAIL: Review failed tests above")
            print("FAIL: Fix issues before production deployment")
            return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        runner = TestRunner()
        
        for filename, description in runner.test_files:
            if test_name.lower() in filename.lower() or test_name.lower() in description.lower():
                success = runner.run_test_file(filename, description)
                sys.exit(0 if success else 1)
        
        print(f"Test not found: {test_name}")
        print("Available tests:")
        for filename, description in runner.test_files:
            print(f"  - {filename} ({description})")
        sys.exit(1)
    else:
        # Run all tests
        runner = TestRunner()
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
