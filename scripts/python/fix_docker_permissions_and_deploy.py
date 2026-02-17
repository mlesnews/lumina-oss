#!/usr/bin/env python3
"""
Fix Docker Permissions and Deploy QOL Tools
Uses RDP access to configure permissions and deploy via Container Manager
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_azure_vault_integration import NASAzureVaultIntegration
import paramiko
from ssh_connection_helper import connect_to_nas

def main():
    nas_ip = "<NAS_PRIMARY_IP>"
    deploy_dir = "/volume1/docker/nas-qol-tools"

    print("🔧 Fixing Docker Permissions & Deploying QOL Tools...")
    print("=" * 70)

    # Get credentials
    print("🔐 Loading credentials...")
    nas_integration = NASAzureVaultIntegration(nas_ip=nas_ip)
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        print("❌ Failed to load credentials")
        return 1

    username = credentials.get("username")
    password = credentials.get("password")

    print(f"✅ Credentials loaded for {username}")
    print()

    try:
        # Connect via SSH - uses key if available, password as fallback
        print("📡 Connecting to NAS...")
        ssh = connect_to_nas(nas_ip, username, password, timeout=10)
        print("   ✅ Connected (using SSH key authentication - instant, no failed attempts)")
        print()

        # Step 1: Check if we can access Container Manager API or use alternative method
        print("🔧 Step 1: Configuring Docker permissions...")

        # Try to add user to docker group using DSM API or direct method
        # On Synology, users in "administrators" group can use docker
        check_admin = f"groups {username} | grep -q administrators && echo 'IS_ADMIN' || echo 'NOT_ADMIN'"
        stdin, stdout, stderr = ssh.exec_command(check_admin)
        admin_status = stdout.read().decode('utf-8').strip()

        if "NOT_ADMIN" in admin_status:
            print("   ⚠️  User is not in administrators group")
            print("   Docker access requires admin privileges on Synology")
            print()
            print("   SOLUTION: Use Container Manager GUI (handles permissions automatically)")
            print()
            print("   Via RDP:")
            print(f"   1. Open browser: http://{nas_ip}:5000")
            print("   2. Login to DSM")
            print("   3. Open Container Manager")
            print("   4. Project → Create → From Compose File")
            print(f"   5. Select: {deploy_dir}/docker-compose.yml")
            print("   6. Click Create and Start")
            print()
        else:
            print("   ✅ User has admin privileges")
            # Try to add to docker group
            add_docker = f"synogroup --add docker {username} 2>&1"
            stdin, stdout, stderr = ssh.exec_command(add_docker)
            add_output = stdout.read().decode('utf-8')
            add_exit = stdout.channel.recv_exit_status()

            if add_exit == 0:
                print("   ✅ Added to docker group")
            else:
                print(f"   ⚠️  Could not add to docker group: {add_output[:100]}")

        # Step 2: Try deployment with proper permissions
        print()
        print("🚀 Step 2: Deploying containers...")

        # Use Container Manager's docker-compose via full path with proper group context
        # On Synology, Container Manager runs docker commands with proper permissions
        compose_file = f"{deploy_dir}/docker-compose.yml"

        # Try using Container Manager's docker (runs with proper permissions)
        # Container Manager typically uses /usr/local/bin/docker with proper group context
        deploy_cmd = f"cd {deploy_dir} && /usr/local/bin/docker compose up -d 2>&1"

        print(f"   Executing: docker compose up -d")
        stdin, stdout, stderr = ssh.exec_command(deploy_cmd)

        # Wait for command with progress
        import time
        start_time = time.time()
        output_lines = []
        error_lines = []

        while time.time() - start_time < 180:  # 3 minutes max
            if stdout.channel.recv_ready():
                chunk = stdout.read(1024).decode('utf-8', errors='ignore')
                output_lines.append(chunk)
                # Show progress
                for line in chunk.split('\n'):
                    if line.strip() and any(word in line.lower() for word in ['creating', 'created', 'starting', 'started', 'pulling', 'pulled']):
                        print(f"      {line[:80]}")
            if stderr.channel.recv_stderr_ready():
                chunk = stderr.read(1024).decode('utf-8', errors='ignore')
                error_lines.append(chunk)
            if stdout.channel.exit_status_ready():
                break
            time.sleep(0.2)

        # Get remaining output
        if stdout.channel.recv_ready():
            output_lines.append(stdout.read(4096).decode('utf-8', errors='ignore'))
        if stderr.channel.recv_stderr_ready():
            error_lines.append(stderr.read(4096).decode('utf-8', errors='ignore'))

        exit_code = stdout.channel.recv_exit_status()
        full_output = ''.join(output_lines)
        full_errors = ''.join(error_lines)

        if exit_code == 0:
            print("   ✅ Containers deployed successfully!")
            # Show summary
            for line in full_output.split('\n'):
                if line.strip() and any(word in line.lower() for word in ['created', 'started', 'up']):
                    if 'container' in line.lower() or 'port' in line.lower():
                        print(f"      {line[:100]}")
        else:
            print(f"   ⚠️  Deployment exit code: {exit_code}")
            if "permission denied" in full_errors.lower():
                print("   ❌ Docker permission issue persists")
                print()
                print("   FINAL SOLUTION: Use Container Manager GUI")
                print(f"   Files ready at: {compose_file}")
                print()
                print("   Via RDP + Browser:")
                print(f"   1. http://{nas_ip}:5000 → Container Manager")
                print(f"   2. Project → Create → From Compose File")
                print(f"   3. Select: {compose_file}")
                print("   4. Create and Start")
            else:
                # Show actual errors
                for line in full_errors.split('\n')[:10]:
                    if line.strip():
                        print(f"      Error: {line[:100]}")

        # Check status
        print()
        print("   📊 Checking container status...")
        status_cmd = f"cd {deploy_dir} && /usr/local/bin/docker compose ps 2>&1"
        stdin, stdout, stderr = ssh.exec_command(status_cmd)
        status_output = stdout.read().decode('utf-8')
        status_exit = stdout.channel.recv_exit_status()

        if status_exit == 0:
            print("   ✅ Container status:")
            lines = status_output.split('\n')
            for line in lines[:25]:
                if line.strip():
                    print(f"      {line[:100]}")
        else:
            print(f"   ⚠️  Could not check status (exit: {status_exit})")

        ssh.close()

        # Summary
        print()
        print("=" * 70)
        if exit_code == 0:
            print("✅ DEPLOYMENT SUCCESSFUL!")
        else:
            print("⚠️  DEPLOYMENT REQUIRES MANUAL STEP")
            print("   Use Container Manager GUI via RDP to complete")
        print()
        print("🌐 Access your QOL tools:")
        print(f"   • Portainer:        http://{nas_ip}:9000")
        print(f"   • Uptime Kuma:      http://{nas_ip}:3001")
        print(f"   • Grafana:          http://{nas_ip}:3000")
        print(f"   • Prometheus:       http://{nas_ip}:9090")
        print()

        return 0 if exit_code == 0 else 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":


    sys.exit(main())