#!/usr/bin/env python3
"""
Homelab Connection Monitor

Monitors all connections, accounts, and access attempts across the homelab.
Detects new devices, accounts, and connections in real-time.

Tags: #HOMELAB #MONITORING #SECURITY #ANOMALY #DETECTION @JARVIS @LUMINA
"""

import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_connection_monitor")


@dataclass
class ActiveConnection:
    """Active network connection"""

    connection_id: str
    source_ip: str
    source_port: int
    target_ip: str
    target_port: int
    protocol: str  # "tcp", "udp"
    state: str  # "established", "listening", "time_wait", etc.
    process_name: Optional[str] = None
    process_id: Optional[int] = None
    device_id: str = ""
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ActiveAccount:
    """Active user account session"""

    account_id: str
    username: str
    session_type: str  # "local", "ssh", "rdp", "api", "web"
    source_ip: Optional[str] = None
    login_time: Optional[str] = None
    device_id: str = ""
    status: str = "active"  # "active", "disconnected"


@dataclass
class ConnectionEvent:
    """Connection event (new, changed, removed)"""

    event_id: str
    event_type: str  # "new_connection", "new_account", "new_device", "connection_closed"
    timestamp: str
    source: str
    target: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # "info", "warning", "critical"


class WindowsConnectionMonitor:
    """Monitor connections on Windows"""

    def get_active_connections(self, device_id: str) -> List[ActiveConnection]:
        """Get active network connections"""
        connections = []

        try:
            # Use netstat
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[4:]:  # Skip headers
                    parts = line.split()
                    if len(parts) >= 5:
                        proto = parts[0].lower()
                        local_addr = parts[1]
                        foreign_addr = parts[2]
                        state = parts[3] if len(parts) > 3 else "UNKNOWN"
                        pid = parts[-1]

                        # Parse addresses
                        if ":" in local_addr:
                            local_ip, local_port = local_addr.rsplit(":", 1)
                        else:
                            continue

                        if ":" in foreign_addr:
                            foreign_ip, foreign_port = foreign_addr.rsplit(":", 1)
                        else:
                            foreign_ip = foreign_addr
                            foreign_port = "0"

                        # Get process name
                        process_name = self._get_process_name(pid)

                        connections.append(
                            ActiveConnection(
                                connection_id=f"{device_id}_conn_{local_addr}_{foreign_addr}_{proto}",
                                source_ip=local_ip,
                                source_port=int(local_port),
                                target_ip=foreign_ip,
                                target_port=int(foreign_port) if foreign_port.isdigit() else 0,
                                protocol=proto,
                                state=state.lower(),
                                process_id=int(pid) if pid.isdigit() else None,
                                process_name=process_name,
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.warning(f"Failed to get Windows connections: {e}")

        return connections

    def get_active_sessions(self, device_id: str) -> List[ActiveAccount]:
        """Get active user sessions"""
        accounts = []

        try:
            # Query active sessions
            result = subprocess.run(
                ["query", "session"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[2:]:  # Skip headers
                    parts = line.split()
                    if len(parts) >= 3:
                        session_name = parts[0]
                        username = parts[1]
                        state = parts[2]

                        if username and username != "USERNAME":
                            accounts.append(
                                ActiveAccount(
                                    account_id=f"{device_id}_session_{username}_{session_name}",
                                    username=username,
                                    session_type="local" if session_name == "console" else "rdp",
                                    device_id=device_id,
                                    status="active" if state == "Active" else "disconnected",
                                )
                            )
        except Exception as e:
            logger.debug(f"Failed to get Windows sessions: {e}")

        return accounts

    def _get_process_name(self, pid: str) -> Optional[str]:
        """Get process name from PID"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(",")
                if len(parts) > 0:
                    return parts[0].strip('"')
        except:
            pass
        return None


class LinuxConnectionMonitor:
    """Monitor connections on Linux"""

    def get_active_connections(self, device_id: str) -> List[ActiveConnection]:
        """Get active network connections"""
        connections = []

        try:
            # Use ss command
            result = subprocess.run(["ss", "-tunp"], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 5:
                        state = parts[0]
                        local_addr = parts[4]
                        peer_addr = parts[5] if len(parts) > 5 else ""
                        process_info = parts[-1] if len(parts) > 5 else ""

                        # Parse addresses
                        if ":" in local_addr:
                            local_ip, local_port = local_addr.rsplit(":", 1)
                        else:
                            continue

                        if ":" in peer_addr:
                            peer_ip, peer_port = peer_addr.rsplit(":", 1)
                        else:
                            peer_ip = peer_addr
                            peer_port = "0"

                        # Extract process info
                        process_name = None
                        process_id = None
                        if "pid=" in process_info:
                            pid_match = process_info.split("pid=")[1].split(",")[0]
                            process_id = int(pid_match) if pid_match.isdigit() else None

                        connections.append(
                            ActiveConnection(
                                connection_id=f"{device_id}_conn_{local_addr}_{peer_addr}",
                                source_ip=local_ip,
                                source_port=int(local_port),
                                target_ip=peer_ip,
                                target_port=int(peer_port) if peer_port.isdigit() else 0,
                                protocol="tcp" if "tcp" in state.lower() else "udp",
                                state=state.lower(),
                                process_id=process_id,
                                process_name=process_name,
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.warning(f"Failed to get Linux connections: {e}")

        return connections

    def get_active_sessions(self, device_id: str) -> List[ActiveAccount]:
        """Get active user sessions"""
        accounts = []

        try:
            # Get logged in users
            result = subprocess.run(["who"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    parts = line.split()
                    if len(parts) >= 3:
                        username = parts[0]
                        terminal = parts[1]
                        source = parts[2] if len(parts) > 2 else "local"

                        accounts.append(
                            ActiveAccount(
                                account_id=f"{device_id}_session_{username}_{terminal}",
                                username=username,
                                session_type="ssh" if "@" in source or ":" in source else "local",
                                source_ip=source if ":" in source else None,
                                device_id=device_id,
                                status="active",
                            )
                        )
        except Exception as e:
            logger.debug(f"Failed to get Linux sessions: {e}")

        return accounts


class ConnectionAnomalyDetector:
    """Detects anomalies in connections"""

    def __init__(self, baseline_file: Optional[Path] = None):
        self.baseline_file = baseline_file
        self.baseline: Dict[str, Any] = {}
        self.load_baseline()

    def load_baseline(self):
        """Load baseline connections"""
        if self.baseline_file and self.baseline_file.exists():
            try:
                with open(self.baseline_file, encoding="utf-8") as f:
                    self.baseline = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load baseline: {e}")

    def detect_new_connections(
        self,
        current_connections: List[ActiveConnection],
        baseline_connections: List[ActiveConnection],
    ) -> List[ConnectionEvent]:
        """Detect new connections"""
        events = []

        baseline_set = {
            (c.source_ip, c.source_port, c.target_ip, c.target_port, c.protocol)
            for c in baseline_connections
        }

        for conn in current_connections:
            conn_key = (
                conn.source_ip,
                conn.source_port,
                conn.target_ip,
                conn.target_port,
                conn.protocol,
            )

            if conn_key not in baseline_set:
                events.append(
                    ConnectionEvent(
                        event_id=f"event_{datetime.now().timestamp()}",
                        event_type="new_connection",
                        timestamp=datetime.now().isoformat(),
                        source=f"{conn.source_ip}:{conn.source_port}",
                        target=f"{conn.target_ip}:{conn.target_port}",
                        details={
                            "protocol": conn.protocol,
                            "state": conn.state,
                            "process": conn.process_name,
                            "device_id": conn.device_id,
                        },
                        severity="warning" if conn.state == "established" else "info",
                    )
                )

        return events

    def detect_new_accounts(
        self, current_accounts: List[ActiveAccount], baseline_accounts: List[ActiveAccount]
    ) -> List[ConnectionEvent]:
        """Detect new account sessions"""
        events = []

        baseline_set = {(a.username, a.session_type, a.source_ip) for a in baseline_accounts}

        for account in current_accounts:
            account_key = (account.username, account.session_type, account.source_ip)

            if account_key not in baseline_set:
                events.append(
                    ConnectionEvent(
                        event_id=f"event_{datetime.now().timestamp()}",
                        event_type="new_account",
                        timestamp=datetime.now().isoformat(),
                        source=account.username,
                        target=account.device_id,
                        details={
                            "session_type": account.session_type,
                            "source_ip": account.source_ip,
                            "login_time": account.login_time,
                        },
                        severity="warning" if account.session_type in ["ssh", "rdp"] else "info",
                    )
                )

        return events

    def detect_new_devices(
        self, current_ips: Set[str], baseline_ips: Set[str]
    ) -> List[ConnectionEvent]:
        """Detect new devices on network"""
        events = []

        new_ips = current_ips - baseline_ips

        for ip in new_ips:
            events.append(
                ConnectionEvent(
                    event_id=f"event_{datetime.now().timestamp()}",
                    event_type="new_device",
                    timestamp=datetime.now().isoformat(),
                    source=ip,
                    target="network",
                    details={"ip_address": ip},
                    severity="critical",
                )
            )

        return events


class HomelabConnectionMonitor:
    """Main connection monitoring system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.windows_monitor = WindowsConnectionMonitor()
        self.linux_monitor = LinuxConnectionMonitor()
        self.anomaly_detector = ConnectionAnomalyDetector()
        self.monitoring_data: Dict[str, Any] = {}

    def monitor_device(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor connections on a device"""
        device_id = device["device_id"]
        os_type = device.get("operating_system", "")

        monitor_data = {
            "device_id": device_id,
            "monitored_at": datetime.now().isoformat(),
            "connections": [],
            "accounts": [],
            "events": [],
        }

        if os_type == "Windows":
            monitor_data["connections"] = [
                asdict(c) for c in self.windows_monitor.get_active_connections(device_id)
            ]
            monitor_data["accounts"] = [
                asdict(a) for a in self.windows_monitor.get_active_sessions(device_id)
            ]
        elif os_type == "Linux" or "Synology" in os_type:
            monitor_data["connections"] = [
                asdict(c) for c in self.linux_monitor.get_active_connections(device_id)
            ]
            monitor_data["accounts"] = [
                asdict(a) for a in self.linux_monitor.get_active_sessions(device_id)
            ]

        return monitor_data

    def monitor_all_devices(self, audit_file: Path) -> Dict[str, Any]:
        """Monitor all devices"""
        with open(audit_file, encoding="utf-8") as f:
            audit_data = json.load(f)

        monitoring_report = {
            "monitoring_id": f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "monitored_at": datetime.now().isoformat(),
            "devices": [],
        }

        all_connections = []
        all_accounts = []
        all_events = []

        for device in audit_data.get("devices", []):
            device_monitor = self.monitor_device(device)
            monitoring_report["devices"].append(device_monitor)

            all_connections.extend(device_monitor["connections"])
            all_accounts.extend(device_monitor["accounts"])

        # Detect anomalies
        baseline_file = (
            self.project_root / "data" / "homelab_monitoring" / "baseline_connections.json"
        )
        if baseline_file.exists():
            with open(baseline_file, encoding="utf-8") as f:
                baseline_data = json.load(f)

            baseline_connections = [
                ActiveConnection(**c) for c in baseline_data.get("connections", [])
            ]
            baseline_accounts = [ActiveAccount(**a) for a in baseline_data.get("accounts", [])]

            current_connections = [ActiveConnection(**c) for c in all_connections]
            current_accounts = [ActiveAccount(**a) for a in all_accounts]

            # Detect new connections
            connection_events = self.anomaly_detector.detect_new_connections(
                current_connections, baseline_connections
            )
            all_events.extend([asdict(e) for e in connection_events])

            # Detect new accounts
            account_events = self.anomaly_detector.detect_new_accounts(
                current_accounts, baseline_accounts
            )
            all_events.extend([asdict(e) for e in account_events])

        monitoring_report["summary"] = {
            "total_connections": len(all_connections),
            "total_accounts": len(all_accounts),
            "total_events": len(all_events),
            "critical_events": len([e for e in all_events if e.get("severity") == "critical"]),
            "warning_events": len([e for e in all_events if e.get("severity") == "warning"]),
        }

        monitoring_report["events"] = all_events

        return monitoring_report

    def save_monitoring_report(self, report: Dict[str, Any], output_file: Path):
        """Save monitoring report"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Monitoring report saved: {output_file}")

        # Save as baseline for next run
        baseline_file = output_file.parent / "baseline_connections.json"
        baseline = {
            "baseline_id": f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "connections": [c for device in report["devices"] for c in device["connections"]],
            "accounts": [a for device in report["devices"] for a in device["accounts"]],
        }

        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False, default=str)

        return report


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor homelab connections and detect anomalies")
    parser.add_argument("--audit-file", help="Audit file to use (default: latest)")
    parser.add_argument("--output", help="Output file (default: monitoring_<timestamp>.json)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    monitor = HomelabConnectionMonitor(project_root)

    # Find audit file
    audit_dir = project_root / "data" / "homelab_audit"
    if args.audit_file:
        audit_file = Path(args.audit_file)
    else:
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        if not audit_files:
            print("❌ No audit files found")
            sys.exit(1)
        audit_file = audit_files[0]
        print(f"Using audit: {audit_file.name}")

    # Monitor
    print("Monitoring connections...")
    report = monitor.monitor_all_devices(audit_file)

    # Save report
    output_dir = project_root / "data" / "homelab_monitoring"
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    monitor.save_monitoring_report(report, output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("CONNECTION MONITORING SUMMARY")
    print("=" * 80)
    summary = report["summary"]
    print(f"Total Connections: {summary['total_connections']}")
    print(f"Total Accounts: {summary['total_accounts']}")
    print(f"Total Events: {summary['total_events']}")
    print(f"Critical Events: {summary['critical_events']}")
    print(f"Warning Events: {summary['warning_events']}")

    if report["events"]:
        print("\nRecent Events:")
        for event in report["events"][:10]:
            print(
                f"  [{event['severity'].upper()}] {event['event_type']}: {event['source']} -> {event['target']}"
            )

    print(f"\nMonitoring report saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
