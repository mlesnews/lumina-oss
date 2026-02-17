#!/usr/bin/env python3
"""
JARVIS Service Bus Migration
Migrate JARVIS file-based communication to Azure Service Bus

This script migrates all JARVIS communication from file-based to Azure Service Bus.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

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

logger = get_logger("JARVISServiceBusMigration")

try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False
    logger.error("Azure Service Bus integration not available")


class JARVISServiceBusMigration:
    """Migrate JARVIS file-based communication to Azure Service Bus"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.jarvis_intelligence_dir = self.project_root / "data" / "jarvis_intelligence"
        self.migration_log_dir = self.project_root / "data" / "migrations" / "service_bus"
        self.migration_log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Service Bus client
        if SERVICE_BUS_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.sb_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
                logger.info("Service Bus client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Service Bus client: {e}")
                self.sb_client = None
        else:
            self.sb_client = None

    def migrate_escalation(self, escalation_file: Path) -> bool:
        """
        Migrate escalation file to Service Bus

        Args:
            escalation_file: Path to escalation JSON file

        Returns:
            True if migrated successfully
        """
        try:
            # Read escalation file
            with open(escalation_file, 'r', encoding='utf-8') as f:
                escalation_data = json.load(f)

            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.ESCALATION,
                timestamp=datetime.now(),
                source="jarvis-helpdesk-integration",
                destination="jarvis-escalation-handler",
                payload=escalation_data,
                correlation_id=escalation_data.get("workflow_id") or escalation_data.get("ticket_id")
            )

            # Publish to Service Bus topic
            success = self.sb_client.publish_to_topic(
                topic_name="jarvis.escalations",
                message=message
            )

            if success:
                logger.info(f"Migrated escalation: {escalation_file.name}")
                # Archive original file
                archive_dir = self.jarvis_intelligence_dir / "archive"
                archive_dir.mkdir(exist_ok=True)
                escalation_file.rename(archive_dir / escalation_file.name)
                return True
            else:
                logger.error(f"Failed to migrate escalation: {escalation_file.name}")
                return False

        except Exception as e:
            logger.error(f"Error migrating escalation {escalation_file.name}: {e}")
            return False

    def migrate_intelligence_item(self, intelligence_file: Path) -> bool:
        """
        Migrate intelligence item to Service Bus

        Args:
            intelligence_file: Path to intelligence JSON file

        Returns:
            True if migrated successfully
        """
        try:
            # Read intelligence file
            with open(intelligence_file, 'r', encoding='utf-8') as f:
                intelligence_data = json.load(f)

            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.INTELLIGENCE,
                timestamp=datetime.now(),
                source="jarvis-intelligence",
                destination="intelligence-processor",
                payload=intelligence_data
            )

            # Publish to Service Bus topic
            success = self.sb_client.publish_to_topic(
                topic_name="jarvis.intelligence",
                message=message
            )

            if success:
                logger.info(f"Migrated intelligence item: {intelligence_file.name}")
                # Archive original file
                archive_dir = self.jarvis_intelligence_dir / "archive"
                archive_dir.mkdir(exist_ok=True)
                intelligence_file.rename(archive_dir / intelligence_file.name)
                return True
            else:
                logger.error(f"Failed to migrate intelligence item: {intelligence_file.name}")
                return False

        except Exception as e:
            logger.error(f"Error migrating intelligence item {intelligence_file.name}: {e}")
            return False

    def migrate_all(self) -> Dict[str, Any]:
        try:
            """
            Migrate all file-based JARVIS communication to Service Bus

            Returns:
                Migration report
            """
            if not self.sb_client:
                logger.error("Service Bus client not available")
                return {"success": False, "error": "Service Bus client not available"}

            report = {
                "migration_started": datetime.now().isoformat(),
                "escalations_migrated": 0,
                "escalations_failed": 0,
                "intelligence_items_migrated": 0,
                "intelligence_items_failed": 0,
                "errors": []
            }

            # Migrate escalations
            escalation_files = list(self.jarvis_intelligence_dir.glob("jarvis_escalation_*.json"))
            logger.info(f"Found {len(escalation_files)} escalation files to migrate")

            for escalation_file in escalation_files:
                if self.migrate_escalation(escalation_file):
                    report["escalations_migrated"] += 1
                else:
                    report["escalations_failed"] += 1
                    report["errors"].append(f"Failed to migrate: {escalation_file.name}")

            # Migrate intelligence items
            intelligence_files = [
                f for f in self.jarvis_intelligence_dir.glob("*.json")
                if f.name.startswith("jarvis_") and "escalation" not in f.name
            ]
            logger.info(f"Found {len(intelligence_files)} intelligence files to migrate")

            for intelligence_file in intelligence_files:
                if self.migrate_intelligence_item(intelligence_file):
                    report["intelligence_items_migrated"] += 1
                else:
                    report["intelligence_items_failed"] += 1
                    report["errors"].append(f"Failed to migrate: {intelligence_file.name}")

            report["migration_completed"] = datetime.now().isoformat()
            report["success"] = (
                report["escalations_failed"] == 0 and
                report["intelligence_items_failed"] == 0
            )

            # Save migration report
            report_file = self.migration_log_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Migration complete. Report saved to: {report_file}")
            return report


        except Exception as e:
            self.logger.error(f"Error in migrate_all: {e}", exc_info=True)
            raise
def main():
    try:
        """Main migration function"""
        project_root = Path(__file__).parent.parent.parent
        migrator = JARVISServiceBusMigration(project_root)
        report = migrator.migrate_all()

        print("\n" + "=" * 60)
        print("JARVIS Service Bus Migration Report")
        print("=" * 60)
        print(f"Escalations Migrated: {report['escalations_migrated']}")
        print(f"Escalations Failed: {report['escalations_failed']}")
        print(f"Intelligence Items Migrated: {report['intelligence_items_migrated']}")
        print(f"Intelligence Items Failed: {report['intelligence_items_failed']}")
        print(f"Success: {report['success']}")
        if report['errors']:
            print(f"\nErrors: {len(report['errors'])}")
            for error in report['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()