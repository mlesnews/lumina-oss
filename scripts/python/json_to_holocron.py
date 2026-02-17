#!/usr/bin/env python3
"""
JSON TO HOLOCRON CONVERTER
Converts large JSON files into queryable SQLite databases (Holocrons)

A Holocron is a structured knowledge repository that can be efficiently queried.
"""

import json
import sqlite3
import gzip
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import argparse
import sys
import logging
logger = logging.getLogger("json_to_holocron")


class HolocronConverter:
    """Converts JSON files into SQLite Holocrons for efficient querying."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / "data" / "holocrons"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect_json_structure(self, data: Any, path: str = "") -> Dict[str, Any]:
        """Analyze JSON structure to determine schema."""
        structure = {
            'type': type(data).__name__,
            'is_list': isinstance(data, list),
            'is_dict': isinstance(data, dict),
            'sample_keys': [],
            'sample_values': []
        }

        if isinstance(data, dict):
            structure['sample_keys'] = list(data.keys())[:10]
            if data:
                first_value = next(iter(data.values()))
                structure['nested_structure'] = self.detect_json_structure(first_value, f"{path}.{list(data.keys())[0]}")
        elif isinstance(data, list) and len(data) > 0:
            structure['item_count'] = len(data)
            if isinstance(data[0], dict):
                structure['sample_keys'] = list(data[0].keys())[:10]
                structure['nested_structure'] = self.detect_json_structure(data[0], f"{path}[0]")

        return structure

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
    def infer_sql_type(self, value: Any) -> str:
        """Infer SQLite type from Python value."""
        if value is None:
            return 'TEXT'
        if isinstance(value, bool):
            return 'INTEGER'  # SQLite uses INTEGER for booleans
        if isinstance(value, int):
            return 'INTEGER'
        if isinstance(value, float):
            return 'REAL'
        if isinstance(value, (list, dict)):
            return 'TEXT'  # Store as JSON string
        return 'TEXT'

    def create_table_schema(self, sample_data: List[Dict], table_name: str) -> str:
        """Create SQL table schema from sample data."""
        if not sample_data:
            return None

        # Flatten all records to get all possible columns
        all_keys = set()
        for record in sample_data[:100]:  # Sample first 100 records
            flattened = self.flatten_dict(record)
            all_keys.update(flattened.keys())

        # Determine types for each column
        columns = {}
        for key in sorted(all_keys):
            # Find first non-None value for this key
            for record in sample_data:
                flattened = self.flatten_dict(record)
                if key in flattened:
                    value = flattened[key]
                    if value is not None:
                        columns[key] = self.infer_sql_type(value)
                        break
            if key not in columns:
                columns[key] = 'TEXT'  # Default to TEXT

        # Build CREATE TABLE statement
        column_defs = [f'"{col}" {dtype}' for col, dtype in columns.items()]
        column_defs.insert(0, '"id" INTEGER PRIMARY KEY AUTOINCREMENT')
        column_defs.insert(1, '"imported_at" TEXT DEFAULT CURRENT_TIMESTAMP')

        schema = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {', '.join(column_defs)}
        );
        """

        return schema, columns

    def convert_json_to_holocron(self, json_path: Path, holocron_name: Optional[str] = None) -> Path:
        """Convert a JSON file to a SQLite Holocron."""
        print(f"\n📦 Converting {json_path.name} to Holocron...")

        # Determine holocron name
        if not holocron_name:
            holocron_name = json_path.stem.replace('.json', '')

        holocron_path = self.output_dir / f"{holocron_name}.holocron.db"

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
            return None

        # Analyze structure
        structure = self.detect_json_structure(data)
        print(f"   Structure: {structure['type']}, Is List: {structure['is_list']}")

        # Connect to SQLite
        conn = sqlite3.connect(str(holocron_path))
        conn.execute("PRAGMA journal_mode = WAL")  # Better performance
        conn.execute("PRAGMA synchronous = NORMAL")

        try:
            if isinstance(data, list):
                if len(data) == 0:
                    print("   ⚠️  Empty list, creating empty holocron")
                    conn.execute(f'CREATE TABLE IF NOT EXISTS "{holocron_name}" (id INTEGER PRIMARY KEY)')
                elif isinstance(data[0], dict):
                    # List of dictionaries - create table from first item
                    print(f"   📊 Processing {len(data)} records...")
                    schema, columns = self.create_table_schema(data, holocron_name)
                    conn.execute(schema)

                    # Insert data
                    cursor = conn.cursor()
                    inserted = 0
                    batch_size = 1000

                    for i in range(0, len(data), batch_size):
                        batch = data[i:i+batch_size]
                        for record in batch:
                            flattened = self.flatten_dict(record)
                            # Ensure all columns exist
                            for col in columns.keys():
                                if col not in flattened:
                                    flattened[col] = None

                            # Build INSERT statement
                            cols = list(flattened.keys())
                            placeholders = ', '.join(['?' for _ in cols])
                            values = [flattened.get(col) for col in cols]

                            # Convert complex types to JSON strings
                            for j, val in enumerate(values):
                                if isinstance(val, (dict, list)):
                                    values[j] = json.dumps(val)

                            try:
                                col_names = ', '.join([f'"{c}"' for c in cols])
                                cursor.execute(
                                    f'INSERT INTO "{holocron_name}" ({col_names}) VALUES ({placeholders})',
                                    values
                                )
                                inserted += 1
                            except sqlite3.OperationalError as e:
                                # Table might need to be altered for new columns
                                print(f"   ⚠️  Schema issue, attempting to add columns: {e}")
                                # Try to add missing columns
                                for col in cols:
                                    if col not in columns:
                                        try:
                                            conn.execute(f'ALTER TABLE "{holocron_name}" ADD COLUMN "{col}" TEXT')
                                        except:
                                            pass
                                # Retry insert
                                try:
                                    col_names = ', '.join([f'"{c}"' for c in cols])
                                    cursor.execute(
                                        f'INSERT INTO "{holocron_name}" ({col_names}) VALUES ({placeholders})',
                                        values
                                    )
                                    inserted += 1
                                except Exception as e2:
                                    print(f"   ⚠️  Skipped record due to: {e2}")

                        if (i // batch_size) % 10 == 0:
                            conn.commit()
                            print(f"   Progress: {inserted}/{len(data)} records...")

                    conn.commit()
                    print(f"   ✅ Inserted {inserted} records")

                else:
                    # List of primitives
                    conn.execute(f'''
                        CREATE TABLE IF NOT EXISTS "{holocron_name}" (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            value TEXT,
                            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    cursor = conn.cursor()
                    for item in data:
                        cursor.execute(f'INSERT INTO "{holocron_name}" (value) VALUES (?)', (json.dumps(item),))
                    conn.commit()
                    print(f"   ✅ Inserted {len(data)} primitive values")

            elif isinstance(data, dict):
                # Single dictionary - create table with one row
                print("   📊 Processing single dictionary...")
                flattened = self.flatten_dict(data)
                columns = {k: self.infer_sql_type(v) for k, v in flattened.items()}

                schema = f'''
                CREATE TABLE IF NOT EXISTS "{holocron_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {', '.join([f'"{col}" {dtype}' for col, dtype in columns.items()])},
                    imported_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                '''
                conn.execute(schema)

                cols = list(flattened.keys())
                values = [flattened.get(col) for col in cols]
                for j, val in enumerate(values):
                    if isinstance(val, (dict, list)):
                        values[j] = json.dumps(val)

                placeholders = ', '.join(['?' for _ in cols])
                col_names = ', '.join([f'"{c}"' for c in cols])
                conn.execute(
                    f'INSERT INTO "{holocron_name}" ({col_names}) VALUES ({placeholders})',
                    values
                )
                conn.commit()
                print("   ✅ Inserted dictionary")

            # Create indexes on common fields
            try:
                cursor = conn.cursor()
                cursor.execute(f'PRAGMA table_info("{holocron_name}")')
                columns_info = cursor.fetchall()

                # Index on timestamp-like fields
                for col_info in columns_info:
                    col_name = col_info[1].lower()
                    if any(keyword in col_name for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
                        try:
                            conn.execute(f'CREATE INDEX IF NOT EXISTS idx_{holocron_name}_{col_info[1]} ON "{holocron_name}"("{col_info[1]}")')
                        except:
                            pass
            except:
                pass

            # Add metadata table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS holocron_metadata (
                    holocron_name TEXT PRIMARY KEY,
                    source_file TEXT,
                    converted_at TEXT,
                    record_count INTEGER,
                    file_size_mb REAL
                )
            ''')

            record_count = conn.execute(f'SELECT COUNT(*) FROM "{holocron_name}"').fetchone()[0]
            file_size_mb = json_path.stat().st_size / (1024 * 1024)

            conn.execute('''
                INSERT OR REPLACE INTO holocron_metadata
                (holocron_name, source_file, converted_at, record_count, file_size_mb)
                VALUES (?, ?, ?, ?, ?)
            ''', (holocron_name, str(json_path), datetime.now().isoformat(), record_count, file_size_mb))
            conn.commit()

            holocron_size_mb = holocron_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Holocron created: {holocron_path.name}")
            print(f"   📊 Size: {file_size_mb:.2f} MB → {holocron_size_mb:.2f} MB ({record_count} records)")

            return holocron_path

        except Exception as e:
            print(f"   ❌ Error creating holocron: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            conn.close()


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Convert large JSON files to queryable SQLite Holocrons"
        )
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to JSON file to convert'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Name for the holocron (default: derived from filename)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Output directory for holocrons (default: data/holocrons)'
        )
        parser.add_argument(
            '--batch',
            action='store_true',
            help='Process all JSON files in directory'
        )

        args = parser.parse_args()

        converter = HolocronConverter(
            output_dir=Path(args.output_dir) if args.output_dir else None
        )

        if args.batch:
            json_path = Path(args.json_file)
            if json_path.is_dir():
                json_files = list(json_path.rglob("*.json")) + list(json_path.rglob("*.json.gz"))
            else:
                json_files = [json_path]

            print(f"🔄 Batch converting {len(json_files)} files...")
            for json_file in json_files:
                if json_file.stat().st_size > 10 * 1024 * 1024:  # Only convert files > 10MB
                    converter.convert_json_to_holocron(json_file)
        else:
            json_path = Path(args.json_file)
            if not json_path.exists():
                print(f"❌ File not found: {json_path}")
                sys.exit(1)

            converter.convert_json_to_holocron(json_path, args.name)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()