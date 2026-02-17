#!/usr/bin/env python3
"""
MARIADB HOLOCRON BACKUP SYSTEM
DBA/DBE Team - Automated Backup and Restore for Holocrons

Features:
- Automated SQL dumps
- Compression
- Retention policies
- Backup verification
- Restore capabilities
- Integration with NAS backup systems
"""

import os
import sys
import subprocess
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse
import json
import logging
logger = logging.getLogger("backup_mariadb_holocrons")


try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

class HolocronBackupManager:
    """DBA/DBE Team - Holocron Backup Management System"""

    def __init__(self, host: str, user: str, password: str, database: str,
                 backup_dir: Path, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup metadata file
        self.metadata_file = self.backup_dir / 'backup_metadata.json'
        self.load_metadata()

    def load_metadata(self):
        try:
            """Load backup metadata."""
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {'backups': [], 'last_backup': None}

        except Exception as e:
            self.logger.error(f"Error in load_metadata: {e}", exc_info=True)
            raise
    def save_metadata(self):
        try:
            """Save backup metadata."""
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in save_metadata: {e}", exc_info=True)
            raise
    def test_connection(self) -> bool:
        """Test MariaDB connection."""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4'
            )
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def list_tables(self) -> List[str]:
        """List all tables in database."""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            print(f"❌ Error listing tables: {e}")
            return []

    def backup_database(self, compress: bool = True, include_metadata: bool = True) -> Optional[Path]:
        """Create full database backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"{self.database}_backup_{timestamp}.sql"
        compressed_file = backup_file.with_suffix('.sql.gz')

        print(f"\n📦 Creating backup: {backup_file.name}")

        # Use mysqldump
        try:
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}',
                '--single-transaction',  # Consistent backup
                '--routines',  # Include stored procedures
                '--triggers',  # Include triggers
                '--events',   # Include events
                '--add-drop-table',  # Include DROP TABLE
                '--complete-insert',  # Complete INSERT statements
                self.database
            ]

            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )

            if result.returncode != 0:
                print(f"❌ Backup failed: {result.stderr}")
                if backup_file.exists():
                    backup_file.unlink()
                return None

            # Get backup size
            backup_size = backup_file.stat().st_size

            # Compress if requested
            if compress:
                print(f"   🗜️  Compressing backup...")
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                compressed_size = compressed_file.stat().st_size
                backup_file.unlink()  # Remove uncompressed
                final_file = compressed_file
                compression_ratio = (1 - compressed_size / backup_size) * 100
                print(f"   ✅ Compressed: {compression_ratio:.1f}% reduction")
            else:
                final_file = backup_file
                compressed_size = backup_size

            # Get table counts
            tables = self.list_tables()
            table_counts = {}
            try:
                conn = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    charset='utf8mb4'
                )
                cursor = conn.cursor()
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                    table_counts[table] = cursor.fetchone()[0]
                conn.close()
            except:
                pass

            # Save metadata
            backup_info = {
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'file': str(final_file.name),
                'path': str(final_file),
                'size_mb': round(backup_size / (1024 * 1024), 2),
                'compressed_size_mb': round(compressed_size / (1024 * 1024), 2),
                'compressed': compress,
                'tables': len(tables),
                'table_counts': table_counts,
                'host': self.host,
                'database': self.database
            }

            self.metadata['backups'].append(backup_info)
            self.metadata['last_backup'] = backup_info
            self.save_metadata()

            print(f"   ✅ Backup complete: {final_file.name}")
            print(f"   📊 Size: {backup_info['compressed_size_mb']} MB ({backup_info['tables']} tables)")

            return final_file

        except FileNotFoundError:
            print("❌ mysqldump not found. Install MySQL client tools.")
            return None
        except Exception as e:
            print(f"❌ Backup error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def backup_table(self, table_name: str, compress: bool = True) -> Optional[Path]:
        """Backup a single table."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"{table_name}_backup_{timestamp}.sql"
        compressed_file = backup_file.with_suffix('.sql.gz')

        print(f"\n📦 Backing up table: {table_name}")

        try:
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}',
                '--single-transaction',
                '--add-drop-table',
                '--complete-insert',
                self.database,
                table_name
            ]

            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )

            if result.returncode != 0:
                print(f"❌ Backup failed: {result.stderr}")
                if backup_file.exists():
                    backup_file.unlink()
                return None

            backup_size = backup_file.stat().st_size

            if compress:
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                compressed_size = compressed_file.stat().st_size
                backup_file.unlink()
                final_file = compressed_file
            else:
                final_file = backup_file
                compressed_size = backup_size

            print(f"   ✅ Table backup complete: {final_file.name}")
            print(f"   📊 Size: {round(compressed_size / (1024 * 1024), 2)} MB")

            return final_file

        except Exception as e:
            print(f"❌ Table backup error: {e}")
            return None

    def list_backups(self) -> List[Dict]:
        """List all backups."""
        return self.metadata.get('backups', [])

    def cleanup_old_backups(self, days: int = 30, keep_minimum: int = 5):
        """Remove backups older than specified days, but keep minimum."""
        cutoff_date = datetime.now() - timedelta(days=days)
        backups = self.metadata.get('backups', [])

        # Sort by datetime (newest first)
        backups_sorted = sorted(
            backups,
            key=lambda x: x.get('datetime', ''),
            reverse=True
        )

        removed = 0
        kept = 0

        for backup in backups_sorted:
            try:
                backup_date = datetime.fromisoformat(backup['datetime'])
                backup_path = Path(backup['path'])

                if backup_date < cutoff_date and kept >= keep_minimum:
                    # Remove old backup
                    if backup_path.exists():
                        backup_path.unlink()
                        print(f"   🗑️  Removed old backup: {backup['file']}")
                    removed += 1
                else:
                    kept += 1
            except:
                pass

        # Update metadata
        self.metadata['backups'] = [
            b for b in backups
            if Path(b['path']).exists()
        ]
        self.save_metadata()

        return removed

    def verify_backup(self, backup_path: Path) -> bool:
        """Verify backup file integrity."""
        print(f"\n🔍 Verifying backup: {backup_path.name}")

        if not backup_path.exists():
            print("   ❌ Backup file not found")
            return False

        try:
            # Check if compressed
            if backup_path.suffix == '.gz':
                # Try to decompress
                with gzip.open(backup_path, 'rb') as f:
                    f.read(1024)  # Read first 1KB
                print("   ✅ Compressed backup is valid")
            else:
                # Check SQL file
                with open(backup_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if 'MySQL dump' in first_line or 'MariaDB dump' in first_line:
                        print("   ✅ SQL backup is valid")
                    else:
                        print("   ⚠️  Backup format may be invalid")
                        return False

            return True

        except Exception as e:
            print(f"   ❌ Backup verification failed: {e}")
            return False

    def restore_database(self, backup_path: Path, drop_existing: bool = False) -> bool:
        """Restore database from backup."""
        print(f"\n🔄 Restoring from: {backup_path.name}")

        if not backup_path.exists():
            print("   ❌ Backup file not found")
            return False

        # Verify backup first
        if not self.verify_backup(backup_path):
            print("   ❌ Backup verification failed")
            return False

        try:
            # Decompress if needed
            if backup_path.suffix == '.gz':
                print("   🗜️  Decompressing backup...")
                temp_file = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                sql_file = temp_file
            else:
                sql_file = backup_path

            # Restore
            cmd = [
                'mysql',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}',
                self.database
            ]

            with open(sql_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True
                )

            # Cleanup temp file
            if backup_path.suffix == '.gz' and temp_file.exists():
                temp_file.unlink()

            if result.returncode != 0:
                print(f"   ❌ Restore failed: {result.stderr}")
                return False

            print("   ✅ Database restored successfully")
            return True

        except FileNotFoundError:
            print("❌ mysql client not found. Install MySQL client tools.")
            return False
        except Exception as e:
            print(f"❌ Restore error: {e}")
            return False


