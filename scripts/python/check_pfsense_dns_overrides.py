import os
import sys
from pathlib import Path

# Add scripts/python to path
LUMINA_ROOT = Path(os.environ.get("LUMINA_ROOT", str(Path.home() / "lumina")))
script_dir = LUMINA_ROOT / "scripts" / "python"
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from pfsense_azure_vault_integration import PFSenseAzureVaultIntegration

def check_pfsense_dns():
    integration = PFSenseAzureVaultIntegration(pfsense_ip="<NAS_IP>")
    # Test SSH connection to pfSense
    print("Testing SSH connection to pfSense...")
    result = integration.execute_ssh_command("grep -i 'domain-overrides' /var/unbound/unbound.conf")
    if result["success"]:
        print("\n✅ Found Domain Overrides on pfSense:")
        print(result["output"])
    else:
        print("\n❌ Could not find Domain Overrides or SSH failed.")
        if result.get("error"):
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    check_pfsense_dns()
