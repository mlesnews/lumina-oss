#!/usr/bin/env python3
"""
Enable MCP_DOCKER in Cursor's state database.

WARNING: Modifying Cursor's internal database while Cursor is running may not take effect
until Cursor is restarted, and there's a risk Cursor overwrites the change.

Tags: #mcp #cursor-state @JARVIS
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
        return False

    print(f"Target database: {db_path}")

    try:
        # Connect with write access
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        # First, read current state
        cur.execute("SELECT value FROM ItemTable WHERE key = 'anysphere.cursor-mcp'")
        row = cur.fetchone()

        current_value = row[0] if row else "{}"
        print(f"Current anysphere.cursor-mcp: {current_value}")

        try:
            current_data = json.loads(current_value) if current_value else {}
        except json.JSONDecodeError:
            current_data = {}

        # Get the MCP_DOCKER server ID from known servers
        cur.execute("SELECT value FROM ItemTable WHERE key = 'mcpService.knownServerIds'")
        known_row = cur.fetchone()

        if known_row:
            known_ids = json.loads(known_row[0])
            print(f"Known server IDs: {known_ids}")

            # Find the MCP_DOCKER one
            mcp_docker_id = None
            for sid in known_ids:
                if "MCP_DOCKER" in sid:
                    mcp_docker_id = sid
                    break

            if mcp_docker_id:
                print(f"Found MCP_DOCKER ID: {mcp_docker_id}")

                # Try different approaches to enable it
                # Approach 1: Add to the mcp settings with enabled: true
                new_data = current_data.copy()
                new_data[mcp_docker_id] = {"enabled": True}

                new_value = json.dumps(new_data)
                print(f"New value to set: {new_value}")

                # Update or insert
                cur.execute(
                    "UPDATE ItemTable SET value = ? WHERE key = 'anysphere.cursor-mcp'",
                    (new_value,),
                )

                if cur.rowcount == 0:
                    # Row doesn't exist, insert it
                    cur.execute(
                        "INSERT INTO ItemTable (key, value) VALUES ('anysphere.cursor-mcp', ?)",
                        (new_value,),
                    )

                conn.commit()
                print("✓ Updated anysphere.cursor-mcp")

                # Verify
                cur.execute("SELECT value FROM ItemTable WHERE key = 'anysphere.cursor-mcp'")
                verify_row = cur.fetchone()
                print(f"Verified value: {verify_row[0] if verify_row else 'NOT FOUND'}")

            else:
                print("MCP_DOCKER not found in known server IDs")
        else:
            print("No known server IDs found")

        conn.close()
        print("\n⚠️  Restart Cursor for changes to take effect.")
        return True

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        print("Cursor may have the database locked. Try closing Cursor first.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    main()
