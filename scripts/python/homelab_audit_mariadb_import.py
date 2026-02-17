#!/usr/bin/env python3
"""
Homelab Audit MariaDB Import System

Imports homelab audit data into MariaDB@NAS-DSM via Holocron format.
Creates and manages database schema for living audit data.

Tags: #HOMELAB #AUDIT #MARIADB #HOLOCRON #IMPORT @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pymysql
from pymysql.cursors import DictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_audit_mariadb_import")


class HomelabAuditMariaDBImporter:
    """Imports homelab audit data to MariaDB"""

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
            logger.error(f"Failed to connect to MariaDB: {e}")
            return False

    def create_schema(self):
        """Create database schema for homelab audit"""
        if not self.connection:
            if not self.connect():
                return False

        cursor = self.connection.cursor()

        try:
            # Create database if not exists
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE {self.database}")

            # Devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id VARCHAR(255) PRIMARY KEY,
                    device_name VARCHAR(255) NOT NULL,
                    device_type VARCHAR(100),
                    hostname VARCHAR(255),
                    ip_address VARCHAR(45),
                    mac_address VARCHAR(17),
                    operating_system VARCHAR(100),
                    os_version VARCHAR(100),
                    os_architecture VARCHAR(50),
                    manufacturer VARCHAR(255),
                    model VARCHAR(255),
                    serial_number VARCHAR(255),
                    discovered_at DATETIME,
                    last_audited DATETIME,
                    audit_version INT DEFAULT 1,
                    complexity_score DECIMAL(10, 2) DEFAULT 0.0,
                    complexity_drift JSON,
                    metadata JSON,
                    INDEX idx_device_type (device_type),
                    INDEX idx_ip_address (ip_address),
                    INDEX idx_last_audited (last_audited)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Features table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_features (
                    feature_id VARCHAR(255) PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    description TEXT,
                    value JSON,
                    unit VARCHAR(50),
                    enabled BOOLEAN DEFAULT TRUE,
                    configurable BOOLEAN DEFAULT FALSE,
                    default_value JSON,
                    current_value JSON,
                    dependencies JSON,
                    commands JSON,
                    metadata JSON,
                    discovered_at DATETIME,
                    last_verified DATETIME,
                    complexity_drift JSON,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id),
                    INDEX idx_category (category),
                    INDEX idx_enabled (enabled)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Commands table (for detailed command tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_commands (
                    command_id VARCHAR(255) PRIMARY KEY,
                    feature_id VARCHAR(255) NOT NULL,
                    device_id VARCHAR(255) NOT NULL,
                    command_type VARCHAR(50),
                    command_text TEXT NOT NULL,
                    shell_type VARCHAR(50),
                    description TEXT,
                    parameters JSON,
                    examples JSON,
                    output_format VARCHAR(50),
                    requires_elevation BOOLEAN DEFAULT FALSE,
                    discovered_at DATETIME,
                    last_verified DATETIME,
                    FOREIGN KEY (feature_id) REFERENCES device_features(feature_id) ON DELETE CASCADE,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_feature_id (feature_id),
                    INDEX idx_device_id (device_id),
                    INDEX idx_command_type (command_type),
                    INDEX idx_shell_type (shell_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Services table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_services (
                    service_id VARCHAR(255) PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(50),
                    pid INT,
                    port INT,
                    protocol VARCHAR(20),
                    metadata JSON,
                    discovered_at DATETIME,
                    last_verified DATETIME,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Network interfaces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_network_interfaces (
                    interface_id VARCHAR(255) PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    is_up BOOLEAN,
                    speed BIGINT,
                    addresses JSON,
                    metadata JSON,
                    discovered_at DATETIME,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Storage devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_storage (
                    storage_id VARCHAR(255) PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    device_path VARCHAR(255),
                    mountpoint VARCHAR(255),
                    fstype VARCHAR(50),
                    total_bytes BIGINT,
                    used_bytes BIGINT,
                    free_bytes BIGINT,
                    usage_percent DECIMAL(5, 2),
                    discovered_at DATETIME,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Installed software table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_software (
                    software_id VARCHAR(255) PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    version VARCHAR(100),
                    publisher VARCHAR(255),
                    install_date DATETIME,
                    metadata JSON,
                    discovered_at DATETIME,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id),
                    INDEX idx_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Configuration files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_config_files (
                    config_id VARCHAR(255) PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size BIGINT,
                    modified_at DATETIME,
                    metadata JSON,
                    discovered_at DATETIME,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Audit history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_history (
                    audit_id VARCHAR(255) PRIMARY KEY,
                    audit_timestamp DATETIME NOT NULL,
                    audit_version VARCHAR(50),
                    total_devices INT,
                    total_features INT,
                    total_complexity_score DECIMAL(10, 2),
                    drift_detected_count INT,
                    ecosystem_complexity JSON,
                    metadata JSON,
                    INDEX idx_audit_timestamp (audit_timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Complexity drift log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS complexity_drift_log (
                    drift_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    drift_timestamp DATETIME NOT NULL,
                    drift_type VARCHAR(100),
                    previous_value JSON,
                    current_value JSON,
                    delta JSON,
                    metadata JSON,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
                    INDEX idx_device_id (device_id),
                    INDEX idx_drift_timestamp (drift_timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            self.connection.commit()
            logger.info("Schema created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def import_audit(self, audit_data: Dict[str, Any]) -> bool:
        """Import audit data to MariaDB"""
        if not self.connection:
            if not self.connect():
                return False

        cursor = self.connection.cursor()

        try:
            # Import audit history
            cursor.execute(
                """
                INSERT INTO audit_history
                (audit_id, audit_timestamp, audit_version, total_devices, total_features,
                 total_complexity_score, drift_detected_count, ecosystem_complexity, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    audit_timestamp = VALUES(audit_timestamp),
                    total_devices = VALUES(total_devices),
                    total_features = VALUES(total_features),
                    total_complexity_score = VALUES(total_complexity_score),
                    drift_detected_count = VALUES(drift_detected_count),
                    ecosystem_complexity = VALUES(ecosystem_complexity),
                    metadata = VALUES(metadata)
            """,
                (
                    audit_data["audit_id"],
                    audit_data["audit_timestamp"],
                    audit_data.get("audit_version", "1.0.0"),
                    len(audit_data.get("devices", [])),
                    sum(len(d.get("features", [])) for d in audit_data.get("devices", [])),
                    audit_data.get("ecosystem_complexity", {}).get("total_complexity_score", 0.0),
                    len(audit_data.get("drift_detected", [])),
                    json.dumps(audit_data.get("ecosystem_complexity", {})),
                    json.dumps(audit_data.get("metadata", {})),
                ),
            )

            # Import devices
            for device_data in audit_data.get("devices", []):
                self._import_device(cursor, device_data)

            # Import drift logs
            for drift_data in audit_data.get("drift_detected", []):
                self._import_drift_log(cursor, drift_data)

            self.connection.commit()
            logger.info(f"Audit imported: {audit_data['audit_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to import audit: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def _import_device(self, cursor, device_data: Dict[str, Any]):
        """Import device data"""
        # Insert/update device
        cursor.execute(
            """
            INSERT INTO devices
            (device_id, device_name, device_type, hostname, ip_address, mac_address,
             operating_system, os_version, os_architecture, manufacturer, model,
             serial_number, discovered_at, last_audited, audit_version, complexity_score,
             complexity_drift, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                device_name = VALUES(device_name),
                device_type = VALUES(device_type),
                hostname = VALUES(hostname),
                ip_address = VALUES(ip_address),
                mac_address = VALUES(mac_address),
                operating_system = VALUES(operating_system),
                os_version = VALUES(os_version),
                os_architecture = VALUES(os_architecture),
                manufacturer = VALUES(manufacturer),
                model = VALUES(model),
                serial_number = VALUES(serial_number),
                last_audited = VALUES(last_audited),
                audit_version = VALUES(audit_version),
                complexity_score = VALUES(complexity_score),
                complexity_drift = VALUES(complexity_drift),
                metadata = VALUES(metadata)
        """,
            (
                device_data["device_id"],
                device_data["device_name"],
                device_data.get("device_type"),
                device_data.get("hostname"),
                device_data.get("ip_address"),
                device_data.get("mac_address"),
                device_data.get("operating_system"),
                device_data.get("os_version"),
                device_data.get("os_architecture"),
                device_data.get("manufacturer"),
                device_data.get("model"),
                device_data.get("serial_number"),
                device_data.get("discovered_at"),
                device_data.get("last_audited"),
                device_data.get("audit_version", 1),
                device_data.get("complexity_score", 0.0),
                json.dumps(device_data.get("complexity_drift", {})),
                json.dumps(device_data.get("metadata", {})),
            ),
        )

        # Import features
        for feature_data in device_data.get("features", []):
            cursor.execute(
                """
                INSERT INTO device_features
                (feature_id, device_id, name, category, subcategory, description, value,
                 unit, enabled, configurable, default_value, current_value, dependencies,
                 metadata, discovered_at, last_verified, complexity_drift)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    category = VALUES(category),
                    subcategory = VALUES(subcategory),
                    description = VALUES(description),
                    value = VALUES(value),
                    unit = VALUES(unit),
                    enabled = VALUES(enabled),
                    configurable = VALUES(configurable),
                    default_value = VALUES(default_value),
                    current_value = VALUES(current_value),
                    dependencies = VALUES(dependencies),
                    metadata = VALUES(metadata),
                    last_verified = VALUES(last_verified),
                    complexity_drift = VALUES(complexity_drift)
            """,
                (
                    feature_data["feature_id"],
                    device_data["device_id"],
                    feature_data["name"],
                    feature_data.get("category"),
                    feature_data.get("subcategory"),
                    feature_data.get("description"),
                    json.dumps(feature_data.get("value")),
                    feature_data.get("unit"),
                    feature_data.get("enabled", True),
                    feature_data.get("configurable", False),
                    json.dumps(feature_data.get("default_value")),
                    json.dumps(feature_data.get("current_value")),
                    json.dumps(feature_data.get("dependencies", [])),
                    json.dumps(feature_data.get("metadata", {})),
                    feature_data.get("discovered_at"),
                    feature_data.get("last_verified"),
                    json.dumps(feature_data.get("complexity_drift", {})),
                ),
            )

        # Import services
        for service_data in device_data.get("services", []):
            cursor.execute(
                """
                INSERT INTO device_services
                (service_id, device_id, name, status, pid, port, protocol, metadata, discovered_at, last_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    pid = VALUES(pid),
                    port = VALUES(port),
                    protocol = VALUES(protocol),
                    metadata = VALUES(metadata),
                    last_verified = VALUES(last_verified)
            """,
                (
                    f"{device_data['device_id']}_service_{service_data.get('name', 'unknown')}",
                    device_data["device_id"],
                    service_data.get("name"),
                    service_data.get("status"),
                    service_data.get("pid"),
                    service_data.get("port"),
                    service_data.get("protocol"),
                    json.dumps(service_data.get("metadata", {})),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        # Import network interfaces
        for interface_data in device_data.get("network_interfaces", []):
            cursor.execute(
                """
                INSERT INTO device_network_interfaces
                (interface_id, device_id, name, is_up, speed, addresses, metadata, discovered_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    is_up = VALUES(is_up),
                    speed = VALUES(speed),
                    addresses = VALUES(addresses),
                    metadata = VALUES(metadata)
            """,
                (
                    f"{device_data['device_id']}_interface_{interface_data.get('name', 'unknown')}",
                    device_data["device_id"],
                    interface_data.get("name"),
                    interface_data.get("is_up"),
                    interface_data.get("speed"),
                    json.dumps(interface_data.get("addresses", [])),
                    json.dumps(interface_data.get("metadata", {})),
                    datetime.now().isoformat(),
                ),
            )

        # Import storage
        for storage_data in device_data.get("storage_devices", []):
            cursor.execute(
                """
                INSERT INTO device_storage
                (storage_id, device_id, device_path, mountpoint, fstype, total_bytes,
                 used_bytes, free_bytes, usage_percent, discovered_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_bytes = VALUES(total_bytes),
                    used_bytes = VALUES(used_bytes),
                    free_bytes = VALUES(free_bytes),
                    usage_percent = VALUES(usage_percent)
            """,
                (
                    f"{device_data['device_id']}_storage_{storage_data.get('device', 'unknown')}",
                    device_data["device_id"],
                    storage_data.get("device"),
                    storage_data.get("mountpoint"),
                    storage_data.get("fstype"),
                    storage_data.get("total"),
                    storage_data.get("used"),
                    storage_data.get("free"),
                    storage_data.get("percent"),
                    datetime.now().isoformat(),
                ),
            )

    def _import_drift_log(self, cursor, drift_data: Dict[str, Any]):
        """Import complexity drift log"""
        device_id = drift_data.get("device_id")
        drift = drift_data.get("drift", {})

        for change in drift.get("changes", []):
            cursor.execute(
                """
                INSERT INTO complexity_drift_log
                (device_id, drift_timestamp, drift_type, previous_value, current_value, delta, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    device_id,
                    drift.get("timestamp", datetime.now().isoformat()),
                    change.get("type"),
                    json.dumps(change.get("previous")),
                    json.dumps(change.get("current")),
                    json.dumps(change.get("delta")),
                    json.dumps(change.get("features", [])),
                ),
            )

    def export_to_holocron(self, audit_id: Optional[str] = None) -> Dict[str, Any]:
        """Export audit data to Holocron format"""
        if not self.connection:
            if not self.connect():
                return {}

        cursor = self.connection.cursor()

        try:
            # Get latest audit or specific audit
            if audit_id:
                cursor.execute("SELECT * FROM audit_history WHERE audit_id = %s", (audit_id,))
            else:
                cursor.execute("SELECT * FROM audit_history ORDER BY audit_timestamp DESC LIMIT 1")

            audit_record = cursor.fetchone()
            if not audit_record:
                return {}

            # Build Holocron structure
            holocron = {
                "holocron_metadata": {
                    "holocron_id": f"HOLOCRON-HOMELAB-AUDIT-{audit_record['audit_id']}",
                    "title": f"Homelab Top-Down Audit - {audit_record['audit_timestamp']}",
                    "classification": "homelab_audit",
                    "created_at": audit_record["audit_timestamp"].isoformat()
                    if hasattr(audit_record["audit_timestamp"], "isoformat")
                    else str(audit_record["audit_timestamp"]),
                    "source": "homelab_topdown_audit",
                    "version": audit_record.get("audit_version", "1.0.0"),
                },
                "audit_data": {
                    "audit_id": audit_record["audit_id"],
                    "audit_timestamp": audit_record["audit_timestamp"].isoformat()
                    if hasattr(audit_record["audit_timestamp"], "isoformat")
                    else str(audit_record["audit_timestamp"]),
                    "total_devices": audit_record["total_devices"],
                    "total_features": audit_record["total_features"],
                    "total_complexity_score": float(audit_record["total_complexity_score"]),
                    "ecosystem_complexity": json.loads(audit_record["ecosystem_complexity"])
                    if isinstance(audit_record["ecosystem_complexity"], str)
                    else audit_record["ecosystem_complexity"],
                },
                "devices": [],
            }

            # Get all devices
            cursor.execute(
                "SELECT * FROM devices WHERE device_id IN (SELECT DISTINCT device_id FROM device_features)"
            )
            devices = cursor.fetchall()

            for device in devices:
                device_holocron = {
                    "device_id": device["device_id"],
                    "device_name": device["device_name"],
                    "device_type": device["device_type"],
                    "operating_system": device["operating_system"],
                    "complexity_score": float(device["complexity_score"]),
                    "features": [],
                }

                # Get features for device
                cursor.execute(
                    "SELECT * FROM device_features WHERE device_id = %s", (device["device_id"],)
                )
                features = cursor.fetchall()

                for feature in features:
                    device_holocron["features"].append(
                        {
                            "feature_id": feature["feature_id"],
                            "name": feature["name"],
                            "category": feature["category"],
                            "value": json.loads(feature["value"])
                            if isinstance(feature["value"], str)
                            else feature["value"],
                            "enabled": bool(feature["enabled"]),
                        }
                    )

                holocron["devices"].append(device_holocron)

            return holocron

        except Exception as e:
            logger.error(f"Failed to export to Holocron: {e}")
            return {}
        finally:
            cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Import homelab audit data to MariaDB")
    parser.add_argument(
        "--host", default=os.environ.get("MARIADB_HOST", "<NAS_PRIMARY_IP>"), help="MariaDB host"
    )
    parser.add_argument(
        "--user", default=os.environ.get("MARIADB_USER", "lumina"), help="MariaDB user"
    )
    parser.add_argument(
        "--password", default=os.environ.get("MARIADB_PASSWORD"), help="MariaDB password"
    )
    parser.add_argument("--database", default="homelab_audit", help="Database name")
    parser.add_argument("--create-schema", action="store_true", help="Create database schema")
    parser.add_argument("--import-audit", metavar="AUDIT_FILE", help="Import audit JSON file")
    parser.add_argument(
        "--export-holocron",
        metavar="AUDIT_ID",
        nargs="?",
        const="latest",
        help="Export to Holocron format (optional: specific audit_id)",
    )

    args = parser.parse_args()

    if not args.password:
        print("Error: MariaDB password required (--password or MARIADB_PASSWORD env var)")
        sys.exit(1)

    importer = HomelabAuditMariaDBImporter(
        host=args.host, user=args.user, password=args.password, database=args.database
    )

    if args.create_schema:
        if importer.connect():
            importer.create_schema()

    if args.import_audit:
        audit_file = Path(args.import_audit)
        if audit_file.exists():
            with open(audit_file, encoding="utf-8") as f:
                audit_data = json.load(f)
            if importer.connect():
                importer.import_audit(audit_data)
        else:
            print(f"Error: Audit file not found: {audit_file}")

    if args.export_holocron:
        if importer.connect():
            audit_id = None if args.export_holocron == "latest" else args.export_holocron
            holocron = importer.export_to_holocron(audit_id=audit_id)
            print(json.dumps(holocron, indent=2, default=str))

    importer.close()


if __name__ == "__main__":
    main()
