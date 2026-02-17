#!/usr/bin/env python3
"""
JARVIS Enhanced Memory System

Long-term memory, episodic memory, semantic memory.
Part of Phase 2 (Toddler → Child).

Tags: #JARVIS #MEMORY #PHASE2 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEnhancedMemory")


class MemoryType(Enum):
    """Types of memory"""
    EPISODIC = "episodic"  # Events, experiences
    SEMANTIC = "semantic"  # Facts, knowledge
    PROCEDURAL = "procedural"  # How-to, skills
    WORKING = "working"  # Short-term, active


@dataclass
class Memory:
    """A memory entry"""
    memory_id: str
    memory_type: MemoryType
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0-1
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    created_time: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISEnhancedMemory:
    """
    Enhanced memory system with long-term, episodic, semantic memory

    Capabilities:
    - Store and retrieve long-term memories
    - Episodic memory (events, experiences)
    - Semantic memory (facts, knowledge)
    - Procedural memory (skills, how-to)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize enhanced memory"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_memory"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.memories_file = self.data_dir / "memories.json"
        self.memories: Dict[str, Memory] = {}

        self._load_data()

        # Integrate with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
        except ImportError:
            self.learning_pipeline = None

        logger.info("=" * 80)
        logger.info("🧠 JARVIS ENHANCED MEMORY")
        logger.info("=" * 80)
        logger.info("   Long-term, episodic, semantic, procedural memory")
        logger.info("")

    def store_memory(self, memory_type: MemoryType, content: str, context: Dict[str, Any] = None, importance: float = 0.5) -> str:
        """Store a memory"""
        memory_id = f"mem_{int(time.time() * 1000)}"
        context = context or {}

        memory = Memory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            context=context,
            importance=importance
        )

        self.memories[memory_id] = memory
        self._save_data()

        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.MEMORY,
                source="enhanced_memory",
                context={"memory_type": memory_type.value, "context": context},
                data={"memory_id": memory_id, "importance": importance}
            )

        logger.debug(f"🧠 Stored {memory_type.value} memory: {memory_id}")
        return memory_id

    def retrieve_memories(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10) -> List[Memory]:
        """Retrieve relevant memories"""
        query_lower = query.lower()
        matches = []

        for memory in self.memories.values():
            if memory_type and memory.memory_type != memory_type:
                continue

            # Simple keyword matching
            if query_lower in memory.content.lower():
                memory.access_count += 1
                memory.last_accessed = datetime.now().isoformat()
                matches.append(memory)

        # Sort by importance and recency
        matches.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        self._save_data()

        return matches[:limit]

    def _load_data(self):
        """Load memories from disk"""
        try:
            if self.memories_file.exists():
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memories = {
                        mem_id: Memory(**{**mem_data, "memory_type": MemoryType(mem_data["memory_type"])})
                        for mem_id, mem_data in data.get("memories", {}).items()
                    }
                    logger.debug(f"Loaded {len(self.memories)} memories")
        except Exception as e:
            logger.debug(f"Could not load memory data: {e}")

    def _save_data(self):
        """Save memories to disk"""
        try:
            data = {
                "memories": {
                    mem_id: {**asdict(mem), "memory_type": mem.memory_type.value}
                    for mem_id, mem in self.memories.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save memory data: {e}")


# Singleton
_memory_instance: Optional[JARVISEnhancedMemory] = None

def get_jarvis_enhanced_memory(project_root: Optional[Path] = None) -> JARVISEnhancedMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = JARVISEnhancedMemory(project_root)
    return _memory_instance
