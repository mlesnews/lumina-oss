#!/usr/bin/env python3
"""Fix NAS containers - restart n8n and ollama."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from synology_container_manager import SynologyContainerManager
from nas_azure_vault_integration import NASAzureVaultIntegration


def main():
    print("=" * 60)
    print("Fixing NAS Containers")
    print("=" * 60)

    # Get credentials
    print("\nGetting credentials...")
    vault = NASAzureVaultIntegration()
    creds = vault.get_nas_credentials()
    if not creds:
        print("ERROR: Could not get credentials")
        return 1

    # Connect
    print(f"Connecting as {creds['username']}...")
    mgr = SynologyContainerManager()
    if not mgr.login(creds["username"], creds["password"]):
        print("ERROR: Could not login to NAS")
        return 1

    try:
        # List containers
        print("\n--- Current Containers ---")
        containers = mgr.list_containers()
        if not containers:
            print("No containers found!")
            return 1

        for c in containers:
            name = c.get("name", "unknown")
            status = c.get("status", "unknown")
            print(f"  {name}: {status}")

        # Restart n8n and ollama if not running
        target_containers = ["n8n", "ollama"]
        
        for target in target_containers:
            for c in containers:
                if c.get("name") == target:
                    container_id = c.get("id", c.get("name"))
                    status = c.get("status", "").lower()
                    
                    if "running" not in status:
                        print(f"\n--- Starting {target} ---")
                        if mgr.start_container(container_id):
                            print(f"  ✅ {target} started")
                        else:
                            print(f"  ❌ Failed to start {target}")
                    else:
                        print(f"\n--- {target} already running ---")
                    break

        # Final status
        print("\n--- Final Status ---")
        containers = mgr.list_containers()
        for c in containers:
            name = c.get("name", "unknown")
            status = c.get("status", "unknown")
            print(f"  {name}: {status}")

    finally:
        mgr.logout()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
