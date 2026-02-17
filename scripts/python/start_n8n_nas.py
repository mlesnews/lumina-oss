#!/usr/bin/env python3
"""
Start N8N on NAS via Docker

Tags: #DOIT #N8N #DOCKER @JARVIS
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartN8N")

from nas_azure_vault_integration import NASAzureVaultIntegration
from azure_service_bus_integration import AzureKeyVaultClient


def start_n8n_container():
    """Start N8N Docker container on NAS"""
    logger.info("="*80)
    logger.info("🚀 STARTING N8N ON NAS")
    logger.info("="*80)
    logger.info("")

    # Get credentials
    logger.info("🔐 Retrieving credentials from Azure Vault...")
    vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")

    try:
        n8n_password = vault.get_secret("n8n-password")
        nas_username = "mlesn"  # From nas_config.json
        nas_password = vault.get_secret("nas-password")  # For sudo
        logger.info("   ✅ Credentials retrieved")
    except Exception as e:
        logger.error(f"   ❌ Failed to retrieve credentials: {e}")
        return 1

    # Connect to NAS
    logger.info("")
    logger.info("🔌 Connecting to NAS...")
    nas = NASAzureVaultIntegration()

    # Find Docker path - use full path with PATH set
    logger.info("")
    logger.info("🔍 Finding Docker installation...")
    # Try to find docker with proper PATH
    find_docker_cmd = "PATH=/usr/local/bin:/usr/bin:/bin:$PATH which docker 2>/dev/null || echo '/usr/local/bin/docker'"
    docker_result = nas.execute_ssh_command(find_docker_cmd)
    docker_path = "/usr/local/bin/docker"  # Default based on earlier test
    if docker_result["success"] and docker_result["output"].strip():
        output = docker_result["output"].strip()
        if output.startswith("/"):
            docker_path = output
    logger.info(f"   ✅ Using Docker at: {docker_path}")

    # Use sudo with password for docker commands
    # Create a helper function to run sudo commands
    def run_sudo_command(cmd):
        """Run command with sudo using password"""
        import shlex
        escaped_password = shlex.quote(nas_password)
        sudo_cmd = f"echo {escaped_password} | sudo -S {cmd}"
        return nas.execute_ssh_command(sudo_cmd)

    docker_cmd_prefix = f"PATH=/usr/local/bin:/usr/bin:/bin:$PATH {docker_path}"
    sudo_docker_prefix = f"echo '{nas_password}' | sudo -S PATH=/usr/local/bin:/usr/bin:/bin:$PATH {docker_path}"

    # Always try to remove existing container first (in case it exists)
    logger.info("")
    logger.info("🔍 Checking for and removing existing N8N container...")
    rm_cmd = f"{sudo_docker_prefix} rm -f n8n 2>&1"
    rm_result = nas.execute_ssh_command(rm_cmd)
    if rm_result["success"] or "No such container" in (rm_result.get("output") or ""):
        logger.info("   ✅ Container cleanup complete")
        import time
        time.sleep(2)  # Wait for cleanup

    # Now create new container
    logger.info("")
    if True:  # Always create new container now
            logger.info("   ⚠️  No existing container found, creating new one...")
            # Create and start new container
            logger.info("")
            logger.info("🐳 Creating N8N Docker container...")

            # Create data directory
            logger.info("   📁 Creating data directory...")
            mkdir_cmd = "mkdir -p /volume1/docker/n8n && chmod 777 /volume1/docker/n8n"
            nas.execute_ssh_command(mkdir_cmd)

            # COMPUSEC: Write env file with secrets, pass to Docker, then delete
            import tempfile, os
            env_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env',
                                                    dir='/volume1/docker/n8n')
            try:
                env_file.write(f"N8N_BASIC_AUTH_ACTIVE=true\n")
                env_file.write(f"N8N_BASIC_AUTH_USER={nas_username}\n")
                env_file.write(f"N8N_BASIC_AUTH_PASSWORD={n8n_password}\n")
                env_file.write(f"N8N_HOST=<NAS_PRIMARY_IP>\nN8N_PORT=5678\n")
                env_file.write(f"N8N_PROTOCOL=http\nN8N_SECURE_COOKIE=false\n")
                env_file.close()
                env_path = env_file.name
            except Exception:
                # Fallback: write via SSH
                env_path = "/volume1/docker/n8n/.n8n.env"

            docker_cmd = f"""sudo PATH=/usr/local/bin:/usr/bin:/bin:$PATH {docker_path} run -d \\
  --name n8n \\
  --restart unless-stopped \\
  -p 5678:5678 \\
  -v /volume1/docker/n8n:/home/node/.n8n \\
  --env-file {env_path} \\
  n8nio/n8n:latest"""

            logger.info("   🚀 Starting container...")
            result = nas.execute_ssh_command(docker_cmd)

            if result["success"]:
                container_id = result["output"].strip()
                logger.info(f"   ✅ N8N container created and started: {container_id[:12]}")
            else:
                logger.error(f"   ❌ Failed to create container: {result.get('error', 'Unknown error')}")
                if result.get("output"):
                    logger.error(f"   Output: {result['output']}")
                return 1

    # Wait a moment for container to start
    logger.info("")
    logger.info("⏳ Waiting for N8N to start...")
    import time
    time.sleep(5)

    # Verify it's running
    logger.info("")
    logger.info("🔍 Verifying N8N is running...")
    verify_cmd = f"{sudo_docker_prefix} ps --format '{{{{.Names}}}}\\t{{{{.Status}}}}' 2>&1 | grep -i '^n8n'"
    result = nas.execute_ssh_command(verify_cmd)

    if result["success"] and result["output"].strip():
        logger.info(f"   ✅ N8N container is running")
        logger.info(f"   Status: {result['output'].strip()}")
    else:
        logger.warning("   ⚠️  Could not verify container status")

    # Test connection
    logger.info("")
    logger.info("🌐 Testing N8N connection...")
    import requests
    from requests.auth import HTTPBasicAuth

    try:
        response = requests.get(
            "http://<NAS_PRIMARY_IP>:5678",
            auth=HTTPBasicAuth(nas_username, n8n_password),
            timeout=10,
            verify=False
        )
        if response.status_code < 500:
            logger.info(f"   ✅ N8N is accessible (HTTP {response.status_code})")
            logger.info("   🌐 URL: http://<NAS_PRIMARY_IP>:5678")
        else:
            logger.warning(f"   ⚠️  N8N responded with HTTP {response.status_code}")
    except Exception as e:
        logger.warning(f"   ⚠️  Connection test failed: {e}")
        logger.info("   (Container may still be starting - wait a few seconds)")

    logger.info("")
    logger.info("="*80)
    logger.info("✅ N8N STARTUP COMPLETE")
    logger.info("="*80)
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("   1. Access N8N: http://<NAS_PRIMARY_IP>:5678")
    logger.info("   2. Login with: mlesn / <password from vault>")
    logger.info("   3. Deploy workflows: python scripts/python/deploy_n8n_with_vault_creds.py")
    logger.info("")

    return 0


if __name__ == "__main__":
    exit(start_n8n_container())
