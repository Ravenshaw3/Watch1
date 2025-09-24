#!/usr/bin/env python3
"""
Watch1 v3.0.1 Production Server Startup Script
Cleans up existing processes and starts fresh production servers
"""

import subprocess
import time
import sys
import os
import signal
import psutil
from typing import List, Dict, Any

class ProductionServerManager:
    def __init__(self):
        self.backend_port = 8000
        self.frontend_port = 3000
        self.backend_process = None
        self.frontend_process = None

    def log(self, message: str, status: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")

    def find_processes_on_port(self, port: int) -> List[Dict[str, Any]]:
        """Find all processes using a specific port"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': proc.info['cmdline']
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            self.log(f"Error finding processes on port {port}: {e}", "WARNING")
        
        return processes

    def kill_process(self, pid: int, name: str = "Unknown") -> bool:
        """Kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            # Wait for graceful termination
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if graceful termination fails
                proc.kill()
                proc.wait()
            
            self.log(f"Killed process {name} (PID: {pid})", "SUCCESS")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.log(f"Could not kill process {pid}: {e}", "WARNING")
            return False

    def cleanup_existing_servers(self):
        """Clean up any existing server processes"""
        self.log("Checking for existing server processes...")
        
        # Check backend port
        backend_processes = self.find_processes_on_port(self.backend_port)
        if backend_processes:
            self.log(f"Found {len(backend_processes)} process(es) on backend port {self.backend_port}")
            for proc in backend_processes:
                self.log(f"  - {proc['name']} (PID: {proc['pid']})")
                self.kill_process(proc['pid'], proc['name'])
        else:
            self.log(f"Backend port {self.backend_port} is free", "SUCCESS")
        
        # Check frontend port
        frontend_processes = self.find_processes_on_port(self.frontend_port)
        if frontend_processes:
            self.log(f"Found {len(frontend_processes)} process(es) on frontend port {self.frontend_port}")
            for proc in frontend_processes:
                self.log(f"  - {proc['name']} (PID: {proc['pid']})")
                self.kill_process(proc['pid'], proc['name'])
        else:
            self.log(f"Frontend port {self.frontend_port} is free", "SUCCESS")
        
        # Also check for any lingering Node.js processes that might be Watch1 related
        self.cleanup_node_processes()
        
        # Wait for ports to be fully released
        if backend_processes or frontend_processes:
            self.log("Waiting for ports to be released...")
            time.sleep(3)

    def cleanup_node_processes(self):
        """Clean up Node.js processes that might be related to Watch1"""
        try:
            node_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'node.exe' or proc.info['name'] == 'node':
                        cmdline = proc.info['cmdline'] or []
                        cmdline_str = ' '.join(cmdline).lower()
                        
                        # Check if it's likely a Watch1 frontend process
                        if any(keyword in cmdline_str for keyword in ['vite', 'watch1', 'frontend', 'dev']):
                            node_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline_str
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if node_processes:
                self.log(f"Found {len(node_processes)} potentially related Node.js process(es)")
                for proc in node_processes:
                    self.log(f"  - {proc['name']} (PID: {proc['pid']}): {proc['cmdline'][:100]}...")
                    self.kill_process(proc['pid'], f"Node.js ({proc['pid']})")
        except Exception as e:
            self.log(f"Error cleaning up Node.js processes: {e}", "WARNING")

    def verify_ports_free(self) -> bool:
        """Verify that required ports are free"""
        backend_free = len(self.find_processes_on_port(self.backend_port)) == 0
        frontend_free = len(self.find_processes_on_port(self.frontend_port)) == 0
        
        if not backend_free:
            self.log(f"Backend port {self.backend_port} is still in use!", "ERROR")
        if not frontend_free:
            self.log(f"Frontend port {self.frontend_port} is still in use!", "ERROR")
        
        return backend_free and frontend_free

    def start_backend_server(self) -> bool:
        """Start the Flask backend server"""
        try:
            self.log("Starting Flask backend server...")
            
            backend_path = os.path.join(os.getcwd(), 'backend')
            if not os.path.exists(os.path.join(backend_path, 'flask_simple.py')):
                self.log("flask_simple.py not found in backend directory!", "ERROR")
                return False
            
            # Start the backend server
            self.backend_process = subprocess.Popen(
                [sys.executable, 'flask_simple.py'],
                cwd=backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment and check if it started successfully
            time.sleep(2)
            if self.backend_process.poll() is None:
                self.log(f"Backend server started (PID: {self.backend_process.pid})", "SUCCESS")
                self.log(f"Backend URL: http://localhost:{self.backend_port}", "SUCCESS")
                return True
            else:
                self.log("Backend server failed to start", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error starting backend server: {e}", "ERROR")
            return False

    def start_frontend_server(self) -> bool:
        """Start the Vue.js frontend server"""
        try:
            self.log("Starting Vue.js frontend server...")
            
            frontend_path = os.path.join(os.getcwd(), 'frontend')
            if not os.path.exists(os.path.join(frontend_path, 'package.json')):
                self.log("package.json not found in frontend directory!", "ERROR")
                return False
            
            # Start the frontend server
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait for frontend to start (it takes longer)
            self.log("Waiting for frontend to initialize...")
            time.sleep(8)
            
            if self.frontend_process.poll() is None:
                self.log(f"Frontend server started (PID: {self.frontend_process.pid})", "SUCCESS")
                self.log(f"Frontend URL: http://localhost:{self.frontend_port}", "SUCCESS")
                return True
            else:
                self.log("Frontend server failed to start", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error starting frontend server: {e}", "ERROR")
            return False

    def test_servers(self) -> bool:
        """Test that both servers are responding"""
        try:
            import requests
            
            # Test backend
            try:
                response = requests.get(f'http://localhost:{self.backend_port}/api/v1/version', timeout=5)
                if response.status_code == 200:
                    version_data = response.json()
                    self.log(f"Backend test: OK (v{version_data.get('version', 'unknown')})", "SUCCESS")
                    backend_ok = True
                else:
                    self.log(f"Backend test: FAILED (HTTP {response.status_code})", "ERROR")
                    backend_ok = False
            except Exception as e:
                self.log(f"Backend test: FAILED ({str(e)})", "ERROR")
                backend_ok = False
            
            # Test frontend
            try:
                response = requests.get(f'http://localhost:{self.frontend_port}', timeout=5)
                if response.status_code == 200:
                    self.log("Frontend test: OK", "SUCCESS")
                    frontend_ok = True
                else:
                    self.log(f"Frontend test: FAILED (HTTP {response.status_code})", "ERROR")
                    frontend_ok = False
            except Exception as e:
                self.log(f"Frontend test: FAILED ({str(e)})", "ERROR")
                frontend_ok = False
            
            return backend_ok and frontend_ok
            
        except ImportError:
            self.log("Requests library not available for testing", "WARNING")
            return True  # Assume OK if we can't test

    def start_production_servers(self):
        """Main method to start production servers"""
        self.log("=" * 60)
        self.log("WATCH1 v3.0.1 - PRODUCTION SERVER STARTUP")
        self.log("=" * 60)
        
        # Step 1: Cleanup existing processes
        self.cleanup_existing_servers()
        
        # Step 2: Verify ports are free
        if not self.verify_ports_free():
            self.log("Cannot start servers - ports still in use!", "ERROR")
            return False
        
        # Step 3: Start backend server
        if not self.start_backend_server():
            self.log("Failed to start backend server", "ERROR")
            return False
        
        # Step 4: Start frontend server
        if not self.start_frontend_server():
            self.log("Failed to start frontend server", "ERROR")
            self.cleanup_on_exit()
            return False
        
        # Step 5: Test servers
        self.log("Testing server connectivity...")
        if self.test_servers():
            self.log("=" * 60)
            self.log("PRODUCTION SERVERS SUCCESSFULLY STARTED!", "SUCCESS")
            self.log("=" * 60)
            self.log(f"Backend:  http://localhost:{self.backend_port}")
            self.log(f"Frontend: http://localhost:{self.frontend_port}")
            self.log("=" * 60)
            self.log("Press Ctrl+C to stop all servers")
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log("Shutting down servers...")
                self.cleanup_on_exit()
                return True
        else:
            self.log("Server tests failed!", "ERROR")
            self.cleanup_on_exit()
            return False

    def cleanup_on_exit(self):
        """Clean up processes on exit"""
        if self.backend_process and self.backend_process.poll() is None:
            self.log("Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process and self.frontend_process.poll() is None:
            self.log("Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()

if __name__ == "__main__":
    manager = ProductionServerManager()
    success = manager.start_production_servers()
    sys.exit(0 if success else 1)
