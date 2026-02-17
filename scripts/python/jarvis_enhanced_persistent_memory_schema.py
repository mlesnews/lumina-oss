#!/usr/bin/env python3
"""
JARVIS Enhanced Persistent Memory Schema

Creates optimized database tables and cells for improved persistent memory
with enhanced querying capabilities for long-term storage.

Features:
- Optimized table structures
- Enhanced indexing for fast queries
- Cell-level organization
- Long-term storage optimization
- NAS integration for archival

Tags: #DATABASE[@DB] @TEAM @DBE @DBA
"""

import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEnhancedMemorySchema")


class EnhancedPersistentMemorySchema:
    """
    Enhanced Persistent Memory Schema

    Creates optimized database structure for long-term memory storage
    with improved querying capabilities.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Database paths
        self.memory_dir = project_root / "data" / "jarvis_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Enhanced database
        self.enhanced_db_path = self.memory_dir / "enhanced_memory.db"

        # NAS integration
        self.nas_backup_path = None
        self._init_nas_integration()

        self.logger.info("✅ Enhanced Persistent Memory Schema initialized")

    def _init_nas_integration(self):
        """Initialize NAS integration for long-term storage"""
        try:
            nas_path = Path(f"\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\jarvis_memory")
            # Don't check exists() - just set path for when NAS is accessible
            self.nas_backup_path = nas_path
            self.logger.debug("NAS backup path configured")
        except Exception:
            pass

    def create_enhanced_schema(self) -> Dict[str, Any]:
        """
        Create enhanced database schema with optimized tables and cells

        Enhanced Structure:
        - memories: Core memory storage (enhanced)
        - memory_cells: Cell-level organization for granular access
        - memory_index: Full-text search index
        - memory_relationships: Relationship graph
        - memory_metadata: Extended metadata
        - memory_archives: Long-term archival storage
        """
        self.logger.info("🔨 Creating enhanced persistent memory schema...")

        try:
            conn = sqlite3.connect(str(self.enhanced_db_path))
            cursor = conn.cursor()

            # 1. Enhanced memories table (core storage)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    context TEXT,
                    tags TEXT,
                    source TEXT,
                    timestamp TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    related_memories TEXT,
                    cell_id TEXT,
                    archived BOOLEAN DEFAULT 0,
                    nas_backed_up BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # 2. Memory cells (cell-level organization)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_cells (
                    cell_id TEXT PRIMARY KEY,
                    cell_name TEXT NOT NULL,
                    cell_type TEXT NOT NULL,
                    description TEXT,
                    parent_cell_id TEXT,
                    memory_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (parent_cell_id) REFERENCES memory_cells(cell_id)
                )
            ''')

            # 3. Memory index (full-text search)
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_index USING fts5(
                    memory_id,
                    content,
                    tags,
                    context,
                    source,
                    content='memories',
                    content_rowid='rowid'
                )
            ''')

            # 4. Memory relationships (relationship graph)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_relationships (
                    relationship_id TEXT PRIMARY KEY,
                    memory_id_1 TEXT NOT NULL,
                    memory_id_2 TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (memory_id_1) REFERENCES memories(memory_id),
                    FOREIGN KEY (memory_id_2) REFERENCES memories(memory_id),
                    UNIQUE(memory_id_1, memory_id_2, relationship_type)
                )
            ''')

            # 5. Memory metadata (extended metadata)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_metadata (
                    metadata_id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (memory_id) REFERENCES memories(memory_id),
                    UNIQUE(memory_id, key)
                )
            ''')

            # 6. Memory archives (long-term archival)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_archives (
                    archive_id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    archive_reason TEXT,
                    archived_at TEXT NOT NULL,
                    restore_priority INTEGER DEFAULT 0,
                    nas_location TEXT,
                    FOREIGN KEY (memory_id) REFERENCES memories(memory_id)
                )
            ''')

            # 7. Memory statistics (query optimization)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_statistics (
                    stat_id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    query_count INTEGER DEFAULT 0,
                    last_queried TEXT,
                    query_patterns TEXT,
                    performance_score REAL DEFAULT 0.0,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (memory_id) REFERENCES memories(memory_id)
                )
            ''')

            # Create indexes for fast queries
            self._create_indexes(cursor)

            conn.commit()
            conn.close()

            self.logger.info("✅ Enhanced schema created successfully")

            return {
                "success": True,
                "database_path": str(self.enhanced_db_path),
                "tables_created": [
                    "memories",
                    "memory_cells",
                    "memory_index",
                    "memory_relationships",
                    "memory_metadata",
                    "memory_archives",
                    "memory_statistics"
                ]
            }

        except Exception as e:
            self.logger.error(f"❌ Schema creation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _create_indexes(self, cursor):
        """Create optimized indexes for fast queries"""
        indexes = [
            # Memory type and priority indexes
            "CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_memory_priority ON memories(priority)",
            "CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memories(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_memory_last_accessed ON memories(last_accessed)",
            "CREATE INDEX IF NOT EXISTS idx_memory_access_count ON memories(access_count)",

            # Cell indexes
            "CREATE INDEX IF NOT EXISTS idx_memory_cell ON memories(cell_id)",
            "CREATE INDEX IF NOT EXISTS idx_cell_type ON memory_cells(cell_type)",
            "CREATE INDEX IF NOT EXISTS idx_cell_parent ON memory_cells(parent_cell_id)",

            # Relationship indexes
            "CREATE INDEX IF NOT EXISTS idx_relationship_memory1 ON memory_relationships(memory_id_1)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_memory2 ON memory_relationships(memory_id_2)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_type ON memory_relationships(relationship_type)",

            # Metadata indexes
            "CREATE INDEX IF NOT EXISTS idx_metadata_memory ON memory_metadata(memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_metadata_key ON memory_metadata(key)",

            # Archive indexes
            "CREATE INDEX IF NOT EXISTS idx_archive_memory ON memory_archives(memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_archive_priority ON memory_archives(restore_priority)",

            # Statistics indexes
            "CREATE INDEX IF NOT EXISTS idx_stat_memory ON memory_statistics(memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_stat_performance ON memory_statistics(performance_score)",

            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_memory_type_priority ON memories(memory_type, priority)",
            "CREATE INDEX IF NOT EXISTS idx_memory_accessed_count ON memories(last_accessed, access_count)",
            "CREATE INDEX IF NOT EXISTS idx_memory_archived ON memories(archived, nas_backed_up)"
        ]

        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                self.logger.debug(f"Index creation warning: {e}")

    def create_memory_cells(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create memory cells for organized storage

        Cells are organizational units that group related memories
        for better querying and management.
        """
        self.logger.info(f"📦 Creating {len(cells)} memory cell(s)...")

        try:
            conn = sqlite3.connect(str(self.enhanced_db_path))
            cursor = conn.cursor()

            created_cells = []
            for cell in cells:
                cell_id = cell.get("cell_id") or f"cell_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(cell.get('cell_name', '')) % 10000}"

                cursor.execute('''
                    INSERT OR REPLACE INTO memory_cells
                    (cell_id, cell_name, cell_type, description, parent_cell_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cell_id,
                    cell.get("cell_name", "Unnamed Cell"),
                    cell.get("cell_type", "general"),
                    cell.get("description", ""),
                    cell.get("parent_cell_id"),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

                created_cells.append(cell_id)

            conn.commit()
            conn.close()

            self.logger.info(f"✅ Created {len(created_cells)} memory cell(s)")

            return {
                "success": True,
                "cells_created": len(created_cells),
                "cell_ids": created_cells
            }

        except Exception as e:
            self.logger.error(f"❌ Cell creation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def migrate_existing_memories(self, source_db_path: Path) -> Dict[str, Any]:
        """Migrate existing memories to enhanced schema"""
        self.logger.info(f"🔄 Migrating memories from {source_db_path}...")

        try:
            # Connect to source database
            source_conn = sqlite3.connect(str(source_db_path))
            source_cursor = source_conn.cursor()

            # Connect to enhanced database
            enhanced_conn = sqlite3.connect(str(self.enhanced_db_path))
            enhanced_cursor = enhanced_conn.cursor()

            # Read existing memories
            source_cursor.execute("SELECT * FROM memories")
            rows = source_cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in source_cursor.description]

            migrated_count = 0
            for row in rows:
                memory_dict = dict(zip(column_names, row))

                # Generate content hash
                import hashlib
                content_hash = hashlib.sha256(memory_dict.get("content", "").encode()).hexdigest()

                # Insert into enhanced schema
                enhanced_cursor.execute('''
                    INSERT OR REPLACE INTO memories
                    (memory_id, memory_type, priority, content, content_hash, context, tags, source,
                     timestamp, last_accessed, access_count, related_memories, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory_dict.get("memory_id"),
                    memory_dict.get("memory_type"),
                    memory_dict.get("priority"),
                    memory_dict.get("content"),
                    content_hash,
                    json.dumps(memory_dict.get("context", {})),
                    json.dumps(memory_dict.get("tags", [])),
                    memory_dict.get("source", ""),
                    memory_dict.get("timestamp"),
                    memory_dict.get("last_accessed"),
                    memory_dict.get("access_count", 0),
                    json.dumps(memory_dict.get("related_memories", [])),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

                # Update full-text index
                enhanced_cursor.execute('''
                    INSERT OR REPLACE INTO memory_index
                    (memory_id, content, tags, context, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    memory_dict.get("memory_id"),
                    memory_dict.get("content"),
                    json.dumps(memory_dict.get("tags", [])),
                    json.dumps(memory_dict.get("context", {})),
                    memory_dict.get("source", "")
                ))

                migrated_count += 1

            enhanced_conn.commit()
            source_conn.close()
            enhanced_conn.close()

            self.logger.info(f"✅ Migrated {migrated_count} memories to enhanced schema")

            return {
                "success": True,
                "memories_migrated": migrated_count
            }

        except Exception as e:
            self.logger.error(f"❌ Migration failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the enhanced schema"""
        try:
            conn = sqlite3.connect(str(self.enhanced_db_path))
            cursor = conn.cursor()

            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # Get index info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
            indexes = [row[0] for row in cursor.fetchall()]

            # Get table row counts
            table_counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                except Exception:
                    pass

            conn.close()

            return {
                "database_path": str(self.enhanced_db_path),
                "tables": tables,
                "table_count": len(tables),
                "indexes": indexes,
                "index_count": len(indexes),
                "table_row_counts": table_counts
            }

        except Exception as e:
            return {
                "error": str(e)
            }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Enhanced Persistent Memory Schema")
        parser.add_argument("--create", action="store_true", help="Create enhanced schema")
        parser.add_argument("--migrate", type=str, help="Migrate from existing database")
        parser.add_argument("--info", action="store_true", help="Get schema information")
        parser.add_argument("--create-cells", type=str, help="Create memory cells (JSON file)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        schema = EnhancedPersistentMemorySchema(project_root)

        if args.create:
            result = schema.create_enhanced_schema()
            import json
            print(json.dumps(result, indent=2))

        elif args.migrate:
            result = schema.migrate_existing_memories(Path(args.migrate))
            import json
            print(json.dumps(result, indent=2))

        elif args.create_cells:
            import json as json_module
            with open(args.create_cells, 'r', encoding='utf-8') as f:
                cells_data = json_module.load(f)
            cells = cells_data.get("memory_cells", cells_data if isinstance(cells_data, list) else [])
            result = schema.create_memory_cells(cells)
            print(json_module.dumps(result, indent=2))

        elif args.info:
            info = schema.get_schema_info()
            import json
            print(json.dumps(info, indent=2, default=str))

        else:
            print("Usage:")
            print("  --create              : Create enhanced schema")
            print("  --migrate <db_path>  : Migrate from existing database")
            print("  --create-cells <json> : Create memory cells from JSON")
            print("  --info                : Get schema information")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()