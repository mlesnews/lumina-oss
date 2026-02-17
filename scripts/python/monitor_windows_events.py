#!/usr/bin/env python3
"""
Windows Event Viewer Monitor - System Health & Memory Integrity Diagnostics

Monitors Windows Event Viewer logs for hardware/software issues and
Memory Integrity blocking events. Provides comprehensive system health reporting.

Author: <COMPANY_NAME> LLC
Date: 2025-01-XX
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WindowsEventMonitor")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class EventSeverity(Enum):
    """Event severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"


class EventCategory(Enum):
    """Event categories"""
    MEMORY_INTEGRITY = "memory_integrity"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    DRIVER = "driver"
    SECURITY = "security"
    SYSTEM = "system"
    DISK = "disk"
    MEMORY = "memory"
    NETWORK = "network"
    APPLICATION = "application"


@dataclass
class EventEntry:
    """Windows Event Log entry"""

    id: int
    level: str
    severity: EventSeverity
    category: EventCategory
    source: str
    log_name: str
    time_created: str
    message: str
    computer: str
    keywords: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "level": self.level,
            "severity": self.severity.value,
            "category": self.category.value,
            "source": self.source,
            "log_name": self.log_name,
            "time_created": self.time_created,
            "message": self.message,
            "computer": self.computer,
            "keywords": self.keywords
        }


@dataclass
class SystemHealthReport:
    """System health report"""

    timestamp: str
    memory_integrity_issues: List[EventEntry]
    hardware_issues: List[EventEntry]
    software_issues: List[EventEntry]
    driver_issues: List[EventEntry]
    disk_issues: List[EventEntry]
    memory_issues: List[EventEntry]
    network_issues: List[EventEntry]
    security_issues: List[EventEntry]
    critical_events: List[EventEntry]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "memory_integrity_issues": [e.to_dict() for e in self.memory_integrity_issues],
            "hardware_issues": [e.to_dict() for e in self.hardware_issues],
            "software_issues": [e.to_dict() for e in self.software_issues],
            "driver_issues": [e.to_dict() for e in self.driver_issues],
            "disk_issues": [e.to_dict() for e in self.disk_issues],
            "memory_issues": [e.to_dict() for e in self.memory_issues],
            "network_issues": [e.to_dict() for e in self.network_issues],
            "security_issues": [e.to_dict() for e in self.security_issues],
            "critical_events": [e.to_dict() for e in self.critical_events],
            "summary": self.summary
        }


