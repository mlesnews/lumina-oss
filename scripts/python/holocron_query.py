#!/usr/bin/env python3
"""
Holocron Query System
Enables high-speed searching and retrieval across chunked @holocron files.
Solves the "TOO LARGE" error by leveraging the Holocron index.

Tags: #HOLOCRON #QUERY #SEARCH #LARGE_FILES @AUTO @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HolocronQuery")


class HolocronQuerySystem:
    """
    Search and retrieve data from chunked Holocron files.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.intelligence_dir = self.project_root / "data" / "intelligence"
        self.chunks_dir = self.project_root / "data" / "holocron" / "chunks"

    def list_indexes(self) -> List[str]:
        """List available Holocron indexes"""
        return [f.name for f in self.intelligence_dir.glob("*_INDEX.json")]

    def get_index(self, index_name: str) -> Optional[Dict[str, Any]]:
        try:
            """Load a specific index"""
            index_path = self.intelligence_dir / index_name
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None

        except Exception as e:
            self.logger.error(f"Error in get_index: {e}", exc_info=True)
            raise
    def search_asks(self, query: str, index_name: str = "LUMINA_ALL_ASKS_ORDERED_INDEX.json") -> List[Dict[str, Any]]:
        """Search for @asks containing the query string across all chunks"""
        index = self.get_index(index_name)
        if not index:
            self.logger.error(f"❌ Index not found: {index_name}")
            return []

        results = []
        query_lower = query.lower()

        self.logger.info(f"🔍 Searching for '{query}' across {len(index['chunks'])} chunks...")

        for chunk_info in index["chunks"]:
            chunk_path = self.project_root / chunk_info["path"]
            if chunk_path.exists():
                try:
                    with open(chunk_path, 'r', encoding='utf-8') as f:
                        chunk_data = json.load(f)

                    # Search in 'asks' key
                    asks = chunk_data.get("asks", [])
                    for ask in asks:
                        if query_lower in ask.get("ask_text", "").lower() or query_lower in ask.get("context", "").lower():
                            ask["chunk_source"] = chunk_info["name"]
                            results.append(ask)
                except Exception as e:
                    self.logger.error(f"❌ Error reading chunk {chunk_info['name']}: {e}")

        self.logger.info(f"✅ Found {len(results)} matches")
        return results

    def get_chunk_by_index(self, index_name: str, chunk_idx: int) -> Optional[Dict[str, Any]]:
        try:
            """Retrieve a specific chunk by its index (1-based)"""
            index = self.get_index(index_name)
            if not index or chunk_idx < 1 or chunk_idx > len(index["chunks"]):
                return None

            chunk_info = index["chunks"][chunk_idx - 1]
            chunk_path = self.project_root / chunk_info["path"]

            if chunk_path.exists():
                with open(chunk_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None


        except Exception as e:
            self.logger.error(f"Error in get_chunk_by_index: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Holocron Query System")
        parser.add_argument("--list", action="store_true", help="List available indexes")
        parser.add_argument("--search", type=str, help="Search term for @asks")
        parser.add_argument("--index", type=str, default="LUMINA_ALL_ASKS_ORDERED_INDEX.json", help="Index file to search")
        parser.add_argument("--get-chunk", type=int, help="Get specific chunk number")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()
        query_system = HolocronQuerySystem()

        if args.list:
            indexes = query_system.list_indexes()
            for idx in indexes:
                print(f"- {idx}")
        elif args.search:
            results = query_system.search_asks(args.search, args.index)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                for i, r in enumerate(results, 1):
                    print(f"\n{i}. [{r.get('timestamp')}] {r.get('ask_text')}")
                    print(f"   Source: {r.get('chunk_source')}")
        elif args.get_chunk:
            chunk = query_system.get_chunk_by_index(args.index, args.get_chunk)
            if chunk:
                print(json.dumps(chunk, indent=2))
            else:
                print(f"Chunk {args.get_chunk} not found in {args.index}")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()