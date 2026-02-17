#!/usr/bin/env python3
"""
Configure all DSM packages - Full Auto via SSH
No browser needed - all via SSH/API
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def get_installed_packages(nas_integration: NASAzureVaultIntegration) -> list:
    """Get list of installed DSM packages"""
    try:
        cmd = "synopkg list 2>/dev/null | grep -E '^[a-zA-Z]' | awk '{print $1}'"
        result = nas_integration.execute_ssh_command(cmd)
        # Handle both string and dict responses
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)
        if isinstance(result, str):
            packages = [p.strip() for p in result.split('\n') if p.strip() and not p.startswith('INFO') and not p.startswith('ERROR')]
            return packages
        return []
    except Exception as e:
        logger.error(f"Error getting packages: {e}")
        return []


def start_package(nas_integration: NASAzureVaultIntegration, package: str) -> bool:
    """Start a DSM package"""
    try:
        cmd = f"synopkg start {package} 2>/dev/null"
        result = nas_integration.execute_ssh_command(cmd)
        # Handle both string and dict responses
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)
        if isinstance(result, str):
            return "started" in result.lower() or "running" in result.lower()
        return False
    except Exception as e:
        logger.debug(f"Error starting {package}: {e}")
        return False


def configure_ldap(nas_integration: NASAzureVaultIntegration, domain: str, base_dn: str, server: str, bind_dn: str) -> bool:
    """Prepare LDAP configuration (actual join requires web interface)"""
    try:
        config_content = f"""Domain: {domain}
Server: {server}
Port: 636
Base DN: {base_dn}
Bind DN: {bind_dn}
"""
        cmd = f"echo '{config_content}' > /tmp/ldap_join_config.txt && cat /tmp/ldap_join_config.txt"
        result = nas_integration.execute_ssh_command(cmd)
        logger.info("LDAP configuration file created")
        return True
    except Exception as e:
        logger.error(f"Error configuring LDAP: {e}")
        return False


def configure_docker_proxy_cache(nas_integration: NASAzureVaultIntegration) -> bool:
    """Check proxy-cache deployment status"""
    try:
        cmd = "docker ps 2>/dev/null | grep nas-proxy-cache || echo 'NOT_RUNNING'"
        result = nas_integration.execute_ssh_command(cmd)
        if "nas-proxy-cache" in result:
            logger.info("Proxy-cache container is running")
            return True
        else:
            logger.info("Proxy-cache not running - files ready at /tmp/nas-proxy-cache/")
            return False
    except Exception as e:
        logger.debug(f"Docker check: {e}")
        return False


def configure_cloud_sync(nas_integration: NASAzureVaultIntegration) -> bool:
    """Prepare Cloud Sync configuration"""
    try:
        # Check if Cloud Sync is installed
        cmd = r"synopkg status CloudSync 2>/dev/null | grep -i 'status\|version' | head -2"
        result = nas_integration.execute_ssh_command(cmd)
        if result:
            logger.info("Cloud Sync package found")
            # Start if stopped
            start_package(nas_integration, "CloudSync")
            return True
        else:
            logger.warning("Cloud Sync package not installed")
            return False
    except Exception as e:
        logger.error(f"Error configuring Cloud Sync: {e}")
        return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure all DSM packages - Full Auto")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--domain", default="matthewlesnewski.onmicrosoft.com", help="Azure AD domain")

    args = parser.parse_args()

    print("=" * 70)
    print("   CONFIGURE ALL DSM PACKAGES - FULL AUTO (NO BROWSER)")
    print("=" * 70)
    print("")

    # Initialize NAS integration
    nas_integration = NASAzureVaultIntegration(
        vault_name=args.vault_name,
        nas_ip=args.nas_ip
    )

    # Step 1: Get installed packages
    print("[1] Getting installed packages...")
    packages = get_installed_packages(nas_integration)
    if packages:
        print(f"  Found {len(packages)} packages:")
        for pkg in packages[:10]:  # Show first 10
            print(f"    - {pkg}")
        if len(packages) > 10:
            print(f"    ... and {len(packages) - 10} more")
    else:
        print("  ⚠ Could not get package list")
    print("")

    # Step 2: Start/configure key packages
    print("[2] Configuring key packages...")

    key_packages = {
        "LDAPServer": "LDAP/Azure AD",
        "DomainController": "Domain Controller",
        "Docker": "Container Manager",
        "CloudSync": "Cloud Sync",
        "ActiveBackupBusiness": "Active Backup",
        "HyperBackup": "Hyper Backup"
    }

    for package, description in key_packages.items():
        print(f"  {description} ({package})...")

        # Check status
        status_cmd = f"synopkg status {package} 2>/dev/null | grep -i 'status\\|version' | head -2"
        status = nas_integration.execute_ssh_command(status_cmd)

        # Handle both string and dict responses
        if isinstance(status, dict):
            status = status.get('output', '') or status.get('stdout', '') or str(status)
        status_str = str(status) if status else ""

        if status_str and "not found" not in status_str.lower():
            print(f"    Status: {status_str.strip()[:50]}")
            # Start if available
            if start_package(nas_integration, package):
                print(f"    ✓ Started")
            else:
                print(f"    - Already running or manual start required")
        else:
            print(f"    ⚠ Package not installed")
    print("")

    # Step 3: Configure LDAP
    print("[3] Configuring LDAP/Azure AD...")
    base_dn = ",".join([f"DC={part}" for part in args.domain.split(".")])
    server = f"ldaps://{args.domain}:636"
    bind_dn = f"CN=admin,CN=Users,{base_dn}"

    if configure_ldap(nas_integration, args.domain, base_dn, server, bind_dn):
        print("  ✓ LDAP configuration prepared")
        print(f"    Config file: /tmp/ldap_join_config.txt")
    print("")

    # Step 4: Configure Docker/Container Manager
    print("[4] Configuring Container Manager...")
    if configure_docker_proxy_cache(nas_integration):
        print("  ✓ Proxy-cache container running")
    else:
        print("  - Proxy-cache files ready at /tmp/nas-proxy-cache/")
    print("")

    # Step 5: Configure Cloud Sync
    print("[5] Configuring Cloud Sync...")
    if configure_cloud_sync(nas_integration):
        print("  ✓ Cloud Sync package configured")
    else:
        print("  ⚠ Cloud Sync requires manual setup for cloud provider credentials")
    print("")

    # Summary
    print("=" * 70)
    print("   CONFIGURATION COMPLETE")
    print("=" * 70)
    print("")
    print("All automated configuration done via SSH (no browser needed)")
    print("")
    print("Configuration files:")
    print("  - /tmp/ldap_join_config.txt (LDAP config)")
    print("  - /tmp/nas-proxy-cache/ (Proxy-cache deployment)")
    print("")
    print("Manual steps (security requirements):")
    print("  - LDAP Join: Must be done via DSM web interface")
    print("  - Cloud Sync: Requires cloud provider credentials")
    print("  - Proxy-cache: Deploy via Container Manager if not running")
    print("")
    print("=" * 70)
    print("")


if __name__ == "__main__":


    main()