class WindowsEventMonitor:
    """Windows Event Viewer monitoring and analysis"""

    # Memory Integrity related Event IDs
    MEMORY_INTEGRITY_EVENT_IDS = {
        3076: "Memory Integrity blocked a driver from loading",
        3077: "Memory Integrity blocked code from running",
        3099: "Memory Integrity service error",
        3033: "Code Integrity: Driver/DLL did not meet Windows signing requirements (BLOCKS Memory Integrity)",
        3034: "Hyper-V/VBS service failed to start",
        3089: "Code Integrity event",
    }

    # Hardware related Event IDs
    HARDWARE_EVENT_IDS = {
        15: "Disk timeout",
        51: "Disk error",
        7: "Disk driver error",
        9: "Disk controller error",
        129: "Storage device error",
        11: "Disk IO error",
        55: "File system corruption",
        1406: "Tape drive hardware error",
        1501: "Disk full",
        1511: "Disk media failure",
        6008: "Unexpected system shutdown",
        41: "Kernel power system crash",
        1076: "Unexpected shutdown",
        6009: "System startup",
        6010: "System shutdown",
        1001: "Application hang",
    }

    # Memory related Event IDs
    MEMORY_EVENT_IDS = {
        2001: "Memory leak detected",
        2019: "Memory allocation failure",
        2020: "Low virtual memory",
        46: "Application memory limit",
        47: "Physical memory dump",
        161: "Dump file creation failed",
        1000: "Application crash",
    }

    # Driver related Event IDs
    DRIVER_EVENT_IDS = {
        219: "Driver loaded",
        220: "Driver unloaded",
        7034: "Service crashed",
        7038: "Service startup failure",
        7023: "Service terminated",
        7022: "Service hung",
        7000: "Service failed to start",
        7009: "Service timeout",
        7011: "Service stop timeout",
    }

    # Network related Event IDs
    NETWORK_EVENT_IDS = {
        5719: "Network adapter not found",
        5712: "Network adapter error",
        5004: "DNS client configuration error",
        5007: "DNS client configuration change",
        10400: "Network interface disabled",
        1058: "Network adapter error",
    }

    # Security related Event IDs
    SECURITY_EVENT_IDS = {
        4624: "Successful logon",
        4625: "Failed logon attempt",
        4648: "Explicit credential logon",
        4672: "Special privileges assigned",
        4688: "New process created",
        4697: "Service installed",
        4698: "Scheduled task created",
        4702: "Audit policy change",
        4719: "System audit policy changed",
        4738: "User account changed",
        4739: "Domain policy changed",
        4755: "Security group member added",
        4767: "User account unlocked",
        4776: "Domain controller attempted to validate credentials",
    }

    def __init__(self, hours_back: int = 24) -> None:
        """
        Initialize event monitor.

        Args:
            hours_back: Number of hours to look back for events (default: 24)
        """
        self.logger = logger
        self.hours_back = hours_back
        self.start_time = datetime.now() - timedelta(hours=hours_back)

    def get_events_powershell(
        self,
        log_name: str,
        event_ids: Optional[List[int]] = None,
        level: Optional[List[str]] = None,
        max_events: int = 1000,
        start_time: Optional[datetime] = None
    ) -> List[EventEntry]:
        """
        Get events from Event Viewer using PowerShell.

        Args:
            log_name: Name of the event log
            event_ids: Optional list of event IDs to filter
            level: Optional list of levels to filter (Error, Warning, Information)
            max_events: Maximum number of events to retrieve
            start_time: Optional start time for filtering events

        Returns:
            List of EventEntry objects
        """
        entries: List[EventEntry] = []

        try:
            # Build filter hashtable
            filter_parts = [f"LogName='{log_name}'"]

            if start_time:
                filter_parts.append(f"StartTime=[DateTime]::Parse('{start_time.isoformat()}')")

            if event_ids:
                ids_str = ",".join(str(eid) for eid in event_ids)
                filter_parts.append(f"ID=@({ids_str})")

            if level:
                levels_str = ",".join(f"'{lvl}'" for lvl in level)
                filter_parts.append(f"Level=@({levels_str})")

            # Build PowerShell command with better error handling
            ps_cmd = (
                f"try {{ "
                f"  $filter = @{{ {', '.join(filter_parts)} }}; "
                f"  $events = Get-WinEvent -FilterHashtable $filter "
                f"    -MaxEvents {max_events} -ErrorAction Stop; "
                f"  $events | ForEach-Object {{ "
                f"    $props = @{{"
                f"      Id = $_.Id; "
                f"      Level = $_.LevelDisplayName; "
                f"      TimeCreated = $_.TimeCreated.ToString('yyyy-MM-ddTHH:mm:ss'); "
                f"      ProviderName = $_.ProviderName; "
                f"      LogName = $_.LogName; "
                f"      Message = ($_.Message -replace '`r`n', ' ' -replace '`n', ' '); "
                f"      MachineName = $_.MachineName; "
                f"      Keywords = ($_.KeywordsDisplayNames -join ', ') "
                f"    }}; "
                f"    [PSCustomObject]$props "
                f"  }} | ConvertTo-Json -Depth 3 -Compress "
                f"}} catch {{ "
                f"  if ($_.Exception.Message -notmatch 'No events were found') {{ "
                f"    Write-Host \"Error: $($_.Exception.Message)\" "
                f"  }} "
                f"  Write-Host '[]' "
                f"}}"
            )

            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace"
            )

            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                # Handle empty array
                if output == "[]" or not output:
                    return entries

                try:
                    # PowerShell may return a single object or array
                    data = json.loads(output)
                    if not isinstance(data, list):
                        data = [data]

                    for event_data in data:
                        # Determine category
                        category = self._categorize_event(
                            event_data.get("Id", 0),
                            event_data.get("Message", ""),
                            log_name
                        )

                        # Determine severity
                        level_str = str(event_data.get("Level", "")).lower()
                        if "critical" in level_str:
                            severity = EventSeverity.CRITICAL
                        elif "error" in level_str:
                            severity = EventSeverity.ERROR
                        elif "warning" in level_str:
                            severity = EventSeverity.WARNING
                        else:
                            severity = EventSeverity.INFORMATION

                        entry = EventEntry(
                            id=event_data.get("Id", 0),
                            level=event_data.get("Level", "Unknown"),
                            severity=severity,
                            category=category,
                            source=event_data.get("ProviderName", "Unknown"),
                            log_name=event_data.get("LogName", log_name),
                            time_created=event_data.get("TimeCreated", ""),
                            message=event_data.get("Message", ""),
                            computer=event_data.get("MachineName", ""),
                            keywords=event_data.get("Keywords")
                        )
                        entries.append(entry)

                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse PowerShell JSON output: {e}")
                    self.logger.debug(f"Output: {output[:500]}")

        except Exception as e:
            self.logger.error(f"Error getting events from {log_name}: {e}")

        return entries

    def _categorize_event(self, event_id: int, message: str, log_name: str) -> EventCategory:
        """Categorize event based on ID, message, and log name"""
        message_lower = message.lower()

        # Memory Integrity events
        if event_id in self.MEMORY_INTEGRITY_EVENT_IDS:
            return EventCategory.MEMORY_INTEGRITY
        if "code integrity" in message_lower or "memory integrity" in message_lower:
            return EventCategory.MEMORY_INTEGRITY
        if "hypervisor enforced" in message_lower or "vbs" in message_lower:
            return EventCategory.MEMORY_INTEGRITY

        # Hardware events
        if event_id in self.HARDWARE_EVENT_IDS:
            return EventCategory.HARDWARE
        if "disk" in message_lower and ("error" in message_lower or "failure" in message_lower):
            return EventCategory.DISK
        if "hardware" in message_lower or "device" in message_lower:
            if "driver" not in message_lower:
                return EventCategory.HARDWARE

        # Disk events
        if event_id in [15, 51, 7, 9, 129, 11, 55, 1406, 1501, 1511]:
            return EventCategory.DISK

        # Memory events
        if event_id in self.MEMORY_EVENT_IDS or "memory" in message_lower:
            return EventCategory.MEMORY

        # Driver events
        if event_id in self.DRIVER_EVENT_IDS or "driver" in message_lower:
            return EventCategory.DRIVER

        # Network events
        if event_id in self.NETWORK_EVENT_IDS or "network" in message_lower:
            return EventCategory.NETWORK

        # Security events
        if event_id in self.SECURITY_EVENT_IDS or log_name.lower() == "security":
            return EventCategory.SECURITY

        # Application events
        if "application" in message_lower or log_name.lower() == "application":
            return EventCategory.APPLICATION

        # System/Software
        if log_name.lower() == "system":
            return EventCategory.SYSTEM

        return EventCategory.SOFTWARE

    def check_memory_integrity_events(self) -> List[EventEntry]:
        """Check for Memory Integrity blocking events"""
        self.logger.info("Checking Memory Integrity events...")

        events: List[EventEntry] = []

        # Check CodeIntegrity log - try specific IDs first, then all errors
        code_integrity_events = self.get_events_powershell(
            log_name="Microsoft-Windows-CodeIntegrity/Operational",
            event_ids=list(self.MEMORY_INTEGRITY_EVENT_IDS.keys()),
            level=["Error", "Warning", "Critical"],
            max_events=100,
            start_time=self.start_time
        )
        events.extend(code_integrity_events)

        # Always also check for all errors/warnings in CodeIntegrity log (Event ID 3033 often appears here)
        all_code_errors = self.get_events_powershell(
            log_name="Microsoft-Windows-CodeIntegrity/Operational",
            level=["Error", "Warning", "Critical"],
            max_events=50,
            start_time=self.start_time
        )
        # Add events that aren't already captured
        existing_ids = {e.id for e in events}
        new_events = [e for e in all_code_errors if e.id not in existing_ids]
        events.extend(new_events)

        # Check System log for VBS/Hyper-V errors
        system_vbs_events = self.get_events_powershell(
            log_name="System",
            event_ids=[3033, 3034],
            level=["Error", "Warning", "Critical"],
            max_events=50,
            start_time=self.start_time
        )
        events.extend(system_vbs_events)

        # Also search System log for Memory Integrity related messages
        all_system_errors = self.get_events_powershell(
            log_name="System",
            level=["Error", "Warning", "Critical"],
            max_events=200,
            start_time=self.start_time
        )

        # Filter for Memory Integrity related from System log
        memory_related = [
            e for e in all_system_errors
            if any(keyword in e.message.lower() for keyword in [
                "code integrity", "memory integrity", "hypervisor enforced",
                "virtualization based security", "vbs", "hyper-v"
            ])
        ]
        events.extend(memory_related)

        # Filter for Memory Integrity related
        memory_integrity_events = [
            e for e in events
            if e.category == EventCategory.MEMORY_INTEGRITY
        ]

        return memory_integrity_events

    def check_hardware_issues(self) -> List[EventEntry]:
        """Check for hardware issues"""
        self.logger.info("Checking hardware issues...")

        events: List[EventEntry] = []

        # Check System log for hardware errors
        hardware_events = self.get_events_powershell(
            log_name="System",
            event_ids=list(self.HARDWARE_EVENT_IDS.keys()),
            level=["Error", "Warning", "Critical"],
            max_events=200,
            start_time=self.start_time
        )
        events.extend(hardware_events)

        # Also get all errors/warnings from System log and filter for hardware
        all_system_events = self.get_events_powershell(
            log_name="System",
            level=["Error", "Warning", "Critical"],
            max_events=500,
            start_time=self.start_time
        )

        # Filter for hardware-related (exclude disk, memory, driver which have own categories)
        hardware_filtered = [
            e for e in all_system_events
            if any(keyword in e.message.lower() for keyword in [
                "hardware error", "device error", "controller error",
                "hardware failure", "unexpected shutdown", "system crash"
            ]) and e.category not in [EventCategory.DISK, EventCategory.MEMORY, EventCategory.DRIVER]
        ]
        events.extend(hardware_filtered)

        return [e for e in events if e.category == EventCategory.HARDWARE]

    def check_disk_issues(self) -> List[EventEntry]:
        """Check for disk issues"""
        self.logger.info("Checking disk issues...")

        disk_events = self.get_events_powershell(
            log_name="System",
            event_ids=[15, 51, 7, 9, 129, 11, 55, 1406, 1501, 1511],
            level=["Error", "Warning", "Critical"],
            max_events=100,
            start_time=self.start_time
        )

        return [e for e in disk_events if e.category == EventCategory.DISK]

    def check_memory_issues(self) -> List[EventEntry]:
        """Check for memory issues"""
        self.logger.info("Checking memory issues...")

        memory_events = self.get_events_powershell(
            log_name="System",
            event_ids=list(self.MEMORY_EVENT_IDS.keys()),
            level=["Error", "Warning", "Critical"],
            max_events=100,
            start_time=self.start_time
        )

        return [e for e in memory_events if e.category == EventCategory.MEMORY]

    def check_driver_issues(self) -> List[EventEntry]:
        """Check for driver issues"""
        self.logger.info("Checking driver issues...")

        driver_events = self.get_events_powershell(
            log_name="System",
            event_ids=list(self.DRIVER_EVENT_IDS.keys()),
            level=["Error", "Warning", "Critical"],
            max_events=200,
            start_time=self.start_time
        )

        return [e for e in driver_events if e.category == EventCategory.DRIVER]

    def check_network_issues(self) -> List[EventEntry]:
        """Check for network issues"""
        self.logger.info("Checking network issues...")

        network_events = self.get_events_powershell(
            log_name="System",
            event_ids=list(self.NETWORK_EVENT_IDS.keys()),
            level=["Error", "Warning", "Critical"],
            max_events=100,
            start_time=self.start_time
        )

        return [e for e in network_events if e.category == EventCategory.NETWORK]

    def check_security_issues(self) -> List[EventEntry]:
        """Check for security issues"""
        self.logger.info("Checking security issues...")

        # Only get critical security events
        security_events = self.get_events_powershell(
            log_name="Security",
            event_ids=[4625, 4648, 4672, 4697, 4698],  # Failed logons, privilege escalation, service installs
            level=["Error", "Warning", "Critical"],
            max_events=50,
            start_time=self.start_time
        )

        return [e for e in security_events if e.category == EventCategory.SECURITY]

    def check_application_issues(self) -> List[EventEntry]:
        """Check for application crashes and issues"""
        self.logger.info("Checking application issues...")

        app_events = self.get_events_powershell(
            log_name="Application",
            event_ids=[1000, 1001],  # Application crash, hang
            level=["Error", "Warning", "Critical"],
            max_events=100,
            start_time=self.start_time
        )

        # Also check System log for application errors
        system_app_events = self.get_events_powershell(
            log_name="System",
            event_ids=[1000, 1001],
            level=["Error", "Warning", "Critical"],
            max_events=50,
            start_time=self.start_time
        )
        app_events.extend(system_app_events)

        return [e for e in app_events if e.category == EventCategory.APPLICATION]

    def generate_health_report(self) -> SystemHealthReport:
        """Generate comprehensive system health report"""
        self.logger.info("Generating system health report...")

        timestamp = datetime.now().isoformat()

        # Collect all events
        memory_integrity_issues = self.check_memory_integrity_events()
        hardware_issues = self.check_hardware_issues()
        disk_issues = self.check_disk_issues()
        memory_issues = self.check_memory_issues()
        driver_issues = self.check_driver_issues()
        network_issues = self.check_network_issues()
        security_issues = self.check_security_issues()
        software_issues = self.check_application_issues()

        # Combine all issues for critical events
        all_issues = (
            memory_integrity_issues + hardware_issues + disk_issues +
            memory_issues + driver_issues + network_issues +
            security_issues + software_issues
        )

        # Filter critical/error events
        critical_events = [
            e for e in all_issues
            if e.severity == EventSeverity.ERROR or "critical" in e.level.lower()
        ]

        # Generate summary
        summary = {
            "total_issues": len(all_issues),
            "critical_errors": len(critical_events),
            "memory_integrity_blocks": len(memory_integrity_issues),
            "hardware_issues": len(hardware_issues),
            "disk_issues": len(disk_issues),
            "memory_issues": len(memory_issues),
            "driver_issues": len(driver_issues),
            "network_issues": len(network_issues),
            "security_issues": len(security_issues),
            "software_issues": len(software_issues),
            "scan_period_hours": self.hours_back,
            "scan_timestamp": timestamp
        }

        report = SystemHealthReport(
            timestamp=timestamp,
            memory_integrity_issues=memory_integrity_issues,
            hardware_issues=hardware_issues,
            software_issues=software_issues,
            driver_issues=driver_issues,
            disk_issues=disk_issues,
            memory_issues=memory_issues,
            network_issues=network_issues,
            security_issues=security_issues,
            critical_events=critical_events,
            summary=summary
        )

        return report

    def save_report(self, report: SystemHealthReport, output_path: Path) -> None:
        try:
            """Save report to JSON file"""
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, indent=2)

            self.logger.info(f"Report saved to {output_path}")


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def print_report(report: SystemHealthReport) -> None:
    """Print formatted health report"""
    print("\n" + "="*80)
    print("WINDOWS SYSTEM HEALTH REPORT")
    print("="*80 + "\n")

    print(f"Scan Period: Last {report.summary['scan_period_hours']} hours")
    print(f"Timestamp: {report.timestamp}\n")

    print("-"*80)
    print("SUMMARY")
    print("-"*80)
    print(f"Total Issues Found: {report.summary['total_issues']}")
    print(f"Critical Errors: {report.summary['critical_errors']}")
    print(f"Memory Integrity Blocks: {report.summary['memory_integrity_blocks']}")
    print(f"Hardware Issues: {report.summary['hardware_issues']}")
    print(f"Disk Issues: {report.summary['disk_issues']}")
    print(f"Memory Issues: {report.summary['memory_issues']}")
    print(f"Driver Issues: {report.summary['driver_issues']}")
    print(f"Network Issues: {report.summary['network_issues']}")
    print(f"Security Issues: {report.summary['security_issues']}")
    print(f"Software Issues: {report.summary['software_issues']}")

    # Memory Integrity Issues
    if report.memory_integrity_issues:
        print("\n" + "="*80)
        print("[CRITICAL] MEMORY INTEGRITY BLOCKING EVENTS")
        print("="*80)
        for event in report.memory_integrity_issues[:10]:  # Show first 10
            print(f"\nEvent ID: {event.id}")
            print(f"Time: {event.time_created}")
            print(f"Level: {event.level}")
            print(f"Source: {event.source}")
            print(f"Message: {event.message[:300]}...")

    # Critical Events
    if report.critical_events:
        print("\n" + "="*80)
        print("[CRITICAL] CRITICAL SYSTEM ERRORS")
        print("="*80)
        for event in report.critical_events[:20]:  # Show first 20
            print(f"\nEvent ID: {event.id} | {event.category.value.upper()}")
            print(f"Time: {event.time_created}")
            print(f"Level: {event.level}")
            print(f"Source: {event.source}")
            print(f"Message: {event.message[:300]}...")

    # Hardware Issues
    if report.hardware_issues:
        print("\n" + "-"*80)
        print("HARDWARE ISSUES")
        print("-"*80)
        for event in report.hardware_issues[:10]:
            print(f"\n[{event.id}] {event.time_created} - {event.source}")
            print(f"  {event.message[:200]}...")

    # Driver Issues
    if report.driver_issues:
        print("\n" + "-"*80)
        print("DRIVER ISSUES")
        print("-"*80)
        for event in report.driver_issues[:10]:
            print(f"\n[{event.id}] {event.time_created} - {event.source}")
            print(f"  {event.message[:200]}...")

    # Disk Issues
    if report.disk_issues:
        print("\n" + "-"*80)
        print("DISK ISSUES")
        print("-"*80)
        for event in report.disk_issues[:10]:
            print(f"\n[{event.id}] {event.time_created} - {event.source}")
            print(f"  {event.message[:200]}...")

    print("\n" + "="*80 + "\n")


def main() -> int:
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor Windows Event Viewer for system health issues"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/windows_event_health_report.json"),
        help="Path to save report JSON"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously monitor events (refresh every 5 minutes)"
    )

    args = parser.parse_args()

    monitor = WindowsEventMonitor(hours_back=args.hours)

    if args.watch:
        print("[INFO] Starting continuous monitoring mode...")
        print("[INFO] Press Ctrl+C to stop\n")

        try:
            while True:
                report = monitor.generate_health_report()
                print_report(report)
                monitor.save_report(report, args.report)

                print(f"\n[INFO] Next scan in 5 minutes... (Report saved to {args.report})")
                import time
                time.sleep(300)  # Wait 5 minutes
        except KeyboardInterrupt:
            print("\n[INFO] Monitoring stopped by user")
            return 0
    else:
        report = monitor.generate_health_report()
        print_report(report)
        monitor.save_report(report, args.report)
        return 0


if __name__ == "__main__":



    sys.exit(main())