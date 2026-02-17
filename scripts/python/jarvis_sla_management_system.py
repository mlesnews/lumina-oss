#!/usr/bin/env python3
"""
JARVIS SLA Management System
Problem Management Team handles all Service Level Agreements (SLAs)
Notifies JARVIS of expiring and unserviced SLAs
Active management supervision - "boots on the ground" style

Tags: #SLA #PROBLEM_MANAGEMENT #DELEGATION #SUPERVISION #MANAGEMENT @JARVIS @C3PO @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("JARVISSLAManagement")
ts_logger = get_timestamp_logger()


class SLAStatus(Enum):
    """SLA status"""
    ACTIVE = "active"
    EXPIRING = "expiring"  # Within warning period
    EXPIRED = "expired"
    UNSERVICED = "unserviced"  # No service/response within SLA window
    MET = "met"
    BREACHED = "breached"
    CANCELLED = "cancelled"


class SLAPriority(Enum):
    """SLA priority"""
    CRITICAL = "critical"  # < 1 hour
    HIGH = "high"  # < 4 hours
    MEDIUM = "medium"  # < 24 hours
    LOW = "low"  # < 72 hours


@dataclass
class SLA:
    """Service Level Agreement"""
    sla_id: str
    title: str
    description: str
    ticket_id: Optional[str] = None  # Related helpdesk ticket
    team_id: str = ""  # Team responsible
    priority: SLAPriority = SLAPriority.MEDIUM
    status: SLAStatus = SLAStatus.ACTIVE

    # Time windows
    created_at: str = ""
    expires_at: str = ""
    warning_threshold_hours: int = 24  # Warn when this many hours before expiration
    response_time_hours: int = 4  # Expected response time

    # Tracking
    last_service_at: Optional[str] = None
    service_count: int = 0
    unserviced_since: Optional[str] = None

    # Management
    assigned_to: Optional[str] = None
    manager_oversight: bool = True  # Requires active management supervision
    escalation_level: int = 0

    # Metadata
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.tags:
            self.tags = []
        if not self.metadata:
            self.metadata = {}

    def is_expiring(self) -> bool:
        """Check if SLA is expiring soon"""
        if not self.expires_at:
            return False

        expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        warning_time = expires - timedelta(hours=self.warning_threshold_hours)
        now = datetime.now(expires.tzinfo if expires.tzinfo else None)

        return warning_time <= now < expires

    def is_expired(self) -> bool:
        """Check if SLA has expired"""
        if not self.expires_at:
            return False

        expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        now = datetime.now(expires.tzinfo if expires.tzinfo else None)

        return now >= expires

    def is_unserviced(self) -> bool:
        """Check if SLA is unserviced (no service within response time)"""
        if not self.last_service_at:
            if self.unserviced_since:
                # Check if unserviced time exceeds response time
                unserviced = datetime.fromisoformat(self.unserviced_since.replace('Z', '+00:00'))
                now = datetime.now(unserviced.tzinfo if unserviced.tzinfo else None)
                hours_unserviced = (now - unserviced).total_seconds() / 3600
                return hours_unserviced > self.response_time_hours
            return False

        last_service = datetime.fromisoformat(self.last_service_at.replace('Z', '+00:00'))
        now = datetime.now(last_service.tzinfo if last_service.tzinfo else None)
        hours_since_service = (now - last_service).total_seconds() / 3600

        return hours_since_service > self.response_time_hours

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data


class JARVISSLAManagementSystem:
    """
    JARVIS SLA Management System

    Problem Management Team handles all SLAs with active supervision.
    Notifies JARVIS of:
    - SLAs due to expire
    - Unserviced SLAs
    - SLA breaches

    Management Philosophy: "Boots on the ground" - active top-down supervision
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SLA Management System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.slas: List[SLA] = []
        self.sla_file = project_root / "data" / "system" / "slas.json"

        # Load existing SLAs
        self._load_slas()

        logger.info("✅ JARVIS SLA Management System initialized")
        logger.info("   Team: Problem Management")
        logger.info("   Philosophy: Active supervision - 'boots on the ground'")

    def _load_slas(self):
        """Load SLAs from storage"""
        if self.sla_file.exists():
            try:
                with open(self.sla_file, 'r') as f:
                    data = json.load(f)
                    self.slas = [SLA(**sla_data) for sla_data in data.get("slas", [])]
                logger.info(f"   Loaded {len(self.slas)} SLAs")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load SLAs: {e}")
                self.slas = []
        else:
            self.slas = []

    def _save_slas(self):
        try:
            """Save SLAs to storage"""
            self.sla_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sla_file, 'w') as f:
                json.dump({
                    "slas": [sla.to_dict() for sla in self.slas],
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_slas: {e}", exc_info=True)
            raise
    def create_sla(
        self,
        title: str,
        description: str,
        ticket_id: Optional[str] = None,
        team_id: str = "",
        priority: SLAPriority = SLAPriority.MEDIUM,
        expires_at: Optional[str] = None,
        response_time_hours: int = 4,
        warning_threshold_hours: int = 24
    ) -> SLA:
        """Create a new SLA"""
        sla_id = f"SLA{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if not expires_at:
            # Default: 7 days from now
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()

        sla = SLA(
            sla_id=sla_id,
            title=title,
            description=description,
            ticket_id=ticket_id,
            team_id=team_id,
            priority=priority,
            status=SLAStatus.ACTIVE,
            expires_at=expires_at,
            response_time_hours=response_time_hours,
            warning_threshold_hours=warning_threshold_hours,
            manager_oversight=True
        )

        self.slas.append(sla)
        self._save_slas()

        logger.info(f"✅ Created SLA {sla_id}: {title}")

        return sla

    def check_expiring_slas(self) -> List[SLA]:
        """Check for SLAs expiring soon"""
        expiring = [sla for sla in self.slas if sla.is_expiring() and sla.status == SLAStatus.ACTIVE]
        return expiring

    def check_expired_slas(self) -> List[SLA]:
        """Check for expired SLAs"""
        expired = [sla for sla in self.slas if sla.is_expired() and sla.status != SLAStatus.EXPIRED]

        # Update status
        for sla in expired:
            sla.status = SLAStatus.EXPIRED

        if expired:
            self._save_slas()

        return expired

    def check_unserviced_slas(self) -> List[SLA]:
        """Check for unserviced SLAs"""
        unserviced = [sla for sla in self.slas if sla.is_unserviced() and sla.status == SLAStatus.ACTIVE]

        # Update status
        for sla in unserviced:
            if sla.status == SLAStatus.ACTIVE:
                sla.status = SLAStatus.UNSERVICED
                if not sla.unserviced_since:
                    sla.unserviced_since = datetime.now().isoformat()

        if unserviced:
            self._save_slas()

        return unserviced

    def notify_jarvis(self, slas: List[SLA], notification_type: str) -> Dict[str, Any]:
        """Notify JARVIS about SLA issues"""
        logger.info("=" * 80)
        logger.info(f"📢 NOTIFYING JARVIS: {notification_type.upper()}")
        logger.info("=" * 80)

        notifications = []

        for sla in slas:
            notification = {
                "sla_id": sla.sla_id,
                "title": sla.title,
                "ticket_id": sla.ticket_id,
                "team_id": sla.team_id,
                "priority": sla.priority.value,
                "status": sla.status.value,
                "notification_type": notification_type,
                "timestamp": datetime.now().isoformat(),
                "requires_management_oversight": sla.manager_oversight
            }

            if notification_type == "expiring":
                notification["expires_at"] = sla.expires_at
                notification["hours_until_expiration"] = (
                    datetime.fromisoformat(sla.expires_at.replace('Z', '+00:00')) -
                    datetime.now()
                ).total_seconds() / 3600

            elif notification_type == "expired":
                notification["expires_at"] = sla.expires_at
                notification["hours_overdue"] = (
                    datetime.now() -
                    datetime.fromisoformat(sla.expires_at.replace('Z', '+00:00'))
                ).total_seconds() / 3600

            elif notification_type == "unserviced":
                notification["last_service_at"] = sla.last_service_at
                notification["unserviced_since"] = sla.unserviced_since
                notification["response_time_hours"] = sla.response_time_hours
                if sla.unserviced_since:
                    notification["hours_unserviced"] = (
                        datetime.now() -
                        datetime.fromisoformat(sla.unserviced_since.replace('Z', '+00:00'))
                    ).total_seconds() / 3600

            notifications.append(notification)

            logger.warning(f"⚠️  {notification_type.upper()}: {sla.sla_id} - {sla.title}")
            logger.warning(f"   Team: {sla.team_id} | Priority: {sla.priority.value}")
            if sla.ticket_id:
                logger.warning(f"   Ticket: {sla.ticket_id}")

        # Save notifications
        notification_file = self.project_root / "data" / "system" / f"sla_notifications_{datetime.now().strftime('%Y%m%d')}.json"
        notification_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing notifications and append
        existing_notifications = []
        if notification_file.exists():
            try:
                with open(notification_file, 'r') as f:
                    existing_notifications = json.load(f).get("notifications", [])
            except:
                pass

        existing_notifications.extend(notifications)

        with open(notification_file, 'w') as f:
            json.dump({
                "notifications": existing_notifications,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, default=str)

        logger.info(f"📊 Total {notification_type} SLAs: {len(notifications)}")
        logger.info(f"   ✅ Notifications saved: {notification_file}")

        return {
            "notification_type": notification_type,
            "count": len(notifications),
            "notifications": notifications,
            "timestamp": datetime.now().isoformat()
        }

    def monitor_slas(self) -> Dict[str, Any]:
        """Monitor all SLAs and notify JARVIS of issues"""
        logger.info("=" * 80)
        logger.info("🔍 PROBLEM MANAGEMENT: SLA Monitoring & Supervision")
        logger.info("=" * 80)
        logger.info("   Active supervision - 'boots on the ground' management")

        # Check expiring SLAs
        expiring = self.check_expiring_slas()
        if expiring:
            logger.warning(f"⚠️  Found {len(expiring)} expiring SLAs")
            self.notify_jarvis(expiring, "expiring")

        # Check expired SLAs
        expired = self.check_expired_slas()
        if expired:
            logger.error(f"❌ Found {len(expired)} expired SLAs")
            self.notify_jarvis(expired, "expired")

        # Check unserviced SLAs
        unserviced = self.check_unserviced_slas()
        if unserviced:
            logger.error(f"❌ Found {len(unserviced)} unserviced SLAs")
            self.notify_jarvis(unserviced, "unserviced")

        # Summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_slas": len(self.slas),
            "active": len([s for s in self.slas if s.status == SLAStatus.ACTIVE]),
            "expiring": len(expiring),
            "expired": len(expired),
            "unserviced": len(unserviced),
            "requires_management_oversight": len([s for s in self.slas if s.manager_oversight])
        }

        logger.info(f"\n📊 SLA Monitoring Summary:")
        logger.info(f"   Total SLAs: {summary['total_slas']}")
        logger.info(f"   Active: {summary['active']}")
        logger.info(f"   ⚠️  Expiring: {summary['expiring']}")
        logger.info(f"   ❌ Expired: {summary['expired']}")
        logger.info(f"   ❌ Unserviced: {summary['unserviced']}")
        logger.info(f"   👔 Requires Management Oversight: {summary['requires_management_oversight']}")

        return summary

    def record_service(self, sla_id: str, service_notes: str = "") -> Dict[str, Any]:
        """Record service/response for an SLA"""
        sla = next((s for s in self.slas if s.sla_id == sla_id), None)

        if not sla:
            return {"status": "error", "error": f"SLA {sla_id} not found"}

        sla.last_service_at = datetime.now().isoformat()
        sla.service_count += 1

        if sla.status == SLAStatus.UNSERVICED:
            sla.status = SLAStatus.ACTIVE
            sla.unserviced_since = None

        self._save_slas()

        logger.info(f"✅ Recorded service for SLA {sla_id}")
        logger.info(f"   Service count: {sla.service_count}")

        return {
            "status": "success",
            "sla_id": sla_id,
            "service_count": sla.service_count,
            "last_service_at": sla.last_service_at
        }

    def get_management_dashboard(self) -> Dict[str, Any]:
        try:
            """Get management dashboard for top-down supervision"""
            logger.info("📊 Generating Management Dashboard...")

            # Categorize SLAs
            by_status = {}
            by_team = {}
            by_priority = {}

            for sla in self.slas:
                # By status
                status = sla.status.value
                by_status[status] = by_status.get(status, 0) + 1

                # By team
                team = sla.team_id or "unassigned"
                if team not in by_team:
                    by_team[team] = []
                by_team[team].append(sla.to_dict())

                # By priority
                priority = sla.priority.value
                by_priority[priority] = by_priority.get(priority, 0) + 1

            # Critical items requiring immediate attention
            critical_items = []
            for sla in self.slas:
                if sla.status in [SLAStatus.EXPIRED, SLAStatus.UNSERVICED]:
                    critical_items.append(sla.to_dict())
                elif sla.is_expiring() and sla.priority in [SLAPriority.CRITICAL, SLAPriority.HIGH]:
                    critical_items.append(sla.to_dict())

            dashboard = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_slas": len(self.slas),
                    "by_status": by_status,
                    "by_priority": by_priority,
                    "by_team": {team: len(slas) for team, slas in by_team.items()}
                },
                "critical_items": critical_items,
                "requires_oversight": len([s for s in self.slas if s.manager_oversight]),
                "teams": by_team
            }

            # Save dashboard
            dashboard_file = self.project_root / "data" / "system" / "sla_management_dashboard.json"
            dashboard_file.parent.mkdir(parents=True, exist_ok=True)
            with open(dashboard_file, 'w') as f:
                json.dump(dashboard, f, indent=2, default=str)

            logger.info(f"   ✅ Dashboard saved: {dashboard_file}")

            return dashboard


        except Exception as e:
            self.logger.error(f"Error in get_management_dashboard: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS SLA Management System")
        parser.add_argument("--monitor", action="store_true", help="Monitor SLAs and notify JARVIS")
        parser.add_argument("--dashboard", action="store_true", help="Generate management dashboard")
        parser.add_argument("--create", action="store_true", help="Create new SLA")
        parser.add_argument("--service", type=str, help="Record service for SLA (provide SLA ID)")

        args = parser.parse_args()

        print("="*80)
        print("📋 JARVIS SLA MANAGEMENT SYSTEM")
        print("="*80)
        print()
        print("Team: Problem Management")
        print("Philosophy: Active supervision - 'boots on the ground'")
        print()

        system = JARVISSLAManagementSystem()

        if args.monitor:
            summary = system.monitor_slas()
            print()
            print("="*80)
            print("✅ MONITORING COMPLETE")
            print("="*80)
            print(f"Expiring: {summary['expiring']}")
            print(f"Expired: {summary['expired']}")
            print(f"Unserviced: {summary['unserviced']}")

        elif args.dashboard:
            dashboard = system.get_management_dashboard()
            print()
            print("="*80)
            print("📊 MANAGEMENT DASHBOARD")
            print("="*80)
            print(json.dumps(dashboard, indent=2, default=str))

        elif args.service:
            result = system.record_service(args.service)
            print(json.dumps(result, indent=2, default=str))

        elif args.create:
            # Interactive SLA creation
            title = input("SLA Title: ")
            description = input("Description: ")
            ticket_id = input("Ticket ID (optional): ") or None
            team_id = input("Team ID: ")

            sla = system.create_sla(
                title=title,
                description=description,
                ticket_id=ticket_id,
                team_id=team_id
            )
            print(f"✅ Created SLA: {sla.sla_id}")

        else:
            # Default: monitor
            summary = system.monitor_slas()
            print()
            print("="*80)
            print("✅ MONITORING COMPLETE")
            print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()