#!/usr/bin/env python3
"""
Watch1 Feature Addition Tool
Helps add new features to the test configuration and validation system
"""

import yaml
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class FeatureAdder:
    def __init__(self, config_path: str = "tools/test-config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load current test configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_path}")
            return {}
    
    def save_config(self):
        """Save updated configuration"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
        print(f"✅ Configuration saved to {self.config_path}")
    
    def add_feature_interactive(self):
        """Add a new feature interactively"""
        print("🆕 Adding New Feature to Test Configuration")
        print("=" * 50)
        
        # Get feature name
        feature_name = input("Feature name (e.g., 'user_profiles'): ").strip()
        if not feature_name:
            print("❌ Feature name is required")
            return False
        
        if feature_name in self.config.get("feature_mappings", {}):
            print(f"❌ Feature '{feature_name}' already exists")
            return False
        
        # Get frontend routes
        print(f"\nFrontend routes for {feature_name}:")
        print("Enter routes one by one (press Enter with empty line to finish):")
        frontend_routes = []
        while True:
            route = input("Route (e.g., '/user/profile'): ").strip()
            if not route:
                break
            if not route.startswith('/'):
                route = '/' + route
            frontend_routes.append(route)
        
        # Get backend endpoints
        print(f"\nBackend endpoints for {feature_name}:")
        print("Enter endpoints one by one (press Enter with empty line to finish):")
        print("Format: METHOD /api/v1/path (e.g., 'GET /api/v1/users/profile')")
        backend_endpoints = []
        while True:
            endpoint = input("Endpoint: ").strip()
            if not endpoint:
                break
            # Validate format
            if not any(endpoint.startswith(method) for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']):
                print("⚠️ Endpoint should start with HTTP method (GET, POST, etc.)")
            if '/api/v1/' not in endpoint:
                print("⚠️ Endpoint should include '/api/v1/' path")
            backend_endpoints.append(endpoint)
        
        # Get dependencies
        print(f"\nDependencies for {feature_name}:")
        existing_features = list(self.config.get("feature_mappings", {}).keys())
        if existing_features:
            print(f"Available features: {', '.join(existing_features)}")
        print("Enter dependencies one by one (press Enter with empty line to finish):")
        dependencies = []
        while True:
            dep = input("Dependency: ").strip()
            if not dep:
                break
            if dep not in existing_features:
                print(f"⚠️ Dependency '{dep}' not found in existing features")
            dependencies.append(dep)
        
        # Check if requires admin
        requires_admin = input("Requires admin access? (y/N): ").strip().lower() == 'y'
        
        # Create feature mapping
        feature_mapping = {
            "frontend_routes": frontend_routes,
            "backend_endpoints": backend_endpoints,
            "dependencies": dependencies
        }
        
        if requires_admin:
            feature_mapping["requires_admin"] = True
        
        # Add to configuration
        if "feature_mappings" not in self.config:
            self.config["feature_mappings"] = {}
        
        self.config["feature_mappings"][feature_name] = feature_mapping
        
        # Update development tracking
        if "development_tracking" not in self.config:
            self.config["development_tracking"] = {}
        
        if "in_development" not in self.config["development_tracking"]:
            self.config["development_tracking"]["in_development"] = []
        
        self.config["development_tracking"]["in_development"].append(feature_name)
        
        # Show summary
        print(f"\n✅ Feature '{feature_name}' added successfully!")
        print(f"   Frontend routes: {len(frontend_routes)}")
        print(f"   Backend endpoints: {len(backend_endpoints)}")
        print(f"   Dependencies: {len(dependencies)}")
        print(f"   Requires admin: {requires_admin}")
        
        return True
    
    def add_feature_from_json(self, feature_data: Dict):
        """Add feature from JSON data"""
        feature_name = feature_data.get("name")
        if not feature_name:
            print("❌ Feature name is required in JSON data")
            return False
        
        if feature_name in self.config.get("feature_mappings", {}):
            print(f"❌ Feature '{feature_name}' already exists")
            return False
        
        # Extract feature mapping
        feature_mapping = {
            "frontend_routes": feature_data.get("frontend_routes", []),
            "backend_endpoints": feature_data.get("backend_endpoints", []),
            "dependencies": feature_data.get("dependencies", [])
        }
        
        if feature_data.get("requires_admin", False):
            feature_mapping["requires_admin"] = True
        
        # Add to configuration
        if "feature_mappings" not in self.config:
            self.config["feature_mappings"] = {}
        
        self.config["feature_mappings"][feature_name] = feature_mapping
        
        print(f"✅ Feature '{feature_name}' added from JSON data")
        return True
    
    def list_features(self):
        """List all current features"""
        print("📋 Current Features in Configuration")
        print("=" * 50)
        
        feature_mappings = self.config.get("feature_mappings", {})
        
        if not feature_mappings:
            print("No features configured yet.")
            return
        
        for feature_name, mapping in feature_mappings.items():
            routes = len(mapping.get("frontend_routes", []))
            endpoints = len(mapping.get("backend_endpoints", []))
            deps = len(mapping.get("dependencies", []))
            admin = mapping.get("requires_admin", False)
            
            admin_flag = " 🔒" if admin else ""
            print(f"• {feature_name}{admin_flag}")
            print(f"  Routes: {routes}, Endpoints: {endpoints}, Dependencies: {deps}")
            
            if mapping.get("dependencies"):
                print(f"  Depends on: {', '.join(mapping['dependencies'])}")
            print()
    
    def remove_feature(self, feature_name: str):
        """Remove a feature from configuration"""
        feature_mappings = self.config.get("feature_mappings", {})
        
        if feature_name not in feature_mappings:
            print(f"❌ Feature '{feature_name}' not found")
            return False
        
        # Check if other features depend on this one
        dependents = []
        for name, mapping in feature_mappings.items():
            if feature_name in mapping.get("dependencies", []):
                dependents.append(name)
        
        if dependents:
            print(f"❌ Cannot remove '{feature_name}' - other features depend on it:")
            for dep in dependents:
                print(f"  • {dep}")
            return False
        
        # Remove from feature mappings
        del self.config["feature_mappings"][feature_name]
        
        # Remove from development tracking
        dev_tracking = self.config.get("development_tracking", {})
        for status in ["in_development", "completed_features", "planned_features"]:
            if status in dev_tracking and feature_name in dev_tracking[status]:
                dev_tracking[status].remove(feature_name)
        
        print(f"✅ Feature '{feature_name}' removed successfully")
        return True
    
    def update_feature_status(self, feature_name: str, new_status: str):
        """Update feature development status"""
        valid_statuses = ["in_development", "completed_features", "planned_features", "deprecated_features"]
        
        if new_status not in valid_statuses:
            print(f"❌ Invalid status. Valid options: {', '.join(valid_statuses)}")
            return False
        
        if "development_tracking" not in self.config:
            self.config["development_tracking"] = {}
        
        dev_tracking = self.config["development_tracking"]
        
        # Remove from all status lists
        for status in valid_statuses:
            if status in dev_tracking and feature_name in dev_tracking[status]:
                dev_tracking[status].remove(feature_name)
        
        # Add to new status
        if new_status not in dev_tracking:
            dev_tracking[new_status] = []
        
        dev_tracking[new_status].append(feature_name)
        
        print(f"✅ Feature '{feature_name}' status updated to '{new_status}'")
        return True

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python add-feature.py add                    # Add feature interactively")
        print("  python add-feature.py list                   # List all features")
        print("  python add-feature.py remove <feature_name>  # Remove a feature")
        print("  python add-feature.py status <feature_name> <status>  # Update feature status")
        return 1
    
    adder = FeatureAdder()
    command = sys.argv[1]
    
    if command == "add":
        if adder.add_feature_interactive():
            adder.save_config()
            print("\n🎉 Feature added successfully!")
            print("Run 'python tools/feature-mapper.py' to validate the new feature.")
        
    elif command == "list":
        adder.list_features()
        
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Feature name required for remove command")
            return 1
        
        feature_name = sys.argv[2]
        if adder.remove_feature(feature_name):
            adder.save_config()
            
    elif command == "status":
        if len(sys.argv) < 4:
            print("❌ Feature name and status required")
            return 1
        
        feature_name = sys.argv[2]
        new_status = sys.argv[3]
        if adder.update_feature_status(feature_name, new_status):
            adder.save_config()
            
    else:
        print(f"❌ Unknown command: {command}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
