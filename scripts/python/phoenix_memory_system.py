#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════
🔥 PHOENIX MEMORY SYSTEM
═══════════════════════════════════════════════════════════════════════════════════

"Rise from the ashes of every session"

The solution to 100% persistent AI memory.

ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Layer 1: PERMANENT INJECTION (.cursorrules + Cursor memories)                  │
│     ↓  [100% automatic at session start]                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Layer 2: PROACTIVE RETRIEVAL (RAG with semantic search)                        │
│     ↓  [Query-time memory retrieval]                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Layer 3: ON-DEMAND RECALL (JARVIS Persistent Memory)                           │
│     ↓  [Explicit memory lookup]                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Layer 4: SESSION CONSOLIDATION (Auto-extract lessons)                          │
│     ↓  [Before session ends, persist critical learnings]                        │
└─────────────────────────────────────────────────────────────────────────────────┘

IMPLEMENTATION DATE: 2026-01-17
STATUS: FOUNDATIONAL
═══════════════════════════════════════════════════════════════════════════════════
"""

import sys
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PHOENIXMemory")


class MemoryUrgency(Enum):
    """Urgency levels for memory injection"""
    CRITICAL = "critical"   # MUST be injected every session (life/death lessons)
    HIGH = "high"           # Should be injected if relevant
    MEDIUM = "medium"       # Inject if space allows
    LOW = "low"             # Archive, retrieve on demand


class MemoryCategory(Enum):
    """Categories of memories"""
    DISASTER_PREVENTION = "disaster_prevention"  # Lessons that prevent catastrophe
    WORKFLOW = "workflow"                        # How to do things
    RULE = "rule"                                # Project rules and standards
    INSIGHT = "insight"                          # Learned patterns and insights
    RELATIONSHIP = "relationship"                # Connections between concepts
    ERROR_PATTERN = "error_pattern"              # Known error patterns
    SOLUTION_PATTERN = "solution_pattern"        # Proven solutions


@dataclass
class PhoenixMemory:
    """A memory in the PHOENIX system"""
    memory_id: str
    title: str
    content: str
    urgency: MemoryUrgency
    category: MemoryCategory
    tags: List[str]
    source_session: str           # Where this was learned
    timestamp: datetime
    last_injected: Optional[datetime] = None
    injection_count: int = 0
    effectiveness_score: float = 1.0  # How useful was this memory
    embedding: Optional[List[float]] = None  # Vector embedding for semantic search
    related_memories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "title": self.title,
            "content": self.content,
            "urgency": self.urgency.value,
            "category": self.category.value,
            "tags": self.tags,
            "source_session": self.source_session,
            "timestamp": self.timestamp.isoformat(),
            "last_injected": self.last_injected.isoformat() if self.last_injected else None,
            "injection_count": self.injection_count,
            "effectiveness_score": self.effectiveness_score,
            "related_memories": self.related_memories
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhoenixMemory':
        return cls(
            memory_id=data["memory_id"],
            title=data["title"],
            content=data["content"],
            urgency=MemoryUrgency(data["urgency"]),
            category=MemoryCategory(data["category"]),
            tags=data.get("tags", []),
            source_session=data.get("source_session", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            last_injected=datetime.fromisoformat(data["last_injected"]) if data.get("last_injected") else None,
            injection_count=data.get("injection_count", 0),
            effectiveness_score=data.get("effectiveness_score", 1.0),
            related_memories=data.get("related_memories", [])
        )


class PHOENIXMemorySystem:
    """
    PHOENIX Memory System - 100% Persistent AI Memory

    "Rise from the ashes of every session"
    """

    def __init__(self, project_root: Path = None):
        self.project_root = Path(project_root or script_dir.parent.parent)
        self.memory_dir = self.project_root / "data" / "phoenix_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Database
        self.db_path = self.memory_dir / "phoenix.db"
        self._init_database()

        # Critical memories file (always load first)
        self.critical_memories_path = self.memory_dir / "CRITICAL_MEMORIES.json"

        # Session state
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_learnings: List[str] = []

        logger.info("🔥 PHOENIX Memory System initialized")
        logger.info(f"   Session: {self.current_session_id}")
        logger.info(f"   Database: {self.db_path}")

    def _init_database(self):
        try:
            """Initialize SQLite database"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,
                    source_session TEXT,
                    timestamp TEXT NOT NULL,
                    last_injected TEXT,
                    injection_count INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 1.0,
                    related_memories TEXT
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_urgency ON memories(urgency)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON memories(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    # ═══════════════════════════════════════════════════════════════════════════
    # LAYER 1: PERMANENT INJECTION
    # ═══════════════════════════════════════════════════════════════════════════

    def get_critical_memories_for_injection(self) -> List[PhoenixMemory]:
        try:
            """
            Get all CRITICAL memories that must be injected every session.

            These are the non-negotiable lessons that the AI must NEVER forget.
            """
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM memories 
                WHERE urgency = 'critical'
                ORDER BY effectiveness_score DESC, injection_count DESC
            ''')

            rows = cursor.fetchall()
            conn.close()

            memories = [self._row_to_memory(row) for row in rows]
            return memories

        except Exception as e:
            self.logger.error(f"Error in get_critical_memories_for_injection: {e}", exc_info=True)
            raise
    def generate_session_start_injection(self) -> str:
        """
        Generate the context injection for session start.

        This is what should be prepended to every session.
        """
        critical_memories = self.get_critical_memories_for_injection()

        if not critical_memories:
            return ""

        lines = [
            "═" * 80,
            "🔥 PHOENIX MEMORY INJECTION",
            "═" * 80,
            f"Session Start: {datetime.now().isoformat()}",
            f"Critical Memories Loaded: {len(critical_memories)}",
            "═" * 80,
            ""
        ]

        for memory in critical_memories:
            lines.append(f"📌 {memory.title}")
            lines.append(f"   Category: {memory.category.value}")
            lines.append(f"   {memory.content[:500]}...")
            lines.append("")

        lines.append("═" * 80)

        return "\n".join(lines)

    def update_cursorrules_with_critical(self):
        try:
            """
            Update .cursorrules with critical memories.

            This ensures PERMANENT injection via Cursor's native system.
            """
            # Find .cursorrules
            cursorrules_path = self.project_root / ".cursorrules"

            if not cursorrules_path.exists():
                logger.warning(".cursorrules not found")
                return

            critical_memories = self.get_critical_memories_for_injection()

            if not critical_memories:
                logger.info("No critical memories to inject into .cursorrules")
                return

            # Generate the critical memories section
            critical_section = self._generate_critical_rules_section(critical_memories)

            # Read existing content
            with open(cursorrules_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find or create the critical memories section
            marker_start = "# PHOENIX CRITICAL MEMORIES (AUTO-GENERATED)"
            marker_end = "# END PHOENIX CRITICAL MEMORIES"

            if marker_start in content:
                # Replace existing section
                pattern = re.compile(
                    f"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
                    re.DOTALL
                )
                content = pattern.sub(critical_section, content)
            else:
                # Append section
                content = content.rstrip() + "\n\n" + critical_section

            # Write back
            with open(cursorrules_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"✅ Updated .cursorrules with {len(critical_memories)} critical memories")

        except Exception as e:
            self.logger.error(f"Error in update_cursorrules_with_critical: {e}", exc_info=True)
            raise
    def _generate_critical_rules_section(self, memories: List[PhoenixMemory]) -> str:
        """Generate the .cursorrules section for critical memories"""
        lines = [
            "# PHOENIX CRITICAL MEMORIES (AUTO-GENERATED)",
            f"# Last Updated: {datetime.now().isoformat()}",
            "# These lessons must NEVER be forgotten",
            ""
        ]

        for memory in memories:
            lines.append(f"## {memory.title}")
            lines.append(f"**Category**: {memory.category.value}")
            lines.append(f"**Tags**: {', '.join(memory.tags)}")
            lines.append("")
            lines.append(memory.content)
            lines.append("")
            lines.append("---")
            lines.append("")

        lines.append("# END PHOENIX CRITICAL MEMORIES")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # LAYER 2: PROACTIVE RETRIEVAL (RAG)
    # ═══════════════════════════════════════════════════════════════════════════

    def retrieve_relevant_memories(
        self,
        query: str,
        limit: int = 5,
        min_relevance: float = 0.3
    ) -> List[Tuple[PhoenixMemory, float]]:
        """
        Retrieve memories relevant to the current query.

        Uses keyword matching (semantic search to be added).
        Returns list of (memory, relevance_score) tuples.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Simple keyword search (to be replaced with vector search)
        query_words = set(query.lower().split())

        cursor.execute('SELECT * FROM memories')
        rows = cursor.fetchall()
        conn.close()

        scored_memories = []

        for row in rows:
            memory = self._row_to_memory(row)

            # Calculate relevance score
            memory_words = set(memory.content.lower().split())
            memory_words.update(tag.lower() for tag in memory.tags)
            memory_words.update(memory.title.lower().split())

            # Simple Jaccard similarity
            intersection = len(query_words & memory_words)
            union = len(query_words | memory_words)
            relevance = intersection / union if union > 0 else 0

            # Boost critical memories
            if memory.urgency == MemoryUrgency.CRITICAL:
                relevance *= 1.5

            if relevance >= min_relevance:
                scored_memories.append((memory, relevance))

        # Sort by relevance
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return scored_memories[:limit]

    # ═══════════════════════════════════════════════════════════════════════════
    # LAYER 3: ON-DEMAND RECALL
    # ═══════════════════════════════════════════════════════════════════════════

    def recall_memory(self, memory_id: str) -> Optional[PhoenixMemory]:
        try:
            """Recall a specific memory by ID"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM memories WHERE memory_id = ?', (memory_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_memory(row)
            return None

        except Exception as e:
            self.logger.error(f"Error in recall_memory: {e}", exc_info=True)
            raise
    def search_memories(
        self,
        query: str = "",
        category: Optional[MemoryCategory] = None,
        urgency: Optional[MemoryUrgency] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[PhoenixMemory]:
        """Search memories with filters"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        conditions = []
        params = []

        if query:
            conditions.append("(content LIKE ? OR title LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        if category:
            conditions.append("category = ?")
            params.append(category.value)

        if urgency:
            conditions.append("urgency = ?")
            params.append(urgency.value)

        if tags:
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f'''
            SELECT * FROM memories 
            WHERE {where_clause}
            ORDER BY urgency DESC, effectiveness_score DESC
            LIMIT ?
        '''
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_memory(row) for row in rows]

    # ═══════════════════════════════════════════════════════════════════════════
    # LAYER 4: SESSION CONSOLIDATION
    # ═══════════════════════════════════════════════════════════════════════════

    def store_memory(
        self,
        title: str,
        content: str,
        urgency: MemoryUrgency = MemoryUrgency.MEDIUM,
        category: MemoryCategory = MemoryCategory.INSIGHT,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store a new memory.

        This is called when a new lesson is learned.
        """
        # Generate memory ID
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        memory_id = f"phx_{timestamp_str}_{content_hash}"

        memory = PhoenixMemory(
            memory_id=memory_id,
            title=title,
            content=content,
            urgency=urgency,
            category=category,
            tags=tags or [],
            source_session=self.current_session_id,
            timestamp=datetime.now()
        )

        self._store_in_database(memory)

        # If critical, update .cursorrules
        if urgency == MemoryUrgency.CRITICAL:
            self.update_cursorrules_with_critical()

        logger.info(f"💾 Stored memory: {title[:50]}... ({urgency.value})")

        return memory_id

    def record_session_learning(self, learning: str):
        """
        Record a learning during the current session.

        These will be reviewed and potentially persisted at session end.
        """
        self.session_learnings.append(learning)
        logger.debug(f"📝 Recorded learning: {learning[:50]}...")

    def consolidate_session_learnings(self) -> Dict[str, Any]:
        """
        Consolidate learnings from the current session.

        This should be called before session ends.
        Reviews all learnings and persists important ones.
        """
        if not self.session_learnings:
            return {"consolidated": 0, "discarded": 0}

        consolidated = 0
        discarded = 0

        for learning in self.session_learnings:
            # Determine if this should be persisted
            # (In full implementation, this would use AI to classify)

            # Simple heuristics
            is_critical = any(word in learning.lower() for word in [
                "critical", "never", "always", "fatal", "disaster", "prevent",
                "lesson", "learned", "mistake", "error", "fix"
            ])

            if is_critical:
                urgency = MemoryUrgency.HIGH
                if any(word in learning.lower() for word in ["fatal", "disaster", "prevent"]):
                    urgency = MemoryUrgency.CRITICAL

                self.store_memory(
                    title=f"Session Learning: {learning[:50]}...",
                    content=learning,
                    urgency=urgency,
                    category=MemoryCategory.INSIGHT,
                    tags=["auto_consolidated", self.current_session_id]
                )
                consolidated += 1
            else:
                discarded += 1

        result = {"consolidated": consolidated, "discarded": discarded}

        logger.info(f"📦 Session consolidation: {consolidated} stored, {discarded} discarded")

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _store_in_database(self, memory: PhoenixMemory):
        """Store memory in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (memory_id, title, content, urgency, category, tags, source_session,
             timestamp, last_injected, injection_count, effectiveness_score, related_memories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.memory_id,
            memory.title,
            memory.content,
            memory.urgency.value,
            memory.category.value,
            json.dumps(memory.tags),
            memory.source_session,
            memory.timestamp.isoformat(),
            memory.last_injected.isoformat() if memory.last_injected else None,
            memory.injection_count,
            memory.effectiveness_score,
            json.dumps(memory.related_memories)
        ))

        conn.commit()
        conn.close()

    def _row_to_memory(self, row) -> PhoenixMemory:
        """Convert database row to PhoenixMemory"""
        return PhoenixMemory(
            memory_id=row[0],
            title=row[1],
            content=row[2],
            urgency=MemoryUrgency(row[3]),
            category=MemoryCategory(row[4]),
            tags=json.loads(row[5] or '[]'),
            source_session=row[6],
            timestamp=datetime.fromisoformat(row[7]),
            last_injected=datetime.fromisoformat(row[8]) if row[8] else None,
            injection_count=row[9],
            effectiveness_score=row[10],
            related_memories=json.loads(row[11] or '[]')
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        stats = {}

        cursor.execute('SELECT COUNT(*) FROM memories')
        stats['total_memories'] = cursor.fetchone()[0]

        cursor.execute('SELECT urgency, COUNT(*) FROM memories GROUP BY urgency')
        stats['by_urgency'] = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT category, COUNT(*) FROM memories GROUP BY category')
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT AVG(effectiveness_score) FROM memories')
        stats['avg_effectiveness'] = cursor.fetchone()[0] or 0

        conn.close()

        return stats


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="PHOENIX Memory System")
    parser.add_argument("--store", type=str, help="Store a new memory (title|content|urgency|category)")
    parser.add_argument("--search", type=str, help="Search memories")
    parser.add_argument("--inject", action="store_true", help="Generate session start injection")
    parser.add_argument("--update-rules", action="store_true", help="Update .cursorrules with critical memories")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--add-critical", type=str, help="Add a critical memory (disaster prevention)")

    args = parser.parse_args()

    phoenix = PHOENIXMemorySystem()

    if args.store:
        parts = args.store.split("|")
        if len(parts) >= 2:
            title, content = parts[0], parts[1]
            urgency = MemoryUrgency(parts[2]) if len(parts) > 2 else MemoryUrgency.MEDIUM
            category = MemoryCategory(parts[3]) if len(parts) > 3 else MemoryCategory.INSIGHT

            memory_id = phoenix.store_memory(title, content, urgency, category)
            print(f"✅ Stored: {memory_id}")

    elif args.search:
        memories = phoenix.search_memories(query=args.search)
        print(f"\n🔍 Found {len(memories)} memories:")
        for mem in memories:
            print(f"   [{mem.urgency.value}] {mem.title}")
            print(f"      {mem.content[:100]}...")

    elif args.inject:
        injection = phoenix.generate_session_start_injection()
        print(injection)

    elif args.update_rules:
        phoenix.update_cursorrules_with_critical()
        print("✅ Updated .cursorrules")

    elif args.stats:
        stats = phoenix.get_statistics()
        print("\n" + "=" * 60)
        print("🔥 PHOENIX MEMORY STATISTICS")
        print("=" * 60)
        print(f"Total Memories: {stats['total_memories']}")
        print(f"\nBy Urgency:")
        for urgency, count in stats.get('by_urgency', {}).items():
            print(f"   {urgency}: {count}")
        print(f"\nBy Category:")
        for category, count in stats.get('by_category', {}).items():
            print(f"   {category}: {count}")
        print(f"\nAvg Effectiveness: {stats['avg_effectiveness']:.2f}")
        print("=" * 60)

    elif args.add_critical:
        # Add a critical disaster prevention memory
        memory_id = phoenix.store_memory(
            title=f"CRITICAL: {args.add_critical[:50]}",
            content=args.add_critical,
            urgency=MemoryUrgency.CRITICAL,
            category=MemoryCategory.DISASTER_PREVENTION,
            tags=["critical", "disaster_prevention", "never_forget"]
        )
        print(f"✅ Added CRITICAL memory: {memory_id}")
        phoenix.update_cursorrules_with_critical()

    else:
        # Default: Show status
        stats = phoenix.get_statistics()
        critical = len([1 for u, c in stats.get('by_urgency', {}).items() if u == 'critical'])

        print("\n" + "🔥" * 40)
        print("PHOENIX MEMORY SYSTEM")
        print("'Rise from the ashes of every session'")
        print("🔥" * 40)
        print(f"\nTotal Memories: {stats['total_memories']}")
        print(f"Critical (Never Forget): {critical}")
        print(f"\nUse --inject to get session start context")
        print("Use --add-critical 'lesson' to add critical memory")
        print("Use --update-rules to sync to .cursorrules")


if __name__ == "__main__":


    main()