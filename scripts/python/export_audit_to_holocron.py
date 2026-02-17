#!/usr/bin/env python3
"""
Export Audit to Holocron Format

Exports homelab audit data to Holocron format for import into knowledge archive.

Tags: #HOMELAB #AUDIT #HOLOCRON #EXPORT @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def export_audit_to_holocron(audit_file: Path, output_file: Optional[Path] = None):
    """Export audit to Holocron format"""
    with open(audit_file, encoding="utf-8") as f:
        audit_data = json.load(f)

    # Build Holocron structure
    holocron = {
        "holocron_metadata": {
            "holocron_id": f"HOLOCRON-HOMELAB-AUDIT-{audit_data['audit_id']}",
            "title": f"Homelab Top-Down Audit - {audit_data['audit_timestamp']}",
            "classification": "homelab_audit",
            "created_at": audit_data["audit_timestamp"],
            "source": "homelab_topdown_audit",
            "version": audit_data.get("audit_version", "1.0.0"),
            "purpose": "Comprehensive audit of homelab infrastructure features, functions, and options",
            "maintained_by": "@JARVIS @LUMINA",
        },
        "audit_data": {
            "audit_id": audit_data["audit_id"],
            "audit_timestamp": audit_data["audit_timestamp"],
            "total_devices": len(audit_data.get("devices", [])),
            "total_features": sum(
                len(d.get("features", [])) for d in audit_data.get("devices", [])
            ),
            "total_complexity_score": audit_data.get("ecosystem_complexity", {}).get(
                "total_complexity_score", 0
            ),
            "ecosystem_complexity": audit_data.get("ecosystem_complexity", {}),
        },
        "devices": [],
    }

    # Process devices
    for device in audit_data.get("devices", []):
        device_holocron = {
            "device_id": device["device_id"],
            "device_name": device["device_name"],
            "device_type": device["device_type"],
            "hostname": device.get("hostname"),
            "ip_address": device.get("ip_address"),
            "mac_address": device.get("mac_address"),
            "operating_system": device.get("operating_system"),
            "os_version": device.get("os_version"),
            "os_architecture": device.get("os_architecture"),
            "manufacturer": device.get("manufacturer"),
            "model": device.get("model"),
            "complexity_score": device.get("complexity_score", 0),
            "features_summary": {"total": len(device.get("features", [])), "by_category": {}},
            "features": [],
        }

        # Count features by category
        from collections import Counter

        categories = Counter(f.get("category", "unknown") for f in device.get("features", []))
        device_holocron["features_summary"]["by_category"] = dict(categories)

        # Include top features (first 100 for Holocron)
        for feature in device.get("features", [])[:100]:
            device_holocron["features"].append(
                {
                    "feature_id": feature.get("feature_id"),
                    "name": feature.get("name"),
                    "category": feature.get("category"),
                    "subcategory": feature.get("subcategory"),
                    "value": feature.get("value"),
                    "enabled": feature.get("enabled", True),
                    "configurable": feature.get("configurable", False),
                }
            )

        # Add summary info
        device_holocron["services_count"] = len(device.get("services", []))
        device_holocron["network_interfaces_count"] = len(device.get("network_interfaces", []))
        device_holocron["storage_devices_count"] = len(device.get("storage_devices", []))
        device_holocron["config_files_count"] = len(device.get("configuration_files", []))

        holocron["devices"].append(device_holocron)

    # Add drift information if available
    if audit_data.get("drift_detected"):
        holocron["drift_summary"] = {
            "drift_events": len(audit_data["drift_detected"]),
            "devices_with_drift": [d.get("device_name") for d in audit_data["drift_detected"]],
        }

    # Determine output file
    if output_file is None:
        audit_dir = audit_file.parent
        output_file = audit_dir / f"holocron_{audit_data['audit_id']}.json"

    # Write Holocron file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(holocron, f, indent=2, ensure_ascii=False, default=str)

    print(f"✅ Holocron exported: {output_file.name}")
    print(f"   Holocron ID: {holocron['holocron_metadata']['holocron_id']}")
    print(f"   Devices: {holocron['audit_data']['total_devices']}")
    print(f"   Features: {holocron['audit_data']['total_features']}")

    return output_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Export audit to Holocron format")
    parser.add_argument("--audit-file", help="Specific audit file (default: latest)")
    parser.add_argument("--output", help="Output file (default: holocron_<audit_id>.json)")

    args = parser.parse_args()

    audit_dir = project_root / "data" / "homelab_audit"

    if args.audit_file:
        audit_file = Path(args.audit_file)
    else:
        # Find latest
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        if not audit_files:
            print("❌ No audit files found")
            sys.exit(1)
        audit_file = audit_files[0]
        print(f"Using latest audit: {audit_file.name}")

    if not audit_file.exists():
        print(f"❌ Audit file not found: {audit_file}")
        sys.exit(1)

    output_file = Path(args.output) if args.output else None

    export_audit_to_holocron(audit_file, output_file)


if __name__ == "__main__":
    main()
