#!/usr/bin/env python3
"""
Database Migration Manager
Manages database schema migrations

Applies database schemas as defined in database_schemas.json
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

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

logger = get_logger("DatabaseMigrationManager")

try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger.error("Database connection manager not available")


class DatabaseMigrationManager:
    """Manages database schema migrations"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.schema_file = self.project_root / "docs" / "data_models" / "database_schemas.json"
        self.migration_log_dir = self.project_root / "data" / "database" / "migrations"
        self.migration_log_dir.mkdir(parents=True, exist_ok=True)

        if DB_AVAILABLE:
            self.db_manager = get_db_manager(project_root)
        else:
            self.db_manager = None

    def load_schemas(self) -> Dict[str, Any]:
        try:
            """Load database schemas from JSON file"""
            if not self.schema_file.exists():
                logger.error(f"Schema file not found: {self.schema_file}")
                return {}

            with open(self.schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_schemas: {e}", exc_info=True)
            raise
    def create_migration_table(self):
        """Create migration tracking table"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return False

        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            applied_by VARCHAR(255),
            status VARCHAR(50) DEFAULT 'applied'
        );
        """

        try:
            self.db_manager.execute_update(query)
            logger.info("Migration tracking table created")
            return True
        except Exception as e:
            logger.error(f"Error creating migration table: {e}")
            return False

    def is_migration_applied(self, migration_name: str) -> bool:
        """Check if a migration has been applied"""
        if not self.db_manager:
            return False

        query = "SELECT COUNT(*) as count FROM schema_migrations WHERE migration_name = %s"
        try:
            results = self.db_manager.execute_query(query, (migration_name,))
            return results[0]['count'] > 0 if results else False
        except Exception:
            # Table might not exist yet
            return False

    def mark_migration_applied(self, migration_name: str):
        """Mark a migration as applied"""
        if not self.db_manager:
            return

        query = """
        INSERT INTO schema_migrations (migration_name, applied_by, status)
        VALUES (%s, %s, 'applied')
        ON CONFLICT (migration_name) DO NOTHING
        """

        try:
            self.db_manager.execute_update(query, (migration_name, "migration_manager"))
        except Exception as e:
            logger.error(f"Error marking migration as applied: {e}")

    def apply_schema(self, schema_name: str, ddl: str) -> bool:
        """Apply a database schema"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return False

        if self.is_migration_applied(schema_name):
            logger.info(f"Migration {schema_name} already applied, skipping")
            return True

        try:
            # Execute DDL
            self.db_manager.execute_update(ddl)

            # Mark as applied
            self.mark_migration_applied(schema_name)

            logger.info(f"✅ Applied migration: {schema_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error applying migration {schema_name}: {e}")
            return False

    def apply_all_schemas(self) -> Dict[str, bool]:
        """Apply all database schemas"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return {}

        # Create migration tracking table first
        self.create_migration_table()

        schemas = self.load_schemas()
        results = {}

        # Apply each schema
        for schema_name, schema_data in schemas.get("schemas", {}).items():
            ddl = schema_data.get("ddl", "")
            if ddl:
                results[schema_name] = self.apply_schema(schema_name, ddl)
            else:
                logger.warning(f"No DDL found for schema: {schema_name}")
                results[schema_name] = False

        return results


def main():
    try:
        """Main migration function"""
        project_root = Path(__file__).parent.parent.parent
        migration_manager = DatabaseMigrationManager(project_root)

        print("=" * 60)
        print("Database Migration Manager")
        print("=" * 60)

        results = migration_manager.apply_all_schemas()

        print("\nMigration Results:")
        for schema_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {schema_name}")

        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from typing import Optional


    main()