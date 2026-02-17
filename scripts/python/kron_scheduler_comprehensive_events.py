#!/usr/bin/env python3
"""
Kron Scheduler - Comprehensive Internal & External Recurring Events

Manages all recurring events for:
- Internal: email, SMS, messenger, documentation, @holocrons
- External: all @sources for both internal and external systems

Integrates with:
- NAS KronScheduler
- SYPHON system
- Holocron archive
- Unified queue adapter
- Triage/BAU coordination

Tags: #KRON #SCHEDULER #INTERNAL #EXTERNAL #EMAIL #SMS #MESSENGER #DOCUMENTATION #HOLOCRON #SOURCES @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KronSchedulerComprehensive")

# Import required modules
try:
    from nas_cron_scheduler import NASCronScheduler, CronJob
    NAS_SCHEDULER_AVAILABLE = True
except ImportError:
    NAS_SCHEDULER_AVAILABLE = False
    logger.warning("   ⚠️  NAS Cron Scheduler not available")

try:
    from nas_kron_triage_coordinator import NASKronTriageCoordinator, PriorityLevel, EventType, CoordinatedEvent
    TRIAGE_COORDINATOR_AVAILABLE = True
except ImportError:
    TRIAGE_COORDINATOR_AVAILABLE = False
    CoordinatedEvent = None
    logger.warning("   ⚠️  NAS Kron Triage Coordinator not available")


class EventCategory(Enum):
    """Event categories"""
    INTERNAL = "internal"
    EXTERNAL = "external"


class InternalEventType(Enum):
    """Internal event types"""
    EMAIL = "email"
    SMS = "sms"
    MESSENGER = "messenger"
    DOCUMENTATION = "documentation"
    HOLOCRON = "holocron"


class ExternalEventType(Enum):
    """External event types"""
    SOURCE_SYPHON = "source_syphon"
    WEB_CRAWL = "web_crawl"
    API_POLL = "api_poll"
    SOCIAL_MEDIA = "social_media"
    NEWS_FEED = "news_feed"
    RSS_FEED = "rss_feed"


@dataclass
class KronScheduledEvent:
    """Kron scheduled event definition"""
    event_id: str
    name: str
    description: str
    category: EventCategory
    event_type: str  # InternalEventType or ExternalEventType value
    schedule: str  # Cron expression
    command: str
    script_path: Optional[str] = None
    enabled: bool = True
    priority: PriorityLevel = PriorityLevel.MEDIUM
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(data.get("category"), Enum):
            data["category"] = data["category"].value
        if isinstance(data.get("priority"), Enum):
            data["priority"] = data["priority"].value
        if data.get("last_run"):
            data["last_run"] = str(data["last_run"])
        if data.get("next_run"):
            data["next_run"] = str(data["next_run"])
        return data


class KronSchedulerComprehensive:
    """
    Kron Scheduler - Comprehensive Internal & External Recurring Events

    Manages all recurring events for internal and external systems.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize comprehensive kron scheduler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "kron_scheduler"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.events_file = self.data_dir / "scheduled_events.json"

        # Systems
        self.nas_scheduler = NASCronScheduler(project_root) if NAS_SCHEDULER_AVAILABLE else None
        self.triage_coordinator = NASKronTriageCoordinator(project_root) if TRIAGE_COORDINATOR_AVAILABLE else None

        # Events
        self.scheduled_events: Dict[str, KronScheduledEvent] = {}

        # Load existing events
        self._load_events()

        # Initialize all event types
        self._initialize_internal_events()
        self._initialize_external_events()

        # Save events
        self._save_events()

        logger.info("✅ Kron Scheduler Comprehensive initialized")
        logger.info(f"   Internal events: {len([e for e in self.scheduled_events.values() if e.category == EventCategory.INTERNAL])}")
        logger.info(f"   External events: {len([e for e in self.scheduled_events.values() if e.category == EventCategory.EXTERNAL])}")
        logger.info(f"   Total events: {len(self.scheduled_events)}")

    def _load_events(self):
        """Load scheduled events"""
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    for event_id, event_data in data.items():
                        # Convert category and priority back to enums
                        if "category" in event_data:
                            event_data["category"] = EventCategory(event_data["category"])
                        if "priority" in event_data:
                            event_data["priority"] = PriorityLevel(event_data["priority"])
                        self.scheduled_events[event_id] = KronScheduledEvent(**event_data)
            except Exception as e:
                logger.debug(f"   Could not load events: {e}")

    def _save_events(self):
        """Save scheduled events"""
        try:
            with open(self.events_file, 'w') as f:
                json.dump({
                    event_id: event.to_dict()
                    for event_id, event in self.scheduled_events.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving events: {e}")

    def _initialize_internal_events(self):
        """Initialize internal recurring events"""
        base_path = "/volume1/docker/lumina"

        # ========== EMAIL EVENTS ==========
        if "internal_email_syphon_all" not in self.scheduled_events:
            self.scheduled_events["internal_email_syphon_all"] = KronScheduledEvent(
                event_id="internal_email_syphon_all",
                name="SYPHON All Email Accounts",
                description="SYPHON all email accounts (secure and unsecure) for data mining and holocron archive",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.EMAIL.value,
                schedule="0 */2 * * *",  # Every 2 hours
                command=f"python {base_path}/scripts/python/syphon_all_emails_to_holocron_youtube.py",
                script_path="scripts/python/syphon_all_emails_to_holocron_youtube.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["email", "syphon", "holocron", "internal", "recurring"]
            )

        if "internal_email_backup" not in self.scheduled_events:
            self.scheduled_events["internal_email_backup"] = KronScheduledEvent(
                event_id="internal_email_backup",
                name="Email Backup to Holocron",
                description="Backup all email messages to holocron archive",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.EMAIL.value,
                schedule="0 3 * * *",  # Daily at 3 AM
                command=f"python {base_path}/scripts/python/syphon_all_emails_to_holocron_youtube.py --backup-only",
                script_path="scripts/python/syphon_all_emails_to_holocron_youtube.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["email", "backup", "holocron", "internal"]
            )

        # ========== SMS EVENTS ==========
        if "internal_sms_syphon_all" not in self.scheduled_events:
            self.scheduled_events["internal_sms_syphon_all"] = KronScheduledEvent(
                event_id="internal_sms_syphon_all",
                name="SYPHON All SMS Messages",
                description="SYPHON all SMS/text messages for data mining and holocron archive",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.SMS.value,
                schedule="0 */3 * * *",  # Every 3 hours
                command=f"python {base_path}/scripts/python/syphon_all_sms_to_holocron_youtube.py",
                script_path="scripts/python/syphon_all_sms_to_holocron_youtube.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["sms", "syphon", "holocron", "internal", "recurring"]
            )

        if "internal_sms_backup" not in self.scheduled_events:
            self.scheduled_events["internal_sms_backup"] = KronScheduledEvent(
                event_id="internal_sms_backup",
                name="SMS Backup to Holocron",
                description="Backup all SMS messages to holocron archive",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.SMS.value,
                schedule="0 4 * * *",  # Daily at 4 AM
                command=f"python {base_path}/scripts/python/syphon_all_sms_to_holocron_youtube.py --backup-only",
                script_path="scripts/python/syphon_all_sms_to_holocron_youtube.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["sms", "backup", "holocron", "internal"]
            )

        # ========== MESSENGER EVENTS ==========
        # Note: Messenger integration scripts would need to be created
        if "internal_messenger_syphon" not in self.scheduled_events:
            self.scheduled_events["internal_messenger_syphon"] = KronScheduledEvent(
                event_id="internal_messenger_syphon",
                name="SYPHON Messenger Platforms",
                description="SYPHON all messenger platforms (Telegram, Discord, Slack, WhatsApp, etc.) for data mining",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.MESSENGER.value,
                schedule="0 */4 * * *",  # Every 4 hours
                command=f"python {base_path}/scripts/python/syphon_all_messengers_to_holocron.py",
                script_path="scripts/python/syphon_all_messengers_to_holocron.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["messenger", "syphon", "holocron", "internal", "recurring"],
                metadata={
                    "platforms": ["telegram", "discord", "slack", "whatsapp", "signal"],
                    "note": "Script needs to be created"
                }
            )

        # ========== DOCUMENTATION EVENTS ==========
        if "internal_documentation_sync" not in self.scheduled_events:
            self.scheduled_events["internal_documentation_sync"] = KronScheduledEvent(
                event_id="internal_documentation_sync",
                name="Documentation Sync to Holocron",
                description="Sync all documentation to holocron archive",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.DOCUMENTATION.value,
                schedule="0 1 * * *",  # Daily at 1 AM
                command=f"python {base_path}/scripts/python/sync_documentation_to_holocron.py",
                script_path="scripts/python/sync_documentation_to_holocron.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["documentation", "sync", "holocron", "internal"]
            )

        if "internal_documentation_backup" not in self.scheduled_events:
            self.scheduled_events["internal_documentation_backup"] = KronScheduledEvent(
                event_id="internal_documentation_backup",
                name="Documentation Backup",
                description="Backup all documentation files",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.DOCUMENTATION.value,
                schedule="0 5 * * 0",  # Weekly on Sunday at 5 AM
                command=f"python {base_path}/scripts/python/backup_documentation.py",
                script_path="scripts/python/backup_documentation.py",
                enabled=True,
                priority=PriorityLevel.LOW,
                tags=["documentation", "backup", "internal"]
            )

        # ========== HOLOCRON EVENTS ==========
        if "internal_holocron_backup" not in self.scheduled_events:
            self.scheduled_events["internal_holocron_backup"] = KronScheduledEvent(
                event_id="internal_holocron_backup",
                name="Holocron Database Backup",
                description="Backup all holocron databases",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.HOLOCRON.value,
                schedule="0 2 * * *",  # Daily at 2 AM
                command=f"python {base_path}/scripts/python/backup_mariadb_holocrons.py",
                script_path="scripts/python/backup_mariadb_holocrons.py",
                enabled=True,
                priority=PriorityLevel.CRITICAL,
                tags=["holocron", "backup", "database", "internal", "critical"]
            )

        if "internal_holocron_scheduled_backups" not in self.scheduled_events:
            self.scheduled_events["internal_holocron_scheduled_backups"] = KronScheduledEvent(
                event_id="internal_holocron_scheduled_backups",
                name="Holocron Scheduled Backups",
                description="Run scheduled holocron backup jobs",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.HOLOCRON.value,
                schedule="0 */6 * * *",  # Every 6 hours
                command=f"python {base_path}/scripts/python/schedule_holocron_backups.py",
                script_path="scripts/python/schedule_holocron_backups.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["holocron", "backup", "scheduled", "internal"]
            )

        if "internal_holocron_sync" not in self.scheduled_events:
            self.scheduled_events["internal_holocron_sync"] = KronScheduledEvent(
                event_id="internal_holocron_sync",
                name="Holocron Sync",
                description="Sync holocron data across systems",
                category=EventCategory.INTERNAL,
                event_type=InternalEventType.HOLOCRON.value,
                schedule="0 */8 * * *",  # Every 8 hours
                command=f"python {base_path}/scripts/python/sync_holocrons.py",
                script_path="scripts/python/sync_holocrons.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["holocron", "sync", "internal"]
            )

    def _initialize_external_events(self):
        """Initialize external recurring events (all @sources)"""
        base_path = "/volume1/docker/lumina"

        # ========== SOURCE SYPHON EVENTS ==========
        if "external_source_syphon_hourly" not in self.scheduled_events:
            self.scheduled_events["external_source_syphon_hourly"] = KronScheduledEvent(
                event_id="external_source_syphon_hourly",
                name="SYPHON Sources - Hourly",
                description="SYPHON all external sources hourly for intelligence gathering",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 * * * *",  # Every hour
                command=f"python {base_path}/scripts/python/syphon_lumina_hourly_nas_kron.py",
                script_path="scripts/python/syphon_lumina_hourly_nas_kron.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["syphon", "sources", "external", "hourly", "recurring"]
            )

        if "external_source_syphon_daily_sweep" not in self.scheduled_events:
            self.scheduled_events["external_source_syphon_daily_sweep"] = KronScheduledEvent(
                event_id="external_source_syphon_daily_sweep",
                name="SYPHON Sources - Daily Sweep",
                description="Daily comprehensive sweep of all external sources",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 6 * * *",  # Daily at 6 AM
                command=f"python {base_path}/scripts/python/daily_source_sweeps_nas_kron_executor.py",
                script_path="scripts/python/daily_source_sweeps_nas_kron_executor.py",
                enabled=True,
                priority=PriorityLevel.CRITICAL,
                tags=["syphon", "sources", "external", "daily", "sweep", "critical"]
            )

        if "syphon_source_sweeps_scans" not in self.scheduled_events:
            self.scheduled_events["syphon_source_sweeps_scans"] = KronScheduledEvent(
                event_id="syphon_source_sweeps_scans",
                name="SYPHON Source Sweeps & Scans",
                description="Comprehensive source sweeps and scans for all sources (internal and external)",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="*/30 * * * *",  # Every 30 minutes
                command=f"python {base_path}/scripts/python/syphon_source_sweeps_scans.py",
                script_path="scripts/python/syphon_source_sweeps_scans.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["syphon", "sources", "sweeps", "scans", "internal", "external", "recurring"]
            )

        # ========== WEB CRAWL EVENTS ==========
        if "external_web_crawl_scheduled" not in self.scheduled_events:
            self.scheduled_events["external_web_crawl_scheduled"] = KronScheduledEvent(
                event_id="external_web_crawl_scheduled",
                name="Web Crawl - Scheduled",
                description="Scheduled web crawling for external sources",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.WEB_CRAWL.value,
                schedule="0 */4 * * *",  # Every 4 hours
                command=f"python {base_path}/scripts/python/web_crawl_scheduled.py",
                script_path="scripts/python/web_crawl_scheduled.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["web", "crawl", "external", "sources"]
            )

        # ========== API POLL EVENTS ==========
        if "external_api_poll" not in self.scheduled_events:
            self.scheduled_events["external_api_poll"] = KronScheduledEvent(
                event_id="external_api_poll",
                name="API Poll - External Sources",
                description="Poll external APIs for new data",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.API_POLL.value,
                schedule="*/30 * * * *",  # Every 30 minutes
                command=f"python {base_path}/scripts/python/api_poll_external_sources.py",
                script_path="scripts/python/api_poll_external_sources.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["api", "poll", "external", "sources"]
            )

        # ========== SOCIAL MEDIA EVENTS ==========
        if "external_social_media_syphon" not in self.scheduled_events:
            self.scheduled_events["external_social_media_syphon"] = KronScheduledEvent(
                event_id="external_social_media_syphon",
                name="Social Media SYPHON",
                description="SYPHON social media platforms for external intelligence",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOCIAL_MEDIA.value,
                schedule="0 */2 * * *",  # Every 2 hours
                command=f"python {base_path}/scripts/python/syphon_social_media_external.py",
                script_path="scripts/python/syphon_social_media_external.py",
                enabled=True,
                priority=PriorityLevel.HIGH,
                tags=["social", "media", "syphon", "external", "sources"]
            )

        # ========== NEWS FEED EVENTS ==========
        if "external_news_feed_syphon" not in self.scheduled_events:
            self.scheduled_events["external_news_feed_syphon"] = KronScheduledEvent(
                event_id="external_news_feed_syphon",
                name="News Feed SYPHON",
                description="SYPHON news feeds for external intelligence",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.NEWS_FEED.value,
                schedule="0 */3 * * *",  # Every 3 hours
                command=f"python {base_path}/scripts/python/syphon_news_feeds_external.py",
                script_path="scripts/python/syphon_news_feeds_external.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["news", "feed", "syphon", "external", "sources"]
            )

        # ========== RSS FEED EVENTS ==========
        if "external_rss_feed_syphon" not in self.scheduled_events:
            self.scheduled_events["external_rss_feed_syphon"] = KronScheduledEvent(
                event_id="external_rss_feed_syphon",
                name="RSS Feed SYPHON",
                description="SYPHON RSS feeds for external intelligence",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.RSS_FEED.value,
                schedule="0 */2 * * *",  # Every 2 hours
                command=f"python {base_path}/scripts/python/syphon_rss_feeds_external.py",
                script_path="scripts/python/syphon_rss_feeds_external.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["rss", "feed", "syphon", "external", "sources"]
            )

        # ========== EXTERNAL SOURCES FOR INTERNAL SYSTEMS ==========
        # External sources for email
        if "external_email_sources_syphon" not in self.scheduled_events:
            self.scheduled_events["external_email_sources_syphon"] = KronScheduledEvent(
                event_id="external_email_sources_syphon",
                name="External Email Sources SYPHON",
                description="SYPHON external email sources (public archives, lists, etc.)",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 */6 * * *",  # Every 6 hours
                command=f"python {base_path}/scripts/python/syphon_external_email_sources.py",
                script_path="scripts/python/syphon_external_email_sources.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["email", "sources", "external", "syphon"]
            )

        # External sources for SMS
        if "external_sms_sources_syphon" not in self.scheduled_events:
            self.scheduled_events["external_sms_sources_syphon"] = KronScheduledEvent(
                event_id="external_sms_sources_syphon",
                name="External SMS Sources SYPHON",
                description="SYPHON external SMS sources (public databases, archives, etc.)",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 */8 * * *",  # Every 8 hours
                command=f"python {base_path}/scripts/python/syphon_external_sms_sources.py",
                script_path="scripts/python/syphon_external_sms_sources.py",
                enabled=True,
                priority=PriorityLevel.LOW,
                tags=["sms", "sources", "external", "syphon"]
            )

        # External sources for messenger
        if "external_messenger_sources_syphon" not in self.scheduled_events:
            self.scheduled_events["external_messenger_sources_syphon"] = KronScheduledEvent(
                event_id="external_messenger_sources_syphon",
                name="External Messenger Sources SYPHON",
                description="SYPHON external messenger sources (public channels, groups, etc.)",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 */4 * * *",  # Every 4 hours
                command=f"python {base_path}/scripts/python/syphon_external_messenger_sources.py",
                script_path="scripts/python/syphon_external_messenger_sources.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["messenger", "sources", "external", "syphon"]
            )

        # External sources for documentation
        if "external_documentation_sources_syphon" not in self.scheduled_events:
            self.scheduled_events["external_documentation_sources_syphon"] = KronScheduledEvent(
                event_id="external_documentation_sources_syphon",
                name="External Documentation Sources SYPHON",
                description="SYPHON external documentation sources (public docs, wikis, etc.)",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 7 * * *",  # Daily at 7 AM
                command=f"python {base_path}/scripts/python/syphon_external_documentation_sources.py",
                script_path="scripts/python/syphon_external_documentation_sources.py",
                enabled=True,
                priority=PriorityLevel.MEDIUM,
                tags=["documentation", "sources", "external", "syphon"]
            )

        # External sources for holocrons
        if "external_holocron_sources_syphon" not in self.scheduled_events:
            self.scheduled_events["external_holocron_sources_syphon"] = KronScheduledEvent(
                event_id="external_holocron_sources_syphon",
                name="External Holocron Sources SYPHON",
                description="SYPHON external holocron sources (public archives, databases, etc.)",
                category=EventCategory.EXTERNAL,
                event_type=ExternalEventType.SOURCE_SYPHON.value,
                schedule="0 8 * * *",  # Daily at 8 AM
                command=f"python {base_path}/scripts/python/syphon_external_holocron_sources.py",
                script_path="scripts/python/syphon_external_holocron_sources.py",
                enabled=True,
                priority=PriorityLevel.LOW,
                tags=["holocron", "sources", "external", "syphon"]
            )

    def get_events_by_category(self, category: EventCategory) -> List[KronScheduledEvent]:
        """Get events by category"""
        return [e for e in self.scheduled_events.values() if e.category == category]

    def get_events_by_type(self, event_type: str) -> List[KronScheduledEvent]:
        """Get events by type"""
        return [e for e in self.scheduled_events.values() if e.event_type == event_type]

    def get_enabled_events(self) -> List[KronScheduledEvent]:
        """Get all enabled events"""
        return [e for e in self.scheduled_events.values() if e.enabled]

    def deploy_to_nas(self) -> Dict[str, Any]:
        """Deploy all events to NAS cron scheduler"""
        if not self.nas_scheduler:
            logger.error("❌ NAS Scheduler not available")
            return {"success": False, "error": "NAS Scheduler not available"}

        deployed = []
        failed = []

        for event in self.get_enabled_events():
            try:
                # Convert to CronJob
                cron_job = CronJob(
                    id=event.event_id,
                    name=event.name,
                    description=event.description,
                    schedule=event.schedule,
                    command=event.command,
                    script_path=event.script_path,
                    enabled=event.enabled,
                    tags=event.tags,
                    metadata=event.metadata
                )

                # Add to NAS scheduler
                self.nas_scheduler.cron_jobs[event.event_id] = cron_job
                deployed.append(event.event_id)
                logger.info(f"   ✅ Deployed: {event.name}")
            except Exception as e:
                failed.append({"event_id": event.event_id, "error": str(e)})
                logger.error(f"   ❌ Failed to deploy {event.name}: {e}")

        # Save NAS scheduler jobs
        if deployed:
            self.nas_scheduler._save_cron_jobs()

        return {
            "success": True,
            "deployed": len(deployed),
            "failed": len(failed),
            "deployed_events": deployed,
            "failed_events": failed
        }

    def coordinate_with_triage(self) -> Dict[str, Any]:
        """Coordinate events with triage/BAU system"""
        if not self.triage_coordinator:
            logger.warning("⚠️  Triage Coordinator not available")
            return {"success": False, "error": "Triage Coordinator not available"}

        # Add all events to triage coordinator
        coordinated = []
        for event in self.get_enabled_events():
            try:
                # Create coordinated event
                coordinated_event = self.triage_coordinator.CoordinatedEvent(
                    event_id=event.event_id,
                    name=event.name,
                    event_type=EventType.KRON,
                    original_schedule=event.schedule,
                    coordinated_schedule=event.schedule,  # Will be adjusted by coordinator
                    priority=event.priority,
                    bau_category="standard",
                    tags=event.tags,
                    metadata=event.metadata
                )

                self.triage_coordinator.coordinated_events[event.event_id] = coordinated_event
                coordinated.append(event.event_id)
            except Exception as e:
                logger.error(f"   ❌ Failed to coordinate {event.name}: {e}")

        return {
            "success": True,
            "coordinated": len(coordinated),
            "coordinated_events": coordinated
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        internal_events = self.get_events_by_category(EventCategory.INTERNAL)
        external_events = self.get_events_by_category(EventCategory.EXTERNAL)
        enabled_events = self.get_enabled_events()

        # Group by type
        by_type = {}
        for event in self.scheduled_events.values():
            if event.event_type not in by_type:
                by_type[event.event_type] = []
            by_type[event.event_type].append(event)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_events": len(self.scheduled_events),
            "internal_events": len(internal_events),
            "external_events": len(external_events),
            "enabled_events": len(enabled_events),
            "disabled_events": len(self.scheduled_events) - len(enabled_events),
            "by_type": {
                event_type: len(events)
                for event_type, events in by_type.items()
            },
            "events": {
                event_id: {
                    "name": event.name,
                    "category": event.category.value,
                    "type": event.event_type,
                    "schedule": event.schedule,
                    "enabled": event.enabled,
                    "priority": event.priority.value
                }
                for event_id, event in self.scheduled_events.items()
            }
        }


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("🚀 KRON SCHEDULER - COMPREHENSIVE INTERNAL & EXTERNAL EVENTS")
    logger.info("=" * 80)
    logger.info("")

    scheduler = KronSchedulerComprehensive()

    # Generate report
    report = scheduler.generate_report()
    logger.info("📊 SCHEDULER REPORT")
    logger.info(f"   Total Events: {report['total_events']}")
    logger.info(f"   Internal: {report['internal_events']}")
    logger.info(f"   External: {report['external_events']}")
    logger.info(f"   Enabled: {report['enabled_events']}")
    logger.info(f"   Disabled: {report['disabled_events']}")
    logger.info("")

    # Deploy to NAS
    logger.info("🚀 Deploying to NAS Cron Scheduler...")
    deploy_result = scheduler.deploy_to_nas()
    if deploy_result["success"]:
        logger.info(f"   ✅ Deployed: {deploy_result['deployed']} events")
        if deploy_result["failed"] > 0:
            logger.warning(f"   ⚠️  Failed: {deploy_result['failed']} events")
    else:
        logger.error(f"   ❌ Deployment failed: {deploy_result.get('error')}")
    logger.info("")

    # Coordinate with triage
    logger.info("🔗 Coordinating with Triage/BAU System...")
    triage_result = scheduler.coordinate_with_triage()
    if triage_result["success"]:
        logger.info(f"   ✅ Coordinated: {triage_result['coordinated']} events")
    else:
        logger.warning(f"   ⚠️  Coordination failed: {triage_result.get('error')}")
    logger.info("")

    logger.info("=" * 80)
    logger.info("✅ KRON SCHEDULER COMPREHENSIVE - COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":


    main()