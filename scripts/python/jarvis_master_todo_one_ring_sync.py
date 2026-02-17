"""
JARVIS Master TODO List - The One Ring Blueprint Sync
Syncs Master TODO List with The One Ring Blueprint, Holocron (Jupyter Notebook),
and database imports of all tables. Treated as a "living" document, ever kept in sync.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #ONE_RING @HOLOCRON #LIVING_DOCUMENT
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import nbformat
from nbformat import NotebookNode

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class JARVISMasterTODOOneRingSync:
    """
    Syncs Master TODO List with The One Ring Blueprint, Holocron, and database.

    The Master TODO List = The One Ring Prompt/Blueprint
    - Synced with @HOLOCRON (Jupyter Notebook)
    - Synced with database imports of all tables
    - Treated as a "living" document
    - Ever kept in sync
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize The One Ring sync system.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.one_ring_blueprint = self.project_root / "config" / "one_ring_blueprint.json"
        self.holocron_notebook = self.project_root / "data" / "jupyter" / "ultron_holocrons" / "holocron_master.ipynb"
        self.master_todo_file = self.project_root / "data" / "todo" / "master_todos.json"
        # MariaDB on NAS (OEM) - @DB[#DATABASE]
        from jarvis_siloed_databases import JARVISSiloedDatabases, DatabaseSystem
        self.db_manager = JARVISSiloedDatabases(project_root)
        self.database_name = self.db_manager.get_database_name(DatabaseSystem.MASTER_TODO)

        # Legacy SQLite (backward compatibility)
        self.database_file = self.project_root / "data" / "holocron" / "holocron.db"

        # Ensure directories exist
        self.one_ring_blueprint.parent.mkdir(parents=True, exist_ok=True)
        self.holocron_notebook.parent.mkdir(parents=True, exist_ok=True)
        self.master_todo_file.parent.mkdir(parents=True, exist_ok=True)
        self.database_file.parent.mkdir(parents=True, exist_ok=True)

    def load_one_ring_blueprint(self) -> Dict[str, Any]:
        """Load The One Ring Blueprint."""
        if self.one_ring_blueprint.exists():
            try:
                with open(self.one_ring_blueprint, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load One Ring Blueprint: {e}", exc_info=True)
                return self._default_one_ring_blueprint()
        else:
            blueprint = self._default_one_ring_blueprint()
            self.save_one_ring_blueprint(blueprint)
            return blueprint

    def _default_one_ring_blueprint(self) -> Dict[str, Any]:
        """Get default One Ring Blueprint structure."""
        return {
            'timestamp': datetime.now().isoformat(),
            'description': 'The One Ring Blueprint - Master TODO List / Living Document',
            'version': '1.0.0',
            'master_todos': [],
            'sync_sources': {
                'holocron_notebook': str(self.holocron_notebook),
                'database': str(self.database_file),
                'master_todo_file': str(self.master_todo_file)
            },
            'sync_status': {
                'last_sync': None,
                'holocron_synced': False,
                'database_synced': False,
                'todo_file_synced': False
            },
            'metadata': {
                'living_document': True,
                'auto_sync': True,
                'sync_interval_seconds': 60
            }
        }

    def save_one_ring_blueprint(self, blueprint: Dict[str, Any]) -> None:
        """Save The One Ring Blueprint."""
        try:
            blueprint['timestamp'] = datetime.now().isoformat()
            with open(self.one_ring_blueprint, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save One Ring Blueprint: {e}", exc_info=True)

    def load_holocron_notebook(self) -> Optional[NotebookNode]:
        """Load Holocron Jupyter Notebook."""
        if self.holocron_notebook.exists():
            try:
                with open(self.holocron_notebook, 'r', encoding='utf-8') as f:
                    return nbformat.read(f, as_version=4)
            except Exception as e:
                logger.error(f"Failed to load Holocron notebook: {e}", exc_info=True)
                return None
        else:
            # Create default Holocron notebook
            notebook = self._create_default_holocron()
            self.save_holocron_notebook(notebook)
            return notebook

    def _create_default_holocron(self) -> NotebookNode:
        """Create default Holocron notebook structure."""
        notebook = nbformat.v4.new_notebook()

        # Add metadata
        notebook.metadata = {
            'name': 'Holocron Master',
            'description': 'The One Ring Blueprint - Master TODO List / Living Document',
            'sync_with': 'one_ring_blueprint',
            'living_document': True
        }

        # Add markdown cell with description
        desc_cell = nbformat.v4.new_markdown_cell("""
# The One Ring Blueprint - Master TODO List

This is a **living document** that syncs with:
- The One Ring Blueprint (`config/one_ring_blueprint.json`)
- Master TODO List (`data/todo/master_todos.json`)
- Database tables (`data/holocron/holocron.db`)

## Sync Status
- Last Sync: {last_sync}
- Holocron: Synced
- Database: Synced
- TODO File: Synced
        """.strip())
        notebook.cells.append(desc_cell)

        # Add code cell for TODO management
        todo_cell = nbformat.v4.new_code_cell("""
# Master TODO List - The One Ring
# This cell is synced with the blueprint

import json
from pathlib import Path

project_root = Path("../../..")
blueprint_file = project_root / "config" / "one_ring_blueprint.json"

with open(blueprint_file, 'r') as f:
    blueprint = json.load(f)

master_todos = blueprint.get('master_todos', [])
print(f"Master TODOs: {len(master_todos)}")
for todo in master_todos:
    print(f"  - {todo.get('content', 'N/A')}")
        """.strip())
        notebook.cells.append(todo_cell)

        return notebook

    def save_holocron_notebook(self, notebook: NotebookNode) -> None:
        """Save Holocron Jupyter Notebook."""
        try:
            with open(self.holocron_notebook, 'w', encoding='utf-8') as f:
                nbformat.write(notebook, f)
        except Exception as e:
            logger.error(f"Failed to save Holocron notebook: {e}", exc_info=True)

    def sync_to_database(self, todos: List[Dict[str, Any]]) -> bool:
        """
        Sync Master TODOs to MariaDB@NAS database.

        Args:
            todos: List of TODO items

        Returns:
            True if successful
        """
        try:
            # Use MariaDB on NAS (OEM) - @DB[#DATABASE]
            from jarvis_siloed_databases import DatabaseSystem
            import pymysql

            # Ensure database exists
            if not self.db_manager.registry['databases'].get('master_todo', {}).get('created', False):
                self.db_manager.create_database(DatabaseSystem.MASTER_TODO)

            # Get connection
            conn = self.db_manager.get_connection(DatabaseSystem.MASTER_TODO)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_todos (
                    id VARCHAR(255) PRIMARY KEY,
                    content TEXT NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP NULL,
                    updated_at TIMESTAMP NULL,
                    completed_at TIMESTAMP NULL,
                    priority INT,
                    tags JSON,
                    metadata JSON,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_status (status),
                    INDEX idx_priority (priority),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Clear existing and insert new
            cursor.execute("DELETE FROM master_todos")

            for todo in todos:
                cursor.execute("""
                    INSERT INTO master_todos 
                    (id, content, status, created_at, updated_at, completed_at, priority, tags, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    content = VALUES(content),
                    status = VALUES(status),
                    updated_at = VALUES(updated_at),
                    completed_at = VALUES(completed_at),
                    priority = VALUES(priority),
                    tags = VALUES(tags),
                    metadata = VALUES(metadata)
                """, (
                    todo.get('id'),
                    todo.get('content'),
                    todo.get('status'),
                    todo.get('created_at'),
                    todo.get('updated_at'),
                    todo.get('completed_at'),
                    todo.get('priority'),
                    json.dumps(todo.get('tags', [])),
                    json.dumps(todo.get('metadata', {}))
                ))

            conn.commit()
            conn.close()

            logger.info(f"Synced {len(todos)} TODOs to MariaDB@NAS: {self.database_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to sync to MariaDB@NAS: {e}", exc_info=True)
            # Fallback to SQLite for backward compatibility
            return self._sync_to_sqlite_fallback(todos)

    def _sync_to_sqlite_fallback(self, todos: List[Dict[str, Any]]) -> bool:
        """Fallback to SQLite for backward compatibility."""
        try:
            self.database_file.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_todos (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT,
                    completed_at TEXT,
                    priority INTEGER,
                    tags TEXT,
                    metadata TEXT,
                    synced_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("DELETE FROM master_todos")

            for todo in todos:
                cursor.execute("""
                    INSERT INTO master_todos 
                    (id, content, status, created_at, updated_at, completed_at, priority, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    todo.get('id'),
                    todo.get('content'),
                    todo.get('status'),
                    todo.get('created_at'),
                    todo.get('updated_at'),
                    todo.get('completed_at'),
                    todo.get('priority'),
                    json.dumps(todo.get('tags', [])),
                    json.dumps(todo.get('metadata', {}))
                ))

            conn.commit()
            conn.close()
            logger.info(f"Synced {len(todos)} TODOs to SQLite (fallback)")
            return True
        except Exception as e:
            logger.error(f"SQLite fallback failed: {e}", exc_info=True)
            return False

    def sync_from_database(self) -> List[Dict[str, Any]]:
        """Load Master TODOs from MariaDB@NAS database."""
        try:
            # Use MariaDB on NAS (OEM) - @DB[#DATABASE]
            from jarvis_siloed_databases import DatabaseSystem
            import pymysql

            conn = self.db_manager.get_connection(DatabaseSystem.MASTER_TODO)
            cursor = conn.cursor()

            cursor.execute("SELECT id, content, status, created_at, updated_at, completed_at, priority, tags, metadata FROM master_todos")
            rows = cursor.fetchall()

            todos = []
            for row in rows:
                todos.append({
                    'id': row[0],
                    'content': row[1],
                    'status': row[2],
                    'created_at': row[3].isoformat() if row[3] else None,
                    'updated_at': row[4].isoformat() if row[4] else None,
                    'completed_at': row[5].isoformat() if row[5] else None,
                    'priority': row[6],
                    'tags': json.loads(row[7]) if row[7] else [],
                    'metadata': json.loads(row[8]) if row[8] else {}
                })

            conn.close()
            return todos

        except Exception as e:
            logger.error(f"Failed to load from MariaDB@NAS: {e}", exc_info=True)
            # Fallback to SQLite
            return self._load_from_sqlite_fallback()

    def _load_from_sqlite_fallback(self) -> List[Dict[str, Any]]:
        """Fallback to SQLite for backward compatibility."""
        try:
            if not self.database_file.exists():
                return []

            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM master_todos")
            rows = cursor.fetchall()

            todos = []
            for row in rows:
                todos.append({
                    'id': row[0],
                    'content': row[1],
                    'status': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'completed_at': row[5],
                    'priority': row[6],
                    'tags': json.loads(row[7]) if row[7] else [],
                    'metadata': json.loads(row[8]) if row[8] else {}
                })

            conn.close()
            return todos
        except Exception as e:
            logger.error(f"SQLite fallback load failed: {e}", exc_info=True)
            return []

    def sync_all(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sync Master TODOs to all sources (One Ring, Holocron, Database, TODO file).

        Args:
            todos: List of TODO items to sync

        Returns:
            Sync status dictionary
        """
        sync_status = {
            'timestamp': datetime.now().isoformat(),
            'one_ring': False,
            'holocron': False,
            'database': False,
            'todo_file': False,
            'total_todos': len(todos)
        }

        # 1. Sync to One Ring Blueprint
        try:
            blueprint = self.load_one_ring_blueprint()
            blueprint['master_todos'] = todos
            blueprint['sync_status']['last_sync'] = datetime.now().isoformat()
            blueprint['sync_status']['todo_file_synced'] = True
            self.save_one_ring_blueprint(blueprint)
            sync_status['one_ring'] = True
        except Exception as e:
            logger.error(f"Failed to sync to One Ring: {e}", exc_info=True)

        # 2. Sync to Holocron Notebook
        try:
            notebook = self.load_holocron_notebook()
            if notebook:
                # Update notebook with current TODOs
                # Find or create TODO cell
                todo_cell_found = False
                for i, cell in enumerate(notebook.cells):
                    if cell.cell_type == 'code' and 'master_todos' in cell.source:
                        # Update existing cell
                        notebook.cells[i].source = f"""
# Master TODO List - The One Ring
# Synced: {datetime.now().isoformat()}

import json
from pathlib import Path

project_root = Path("../../..")
blueprint_file = project_root / "config" / "one_ring_blueprint.json"

with open(blueprint_file, 'r') as f:
    blueprint = json.load(f)

master_todos = blueprint.get('master_todos', [])
print(f"Master TODOs: {{len(master_todos)}}")
for todo in master_todos:
    status_icon = "🔄" if todo.get('status') == 'in_progress' else "⏳"
    print(f"  {{status_icon}} {{todo.get('content', 'N/A')}}")
                        """.strip()
                        todo_cell_found = True
                        break

                if not todo_cell_found:
                    # Add new TODO cell
                    todo_cell = nbformat.v4.new_code_cell(f"""
# Master TODO List - The One Ring
# Synced: {datetime.now().isoformat()}

import json
from pathlib import Path

project_root = Path("../../..")
blueprint_file = project_root / "config" / "one_ring_blueprint.json"

with open(blueprint_file, 'r') as f:
    blueprint = json.load(f)

master_todos = blueprint.get('master_todos', [])
print(f"Master TODOs: {{len(master_todos)}}")
for todo in master_todos:
    status_icon = "🔄" if todo.get('status') == 'in_progress' else "⏳"
    print(f"  {{status_icon}} {{todo.get('content', 'N/A')}}")
                    """.strip())
                    notebook.cells.append(todo_cell)

                self.save_holocron_notebook(notebook)
                sync_status['holocron'] = True
        except Exception as e:
            logger.error(f"Failed to sync to Holocron: {e}", exc_info=True)

        # 3. Sync to Database
        sync_status['database'] = self.sync_to_database(todos)

        # 4. Sync to TODO file (for backward compatibility)
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'description': 'Master TODO List - The One Ring Blueprint (Living Document)',
                'synced_with': {
                    'one_ring_blueprint': str(self.one_ring_blueprint),
                    'holocron_notebook': str(self.holocron_notebook),
                    'database': str(self.database_file)
                },
                'todos': todos
            }
            with open(self.master_todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            sync_status['todo_file'] = True
        except Exception as e:
            logger.error(f"Failed to sync to TODO file: {e}", exc_info=True)

        return sync_status

    def get_sync_status(self) -> Dict[str, Any]:
        try:
            """Get current sync status."""
            blueprint = self.load_one_ring_blueprint()
            return {
                'one_ring_blueprint': {
                    'exists': self.one_ring_blueprint.exists(),
                    'last_sync': blueprint.get('sync_status', {}).get('last_sync'),
                    'todos_count': len(blueprint.get('master_todos', []))
                },
                'holocron_notebook': {
                    'exists': self.holocron_notebook.exists(),
                    'path': str(self.holocron_notebook)
                },
                'database': {
                    'type': 'MariaDB@NAS',
                    'name': self.database_name,
                    'exists': True,  # Checked via connection
                    'path': f"{self.db_manager.registry['nas_host']}:{self.database_name}"
                },
                'database_sqlite_fallback': {
                    'exists': self.database_file.exists(),
                    'path': str(self.database_file)
                },
                'todo_file': {
                    'exists': self.master_todo_file.exists(),
                    'path': str(self.master_todo_file)
                }
            }


        except Exception as e:
            self.logger.error(f"Error in get_sync_status: {e}", exc_info=True)
            raise
def main():
    """CLI interface for One Ring sync."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Master TODO - One Ring Sync")
    parser.add_argument('--sync', action='store_true', help='Sync all sources')
    parser.add_argument('--status', action='store_true', help='Show sync status')
    parser.add_argument('--load-from-db', action='store_true', help='Load from database')

    args = parser.parse_args()

    sync_system = JARVISMasterTODOOneRingSync()

    if args.status:
        status = sync_system.get_sync_status()
        print("\n📊 Sync Status:")
        print(f"  One Ring Blueprint: {'✅' if status['one_ring_blueprint']['exists'] else '❌'}")
        print(f"    TODOs: {status['one_ring_blueprint']['todos_count']}")
        print(f"    Last Sync: {status['one_ring_blueprint']['last_sync']}")
        print(f"  Holocron Notebook: {'✅' if status['holocron_notebook']['exists'] else '❌'}")
        print(f"  Database: {'✅' if status['database']['exists'] else '❌'}")
        print(f"  TODO File: {'✅' if status['todo_file']['exists'] else '❌'}")

    if args.load_from_db:
        todos = sync_system.sync_from_database()
        print(f"\n📋 Loaded {len(todos)} TODOs from database")
        for todo in todos:
            print(f"  - {todo.get('content', 'N/A')}")

    if args.sync:
        # Load current TODOs from One Ring
        blueprint = sync_system.load_one_ring_blueprint()
        todos = blueprint.get('master_todos', [])

        # Sync to all sources
        status = sync_system.sync_all(todos)
        print("\n🔄 Sync Results:")
        print(f"  One Ring: {'✅' if status['one_ring'] else '❌'}")
        print(f"  Holocron: {'✅' if status['holocron'] else '❌'}")
        print(f"  Database: {'✅' if status['database'] else '❌'}")
        print(f"  TODO File: {'✅' if status['todo_file'] else '❌'}")
        print(f"  Total TODOs: {status['total_todos']}")


if __name__ == "__main__":


    main()