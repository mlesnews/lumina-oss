#!/usr/bin/env python3
"""
Verification Service Bus Integration
Helper functions for @v3 verification system to use Azure Service Bus
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
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

logger = get_logger("VerificationServiceBus")

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
    logger.warning("Azure Service Bus integration not available")


def send_verification_request(verification_data: Dict[str, Any], sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Send verification request to verification queue

    Args:
        verification_data: Verification request data
        sb_client: Optional Service Bus client

    Returns:
        True if sent successfully
    """
    if not SERVICE_BUS_AVAILABLE:
        return False

    try:
        if not sb_client:
            kv_client = get_key_vault_client()
            sb_client = get_service_bus_client(key_vault_client=kv_client)

        message = ServiceBusMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.VERIFICATION,
            timestamp=datetime.now(),
            source="lumina-verification",
            destination="v3-verification-processor",
            payload={
                "MessageType": "VerificationRequest",
                **verification_data
            },
            correlation_id=verification_data.get("workflow_id")
        )

        # Send to verification queue
        success = sb_client.send_to_queue("verification-queue", message)

        # Also publish to topic
        sb_client.publish_to_topic("lumina.verification", message)

        return success

    except Exception as e:
        logger.error(f"Error sending verification request: {e}")
        return False


def publish_verification_result(verification_id: str, workflow_id: str, status: str,
                               results: Optional[Dict[str, Any]] = None, errors: Optional[list] = None,
                               sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish verification result to verification topic

    Args:
        verification_id: Verification ID
        workflow_id: Workflow ID
        status: Verification status (verified, failed, warning)
        results: Optional verification results
        errors: Optional list of errors
        sb_client: Optional Service Bus client

    Returns:
        True if published successfully
    """
    if not SERVICE_BUS_AVAILABLE:
        return False

    try:
        if not sb_client:
            kv_client = get_key_vault_client()
            sb_client = get_service_bus_client(key_vault_client=kv_client)

        message = ServiceBusMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.VERIFICATION,
            timestamp=datetime.now(),
            source="v3-verification-processor",
            destination="workflow-processor",
            payload={
                "MessageType": "VerificationResult",
                "VerificationId": verification_id,
                "WorkflowId": workflow_id,
                "Status": status,
                "Results": results,
                "Errors": errors
            },
            correlation_id=workflow_id
        )

        # Publish to verification topic
        success = sb_client.publish_to_topic("lumina.verification", message)

        return success

    except Exception as e:
        logger.error(f"Error publishing verification result: {e}")
        return False
