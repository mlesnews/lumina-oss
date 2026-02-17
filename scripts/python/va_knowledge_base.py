#!/usr/bin/env python3
"""
VA Knowledge Base System

Shared knowledge repository, synchronization, and learning system for VAs.

Tags: #VIRTUAL_ASSISTANT #KNOWLEDGE_BASE #LEARNING #SYNCHRONIZATION @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VAKnowledgeBase")


@dataclass
class KnowledgeEntry:
    """Knowledge entry"""
    entry_id: str
    source_va: str
    knowledge_type: str
    content: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    shared_with: List[str] = field(default_factory=list)
    access_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class VAKnowledgeBase:
    """
    VA Knowledge Base System

    Features:
    - Shared knowledge repository
    - VA-specific knowledge
    - Knowledge synchronization
    - Context sharing
    - Learning system
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize knowledge base system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Knowledge storage
        self.shared_knowledge: Dict[str, KnowledgeEntry] = {}
        self.va_knowledge: Dict[str, List[str]] = {va.character_id: [] for va in self.vas}

        # Knowledge counter
        self.knowledge_counter = 0

        # Data persistence
        self.data_dir = project_root / "data" / "va_knowledge_base"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("📚 VA KNOWLEDGE BASE SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Knowledge base initialized")
        logger.info("=" * 80)

    def store_knowledge(self, va_id: str, knowledge_type: str, content: Dict[str, Any],
                       tags: Optional[List[str]] = None,
                       share_with: Optional[List[str]] = None) -> KnowledgeEntry:
        """Store knowledge from a VA"""
        va = self.registry.get_character(va_id)
        if not va or va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            raise ValueError(f"VA {va_id} not found")

        self.knowledge_counter += 1
        entry_id = f"knowledge_{self.knowledge_counter:06d}"

        # Determine sharing
        if share_with is None:
            share_with = [v.character_id for v in self.vas if v.character_id != va_id]

        entry = KnowledgeEntry(
            entry_id=entry_id,
            source_va=va_id,
            knowledge_type=knowledge_type,
            content=content,
            tags=tags or [],
            shared_with=share_with
        )

        self.shared_knowledge[entry_id] = entry
        self.va_knowledge[va_id].append(entry_id)

        logger.info(f"📚 Stored knowledge: {entry_id} from {va_id} ({knowledge_type})")
        return entry

    def share_knowledge(self, source_va: str, target_va: str, entry_id: str) -> bool:
        """Share knowledge entry with another VA"""
        entry = self.shared_knowledge.get(entry_id)
        if not entry:
            return False

        if target_va not in entry.shared_with:
            entry.shared_with.append(target_va)
            entry.updated_at = datetime.now().isoformat()

        if entry_id not in self.va_knowledge[target_va]:
            self.va_knowledge[target_va].append(entry_id)

        logger.info(f"📤 Shared knowledge {entry_id} from {source_va} to {target_va}")
        return True

    def query_knowledge(self, va_id: str, query: str,
                       knowledge_type: Optional[str] = None) -> List[KnowledgeEntry]:
        """Query knowledge available to a VA"""
        # Get accessible knowledge entries
        accessible = []

        # Own knowledge
        for entry_id in self.va_knowledge.get(va_id, []):
            entry = self.shared_knowledge.get(entry_id)
            if entry:
                accessible.append(entry)

        # Shared knowledge
        for entry in self.shared_knowledge.values():
            if va_id in entry.shared_with and entry_id not in self.va_knowledge.get(va_id, []):
                accessible.append(entry)

        # Filter by type if specified
        if knowledge_type:
            accessible = [e for e in accessible if e.knowledge_type == knowledge_type]

        # Simple text matching (in real implementation, would use better search)
        if query:
            query_lower = query.lower()
            accessible = [
                e for e in accessible
                if query_lower in str(e.content).lower() or
                any(query_lower in tag.lower() for tag in e.tags)
            ]

        # Update access count
        for entry in accessible:
            entry.access_count += 1

        logger.info(f"🔍 Query from {va_id}: {len(accessible)} results")
        return accessible

    def sync_knowledge(self):
        """Synchronize knowledge across all VAs"""
        logger.info("🔄 Synchronizing knowledge...")

        # Share all knowledge with all VAs (simplified sync)
        for entry_id, entry in self.shared_knowledge.items():
            for va in self.vas:
                if va.character_id != entry.source_va:
                    if entry_id not in self.va_knowledge[va.character_id]:
                        self.va_knowledge[va.character_id].append(entry_id)
                    if va.character_id not in entry.shared_with:
                        entry.shared_with.append(va.character_id)

        logger.info("✅ Knowledge synchronized")

    def learn_from_interactions(self, va_id: str, interaction_data: Dict[str, Any]):
        """Learn from VA interactions"""
        # Extract patterns and store as knowledge
        knowledge_type = "interaction_pattern"

        content = {
            "interaction": interaction_data,
            "learned_at": datetime.now().isoformat()
        }

        tags = ["learning", "interaction", va_id]

        self.store_knowledge(va_id, knowledge_type, content, tags=tags)
        logger.info(f"🧠 Learned from interaction: {va_id}")

    def get_va_knowledge_summary(self, va_id: str) -> Dict[str, Any]:
        """Get knowledge summary for a VA"""
        entry_ids = self.va_knowledge.get(va_id, [])

        summary = {
            "va_id": va_id,
            "total_knowledge": len(entry_ids),
            "by_type": {},
            "shared_count": 0,
            "recent_knowledge": []
        }

        for entry_id in entry_ids:
            entry = self.shared_knowledge.get(entry_id)
            if not entry:
                continue

            # Count by type
            summary["by_type"][entry.knowledge_type] = summary["by_type"].get(entry.knowledge_type, 0) + 1

            # Count shared
            if len(entry.shared_with) > 0:
                summary["shared_count"] += 1

            # Recent knowledge
            summary["recent_knowledge"].append({
                "entry_id": entry_id,
                "type": entry.knowledge_type,
                "created_at": entry.created_at
            })

        summary["recent_knowledge"] = sorted(
            summary["recent_knowledge"],
            key=lambda x: x["created_at"],
            reverse=True
        )[:10]

        return summary

    def _save_state(self):
        try:
            """Save knowledge base state"""
            state_file = self.data_dir / "knowledge_base.json"

            state = {
                "shared_knowledge": {eid: e.to_dict() for eid, e in self.shared_knowledge.items()},
                "va_knowledge": self.va_knowledge.copy(),
                "knowledge_counter": self.knowledge_counter,
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved knowledge base to {state_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    kb = VAKnowledgeBase(registry)

    print("=" * 80)
    print("📚 VA KNOWLEDGE BASE SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Store knowledge
    print("Storing knowledge...")
    kb.store_knowledge("jarvis_va", "workflow", {
        "workflow_id": "test_workflow",
        "steps": ["step1", "step2", "step3"]
    }, tags=["automation", "workflow"])

    kb.store_knowledge("ace", "security", {
        "threat_type": "malware",
        "detection_method": "pattern_matching"
    }, tags=["security", "combat"])

    kb.store_knowledge("imva", "ui_pattern", {
        "pattern": "notification",
        "style": "bobblehead"
    }, tags=["ui", "visualization"])
    print("  ✅ Knowledge stored")
    print()

    # Test: Query knowledge
    print("Querying knowledge...")
    results = kb.query_knowledge("jarvis_va", "workflow")
    print(f"  ✅ Found {len(results)} results for 'workflow'")

    results = kb.query_knowledge("ace", "security")
    print(f"  ✅ Found {len(results)} results for 'security'")
    print()

    # Test: Share knowledge
    print("Sharing knowledge...")
    kb.share_knowledge("jarvis_va", "ace", "knowledge_000001")
    print("  ✅ Knowledge shared")
    print()

    # Test: Sync knowledge
    print("Synchronizing knowledge...")
    kb.sync_knowledge()
    print("  ✅ Knowledge synchronized")
    print()

    # Test: Knowledge summary
    print("Knowledge Summary:")
    for va in kb.vas:
        summary = kb.get_va_knowledge_summary(va.character_id)
        print(f"  • {va.name}: {summary['total_knowledge']} entries")
        if summary['by_type']:
            print(f"    Types: {summary['by_type']}")
    print()

    # Save state
    kb._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()