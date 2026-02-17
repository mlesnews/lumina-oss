#!/usr/bin/env python3
"""
Extend MariaDB Schema for Control Interfaces

Adds tables for commands, APIs, and CLI tools to the homelab audit database.

Tags: #HOMELAB #AUDIT #MARIADB #SCHEMA #CONTROL @JARVIS @LUMINA
"""

import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger

    from scripts.python.jarvis_mariadb_nas_connection import JARVISMariaDBNASConnection
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("extend_audit_mariadb_schema")


def extend_schema(
    host: str, user: str, password: str, database: str = "homelab_audit", port: int = 3306
):
    """Extend MariaDB schema with control interface tables"""

    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset="utf8mb4",
            cursorclass=DictCursor,
        )
        cursor = conn.cursor()

        print("Extending schema with control interface tables...")

        # Commands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_commands (
                command_id VARCHAR(255) PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL,
                feature_id VARCHAR(255),
                name VARCHAR(255) NOT NULL,
                command TEXT NOT NULL,
                description TEXT,
                parameters JSON,
                examples JSON,
                requires_admin BOOLEAN DEFAULT FALSE,
                platform VARCHAR(50),
                category VARCHAR(100),
                discovered_at DATETIME,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                INDEX idx_device_id (device_id),
                INDEX idx_category (category),
                INDEX idx_platform (platform)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ device_commands table created")

        # API endpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_api_endpoints (
                endpoint_id VARCHAR(255) PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL,
                feature_id VARCHAR(255),
                name VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                method VARCHAR(10) NOT NULL,
                description TEXT,
                parameters JSON,
                authentication VARCHAR(50),
                examples JSON,
                response_format VARCHAR(20) DEFAULT 'json',
                discovered_at DATETIME,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                INDEX idx_device_id (device_id),
                INDEX idx_method (method),
                INDEX idx_authentication (authentication)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ device_api_endpoints table created")

        # CLI tools table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_cli_tools (
                cli_id VARCHAR(255) PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                executable VARCHAR(255),
                description TEXT,
                version VARCHAR(50),
                available BOOLEAN DEFAULT FALSE,
                installation_path VARCHAR(500),
                discovered_at DATETIME,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                INDEX idx_device_id (device_id),
                INDEX idx_available (available)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ device_cli_tools table created")

        # Command execution log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_execution_log (
                execution_id INT AUTO_INCREMENT PRIMARY KEY,
                command_id VARCHAR(255) NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                executed_at DATETIME NOT NULL,
                command_string TEXT,
                parameters JSON,
                success BOOLEAN,
                returncode INT,
                stdout TEXT,
                stderr TEXT,
                execution_time_ms INT,
                FOREIGN KEY (command_id) REFERENCES device_commands(command_id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                INDEX idx_command_id (command_id),
                INDEX idx_device_id (device_id),
                INDEX idx_executed_at (executed_at),
                INDEX idx_success (success)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ command_execution_log table created")

        # API test log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_test_log (
                test_id INT AUTO_INCREMENT PRIMARY KEY,
                endpoint_id VARCHAR(255) NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                tested_at DATETIME NOT NULL,
                url TEXT,
                method VARCHAR(10),
                parameters JSON,
                success BOOLEAN,
                status_code INT,
                response_time_ms INT,
                response_preview TEXT,
                error_message TEXT,
                FOREIGN KEY (endpoint_id) REFERENCES device_api_endpoints(endpoint_id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                INDEX idx_endpoint_id (endpoint_id),
                INDEX idx_device_id (device_id),
                INDEX idx_tested_at (tested_at),
                INDEX idx_success (success)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ api_test_log table created")

        # Control interface registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS control_interface_registry (
                interface_id VARCHAR(255) PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                control_type VARCHAR(50),
                commands_count INT DEFAULT 0,
                api_endpoints_count INT DEFAULT 0,
                cli_tools_count INT DEFAULT 0,
                discovered_at DATETIME,
                last_updated DATETIME,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                INDEX idx_device_id (device_id),
                INDEX idx_control_type (control_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ control_interface_registry table created")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n✅ Schema extension complete!")
        return True

    except Exception as e:
        logger.error(f"Failed to extend schema: {e}")
        return False


def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Extend MariaDB schema for control interfaces")
    parser.add_argument(
        "--host", default=os.environ.get("MARIADB_HOST", "<NAS_PRIMARY_IP>"), help="MariaDB host"
    )
    parser.add_argument(
        "--user", default=os.environ.get("MARIADB_USER", "dbadmin"), help="MariaDB user"
    )
    parser.add_argument(
        "--password", default=os.environ.get("MARIADB_PASSWORD"), help="MariaDB password"
    )
    parser.add_argument("--database", default="homelab_audit", help="Database name")

    args = parser.parse_args()

    if not args.password:
        # Try to get from connection manager
        manager = JARVISMariaDBNASConnection()
        params = manager.get_connection_params(args.database, args.user)
        args.password = params["password"]
        args.host = params["host"]
        args.port = params["port"]

    if extend_schema(args.host, args.user, args.password, args.database, args.port):
        print("\n✅ Schema extended successfully!")
    else:
        print("\n❌ Schema extension failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
