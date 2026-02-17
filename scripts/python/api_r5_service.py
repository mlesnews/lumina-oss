#!/usr/bin/env python3
"""
API R5 Knowledge Service
Handles R5 knowledge search and ingestion

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

logger = get_logger("APIR5Service")

try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from r5_service_bus_integration import publish_knowledge_entry
    from azure_service_bus_integration import get_service_bus_client, get_key_vault_client
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False


class R5Service:
    """Handles R5 knowledge operations"""

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

    def search_knowledge(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search R5 knowledge"""
        if not self.db_manager:
            return {"results": [], "total": 0, "query": query}

        # Build search query
        where_clauses = ["content ILIKE %s OR tags::text ILIKE %s"]
        params = [f"%{query}%", f"%{query}%"]

        if filters:
            if filters.get("category"):
                where_clauses.append("category = %s")
                params.append(filters["category"])
            if filters.get("tags"):
                where_clauses.append("tags && %s")
                params.append(filters["tags"])
            if filters.get("min_relevance"):
                where_clauses.append("relevance_score >= %s")
                params.append(filters["min_relevance"])

        where_sql = " AND ".join(where_clauses)

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM r5_entries WHERE {where_sql}"
        count_results = self.db_manager.execute_query(count_query, tuple(params))
        total = count_results[0]['total'] if count_results else 0

        # Get results
        query_sql = f"""
        SELECT id, entry_id, category, content, tags, patterns, timestamp, metadata,
               source, relevance_score
        FROM r5_entries
        WHERE {where_sql}
        ORDER BY relevance_score DESC NULLS LAST, timestamp DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        try:
            results = self.db_manager.execute_query(query_sql, tuple(params))
            entries = [
                {
                    "id": str(e["id"]),
                    "entry_id": e.get("entry_id"),
                    "category": e.get("category"),
                    "content": e.get("content"),
                    "tags": e.get("tags", []),
                    "patterns": e.get("patterns", []),
                    "timestamp": e["timestamp"].isoformat() if hasattr(e["timestamp"], 'isoformat') else str(e["timestamp"]),
                    "metadata": e.get("metadata"),
                    "source": e.get("source"),
                    "relevance_score": e.get("relevance_score")
                }
                for e in results
            ]

            return {
                "results": entries,
                "total": total,
                "query": query,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {"results": [], "total": 0, "query": query}

    def ingest_knowledge(
        self,
        entry_id: str,
        category: str,
        content: str,
        tags: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        extract_patterns: bool = True
    ) -> Dict[str, Any]:
        """Ingest knowledge into R5"""
        if not self.db_manager:
            raise RuntimeError("Database manager not available")

        entry_uuid = str(uuid.uuid4())

        # Insert into database
        query = """
        INSERT INTO r5_entries (id, entry_id, category, content, tags, patterns, metadata, source, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id, entry_id, category, content, tags, patterns, timestamp, metadata, source
        """

        try:
            results = self.db_manager.execute_query(
                query,
                (
                    entry_uuid,
                    entry_id,
                    category,
                    content,
                    tags or [],
                    patterns or [],
                    json.dumps(metadata or {}),
                    source
                )
            )

            if not results:
                raise Exception("Knowledge ingestion failed")

            entry = results[0]

            # Publish to Service Bus for pattern extraction
            if self.service_bus_client and extract_patterns:
                publish_knowledge_entry({
                    "id": str(entry["id"]),
                    "entry_id": entry_id,
                    "category": category,
                    "content": content,
                    "tags": tags,
                    "patterns": patterns,
                    "metadata": metadata,
                    "source": source
                }, extract_patterns=True, sb_client=self.service_bus_client)

            return {
                "id": str(entry["id"]),
                "entry_id": entry.get("entry_id"),
                "category": entry.get("category"),
                "content": entry.get("content"),
                "tags": entry.get("tags", []),
                "patterns": entry.get("patterns", []),
                "timestamp": entry["timestamp"].isoformat() if hasattr(entry["timestamp"], 'isoformat') else str(entry["timestamp"]),
                "metadata": entry.get("metadata"),
                "source": entry.get("source")
            }
        except Exception as e:
            logger.error(f"Error ingesting knowledge: {e}")
            raise


def get_r5_service(project_root: Optional[Path] = None) -> R5Service:
    """Get global R5 service"""
    return R5Service(project_root)
