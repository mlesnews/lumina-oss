#!/usr/bin/env python3
"""
Setup Homelab Audit MariaDB Database

Quick setup script that uses existing JARVIS MariaDB connection manager
to create schema and import initial audit.

Tags: #HOMELAB #AUDIT #MARIADB #SETUP @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.homelab_audit_mariadb_import import HomelabAuditMariaDBImporter
from scripts.python.jarvis_mariadb_nas_connection import JARVISMariaDBNASConnection


def main():
    """Setup homelab audit database"""
    print("=" * 80)
    print("HOMELAB AUDIT MARIADB SETUP")
    print("=" * 80)

    # Get connection manager
    manager = JARVISMariaDBNASConnection()

    # Database name
    database = "homelab_audit"

    # Get connection params
    print("\n1. Getting MariaDB connection parameters...")
    try:
        params = manager.get_connection_params(database, username="dbadmin")
        print(f"   Host: {params['host']}:{params['port']}")
        print(f"   Database: {database}")
        print(f"   User: {params['user']}")
    except Exception as e:
        print(f"   ❌ Failed to get connection params: {e}")
        return False

    # Create importer
    print("\n2. Creating importer...")
    importer = HomelabAuditMariaDBImporter(
        host=params["host"],
        user=params["user"],
        password=params["password"],
        database=database,
        port=params["port"],
    )

    # Create schema
    print("\n3. Creating database schema...")
    if importer.connect():
        if importer.create_schema():
            print("   ✅ Schema created successfully")
        else:
            print("   ❌ Failed to create schema")
            return False
    else:
        print("   ❌ Failed to connect to MariaDB")
        return False

    # Find latest audit file
    print("\n4. Finding latest audit file...")
    audit_dir = project_root / "data" / "homelab_audit"
    audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)

    if not audit_files:
        print("   ⚠️  No audit files found")
        return False

    latest_audit = audit_files[0]
    print(f"   Found: {latest_audit.name}")

    # Import audit
    print("\n5. Importing audit data...")
    with open(latest_audit, encoding="utf-8") as f:
        audit_data = json.load(f)

    if importer.import_audit(audit_data):
        print("   ✅ Audit imported successfully")
        print(f"   Audit ID: {audit_data['audit_id']}")
        print(f"   Devices: {len(audit_data.get('devices', []))}")
        print(
            f"   Total Features: {sum(len(d.get('features', [])) for d in audit_data.get('devices', []))}"
        )
    else:
        print("   ❌ Failed to import audit")
        return False

    # Export to Holocron format
    print("\n6. Exporting to Holocron format...")
    holocron = importer.export_to_holocron(audit_id=audit_data["audit_id"])

    if holocron:
        holocron_file = audit_dir / f"holocron_{audit_data['audit_id']}.json"
        with open(holocron_file, "w", encoding="utf-8") as f:
            json.dump(holocron, f, indent=2, ensure_ascii=False, default=str)
        print(f"   ✅ Holocron exported: {holocron_file.name}")
        print(f"   Holocron ID: {holocron['holocron_metadata']['holocron_id']}")
    else:
        print("   ⚠️  Failed to export Holocron")

    importer.close()

    print("\n" + "=" * 80)
    print("✅ SETUP COMPLETE")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
    success = main()
    sys.exit(0 if success else 1)
    success = main()
    sys.exit(0 if success else 1)
    success = main()
    sys.exit(0 if success else 1)
