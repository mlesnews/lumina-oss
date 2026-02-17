#!/usr/bin/env python3
"""
Monitoring Service
System health monitoring and business metrics

Provides health checks and business metrics for the API server.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

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

logger = get_logger("MonitoringService")

try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from azure_service_bus_integration import get_service_bus_client, get_key_vault_client
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class MonitoringService:
    """System monitoring and health checks"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.start_time = datetime.now()

        # Initialize components
        self.db_manager = None
        if DB_AVAILABLE:
            try:
                self.db_manager = get_db_manager(project_root)
            except Exception as e:
                logger.warning(f"Database manager not available: {e}")

        self.service_bus_client = None
        self.key_vault_client = None
        if AZURE_AVAILABLE:
            try:
                self.key_vault_client = get_key_vault_client()
                self.service_bus_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=self.key_vault_client
                )
            except Exception as e:
                logger.warning(f"Azure services not available: {e}")

    def check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        if not self.db_manager:
            return {"status": "unavailable", "error": "Database manager not initialized"}

        try:
            conn = self.db_manager.get_connection()
            self.db_manager.return_connection(conn)
            return {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_service_bus_health(self) -> Dict[str, Any]:
        """Check Service Bus health"""
        if not self.service_bus_client:
            return {"status": "unavailable", "error": "Service Bus client not initialized"}

        try:
            # Simple check - try to get client
            if self.service_bus_client.client:
                return {"status": "healthy"}
            return {"status": "unhealthy", "error": "Service Bus client not connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_key_vault_health(self) -> Dict[str, Any]:
        """Check Key Vault health"""
        if not self.key_vault_client:
            return {"status": "unavailable", "error": "Key Vault client not initialized"}

        try:
            # Try to list secrets (lightweight operation)
            secrets = self.key_vault_client.list_secrets()
            return {"status": "healthy", "secrets_count": len(secrets)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        database_health = self.check_database_health()
        service_bus_health = self.check_service_bus_health()
        key_vault_health = self.check_key_vault_health()

        components = {
            "api": {"status": "healthy"},
            "database": database_health,
            "service_bus": service_bus_health,
            "key_vault": key_vault_health
        }

        # Determine overall status
        all_healthy = all(
            comp.get("status") == "healthy" or comp.get("status") == "unavailable"
            for comp in components.values()
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "components": components
        }

    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }

        # Get workflow metrics
        if self.db_manager:
            try:
                workflow_query = """
                SELECT 
                    COUNT(*) as total_workflows,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_workflows,
                    COUNT(*) FILTER (WHERE status = 'running') as running_workflows,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_workflows
                FROM workflows
                """
                results = self.db_manager.execute_query(workflow_query)
                if results:
                    metrics["workflows"] = {
                        "total": results[0].get("total_workflows", 0),
                        "completed": results[0].get("completed_workflows", 0),
                        "running": results[0].get("running_workflows", 0),
                        "failed": results[0].get("failed_workflows", 0)
                    }
            except Exception as e:
                logger.debug(f"Error getting workflow metrics: {e}")

            # Get ticket metrics
            try:
                ticket_query = """
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(*) FILTER (WHERE status = 'open') as open_tickets,
                    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_tickets
                FROM helpdesk_tickets
                """
                results = self.db_manager.execute_query(ticket_query)
                if results:
                    metrics["tickets"] = {
                        "total": results[0].get("total_tickets", 0),
                        "open": results[0].get("open_tickets", 0),
                        "resolved": results[0].get("resolved_tickets", 0)
                    }
            except Exception as e:
                logger.debug(f"Error getting ticket metrics: {e}")

            # Get user metrics
            try:
                user_query = """
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE is_active = TRUE) as active_users
                FROM users
                """
                results = self.db_manager.execute_query(user_query)
                if results:
                    metrics["users"] = {
                        "total": results[0].get("total_users", 0),
                        "active": results[0].get("active_users", 0)
                    }
            except Exception as e:
                logger.debug(f"Error getting user metrics: {e}")

        return metrics


def get_monitoring_service(project_root: Optional[Path] = None) -> MonitoringService:
    """Get global monitoring service"""
    return MonitoringService(project_root)
