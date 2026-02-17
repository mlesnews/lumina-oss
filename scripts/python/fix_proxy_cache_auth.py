#!/usr/bin/env python3
"""
Fix Proxy-Cache Authentication Caching Configuration
Updates nginx.conf on NAS with authentication caching
#JARVIS #PROXY-CACHE #AUTHENTICATION #CACHE #FIX
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_local_nginx_conf() -> str:
    try:
        """Read the updated nginx.conf from local filesystem"""
        nginx_conf_path = project_root / "scripts" / "docker" / "nas-proxy-cache" / "nginx.conf"
        with open(nginx_conf_path, "r", encoding="utf-8") as f:
            return f.read()


    except Exception as e:
        logger.error(f"Error in read_local_nginx_conf: {e}", exc_info=True)
        raise
def update_nas_nginx_conf(nas_integration: NASAzureVaultIntegration, nginx_conf: str) -> bool:
    """Update nginx.conf on NAS with authentication caching"""
    try:
        # Create directory if it doesn't exist
        nas_integration.execute_ssh_command("mkdir -p /tmp/nas-proxy-cache")

        # Save nginx.conf to NAS
        # Escape the content for shell
        escaped_conf = nginx_conf.replace("'", "'\"'\"'")
        cmd = f"cat > /tmp/nas-proxy-cache/nginx.conf << 'NGINX_EOF'\n{nginx_conf}\nNGINX_EOF"
        result = nas_integration.execute_ssh_command(cmd)

        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        # Verify file was created
        verify_cmd = "test -f /tmp/nas-proxy-cache/nginx.conf && echo 'EXISTS' || echo 'NOT_EXISTS'"
        verify_result = nas_integration.execute_ssh_command(verify_cmd)
        if isinstance(verify_result, dict):
            verify_result = verify_result.get('output', '') or verify_result.get('stdout', '') or str(verify_result)

        if 'EXISTS' in str(verify_result):
            logger.info("✓ nginx.conf updated on NAS with authentication caching")
            return True
        else:
            logger.error("✗ Failed to verify nginx.conf on NAS")
            return False

    except Exception as e:
        logger.error(f"Failed to update nginx.conf on NAS: {e}")
        return False


def check_container_status(nas_integration: NASAzureVaultIntegration) -> dict:
    """Check proxy-cache container status"""
    result = nas_integration.execute_ssh_command("docker ps -a 2>/dev/null | grep nas-proxy-cache || echo 'NOT_FOUND'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)

    status = {
        "running": False,
        "exists": False
    }

    if 'nas-proxy-cache' in str(result) and 'NOT_FOUND' not in str(result):
        status["exists"] = True
        if 'Up' in str(result) or 'running' in str(result).lower():
            status["running"] = True

    return status


def restart_container(nas_integration: NASAzureVaultIntegration) -> bool:
    """Restart proxy-cache container to apply new configuration"""
    try:
        # Check if container exists
        status = check_container_status(nas_integration)

        if not status["exists"]:
            logger.warning("Container not found. Please deploy it first via Container Manager.")
            return False

        # Stop container
        logger.info("Stopping container...")
        nas_integration.execute_ssh_command("docker stop nas-proxy-cache 2>/dev/null || true")

        # Start container (will use updated config from volume mount)
        logger.info("Starting container...")
        result = nas_integration.execute_ssh_command("docker start nas-proxy-cache 2>/dev/null || echo 'FAILED'")

        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        if 'FAILED' not in str(result):
            logger.info("✓ Container restarted")
            return True
        else:
            logger.warning("Container restart may require manual intervention via Container Manager")
            return False

    except Exception as e:
        logger.error(f"Failed to restart container: {e}")
        return False


def main():
    print("=" * 70)
    print("   FIX PROXY-CACHE AUTHENTICATION CACHING")
    print("=" * 70)
    print("")

    nas_integration = NASAzureVaultIntegration(vault_name="jarvis-lumina", nas_ip="<NAS_PRIMARY_IP>")

    # Read updated nginx.conf
    logger.info("Reading updated nginx.conf...")
    nginx_conf = read_local_nginx_conf()

    # Update on NAS
    logger.info("Updating nginx.conf on NAS...")
    if not update_nas_nginx_conf(nas_integration, nginx_conf):
        print("✗ Failed to update nginx.conf")
        return 1

    print("")
    print("✓ Authentication caching configuration updated")
    print("")
    print("Next steps:")
    print("  1. If container is running, restart it via Container Manager")
    print("  2. Or run: docker restart nas-proxy-cache (if accessible)")
    print("  3. Verify: docker logs nas-proxy-cache")
    print("")

    # Check container status
    status = check_container_status(nas_integration)
    print(f"Container Status: {'Running' if status['running'] else 'Stopped' if status['exists'] else 'Not Found'}")

    if status["exists"] and not status["running"]:
        print("")
        print("⚠️  Container exists but is not running.")
        print("   Start it via Container Manager to apply new configuration.")

    return 0


if __name__ == "__main__":


    sys.exit(main())