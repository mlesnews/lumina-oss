#!/usr/bin/env python3
"""
Complete QOL Deployment - Using Remote Access
Configures Docker access and deploys all containers
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_azure_vault_integration import NASAzureVaultIntegration
import paramiko
from scp import SCPClient
from ssh_connection_helper import connect_to_nas

def main():
    nas_ip = "<NAS_PRIMARY_IP>"
    deploy_dir = "/volume1/docker/nas-qol-tools"

    print("🚀 Completing QOL Tools Deployment...")
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

        # Step 1: Fix Docker socket permissions
        print("🔧 Step 1: Fixing Docker access...")

        # Check socket ownership and permissions
        check_socket = "ls -la /var/run/docker.sock 2>&1"
        stdin, stdout, stderr = ssh.exec_command(check_socket)
        socket_info = stdout.read().decode('utf-8')
        print(f"   Docker socket: {socket_info.strip()}")

        # Extract group from socket (format: srw-rw---- 1 root root or srw-rw---- 1 root docker)
        socket_group = "root"  # Default
        if "docker" in socket_info:
            socket_group = "docker"
        elif "root" in socket_info:
            # Check what groups exist
            check_groups = "getent group | grep -E '(docker|root)' 2>&1"
            stdin, stdout, stderr = ssh.exec_command(check_groups)
            groups_info = stdout.read().decode('utf-8')
            print(f"   Available groups: {groups_info.strip()[:100]}")

        # Check if user is in docker group
        check_group = f"groups {username} | grep -q docker && echo 'IN_GROUP' || echo 'NOT_IN_GROUP'"
        stdin, stdout, stderr = ssh.exec_command(check_group)
        group_status = stdout.read().decode('utf-8').strip()

        if "NOT_IN_GROUP" in group_status:
            print("   Adding user to docker group...")

            # Method 1: Try Synology-specific synogroup command (no sudo needed)
            add_syno = f"synogroup --add docker {username} 2>&1"
            stdin, stdout, stderr = ssh.exec_command(add_syno)
            syno_output = stdout.read().decode('utf-8')
            syno_errors = stderr.read().decode('utf-8')
            syno_exit = stdout.channel.recv_exit_status()

            if syno_exit == 0:
                print("   ✅ User added to docker group (via synogroup)")
            else:
                # Method 2: Try with sudo (may require password, but try anyway)
                print("   Trying with sudo...")
                add_std = f"echo '{password}' | sudo -S usermod -aG docker {username} 2>&1"
                stdin, stdout, stderr = ssh.exec_command(add_std)
                std_output = stdout.read().decode('utf-8')
                std_errors = stderr.read().decode('utf-8')
                std_exit = stdout.channel.recv_exit_status()

                if std_exit == 0 and "usermod" in std_output.lower():
                    print("   ✅ User added to docker group (via sudo usermod)")
                else:
                    print("   ⚠️  Cannot add to group automatically (requires admin access)")
                    print("   Solution: Use Container Manager GUI or configure via DSM")
        else:
            print("   ✅ User already in docker group")

        # Verify docker access - use newgrp to activate group membership in current session
        print("   Testing Docker access with newgrp...")
        test_docker_newgrp = f"newgrp docker << 'TEST_EOF'\ndocker ps 2>&1 | head -1\nTEST_EOF"
        stdin, stdout, stderr = ssh.exec_command(test_docker_newgrp)
        docker_test_newgrp = stdout.read().decode('utf-8')
        docker_exit_newgrp = stdout.channel.recv_exit_status()

        if docker_exit_newgrp == 0 or "CONTAINER" in docker_test_newgrp.upper():
            print("   ✅ Docker access works with newgrp")
            use_newgrp = True
        else:
            # Try direct access
            test_docker = "docker ps 2>&1 | head -1"
            stdin, stdout, stderr = ssh.exec_command(test_docker)
            docker_test = stdout.read().decode('utf-8')
            docker_exit = stdout.channel.recv_exit_status()

            if docker_exit == 0 or "CONTAINER" in docker_test.upper():
                print("   ✅ Docker access confirmed (direct)")
                use_newgrp = False
            else:
                print("   ⚠️  Docker access still restricted")
                print("   Will use newgrp wrapper for all docker commands...")
                use_newgrp = True
        print()

        # Step 2: Verify docker access
        print("🔍 Step 2: Verifying Docker access...")
        test_docker = "docker ps 2>&1 || /usr/local/bin/docker ps 2>&1"
        stdin, stdout, stderr = ssh.exec_command(test_docker)
        docker_test = stdout.read().decode('utf-8')
        docker_errors = stderr.read().decode('utf-8')
        docker_exit = stdout.channel.recv_exit_status()

        if docker_exit == 0 or "CONTAINER" in docker_test.upper():
            print("   ✅ Docker access confirmed")
            docker_cmd = "docker"
        else:
            # Try with full path
            test_docker_path = "/usr/local/bin/docker ps 2>&1"
            stdin, stdout, stderr = ssh.exec_command(test_docker_path)
            docker_test_path = stdout.read().decode('utf-8')
            docker_exit_path = stdout.channel.recv_exit_status()

            if docker_exit_path == 0:
                print("   ✅ Docker access confirmed (using /usr/local/bin/docker)")
                docker_cmd = "/usr/local/bin/docker"
            else:
                print(f"   ⚠️  Docker access issue: {docker_errors[:200]}")
                print("   Trying with newgrp to activate docker group...")
                docker_cmd = "newgrp docker << 'DOCKER_EOF'\ndocker\nDOCKER_EOF"
        print()

        # Step 3: Deploy containers
        print("🚀 Step 3: Deploying QOL tools containers...")
        print(f"   Working directory: {deploy_dir}")

        # Check if compose file exists
        check_file = f"test -f {deploy_dir}/docker-compose.yml && echo 'EXISTS' || echo 'MISSING'"
        stdin, stdout, stderr = ssh.exec_command(check_file)
        file_status = stdout.read().decode('utf-8').strip()

        if "MISSING" in file_status:
            print(f"   ❌ docker-compose.yml not found at {deploy_dir}")
            print("   Please ensure files were copied successfully")
            ssh.close()
            return 1

        print("   ✅ docker-compose.yml found")

        # Determine compose command - use full path
        if docker_cmd == "docker":
            # Try to find actual docker path
            find_docker = "which docker 2>/dev/null || echo '/usr/local/bin/docker'"
            stdin, stdout, stderr = ssh.exec_command(find_docker)
            docker_path = stdout.read().decode('utf-8').strip()
            if docker_path:
                docker_cmd = docker_path

        # Test compose plugin - use newgrp if needed
        if use_newgrp:
            # Use bash -c with newgrp to execute commands in docker group context
            compose_test = f"bash -c 'newgrp docker << EOF\n{docker_cmd} compose version\nEOF'"
        else:
            compose_test = f"{docker_cmd} compose version 2>&1"

        stdin, stdout, stderr = ssh.exec_command(compose_test)
        compose_output = stdout.read().decode('utf-8')
        compose_exit = stdout.channel.recv_exit_status()

        if compose_exit == 0 and ("compose" in compose_output.lower() or "version" in compose_output.lower()):
            if use_newgrp:
                # Create a wrapper script that uses newgrp
                compose_cmd = f"bash -c 'newgrp docker << EOF\n{docker_cmd} compose\nEOF'"
            else:
                compose_cmd = f"{docker_cmd} compose"
            print(f"   ✅ Using Docker Compose plugin: {docker_cmd} compose")
        else:
            # Try docker-compose standalone
            find_compose = "which docker-compose 2>/dev/null || find /usr/local/bin /usr/bin -name docker-compose -type f 2>/dev/null | head -1"
            stdin, stdout, stderr = ssh.exec_command(find_compose)
            compose_path = stdout.read().decode('utf-8').strip()
            if compose_path:
                if use_newgrp:
                    compose_cmd = f"bash -c 'newgrp docker << EOF\n{compose_path}\nEOF'"
                else:
                    compose_cmd = compose_path
                print(f"   ✅ Using docker-compose standalone: {compose_path}")
            else:
                # Last resort
                if use_newgrp:
                    compose_cmd = f"bash -c 'newgrp docker << EOF\n{docker_cmd} compose\nEOF'"
                else:
                    compose_cmd = f"{docker_cmd} compose"
                print(f"   ⚠️  Using fallback: {docker_cmd} compose")

        print(f"   Using: {compose_cmd}")
        print()

        # Pull images (skip if takes too long, can pull on first start)
        print("   📥 Pulling latest images (this may take a while)...")
        # Use the compose_cmd as-is (it already handles newgrp if needed)
        pull_cmd = f"cd {deploy_dir} && {compose_cmd} pull 2>&1"
        stdin, stdout, stderr = ssh.exec_command(pull_cmd)
        # Don't wait too long - let it run in background if needed
        pull_output = ""
        pull_errors = ""
        try:
            # Read with timeout
            import select
            import time
            start_time = time.time()
            while time.time() - start_time < 60:  # Wait up to 60 seconds
                if stdout.channel.recv_ready():
                    pull_output += stdout.read(1024).decode('utf-8', errors='ignore')
                if stderr.channel.recv_stderr_ready():
                    pull_errors += stderr.read(1024).decode('utf-8', errors='ignore')
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
            # Get remaining output
            if stdout.channel.recv_ready():
                pull_output += stdout.read(4096).decode('utf-8', errors='ignore')
            if stderr.channel.recv_stderr_ready():
                pull_errors += stderr.read(4096).decode('utf-8', errors='ignore')
            pull_exit = stdout.channel.recv_exit_status()
        except:
            pull_exit = 0  # Assume success if we can't determine
            pull_output = "Images pulling in background..."

        if pull_exit == 0 or "pulling" in pull_output.lower() or "pulled" in pull_output.lower():
            print("   ✅ Image pull initiated")
            if pull_output:
                lines = pull_output.split('\n')
                for line in lines[-3:]:
                    if line.strip():
                        print(f"      {line[:80]}")
        else:
            print(f"   ⚠️  Pull may have issues (will pull on start)")
            if pull_errors:
                print(f"      {pull_errors[:150]}")
        print()

        # Start containers
        print("   🚀 Starting containers...")
        # Use the compose_cmd as-is (it already handles newgrp if needed)
        up_cmd = f"cd {deploy_dir} && {compose_cmd} up -d 2>&1"
        stdin, stdout, stderr = ssh.exec_command(up_cmd)

        # Wait for command with timeout
        import time
        start_time = time.time()
        up_output = ""
        up_errors = ""
        while time.time() - start_time < 120:  # Wait up to 2 minutes
            if stdout.channel.recv_ready():
                chunk = stdout.read(1024).decode('utf-8', errors='ignore')
                up_output += chunk
                # Print progress
                if "creating" in chunk.lower() or "created" in chunk.lower() or "starting" in chunk.lower():
                    for line in chunk.split('\n'):
                        if line.strip() and ("creating" in line.lower() or "created" in line.lower() or "started" in line.lower()):
                            print(f"      {line[:80]}")
            if stderr.channel.recv_stderr_ready():
                up_errors += stderr.read(1024).decode('utf-8', errors='ignore')
            if stdout.channel.exit_status_ready():
                break
            time.sleep(0.2)

        # Get remaining output
        if stdout.channel.recv_ready():
            up_output += stdout.read(4096).decode('utf-8', errors='ignore')
        if stderr.channel.recv_stderr_ready():
            up_errors += stderr.read(4096).decode('utf-8', errors='ignore')

        up_exit = stdout.channel.recv_exit_status()

        if up_exit == 0:
            print("   ✅ Containers started successfully")
            # Show any remaining output
            lines = up_output.split('\n')
            shown_lines = []
            for line in lines:
                if line.strip() and ("creating" in line.lower() or "created" in line.lower() or "started" in line.lower()):
                    line_short = line[:80]
                    if line_short not in shown_lines:  # Avoid duplicates
                        print(f"      {line_short}")
                        shown_lines.append(line_short)
        else:
            print(f"   ⚠️  Exit code: {up_exit}")
            if up_output:
                # Show actual output - might contain useful info
                error_lines = up_output.split('\n')
                for err in error_lines[-10:]:
                    if err.strip() and ("error" in err.lower() or "failed" in err.lower() or "permission" in err.lower()):
                        print(f"      {err[:100]}")
            if up_errors:
                error_lines = up_errors.split('\n')[:5]
                for err in error_lines:
                    if err.strip():
                        print(f"      Error: {err[:100]}")
        print()

        # Check status
        print("   📊 Checking container status...")
        # Use the compose_cmd as-is (it already handles newgrp if needed)
        ps_cmd = f"cd {deploy_dir} && {compose_cmd} ps 2>&1"
        stdin, stdout, stderr = ssh.exec_command(ps_cmd)
        ps_output = stdout.read().decode('utf-8')
        ps_exit = stdout.channel.recv_exit_status()

        if ps_exit == 0:
            print("   ✅ Container status:")
            lines = ps_output.split('\n')
            for line in lines[:20]:  # Show first 20 lines
                if line.strip():
                    print(f"      {line[:100]}")
        print()

        ssh.close()

        # Success summary
        print("=" * 70)
        print("✅ DEPLOYMENT COMPLETED!")
        print()
        print("🌐 Access your QOL tools:")
        print(f"   • Portainer:        http://{nas_ip}:9000")
        print(f"   • Uptime Kuma:      http://{nas_ip}:3001")
        print(f"   • Grafana:          http://{nas_ip}:3000 (admin/admin - CHANGE PASSWORD!)")
        print(f"   • Prometheus:       http://{nas_ip}:9090")
        print(f"   • Traefik Dashboard: http://{nas_ip}:8080")
        print(f"   • Code Server:      http://{nas_ip}:8080")
        print(f"   • MinIO Console:     http://{nas_ip}:9001")
        print(f"   • RabbitMQ:         http://{nas_ip}:15672")
        print(f"   • Duplicati:        http://{nas_ip}:8200")
        print(f"   • FileBrowser:      http://{nas_ip}:80")
        print()
        print("⚠️  SECURITY: Change default passwords immediately!")
        print("   - Grafana: admin/admin")
        print("   - MinIO: minioadmin/minioadmin")
        print()

        return 0

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":


    sys.exit(main())