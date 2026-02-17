#!/usr/bin/env python3
"""
Import Control Interfaces to MariaDB

Imports control interface data (commands, APIs, CLIs) into MariaDB@NAS-DSM.

Tags: #HOMELAB #CONTROL #MARIADB #IMPORT @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
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

logger = get_logger("import_control_interfaces_mariadb")


class ControlInterfaceMariaDBImporter:
    """Imports control interfaces to MariaDB"""

    def __init__(
        self, host: str, user: str, password: str, database: str = "homelab_audit", port: int = 3306
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        """Connect to MariaDB"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset="utf8mb4",
                cursorclass=DictCursor,
            )
            logger.info(f"Connected to MariaDB: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def import_control_map(self, control_map_file: Path) -> bool:
        """Import control interface map"""
        if not self.connection:
            if not self.connect():
                return False

        with open(control_map_file, encoding="utf-8") as f:
            control_map = json.load(f)

        cursor = self.connection.cursor()

        try:
            interfaces = control_map.get("interfaces", [])

            for interface in interfaces:
                device_id = interface["device_id"]

                # Import control interface registry
                cursor.execute(
                    """
                    INSERT INTO control_interface_registry
                    (interface_id, device_id, name, description, control_type,
                     commands_count, api_endpoints_count, cli_tools_count, discovered_at, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        description = VALUES(description),
                        control_type = VALUES(control_type),
                        commands_count = VALUES(commands_count),
                        api_endpoints_count = VALUES(api_endpoints_count),
                        cli_tools_count = VALUES(cli_tools_count),
                        last_updated = VALUES(last_updated)
                """,
                    (
                        interface["interface_id"],
                        device_id,
                        interface["name"],
                        interface.get("description"),
                        interface.get("control_type"),
                        len(interface.get("commands", [])),
                        len(interface.get("api_endpoints", [])),
                        len(interface.get("cli_tools", [])),
                        interface.get("discovered_at", datetime.now().isoformat()),
                        datetime.now().isoformat(),
                    ),
                )

                # Import commands
                for cmd in interface.get("commands", []):
                    cursor.execute(
                        """
                        INSERT INTO device_commands
                        (command_id, device_id, feature_id, name, command, description,
                         parameters, examples, requires_admin, platform, category, discovered_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            command = VALUES(command),
                            description = VALUES(description),
                            parameters = VALUES(parameters),
                            examples = VALUES(examples),
                            requires_admin = VALUES(requires_admin),
                            platform = VALUES(platform),
                            category = VALUES(category)
                    """,
                        (
                            cmd["command_id"],
                            device_id,
                            cmd.get("feature_id"),
                            cmd["name"],
                            cmd["command"],
                            cmd.get("description"),
                            json.dumps(cmd.get("parameters", [])),
                            json.dumps(cmd.get("examples", [])),
                            cmd.get("requires_admin", False),
                            cmd.get("platform"),
                            cmd.get("category"),
                            cmd.get("discovered_at", datetime.now().isoformat()),
                        ),
                    )

                # Import API endpoints
                for api in interface.get("api_endpoints", []):
                    cursor.execute(
                        """
                        INSERT INTO device_api_endpoints
                        (endpoint_id, device_id, feature_id, name, url, method, description,
                         parameters, authentication, examples, response_format, discovered_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            url = VALUES(url),
                            method = VALUES(method),
                            description = VALUES(description),
                            parameters = VALUES(parameters),
                            authentication = VALUES(authentication),
                            examples = VALUES(examples),
                            response_format = VALUES(response_format)
                    """,
                        (
                            api["endpoint_id"],
                            device_id,
                            api.get("feature_id"),
                            api["name"],
                            api["url"],
                            api["method"],
                            api.get("description"),
                            json.dumps(api.get("parameters", [])),
                            api.get("authentication"),
                            json.dumps(api.get("examples", [])),
                            api.get("response_format", "json"),
                            api.get("discovered_at", datetime.now().isoformat()),
                        ),
                    )

                # Import CLI tools
                for cli in interface.get("cli_tools", []):
                    cursor.execute(
                        """
                        INSERT INTO device_cli_tools
                        (cli_id, device_id, name, executable, description, version,
                         available, installation_path, discovered_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            executable = VALUES(executable),
                            description = VALUES(description),
                            version = VALUES(version),
                            available = VALUES(available),
                            installation_path = VALUES(installation_path)
                    """,
                        (
                            cli["cli_id"],
                            device_id,
                            cli["name"],
                            cli.get("executable"),
                            cli.get("description"),
                            cli.get("version"),
                            cli.get("available", False),
                            cli.get("installation_path"),
                            cli.get("discovered_at", datetime.now().isoformat()),
                        ),
                    )

            self.connection.commit()
            logger.info(f"Control interfaces imported: {len(interfaces)} interfaces")
            return True

        except Exception as e:
            logger.error(f"Failed to import: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()


def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Import control interfaces to MariaDB")
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
    parser.add_argument("--map-file", help="Control map file (default: latest)")

    args = parser.parse_args()

    if not args.password:
        # Try to get from connection manager
        manager = JARVISMariaDBNASConnection()
        params = manager.get_connection_params(args.database, args.user)
        args.password = params["password"]
        args.host = params["host"]
        args.port = params["port"]

    # Find control map file
    if args.map_file:
        map_file = Path(args.map_file)
    else:
        control_dir = project_root / "data" / "homelab_control"
        maps = sorted(control_dir.glob("control_map_*.json"), reverse=True)
        if not maps:
            print("❌ No control map files found")
            sys.exit(1)
        map_file = maps[0]
        print(f"Using control map: {map_file.name}")

    importer = ControlInterfaceMariaDBImporter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database,
        port=args.port,
    )

    if importer.connect():
        if importer.import_control_map(map_file):
            print("✅ Control interfaces imported successfully")
        else:
            print("❌ Import failed")
            sys.exit(1)

    importer.close()


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
