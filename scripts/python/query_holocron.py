#!/usr/bin/env python3
"""
HOLOCRON QUERY INTERFACE
Query SQLite Holocrons using SQL or natural language patterns
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import argparse
import logging
logger = logging.getLogger("query_holocron")


try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

class HolocronQuery:
    """Query interface for Holocrons."""

    def __init__(self, holocron_path: Path):
        self.holocron_path = holocron_path
        self.conn = sqlite3.connect(str(holocron_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

    def list_tables(self) -> List[str]:
        try:
            """List all tables in the holocron."""
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Error in list_tables: {e}", exc_info=True)
            raise
    def get_table_info(self, table_name: str) -> Dict:
        try:
            """Get information about a table."""
            cursor = self.conn.cursor()
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()

            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = cursor.fetchone()[0]

            return {
                'table_name': table_name,
                'columns': [{'name': col[1], 'type': col[2]} for col in columns],
                'row_count': row_count
            }

        except Exception as e:
            self.logger.error(f"Error in get_table_info: {e}", exc_info=True)
            raise
    def execute_query(self, query: str, limit: int = 100) -> List[Dict]:
        """Execute a SQL query and return results."""
        # Add LIMIT if not present
        query_upper = query.upper().strip()
        if 'LIMIT' not in query_upper and 'SELECT' in query_upper:
            query = f"{query.rstrip(';')} LIMIT {limit}"

        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"SQL Error: {e}")

    def search(self, table_name: str, search_term: str, columns: Optional[List[str]] = None) -> List[Dict]:
        """Search across text columns in a table."""
        info = self.get_table_info(table_name)
        text_columns = [col['name'] for col in info['columns']
                       if col['type'].upper() in ('TEXT', 'VARCHAR', 'CHAR')]

        if columns:
            text_columns = [c for c in text_columns if c in columns]

        if not text_columns:
            return []

        # Build OR conditions for all text columns
        conditions = ' OR '.join([f'"{col}" LIKE ?' for col in text_columns])
        params = [f'%{search_term}%'] * len(text_columns)

        query = f'SELECT * FROM "{table_name}" WHERE {conditions}'
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows[:100]]  # Limit to 100 results
        except sqlite3.Error as e:
            raise Exception(f"SQL Error: {e}")

    def get_metadata(self) -> Dict:
        """Get holocron metadata."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM holocron_metadata')
            row = cursor.fetchone()
            if row:
                return dict(row)
        except:
            pass
        return {}

    def close(self):
        """Close the connection."""
        self.conn.close()


def format_output(results: List[Dict], format_type: str = 'table') -> str:
    try:
        """Format query results for display."""
        if not results:
            return "No results found."

        if format_type == 'json':
            return json.dumps(results, indent=2, default=str)
        elif format_type == 'csv':
            if not results:
                return ""
            headers = list(results[0].keys())
            lines = [','.join(headers)]
            for row in results:
                lines.append(','.join([str(row.get(h, '')) for h in headers]))
            return '\n'.join(lines)
        else:  # table
            if not results:
                return "No results found."
            headers = list(results[0].keys())
            rows = [[str(row.get(h, ''))[:100] for h in headers] for row in results]  # Truncate long values

            if TABULATE_AVAILABLE:
                return tabulate(rows, headers=headers, tablefmt='grid', maxcolwidths=50)
            else:
                # Fallback to simple table format
                col_widths = [max(len(str(h)), max(len(str(r[i])) for r in rows) if rows else 0) for i, h in enumerate(headers)]
                col_widths = [min(w, 50) for w in col_widths]  # Cap at 50

                # Header
                header_row = ' | '.join([str(h).ljust(col_widths[i])[:col_widths[i]] for i, h in enumerate(headers)])
                separator = '-' * len(header_row)

                # Data rows
                data_rows = []
                for row in rows:
                    data_rows.append(' | '.join([str(cell).ljust(col_widths[i])[:col_widths[i]] for i, cell in enumerate(row)]))

                return '\n'.join([header_row, separator] + data_rows)


    except Exception as e:
        logger.error(f"Error in format_output: {e}", exc_info=True)
        raise
def main():
    parser = argparse.ArgumentParser(
        description="Query SQLite Holocrons"
    )
    parser.add_argument(
        'holocron',
        type=str,
        help='Path to holocron database file'
    )
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='SQL query to execute'
    )
    parser.add_argument(
        '--search', '-s',
        type=str,
        help='Search term to find in text columns'
    )
    parser.add_argument(
        '--table', '-t',
        type=str,
        help='Table name (required for search)'
    )
    parser.add_argument(
        '--list-tables',
        action='store_true',
        help='List all tables in the holocron'
    )
    parser.add_argument(
        '--info',
        type=str,
        help='Get info about a specific table'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['table', 'json', 'csv'],
        default='table',
        help='Output format'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=100,
        help='Limit number of results'
    )

    args = parser.parse_args()

    holocron_path = Path(args.holocron)
    if not holocron_path.exists():
        print(f"❌ Holocron not found: {holocron_path}")
        return

    query_interface = HolocronQuery(holocron_path)

    try:
        if args.list_tables:
            tables = query_interface.list_tables()
            print(f"\n📚 Tables in holocron ({len(tables)}):")
            for table in tables:
                info = query_interface.get_table_info(table)
                print(f"  • {table} ({info['row_count']} rows, {len(info['columns'])} columns)")

        elif args.info:
            info = query_interface.get_table_info(args.info)
            print(f"\n📊 Table: {info['table_name']}")
            print(f"   Rows: {info['row_count']}")
            print(f"   Columns:")
            for col in info['columns']:
                print(f"     • {col['name']} ({col['type']})")

        elif args.query:
            results = query_interface.execute_query(args.query, limit=args.limit)
            print(f"\n📊 Query Results ({len(results)} rows):")
            print(format_output(results, args.format))

        elif args.search:
            if not args.table:
                print("❌ --table required for search")
                return
            results = query_interface.search(args.table, args.search)
            print(f"\n🔍 Search Results for '{args.search}' ({len(results)} rows):")
            print(format_output(results, args.format))

        else:
            # Interactive mode
            metadata = query_interface.get_metadata()
            if metadata:
                print(f"\n📦 Holocron: {holocron_path.name}")
                print(f"   Source: {metadata.get('source_file', 'Unknown')}")
                print(f"   Records: {metadata.get('record_count', 'Unknown')}")
                print(f"   Converted: {metadata.get('converted_at', 'Unknown')}")

            tables = query_interface.list_tables()
            print(f"\n📚 Available tables: {', '.join(tables)}")
            print("\n💡 Usage examples:")
            print("  --list-tables              List all tables")
            print("  --info <table>             Get table info")
            print("  --query 'SELECT * FROM ...' Execute SQL query")
            print("  --search <term> --table <table>  Search in table")

    finally:
        query_interface.close()


if __name__ == "__main__":


    main()