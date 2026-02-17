#!/usr/bin/env python3
"""
Jedi Archives Card Catalog Viewer
Quickly find and view artifacts by Dewey Decimal classification.

Tags: #LIBRARIAN #CATALOG #DEWEY @JOCOSTA-NU
"""

import sys
import json
from pathlib import Path
import argparse
import logging
logger = logging.getLogger("view_card_catalog")


def view_catalog(dewey_filter=None):
    try:
        project_root = Path(__file__).parent.parent.parent
        index_file = project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"

        if not index_file.exists():
            print("❌ Card Catalog not found.")
            return

        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)

        entries = index.get("entries", {})

        print("\n🏛️  JEDI TEMPLE LIBRARY: CARD CATALOG")
        print("=" * 60)

        found = False
        for entry_id, data in entries.items():
            dewey = data.get("classification", "Unknown")
            if dewey_filter and dewey_filter not in dewey:
                continue

            found = True
            print(f"[{dewey}] {data.get('title')}")
            print(f"   ID: {entry_id}")
            print(f"   Location: {data.get('location')}")
            print("-" * 60)

        if not found:
            print(f"No artifacts found matching: {dewey_filter}")

    except Exception as e:
        logger.error(f"Error in view_catalog: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View Jedi Archives Catalog")
    parser.add_argument("--dewey", type=str, help="Filter by Dewey Decimal code (e.g., 600)")
    args = parser.parse_args()

    view_catalog(args.dewey)
