#!/usr/bin/env python3
"""
Database Connection Manager
Manages PostgreSQL database connections with Azure Key Vault integration

All database connections use secrets from Azure Key Vault.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DatabaseConnectionManager")

# PostgreSQL imports
try:
    import psycopg2
    from psycopg2 import pool, sql
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("psycopg2 not available. Install with: pip install psycopg2-binary")

# Azure Key Vault integration
try:
    from azure_service_bus_integration import get_key_vault_client
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure Key Vault integration not available")


class DatabaseConnectionManager:
    """Manages PostgreSQL database connections"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self.key_vault_client = None

        # Initialize Key Vault client
        if AZURE_AVAILABLE:
            try:
                self.key_vault_client = get_key_vault_client()
                logger.info("Key Vault client initialized for database connections")
            except Exception as e:
                logger.warning(f"Key Vault not available: {e}")

        self._initialize_connection_pool()

    def _get_connection_string(self) -> str:
        """Get database connection string from Key Vault"""
        if self.key_vault_client:
            try:
                connection_string = self.key_vault_client.get_secret("postgres-connection-string")
                return connection_string
            except Exception as e:
                logger.error(f"Failed to get connection string from Key Vault: {e}")

        # Fallback to environment variable
        import os
        connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("Database connection string not found in Key Vault or environment")

        return connection_string

    def _initialize_connection_pool(self):
        """Initialize connection pool"""
        if not POSTGRES_AVAILABLE:
            logger.error("PostgreSQL not available")
            return

        try:
            connection_string = self._get_connection_string()

            # Create connection pool
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=connection_string
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            self.connection_pool = None

    def get_connection(self):
        """Get a database connection from the pool"""
        if not self.connection_pool:
            raise RuntimeError("Connection pool not initialized")

        return self.connection_pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute a SELECT query and return results"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.return_connection(conn)

    def execute_transaction(self, queries: list) -> bool:
        """Execute multiple queries in a transaction"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                for query, params in queries:
                    cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)

    def close_pool(self):
        """Close the connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")


def get_db_manager(project_root: Optional[Path] = None) -> DatabaseConnectionManager:
    """Get global database connection manager"""
    return DatabaseConnectionManager(project_root)


if __name__ == "__main__":
    # Test database connection
    db_manager = get_db_manager()

    print("=" * 60)
    print("Database Connection Manager")
    print("=" * 60)

    try:
        # Test connection
        conn = db_manager.get_connection()
        print("✅ Database connection successful")
        db_manager.return_connection(conn)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    print("=" * 60)
