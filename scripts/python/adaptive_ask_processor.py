#!/usr/bin/env python3
"""
Adaptive Ask Processor - Context-Aware Ask Processing System

Processes @asks adaptively based on context, perspective, and situation.
Switches between chronological and triage views dynamically.
Learns and adapts based on performance and collaboration patterns.

Tags: #ADAPTIVE #CONTEXT_AWARE #LEARNING #COLLABORATION @JARVIS @LUMINA @AIQ
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from collections import defaultdict
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("AdaptiveAskProcessor")


class ProcessingMode(Enum):
    """Processing modes for asks"""
    CHRONOLOGICAL = "chronological"  # Natural flow, as discovered
    TRIAGE = "triage"  # Prioritized by importance
    DEPENDENCY = "dependency"  # By dependencies/blockers
    CATEGORY = "category"  # Grouped by category
    CONTEXT = "context"  # Based on current workflow context


class CollaborationContext(Enum):
    """Current collaboration context"""
    REVIEW = "review"  # Reviewing/auditing - use chronological
    EXECUTION = "execution"  # Executing tasks - use triage
    PLANNING = "planning"  # Planning - use dependency view
    DISCOVERY = "discovery"  # Discovering - use category view
    COLLABORATION = "collaboration"  # Active collaboration - adaptive


@dataclass
class PerformanceMetrics:
    """Performance metrics for collaboration"""
    individual_ai_performance: float = 0.0
    individual_human_performance: float = 0.0
    collaborative_performance: float = 0.0
    decision_quality: float = 0.0
    step_completion_rate: float = 0.0
    repetition_count: int = 0
    learned_patterns: int = 0
    last_updated: str = ""


@dataclass
class AskPattern:
    """Pattern learned from asks"""
    pattern_id: str
    pattern_text: str
    frequency: int
    success_rate: float
    context: str
    learned_at: str
    last_seen: str


class AdaptiveAskProcessor:
    """
    Adaptive Ask Processor - Context-Aware Processing

    Adapts to current workflow context, learns from performance,
    and prevents repetition through pattern matching.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize adaptive ask processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.adaptive_dir = self.data_dir / "adaptive_ask_processor"
        self.adaptive_dir.mkdir(parents=True, exist_ok=True)

        # Current context
        self.current_context: CollaborationContext = CollaborationContext.COLLABORATION
        self.current_mode: ProcessingMode = ProcessingMode.TRIAGE

        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.metrics_file = self.adaptive_dir / "performance_metrics.json"

        # Pattern matching
        self.patterns: List[AskPattern] = []
        self.patterns_file = self.adaptive_dir / "learned_patterns.json"

        # Ask database (cross-indexed)
        self.ask_database: List[Dict[str, Any]] = []
        self.database_file = self.adaptive_dir / "ask_database.json"

        # Load existing data
        self._load_metrics()
        self._load_patterns()
        self._load_database()

        logger.info("=" * 80)
        logger.info("🔄 ADAPTIVE ASK PROCESSOR INITIALIZED")
        logger.info(f"   Context: {self.current_context.value}")
        logger.info(f"   Mode: {self.current_mode.value}")
        logger.info("=" * 80)

    def _load_metrics(self):
        """Load performance metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = PerformanceMetrics(**data)
                    logger.info(f"✅ Loaded performance metrics")
            except Exception as e:
                logger.warning(f"⚠️  Error loading metrics: {e}")

    def _save_metrics(self):
        """Save performance metrics"""
        try:
            self.metrics.last_updated = datetime.now().isoformat()
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.metrics), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Error saving metrics: {e}")

    def _load_patterns(self):
        """Load learned patterns"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = [AskPattern(**p) for p in data.get("patterns", [])]
                    logger.info(f"✅ Loaded {len(self.patterns)} learned patterns")
            except Exception as e:
                logger.warning(f"⚠️  Error loading patterns: {e}")

    def _save_patterns(self):
        """Save learned patterns"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "patterns": [asdict(p) for p in self.patterns],
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Error saving patterns: {e}")

    def _load_database(self):
        """Load ask database"""
        if self.database_file.exists():
            try:
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ask_database = data.get("asks", [])
                    logger.info(f"✅ Loaded {len(self.ask_database)} asks from database")
            except Exception as e:
                logger.warning(f"⚠️  Error loading database: {e}")

    def _save_database(self):
        """Save ask database"""
        try:
            with open(self.database_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "asks": self.ask_database,
                    "last_updated": datetime.now().isoformat(),
                    "total_asks": len(self.ask_database)
                }, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"⚠️  Error saving database: {e}")

    def detect_context(self, activity: Optional[str] = None) -> CollaborationContext:
        """
        Detect current collaboration context

        Args:
            activity: Current activity description

        Returns:
            Detected collaboration context
        """
        # Simple context detection (can be enhanced with ML)
        if activity:
            activity_lower = activity.lower()
            if any(word in activity_lower for word in ["review", "audit", "check", "examine"]):
                return CollaborationContext.REVIEW
            elif any(word in activity_lower for word in ["execute", "run", "do", "implement"]):
                return CollaborationContext.EXECUTION
            elif any(word in activity_lower for word in ["plan", "design", "architect"]):
                return CollaborationContext.PLANNING
            elif any(word in activity_lower for word in ["discover", "explore", "find"]):
                return CollaborationContext.DISCOVERY

        # Default to collaboration (adaptive)
        return CollaborationContext.COLLABORATION

    def select_mode(self, context: CollaborationContext) -> ProcessingMode:
        """
        Select processing mode based on context

        Args:
            context: Current collaboration context

        Returns:
            Appropriate processing mode
        """
        mode_mapping = {
            CollaborationContext.REVIEW: ProcessingMode.CHRONOLOGICAL,
            CollaborationContext.EXECUTION: ProcessingMode.TRIAGE,
            CollaborationContext.PLANNING: ProcessingMode.DEPENDENCY,
            CollaborationContext.DISCOVERY: ProcessingMode.CATEGORY,
            CollaborationContext.COLLABORATION: ProcessingMode.CONTEXT
        }

        selected_mode = mode_mapping.get(context, ProcessingMode.TRIAGE)
        logger.info(f"📊 Context: {context.value} → Mode: {selected_mode.value}")
        return selected_mode

    def process_asks_adaptively(
        self,
        asks: List[Dict[str, Any]],
        context: Optional[CollaborationContext] = None,
        activity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process asks adaptively based on context

        Args:
            asks: List of asks to process
            context: Collaboration context (auto-detected if not provided)
            activity: Current activity description

        Returns:
            Processed asks in appropriate order
        """
        # Detect context if not provided
        if context is None:
            context = self.detect_context(activity)

        self.current_context = context

        # Select mode
        mode = self.select_mode(context)
        self.current_mode = mode

        # Check for patterns (prevent repetition)
        filtered_asks = self._filter_repetitive_asks(asks)

        # Process based on mode
        if mode == ProcessingMode.CHRONOLOGICAL:
            return self._process_chronological(filtered_asks)
        elif mode == ProcessingMode.TRIAGE:
            return self._process_triage(filtered_asks)
        elif mode == ProcessingMode.DEPENDENCY:
            return self._process_dependency(filtered_asks)
        elif mode == ProcessingMode.CATEGORY:
            return self._process_category(filtered_asks)
        elif mode == ProcessingMode.CONTEXT:
            return self._process_context_aware(filtered_asks)
        else:
            return filtered_asks

    def _filter_repetitive_asks(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out repetitive asks using pattern matching"""
        filtered = []
        for ask in asks:
            ask_text = ask.get('ask_text', ask.get('text', ''))

            # Check against learned patterns
            is_repetitive = False
            for pattern in self.patterns:
                similarity = self._calculate_similarity(ask_text, pattern.pattern_text)
                if similarity > 0.85:  # 85% similarity threshold
                    is_repetitive = True
                    pattern.frequency += 1
                    pattern.last_seen = datetime.now().isoformat()
                    logger.info(f"⚠️  Repetitive ask detected (similarity: {similarity:.2f}): {ask_text[:50]}...")
                    self.metrics.repetition_count += 1
                    break

            if not is_repetitive:
                filtered.append(ask)

        if len(filtered) < len(asks):
            logger.info(f"🔍 Filtered {len(asks) - len(filtered)} repetitive asks")

        return filtered

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple implementation)"""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _process_chronological(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process asks in chronological order"""
        return sorted(asks, key=lambda x: x.get('timestamp', ''))

    def _process_triage(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process asks with triage prioritization"""
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'normal': 3, 'low': 4}
        return sorted(asks, key=lambda x: (
            priority_order.get(x.get('priority', 'normal'), 3),
            x.get('timestamp', '')
        ))

    def _process_dependency(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process asks by dependencies"""
        # Group by dependencies
        no_deps = [a for a in asks if not a.get('dependencies')]
        with_deps = [a for a in asks if a.get('dependencies')]

        # Sort with_deps by number of dependencies (fewer deps first)
        with_deps.sort(key=lambda x: len(x.get('dependencies', [])))

        return no_deps + with_deps

    def _process_category(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process asks by category"""
        by_category = defaultdict(list)
        for ask in asks:
            category = ask.get('category', 'general')
            by_category[category].append(ask)

        # Return grouped by category
        result = []
        for category, category_asks in sorted(by_category.items()):
            result.extend(category_asks)
        return result

    def _process_context_aware(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process asks with context awareness (adaptive)"""
        # Start with triage, but adapt based on performance
        if self.metrics.collaborative_performance > 0.8:
            # High performance - use triage for efficiency
            return self._process_triage(asks)
        else:
            # Lower performance - use chronological for clarity
            return self._process_chronological(asks)

    def learn_pattern(self, ask_text: str, success: bool, context: str = ""):
        """Learn a pattern from an ask"""
        # Check if similar pattern exists
        existing_pattern = None
        for pattern in self.patterns:
            similarity = self._calculate_similarity(ask_text, pattern.pattern_text)
            if similarity > 0.85:
                existing_pattern = pattern
                break

        if existing_pattern:
            # Update existing pattern
            existing_pattern.frequency += 1
            existing_pattern.last_seen = datetime.now().isoformat()
            if success:
                existing_pattern.success_rate = (
                    (existing_pattern.success_rate * (existing_pattern.frequency - 1) + 1.0) /
                    existing_pattern.frequency
                )
            else:
                existing_pattern.success_rate = (
                    (existing_pattern.success_rate * (existing_pattern.frequency - 1) + 0.0) /
                    existing_pattern.frequency
                )
        else:
            # Create new pattern
            new_pattern = AskPattern(
                pattern_id=f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                pattern_text=ask_text,
                frequency=1,
                success_rate=1.0 if success else 0.0,
                context=context,
                learned_at=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat()
            )
            self.patterns.append(new_pattern)
            self.metrics.learned_patterns += 1

        self._save_patterns()
        logger.info(f"📚 Learned pattern: {ask_text[:50]}... (success: {success})")

    def update_performance(
        self,
        ai_performance: Optional[float] = None,
        human_performance: Optional[float] = None,
        collaborative_performance: Optional[float] = None,
        decision_quality: Optional[float] = None,
        step_completion: Optional[float] = None
    ):
        """Update performance metrics"""
        if ai_performance is not None:
            self.metrics.individual_ai_performance = ai_performance
        if human_performance is not None:
            self.metrics.individual_human_performance = human_performance
        if collaborative_performance is not None:
            self.metrics.collaborative_performance = collaborative_performance
        if decision_quality is not None:
            self.metrics.decision_quality = decision_quality
        if step_completion is not None:
            self.metrics.step_completion_rate = step_completion

        self._save_metrics()
        logger.info("📊 Performance metrics updated")

    def get_reminders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get reminders for partial/incomplete items

        Returns:
            List of items that need reminders
        """
        reminders = []

        # Check database for partial completions
        for ask in self.ask_database:
            status = ask.get('status', 'pending')
            if status in ['partial', 'in_progress']:
                reminders.append({
                    'type': 'partial_completion',
                    'ask': ask,
                    'message': f"Reminder: {ask.get('ask_text', '')[:50]}... is partially completed"
                })

        # Check for missing steps (if we have step tracking)
        # This would be enhanced with workflow step tracking

        return reminders[:limit]

    def query_database(
        self,
        query_type: str = "all",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query ask database with filters

        Args:
            query_type: Type of query (all, by_priority, by_category, by_status, etc.)
            filters: Additional filters to apply

        Returns:
            Filtered asks
        """
        results = self.ask_database.copy()

        if filters:
            for key, value in filters.items():
                results = [a for a in results if a.get(key) == value]

        if query_type == "by_priority":
            priority = filters.get('priority') if filters else None
            if priority:
                results = [a for a in results if a.get('priority') == priority]

        elif query_type == "by_category":
            category = filters.get('category') if filters else None
            if category:
                results = [a for a in results if a.get('category') == category]

        elif query_type == "by_status":
            status = filters.get('status') if filters else None
            if status:
                results = [a for a in results if a.get('status') == status]

        logger.info(f"🔍 Query: {query_type} returned {len(results)} results")
        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Adaptive Ask Processor - Context-Aware Processing")
    parser.add_argument('--context', type=str, help='Set collaboration context (review, execution, planning, discovery)')
    parser.add_argument('--activity', type=str, help='Current activity description')
    parser.add_argument('--query', type=str, help='Query type (all, by_priority, by_category, by_status)')
    parser.add_argument('--reminders', action='store_true', help='Show reminders')

    args = parser.parse_args()

    processor = AdaptiveAskProcessor()

    if args.reminders:
        reminders = processor.get_reminders()
        print("\n📋 REMINDERS:")
        print("=" * 80)
        for reminder in reminders:
            print(f"   • {reminder['message']}")

    elif args.query:
        filters = {}
        if args.context:
            filters['context'] = args.context
        results = processor.query_database(args.query, filters)
        print(f"\n🔍 Query Results: {len(results)} asks")
        for ask in results[:10]:
            print(f"   • {ask.get('ask_text', '')[:70]}...")

    else:
        print("🔄 Adaptive Ask Processor")
        print("\nUsage:")
        print("  --context CONTEXT    Set collaboration context")
        print("  --activity ACTIVITY  Describe current activity")
        print("  --query TYPE         Query database")
        print("  --reminders          Show reminders")


if __name__ == "__main__":


    main()