#!/usr/bin/env python3
"""
NAS Disaster Recovery Check
Checks status of Active Backup for Business and Hyper Backup via SSH
"""

import json
import sys
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("nas_disaster_recovery_check")


# Add current directory to path to find nas_azure_vault_integration
sys.path.append(str(Path(__file__).parent))

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    print(
        "❌ Could not import NASAzureVaultIntegration. Make sure it is in the same directory."
    )
    sys.exit(1)

# Load Config
CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "config" / "lumina_nas_ssh_config.json"
)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def load_config():
    try:
        if not CONFIG_PATH.exists():
            print(f"❌ Config file not found at {CONFIG_PATH}")
            sys.exit(1)
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)


    except Exception as e:
        logger.error(f"Error in load_config: {e}", exc_info=True)
        raise
def check_disaster_recovery_status():
    config = load_config()
    dr_config = config.get("operations", {}).get("disaster_recovery", {})

    if not dr_config:
        print("❌ No Disaster Recovery configuration found.")
        return

    nas_ip = config["nas"]["host"]

    print(f"🔍 Checking Disaster Recovery Status on NAS ({nas_ip})...")

    # Initialize integration (Vault name defaults to jarvis-lumina if not set)
    integration = NASAzureVaultIntegration(nas_ip=nas_ip)

    # Check Active Backup for Business
    abb_config = dr_config.get("active_backup_for_business", {})
    if abb_config.get("enabled"):
        cmd = abb_config["service_command"]
        print("   Checking Active Backup for Business...")
        result = integration.execute_ssh_command(cmd)

        if result["success"]:
            output = result["output"].strip()
            if "start/running" in output.lower():
                print("   ✅ Active Backup for Business is RUNNING.")
                print("      - Bare-metal recovery capability: ENABLED")
                print(
                    f"      - Target devices: {', '.join(abb_config.get('target_devices', []))}"
                )
            else:
                print("   ⚠️ Active Backup for Business is NOT running.")
                print(f"      Status: {output}")
        else:
            print("   ❌ Failed to check Active Backup for Business.")
            print(f"      Error: {result.get('error')}")

    # Check Hyper Backup
    hb_config = dr_config.get("hyper_backup", {})
    if hb_config.get("enabled"):
        cmd = hb_config["service_command"]
        print("   Checking Hyper Backup...")
        result = integration.execute_ssh_command(cmd)

        if result["success"]:
            output = result["output"].strip()
            if "start/running" in output.lower():
                print("   ✅ Hyper Backup is RUNNING.")
                print("      - NAS Data Backup: ACTIVE")
                print(f"      - Destination: {hb_config.get('target_destination')}")
            else:
                print("   ⚠️ Hyper Backup is NOT running.")
                print(f"      Status: {output}")
        else:
            print("   ❌ Failed to check Hyper Backup.")
            print(f"      Error: {result.get('error')}")


if __name__ == "__main__":
    check_disaster_recovery_status()
