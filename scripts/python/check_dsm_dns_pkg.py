import os
import sys
from pathlib import Path

# Add scripts/python to path
LUMINA_ROOT = Path(os.environ.get("LUMINA_ROOT", str(Path.home() / "lumina")))
script_dir = LUMINA_ROOT / "scripts" / "python"
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration

def check_pkg():
    integration = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
    # List package directories
    print("\nListing /var/packages directories...")
    result_ls = integration.execute_ssh_command("ls -1 /var/packages")
    if result_ls['success']:
        pkgs = result_ls['output'].splitlines()
        print(f"  Total package directories: {len(pkgs)}")
        dns_pkgs = [p for p in pkgs if 'dns' in p.lower()]
        if dns_pkgs:
            print(f"  ✅ DNS-related packages found in /var/packages: {dns_pkgs}")
        else:
            print("  ❌ No DNS-related packages found in /var/packages.")
    else:
        print(f"  Error listing /var/packages: {result_ls.get('error')}")

if __name__ == "__main__":
    check_pkg()
