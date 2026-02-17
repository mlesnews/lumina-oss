#!/usr/bin/env python3
"""
NAS Migration Interrupt and Latency Diagnostic
Engages Backup, Storage, and Network Teams

Investigates interrupts and latency issues potentially caused by NAS migration.
Coordinates with @BACKUP, @STORAGE, and @NETWORK teams.

Tags: #NAS-MIGRATION #INTERRUPTS #LATENCY #PERFORMANCE #TEAMS #BACKUP #STORAGE #NETWORK @JARVIS @TEAM
"""

import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("NASMigrationInterruptDiagnostic")
ts_logger = get_timestamp_logger()


@dataclass
class InterruptMetrics:
    """System interrupt metrics"""
    timestamp: str
    interrupt_count: int
    context_switches: int
    cpu_usage_percent: float
    network_io_bytes: int
    disk_io_bytes: int
    latency_ms: float


@dataclass
class MigrationImpact:
    """NAS migration impact assessment"""
    migration_active: bool
    network_bandwidth_mbps: float
    disk_io_mbps: float
    interrupt_rate_per_sec: float
    latency_impact_ms: float
    recommendations: List[str]


class NASMigrationInterruptDiagnostic:
    """
    NAS Migration Interrupt and Latency Diagnostic

    Engages @BACKUP, @STORAGE, and @NETWORK teams to investigate
    interrupts and latency issues from NAS migration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base_path = f"\\\\{self.nas_ip}\\backups\\MATT_Backups"

        logger.info("🔍 NAS Migration Interrupt Diagnostic initialized")
        logger.info("   Engaging @BACKUP, @STORAGE, @NETWORK teams")

    def check_migration_status(self) -> Dict[str, Any]:
        """Check if NAS migration is currently active"""
        logger.info("📊 Checking NAS migration status...")

        status = {
            "migration_active": False,
            "active_processes": [],
            "network_connections": [],
            "disk_activity": False
        }

        # Check for active migration processes
        try:
            # Check for robocopy (common migration tool)
            robocopy_processes = subprocess.run(
                ["powershell", "-Command", "Get-Process robocopy -ErrorAction SilentlyContinue | Select-Object Id, CPU, WorkingSet"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if robocopy_processes.returncode == 0 and robocopy_processes.stdout.strip():
                status["migration_active"] = True
                status["active_processes"].append({
                    "name": "robocopy",
                    "processes": robocopy_processes.stdout.strip()
                })
                logger.info("   ⚠️  Active robocopy processes detected")

            # Check for Python migration scripts
            python_migration = subprocess.run(
                ["powershell", "-Command", "Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*nas*migration*'} | Select-Object Id, CPU"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if python_migration.returncode == 0 and python_migration.stdout.strip():
                status["migration_active"] = True
                status["active_processes"].append({
                    "name": "python_nas_migration",
                    "processes": python_migration.stdout.strip()
                })
                logger.info("   ⚠️  Active Python migration scripts detected")

        except Exception as e:
            logger.debug(f"   Error checking migration processes: {e}")

        # Check network connections to NAS
        try:
            nas_connections = subprocess.run(
                ["powershell", "-Command", f"Get-NetTCPConnection -RemoteAddress {self.nas_ip} -ErrorAction SilentlyContinue | Select-Object State, LocalPort, RemotePort"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if nas_connections.returncode == 0 and nas_connections.stdout.strip():
                status["network_connections"] = nas_connections.stdout.strip().split('\n')
                if len(status["network_connections"]) > 1:  # More than header
                    status["migration_active"] = True
                    logger.info(f"   ⚠️  {len(status['network_connections'])-1} active connections to NAS")

        except Exception as e:
            logger.debug(f"   Error checking network connections: {e}")

        # Check disk I/O activity
        try:
            disk_activity = subprocess.run(
                ["powershell", "-Command", "Get-Counter '\\PhysicalDisk(*)\\Disk Bytes/sec' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Where-Object {$_.CookedValue -gt 1000000} | Select-Object InstanceName, CookedValue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if disk_activity.returncode == 0 and disk_activity.stdout.strip():
                status["disk_activity"] = True
                logger.info("   ⚠️  High disk I/O activity detected")

        except Exception as e:
            logger.debug(f"   Error checking disk activity: {e}")

        return status

    def measure_interrupts(self, duration_seconds: int = 10) -> InterruptMetrics:
        """Measure system interrupts and context switches"""
        logger.info(f"📈 Measuring interrupts over {duration_seconds} seconds...")

        try:
            # Get initial counters
            initial = subprocess.run(
                ["powershell", "-Command", "Get-Counter '\\System\\Context Switches/sec','\\System\\Interrupts/sec' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Select-Object Path, CookedValue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            time.sleep(duration_seconds)

            # Get final counters
            final = subprocess.run(
                ["powershell", "-Command", "Get-Counter '\\System\\Context Switches/sec','\\System\\Interrupts/sec' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Select-Object Path, CookedValue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse results (simplified - would need proper parsing)
            interrupt_count = 0
            context_switches = 0

            # Get CPU usage
            cpu_usage = subprocess.run(
                ["powershell", "-Command", "(Get-Counter '\\Processor(_Total)\\% Processor Time' -ErrorAction SilentlyContinue).CounterSamples.CookedValue"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse CPU value (handle LUMINA environment messages)
            cpu_output = cpu_usage.stdout.strip() if cpu_usage.returncode == 0 else ""
            cpu_percent = 0.0
            if cpu_output:
                # Extract numeric value from output (may contain environment messages)
                import re
                cpu_match = re.search(r'(\d+\.?\d*)', cpu_output)
                if cpu_match:
                    cpu_percent = float(cpu_match.group(1))

            # Get network I/O
            network_io = subprocess.run(
                ["powershell", "-Command", "(Get-Counter '\\Network Interface(*)\\Bytes Total/sec' -ErrorAction SilentlyContinue).CounterSamples | Measure-Object -Property CookedValue -Sum | Select-Object -ExpandProperty Sum"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse network value (handle LUMINA environment messages)
            network_output = network_io.stdout.strip() if network_io.returncode == 0 else ""
            network_bytes = 0
            if network_output:
                import re
                network_match = re.search(r'(\d+\.?\d*)', network_output)
                if network_match:
                    network_bytes = int(float(network_match.group(1)))

            # Get disk I/O
            disk_io = subprocess.run(
                ["powershell", "-Command", "(Get-Counter '\\PhysicalDisk(_Total)\\Disk Bytes/sec' -ErrorAction SilentlyContinue).CounterSamples.CookedValue"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse disk value (handle LUMINA environment messages)
            disk_output = disk_io.stdout.strip() if disk_io.returncode == 0 else ""
            disk_bytes = 0
            if disk_output:
                import re
                disk_match = re.search(r'(\d+\.?\d*)', disk_output)
                if disk_match:
                    disk_bytes = int(float(disk_match.group(1)))

            # Measure latency (ping test)
            latency_start = time.time()
            ping_test = subprocess.run(
                ["ping", "-n", "1", self.nas_ip],
                capture_output=True,
                timeout=5
            )
            latency_ms = (time.time() - latency_start) * 1000

            metrics = InterruptMetrics(
                timestamp=datetime.now().isoformat(),
                interrupt_count=interrupt_count,
                context_switches=context_switches,
                cpu_usage_percent=cpu_percent,
                network_io_bytes=network_bytes,
                disk_io_bytes=disk_bytes,
                latency_ms=latency_ms
            )

            logger.info(f"   CPU Usage: {cpu_percent:.1f}%")
            logger.info(f"   Network I/O: {network_bytes / (1024*1024):.2f} MB/s")
            logger.info(f"   Disk I/O: {disk_bytes / (1024*1024):.2f} MB/s")
            logger.info(f"   Latency to NAS: {latency_ms:.2f} ms")

            return metrics

        except Exception as e:
            logger.error(f"   ❌ Error measuring interrupts: {e}", exc_info=True)
            return InterruptMetrics(
                timestamp=datetime.now().isoformat(),
                interrupt_count=0,
                context_switches=0,
                cpu_usage_percent=0.0,
                network_io_bytes=0,
                disk_io_bytes=0,
                latency_ms=0.0
            )

    def assess_migration_impact(self) -> MigrationImpact:
        """Assess impact of NAS migration on system performance"""
        logger.info("🔍 Assessing NAS migration impact...")

        migration_status = self.check_migration_status()
        metrics = self.measure_interrupts(duration_seconds=5)

        # Calculate impact
        network_bandwidth_mbps = (metrics.network_io_bytes * 8) / (1024 * 1024)  # Convert to Mbps
        disk_io_mbps = metrics.disk_io_bytes / (1024 * 1024)
        interrupt_rate = metrics.interrupt_count / 5.0  # Per second
        latency_impact = metrics.latency_ms - 1.0  # Baseline ~1ms

        recommendations = []

        if migration_status["migration_active"]:
            recommendations.append("⚠️  NAS migration is currently active")

        if network_bandwidth_mbps > 100:
            recommendations.append(f"⚠️  High network bandwidth usage: {network_bandwidth_mbps:.2f} Mbps")
            recommendations.append("   → Consider throttling migration during peak hours")
            recommendations.append("   → @NETWORK team: Review network capacity")

        if disk_io_mbps > 50:
            recommendations.append(f"⚠️  High disk I/O: {disk_io_mbps:.2f} MB/s")
            recommendations.append("   → @STORAGE team: Check disk performance")
            recommendations.append("   → Consider pausing migration if causing system slowdown")

        if metrics.latency_ms > 10:
            recommendations.append(f"⚠️  High latency to NAS: {metrics.latency_ms:.2f} ms")
            recommendations.append("   → @NETWORK team: Check network path to NAS")
            recommendations.append("   → Verify LAN connection (not WiFi)")

        if metrics.cpu_usage_percent > 80:
            recommendations.append(f"⚠️  High CPU usage: {metrics.cpu_usage_percent:.1f}%")
            recommendations.append("   → Consider reducing migration concurrency")

        if interrupt_rate > 1000:
            recommendations.append(f"⚠️  High interrupt rate: {interrupt_rate:.0f} interrupts/sec")
            recommendations.append("   → @NETWORK team: Check for network adapter issues")
            recommendations.append("   → @STORAGE team: Check for disk controller issues")

        if not recommendations:
            recommendations.append("✅ No significant impact detected")
            recommendations.append("   System performance appears normal")

        impact = MigrationImpact(
            migration_active=migration_status["migration_active"],
            network_bandwidth_mbps=network_bandwidth_mbps,
            disk_io_mbps=disk_io_mbps,
            interrupt_rate_per_sec=interrupt_rate,
            latency_impact_ms=latency_impact,
            recommendations=recommendations
        )

        return impact

    def engage_teams(self, impact: MigrationImpact) -> Dict[str, Any]:
        """Engage @BACKUP, @STORAGE, and @NETWORK teams"""
        logger.info("👥 Engaging teams: @BACKUP, @STORAGE, @NETWORK")

        team_actions = {
            "@BACKUP": [],
            "@STORAGE": [],
            "@NETWORK": [],
            "timestamp": datetime.now().isoformat()
        }

        # @BACKUP Team Actions
        if impact.migration_active:
            team_actions["@BACKUP"].append({
                "action": "Review migration schedule",
                "priority": "HIGH",
                "details": "NAS migration is active and may be causing interrupts"
            })
            team_actions["@BACKUP"].append({
                "action": "Check backup window conflicts",
                "priority": "MEDIUM",
                "details": "Ensure migration doesn't conflict with backup schedules"
            })

        # @STORAGE Team Actions
        if impact.disk_io_mbps > 50:
            team_actions["@STORAGE"].append({
                "action": "Monitor disk I/O performance",
                "priority": "HIGH",
                "details": f"High disk I/O detected: {impact.disk_io_mbps:.2f} MB/s"
            })
            team_actions["@STORAGE"].append({
                "action": "Check storage array performance",
                "priority": "MEDIUM",
                "details": "Verify NAS storage array can handle migration load"
            })

        if impact.interrupt_rate_per_sec > 1000:
            team_actions["@STORAGE"].append({
                "action": "Check disk controller interrupts",
                "priority": "HIGH",
                "details": f"High interrupt rate: {impact.interrupt_rate_per_sec:.0f}/sec"
            })

        # @NETWORK Team Actions
        if impact.network_bandwidth_mbps > 100:
            team_actions["@NETWORK"].append({
                "action": "Monitor network bandwidth",
                "priority": "HIGH",
                "details": f"High network usage: {impact.network_bandwidth_mbps:.2f} Mbps"
            })
            team_actions["@NETWORK"].append({
                "action": "Verify LAN connection (not WiFi)",
                "priority": "HIGH",
                "details": "WiFi bandwidth insufficient for large migrations"
            })
            team_actions["@NETWORK"].append({
                "action": "Check network path to NAS",
                "priority": "MEDIUM",
                "details": "Verify optimal routing to <NAS_PRIMARY_IP>"
            })

        if impact.latency_impact_ms > 5:
            team_actions["@NETWORK"].append({
                "action": "Investigate network latency",
                "priority": "HIGH",
                "details": f"High latency detected: {impact.latency_impact_ms:.2f} ms"
            })

        if impact.interrupt_rate_per_sec > 1000:
            team_actions["@NETWORK"].append({
                "action": "Check network adapter interrupts",
                "priority": "HIGH",
                "details": f"High interrupt rate: {impact.interrupt_rate_per_sec:.0f}/sec"
            })

        # Log team engagements
        for team, actions in team_actions.items():
            if team.startswith("@") and actions:
                logger.info(f"   {team} Team: {len(actions)} actions")
                for action in actions:
                    logger.info(f"      - [{action['priority']}] {action['action']}")

        return team_actions

    def generate_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive diagnostic report"""
            logger.info("📋 Generating diagnostic report...")

            impact = self.assess_migration_impact()
            team_actions = self.engage_teams(impact)

            report = {
                "timestamp": datetime.now().isoformat(),
                "migration_status": {
                    "active": impact.migration_active,
                    "network_bandwidth_mbps": impact.network_bandwidth_mbps,
                    "disk_io_mbps": impact.disk_io_mbps,
                    "interrupt_rate_per_sec": impact.interrupt_rate_per_sec,
                    "latency_impact_ms": impact.latency_impact_ms
                },
                "recommendations": impact.recommendations,
                "team_actions": team_actions,
                "next_steps": [
                    "Monitor system performance during migration",
                    "Coordinate with @BACKUP team on migration schedule",
                    "Coordinate with @STORAGE team on disk I/O",
                    "Coordinate with @NETWORK team on bandwidth and latency"
                ]
            }

            # Save report
            report_file = self.project_root / "data" / "system" / "nas_migration_interrupt_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"   ✅ Report saved to {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="NAS Migration Interrupt and Latency Diagnostic")
        parser.add_argument("--check", action="store_true", help="Check migration status")
        parser.add_argument("--measure", action="store_true", help="Measure interrupts and latency")
        parser.add_argument("--assess", action="store_true", help="Assess migration impact")
        parser.add_argument("--teams", action="store_true", help="Engage teams")
        parser.add_argument("--report", action="store_true", help="Generate full report")

        args = parser.parse_args()

        print("="*80)
        print("🔍 NAS MIGRATION INTERRUPT & LATENCY DIAGNOSTIC")
        print("="*80)
        print()
        print("Engaging: @BACKUP, @STORAGE, @NETWORK teams")
        print()

        diagnostic = NASMigrationInterruptDiagnostic()

        if args.check:
            status = diagnostic.check_migration_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.measure:
            metrics = diagnostic.measure_interrupts()
            print(json.dumps(asdict(metrics), indent=2))

        elif args.assess:
            impact = diagnostic.assess_migration_impact()
            print(json.dumps(asdict(impact), indent=2, default=str))

        elif args.teams:
            impact = diagnostic.assess_migration_impact()
            actions = diagnostic.engage_teams(impact)
            print(json.dumps(actions, indent=2, default=str))

        elif args.report:
            report = diagnostic.generate_report()
            print(json.dumps(report, indent=2, default=str))

        else:
            # Default: generate full report
            report = diagnostic.generate_report()
            print("\n📊 DIAGNOSTIC REPORT")
            print("="*80)
            print(f"\nMigration Active: {report['migration_status']['active']}")
            print(f"Network Bandwidth: {report['migration_status']['network_bandwidth_mbps']:.2f} Mbps")
            print(f"Disk I/O: {report['migration_status']['disk_io_mbps']:.2f} MB/s")
            print(f"Interrupt Rate: {report['migration_status']['interrupt_rate_per_sec']:.0f}/sec")
            print(f"Latency Impact: {report['migration_status']['latency_impact_ms']:.2f} ms")
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
            print("\n👥 Team Actions:")
            for team, actions in report['team_actions'].items():
                if team.startswith("@") and actions:
                    print(f"\n   {team}:")
                    for action in actions:
                        print(f"      [{action['priority']}] {action['action']}")
            print(f"\n📄 Full report saved to: {report.get('_report_file', 'N/A')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()