#!/usr/bin/env python3
"""
ULTRON Cluster Router Startup Script for NAS Cron
Automatically starts the ULTRON router service on NAS boot
"""
import subprocess
import sys
import time
import socket
from pathlib import Path

def start_ultron_router():
    """Start the ULTRON router service"""
    print("🚀 Starting ULTRON Cluster Router...")

    try:
        # Navigate to project root (assuming script is in /volume1/scripts/)
        project_root = Path("/volume1/scripts/../../my_projects/.lumina")
        if not project_root.exists():
            project_root = Path("/volume1/my_projects/.lumina")

        if not project_root.exists():
            print("❌ Project directory not found")
            return False

        # Check if router is already running
        try:
            with socket.create_connection(("<NAS_PRIMARY_IP>", 3008), timeout=5):
                print("✅ ULTRON Router is already running")
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass

        # Start the router
        print("🔧 Starting ULTRON Router service...")

        # Use the deployment script
        deploy_script = project_root / "deploy_ultron_production.py"
        if not deploy_script.exists():
            print("❌ Deployment script not found")
            return False

        # Start the router in background
        process = subprocess.Popen([
            sys.executable, str(deploy_script), "--start"
        ], cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for startup (up to 30 seconds)
        timeout = 30
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            try:
                with socket.create_connection(("<NAS_PRIMARY_IP>", 3008), timeout=2):
                    print("✅ ULTRON Router started successfully")
                    return True
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(2)

        print("⚠️ ULTRON Router took too long to start")
        return False

    except Exception as e:
        print(f"❌ Failed to start ULTRON Router: {e}")
        return False

if __name__ == "__main__":
    success = start_ultron_router()
    sys.exit(0 if success else 1)