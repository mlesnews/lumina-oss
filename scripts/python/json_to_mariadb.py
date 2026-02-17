#!/usr/bin/env python3
"""
JSON TO MARIADB CONVERTER
Converts large JSON files into MariaDB tables for efficient querying on NAS

MariaDB is much better than SQLite for:
- Large datasets (millions of records)
- Concurrent access
- Complex queries
- Better indexing and performance
"""

import json
import gzip
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import argparse
import sys
import os

# Add scripts directory to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    print("⚠️  pymysql not installed. Install with: pip install pymysql")

try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

class MariaDBConverter:
    """Converts JSON files into MariaDB tables for efficient querying."""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        if not PYMYSQL_AVAILABLE:
            raise ImportError("pymysql is required. Install with: pip install pymysql")

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def connect(self):
        """Connect to MariaDB."""
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print(f"✅ Connected to MariaDB at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to MariaDB: {e}")
            return False

    def close(self):
        """Close the connection."""
        if self.conn:
            self.conn.close()

    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        try:
            """Flatten nested dictionary."""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(self.flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    # Handle list of dicts - store as JSON string
                    items.append((new_key, json.dumps(v)))
                else:
                    items.append((new_key, v))
            return dict(items)

        except Exception as e:
            self.logger.error(f"Error in flatten_dict: {e}", exc_info=True)
            raise
    def infer_mysql_type(self, value: Any, col_name: str = '') -> str:
        """Infer MySQL/MariaDB type from Python value."""
        if value is None:
            return 'TEXT'
        if isinstance(value, bool):
            return 'BOOLEAN'
        if isinstance(value, int):
            if -2147483648 <= value <= 2147483647:
                return 'INT'
            else:
                return 'BIGINT'
        if isinstance(value, float):
            return 'DOUBLE'
        if isinstance(value, (list, dict)):
            return 'JSON'  # MariaDB supports JSON type
        if isinstance(value, str):
            # Check if it's a date/timestamp
            if 'time' in col_name.lower() or 'date' in col_name.lower():
                if len(value) > 50:
                    return 'TEXT'
                return 'DATETIME'
            # Estimate TEXT vs VARCHAR
            if len(value) > 255:
                return 'TEXT'
            elif len(value) > 100:
                return 'VARCHAR(500)'
            else:
                return 'VARCHAR(255)'
        return 'TEXT'

    def create_table_schema(self, sample_data: List[Dict], table_name: str) -> tuple:
        """Create MariaDB table schema from sample data."""
        if not sample_data:
            return None, {}

        # Flatten all records to get all possible columns
        all_keys = set()
        for record in sample_data[:1000]:  # Sample first 1000 records
            flattened = self.flatten_dict(record)
            all_keys.update(flattened.keys())

        # Determine types for each column
        columns = {}
        type_samples = {}

        for key in sorted(all_keys):
            # Collect samples for this key
            samples = []
            for record in sample_data[:100]:
                flattened = self.flatten_dict(record)
                if key in flattened:
                    samples.append(flattened[key])

            if samples:
                # Use the most common non-None type
                non_none_samples = [s for s in samples if s is not None]
                if non_none_samples:
                    value = non_none_samples[0]
                    columns[key] = self.infer_mysql_type(value, key)
                    type_samples[key] = value

        # Build CREATE TABLE statement
        column_defs = ['`id` INT AUTO_INCREMENT PRIMARY KEY']
        column_defs.append('`imported_at` DATETIME DEFAULT CURRENT_TIMESTAMP')

        for col, dtype in columns.items():
            # Sanitize column name
            safe_col = col.replace(' ', '_').replace('-', '_')
            if dtype == 'JSON':
                column_defs.append(f'`{safe_col}` JSON')
            elif dtype == 'TEXT':
                column_defs.append(f'`{safe_col}` TEXT')
            else:
                column_defs.append(f'`{safe_col}` {dtype}')

        schema = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            {', '.join(column_defs)},
            INDEX `idx_imported_at` (`imported_at`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        return schema, columns

    def convert_json_to_mariadb(self, json_path: Path, table_name: Optional[str] = None) -> bool:
        """Convert a JSON file to a MariaDB table."""
        if not self.conn:
            if not self.connect():
                return False

        print(f"\n📦 Converting {json_path.name} to MariaDB table...")

        # Determine table name
        if not table_name:
            table_name = json_path.stem.replace('.json', '').replace('-', '_').replace(' ', '_')
            # Ensure valid table name
            table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name)

        # Load JSON
        try:
            if json_path.suffix == '.gz' or json_path.name.endswith('.json.gz'):
                with gzip.open(json_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return False

        cursor = self.conn.cursor()

        try:
            if isinstance(data, list):
                if len(data) == 0:
                    print("   ⚠️  Empty list, creating empty table")
                    cursor.execute(f'CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY)')
                elif isinstance(data[0], dict):
                    # List of dictionaries
                    print(f"   📊 Processing {len(data)} records...")
                    schema, columns = self.create_table_schema(data, table_name)

                    # Create table
                    cursor.execute(f'DROP TABLE IF EXISTS `{table_name}`')
                    cursor.execute(schema)

                    # Insert data in batches
                    inserted = 0
                    batch_size = 1000

                    for i in range(0, len(data), batch_size):
                        batch = data[i:i+batch_size]
                        batch_values = []

                        for record in batch:
                            flattened = self.flatten_dict(record)
                            # Ensure all columns exist
                            for col in columns.keys():
                                if col not in flattened:
                                    flattened[col] = None

                            # Prepare values
                            cols = list(flattened.keys())
                            values = []
                            for col in cols:
                                val = flattened.get(col)
                                if isinstance(val, (dict, list)):
                                    values.append(json.dumps(val))
                                else:
                                    values.append(val)

                            # Build column names (sanitized)
                            safe_cols = [col.replace(' ', '_').replace('-', '_') for col in cols]
                            placeholders = ', '.join(['%s'] * len(values))
                            col_names = ', '.join([f'`{c}`' for c in safe_cols])

                            batch_values.append(tuple(values))

                        # Bulk insert
                        if batch_values:
                            try:
                                safe_cols = [col.replace(' ', '_').replace('-', '_') for col in cols]
                                col_names = ', '.join([f'`{c}`' for c in safe_cols])
                                placeholders = ', '.join(['%s'] * len(safe_cols))

                                insert_sql = f'INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})'
                                cursor.executemany(insert_sql, batch_values)
                                inserted += len(batch_values)

                                if (i // batch_size) % 10 == 0:
                                    self.conn.commit()
                                    print(f"   Progress: {inserted}/{len(data)} records...")
                            except Exception as e:
                                print(f"   ⚠️  Batch insert error: {e}")
                                # Try individual inserts for this batch
                                for record in batch:
                                    try:
                                        flattened = self.flatten_dict(record)
                                        cols = list(flattened.keys())
                                        values = [flattened.get(col) for col in cols]
                                        for j, val in enumerate(values):
                                            if isinstance(val, (dict, list)):
                                                values[j] = json.dumps(val)

                                        safe_cols = [col.replace(' ', '_').replace('-', '_') for col in cols]
                                        col_names = ', '.join([f'`{c}`' for c in safe_cols])
                                        placeholders = ', '.join(['%s'] * len(values))

                                        cursor.execute(
                                            f'INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})',
                                            values
                                        )
                                        inserted += 1
                                    except Exception as e2:
                                        print(f"   ⚠️  Skipped record: {e2}")

                    self.conn.commit()
                    print(f"   ✅ Inserted {inserted} records into table `{table_name}`")

                    # Create indexes on timestamp fields
                    try:
                        cursor.execute(f'SHOW COLUMNS FROM `{table_name}`')
                        columns_info = cursor.fetchall()
                        for col_info in columns_info:
                            col_name = col_info['Field'].lower()
                            if any(keyword in col_name for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
                                try:
                                    idx_name = f'idx_{table_name}_{col_info["Field"]}'
                                    cursor.execute(f'CREATE INDEX `{idx_name}` ON `{table_name}`(`{col_info["Field"]}`)')
                                except:
                                    pass
                    except:
                        pass

                    # Add metadata
                    try:
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS `holocron_metadata` (
                                `id` INT AUTO_INCREMENT PRIMARY KEY,
                                `table_name` VARCHAR(255),
                                `source_file` TEXT,
                                `converted_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
                                `record_count` BIGINT,
                                `file_size_mb` DOUBLE,
                                INDEX `idx_table_name` (`table_name`)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                        ''')

                        record_count = cursor.execute(f'SELECT COUNT(*) as cnt FROM `{table_name}`')
                        result = cursor.fetchone()
                        record_count = result['cnt'] if result else 0
                        file_size_mb = json_path.stat().st_size / (1024 * 1024)

                        cursor.execute('''
                            INSERT INTO `holocron_metadata`
                            (table_name, source_file, converted_at, record_count, file_size_mb)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                source_file = VALUES(source_file),
                                converted_at = VALUES(converted_at),
                                record_count = VALUES(record_count),
                                file_size_mb = VALUES(file_size_mb)
                        ''', (table_name, str(json_path), datetime.now(), record_count, file_size_mb))
                        self.conn.commit()
                    except Exception as e:
                        print(f"   ⚠️  Could not save metadata: {e}")

                    return True
                else:
                    # List of primitives
                    cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS `{table_name}` (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            value TEXT,
                            imported_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    ''')
                    for item in data:
                        cursor.execute(f'INSERT INTO `{table_name}` (value) VALUES (%s)', (json.dumps(item),))
                    self.conn.commit()
                    print(f"   ✅ Inserted {len(data)} primitive values")
                    return True

            elif isinstance(data, dict):
                # Single dictionary
                print("   📊 Processing single dictionary...")
                flattened = self.flatten_dict(data)
                columns = {k: self.infer_mysql_type(v, k) for k, v in flattened.items()}

                col_defs = ['`id` INT AUTO_INCREMENT PRIMARY KEY']
                col_defs.append('`imported_at` DATETIME DEFAULT CURRENT_TIMESTAMP')
                for col, dtype in columns.items():
                    safe_col = col.replace(' ', '_').replace('-', '_')
                    if dtype == 'JSON':
                        col_defs.append(f'`{safe_col}` JSON')
                    elif dtype == 'TEXT':
                        col_defs.append(f'`{safe_col}` TEXT')
                    else:
                        col_defs.append(f'`{safe_col}` {dtype}')

                schema = f'''
                CREATE TABLE IF NOT EXISTS `{table_name}` (
                    {', '.join(col_defs)}
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                '''
                cursor.execute(f'DROP TABLE IF EXISTS `{table_name}`')
                cursor.execute(schema)

                cols = list(flattened.keys())
                values = [flattened.get(col) for col in cols]
                for j, val in enumerate(values):
                    if isinstance(val, (dict, list)):
                        values[j] = json.dumps(val)

                safe_cols = [col.replace(' ', '_').replace('-', '_') for col in cols]
                col_names = ', '.join([f'`{c}`' for c in safe_cols])
                placeholders = ', '.join(['%s'] * len(values))

                cursor.execute(
                    f'INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})',
                    values
                )
                self.conn.commit()
                print("   ✅ Inserted dictionary")
                return True

        except Exception as e:
            print(f"   ❌ Error creating table: {e}")
            import traceback
            traceback.print_exc()
            return False


def get_credentials_from_vault(host: str = None) -> dict:
    """Get MariaDB credentials from Azure Vault or ProtonPass."""
    if not SECRETS_MANAGER_AVAILABLE:
        return {}

    project_root = Path(__file__).parent.parent.parent
    manager = UnifiedSecretsManager(project_root)

    # Try common secret name patterns
    secret_patterns = [
        # dbadmin (likely the configured user)
        "dbadmin-password",
        "dbadmin-username",
        "dbadmin-user",
        "mariadb-dbadmin-password",
        "mariadb-dbadmin-username",
        # MariaDB specific
        f"mariadb-{host.replace('.', '-')}-password" if host else None,
        f"mariadb-{host.replace('.', '-')}-username" if host else None,
        "mariadb-password",
        "mariadb-username",
        "mariadb-root-password",
        "nas-mariadb-password",
        "nas-mariadb-username",
        # Also try NAS password (might be same for MariaDB)
        f"nas-password-{host.replace('.', '-')}" if host else None,
        "nas-password",
    ]

    credentials = {}

    # Try Azure Vault first
    try:
        for pattern in [p for p in secret_patterns if p and 'password' in p]:
            password = manager.get_secret(pattern, source=SecretSource.AZURE_KEY_VAULT)
            if password:
                credentials['password'] = password
                break

        for pattern in [p for p in secret_patterns if p and 'username' in p]:
            username = manager.get_secret(pattern, source=SecretSource.AZURE_KEY_VAULT)
            if username:
                credentials['username'] = username
                break

        if credentials:
            return credentials
    except:
        pass

    # Fallback to ProtonPass
    try:
        for pattern in [p for p in secret_patterns if p and 'password' in p]:
            password = manager.get_secret(pattern, source=SecretSource.PROTONPASS)
            if password:
                credentials['password'] = password
                break

        for pattern in [p for p in secret_patterns if p and 'username' in p]:
            username = manager.get_secret(pattern, source=SecretSource.PROTONPASS)
            if username:
                credentials['username'] = username
                break
    except:
        pass

    return credentials

def main():
    parser = argparse.ArgumentParser(
        description="Convert large JSON files to MariaDB tables"
    )
    parser.add_argument(
        'json_file',
        type=str,
        help='Path to JSON file to convert'
    )
    parser.add_argument(
        '--host',
        type=str,
        help='MariaDB host (default: from NAS config or localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=3306,
        help='MariaDB port (default: 3306)'
    )
    parser.add_argument(
        '--user',
        type=str,
        help='MariaDB username (will check Azure Vault/ProtonPass if not provided)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='MariaDB password (will check Azure Vault/ProtonPass if not provided)'
    )
    parser.add_argument(
        '--database',
        type=str,
        required=True,
        help='MariaDB database name'
    )
    parser.add_argument(
        '--table',
        type=str,
        help='Table name (default: derived from filename)'
    )
    parser.add_argument(
        '--no-vault',
        action='store_true',
        help='Skip Azure Vault/ProtonPass credential lookup'
    )

    args = parser.parse_args()

    # Get NAS config for defaults
    nas_config = get_nas_config()
    if not args.host and nas_config.get('host'):
        args.host = nas_config['host']
        print(f"💡 Using NAS host from config: {args.host}")

    if not args.host:
        args.host = 'localhost'

    # Try to get credentials from vault first
    vault_creds = {}
    if not args.no_vault and SECRETS_MANAGER_AVAILABLE:
        print("🔍 Checking Azure Vault / ProtonPass for credentials...")
        vault_creds = get_credentials_from_vault(args.host)
        if vault_creds:
            print("   ✅ Credentials found in vault!")

    # Use provided args, vault, or env
    user = args.user or vault_creds.get('username') or nas_config.get('username')
    password = args.password or vault_creds.get('password') or os.environ.get('MARIADB_PASSWORD')

    if not user:
        print("❌ Username required. Use --user or ensure credentials are in Azure Vault/ProtonPass")
        print("   Expected secret names: mariadb-username, mariadb-password, or mariadb-{host}-username/password")
        sys.exit(1)

    if not password:
        print("❌ Password required. Use --password, set MARIADB_PASSWORD, or ensure credentials are in Azure Vault/ProtonPass")
        print("   Expected secret names: mariadb-password, mariadb-root-password, or mariadb-{host}-password")
        sys.exit(1)

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        sys.exit(1)

    converter = MariaDBConverter(
        host=args.host,
        user=args.user,
        password=password,
        database=args.database,
        port=args.port
    )

    try:
        success = converter.convert_json_to_mariadb(json_path, args.table)
        if success:
            print(f"\n✅ Conversion complete! Table: {args.table or json_path.stem}")
        else:
            print("\n❌ Conversion failed")
            sys.exit(1)
    finally:
        converter.close()


if __name__ == "__main__":
    import os
    if not PYMYSQL_AVAILABLE:
        print("❌ pymysql is required. Install with: pip install pymysql")
        sys.exit(1)


    main()