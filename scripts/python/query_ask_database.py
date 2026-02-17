"""
Query @ASK Database for Request ID
Searches enhanced_memory.db and ask_cache for the original @ASK.

#JARVIS #LUMINA #ASK
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging
logger = logging.getLogger("query_ask_database")


def query_enhanced_memory_db(request_id: str, project_root: Path) -> Optional[Dict[str, Any]]:
    """Query enhanced_memory.db for the request ID."""
    db_path = project_root / "data" / "memory" / "enhanced_memory.db"

    if not db_path.exists():
        print(f"⚠ Database not found: {db_path}")
        return None

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Try different table/column combinations
        tables_to_check = [
            ("asks", "ask_id"),
            ("asks", "request_id"),
            ("asks", "id"),
            ("ask_requests", "request_id"),
            ("ask_requests", "id"),
            ("requests", "request_id"),
            ("requests", "id"),
        ]

        for table, column in tables_to_check:
            try:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    # Table exists, try to query
                    query = f"SELECT * FROM {table} WHERE {column} LIKE ?"
                    cursor.execute(query, (f"%{request_id}%",))
                    row = cursor.fetchone()
                    if row:
                        result = dict(row)
                        conn.close()
                        return result
            except Exception as e:
                continue

        # Try searching all text columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                for row in rows:
                    row_dict = dict(row)
                    # Check if request_id appears anywhere in the row
                    row_str = json.dumps(row_dict, default=str).lower()
                    if request_id.lower() in row_str:
                        conn.close()
                        return row_dict
            except:
                continue

        conn.close()
        return None

    except Exception as e:
        print(f"Error querying database: {e}")
        return None

def main():
    try:
        """Main function."""
        project_root = Path(__file__).parent.parent.parent
        request_id = "c1fa7198-7bf3-46ae-8865-2a67f0085988"

        print("="*80)
        print("QUERYING @ASK DATABASE FOR ORIGINAL REQUEST")
        print("="*80)
        print(f"\nRequest ID: {request_id}")
        print("\nSearching enhanced_memory.db...")

        result = query_enhanced_memory_db(request_id, project_root)

        if result:
            print("\n✓ Found @ASK in database!")
            print("\n@ASK Details:")
            print(json.dumps(result, indent=2, default=str))

            # Save to HVAC bids directory
            output_file = project_root / "data" / "hvac_bids" / f"original_ask_{request_id}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n✓ Saved to: {output_file}")
        else:
            print("\n⚠ @ASK not found in enhanced_memory.db")
            print("\nThe original @ASK request may:")
            print("  1. Be stored with a different ID format")
            print("  2. Be in ask_cache/discovered_asks.json (very large file)")
            print("  3. Need to be retrieved from Gmail using the Request ID")
            print("\nTo find the email in Gmail, search for:")
            print(f"  {request_id} has:attachment")
            print("\nOr search for the subject:")
            print("  'HVAC Company Bids for Furnace/AC replacement'")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()