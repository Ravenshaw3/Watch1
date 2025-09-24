#!/usr/bin/env python3
"""
Watch1 v3.0.1 - Development Environment Health Monitor
Comprehensive health monitoring and diagnostics tool
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import sqlite3
import redis
import psycopg2

class HealthMonitor:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.frontend_url = "http://localhost:3000"
        self.nginx_url = "http://localhost"
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'watch1_dev',
            'user': 'watch1_user',
            'password': 'watch1_dev_password'
        }
        self.redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "SUCCESS": "\033[92m",
            "ERROR": "\033[91m",
            "WARNING": "\033[93m",
            "INFO": "\033[94m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] [{level}] {message}{colors['RESET']}")
    
    def test_docker_containers(self) -> Dict[str, Any]:
        """Test Docker container health"""
        self.log("Testing Docker containers...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.dev.yml", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))
            
            container_status = {}
            for container in containers:
                service = container.get('Service', 'unknown')
                state = container.get('State', 'unknown')
                health = container.get('Health', 'No health check')
                
                container_status[service] = {
                    'state': state,
                    'health': health,
                    'status': 'healthy' if state == 'running' and health in ['healthy', 'No health check'] else 'unhealthy'
                }
            
            return {
                'status': 'success',
                'containers': container_status,
                'total': len(containers),
                'healthy': sum(1 for c in container_status.values() if c['status'] == 'healthy')
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'error': f"Docker command failed: {e}",
                'containers': {}
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'containers': {}
            }
    
    def test_database_connection(self) -> Dict[str, Any]:
        """Test database connectivity and basic operations"""
        self.log("Testing database connection...")
        
        # Test PostgreSQL (primary)
        postgres_result = self._test_postgres()
        
        # Test SQLite (fallback)
        sqlite_result = self._test_sqlite()
        
        return {
            'postgresql': postgres_result,
            'sqlite': sqlite_result,
            'primary_available': postgres_result['status'] == 'success',
            'fallback_available': sqlite_result['status'] == 'success'
        }
    
    def _test_postgres(self) -> Dict[str, Any]:
        """Test PostgreSQL connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Test tables exist
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'success',
                'version': version,
                'tables': tables,
                'table_count': len(tables)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _test_sqlite(self) -> Dict[str, Any]:
        """Test SQLite connection"""
        try:
            db_path = './watch1.db'
            if not os.path.exists(db_path):
                return {
                    'status': 'error',
                    'error': 'SQLite database file not found'
                }
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            
            # Test tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get media count
            if 'media_files' in tables:
                cursor.execute("SELECT COUNT(*) FROM media_files;")
                media_count = cursor.fetchone()[0]
            else:
                media_count = 0
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'success',
                'version': version,
                'tables': tables,
                'table_count': len(tables),
                'media_count': media_count
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_redis_connection(self) -> Dict[str, Any]:
        """Test Redis connectivity"""
        self.log("Testing Redis connection...")
        
        try:
            r = redis.Redis(**self.redis_config)
            
            # Test basic operations
            r.ping()
            r.set('health_check', 'ok', ex=10)
            value = r.get('health_check')
            
            # Get info
            info = r.info()
            
            return {
                'status': 'success',
                'version': info.get('redis_version'),
                'memory_used': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'operations_per_sec': info.get('instantaneous_ops_per_sec')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoint health"""
        self.log("Testing API endpoints...")
        
        # First get auth token
        auth_result = self._get_auth_token()
        if auth_result['status'] != 'success':
            return {
                'authentication': auth_result,
                'endpoints': {}
            }
        
        token = auth_result['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        endpoints = [
            ('/version', 'Version'),
            ('/media/', 'Media Library'),
            ('/playlists/', 'Playlists'),
            ('/analytics/dashboard', 'Analytics'),
            ('/settings/', 'Settings')
        ]
        
        endpoint_results = {}
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers if endpoint != '/version' else {},
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    endpoint_results[name] = {
                        'status': 'success',
                        'status_code': response.status_code,
                        'response_time_ms': round(response_time, 2),
                        'data_keys': list(data.keys()) if isinstance(data, dict) else 'non-dict',
                        'data_size': len(str(data))
                    }
                else:
                    endpoint_results[name] = {
                        'status': 'error',
                        'status_code': response.status_code,
                        'response_time_ms': round(response_time, 2),
                        'error': response.text[:200]
                    }
                    
            except Exception as e:
                endpoint_results[name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'authentication': auth_result,
            'endpoints': endpoint_results
        }
    
    def _get_auth_token(self) -> Dict[str, Any]:
        """Get authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login/access-token",
                json={
                    'username': 'test@example.com',
                    'password': 'testpass123'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'success',
                    'token': data.get('access_token')
                }
            else:
                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_frontend_health(self) -> Dict[str, Any]:
        """Test frontend accessibility"""
        self.log("Testing frontend health...")
        
        try:
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'success' if response.status_code == 200 else 'error',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'content_length': len(response.content)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_nginx_proxy(self) -> Dict[str, Any]:
        """Test Nginx proxy health"""
        self.log("Testing Nginx proxy...")
        
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.nginx_url}/health", timeout=5)
            
            # Test API proxy
            api_response = requests.get(f"{self.nginx_url}/api/v1/version", timeout=5)
            
            return {
                'health_endpoint': {
                    'status': 'success' if health_response.status_code == 200 else 'error',
                    'status_code': health_response.status_code
                },
                'api_proxy': {
                    'status': 'success' if api_response.status_code == 200 else 'error',
                    'status_code': api_response.status_code
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive report"""
        self.log("Starting comprehensive health check...", "INFO")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'docker': self.test_docker_containers(),
            'database': self.test_database_connection(),
            'redis': self.test_redis_connection(),
            'api': self.test_api_endpoints(),
            'frontend': self.test_frontend_health(),
            'nginx': self.test_nginx_proxy()
        }
        
        # Calculate overall health
        health_scores = []
        
        # Docker health
        if report['docker']['status'] == 'success':
            docker_score = report['docker']['healthy'] / max(report['docker']['total'], 1)
            health_scores.append(docker_score)
        
        # Database health
        if report['database']['primary_available'] or report['database']['fallback_available']:
            health_scores.append(1.0)
        else:
            health_scores.append(0.0)
        
        # Redis health
        health_scores.append(1.0 if report['redis']['status'] == 'success' else 0.0)
        
        # API health
        if report['api']['authentication']['status'] == 'success':
            api_endpoints = report['api']['endpoints']
            if api_endpoints:
                api_score = sum(1 for ep in api_endpoints.values() if ep.get('status') == 'success') / len(api_endpoints)
                health_scores.append(api_score)
        
        # Frontend health
        health_scores.append(1.0 if report['frontend']['status'] == 'success' else 0.0)
        
        overall_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
        
        report['overall_health'] = {
            'score': round(overall_health * 100, 1),
            'status': 'healthy' if overall_health >= 0.8 else 'degraded' if overall_health >= 0.5 else 'unhealthy'
        }
        
        return report
    
    def print_health_report(self, report: Dict[str, Any]):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("WATCH1 v3.0.1 - DEVELOPMENT ENVIRONMENT HEALTH REPORT")
        print("="*60)
        
        # Overall status
        overall = report['overall_health']
        status_color = {
            'healthy': 'SUCCESS',
            'degraded': 'WARNING',
            'unhealthy': 'ERROR'
        }.get(overall['status'], 'INFO')
        
        self.log(f"Overall Health: {overall['score']}% ({overall['status'].upper()})", status_color)
        print()
        
        # Docker containers
        self.log("Docker Containers:", "INFO")
        docker = report['docker']
        if docker['status'] == 'success':
            for service, info in docker['containers'].items():
                status_level = 'SUCCESS' if info['status'] == 'healthy' else 'ERROR'
                self.log(f"  {service}: {info['state']} ({info['health']})", status_level)
        else:
            self.log(f"  Error: {docker.get('error', 'Unknown error')}", "ERROR")
        print()
        
        # Database
        self.log("Database:", "INFO")
        db = report['database']
        if db['primary_available']:
            pg = db['postgresql']
            self.log(f"  PostgreSQL: Connected ({pg['table_count']} tables)", "SUCCESS")
        else:
            self.log("  PostgreSQL: Not available", "WARNING")
        
        if db['fallback_available']:
            sqlite = db['sqlite']
            self.log(f"  SQLite: Connected ({sqlite['table_count']} tables, {sqlite['media_count']} media)", "SUCCESS")
        else:
            self.log("  SQLite: Not available", "ERROR")
        print()
        
        # Redis
        self.log("Redis Cache:", "INFO")
        redis_info = report['redis']
        if redis_info['status'] == 'success':
            self.log(f"  Connected (v{redis_info['version']}, {redis_info['memory_used']})", "SUCCESS")
        else:
            self.log(f"  Error: {redis_info.get('error', 'Unknown error')}", "ERROR")
        print()
        
        # API Endpoints
        self.log("API Endpoints:", "INFO")
        api = report['api']
        if api['authentication']['status'] == 'success':
            self.log("  Authentication: Working", "SUCCESS")
            for name, info in api['endpoints'].items():
                if info['status'] == 'success':
                    self.log(f"  {name}: OK ({info['response_time_ms']}ms)", "SUCCESS")
                else:
                    self.log(f"  {name}: Error {info.get('status_code', 'N/A')}", "ERROR")
        else:
            self.log("  Authentication: Failed", "ERROR")
        print()
        
        # Frontend
        self.log("Frontend:", "INFO")
        frontend = report['frontend']
        if frontend['status'] == 'success':
            self.log(f"  Accessible ({frontend['response_time_ms']}ms)", "SUCCESS")
        else:
            self.log(f"  Error: {frontend.get('error', 'Unknown error')}", "ERROR")
        print()
        
        # Nginx
        self.log("Nginx Proxy:", "INFO")
        nginx = report['nginx']
        if 'health_endpoint' in nginx:
            health_status = 'SUCCESS' if nginx['health_endpoint']['status'] == 'success' else 'ERROR'
            self.log(f"  Health endpoint: {nginx['health_endpoint']['status']}", health_status)
            
            api_status = 'SUCCESS' if nginx['api_proxy']['status'] == 'success' else 'ERROR'
            self.log(f"  API proxy: {nginx['api_proxy']['status']}", api_status)
        else:
            self.log(f"  Error: {nginx.get('error', 'Unknown error')}", "ERROR")
        
        print("\n" + "="*60)
        self.log(f"Report generated at: {report['timestamp']}", "INFO")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Watch1 Development Environment Health Monitor')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    monitor = HealthMonitor()
    
    if args.continuous:
        try:
            while True:
                report = monitor.run_comprehensive_health_check()
                
                if args.json:
                    print(json.dumps(report, indent=2))
                else:
                    monitor.print_health_report(report)
                
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            monitor.log("Monitoring stopped by user", "INFO")
    else:
        report = monitor.run_comprehensive_health_check()
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            monitor.print_health_report(report)

if __name__ == "__main__":
    main()
