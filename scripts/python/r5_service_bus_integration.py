#!/usr/bin/env python3
"""
R5 Service Bus Integration
Helper functions for R5 knowledge system to use Azure Service Bus
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
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

logger = get_logger("R5ServiceBus")

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


def publish_knowledge_entry(entry_data: Dict[str, Any], extract_patterns: bool = True,
                          sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish knowledge entry to R5 ingestion queue

    Args:
        entry_data: Knowledge entry data
        extract_patterns: Whether to extract patterns
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
            message_type=MessageType.KNOWLEDGE,
            timestamp=datetime.now(),
            source="r5-ingestion",
            destination="r5-ingestion-processor",
            payload={
                "MessageType": "KnowledgeEntry",
                "ExtractPatterns": extract_patterns,
                **entry_data
            }
        )

        # Send to R5 ingestion queue
        success = sb_client.send_to_queue("r5-ingestion-queue", message)

        # Also publish to topic for pattern extraction if needed
        if extract_patterns:
            sb_client.publish_to_topic("r5.knowledge", message)

        return success

    except Exception as e:
        logger.error(f"Error publishing knowledge entry: {e}")
        return False


def publish_batch_ingestion(entries: List[Dict[str, Any]], sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish batch knowledge ingestion to R5

    Args:
        entries: List of knowledge entry data
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
            message_type=MessageType.KNOWLEDGE,
            timestamp=datetime.now(),
            source="r5-ingestion",
            destination="r5-ingestion-processor",
            payload={
                "MessageType": "BatchIngestion",
                "BatchId": str(uuid.uuid4()),
                "Entries": entries
            }
        )

        # Send to R5 ingestion queue
        success = sb_client.send_to_queue("r5-ingestion-queue", message)

        return success

    except Exception as e:
        logger.error(f"Error publishing batch ingestion: {e}")
        return False


def publish_pattern_update(pattern_data: Dict[str, Any], sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish pattern update to R5 knowledge topic

    Args:
        pattern_data: Pattern data
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
            message_type=MessageType.KNOWLEDGE,
            timestamp=datetime.now(),
            source="r5-pattern-extractor",
            destination="r5-pattern-extractor",
            payload={
                "MessageType": "PatternUpdate",
                **pattern_data
            }
        )

        # Publish to R5 knowledge topic
        success = sb_client.publish_to_topic("r5.knowledge", message)

        return success

    except Exception as e:
        logger.error(f"Error publishing pattern update: {e}")
        return False
