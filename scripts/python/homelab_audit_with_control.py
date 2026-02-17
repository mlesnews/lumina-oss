#!/usr/bin/env python3
"""
Homelab Audit with Control Interface Discovery

Extended audit system that includes control interface discovery (commands, APIs, CLIs)
as part of the comprehensive audit.

Tags: #HOMELAB #AUDIT #CONTROL #INTEGRATED @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.homelab_control_interface_discovery import ControlInterfaceMapper
from scripts.python.homelab_topdown_audit import HomelabTopDownAuditor


def main():
    """Run audit with control interface discovery"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run homelab audit with control interface discovery"
    )
    parser.add_argument("--no-network-scan", action="store_true", help="Skip network scanning")
    parser.add_argument("--output", help="Output file for combined audit")

    args = parser.parse_args()

    print("=" * 80)
    print("HOMELAB AUDIT WITH CONTROL INTERFACE DISCOVERY")
    print("=" * 80)

    # Step 1: Run standard audit
    print("\n1. Running standard audit...")
    auditor = HomelabTopDownAuditor(project_root)
    audit = auditor.run_full_audit(scan_network=not args.no_network_scan)

    print(
        f"   ✅ Audit complete: {len(audit.devices)} devices, {sum(len(d.features) for d in audit.devices)} features"
    )

    # Step 2: Discover control interfaces
    print("\n2. Discovering control interfaces...")
    mapper = ControlInterfaceMapper(project_root)

    # Find latest audit file
    audit_dir = project_root / "data" / "homelab_audit"
    audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
    latest_audit_file = audit_files[0]

    interfaces = mapper.map_all_devices(latest_audit_file)
    print(f"   ✅ Control interfaces discovered: {len(interfaces)} interfaces")
    print(f"      Commands: {sum(len(i.commands) for i in interfaces)}")
    print(f"      APIs: {sum(len(i.api_endpoints) for i in interfaces)}")
    print(f"      CLIs: {sum(len(i.cli_tools) for i in interfaces)}")

    # Step 3: Combine audit and control interfaces
    print("\n3. Combining audit and control interfaces...")

    # Load audit JSON
    with open(latest_audit_file, encoding="utf-8") as f:
        audit_data = json.load(f)

    # Add control interfaces to each device
    for device in audit_data.get("devices", []):
        device_id = device["device_id"]

        # Find matching control interface
        for interface in interfaces:
            if interface.device_id == device_id:
                device["control_interface"] = asdict(interface)
                break

    # Add summary
    audit_data["control_interfaces_summary"] = {
        "total_interfaces": len(interfaces),
        "total_commands": sum(len(i.commands) for i in interfaces),
        "total_api_endpoints": sum(len(i.api_endpoints) for i in interfaces),
        "total_cli_tools": sum(len(i.cli_tools) for i in interfaces),
    }

    # Save combined audit
    output_dir = project_root / "data" / "homelab_audit"
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"audit_with_control_{audit.audit_id}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"   ✅ Combined audit saved: {output_file.name}")

    # Print summary
    print("\n" + "=" * 80)
    print("COMPLETE AUDIT SUMMARY")
    print("=" * 80)
    print(f"Devices: {len(audit.devices)}")
    print(f"Features: {sum(len(d.features) for d in audit.devices)}")
    print(f"Control Interfaces: {len(interfaces)}")
    print(f"Commands: {audit_data['control_interfaces_summary']['total_commands']}")
    print(f"API Endpoints: {audit_data['control_interfaces_summary']['total_api_endpoints']}")
    print(f"CLI Tools: {audit_data['control_interfaces_summary']['total_cli_tools']}")
    print("=" * 80)

    return audit_data


if __name__ == "__main__":
    main()
    main()
