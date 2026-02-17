#!/usr/bin/env python3
"""
JARVIS Persistent Memory System

Ensures JARVIS remembers everything persistently throughout the entire ecosystem.
Integrates with R5 Living Context Matrix and all JARVIS systems.

Features:
- Persistent memory storage
- Cross-system memory sharing
- Context preservation
- Knowledge aggregation
- Long-term memory
- Short-term memory
- Working memory
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import hashlib

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPersistentMemory")


class MemoryType(Enum):
    """Types of memory"""
    LONG_TERM = "long_term"  # Permanent knowledge
    SHORT_TERM = "short_term"  # Recent context
    WORKING = "working"  # Current session
    EPISODIC = "episodic"  # Events and experiences
    SEMANTIC = "semantic"  # Facts and knowledge
    PROCEDURAL = "procedural"  # Skills and procedures


class MemoryPriority(Enum):
    """Memory priority levels (5/5 importance rating system)"""
    CRITICAL = "critical"  # 5/5 - Never forget, highest importance
    HIGH = "high"  # 4/5 - Very important
    MEDIUM = "medium"  # 3/5 - Normal importance
    LOW = "low"  # 2/5 - Can be archived
    TEMPORARY = "temporary"  # 1/5 - Can be deleted

    @classmethod
    def from_importance_rating(cls, rating: int) -> 'MemoryPriority':
        """Convert 1-5 importance rating to MemoryPriority"""
        if rating == 5:
            return cls.CRITICAL
        elif rating == 4:
            return cls.HIGH
        elif rating == 3:
            return cls.MEDIUM
        elif rating == 2:
            return cls.LOW
        else:
            return cls.TEMPORARY

    def to_importance_rating(self) -> int:
        """Convert MemoryPriority to 1-5 importance rating"""
        mapping = {
            MemoryPriority.CRITICAL: 5,
            MemoryPriority.HIGH: 4,
            MemoryPriority.MEDIUM: 3,
            MemoryPriority.LOW: 2,
            MemoryPriority.TEMPORARY: 1
        }
        return mapping.get(self, 3)


@dataclass
class Memory:
    """A single memory entry"""
    memory_id: str
    memory_type: MemoryType
    priority: MemoryPriority
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    source: str = ""  # Where this memory came from
    timestamp: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    related_memories: List[str] = field(default_factory=list)  # IDs of related memories

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['memory_type'] = self.memory_type.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create from dictionary"""
        data['memory_type'] = MemoryType(data['memory_type'])
        data['priority'] = MemoryPriority(data['priority'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


class JARVISPersistentMemory:
    """
    JARVIS Persistent Memory System

    Ensures JARVIS remembers everything across the entire ecosystem.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Memory storage
        self.memory_dir = project_root / "data" / "jarvis_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # SQLite database for fast queries
        self.db_path = self.memory_dir / "memory.db"
        self._init_database()

        # JSON backup for redundancy
        self.json_backup_path = self.memory_dir / "memory_backup.json"

        # In-memory cache for fast access
        self.memory_cache: Dict[str, Memory] = {}
        self.cache_size_limit = 10000  # Max cached memories

        # R5 Integration
        self.r5_integration = None
        self._init_r5_integration()

        self.logger.info("✅ JARVIS Persistent Memory initialized")
        self.logger.info(f"   Database: {self.db_path}")
        self.logger.info(f"   Backup: {self.json_backup_path}")

    def _init_database(self):
        try:
            """Initialize SQLite database"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Create memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    tags TEXT,
                    source TEXT,
                    timestamp TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    related_memories TEXT
                )
            ''')

            # Create indexes for fast queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON memories(priority)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON memories(source)')

            conn.commit()
            conn.close()

            self.logger.info("✅ Memory database initialized")

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def _init_r5_integration(self):
        """Initialize R5 Living Context Matrix integration"""
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.r5_integration = R5LivingContextMatrix(self.project_root)
            self.logger.info("✅ R5 Living Context Matrix integrated")
        except ImportError:
            self.logger.debug("R5 Living Context Matrix not available")
        except Exception as e:
            self.logger.debug(f"R5 integration error: {e}")

    def store_memory(self, content: str, memory_type: MemoryType = MemoryType.SHORT_TERM,
                     priority: MemoryPriority = MemoryPriority.MEDIUM,
                     context: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None,
                     source: str = "") -> str:
        """
        Store a memory persistently

        Returns:
            memory_id: Unique ID of stored memory
        """
        # Generate memory ID
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        memory_id = f"mem_{timestamp_str}_{content_hash}"

        # Create memory object
        memory = Memory(
            memory_id=memory_id,
            memory_type=memory_type,
            priority=priority,
            content=content,
            context=context or {},
            tags=tags or [],
            source=source,
            timestamp=datetime.now(),
            last_accessed=datetime.now()
        )

        # Store in database
        self._store_in_database(memory)

        # Store in cache
        if len(self.memory_cache) < self.cache_size_limit:
            self.memory_cache[memory_id] = memory

        # Store in R5 if long-term or high priority
        if memory_type == MemoryType.LONG_TERM or priority in [MemoryPriority.CRITICAL, MemoryPriority.HIGH]:
            self._store_in_r5(memory)

        # Backup to JSON
        self._backup_to_json()

        self.logger.info(f"💾 Memory stored: {memory_id[:20]}... ({memory_type.value})")

        return memory_id

    def _store_in_database(self, memory: Memory):
        try:
            """Store memory in SQLite database"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO memories 
                (memory_id, memory_type, priority, content, context, tags, source, 
                 timestamp, last_accessed, access_count, related_memories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.memory_id,
                memory.memory_type.value,
                memory.priority.value,
                memory.content,
                json.dumps(memory.context),
                json.dumps(memory.tags),
                memory.source,
                memory.timestamp.isoformat(),
                memory.last_accessed.isoformat(),
                memory.access_count,
                json.dumps(memory.related_memories)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in _store_in_database: {e}", exc_info=True)
            raise
    def _store_in_r5(self, memory: Memory):
        """Store memory in R5 Living Context Matrix"""
        if not self.r5_integration:
            return

        try:
            # Store as knowledge in R5
            self.r5_integration.store_knowledge(
                content=memory.content,
                context=memory.context,
                tags=memory.tags,
                source=f"jarvis_memory:{memory.memory_id}"
            )
        except Exception as e:
            self.logger.debug(f"R5 storage error: {e}")

    def _backup_to_json(self):
        """Backup memories to JSON file"""
        try:
            # Get all memories from database
            memories = self.retrieve_all_memories()

            # Convert to JSON
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'count': len(memories),
                'memories': [m.to_dict() for m in memories]
            }

            # Write to file
            with open(self.json_backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Backup error: {e}")

    def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        try:
            """Retrieve a memory by ID"""
            # Check cache first
            if memory_id in self.memory_cache:
                memory = self.memory_cache[memory_id]
                memory.last_accessed = datetime.now()
                memory.access_count += 1
                self._update_access(memory)
                return memory

            # Query database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM memories WHERE memory_id = ?', (memory_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                memory = self._row_to_memory(row)
                # Update cache
                if len(self.memory_cache) < self.cache_size_limit:
                    self.memory_cache[memory_id] = memory
                return memory

            return None

        except Exception as e:
            self.logger.error(f"Error in retrieve_memory: {e}", exc_info=True)
            raise

    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None,
                       tags: Optional[List[str]] = None,
                       limit: int = 100) -> List[Memory]:
        """Search memories by content, type, or tags"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Build query
            conditions = []
            params = []

            if query:
                conditions.append("content LIKE ?")
                params.append(f"%{query}%")

            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type.value)

            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            sql = f'''
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY last_accessed DESC, access_count DESC
                LIMIT ?
            '''
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            memories = [self._row_to_memory(row) for row in rows]

            # Update access times
            for memory in memories:
                memory.last_accessed = datetime.now()
                memory.access_count += 1
                self._update_access(memory)

            return memories

        except Exception as e:
            self.logger.error(f"Error in search_memories: {e}", exc_info=True)
            raise
    def retrieve_all_memories(self, memory_type: Optional[MemoryType] = None) -> List[Memory]:
        try:
            """Retrieve all memories (or filtered by type)"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            if memory_type:
                cursor.execute('SELECT * FROM memories WHERE memory_type = ?', (memory_type.value,))
            else:
                cursor.execute('SELECT * FROM memories')

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_memory(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error in retrieve_all_memories: {e}", exc_info=True)
            raise
    def _row_to_memory(self, row) -> Memory:
        try:
            """Convert database row to Memory object"""
            return Memory(
                memory_id=row[0],
                memory_type=MemoryType(row[1]),
                priority=MemoryPriority(row[2]),
                content=row[3],
                context=json.loads(row[4] or '{}'),
                tags=json.loads(row[5] or '[]'),
                source=row[6],
                timestamp=datetime.fromisoformat(row[7]),
                last_accessed=datetime.fromisoformat(row[8]),
                access_count=row[9],
                related_memories=json.loads(row[10] or '[]')
            )

        except Exception as e:
            self.logger.error(f"Error in _row_to_memory: {e}", exc_info=True)
            raise
    def _update_access(self, memory: Memory):
        try:
            """Update access information in database"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE memories 
                SET last_accessed = ?, access_count = ?
                WHERE memory_id = ?
            ''', (memory.last_accessed.isoformat(), memory.access_count, memory.memory_id))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in _update_access: {e}", exc_info=True)
            raise
    def link_memories(self, memory_id1: str, memory_id2: str):
        """Link two memories together"""
        mem1 = self.retrieve_memory(memory_id1)
        mem2 = self.retrieve_memory(memory_id2)

        if mem1 and mem2:
            if memory_id2 not in mem1.related_memories:
                mem1.related_memories.append(memory_id2)
            if memory_id1 not in mem2.related_memories:
                mem2.related_memories.append(memory_id1)

            self._store_in_database(mem1)
            self._store_in_database(mem2)

    def get_memory_stats(self) -> Dict[str, Any]:
        try:
            """Get statistics about stored memories"""
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            stats = {}

            # Total count
            cursor.execute('SELECT COUNT(*) FROM memories')
            stats['total'] = cursor.fetchone()[0]

            # By type
            cursor.execute('SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type')
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

            # By priority
            cursor.execute('SELECT priority, COUNT(*) FROM memories GROUP BY priority')
            stats['by_priority'] = {row[0]: row[1] for row in cursor.fetchall()}

            # Most accessed
            cursor.execute('SELECT memory_id, access_count FROM memories ORDER BY access_count DESC LIMIT 10')
            stats['most_accessed'] = [{'id': row[0], 'count': row[1]} for row in cursor.fetchall()]

            conn.close()

            return stats


        except Exception as e:
            self.logger.error(f"Error in get_memory_stats: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Persistent Memory")
    parser.add_argument("--store", type=str, help="Store a memory")
    parser.add_argument("--retrieve", type=str, help="Retrieve memory by ID")
    parser.add_argument("--search", type=str, help="Search memories")
    parser.add_argument("--stats", action="store_true", help="Get memory statistics")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    memory = JARVISPersistentMemory(project_root)

    if args.store:
        memory_id = memory.store_memory(args.store)
        print(f"✅ Memory stored: {memory_id}")

    elif args.retrieve:
        mem = memory.retrieve_memory(args.retrieve)
        if mem:
            print(f"\n📝 Memory: {mem.memory_id}")
            print(f"   Type: {mem.memory_type.value}")
            print(f"   Priority: {mem.priority.value}")
            print(f"   Content: {mem.content[:100]}...")
            print(f"   Accessed: {mem.access_count} times")
        else:
            print("❌ Memory not found")

    elif args.search:
        results = memory.search_memories(args.search)
        print(f"\n🔍 Found {len(results)} memories:")
        for mem in results[:10]:
            print(f"   - {mem.memory_id[:20]}... : {mem.content[:50]}...")

    elif args.stats:
        stats = memory.get_memory_stats()
        print("\n" + "="*80)
        print("JARVIS MEMORY STATISTICS")
        print("="*80)
        print(f"Total Memories: {stats['total']}")
        print(f"\nBy Type:")
        for type, count in stats['by_type'].items():
            print(f"   {type}: {count}")
        print(f"\nBy Priority:")
        for priority, count in stats['by_priority'].items():
            print(f"   {priority}: {count}")
        print("="*80)

    else:
        print("Usage:")
        print("  --store 'content'    : Store a memory")
        print("  --retrieve <id>      : Retrieve memory")
        print("  --search 'query'     : Search memories")
        print("  --stats              : Get statistics")


if __name__ == "__main__":


    main()