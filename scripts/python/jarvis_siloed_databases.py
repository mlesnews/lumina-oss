"""
JARVIS Siloed Databases System
Multi-database architecture for LUMINA systems.

Standing Order: @DB[#DATABASE] = MariaDB@NAS (OEM)
Multiple databases for siloed systems:
- @HELPDESK: Helpdesk system
- @HOLOGRAM: Metadata linking to Jupyter Notebooks
- Additional systems as needed

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA @DB #DATABASE #MARIADB #NAS @HELPDESK @HOLOGRAM
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from jarvis_mariadb_nas_connection import JARVISMariaDBNASConnection, get_mariadb_connection

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class DatabaseSystem(str, Enum):
    """Database system identifiers."""
    HELPDESK = "helpdesk"
    HOLOGRAM = "hologram"
    MASTER_TODO = "master_todo"
    SYPHON = "syphon"
    JARVIS = "jarvis"
    HOLOCRON = "holocron"


class JARVISSiloedDatabases:
    """
    Manages siloed databases on MariaDB@NAS.

    Architecture:
    - One database per system/category
    - Siloed for separation of concerns
    - All on MariaDB@NAS
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize siloed databases manager.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # Database registry
        self.registry_file = self.project_root / "config" / "lumina_db_registry.json"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

        # Connection manager
        self.connection_manager = JARVISMariaDBNASConnection(project_root)

        # Load registry
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load database registry."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load registry: {e}", exc_info=True)
                return self._default_registry()
        else:
            registry = self._default_registry()
            self._save_registry(registry)
            return registry

    def _default_registry(self) -> Dict[str, Any]:
        """Get default database registry."""
        return {
            'timestamp': datetime.now().isoformat(),
            'description': 'LUMINA Database Registry - Siloed Databases on MariaDB@NAS',
            'oem_database': 'MariaDB@NAS',
            'nas_host': '<NAS_PRIMARY_IP>',
            'nas_hostname': '<LOCAL_HOSTNAME>',
            'databases': {
                'helpdesk': {
                    'name': 'helpdesk',
                    'system': '@HELPDESK',
                    'description': 'Helpdesk system database',
                    'created': False,
                    'tables': []
                },
                'hologram': {
                    'name': 'hologram',
                    'system': '@HOLOGRAM',
                    'description': 'Metadata linking to Jupyter Notebooks',
                    'created': False,
                    'tables': ['notebook_metadata', 'notebook_links', 'internal_urls']
                },
                'master_todo': {
                    'name': 'master_todo',
                    'system': '@ONE_RING',
                    'description': 'Master TODO List - The One Ring Blueprint',
                    'created': False,
                    'tables': ['master_todos']
                },
                'holocron': {
                    'name': 'holocron',
                    'system': '@HOLOCRON',
                    'description': 'Holocron Jupyter Notebook database',
                    'created': False,
                    'tables': []
                }
            }
        }

    def _save_registry(self, registry: Optional[Dict[str, Any]] = None) -> None:
        """Save database registry."""
        if registry is None:
            registry = self.registry
        try:
            registry['timestamp'] = datetime.now().isoformat()
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}", exc_info=True)

    def get_database_name(self, system: DatabaseSystem) -> str:
        """
        Get database name for system.

        Args:
            system: Database system identifier

        Returns:
            Database name
        """
        return self.registry['databases'].get(system.value, {}).get('name', system.value)

    def create_database(self, system: DatabaseSystem) -> bool:
        """
        Create database for system.

        Args:
            system: Database system identifier

        Returns:
            True if successful
        """
        db_name = self.get_database_name(system)

        try:
            # Connect to MySQL (no database specified)
            conn = self.connection_manager.get_connection("mysql")
            cursor = conn.cursor()

            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()

            # Update registry
            if system.value in self.registry['databases']:
                self.registry['databases'][system.value]['created'] = True
                self.registry['databases'][system.value]['created_at'] = datetime.now().isoformat()
                self._save_registry()

            conn.close()
            logger.info(f"Created database: {db_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create database {db_name}: {e}", exc_info=True)
            return False

    def get_connection(self, system: DatabaseSystem) -> Any:
        """
        Get database connection for system.

        Args:
            system: Database system identifier

        Returns:
            Database connection
        """
        db_name = self.get_database_name(system)
        return self.connection_manager.get_connection(db_name)

    def setup_hologram_database(self) -> bool:
        """
        Setup @HOLOGRAM database with metadata tables.

        Returns:
            True if successful
        """
        try:
            # Create database if not exists
            if not self.registry['databases']['hologram']['created']:
                if not self.create_database(DatabaseSystem.HOLOGRAM):
                    return False

            # Get connection
            conn = self.get_connection(DatabaseSystem.HOLOGRAM)
            cursor = conn.cursor()

            # Create notebook_metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notebook_metadata (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    notebook_path TEXT NOT NULL,
                    notebook_name VARCHAR(255) NOT NULL,
                    jupyter_url TEXT,
                    internal_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    metadata JSON,
                    INDEX idx_notebook_name (notebook_name),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Create notebook_links table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notebook_links (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    source_notebook_id INT,
                    target_notebook_id INT,
                    link_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_notebook_id) REFERENCES notebook_metadata(id),
                    FOREIGN KEY (target_notebook_id) REFERENCES notebook_metadata(id),
                    INDEX idx_source (source_notebook_id),
                    INDEX idx_target (target_notebook_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Create internal_urls table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS internal_urls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    url TEXT NOT NULL,
                    notebook_id INT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (notebook_id) REFERENCES notebook_metadata(id),
                    INDEX idx_notebook (notebook_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            conn.commit()
            conn.close()

            logger.info("Setup @HOLOGRAM database with metadata tables")
            return True

        except Exception as e:
            logger.error(f"Failed to setup @HOLOGRAM database: {e}", exc_info=True)
            return False

    def setup_helpdesk_database(self) -> bool:
        """
        Setup @HELPDESK database.

        Returns:
            True if successful
        """
        try:
            # Create database if not exists
            if not self.registry['databases']['helpdesk']['created']:
                if not self.create_database(DatabaseSystem.HELPDESK):
                    return False

            logger.info("Setup @HELPDESK database")
            return True

        except Exception as e:
            logger.error(f"Failed to setup @HELPDESK database: {e}", exc_info=True)
            return False

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get registry summary."""
        return {
            'oem_database': self.registry['oem_database'],
            'nas_host': self.registry['nas_host'],
            'total_databases': len(self.registry['databases']),
            'databases': {
                name: {
                    'created': info.get('created', False),
                    'system': info.get('system', ''),
                    'tables': info.get('tables', [])
                }
                for name, info in self.registry['databases'].items()
            }
        }


def main():
    """CLI interface for siloed databases."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Siloed Databases")
    parser.add_argument('--setup-hologram', action='store_true', help='Setup @HOLOGRAM database')
    parser.add_argument('--setup-helpdesk', action='store_true', help='Setup @HELPDESK database')
    parser.add_argument('--registry', action='store_true', help='Show registry')

    args = parser.parse_args()

    manager = JARVISSiloedDatabases()

    if args.setup_hologram:
        if manager.setup_hologram_database():
            print("✅ @HOLOGRAM database setup complete")
        else:
            print("❌ @HOLOGRAM database setup failed")

    if args.setup_helpdesk:
        if manager.setup_helpdesk_database():
            print("✅ @HELPDESK database setup complete")
        else:
            print("❌ @HELPDESK database setup failed")

    if args.registry:
        summary = manager.get_registry_summary()
        print("\n📊 Database Registry:")
        print(f"  OEM Database: {summary['oem_database']}")
        print(f"  NAS Host: {summary['nas_host']}")
        print(f"  Total Databases: {summary['total_databases']}")
        print("\n  Databases:")
        for name, info in summary['databases'].items():
            status = "✅" if info['created'] else "❌"
            print(f"    {status} {name} ({info['system']})")
            if info['tables']:
                print(f"      Tables: {', '.join(info['tables'])}")


if __name__ == "__main__":


    main()