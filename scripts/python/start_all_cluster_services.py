#!/usr/bin/env python3
"""
Start all ULTRON and Iron Legion services across the cluster.

This script should be run on each machine in the cluster:
- Laptop (<NAS_IP>): Start Ollama
- Desktop (<NAS_PRIMARY_IP>): Start Ollama + Iron Legion containers
- NAS (<NAS_IP>): Start Ollama + Iron Legion containers
"""

import subprocess
import sys
import time
import socket
from pathlib import Path
import logging
logger = logging.getLogger("start_all_cluster_services")


def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a dummy address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def run_command(cmd, shell=True, capture_output=True, text=True, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture_output,
                              text=text, cwd=cwd)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")

    # Check if Ollama is already running
    stdout, stderr, code = run_command("curl -s http://localhost:11434/api/tags")
    if code == 0:
        print("✅ Ollama is already running")
        return True

    # Try to start Ollama
    print("Starting Ollama...")
    stdout, stderr, code = run_command("ollama serve", shell=False)
    if code != 0:
        print(f"❌ Failed to start Ollama: {stderr}")
        return False

    # Wait for Ollama to start
    print("⏳ Waiting for Ollama to initialize...")
    for i in range(30):
        time.sleep(2)
        stdout, stderr, code = run_command("curl -s http://localhost:11434/api/tags")
        if code == 0:
            print("✅ Ollama started successfully")
            return True

    print("❌ Ollama failed to start within 60 seconds")
    return False

def start_continuous_git_commit():
    """Start continuous git commit service"""
    print("🚀 Starting Continuous Git Commit service...")

    try:
        # Import and run the startup script
        script_path = Path(__file__).parent / "start_continuous_git_commit.py"
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=Path(__file__).parent)

        if result.returncode == 0:
            print("✅ Continuous Git Commit service started")
            return True
        else:
            print(f"❌ Failed to start Continuous Git Commit: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error starting Continuous Git Commit service: {e}")
        return False

def start_iron_legion_containers():
    try:
        """Start Iron Legion Docker containers"""
        print("🚀 Starting Iron Legion containers...")

        local_ip = get_local_ip()
        print(f"Local IP: {local_ip}")

        # Determine which compose file to use based on IP
        if local_ip.startswith("<NAS_PRIMARY_IP>"):  # Desktop
            compose_file = "containerization/docker-compose.iron-legion.yml"
            print("📍 Running on DESKTOP - using Iron Legion compose")
        elif local_ip.startswith("<NAS_IP>"):  # NAS
            compose_file = "containerization/docker-compose.iron-legion.yml"
            print("📍 Running on NAS - using Iron Legion compose")
        else:
            print(f"📍 Local IP {local_ip} not recognized as cluster node")
            return False

        # Check if compose file exists
        if not Path(compose_file).exists():
            print(f"❌ Compose file not found: {compose_file}")
            return False

        # Stop any existing containers
        print("Stopping existing containers...")
        run_command(f"docker-compose -f {compose_file} down")

        # Start containers
        print("Starting Iron Legion containers...")
        stdout, stderr, code = run_command(f"docker-compose -f {compose_file} up -d")

        if code != 0:
            print(f"❌ Failed to start containers: {stderr}")
            return False

        print("✅ Iron Legion containers started")
        print("⏳ Waiting 30 seconds for containers to initialize...")

        time.sleep(30)

        # Check container status
        stdout, stderr, code = run_command("docker ps --filter 'name=iron' --format '{{.Names}}\t{{.Status}}'")
        if code == 0 and stdout.strip():
            containers = [line.split('\t')[0] for line in stdout.strip().split('\n') if line.strip()]
            running = [c for c in containers if 'Up' in stdout]
            print(f"📊 Containers: {len(running)}/{len(containers)} running")
            return len(running) > 0
        else:
            print("❌ No Iron Legion containers found running")
            return False

    except Exception as e:
        logger.error(f"Error in start_iron_legion_containers: {e}", exc_info=True)
        raise
def test_local_services():
    """Test local services"""
    print("🧪 Testing local services...")

    local_ip = get_local_ip()
    tests_passed = 0
    total_tests = 0

    # Test Ollama
    total_tests += 1
    stdout, stderr, code = run_command("curl -s http://localhost:11434/api/tags")
    if code == 0:
        print("✅ Ollama API responding")
        tests_passed += 1
    else:
        print("❌ Ollama API not responding")

    # Test Iron Legion endpoints based on IP
    if local_ip.startswith("<NAS_PRIMARY_IP>"):  # Desktop
        iron_ports = [3001, 3002, 3003, 3004, 3005, 3006, 3007]
    elif local_ip.startswith("<NAS_IP>"):  # NAS
        iron_ports = [3001, 3002, 3003, 3004]
    else:
        iron_ports = []

    for port in iron_ports:
        total_tests += 1
        stdout, stderr, code = run_command(f"curl -s http://localhost:{port}/health")
        if code == 0:
            print(f"✅ Iron Legion port {port} responding")
            tests_passed += 1
        else:
            print(f"❌ Iron Legion port {port} not responding")

    print(f"📊 Tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def main():
    """Main function"""
    print("🔧 ULTRON CLUSTER SERVICE STARTER")
    print("=" * 50)

    local_ip = get_local_ip()
    print(f"Local IP: {local_ip}")

    # Determine machine type
    if local_ip.startswith("<NAS_IP>") or local_ip == "10.2.0.2":
        machine_type = "LAPTOP"
    elif local_ip.startswith("<NAS_PRIMARY_IP>"):
        machine_type = "DESKTOP"
    elif local_ip.startswith("<NAS_IP>"):
        machine_type = "NAS"
    else:
        machine_type = "UNKNOWN"

    print(f"Machine Type: {machine_type}")
    print()

    success = True

    # Start Continuous Git Commit on all machines
    if not start_continuous_git_commit():
        success = False

    # Start Ollama on all machines
    if not start_ollama_service():
        success = False

    # Start Iron Legion on desktop and NAS
    if machine_type in ["DESKTOP", "NAS"]:
        if not start_iron_legion_containers():
            success = False
    else:
        print("ℹ️  Skipping Iron Legion containers (not desktop/NAS)")

    # Test services
    if not test_local_services():
        success = False

    if success:
        print("\n✅ All services started successfully!")
        print(f"This {machine_type} is now fully operational in the ULTRON cluster.")
        return 0
    else:
        print("\n❌ Some services failed to start. Check logs above.")
        return 1

if __name__ == "__main__":

    sys.exit(main())