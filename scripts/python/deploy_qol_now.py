#!/usr/bin/env python3
"""
Immediate QOL Tools Deployment
Uses paramiko if available, otherwise provides exact commands
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_azure_vault_integration import NASAzureVaultIntegration
from ssh_connection_helper import connect_to_nas

def main():
    nas_ip = "<NAS_PRIMARY_IP>"
    nas_user = "backupadm"
    deploy_dir = project_root / "containerization" / "services" / "nas-qol-tools"

    print("🚀 Deploying QOL Tools to NAS...")
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

    # Try root access first (if sudoless root access is available)
    # Fallback to regular user
    try_usernames = ["root", username]

    print(f"✅ Credentials loaded for {username}")
    print()

    # Try paramiko
    try:
        import paramiko
        from scp import SCPClient

        print("📤 Copying files to NAS via SSH...")

        # Try connecting - first try root, then regular user
        ssh = None
        connected_user = None

        for try_user in try_usernames:
            try:
                print(f"   Trying connection as {try_user}...")
                ssh = connect_to_nas(nas_ip, try_user, password, timeout=10)
                connected_user = try_user
                print(f"   ✅ Connected as {connected_user} (using SSH key)")
                break
            except paramiko.AuthenticationException:
                print(f"   ⚠️  Authentication failed for {try_user}")
                if ssh:
                    ssh.close()
                continue

        if not ssh or not connected_user:
            print(f"   ❌ Failed to connect with any user")
            return 1

        # Create directory
        print("   Creating remote directory...")
        stdin, stdout, stderr = ssh.exec_command("mkdir -p /volume1/docker/nas-qol-tools")
        stdout.channel.recv_exit_status()

        # Copy docker-compose.yml
        print("   Copying docker-compose.yml...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(str(deploy_dir / "docker-compose.yml"), "/volume1/docker/nas-qol-tools/docker-compose.yml")

        print("   ✅ Files copied")
        print()

        # Deploy
        print("🚀 Deploying containers...")

        # Find Docker - Synology uses Container Manager which may have docker in different locations
        print("   Locating Docker...")
        find_docker = "which docker 2>/dev/null || find /usr/local/bin /usr/bin /var/packages/Docker/target/usr/bin -name docker -type f 2>/dev/null | head -1"
        stdin, stdout, stderr = ssh.exec_command(find_docker)
        docker_path = stdout.read().decode('utf-8').strip()
        docker_errors = stderr.read().decode('utf-8')

        if docker_path and "/" in docker_path:
            print(f"   ✅ Found Docker at: {docker_path}")
            docker_cmd = docker_path
        else:
            # Try Synology Container Manager path
            syno_docker = "/var/packages/Docker/target/usr/bin/docker"
            test_syno = f"test -x {syno_docker} && echo {syno_docker} || echo ''"
            stdin, stdout, stderr = ssh.exec_command(test_syno)
            syno_path = stdout.read().decode('utf-8').strip()

            if syno_path:
                print(f"   ✅ Using Synology Docker: {syno_path}")
                docker_cmd = syno_path
            else:
                print("   ⚠️  Docker not found in standard locations")
                print("   Trying Container Manager API approach...")
                # Use Synology's synoservice or Container Manager API
                docker_cmd = "/usr/local/bin/docker"  # Fallback

        # Check if compose plugin is available
        print(f"   Testing: {docker_cmd} compose version")
        test_compose = f"{docker_cmd} compose version 2>&1"
        stdin, stdout, stderr = ssh.exec_command(test_compose)
        compose_output = stdout.read().decode('utf-8')
        compose_errors = stderr.read().decode('utf-8')

        if "compose" in compose_output.lower() or "version" in compose_output.lower():
            compose_cmd = f"{docker_cmd} compose"
            print(f"   ✅ Using: {compose_cmd}")
        else:
            # Try docker-compose standalone
            find_compose = "which docker-compose 2>/dev/null || find /usr/local/bin /usr/bin -name docker-compose -type f 2>/dev/null | head -1"
            stdin, stdout, stderr = ssh.exec_command(find_compose)
            compose_path = stdout.read().decode('utf-8').strip()

            if compose_path:
                compose_cmd = compose_path
                print(f"   ✅ Using: {compose_cmd}")
            else:
                compose_cmd = f"{docker_cmd} compose"  # Fallback
                print(f"   ⚠️  Using fallback: {compose_cmd}")

        # Deploy commands
        deploy_dir = "/volume1/docker/nas-qol-tools"

        # Check if user is in docker group, if not try to add them
        print("   Checking Docker group membership...")
        check_group = f"groups {connected_user} | grep -q docker && echo 'yes' || echo 'no'"
        stdin, stdout, stderr = ssh.exec_command(check_group)
        in_docker_group = "yes" in stdout.read().decode('utf-8')

        if not in_docker_group:
            print("   ⚠️  User not in docker group, attempting to add...")
            # Try adding user to docker group (requires root/sudo)
            add_to_group = f"sudo usermod -aG docker {connected_user} 2>&1 || echo 'FAILED'"
            stdin, stdout, stderr = ssh.exec_command(add_to_group)
            add_result = stdout.read().decode('utf-8')
            if "FAILED" not in add_result:
                print("   ✅ Added to docker group (may require re-login)")
                # Try using newgrp to activate group membership
                compose_cmd = f"newgrp docker <<EOF\n{compose_cmd}\nEOF"
            else:
                print("   ⚠️  Could not add to docker group, trying sudo...")
                # Fallback: try sudo
                compose_cmd = f"sudo {compose_cmd}"
        else:
            print("   ✅ User in docker group")
            compose_cmd = compose_cmd

        commands = [
            f"cd {deploy_dir} && pwd",
            f"cd {deploy_dir} && {compose_cmd} pull",
            f"cd {deploy_dir} && {compose_cmd} up -d",
            f"cd {deploy_dir} && {compose_cmd} ps"
        ]

        for cmd in commands:
            print(f"   Running: {cmd.split('&&')[-1].strip()}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()

            output = stdout.read().decode('utf-8')
            errors = stderr.read().decode('utf-8')

            if exit_status == 0:
                if output:
                    lines = output.split('\n')[:15]
                    for line in lines:
                        if line.strip() and not line.startswith('WARNING'):
                            print(f"      {line}")
            else:
                print(f"      ❌ Exit code: {exit_status}")
                if errors:
                    error_lines = errors.split('\n')[:5]
                    for err in error_lines:
                        if err.strip():
                            print(f"      Error: {err[:100]}")
                if output:
                    output_lines = output.split('\n')[:5]
                    for out in output_lines:
                        if out.strip() and "error" in out.lower():
                            print(f"      {out[:100]}")

        ssh.close()
        print()
        print("=" * 70)
        print("✅ Deployment completed!")
        print()
        print("Access your QOL tools:")
        print(f"   • Portainer: http://{nas_ip}:9000")
        print(f"   • Uptime Kuma: http://{nas_ip}:3001")
        print(f"   • Grafana: http://{nas_ip}:3000")
        print(f"   • Prometheus: http://{nas_ip}:9090")
        print()
        return 0

    except ImportError:
        print("⚠️  paramiko/scp not installed")
        print("   Installing paramiko and scp...")

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko", "scp", "-q"])
            print("   ✅ Installed. Retrying...")
            print()
            # Retry after installation
            return main()
        except Exception as e:
            print(f"   ❌ Installation failed: {e}")
            print()
            print("Manual deployment required:")
            print(f"   1. scp -r {deploy_dir} {username}@{nas_ip}:/volume1/docker/")
            print(f"   2. ssh {username}@{nas_ip}")
            print(f"   3. cd /volume1/docker/nas-qol-tools")
            print(f"   4. docker-compose up -d")
            return 1

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print()
        print("Manual deployment:")
        print(f"   1. scp -r {deploy_dir} {username}@{nas_ip}:/volume1/docker/")
        print(f"   2. ssh {username}@{nas_ip}")
        print(f"   3. cd /volume1/docker/nas-qol-tools")
        print(f"   4. docker-compose up -d")
        return 1

if __name__ == "__main__":


    sys.exit(main())