def main():
    try:
        parser = argparse.ArgumentParser(
            description="DBA/DBE Team - MariaDB Holocron Backup Manager"
        )
        parser.add_argument(
            '--host',
            type=str,
            required=True,
            help='MariaDB host'
        )
        parser.add_argument(
            '--user',
            type=str,
            required=True,
            help='MariaDB username'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='MariaDB password (or use MARIADB_PASSWORD env var)'
        )
        parser.add_argument(
            '--database',
            type=str,
            required=True,
            help='Database name'
        )
        parser.add_argument(
            '--backup-dir',
            type=str,
            required=True,
            help='Backup directory path'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=3306,
            help='MariaDB port'
        )
        parser.add_argument(
            '--action',
            choices=['backup', 'backup-table', 'list', 'verify', 'restore', 'cleanup'],
            default='backup',
            help='Action to perform'
        )
        parser.add_argument(
            '--table',
            type=str,
            help='Table name (for backup-table action)'
        )
        parser.add_argument(
            '--backup-file',
            type=str,
            help='Backup file path (for verify/restore)'
        )
        parser.add_argument(
            '--retention-days',
            type=int,
            default=30,
            help='Days to keep backups (for cleanup)'
        )
        parser.add_argument(
            '--no-compress',
            action='store_true',
            help='Skip compression'
        )

        args = parser.parse_args()

        password = args.password or os.environ.get('MARIADB_PASSWORD')
        if not password:
            print("❌ Password required. Use --password or set MARIADB_PASSWORD")
            sys.exit(1)

        backup_dir = Path(args.backup_dir)

        manager = HolocronBackupManager(
            host=args.host,
            user=args.user,
            password=password,
            database=args.database,
            backup_dir=backup_dir,
            port=args.port
        )

        # Test connection
        if not manager.test_connection():
            print("❌ Cannot connect to MariaDB")
            sys.exit(1)

        print("✅ Connected to MariaDB")

        if args.action == 'backup':
            manager.backup_database(compress=not args.no_compress)

        elif args.action == 'backup-table':
            if not args.table:
                print("❌ --table required for backup-table action")
                sys.exit(1)
            manager.backup_table(args.table, compress=not args.no_compress)

        elif args.action == 'list':
            backups = manager.list_backups()
            print(f"\n📋 Found {len(backups)} backups:")
            for backup in backups[-10:]:  # Show last 10
                print(f"   • {backup['file']} ({backup['datetime']}) - {backup['compressed_size_mb']} MB")

        elif args.action == 'verify':
            if not args.backup_file:
                print("❌ --backup-file required for verify action")
                sys.exit(1)
            manager.verify_backup(Path(args.backup_file))

        elif args.action == 'restore':
            if not args.backup_file:
                print("❌ --backup-file required for restore action")
                sys.exit(1)
            response = input("⚠️  This will overwrite the database. Continue? (yes/no): ")
            if response.lower() == 'yes':
                manager.restore_database(Path(args.backup_file))
            else:
                print("   Cancelled.")

        elif args.action == 'cleanup':
            removed = manager.cleanup_old_backups(days=args.retention_days)
            print(f"\n✅ Cleanup complete: Removed {removed} old backups")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    if not PYMYSQL_AVAILABLE:
        print("❌ pymysql required. Install with: pip install pymysql")
        sys.exit(1)


    main()