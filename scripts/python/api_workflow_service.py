#!/usr/bin/env python3
"""
API Workflow Service
Handles workflow CRUD operations and execution

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

logger = get_logger("APIWorkflowService")

try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from workflow_service_bus_integration import (
        publish_workflow_created,
        publish_workflow_status_update,
        publish_workflow_completed,
        send_workflow_execution_request
    )
    from azure_service_bus_integration import get_service_bus_client, get_key_vault_client
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False


class WorkflowService:
    """Handles workflow operations"""

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

    def create_workflow(
        self,
        name: str,
        description: Optional[str],
        steps: List[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]],
        created_by: str
    ) -> Dict[str, Any]:
        """Create a new workflow"""
        if not self.db_manager:
            raise RuntimeError("Database manager not available")

        workflow_id = str(uuid.uuid4())

        # Insert workflow
        workflow_query = """
        INSERT INTO workflows (id, name, description, status, priority, created_by, parameters, created_at, updated_at)
        VALUES (%s, %s, %s, 'pending', 5, %s, %s, NOW(), NOW())
        RETURNING id, name, description, status, priority, created_by, created_at
        """

        try:
            workflow_results = self.db_manager.execute_query(
                workflow_query,
                (workflow_id, name, description, created_by, json.dumps(parameters or {}))
            )

            if not workflow_results:
                raise Exception("Workflow creation failed")

            workflow = workflow_results[0]

            # Insert workflow steps
            for idx, step in enumerate(steps):
                step_id = str(uuid.uuid4())
                step_query = """
                INSERT INTO workflow_steps (id, workflow_id, step_id, name, action, status, "order", parameters)
                VALUES (%s, %s, %s, %s, %s, 'pending', %s, %s)
                """
                self.db_manager.execute_update(
                    step_query,
                    (
                        step_id,
                        workflow_id,
                        step.get("step_id", f"step_{idx}"),
                        step.get("name", "Unnamed Step"),
                        step.get("action", "unknown"),
                        idx,
                        json.dumps(step.get("parameters", {}))
                    )
                )

            # Publish to Service Bus
            if self.service_bus_client:
                publish_workflow_created({
                    "id": workflow_id,
                    "name": name,
                    "description": description,
                    "steps": steps,
                    "parameters": parameters,
                    "created_by": created_by
                }, self.service_bus_client)

            return {
                "id": str(workflow["id"]),
                "name": workflow["name"],
                "description": workflow["description"],
                "status": workflow["status"],
                "priority": workflow["priority"],
                "created_by": str(workflow["created_by"]),
                "created_at": workflow["created_at"].isoformat() if hasattr(workflow["created_at"], 'isoformat') else str(workflow["created_at"])
            }
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        if not self.db_manager:
            return None

        query = """
        SELECT id, name, description, status, priority, created_by, droid_assigned,
               created_at, updated_at, started_at, completed_at, execution_time,
               parameters, result, error
        FROM workflows
        WHERE id = %s
        """

        try:
            results = self.db_manager.execute_query(query, (workflow_id,))
            if not results:
                return None

            workflow = results[0]

            # Get workflow steps
            steps_query = """
            SELECT id, step_id, name, action, status, "order", parameters,
                   started_at, completed_at, execution_time, error, result
            FROM workflow_steps
            WHERE workflow_id = %s
            ORDER BY "order"
            """
            steps_results = self.db_manager.execute_query(steps_query, (workflow_id,))

            return {
                "id": str(workflow["id"]),
                "name": workflow["name"],
                "description": workflow["description"],
                "status": workflow["status"],
                "priority": workflow["priority"],
                "created_by": str(workflow["created_by"]),
                "droid_assigned": workflow.get("droid_assigned"),
                "created_at": workflow["created_at"].isoformat() if hasattr(workflow["created_at"], 'isoformat') else str(workflow["created_at"]),
                "updated_at": workflow["updated_at"].isoformat() if hasattr(workflow["updated_at"], 'isoformat') else str(workflow["updated_at"]),
                "started_at": workflow["started_at"].isoformat() if workflow.get("started_at") and hasattr(workflow["started_at"], 'isoformat') else (str(workflow["started_at"]) if workflow.get("started_at") else None),
                "completed_at": workflow["completed_at"].isoformat() if workflow.get("completed_at") and hasattr(workflow["completed_at"], 'isoformat') else (str(workflow["completed_at"]) if workflow.get("completed_at") else None),
                "execution_time": workflow.get("execution_time"),
                "parameters": workflow.get("parameters"),
                "result": workflow.get("result"),
                "error": workflow.get("error"),
                "steps": [
                    {
                        "id": str(step["id"]),
                        "step_id": step["step_id"],
                        "name": step["name"],
                        "action": step["action"],
                        "status": step["status"],
                        "order": step["order"],
                        "parameters": step.get("parameters"),
                        "started_at": step["started_at"].isoformat() if step.get("started_at") and hasattr(step["started_at"], 'isoformat') else (str(step["started_at"]) if step.get("started_at") else None),
                        "completed_at": step["completed_at"].isoformat() if step.get("completed_at") and hasattr(step["completed_at"], 'isoformat') else (str(step["completed_at"]) if step.get("completed_at") else None),
                        "execution_time": step.get("execution_time"),
                        "error": step.get("error"),
                        "result": step.get("result")
                    }
                    for step in steps_results
                ]
            }
        except Exception as e:
            logger.error(f"Error getting workflow: {e}")
            return None

    def list_workflows(
        self,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List workflows with filters"""
        if not self.db_manager:
            return {"workflows": [], "total": 0, "limit": limit, "offset": offset}

        # Build query with filters
        where_clauses = []
        params = []

        if status:
            where_clauses.append("status = %s")
            params.append(status)

        if created_by:
            where_clauses.append("created_by = %s")
            params.append(created_by)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM workflows WHERE {where_sql}"
        count_results = self.db_manager.execute_query(count_query, tuple(params))
        total = count_results[0]['total'] if count_results else 0

        # Get workflows
        query = f"""
        SELECT id, name, description, status, priority, created_by, created_at, updated_at
        FROM workflows
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        try:
            results = self.db_manager.execute_query(query, tuple(params))
            workflows = [
                {
                    "id": str(w["id"]),
                    "name": w["name"],
                    "description": w["description"],
                    "status": w["status"],
                    "priority": w["priority"],
                    "created_by": str(w["created_by"]),
                    "created_at": w["created_at"].isoformat() if hasattr(w["created_at"], 'isoformat') else str(w["created_at"]),
                    "updated_at": w["updated_at"].isoformat() if hasattr(w["updated_at"], 'isoformat') else str(w["updated_at"])
                }
                for w in results
            ]

            return {
                "workflows": workflows,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return {"workflows": [], "total": 0, "limit": limit, "offset": offset}

    def update_workflow(
        self,
        workflow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> bool:
        """Update workflow"""
        if not self.db_manager:
            return False

        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)

        if description is not None:
            updates.append("description = %s")
            params.append(description)

        if status is not None:
            updates.append("status = %s")
            params.append(status)

        if not updates:
            return True

        updates.append("updated_at = NOW()")
        params.append(workflow_id)

        query = f"""
        UPDATE workflows
        SET {', '.join(updates)}
        WHERE id = %s
        """

        try:
            rows_affected = self.db_manager.execute_update(query, tuple(params))

            # Publish status update to Service Bus
            if rows_affected > 0 and status and self.service_bus_client:
                publish_workflow_status_update(workflow_id, status, None, None, self.service_bus_client)

            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            return False

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        if not self.db_manager:
            return False

        query = "DELETE FROM workflows WHERE id = %s"

        try:
            rows_affected = self.db_manager.execute_update(query, (workflow_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            return False

    def execute_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Execute workflow"""
        # Update workflow status
        self.update_workflow(workflow_id, status="running")

        # Send execution request to Service Bus
        if self.service_bus_client:
            send_workflow_execution_request(workflow_id, parameters, True, self.service_bus_client)
            return True

        return False


def get_workflow_service(project_root: Optional[Path] = None) -> WorkflowService:
    """Get global workflow service"""
    return WorkflowService(project_root)
