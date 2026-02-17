#!/usr/bin/env python3
"""
Troubleshooting @ALWAYS Importance System

@ALWAYS policy: When focusing and troubleshooting any situations/problems,
this must be an @ALWAYS +++++ FIVE OF FIVE memory add/update/deletion,
similar to five-star ratings but for importance.

Tags: #troubleshooting #always #importance #5of5 #memory #priority
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority
from prevent_memory_gap_automation import MemoryGapPrevention

logger = get_logger("TroubleshootingAlwaysImportance")


class ImportanceRating(Enum):
    """5/5 importance rating system"""
    ONE = 1  # Lowest importance
    TWO = 2  # Low importance
    THREE = 3  # Medium importance
    FOUR = 4  # High importance
    FIVE = 5  # Critical importance (+++++)


@dataclass
class TroubleshootingEvent:
    """Troubleshooting event with importance rating"""
    event_id: str
    situation: str
    problem: str
    importance_rating: ImportanceRating
    analysis: str
    solutions: List[str] = field(default_factory=list)
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['importance_rating'] = self.importance_rating.value
        result['created_at'] = self.created_at.isoformat()
        if self.resolved_at:
            result['resolved_at'] = self.resolved_at.isoformat()
        return result


class TroubleshootingAlwaysImportanceSystem:
    """
    Troubleshooting @ALWAYS Importance System

    When focusing and troubleshooting situations/problems:
    - Must be @ALWAYS policy
    - Must use 5/5 importance rating system
    - Must store in memory with appropriate priority
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.memory = JARVISPersistentMemory(self.project_root)
        self.memory_gap_prevention = MemoryGapPrevention(self.project_root)

        logger.info("=" * 80)
        logger.info("🔧 TROUBLESHOOTING @ALWAYS IMPORTANCE SYSTEM")
        logger.info("=" * 80)
        logger.info("   Policy: @ALWAYS for troubleshooting")
        logger.info("   Importance: 5/5 rating system (+++++)")
        logger.info("   Memory: Automatic storage with priority")
        logger.info("=" * 80)
        logger.info("")

    def create_troubleshooting_memory(
        self,
        situation: str,
        problem: str,
        importance_rating: int,
        analysis: str,
        solutions: Optional[List[str]] = None
    ) -> str:
        """
        Create troubleshooting memory with importance rating

        @ALWAYS policy: All troubleshooting must use 5/5 importance system
        """
        if importance_rating < 1 or importance_rating > 5:
            logger.warning(f"⚠️  Importance rating {importance_rating} out of range, using 5")
            importance_rating = 5

        # Convert to MemoryPriority
        priority = MemoryPriority.from_importance_rating(importance_rating)

        # Create memory content
        content = f"TROUBLESHOOTING @ALWAYS: {situation}\n\n"
        content += f"Problem: {problem}\n\n"
        content += f"Importance Rating: {importance_rating}/5 ({'+' * importance_rating})\n\n"
        content += f"Analysis: {analysis}\n\n"

        if solutions:
            content += "Solutions:\n"
            for i, sol in enumerate(solutions, 1):
                content += f"{i}. {sol}\n"

        # Check for existing memory (use specific keywords to avoid false matches)
        keywords = [
            situation.lower().replace(" ", "_"),
            problem.lower()[:50].replace(" ", "_"),
            f"vas_state_resyphon" if "vas" in situation.lower() or "resyphon" in situation.lower() else None,
            f"performance_timeout" if "timeout" in problem.lower() or "performance" in problem.lower() else None
        ]
        keywords = [k for k in keywords if k]  # Remove None values

        tags = [
            "troubleshooting",
            "@always",
            f"importance_{importance_rating}",
            f"rating_{importance_rating}of5",
            situation.lower().replace(" ", "_"),
            "problem_solving"
        ]

        # Use memory gap prevention
        context = {"category": "troubleshooting", "situation": situation, "problem": problem}
        result = self.memory_gap_prevention.store_memory_safely(
            content=content,
            memory_type=MemoryType.EPISODIC,
            priority=priority,
            tags=tags,
            content_keywords=keywords,
            context=context
        )

        if result.get("stored", True):
            memory_id = result.get("memory_id", "unknown")
        else:
            memory_id = result.get("existing_memory", {}).get("memory_id", "existing")

        logger.info("=" * 80)
        logger.info("🔧 TROUBLESHOOTING MEMORY CREATED (@ALWAYS)")
        logger.info("=" * 80)
        logger.info(f"   Situation: {situation}")
        logger.info(f"   Problem: {problem}")
        logger.info(f"   Importance: {importance_rating}/5 ({'+' * importance_rating})")
        logger.info(f"   Priority: {priority.value}")
        logger.info(f"   Memory ID: {memory_id}")
        logger.info("=" * 80)
        logger.info("")

        return memory_id

    def store_troubleshooting_always_policy(self):
        """Store the @ALWAYS troubleshooting policy as CRITICAL memory"""
        content = """TROUBLESHOOTING @ALWAYS POLICY

When focusing and troubleshooting any situations and problems, this must be an @ALWAYS policy.

Importance Rating System (5/5):
- 5/5 (+++++) = CRITICAL - Never forget, highest importance
- 4/5 (++++) = HIGH - Very important
- 3/5 (+++) = MEDIUM - Normal importance
- 2/5 (++) = LOW - Can be archived
- 1/5 (+) = TEMPORARY - Can be deleted

Memory Storage:
- All troubleshooting events must be stored in memory
- Must use appropriate priority based on importance rating
- Must use @ALWAYS tag
- Must include situation, problem, analysis, and solutions

This is similar to five-star ratings but for importance, not quality.

Policy applies to:
- All troubleshooting activities
- Problem-solving sessions
- Situation analysis
- Roadblock identification
- Issue resolution

@ALWAYS +++++ (5/5) IMPORTANCE"""

        context = {"category": "policy", "type": "troubleshooting_always"}
        result = self.memory_gap_prevention.store_memory_safely(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.CRITICAL,
            tags=["troubleshooting", "@always", "policy", "importance", "5of5", "critical", "+++++"],
            content_keywords=["troubleshooting_always_policy", "5of5_importance", "troubleshooting_memory"],
            context=context
        )

        if result.get("stored", True):
            memory_id = result.get("memory_id", "unknown")
        else:
            memory_id = result.get("existing_memory", {}).get("memory_id", "existing")

        logger.info("✅ TROUBLESHOOTING @ALWAYS POLICY STORED (CRITICAL)")
        logger.info(f"   Memory ID: {memory_id}")
        logger.info("   Priority: CRITICAL (5/5)")
        logger.info("")

        return memory_id


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Troubleshooting @ALWAYS Importance System")
    parser.add_argument('--store-policy', action='store_true', help='Store @ALWAYS policy')
    parser.add_argument('--troubleshoot', nargs=4, metavar=('SITUATION', 'PROBLEM', 'RATING', 'ANALYSIS'),
                       help='Create troubleshooting memory')
    parser.add_argument('--solution', action='append', metavar='SOLUTION', help='Add solution (can use multiple times)')

    args = parser.parse_args()

    system = TroubleshootingAlwaysImportanceSystem()

    if args.store_policy:
        system.store_troubleshooting_always_policy()
        print("\n✅ Troubleshooting @ALWAYS policy stored")

    elif args.troubleshoot:
        situation, problem, rating_str, analysis = args.troubleshoot
        try:
            rating = int(rating_str)
        except ValueError:
            print(f"❌ Invalid rating: {rating_str}, using 5")
            rating = 5

        solutions = args.solution if args.solution else []
        memory_id = system.create_troubleshooting_memory(
            situation=situation,
            problem=problem,
            importance_rating=rating,
            analysis=analysis,
            solutions=solutions
        )
        print(f"\n✅ Troubleshooting memory created: {memory_id}")

    else:
        print("\n" + "=" * 80)
        print("🔧 TROUBLESHOOTING @ALWAYS IMPORTANCE SYSTEM")
        print("=" * 80)
        print("   Use --store-policy to store @ALWAYS policy")
        print("   Use --troubleshoot to create troubleshooting memory")
        print("   Use --solution to add solutions (can use multiple times)")
        print("=" * 80)
        print("")


if __name__ == "__main__":


    main()