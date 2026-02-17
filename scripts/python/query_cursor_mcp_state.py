#!/usr/bin/env python3
"""
Query Cursor's MCP enabled/disabled state from its internal database.

This reads Cursor's state.vscdb to find MCP server toggle states.

Tags: #transparency #mcp #cursor-state @JARVIS
"""

import json
import os
import sqlite3
from pathlib import Path


def get_cursor_state_db() -> Path:
    """Get path to Cursor's state database."""
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "Cursor" / "User" / "globalStorage" / "state.vscdb"


def query_mcp_state():
    """Query MCP-related state from Cursor's database."""
    db_path = get_cursor_state_db()

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return None

    print(f"Reading: {db_path}")

    try:
        # Connect read-only to avoid locking issues with running Cursor
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = conn.cursor()

        # Get all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"Tables: {tables}")

        # The main table is usually 'ItemTable' which stores key-value pairs
        if "ItemTable" in tables:
            # Search for MCP-related keys
            cur.execute(
                "SELECT key, value FROM ItemTable WHERE key LIKE '%mcp%' OR key LIKE '%MCP%'"
            )
            mcp_rows = cur.fetchall()

            if mcp_rows:
                print(f"\nMCP-related entries ({len(mcp_rows)}):")
                for key, value in mcp_rows:
                    # Try to parse JSON values
                    try:
                        parsed = json.loads(value)
                        print(f"  {key}: {json.dumps(parsed, indent=4)}")
                    except (json.JSONDecodeError, TypeError):
                        # Show first 200 chars of raw value
                        val_preview = str(value)[:200] if value else "(empty)"
                        print(f"  {key}: {val_preview}")
            else:
                print("\nNo MCP-related entries found in ItemTable")

            # Also look for anything with "disabled" or "enabled" that might relate
            cur.execute(
                "SELECT key FROM ItemTable WHERE key LIKE '%disabled%' OR key LIKE '%enabled%' LIMIT 20"
            )
            state_keys = [r[0] for r in cur.fetchall()]
            if state_keys:
                print(f"\nEnabled/disabled related keys (sample): {state_keys[:10]}")

            # Look specifically for anysphere.cursor-mcp and cursor-mcp related
            cur.execute(
                "SELECT key, value FROM ItemTable WHERE key LIKE '%cursor-mcp%' OR key LIKE '%anysphere%'"
            )
            cursor_mcp_rows = cur.fetchall()
            if cursor_mcp_rows:
                print("\nCursor MCP specific entries:")
                for key, value in cursor_mcp_rows:
                    print(f"  {key}: {value[:500] if value else '(empty)'}")

            # Look for server disabled states
            cur.execute(
                "SELECT key, value FROM ItemTable WHERE key LIKE '%Server%' AND (key LIKE '%disabled%' OR key LIKE '%enabled%' OR key LIKE '%state%')"
            )
            server_state_rows = cur.fetchall()
            if server_state_rows:
                print("\nServer state entries:")
                for key, value in server_state_rows:
                    print(f"  {key}: {value[:300] if value else '(empty)'}")

            # Check cursorDiskKV table too
            cur.execute(
                "SELECT key, value FROM cursorDiskKV WHERE key LIKE '%mcp%' OR key LIKE '%MCP%'"
            )
            disk_kv_rows = cur.fetchall()
            if disk_kv_rows:
                print("\ncursorDiskKV MCP entries:")
                for key, value in disk_kv_rows:
                    val_str = value[:500] if isinstance(value, str) else str(value)[:500]
                    print(f"  {key}: {val_str}")

        conn.close()

    except sqlite3.OperationalError as e:
        print(f"Database error (Cursor may have it locked): {e}")
        print("Try closing Cursor and running again, or this is expected while Cursor is open.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    query_mcp_state()
