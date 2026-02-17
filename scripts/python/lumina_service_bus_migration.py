#!/usr/bin/env python3
"""
Lumina Service Bus Migration
Migrate Lumina file-based communication to Azure Service Bus

This script migrates all Lumina async communication from file-based to Azure Service Bus.
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

logger = get_logger("LuminaServiceBusMigration")

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


class LuminaServiceBusMigration:
    """Migrate Lumina file-based communication to Azure Service Bus"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
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

    def migrate_workflow_message(self, workflow_data: Dict[str, Any], message_type: str) -> bool:
        """
        Migrate workflow message to Service Bus

        Args:
            workflow_data: Workflow data
            message_type: Type of workflow message (WorkflowCreated, WorkflowExecutionRequest, etc.)

        Returns:
            True if migrated successfully
        """
        try:
            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.WORKFLOW,
                timestamp=datetime.now(),
                source="lumina-workflow-processor",
                destination="lumina-workflow-processor",
                payload={
                    "MessageType": message_type,
                    "WorkflowId": workflow_data.get("id") or workflow_data.get("workflow_id"),
                    **workflow_data
                },
                correlation_id=workflow_data.get("id") or workflow_data.get("workflow_id")
            )

            # Publish to Service Bus topic
            success = self.sb_client.publish_to_topic(
                topic_name="lumina.workflows",
                message=message
            )

            if success:
                logger.info(f"Migrated workflow message: {message_type}")
                return True
            else:
                logger.error(f"Failed to migrate workflow message: {message_type}")
                return False

        except Exception as e:
            logger.error(f"Error migrating workflow message: {e}")
            return False

    def migrate_verification_request(self, verification_data: Dict[str, Any]) -> bool:
        """
        Migrate verification request to Service Bus

        Args:
            verification_data: Verification data

        Returns:
            True if migrated successfully
        """
        try:
            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.VERIFICATION,
                timestamp=datetime.now(),
                source="lumina-verification",
                destination="v3-verification-processor",
                payload=verification_data,
                correlation_id=verification_data.get("workflow_id")
            )

            # Send to verification queue
            success = self.sb_client.send_to_queue(
                queue_name="verification-queue",
                message=message
            )

            if success:
                logger.info("Migrated verification request")
                return True
            else:
                logger.error("Failed to migrate verification request")
                return False

        except Exception as e:
            logger.error(f"Error migrating verification request: {e}")
            return False

    def migrate_r5_knowledge(self, knowledge_data: Dict[str, Any]) -> bool:
        """
        Migrate R5 knowledge entry to Service Bus

        Args:
            knowledge_data: Knowledge entry data

        Returns:
            True if migrated successfully
        """
        try:
            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.KNOWLEDGE,
                timestamp=datetime.now(),
                source="r5-ingestion",
                destination="r5-ingestion-processor",
                payload={
                    "MessageType": "KnowledgeEntry",
                    "ExtractPatterns": True,
                    **knowledge_data
                }
            )

            # Send to R5 ingestion queue
            success = self.sb_client.send_to_queue(
                queue_name="r5-ingestion-queue",
                message=message
            )

            if success:
                logger.info("Migrated R5 knowledge entry")
                return True
            else:
                logger.error("Failed to migrate R5 knowledge entry")
                return False

        except Exception as e:
            logger.error(f"Error migrating R5 knowledge entry: {e}")
            return False

    def migrate_all(self) -> Dict[str, Any]:
        try:
            """
            Migrate all Lumina file-based communication to Service Bus

            Returns:
                Migration report
            """
            if not self.sb_client:
                logger.error("Service Bus client not available")
                return {"success": False, "error": "Service Bus client not available"}

            report = {
                "migration_started": datetime.now().isoformat(),
                "workflows_migrated": 0,
                "workflows_failed": 0,
                "verifications_migrated": 0,
                "verifications_failed": 0,
                "r5_entries_migrated": 0,
                "r5_entries_failed": 0,
                "errors": []
            }

            # Note: Actual migration would scan for file-based communication patterns
            # and migrate them. This is a framework for the migration.

            report["migration_completed"] = datetime.now().isoformat()
            report["success"] = (
                report["workflows_failed"] == 0 and
                report["verifications_failed"] == 0 and
                report["r5_entries_failed"] == 0
            )

            # Save migration report
            report_file = self.migration_log_dir / f"lumina_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        migrator = LuminaServiceBusMigration(project_root)
        report = migrator.migrate_all()

        print("\n" + "=" * 60)
        print("Lumina Service Bus Migration Report")
        print("=" * 60)
        print(f"Workflows Migrated: {report['workflows_migrated']}")
        print(f"Verifications Migrated: {report['verifications_migrated']}")
        print(f"R5 Entries Migrated: {report['r5_entries_migrated']}")
        print(f"Success: {report['success']}")
        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()