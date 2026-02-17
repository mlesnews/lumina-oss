#!/usr/bin/env python3
"""
Quick Report Generator for Homelab Audit

Generates a quick summary report from audit JSON files without requiring MariaDB.

Tags: #HOMELAB #AUDIT #REPORTING @JARVIS @LUMINA
"""

import json
import sys
from collections import Counter
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def generate_quick_report(audit_file: Path):
    """Generate quick report from audit JSON"""
    with open(audit_file, encoding="utf-8") as f:
        audit_data = json.load(f)

    print("=" * 80)
    print("HOMELAB AUDIT QUICK REPORT")
    print("=" * 80)
    print(f"Audit ID: {audit_data['audit_id']}")
    print(f"Timestamp: {audit_data['audit_timestamp']}")
    print()

    # Summary
    print("SUMMARY")
    print("-" * 80)
    print(f"Total Devices: {len(audit_data.get('devices', []))}")

    total_features = sum(len(d.get("features", [])) for d in audit_data.get("devices", []))
    print(f"Total Features: {total_features}")

    if audit_data.get("ecosystem_complexity"):
        ec = audit_data["ecosystem_complexity"]
        print(f"Total Complexity Score: {ec.get('total_complexity_score', 0)}")
        print(f"Average Complexity: {ec.get('average_complexity_score', 0)}")

    print(f"Drift Detected: {len(audit_data.get('drift_detected', []))}")
    print()

    # Devices
    print("DEVICES")
    print("-" * 80)
    for device in audit_data.get("devices", []):
        print(f"\n{device['device_name']} ({device['device_type']})")
        print(f"  OS: {device.get('operating_system', 'Unknown')} {device.get('os_version', '')}")
        print(f"  IP: {device.get('ip_address', 'Unknown')}")
        print(f"  Complexity Score: {device.get('complexity_score', 0)}")
        print(f"  Features: {len(device.get('features', []))}")
        print(f"  Services: {len(device.get('services', []))}")
        print(f"  Network Interfaces: {len(device.get('network_interfaces', []))}")
        print(f"  Storage Devices: {len(device.get('storage_devices', []))}")
        print(f"  Config Files: {len(device.get('configuration_files', []))}")

        # Features by category
        if device.get("features"):
            categories = Counter(f.get("category", "unknown") for f in device["features"])
            print("  Features by Category:")
            for cat, count in categories.most_common():
                print(f"    {cat}: {count}")

    # Drift
    if audit_data.get("drift_detected"):
        print("\nCOMPLEXITY DRIFT")
        print("-" * 80)
        for drift in audit_data["drift_detected"]:
            print(
                f"  {drift.get('device_name')}: {len(drift.get('drift', {}).get('changes', []))} changes"
            )

    print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate quick audit report")
    parser.add_argument("--audit-file", help="Specific audit file (default: latest)")

    args = parser.parse_args()

    audit_dir = project_root / "data" / "homelab_audit"

    if args.audit_file:
        audit_file = Path(args.audit_file)
    else:
        # Find latest
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        if not audit_files:
            print("No audit files found")
            sys.exit(1)
        audit_file = audit_files[0]

    if not audit_file.exists():
        print(f"Audit file not found: {audit_file}")
        sys.exit(1)

    generate_quick_report(audit_file)


if __name__ == "__main__":
    main()
