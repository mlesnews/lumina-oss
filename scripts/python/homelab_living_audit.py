#!/usr/bin/env python3
"""
Homelab Living Audit System

Periodic, automated audit system that runs comprehensive audits including:
- Device discovery
- Feature enumeration
- Software inventory
- Control interface discovery
- Network topology mapping
- Connection monitoring
- Anomaly detection

Runs periodically (daily by default) to maintain a living, breathing view of the homelab.

Tags: #HOMELAB #AUDIT #LIVING #AUTOMATED #PERIODIC @JARVIS @LUMINA
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.homelab_connection_monitor import HomelabConnectionMonitor
from scripts.python.homelab_control_interface_discovery import ControlInterfaceMapper
from scripts.python.homelab_network_topology import NetworkTopologyMapper
from scripts.python.homelab_software_discovery import HomelabSoftwareDiscovery
from scripts.python.homelab_topdown_audit import HomelabTopDownAuditor

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_living_audit")


class HomelabLivingAudit:
    """Living audit system that runs periodic comprehensive audits"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.auditor = HomelabTopDownAuditor(project_root)
        self.control_mapper = ControlInterfaceMapper(project_root)
        self.software_discovery = HomelabSoftwareDiscovery(project_root)
        self.topology_mapper = NetworkTopologyMapper(project_root)
        self.connection_monitor = HomelabConnectionMonitor(project_root)
        self.architecture_discovery = HomelabArchitectureDiscovery(project_root)

    def run_comprehensive_audit(self, scan_network: bool = True) -> Dict[str, Any]:
        """Run comprehensive audit of everything"""
        print("=" * 80)
        print("HOMELAB LIVING AUDIT - COMPREHENSIVE")
        print("=" * 80)
        print(f"Started: {datetime.now().isoformat()}")
        print()

        audit_results = {
            "audit_id": f"living_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "components": {},
        }

        # 1. Device and Feature Audit
        print("1. Running device and feature audit...")
        audit = self.auditor.run_full_audit(scan_network=scan_network)
        audit_results["components"]["device_audit"] = {
            "devices": len(audit.devices),
            "features": sum(len(d.features) for d in audit.devices),
            "audit_id": audit.audit_id,
        }
        print(
            f"   ✅ {len(audit.devices)} devices, {sum(len(d.features) for d in audit.devices)} features"
        )

        # Find latest audit file
        audit_dir = project_root / "data" / "homelab_audit"
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        latest_audit_file = audit_files[0]

        # 2. Control Interface Discovery
        print("\n2. Discovering control interfaces...")
        interfaces = self.control_mapper.map_all_devices(latest_audit_file)
        audit_results["components"]["control_interfaces"] = {
            "interfaces": len(interfaces),
            "commands": sum(len(i.commands) for i in interfaces),
            "api_endpoints": sum(len(i.api_endpoints) for i in interfaces),
            "cli_tools": sum(len(i.cli_tools) for i in interfaces),
        }
        print(
            f"   ✅ {len(interfaces)} interfaces, {sum(len(i.commands) for i in interfaces)} commands, "
            f"{sum(len(i.api_endpoints) for i in interfaces)} APIs, {sum(len(i.cli_tools) for i in interfaces)} CLIs"
        )

        # 3. Software Inventory
        print("\n3. Discovering software inventory...")
        software_inventory = self.software_discovery.discover_all_software(latest_audit_file)
        total_packages = sum(d["total_packages"] for d in software_inventory["devices"])
        audit_results["components"]["software_inventory"] = {
            "devices": len(software_inventory["devices"]),
            "total_packages": total_packages,
        }
        print(
            f"   ✅ {total_packages} software packages across {len(software_inventory['devices'])} devices"
        )

        # 4. Network Topology
        print("\n4. Mapping network topology...")
        topology = self.topology_mapper.generate_topology_map(latest_audit_file)
        audit_results["components"]["network_topology"] = {
            "devices": len(topology["devices"]),
            "segments": len(topology["segments"]),
            "connections": len(topology["connections"]),
            "graph_nodes": topology["graph"]["summary"]["total_nodes"],
            "graph_edges": topology["graph"]["summary"]["total_edges"],
        }
        print(
            f"   ✅ {len(topology['devices'])} devices, {len(topology['segments'])} segments, "
            f"{len(topology['connections'])} connections"
        )

        # 5. Connection Monitoring
        print("\n5. Monitoring connections...")
        monitoring = self.connection_monitor.monitor_all_devices(latest_audit_file)
        audit_results["components"]["connection_monitoring"] = {
            "connections": monitoring["summary"]["total_connections"],
            "accounts": monitoring["summary"]["total_accounts"],
            "events": monitoring["summary"]["total_events"],
            "critical_events": monitoring["summary"]["critical_events"],
            "warning_events": monitoring["summary"]["warning_events"],
        }
        print(
            f"   ✅ {monitoring['summary']['total_connections']} connections, "
            f"{monitoring['summary']['total_accounts']} accounts, "
            f"{monitoring['summary']['total_events']} events"
        )

        # 6. Architecture Discovery
        print("\n6. Discovering architecture (applications, services, frameworks)...")
        architecture = self.architecture_discovery.discover_all_architecture(latest_audit_file)
        audit_results["components"]["architecture"] = {
            "services": architecture["summary"]["total_services"],
            "processes": architecture["summary"]["total_processes"],
            "applications": architecture["summary"]["total_applications"],
            "frameworks": architecture["summary"]["total_frameworks"],
        }
        print(
            f"   ✅ {architecture['summary']['total_services']} services, "
            f"{architecture['summary']['total_processes']} processes, "
            f"{architecture['summary']['total_applications']} applications, "
            f"{architecture['summary']['total_frameworks']} frameworks"
        )

        audit_results["completed_at"] = datetime.now().isoformat()
        duration = datetime.fromisoformat(audit_results["completed_at"]) - datetime.fromisoformat(
            audit_results["started_at"]
        )
        audit_results["duration_seconds"] = duration.total_seconds()

        # Save comprehensive report
        output_dir = project_root / "data" / "homelab_living_audit"
        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = output_dir / f"living_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False, default=str)

        print("\n" + "=" * 80)
        print("COMPREHENSIVE AUDIT COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        print(f"Report saved: {report_file}")
        print("=" * 80)

        return audit_results

    def run_periodic(self, interval_hours: int = 24, max_runs: Optional[int] = None):
        """Run periodic audits"""
        print("=" * 80)
        print("HOMELAB LIVING AUDIT - PERIODIC MODE")
        print("=" * 80)
        print(f"Interval: {interval_hours} hours")
        print(f"Max runs: {max_runs if max_runs else 'unlimited'}")
        print()

        run_count = 0

        while True:
            try:
                run_count += 1
                print(f"\n{'=' * 80}")
                print(f"RUN #{run_count} - {datetime.now().isoformat()}")
                print(f"{'=' * 80}\n")

                self.run_comprehensive_audit(scan_network=True)

                if max_runs and run_count >= max_runs:
                    print(f"\n✅ Completed {max_runs} runs. Stopping.")
                    break

                print(f"\n⏳ Waiting {interval_hours} hours until next audit...")
                time.sleep(interval_hours * 3600)

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user. Stopping periodic audits.")
                break
            except Exception as e:
                logger.error(f"Error in periodic audit: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")
                print("⏳ Waiting before retry...")
                time.sleep(3600)  # Wait 1 hour before retry


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab Living Audit System")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--periodic", action="store_true", help="Run periodically (default: daily)")
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=24,
        help="Interval between audits in hours (default: 24)",
    )
    parser.add_argument("--max-runs", type=int, help="Maximum number of runs (for periodic mode)")
    parser.add_argument("--no-network-scan", action="store_true", help="Skip network scanning")

    args = parser.parse_args()

    living_audit = HomelabLivingAudit(project_root)

    if args.periodic or not args.once:
        living_audit.run_periodic(interval_hours=args.interval_hours, max_runs=args.max_runs)
    else:
        living_audit.run_comprehensive_audit(scan_network=not args.no_network_scan)


if __name__ == "__main__":
    main()
    main()
    main()
