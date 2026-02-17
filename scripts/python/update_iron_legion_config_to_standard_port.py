#!/usr/bin/env python3
"""
Update Iron Legion Cluster Config to Use Standard Ollama Port

Since the configured ports (3000, 11437) are inoperative but standard Ollama port (11434) is available,
this script updates the cluster configuration to use the standard port.
"""

import json
import sys
from pathlib import Path
import logging
logger = logging.getLogger("update_iron_legion_config_to_standard_port")


# Path to Iron Legion config (in <COMPANY> workspace)
config_paths = [
    Path(r"C:\Users\mlesn\Dropbox\my_projects\<COMPANY>-financial-services_llc-env\llm_cluster\configs\iron_legion_cluster.json"),
    Path(r"C:\Users\mlesn\Dropbox\my_projects\.lumina\config\iron_legion_cluster.json"),
]

def update_config_to_standard_port(config_path: Path):
    """Update cluster config to use standard Ollama port 11434"""
    if not config_path.exists():
        print(f"⚠️ Config file not found: {config_path}")
        return False

    try:
        # Read current config
        with open(config_path, 'r') as f:
            config = json.load(f)

        print(f"📄 Current config endpoints:")
        print(f"   Primary: {config.get('endpoints', {}).get('primary', {}).get('url', 'N/A')}")
        print(f"   Fallback: {config.get('endpoints', {}).get('fallback', {}).get('url', 'N/A')}")

        # Update primary endpoint to standard Ollama port
        if 'endpoints' in config and 'primary' in config['endpoints']:
            config['endpoints']['primary']['url'] = "http://localhost:11434"
            config['endpoints']['primary']['type'] = "ollama"

        # Update fallback endpoint to standard Ollama port
        if 'endpoints' in config and 'fallback' in config['endpoints']:
            config['endpoints']['fallback']['url'] = "http://localhost:11434"
            config['endpoints']['fallback']['type'] = "ollama"

        # Update health check endpoints
        if 'health_check' in config and 'endpoints' in config['health_check']:
            config['health_check']['endpoints'] = [
                "http://localhost:11434/api/tags"
            ]

        # Backup original config
        backup_path = config_path.with_suffix('.json.backup')
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Backup saved to: {backup_path}")

        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Updated config endpoints:")
        print(f"   Primary: {config['endpoints']['primary']['url']}")
        print(f"   Fallback: {config['endpoints']['fallback']['url']}")
        print(f"   Health Check: {config['health_check']['endpoints'][0]}")

        return True

    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False


def main():
    try:
        """Update all found Iron Legion configs"""
        print("🔧 UPDATING IRON LEGION CLUSTER CONFIG")
        print("=" * 50)
        print("Updating endpoints to use standard Ollama port: 11434\n")

        updated = False
        for config_path in config_paths:
            if config_path.exists():
                print(f"\n📝 Updating: {config_path}")
                print("-" * 50)
                if update_config_to_standard_port(config_path):
                    updated = True
                    print(f"✅ Successfully updated: {config_path}\n")
                else:
                    print(f"❌ Failed to update: {config_path}\n")

        if not updated:
            print("\n⚠️ No config files found or updated.")
            print("Please ensure the Iron Legion cluster config exists in one of these locations:")
            for path in config_paths:
                print(f"  • {path}")

        print("\n" + "=" * 50)
        print("Iron Legion Config Update Complete")
        return 0 if updated else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())