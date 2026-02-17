#!/usr/bin/env python3
"""
API Helpdesk Service
Handles helpdesk tickets and droid assignment

Integrates with database and Azure Service Bus.
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

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

logger = get_logger("APIHelpdeskService")

try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from azure_service_bus_integration import (
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False


class HelpdeskService:
    """Handles helpdesk operations"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent

        if DB_AVAILABLE:
            self.db_manager = get_db_manager(project_root)
        else:
            self.db_manager = None

        self.service_bus_client = None
        if SERVICE_BUS_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.service_bus_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
            except Exception as e:
                logger.warning(f"Service Bus not available: {e}")

    def create_ticket(
        self,
        title: str,
        description: str,
        priority: str,
        category: Optional[str],
        created_by: str
    ) -> Dict[str, Any]:
        """Create a helpdesk ticket"""
        if not self.db_manager:
            raise RuntimeError("Database manager not available")

        ticket_uuid = str(uuid.uuid4())

        # Generate ticket_id in format T000000000
        # Get next ticket number
        count_query = "SELECT COUNT(*) as count FROM helpdesk_tickets"
        count_results = self.db_manager.execute_query(count_query)
        ticket_number = (count_results[0]['count'] if count_results else 0) + 1
        ticket_id = f"T{ticket_number:09d}"

        query = """
        INSERT INTO helpdesk_tickets (id, ticket_id, title, description, priority, category, status, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'open', %s, NOW(), NOW())
        RETURNING id, ticket_id, title, description, priority, category, status, created_by, created_at, updated_at
        """

        try:
            results = self.db_manager.execute_query(
                query,
                (ticket_uuid, ticket_id, title, description, priority, category, created_by)
            )

            if not results:
                raise Exception("Ticket creation failed")

            ticket = results[0]

            # Publish to Service Bus for droid assignment
            if self.service_bus_client:
                sb_message = ServiceBusMessage(
                    message_id=str(ticket_uuid),
                    message_type=MessageType.ESCALATION,
                    timestamp=datetime.now(),
                    source="api-helpdesk",
                    destination="helpdesk-coordinator",
                    payload={
                        "MessageType": "TicketCreated",
                        "TicketId": ticket_id,
                        "Title": title,
                        "Description": description,
                        "Priority": priority,
                        "Category": category,
                        "CreatedBy": created_by
                    }
                )
                self.service_bus_client.publish_to_topic("helpdesk.coordination", sb_message)
                self.service_bus_client.send_to_queue("droid-assignment-queue", sb_message)

            return {
                "id": str(ticket["id"]),
                "ticket_id": ticket.get("ticket_id"),
                "title": ticket["title"],
                "description": ticket["description"],
                "priority": ticket["priority"],
                "category": ticket.get("category"),
                "status": ticket["status"],
                "created_by": str(ticket["created_by"]),
                "created_at": ticket["created_at"].isoformat() if hasattr(ticket["created_at"], 'isoformat') else str(ticket["created_at"]),
                "updated_at": ticket["updated_at"].isoformat() if hasattr(ticket["updated_at"], 'isoformat') else str(ticket["updated_at"])
            }
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            raise

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List helpdesk tickets"""
        if not self.db_manager:
            return {"tickets": [], "total": 0, "limit": limit, "offset": offset}

        # Build query with filters
        where_clauses = []
        params = []

        if status:
            where_clauses.append("status = %s")
            params.append(status)

        if priority:
            where_clauses.append("priority = %s")
            params.append(priority)

        if created_by:
            where_clauses.append("created_by = %s")
            params.append(created_by)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM helpdesk_tickets WHERE {where_sql}"
        count_results = self.db_manager.execute_query(count_query, tuple(params))
        total = count_results[0]['total'] if count_results else 0

        # Get tickets
        query = f"""
        SELECT id, ticket_id, title, description, priority, category, status, created_by,
               droid_assigned, created_at, updated_at, resolved_at
        FROM helpdesk_tickets
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        try:
            results = self.db_manager.execute_query(query, tuple(params))
            tickets = [
                {
                    "id": str(t["id"]),
                    "ticket_id": t.get("ticket_id"),
                    "title": t["title"],
                    "description": t["description"],
                    "priority": t["priority"],
                    "category": t.get("category"),
                    "status": t["status"],
                    "created_by": str(t["created_by"]),
                    "droid_assigned": t.get("droid_assigned"),
                    "created_at": t["created_at"].isoformat() if hasattr(t["created_at"], 'isoformat') else str(t["created_at"]),
                    "updated_at": t["updated_at"].isoformat() if hasattr(t["updated_at"], 'isoformat') else str(t["updated_at"]),
                    "resolved_at": t["resolved_at"].isoformat() if t.get("resolved_at") and hasattr(t["resolved_at"], 'isoformat') else (str(t["resolved_at"]) if t.get("resolved_at") else None)
                }
                for t in results
            ]

            return {
                "tickets": tickets,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error listing tickets: {e}")
            return {"tickets": [], "total": 0, "limit": limit, "offset": offset}


def get_helpdesk_service(project_root: Optional[Path] = None) -> HelpdeskService:
    """Get global helpdesk service"""
    return HelpdeskService(project_root)
