#!/usr/bin/env python3
"""
Check Proxy-Cache Authentication Caching Configuration
Verifies if authentication caching is properly configured
#JARVIS #PROXY-CACHE #AUTHENTICATION #CACHE
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_proxy_cache_status(nas_integration: NASAzureVaultIntegration) -> dict:
    """Check proxy-cache container status"""
    status = {
        "running": False,
        "files_exist": False,
        "has_auth_cache": False
    }

    # Check if container is running
    result = nas_integration.execute_ssh_command("docker ps 2>/dev/null | grep nas-proxy-cache || echo 'NOT_RUNNING'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)

    if 'nas-proxy-cache' in str(result) and 'NOT_RUNNING' not in str(result):
        status["running"] = True

    # Check if files exist
    result = nas_integration.execute_ssh_command("test -d /tmp/nas-proxy-cache && echo 'EXISTS' || echo 'NOT_EXISTS'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)

    if 'EXISTS' in str(result):
        status["files_exist"] = True

    # Check nginx.conf for auth cache
    result = nas_integration.execute_ssh_command("grep -i 'auth.*cache\\|cache.*auth\\|proxy_cache.*auth' /tmp/nas-proxy-cache/nginx.conf 2>/dev/null || echo 'NO_AUTH_CACHE'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)

    if 'NO_AUTH_CACHE' not in str(result):
        status["has_auth_cache"] = True

    return status


def main():
    nas_integration = NASAzureVaultIntegration(vault_name="jarvis-lumina", nas_ip="<NAS_PRIMARY_IP>")

    print("=" * 70)
    print("   PROXY-CACHE AUTHENTICATION CACHING CHECK")
    print("=" * 70)
    print("")

    status = check_proxy_cache_status(nas_integration)

    print("Status:")
    print(f"  Container Running: {'✓' if status['running'] else '✗'}")
    print(f"  Files Exist: {'✓' if status['files_exist'] else '✗'}")
    print(f"  Auth Cache Configured: {'✓' if status['has_auth_cache'] else '✗'}")
    print("")

    if not status['has_auth_cache']:
        print("⚠️  Authentication caching NOT configured in proxy-cache")
        print("   Need to add LDAP authentication caching")

    return 0


if __name__ == "__main__":


    sys.exit(main())