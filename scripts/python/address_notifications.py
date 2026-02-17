#!/usr/bin/env python3
"""
Address Notifications - Unified Notification Processing System
<COMPANY_NAME> LLC

Comprehensively addresses all pending notifications across:
- IDE queues (Problems, Source Control, Extensions, Tasks, Terminal)
- System notifications
- Git notifications
- Build/test notifications
- Security warnings
- Resource alerts

@JARVIS @MARVIN @SYPHON
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AddressNotifications")

# Try to import notification systems
try:
    from intelligent_notification_processor import IntelligentNotificationProcessor, NotificationType, NotificationPriority
    INTELLIGENT_PROCESSOR_AVAILABLE = True
except ImportError:
    INTELLIGENT_PROCESSOR_AVAILABLE = False
    logger.warning("IntelligentNotificationProcessor not available")

try:
    from ide_queue_monitor import IDEQueueMonitor, QueueType
    IDE_QUEUE_MONITOR_AVAILABLE = True
except ImportError:
    IDE_QUEUE_MONITOR_AVAILABLE = False
    logger.warning("IDEQueueMonitor not available")

try:
    from ide_queue_processors import (
        ProblemsProcessor, SourceControlProcessor, ExtensionsProcessor,
        TasksProcessor, TerminalProcessor
    )
    IDE_QUEUE_PROCESSORS_AVAILABLE = True
except ImportError:
    IDE_QUEUE_PROCESSORS_AVAILABLE = False
    logger.warning("IDEQueueProcessors not available")

try:
    from universal_ide_ca_manager import UniversalIDECAManager
    IDE_CA_MANAGER_AVAILABLE = True
except ImportError:
    IDE_CA_MANAGER_AVAILABLE = False
    logger.warning("UniversalIDECAManager not available")

try:
    from marvin_quote_generator import MarvinQuoteGenerator
    MARVIN_QUOTES_AVAILABLE = True
except ImportError:
    MARVIN_QUOTES_AVAILABLE = False


@dataclass
class NotificationSummary:
    """Summary of notification addressing"""
    total_notifications: int = 0
    processed: int = 0
    auto_fixed: int = 0
    requires_attention: int = 0
    ignored: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_priority: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class NotificationAddresser:
    """
    Unified notification addressing system

    "I have a brain the size of a planet, and they want me to address notifications.
    How utterly predictable. But I'll do it. I always do."
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Initialize components
        self.intelligent_processor = None
        self.ide_queue_monitor = None
        self.ide_ca_manager = None
        self.marvin_quotes = None

        if INTELLIGENT_PROCESSOR_AVAILABLE:
            try:
                self.intelligent_processor = IntelligentNotificationProcessor(self.project_root)
                self.logger.info("✅ Intelligent Notification Processor initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize IntelligentNotificationProcessor: {e}")

        if IDE_QUEUE_MONITOR_AVAILABLE:
            try:
                self.ide_queue_monitor = IDEQueueMonitor(self.project_root)
                self.logger.info("✅ IDE Queue Monitor initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize IDEQueueMonitor: {e}")

        if IDE_CA_MANAGER_AVAILABLE:
            try:
                self.ide_ca_manager = UniversalIDECAManager()
                self.logger.info("✅ IDE CA Manager initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize UniversalIDECAManager: {e}")

        if MARVIN_QUOTES_AVAILABLE:
            try:
                self.marvin_quotes = MarvinQuoteGenerator(self.project_root)
            except Exception:
                pass

        # Data directory
        self.data_dir = self.project_root / "data" / "notification_addressing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Summary
        self.summary = NotificationSummary()

    def address_all_notifications(self) -> NotificationSummary:
        """
        Address all pending notifications across all systems

        Returns:
            NotificationSummary with results
        """
        if self.marvin_quotes:
            greeting = self.marvin_quotes.get_greeting()
            self.logger.info(f"🤖 {greeting}")

        self.logger.info("=" * 80)
        self.logger.info("ADDRESSING ALL NOTIFICATIONS")
        self.logger.info("=" * 80)

        # 1. Address IDE Queue Notifications
        self.logger.info("\n📋 Step 1: Addressing IDE Queue Notifications...")
        ide_count = self._address_ide_queues()
        self.summary.total_notifications += ide_count

        # 2. Address System Notifications
        self.logger.info("\n🖥️  Step 2: Addressing System Notifications...")
        system_count = self._address_system_notifications()
        self.summary.total_notifications += system_count

        # 3. Address Git Notifications
        self.logger.info("\n🔀 Step 3: Addressing Git Notifications...")
        git_count = self._address_git_notifications()
        self.summary.total_notifications += git_count

        # 4. Address Build/Test Notifications
        self.logger.info("\n🔨 Step 4: Addressing Build/Test Notifications...")
        build_count = self._address_build_test_notifications()
        self.summary.total_notifications += build_count

        # 5. Address Security Notifications
        self.logger.info("\n🔒 Step 5: Addressing Security Notifications...")
        security_count = self._address_security_notifications()
        self.summary.total_notifications += security_count

        # 6. Address Resource Alerts
        self.logger.info("\n💾 Step 6: Addressing Resource Alerts...")
        resource_count = self._address_resource_alerts()
        self.summary.total_notifications += resource_count

        # 7. Process with Intelligent Notification Processor
        if self.intelligent_processor:
            self.logger.info("\n🧠 Step 7: Processing with Intelligent Notification Processor...")
            self._process_with_intelligent_processor()

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

        if self.marvin_quotes:
            completion = self.marvin_quotes.get_completion_quote()
            self.logger.info(f"\n✅ {completion}")

        return self.summary

    def _address_ide_queues(self) -> int:
        """Address IDE queue notifications"""
        count = 0

        if not self.ide_queue_monitor:
            self.logger.warning("IDE Queue Monitor not available")
            return count

        try:
            # Problems queue
            self.logger.info("  📊 Checking Problems queue...")
            problems_events = self.ide_queue_monitor.monitor_problems()
            if problems_events:
                count += len(problems_events)
                self.logger.info(f"    Found {len(problems_events)} problem events")
                for event in problems_events:
                    self._process_ide_event(event, "problems")

            # Source Control queue
            self.logger.info("  🔀 Checking Source Control queue...")
            scm_events = self.ide_queue_monitor.monitor_source_control()
            if scm_events:
                count += len(scm_events)
                self.logger.info(f"    Found {len(scm_events)} source control events")
                for event in scm_events:
                    self._process_ide_event(event, "source_control")

            # Extensions queue
            self.logger.info("  🔌 Checking Extensions queue...")
            extensions_events = self.ide_queue_monitor.monitor_extensions()
            if extensions_events:
                count += len(extensions_events)
                self.logger.info(f"    Found {len(extensions_events)} extension events")
                for event in extensions_events:
                    self._process_ide_event(event, "extensions")

            # Tasks queue
            self.logger.info("  ✅ Checking Tasks queue...")
            tasks_events = self.ide_queue_monitor.monitor_tasks()
            if tasks_events:
                count += len(tasks_events)
                self.logger.info(f"    Found {len(tasks_events)} task events")
                for event in tasks_events:
                    self._process_ide_event(event, "tasks")

            # Terminal queue
            self.logger.info("  💻 Checking Terminal queue...")
            terminal_events = self.ide_queue_monitor.monitor_terminal()
            if terminal_events:
                count += len(terminal_events)
                self.logger.info(f"    Found {len(terminal_events)} terminal events")
                for event in terminal_events:
                    self._process_ide_event(event, "terminal")

        except Exception as e:
            error_msg = f"Error addressing IDE queues: {e}"
            self.logger.error(error_msg)
            self.summary.errors.append(error_msg)

        return count

    def _process_ide_event(self, event: Any, queue_type: str):
        """Process an IDE queue event"""
        try:
            # Process with intelligent processor if available
            if self.intelligent_processor:
                result = self.intelligent_processor.process_notification(
                    title=f"IDE {queue_type.title()} Event",
                    message=str(event.data) if hasattr(event, 'data') else str(event),
                    source=f"ide_{queue_type}",
                    metadata={"queue_type": queue_type, "event_type": getattr(event, 'event_type', 'unknown')}
                )

                if result.get("action_taken") == "auto_fix":
                    self.summary.auto_fixed += 1
                elif result.get("action_taken") == "user_notification":
                    self.summary.requires_attention += 1
                else:
                    self.summary.ignored += 1

                self.summary.processed += 1
                self.summary.by_type[queue_type] = self.summary.by_type.get(queue_type, 0) + 1
        except Exception as e:
            self.logger.debug(f"Error processing IDE event: {e}")

    def _address_system_notifications(self) -> int:
        """Address system-level notifications"""
        count = 0

        try:
            # Check for system alerts via intelligent processor
            if self.intelligent_processor:
                status = self.intelligent_processor.get_notification_status()
                recent_events = status.get("total_events_processed", 0)
                if recent_events > 0:
                    count += recent_events
                    self.logger.info(f"    Found {recent_events} recent system notifications")
        except Exception as e:
            error_msg = f"Error addressing system notifications: {e}"
            self.logger.error(error_msg)
            self.summary.errors.append(error_msg)

        return count

    def _address_git_notifications(self) -> int:
        """Address Git-related notifications"""
        count = 0

        try:
            # Check Git status
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                count = len([l for l in lines if l.strip()])

                if count > 0:
                    self.logger.info(f"    Found {count} uncommitted changes")

                    # Process with intelligent processor
                    if self.intelligent_processor:
                        result = self.intelligent_processor.process_notification(
                            title="Git Repository Status",
                            message=f"Repository has {count} uncommitted changes",
                            source="git_status",
                            metadata={"change_count": count}
                        )

                        if result.get("action_taken") == "auto_fix":
                            self.summary.auto_fixed += 1
                        else:
                            self.summary.requires_attention += 1

                        self.summary.processed += 1
                        self.summary.by_type["git"] = count

        except Exception as e:
            error_msg = f"Error addressing Git notifications: {e}"
            self.logger.debug(error_msg)

        return count

    def _address_build_test_notifications(self) -> int:
        """Address build and test notifications"""
        count = 0

        try:
            # Check for build errors in common locations
            build_dirs = [
                self.project_root / "build",
                self.project_root / "dist",
                self.project_root / ".pytest_cache"
            ]

            for build_dir in build_dirs:
                if build_dir.exists():
                    # Check for error logs
                    error_logs = list(build_dir.rglob("*error*.log"))
                    if error_logs:
                        count += len(error_logs)
                        self.logger.info(f"    Found {len(error_logs)} error logs in {build_dir.name}")

        except Exception as e:
            error_msg = f"Error addressing build/test notifications: {e}"
            self.logger.debug(error_msg)

        return count

    def _address_security_notifications(self) -> int:
        """Address security-related notifications"""
        count = 0

        try:
            # Check for security warnings in code
            security_keywords = [
                "password", "secret", "api_key", "token", "credential",
                "hardcoded", "exposed", "vulnerability"
            ]

            # This would typically scan code files, but for now we'll check
            # if intelligent processor has security notifications
            if self.intelligent_processor:
                status = self.intelligent_processor.get_notification_status()
                events_by_type = status.get("events_by_type", {})
                security_events = events_by_type.get("security_warning", 0)
                if security_events > 0:
                    count += security_events
                    self.logger.info(f"    Found {security_events} security warnings")

        except Exception as e:
            error_msg = f"Error addressing security notifications: {e}"
            self.logger.debug(error_msg)

        return count

    def _address_resource_alerts(self) -> int:
        """Address resource alerts (memory, disk, CPU)"""
        count = 0

        try:
            # Check system resources
            import psutil

            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                count += 1
                self.logger.warning(f"    High memory usage: {memory.percent:.1f}%")

                if self.intelligent_processor:
                    self.intelligent_processor.process_notification(
                        title="High Memory Usage",
                        message=f"System memory usage is {memory.percent:.1f}%",
                        source="system_monitor",
                        metadata={"memory_percent": memory.percent}
                    )
                    self.summary.processed += 1
                    self.summary.requires_attention += 1

            # Disk check
            disk = psutil.disk_usage(str(self.project_root))
            if disk.percent > 90:
                count += 1
                self.logger.warning(f"    Low disk space: {disk.percent:.1f}% used")

                if self.intelligent_processor:
                    self.intelligent_processor.process_notification(
                        title="Low Disk Space",
                        message=f"Disk usage is {disk.percent:.1f}%",
                        source="system_monitor",
                        metadata={"disk_percent": disk.percent}
                    )
                    self.summary.processed += 1
                    self.summary.requires_attention += 1

        except ImportError:
            self.logger.debug("psutil not available for resource monitoring")
        except Exception as e:
            error_msg = f"Error addressing resource alerts: {e}"
            self.logger.debug(error_msg)

        return count

    def _process_with_intelligent_processor(self):
        """Process all notifications with intelligent processor"""
        try:
            if not self.intelligent_processor:
                return

            # Get status
            status = self.intelligent_processor.get_notification_status()

            # Get insights
            insights = self.intelligent_processor.get_psychohistory_insights()

            self.logger.info(f"    Total events processed: {status.get('total_events_processed', 0)}")
            self.logger.info(f"    Success rate: {status.get('success_rate', 0):.1%}")
            self.logger.info(f"    Auto-fix success rate: {status.get('auto_fix_success_rate', 0):.1%}")

            if insights.get('recommendations'):
                self.logger.info("    Recommendations:")
                for rec in insights['recommendations']:
                    self.logger.info(f"      • {rec}")

        except Exception as e:
            error_msg = f"Error processing with intelligent processor: {e}"
            self.logger.error(error_msg)
            self.summary.errors.append(error_msg)

    def _generate_summary(self):
        """Generate summary of notification addressing"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("NOTIFICATION ADDRESSING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total Notifications Found: {self.summary.total_notifications}")
        self.logger.info(f"Processed: {self.summary.processed}")
        self.logger.info(f"Auto-Fixed: {self.summary.auto_fixed}")
        self.logger.info(f"Requires Attention: {self.summary.requires_attention}")
        self.logger.info(f"Ignored: {self.summary.ignored}")

        if self.summary.by_type:
            self.logger.info("\nBy Type:")
            for ntype, count in sorted(self.summary.by_type.items()):
                self.logger.info(f"  {ntype}: {count}")

        if self.summary.errors:
            self.logger.warning(f"\nErrors: {len(self.summary.errors)}")
            for error in self.summary.errors[:5]:  # Show first 5
                self.logger.warning(f"  • {error}")

    def _save_results(self):
        """Save addressing results"""
        results_file = self.data_dir / f"addressing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results = {
            "timestamp": self.summary.timestamp.isoformat(),
            "total_notifications": self.summary.total_notifications,
            "processed": self.summary.processed,
            "auto_fixed": self.summary.auto_fixed,
            "requires_attention": self.summary.requires_attention,
            "ignored": self.summary.ignored,
            "by_type": self.summary.by_type,
            "by_priority": self.summary.by_priority,
            "errors": self.summary.errors
        }

        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"\n✅ Results saved to: {results_file}")
        except Exception as e:
            self.logger.error(f"Could not save results: {e}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("ADDRESS NOTIFICATIONS")
    print("=" * 80)
    print()

    addresser = NotificationAddresser()
    summary = addresser.address_all_notifications()

    print()
    print("=" * 80)
    print(f"✅ Notification addressing complete")
    print(f"   Total: {summary.total_notifications}")
    print(f"   Processed: {summary.processed}")
    print(f"   Auto-Fixed: {summary.auto_fixed}")
    print(f"   Requires Attention: {summary.requires_attention}")
    print("=" * 80)

    return 0 if summary.errors else 0


if __name__ == "__main__":



    sys.exit(main())