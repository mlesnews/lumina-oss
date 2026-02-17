#!/usr/bin/env python3
"""
Fix Iron Legion containers on KAIJU desktop.

Starts the missing Iron Legion containers that should be running at <NAS_PRIMARY_IP>:3001-3007.
"""

import subprocess
import sys
import time
from pathlib import Path
import logging
logger = logging.getLogger("fix_iron_legion_containers")


def run_command(cmd, cwd=None):
    """Run command and return (stdout, returncode)"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1

def check_iron_legion_containers():
    """Check status of Iron Legion containers on desktop"""
    print("🔍 Checking Iron Legion containers on KAIJU desktop (<NAS_PRIMARY_IP>)...")

    # SSH command to check containers
    ssh_cmd = 'ssh <NAS_PRIMARY_IP> "docker ps --filter \'name=iron-legion\' --format \'{{.Names}}\t{{.Status}}\'"'
    stdout, code = run_command(ssh_cmd)

    if code != 0:
        print(f"❌ Cannot connect to KAIJU desktop: {stdout}")
        return False

    containers = []
    if stdout.strip():
        for line in stdout.strip().split('\n'):
            if line.strip():
                name, status = line.split('\t', 1)
                containers.append((name, status))
                print(f"   {name}: {status}")

    expected_containers = [
        "iron-legion-mark-i-codellama-llamacpp",
        "iron-legion-mark-ii-llama32-llamacpp",
        "iron-legion-mark-iii-qwen-llamacpp",
        "iron-legion-mark-iv-llama3-llamacpp",
        "iron-legion-mark-v-mistral-llamacpp",
        "iron-legion-mark-vi-mixtral-llamacpp",
        "iron-legion-mark-vii-gemma-llamacpp"
    ]

    running_containers = [name for name, status in containers if 'Up' in status]

    print(f"\n📊 Status: {len(running_containers)}/{len(expected_containers)} containers running")

    if len(running_containers) < len(expected_containers):
        print("\n⚠️  Missing containers detected. Starting Iron Legion cluster...")
        return start_iron_legion_cluster()

    return len(running_containers) == len(expected_containers)

def start_iron_legion_cluster():
    try:
        """Start Iron Legion cluster using docker-compose"""
        print("🚀 Starting Iron Legion cluster on KAIJU desktop...")

        # Find docker-compose file
        project_root = Path(__file__).parent.parent.parent
        compose_files = [
            project_root / "containerization" / "docker-compose.iron-legion.yml",
            project_root / ".lumina" / "containerization" / "docker-compose.iron-legion.yml",
            project_root / "<COMPANY>-financial-services_llc-env" / "containerization" / "docker-compose.iron-legion.yml"
        ]

        compose_file = None
        for cf in compose_files:
            if cf.exists():
                compose_file = cf
                break

        if not compose_file:
            print("❌ Cannot find docker-compose.iron-legion.yml file")
            return False

        print(f"📁 Using compose file: {compose_file}")

        # Copy compose file to desktop and start
        remote_path = "/tmp/docker-compose.iron-legion.yml"

        # SCP the file
        scp_cmd = f'scp "{compose_file}" <NAS_PRIMARY_IP>:{remote_path}'
        stdout, code = run_command(scp_cmd)

        if code != 0:
            print(f"❌ Failed to copy compose file: {stdout}")
            return False

        # Start containers
        ssh_cmd = f'ssh <NAS_PRIMARY_IP> "cd /tmp && docker-compose -f docker-compose.iron-legion.yml up -d"'
        stdout, code = run_command(ssh_cmd)

        if code != 0:
            print(f"❌ Failed to start containers: {stdout}")
            return False

        print("✅ Iron Legion containers started")
        print("⏳ Waiting 30 seconds for containers to initialize...")

        time.sleep(30)

        # Verify containers are running
        return check_iron_legion_containers()

    except Exception as e:
        logger.error(f"Error in start_iron_legion_cluster: {e}", exc_info=True)
        raise
def test_iron_legion_endpoints():
    """Test Iron Legion endpoints"""
    print("\n🧪 Testing Iron Legion endpoints...")

    endpoints = [
        ("http://<NAS_PRIMARY_IP>:3001/health", "Mark I"),
        ("http://<NAS_PRIMARY_IP>:3002/health", "Mark II"),
        ("http://<NAS_PRIMARY_IP>:3003/health", "Mark III"),
        ("http://<NAS_PRIMARY_IP>:3004/health", "Mark IV"),
        ("http://<NAS_PRIMARY_IP>:3005/health", "Mark V"),
        ("http://<NAS_PRIMARY_IP>:3006/health", "Mark VI"),
        ("http://<NAS_PRIMARY_IP>:3007/health", "Mark VII")
    ]

    healthy = 0
    for url, name in endpoints:
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} ({url}): HEALTHY")
                healthy += 1
            else:
                print(f"   ❌ {name} ({url}): HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name} ({url}): ERROR - {e}")

    print(f"\n📊 Iron Legion Health: {healthy}/7 nodes healthy")
    return healthy == 7

def main():
    """Main function"""
    print("🔧 IRON LEGION CONTAINER FIX")
    print("=" * 50)

    # Check containers
    containers_ok = check_iron_legion_containers()

    if not containers_ok:
        print("\n❌ Iron Legion containers are not properly running")
        return 1

    # Test endpoints
    endpoints_ok = test_iron_legion_endpoints()

    if endpoints_ok:
        print("\n✅ Iron Legion cluster is fully operational!")
        return 0
    else:
        print("\n⚠️  Iron Legion containers are running but some endpoints are not responding")
        print("   This may be normal during startup. Try again in a few minutes.")
        return 1

if __name__ == "__main__":

    sys.exit(main())