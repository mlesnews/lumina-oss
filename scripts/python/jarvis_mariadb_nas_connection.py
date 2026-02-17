"""
JARVIS MariaDB on NAS Connection
Standard database connection for LUMINA - MariaDB on NAS (OEM).

Standing Order: @DB[#DATABASE] = MariaDB@NAS (unless modified)

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA @DB #DATABASE #MARIADB #NAS
"""

import pymysql
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import json

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class JARVISMariaDBNASConnection:
    """
    MariaDB on NAS connection manager.

    Standard: @DB[#DATABASE] = MariaDB@NAS
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize MariaDB on NAS connection.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # NAS connection details
        self.nas_host = "<NAS_PRIMARY_IP>"  # DS1821PLUS
        self.nas_hostname = "<LOCAL_HOSTNAME>"
        self.mariadb_port = 3306

        # Azure Key Vault name
        self.vault_name = "jarvis-lumina"

    def get_connection_params(self, database: str, 
                            username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get MariaDB connection parameters.

        Args:
            database: Database name
            username: Optional username (defaults to dbadmin)

        Returns:
            Connection parameters dictionary
        """
        if username is None:
            username = "dbadmin"

        # Get password from Azure Key Vault via az CLI (COMPUSEC: never log/display)
        password = None
        secret_name = f"mariadb-{username}-password"
        try:
            result = subprocess.run(
                ["az", "keyvault", "secret", "show", "--vault-name", self.vault_name,
                 "--name", secret_name, "--query", "value", "-o", "tsv"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                password = result.stdout.strip().replace("\r", "")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Azure Key Vault CLI not available: {e}")

        if not password:
            raise RuntimeError(
                f"Cannot retrieve MariaDB credentials from vault (secret: {secret_name}). "
                f"Ensure 'az' CLI is installed and authenticated."
            )

        return {
            'host': self.nas_host,
            'port': self.mariadb_port,
            'user': username,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'connect_timeout': 10
        }

    def get_connection(self, database: str, 
                      username: Optional[str] = None) -> pymysql.Connection:
        """
        Get MariaDB connection.

        Args:
            database: Database name
            username: Optional username

        Returns:
            PyMySQL connection object
        """
        params = self.get_connection_params(database, username)

        try:
            conn = pymysql.connect(**params)
            logger.info(f"Connected to MariaDB on NAS: {database}")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to MariaDB on NAS: {e}", exc_info=True)
            raise

    def test_connection(self, database: str = "test") -> bool:
        """
        Test MariaDB connection.

        Args:
            database: Database name to test

        Returns:
            True if connection successful
        """
        try:
            conn = self.get_connection(database)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def get_mariadb_connection(database: str, 
                         username: Optional[str] = None,
                         project_root: Optional[Path] = None) -> pymysql.Connection:
    """
    Convenience function to get MariaDB connection.

    Args:
        database: Database name
        username: Optional username
        project_root: Project root directory

    Returns:
        PyMySQL connection object
    """
    manager = JARVISMariaDBNASConnection(project_root)
    return manager.get_connection(database, username)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS MariaDB on NAS Connection")
    parser.add_argument('--test', type=str, help='Test connection to database')
    parser.add_argument('--list-databases', action='store_true', help='List databases')

    args = parser.parse_args()

    manager = JARVISMariaDBNASConnection()

    if args.test:
        if manager.test_connection(args.test):
            print(f"✅ Connection to '{args.test}' successful")
        else:
            print(f"❌ Connection to '{args.test}' failed")

    if args.list_databases:
        try:
            conn = manager.get_connection("information_schema")
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n📊 Databases on MariaDB@NAS:")
            for db in databases:
                print(f"  - {db[0]}")
            conn.close()
        except Exception as e:
            print(f"❌ Failed to list databases: {e}")
