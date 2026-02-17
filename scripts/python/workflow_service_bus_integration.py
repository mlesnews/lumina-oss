#!/usr/bin/env python3
"""
Workflow Service Bus Integration
Helper functions for workflow systems to use Azure Service Bus
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

logger = get_logger("WorkflowServiceBus")

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


def publish_workflow_created(workflow_data: Dict[str, Any], sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish workflow created event to Service Bus

    Args:
        workflow_data: Workflow data
        sb_client: Optional Service Bus client (creates if not provided)

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
            message_type=MessageType.WORKFLOW,
            timestamp=datetime.now(),
            source="workflow-processor",
            destination="workflow-processor",
            payload={
                "MessageType": "WorkflowCreated",
                "WorkflowId": workflow_data.get("id") or workflow_data.get("workflow_id"),
                "Name": workflow_data.get("name"),
                "CreatedBy": workflow_data.get("created_by"),
                "Priority": workflow_data.get("priority", 5),
                **workflow_data
            },
            correlation_id=workflow_data.get("id") or workflow_data.get("workflow_id")
        )

        # Publish to both JARVIS and Lumina workflow topics
        success1 = sb_client.publish_to_topic("jarvis.workflows", message)
        success2 = sb_client.publish_to_topic("lumina.workflows", message)

        return success1 or success2

    except Exception as e:
        logger.error(f"Error publishing workflow created: {e}")
        return False


def publish_workflow_status_update(workflow_id: str, status: str, progress: Optional[int] = None, 
                                   current_step: Optional[str] = None, sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish workflow status update to Service Bus

    Args:
        workflow_id: Workflow ID
        status: New status
        progress: Optional progress percentage
        current_step: Optional current step
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
            message_type=MessageType.WORKFLOW,
            timestamp=datetime.now(),
            source="workflow-processor",
            destination="workflow-notifications",
            payload={
                "MessageType": "WorkflowStatusUpdate",
                "WorkflowId": workflow_id,
                "Status": status,
                "Progress": progress,
                "CurrentStep": current_step
            },
            correlation_id=workflow_id
        )

        # Publish to both topics
        success1 = sb_client.publish_to_topic("jarvis.workflows", message)
        success2 = sb_client.publish_to_topic("lumina.workflows", message)

        return success1 or success2

    except Exception as e:
        logger.error(f"Error publishing workflow status update: {e}")
        return False


def publish_workflow_completed(workflow_id: str, status: str, execution_time: Optional[float] = None,
                              result: Optional[Dict[str, Any]] = None, error: Optional[str] = None,
                              sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Publish workflow completed event to Service Bus

    Args:
        workflow_id: Workflow ID
        status: Completion status (completed or failed)
        execution_time: Optional execution time in seconds
        result: Optional result data
        error: Optional error message
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
            message_type=MessageType.WORKFLOW,
            timestamp=datetime.now(),
            source="workflow-processor",
            destination="workflow-notifications",
            payload={
                "MessageType": "WorkflowCompleted",
                "WorkflowId": workflow_id,
                "Status": status,
                "ExecutionTime": execution_time,
                "Result": result,
                "Error": error
            },
            correlation_id=workflow_id
        )

        # Publish to both topics
        success1 = sb_client.publish_to_topic("jarvis.workflows", message)
        success2 = sb_client.publish_to_topic("lumina.workflows", message)

        return success1 or success2

    except Exception as e:
        logger.error(f"Error publishing workflow completed: {e}")
        return False


def send_workflow_execution_request(workflow_id: str, parameters: Optional[Dict[str, Any]] = None,
                                   async_execution: bool = True, sb_client: Optional[AzureServiceBusClient] = None) -> bool:
    """
    Send workflow execution request to Service Bus queue

    Args:
        workflow_id: Workflow ID to execute
        parameters: Optional execution parameters
        async_execution: Whether execution is async
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
            message_type=MessageType.WORKFLOW,
            timestamp=datetime.now(),
            source="workflow-api",
            destination="workflow-execution-queue",
            payload={
                "MessageType": "WorkflowExecutionRequest",
                "WorkflowId": workflow_id,
                "Parameters": parameters or {},
                "Async": async_execution
            },
            correlation_id=workflow_id
        )

        # Send to execution queue
        success = sb_client.send_to_queue("workflow-execution-queue", message)

        return success

    except Exception as e:
        logger.error(f"Error sending workflow execution request: {e}")
        return False
