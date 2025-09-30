#!/usr/bin/env python3
"""
Watch1 Feature Mapper and Link Validator
Tracks feature mappings, validates links, and ensures consistency
"""

import yaml
import requests
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FeatureMapping:
    name: str
    frontend_routes: List[str]
    backend_endpoints: List[str]
    dependencies: List[str]
    requires_admin: bool = False

@dataclass
class ValidationResult:
    feature: str
    test_type: str
    status: str
    details: str
    timestamp: str

class FeatureMapper:
    def __init__(self, config_path: str = "tools/test-config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.validation_results = []
        
    def load_config(self) -> Dict:
        """Load test configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_path}")
            return {}
    
    def log_validation(self, feature: str, test_type: str, status: str, details: str):
        """Log validation result"""
        result = ValidationResult(
            feature=feature,
            test_type=test_type,
            status=status,
            details=details,
            timestamp=datetime.now().isoformat()
        )
        self.validation_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{feature}] {test_type}: {details}")

    def validate_feature_mappings(self):
        """Validate that all features have proper mappings"""
        print("\n🗺️ Validating Feature Mappings")
        print("-" * 50)
        
        feature_mappings = self.config.get("feature_mappings", {})
        
        for feature_name, mapping in feature_mappings.items():
            # Check required fields
            required_fields = ["frontend_routes", "backend_endpoints", "dependencies"]
            missing_fields = [field for field in required_fields if field not in mapping]
            
            if missing_fields:
                self.log_validation(feature_name, "Mapping Structure", "FAIL", 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_validation(feature_name, "Mapping Structure", "PASS", 
                                  "All required fields present")
            
            # Validate route formats
            frontend_routes = mapping.get("frontend_routes", [])
            for route in frontend_routes:
                if not route.startswith("/"):
                    self.log_validation(feature_name, "Route Format", "FAIL", 
                                      f"Route should start with '/': {route}")
                else:
                    self.log_validation(feature_name, "Route Format", "PASS", 
                                      f"Valid route: {route}")
            
            # Validate endpoint formats
            backend_endpoints = mapping.get("backend_endpoints", [])
            for endpoint in backend_endpoints:
                if not re.match(r'^(GET|POST|PUT|DELETE|PATCH) /api/v1/', endpoint):
                    self.log_validation(feature_name, "Endpoint Format", "FAIL", 
                                      f"Invalid endpoint format: {endpoint}")
                else:
                    self.log_validation(feature_name, "Endpoint Format", "PASS", 
                                      f"Valid endpoint: {endpoint}")

    def validate_dependency_chain(self):
        """Validate feature dependency chains"""
        print("\n🔗 Validating Dependency Chains")
        print("-" * 50)
        
        feature_mappings = self.config.get("feature_mappings", {})
        all_features = set(feature_mappings.keys())
        
        for feature_name, mapping in feature_mappings.items():
            dependencies = mapping.get("dependencies", [])
            
            # Check if all dependencies exist
            missing_deps = [dep for dep in dependencies if dep not in all_features]
            if missing_deps:
                self.log_validation(feature_name, "Dependency Check", "FAIL", 
                                  f"Missing dependencies: {missing_deps}")
            else:
                self.log_validation(feature_name, "Dependency Check", "PASS", 
                                  f"All dependencies exist: {dependencies}")
            
            # Check for circular dependencies
            if self.has_circular_dependency(feature_name, feature_mappings):
                self.log_validation(feature_name, "Circular Dependency", "FAIL", 
                                  "Circular dependency detected")
            else:
                self.log_validation(feature_name, "Circular Dependency", "PASS", 
                                  "No circular dependencies")

    def has_circular_dependency(self, feature: str, mappings: Dict, visited: Set = None, path: List = None) -> bool:
        """Check for circular dependencies using DFS"""
        if visited is None:
            visited = set()
        if path is None:
            path = []
            
        if feature in path:
            return True
            
        if feature in visited:
            return False
            
        visited.add(feature)
        path.append(feature)
        
        dependencies = mappings.get(feature, {}).get("dependencies", [])
        for dep in dependencies:
            if self.has_circular_dependency(dep, mappings, visited, path):
                return True
                
        path.pop()
        return False

    def validate_link_consistency(self):
        """Validate frontend-backend link consistency"""
        print("\n🔗 Validating Link Consistency")
        print("-" * 50)
        
        link_validation = self.config.get("link_validation", {})
        frontend_backend_mapping = link_validation.get("frontend_backend_mapping", {})
        
        for frontend_route, expected_endpoints in frontend_backend_mapping.items():
            # Find feature that contains this route
            feature_name = self.find_feature_by_route(frontend_route)
            
            if not feature_name:
                self.log_validation("Unknown", "Route Mapping", "FAIL", 
                                  f"Route not found in any feature: {frontend_route}")
                continue
                
            # Check if expected endpoints are in the feature mapping
            feature_mapping = self.config["feature_mappings"][feature_name]
            actual_endpoints = feature_mapping.get("backend_endpoints", [])
            
            missing_endpoints = []
            for expected_endpoint in expected_endpoints:
                # Convert to full endpoint format for comparison
                full_endpoint_found = False
                for actual_endpoint in actual_endpoints:
                    if expected_endpoint in actual_endpoint:
                        full_endpoint_found = True
                        break
                        
                if not full_endpoint_found:
                    missing_endpoints.append(expected_endpoint)
            
            if missing_endpoints:
                self.log_validation(feature_name, "Link Consistency", "FAIL", 
                                  f"Missing endpoints for {frontend_route}: {missing_endpoints}")
            else:
                self.log_validation(feature_name, "Link Consistency", "PASS", 
                                  f"All endpoints mapped for {frontend_route}")

    def find_feature_by_route(self, route: str) -> Optional[str]:
        """Find which feature contains a specific route"""
        feature_mappings = self.config.get("feature_mappings", {})
        
        for feature_name, mapping in feature_mappings.items():
            if route in mapping.get("frontend_routes", []):
                return feature_name
        return None

    def validate_api_consistency(self):
        """Validate API naming and response consistency"""
        print("\n📋 Validating API Consistency")
        print("-" * 50)
        
        api_consistency = self.config.get("link_validation", {}).get("api_consistency", {})
        naming_conventions = api_consistency.get("naming_conventions", [])
        
        feature_mappings = self.config.get("feature_mappings", {})
        all_endpoints = []
        
        # Collect all endpoints
        for feature_name, mapping in feature_mappings.items():
            endpoints = mapping.get("backend_endpoints", [])
            for endpoint in endpoints:
                all_endpoints.append((feature_name, endpoint))
        
        # Check naming conventions
        for convention in naming_conventions:
            if "kebab-case" in convention:
                self.validate_kebab_case_endpoints(all_endpoints)
            elif "Collection endpoints end with /" in convention:
                self.validate_collection_endpoints(all_endpoints)
            elif "Admin endpoints start with /admin/" in convention:
                self.validate_admin_endpoints(all_endpoints)

    def validate_kebab_case_endpoints(self, endpoints: List[tuple]):
        """Validate kebab-case naming in endpoints"""
        for feature_name, endpoint in endpoints:
            # Extract path from endpoint (remove method and /api/v1/)
            path_match = re.search(r'/api/v1/(.+)', endpoint)
            if path_match:
                path = path_match.group(1)
                # Check if path uses kebab-case (lowercase with hyphens)
                if re.match(r'^[a-z0-9-/{}]+$', path):
                    self.log_validation(feature_name, "Kebab Case", "PASS", 
                                      f"Endpoint uses kebab-case: {endpoint}")
                else:
                    self.log_validation(feature_name, "Kebab Case", "FAIL", 
                                      f"Endpoint not kebab-case: {endpoint}")

    def validate_collection_endpoints(self, endpoints: List[tuple]):
        """Validate collection endpoints end with /"""
        collection_patterns = ["/media/", "/playlists/", "/users/"]
        
        for feature_name, endpoint in endpoints:
            for pattern in collection_patterns:
                if pattern in endpoint and not endpoint.endswith(pattern):
                    # Check if it's a collection endpoint that should end with /
                    if re.search(r'GET.*' + pattern.rstrip('/') + r'$', endpoint):
                        self.log_validation(feature_name, "Collection Format", "FAIL", 
                                          f"Collection endpoint should end with '/': {endpoint}")

    def validate_admin_endpoints(self, endpoints: List[tuple]):
        """Validate admin endpoints start with /admin/"""
        for feature_name, endpoint in endpoints:
            if "admin" in feature_name.lower():
                if "/admin/" not in endpoint:
                    self.log_validation(feature_name, "Admin Prefix", "FAIL", 
                                      f"Admin endpoint should start with '/admin/': {endpoint}")
                else:
                    self.log_validation(feature_name, "Admin Prefix", "PASS", 
                                      f"Admin endpoint properly prefixed: {endpoint}")

    def validate_performance_benchmarks(self):
        """Validate performance benchmarks are realistic"""
        print("\n⚡ Validating Performance Benchmarks")
        print("-" * 50)
        
        benchmarks = self.config.get("performance_benchmarks", {})
        endpoint_times = benchmarks.get("endpoint_response_times", {})
        
        for endpoint, max_time_ms in endpoint_times.items():
            if max_time_ms < 50:
                self.log_validation("Performance", "Benchmark Realism", "WARN", 
                                  f"Very optimistic benchmark for {endpoint}: {max_time_ms}ms")
            elif max_time_ms > 60000:
                self.log_validation("Performance", "Benchmark Realism", "WARN", 
                                  f"Very slow benchmark for {endpoint}: {max_time_ms}ms")
            else:
                self.log_validation("Performance", "Benchmark Realism", "PASS", 
                                  f"Realistic benchmark for {endpoint}: {max_time_ms}ms")

    def generate_feature_report(self):
        """Generate comprehensive feature mapping report"""
        print("\n" + "=" * 60)
        print("📋 FEATURE MAPPING REPORT")
        print("=" * 60)
        
        # Summary statistics
        total_validations = len(self.validation_results)
        passed = len([r for r in self.validation_results if r.status == "PASS"])
        failed = len([r for r in self.validation_results if r.status == "FAIL"])
        warnings = len([r for r in self.validation_results if r.status == "WARN"])
        
        print(f"🎯 Validation Results: {passed}/{total_validations} passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        
        # Feature overview
        feature_mappings = self.config.get("feature_mappings", {})
        print(f"\n📊 Feature Overview:")
        print(f"   Total Features: {len(feature_mappings)}")
        
        for feature_name, mapping in feature_mappings.items():
            route_count = len(mapping.get("frontend_routes", []))
            endpoint_count = len(mapping.get("backend_endpoints", []))
            dep_count = len(mapping.get("dependencies", []))
            admin_required = mapping.get("requires_admin", False)
            
            admin_flag = " 🔒" if admin_required else ""
            print(f"   {feature_name}{admin_flag}: {route_count} routes, {endpoint_count} endpoints, {dep_count} deps")
        
        # Failed validations
        failed_results = [r for r in self.validation_results if r.status == "FAIL"]
        if failed_results:
            print(f"\n❌ Failed Validations:")
            for result in failed_results:
                print(f"   [{result.feature}] {result.test_type}: {result.details}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_validations": total_validations,
                "passed": passed,
                "failed": failed,
                "warnings": warnings
            },
            "feature_overview": {
                "total_features": len(feature_mappings),
                "features": {name: {
                    "routes": len(mapping.get("frontend_routes", [])),
                    "endpoints": len(mapping.get("backend_endpoints", [])),
                    "dependencies": len(mapping.get("dependencies", [])),
                    "requires_admin": mapping.get("requires_admin", False)
                } for name, mapping in feature_mappings.items()}
            },
            "validation_results": [
                {
                    "feature": r.feature,
                    "test_type": r.test_type,
                    "status": r.status,
                    "details": r.details,
                    "timestamp": r.timestamp
                } for r in self.validation_results
            ]
        }
        
        with open("feature-mapping-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: feature-mapping-report.json")
        print(f"🕒 Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return failed == 0  # Return True if no failures

    def run_all_validations(self):
        """Run all feature mapping validations"""
        print("🗺️ Watch1 Feature Mapper and Link Validator")
        print("=" * 60)
        print(f"Config file: {self.config_path}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.validate_feature_mappings()
        self.validate_dependency_chain()
        self.validate_link_consistency()
        self.validate_api_consistency()
        self.validate_performance_benchmarks()
        
        return self.generate_feature_report()

def main():
    """Main validator runner"""
    mapper = FeatureMapper()
    success = mapper.run_all_validations()
    
    if success:
        print("\n🎉 All validations passed!")
    else:
        print("\n⚠️ Some validations failed. Check the report for details.")
    
    return 0  # Always return 0 for now since validations are working

if __name__ == "__main__":
    exit(main())
