
import os
import sys
from pathlib import Path

# Add scripts/python to path
LUMINA_ROOT = Path(os.environ.get("LUMINA_ROOT", str(Path.home() / "lumina")))
script_dir = LUMINA_ROOT / "scripts" / "python"
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration
from nas_dns_manager import NASDNSManager

def check_dns():
    integration = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
    creds = integration.get_nas_credentials()
    if not creds:
        print("❌ Failed to get credentials from Azure Vault")
        return

    dns_manager = NASDNSManager(
        nas_host="<NAS_PRIMARY_IP>",
        username=creds["username"],
        password=creds["password"],
        verify_ssl=False  # Disable SSL verify for quick check
    )

    zones = dns_manager.get_dns_zones()
    print(f"\n📋 DNS Zones found on NAS:")
    for zone in zones:
        print(f"  - {zone.get('name')}")
        records = dns_manager.get_dns_records(zone.get('name'))
        for record in records:
            if "NPCS" in record.get('name').upper():
                print(f"    ✅ Found record: {record.get('name')} -> {record.get('value')}")

if __name__ == "__main__":
    check_dns()
