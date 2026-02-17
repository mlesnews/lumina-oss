#!/usr/bin/env python3
"""
JARVIS Enhanced Memory Query System

Provides optimized query capabilities for enhanced persistent memory
with cell-level access and long-term storage queries.

Features:
- Cell-based queries
- Full-text search
- Relationship queries
- Performance-optimized queries
- Long-term archival queries
"""

import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEnhancedMemoryQueries")


class EnhancedMemoryQueryEngine:
    """
    Enhanced Memory Query Engine

    Provides optimized querying capabilities for enhanced persistent memory.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Database path
        self.db_path = project_root / "data" / "jarvis_memory" / "enhanced_memory.db"

        if not self.db_path.exists():
            self.logger.warning("⚠️  Enhanced database not found - create schema first")

    def query_by_cell(self, cell_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query memories by cell"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM memories
                WHERE cell_id = ?
                ORDER BY last_accessed DESC, access_count DESC
                LIMIT ?
            ''', (cell_id, limit))

            rows = cursor.fetchall()
            memories = [dict(row) for row in rows]

            conn.close()

            return memories

        except Exception as e:
            self.logger.error(f"Query error: {e}", exc_info=True)
            return []

    def full_text_search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Full-text search across memories"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT m.* FROM memories m
                JOIN memory_index idx ON m.memory_id = idx.memory_id
                WHERE memory_index MATCH ?
                ORDER BY m.last_accessed DESC
                LIMIT ?
            ''', (query, limit))

            rows = cursor.fetchall()
            memories = [dict(row) for row in rows]

            conn.close()

            return memories

        except Exception as e:
            self.logger.error(f"Full-text search error: {e}", exc_info=True)
            return []

    def query_relationships(self, memory_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query memory relationships"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if relationship_type:
                cursor.execute('''
                    SELECT * FROM memory_relationships
                    WHERE (memory_id_1 = ? OR memory_id_2 = ?)
                    AND relationship_type = ?
                    ORDER BY strength DESC
                ''', (memory_id, memory_id, relationship_type))
            else:
                cursor.execute('''
                    SELECT * FROM memory_relationships
                    WHERE memory_id_1 = ? OR memory_id_2 = ?
                    ORDER BY strength DESC
                ''', (memory_id, memory_id))

            rows = cursor.fetchall()
            relationships = [dict(row) for row in rows]

            conn.close()

            return relationships

        except Exception as e:
            self.logger.error(f"Relationship query error: {e}", exc_info=True)
            return []

    def query_long_term_memories(self, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """Query long-term memories (not accessed recently)"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute('''
                SELECT * FROM memories
                WHERE last_accessed < ?
                AND archived = 0
                ORDER BY last_accessed ASC, access_count ASC
                LIMIT ?
            ''', (cutoff_date, limit))

            rows = cursor.fetchall()
            memories = [dict(row) for row in rows]

            conn.close()

            return memories

        except Exception as e:
            self.logger.error(f"Long-term query error: {e}", exc_info=True)
            return []

    def query_high_performance_memories(self, min_score: float = 0.7, limit: int = 100) -> List[Dict[str, Any]]:
        """Query high-performance memories (frequently accessed, fast queries)"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT m.*, s.performance_score FROM memories m
                JOIN memory_statistics s ON m.memory_id = s.memory_id
                WHERE s.performance_score >= ?
                ORDER BY s.performance_score DESC, m.access_count DESC
                LIMIT ?
            ''', (min_score, limit))

            rows = cursor.fetchall()
            memories = [dict(row) for row in rows]

            conn.close()

            return memories

        except Exception as e:
            self.logger.error(f"Performance query error: {e}", exc_info=True)
            return []

    def query_by_metadata(self, key: str, value: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query memories by metadata key-value"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT m.* FROM memories m
                JOIN memory_metadata md ON m.memory_id = md.memory_id
                WHERE md.key = ? AND md.value = ?
                ORDER BY m.last_accessed DESC
                LIMIT ?
            ''', (key, value, limit))

            rows = cursor.fetchall()
            memories = [dict(row) for row in rows]

            conn.close()

            return memories

        except Exception as e:
            self.logger.error(f"Metadata query error: {e}", exc_info=True)
            return []


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Enhanced Memory Query Engine")
        parser.add_argument("--cell", type=str, help="Query by cell ID")
        parser.add_argument("--search", type=str, help="Full-text search")
        parser.add_argument("--relationships", type=str, help="Query relationships for memory ID")
        parser.add_argument("--long-term", type=int, default=30, help="Query long-term memories (days)")
        parser.add_argument("--high-performance", action="store_true", help="Query high-performance memories")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        query_engine = EnhancedMemoryQueryEngine(project_root)

        if args.cell:
            results = query_engine.query_by_cell(args.cell)
            print(f"Found {len(results)} memories in cell {args.cell}")
            for mem in results[:10]:
                print(f"  - {mem.get('memory_id')}: {mem.get('content', '')[:50]}...")

        elif args.search:
            results = query_engine.full_text_search(args.search)
            print(f"Found {len(results)} memories matching '{args.search}'")
            for mem in results[:10]:
                print(f"  - {mem.get('memory_id')}: {mem.get('content', '')[:50]}...")

        elif args.relationships:
            results = query_engine.query_relationships(args.relationships)
            print(f"Found {len(results)} relationships for {args.relationships}")
            for rel in results[:10]:
                print(f"  - {rel.get('relationship_type')}: {rel.get('memory_id_1')} <-> {rel.get('memory_id_2')}")

        elif args.long_term:
            results = query_engine.query_long_term_memories(days=args.long_term)
            print(f"Found {len(results)} long-term memories (not accessed in {args.long_term} days)")
            for mem in results[:10]:
                print(f"  - {mem.get('memory_id')}: Last accessed {mem.get('last_accessed')}")

        elif args.high_performance:
            results = query_engine.query_high_performance_memories()
            print(f"Found {len(results)} high-performance memories")
            for mem in results[:10]:
                print(f"  - {mem.get('memory_id')}: Score {mem.get('performance_score', 0):.2f}")

        else:
            print("Usage:")
            print("  --cell <cell_id>           : Query by cell")
            print("  --search <query>          : Full-text search")
            print("  --relationships <mem_id>  : Query relationships")
            print("  --long-term <days>        : Query long-term memories")
            print("  --high-performance        : Query high-performance memories")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()