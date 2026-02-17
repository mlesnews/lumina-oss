#!/usr/bin/env python3
"""
Find where Cursor stores MCP server disabled state.
"""

import json
import os
import sqlite3
from pathlib import Path


def main():
    db_path = (
        Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "globalStorage" / "state.vscdb"
    )

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()

    # Search for any key containing our MCP server name
    search_terms = ["MCP_DOCKER", "disabled", "enabled", "toggle", "server"]

    for term in search_terms:
        print(f"\n=== Searching for '{term}' ===")
        cur.execute(
            "SELECT key, value FROM ItemTable WHERE key LIKE ? OR value LIKE ? LIMIT 10",
            (f"%{term}%", f"%{term}%"),
        )
        rows = cur.fetchall()
        for key, value in rows:
            val_preview = ""
            if value:
                try:
                    parsed = json.loads(value)
                    val_preview = json.dumps(parsed)[:200]
                except:
                    val_preview = str(value)[:200]
            print(f"  {key}: {val_preview}")

    # Also check cursorDiskKV
    print("\n=== cursorDiskKV all entries ===")
    cur.execute("SELECT key FROM cursorDiskKV LIMIT 50")
    for row in cur.fetchall():
        print(f"  {row[0]}")

    conn.close()


if __name__ == "__main__":
    main()
