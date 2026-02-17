#!/usr/bin/env python3
"""
API Intelligence Service
Handles intelligence feed items

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

logger = get_logger("APIIntelligenceService")

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


class IntelligenceService:
    """Handles intelligence feed operations"""

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

    def get_intelligence_feed(
        self,
        type_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        action_required: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get intelligence feed items"""
        if not self.db_manager:
            return {"items": [], "total": 0, "limit": limit, "offset": offset}

        # Build query with filters
        where_clauses = []
        params = []

        if type_filter:
            where_clauses.append("type = %s")
            params.append(type_filter)

        if priority_filter:
            where_clauses.append("priority = %s")
            params.append(priority_filter)

        if action_required is not None:
            where_clauses.append("action_required = %s")
            params.append(action_required)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM intelligence_items WHERE {where_sql}"
        count_results = self.db_manager.execute_query(count_query, tuple(params))
        total = count_results[0]['total'] if count_results else 0

        # Get items
        query = f"""
        SELECT id, type, priority, title, message, source, action_required,
               created_at, acknowledged_at, resolved_at, acknowledged_by, metadata,
               related_workflow_id, related_ticket_id
        FROM intelligence_items
        WHERE {where_sql}
        ORDER BY 
            CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END,
            created_at DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        try:
            results = self.db_manager.execute_query(query, tuple(params))
            items = [
                {
                    "id": str(i["id"]),
                    "type": i["type"],
                    "priority": i["priority"],
                    "title": i["title"],
                    "message": i["message"],
                    "source": i["source"],
                    "action_required": i.get("action_required", False),
                    "created_at": i["created_at"].isoformat() if hasattr(i["created_at"], 'isoformat') else str(i["created_at"]),
                    "acknowledged_at": i["acknowledged_at"].isoformat() if i.get("acknowledged_at") and hasattr(i["acknowledged_at"], 'isoformat') else (str(i["acknowledged_at"]) if i.get("acknowledged_at") else None),
                    "resolved_at": i["resolved_at"].isoformat() if i.get("resolved_at") and hasattr(i["resolved_at"], 'isoformat') else (str(i["resolved_at"]) if i.get("resolved_at") else None),
                    "acknowledged_by": str(i["acknowledged_by"]) if i.get("acknowledged_by") else None,
                    "metadata": i.get("metadata"),
                    "related_workflow_id": str(i["related_workflow_id"]) if i.get("related_workflow_id") else None,
                    "related_ticket_id": str(i["related_ticket_id"]) if i.get("related_ticket_id") else None
                }
                for i in results
            ]

            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error getting intelligence feed: {e}")
            return {"items": [], "total": 0, "limit": limit, "offset": offset}


def get_intelligence_service(project_root: Optional[Path] = None) -> IntelligenceService:
    """Get global intelligence service"""
    return IntelligenceService(project_root)
