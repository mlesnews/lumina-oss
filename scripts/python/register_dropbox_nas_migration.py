"""
Register Dropbox to NAS Migration with LUMINA
Quick registration script for the migration system.
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from dropbox_nas_migration_integration import DropboxNASMigrationIntegration

def main():
    """Register migration system with LUMINA."""
    print("🔗 Registering Dropbox to NAS Migration with LUMINA...")

    integration = DropboxNASMigrationIntegration(project_root=project_root)
    result = integration.register_with_lumina()

    if result.get("success"):
        print(f"✅ Successfully registered: {result.get('registered')}")
        print(f"   Updated at: {result.get('updated_at')}")

        # Show status
        print("\n📊 Migration Status:")
        status = integration.get_migration_status()
        for key, value in status.items():
            if key != "last_check":
                status_icon = "✅" if value else "❌"
                print(f"   {status_icon} {key}: {value}")
    else:
        print(f"❌ Registration failed: {result.get('error')}")
        return 1

    return 0

if __name__ == "__main__":


    sys.exit(main())