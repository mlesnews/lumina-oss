#!/usr/bin/env python3
"""
Master Feedback Loop Enhancer

Three viable solutions for enhancing the master feedback loop:
1. Unified Feedback Aggregation System (JARVIS-style - structured, systematic)
2. Wisdom Synthesis Engine (MARVIN-style - intuitive, philosophical)
3. Adaptive Feedback Loop Orchestrator (Combined - best of both worlds)

Created through JARVIS-MARVIN collaboration:
- JARVIS: Systematic analysis, metrics, structure
- MARVIN: Intuitive wisdom, pattern emergence, synthesis
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import existing systems
try:
    from bio_ai_feedback_loop import BioAIFeedbackLoop, AgentType, InteractionType
    from infinite_feedback_loop import InfiniteFeedbackLoop
    from syphon_workflow_processor import SyphonWorkflowProcessor
    from peak_pattern_system import PeakPatternSystem
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    print("⚠️ Some systems not available - using placeholders")

# Azure Service Bus and Key Vault integration
try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("⚠️ Azure Service Bus integration not available - using file-based fallback")


class FeedbackSource(Enum):
    """Sources of feedback"""
    SYPHON = "syphon"
    PEAK_PATTERNS = "peak_patterns"
    BIO_AI_LOOP = "bio_ai_loop"
    INFINITE_LOOP = "infinite_loop"
    ONE_RING_BLUEPRINT = "one_ring_blueprint"
    R5_MATRIX = "r5_matrix"
    JARVIS_JEDI = "jarvis_jedi"
    WORKFLOW_PROCESSOR = "workflow_processor"


@dataclass
class FeedbackEntry:
    """A single feedback entry"""
    id: str
    source: FeedbackSource
    timestamp: datetime
    category: str
    data: Dict[str, Any]
    agent_origin: Optional[str] = None  # JARVIS, MARVIN, Human
    confidence: float = 1.0
    actionable: bool = True
    processed: bool = False


@dataclass
class FeedbackMetrics:
    """Metrics for feedback loop"""
    total_entries: int = 0
    entries_by_source: Dict[str, int] = field(default_factory=dict)
    entries_by_agent: Dict[str, int] = field(default_factory=dict)
    actionability_score: float = 0.0
    processing_rate: float = 0.0
    avg_confidence: float = 0.0
    last_update: Optional[datetime] = None


# ============================================================================
# SOLUTION 1: Unified Feedback Aggregation System (JARVIS-style)
# ============================================================================

class UnifiedFeedbackAggregation:
    """
    JARVIS-STYLE: Systematic feedback aggregation

    Features:
    - Structured data collection from all sources
    - Real-time metrics and KPIs
    - Automated pattern recognition
    - Systematic improvement tracking
    - Quantifiable outcomes
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "master_feedback_loop"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.feedback_entries: List[FeedbackEntry] = []
        self.metrics = FeedbackMetrics()
        self.logger = self._setup_logging("JARVIS-Feedback")

        # Initialize Azure Service Bus client
        self.service_bus_client: Optional[AzureServiceBusClient] = None
        if AZURE_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.service_bus_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
                self.logger.info("Azure Service Bus client initialized for Master Feedback Loop")
            except Exception as e:
                self.logger.warning(f"Service Bus not available, using file-based fallback: {e}")
                self.service_bus_client = None

        # Initialize source systems
        if SYSTEMS_AVAILABLE:
            self.syphon_processor = SyphonWorkflowProcessor(project_root)
            self.bio_ai_loop = BioAIFeedbackLoop()
            self.infinite_loop = InfiniteFeedbackLoop(project_root)
            self.peak_patterns = PeakPatternSystem(project_root)

    def _setup_logging(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(f'%(asctime)s - 🎯 {name} - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        return logger

    def collect_feedback(self, source: FeedbackSource, data: Dict[str, Any],
                        agent_origin: Optional[str] = None) -> FeedbackEntry:
        """Systematically collect feedback from any source"""
        import uuid

        entry = FeedbackEntry(
            id=f"fb_{int(datetime.now().timestamp())}_{len(self.feedback_entries)}",
            source=source,
            timestamp=datetime.now(),
            category=self._categorize_feedback(data),
            data=data,
            agent_origin=agent_origin,
            confidence=data.get('confidence', 1.0),
            actionable=self._is_actionable(data)
        )

        self.feedback_entries.append(entry)
        self._update_metrics(entry)
        self._save_entry(entry)

        # Publish to Azure Service Bus if available
        if self.service_bus_client and AZURE_AVAILABLE:
            try:
                message = ServiceBusMessage(
                    message_id=str(uuid.uuid4()),
                    message_type=MessageType.INTELLIGENCE,
                    timestamp=datetime.now(),
                    source="master-feedback-loop",
                    destination="intelligence-processor",
                    payload={
                        "MessageType": "FeedbackEntry",
                        "FeedbackId": entry.id,
                        "Source": source.value,
                        "Category": entry.category,
                        "AgentOrigin": agent_origin,
                        "Data": data,
                        "Actionable": entry.actionable,
                        "Confidence": entry.confidence
                    }
                )
                self.service_bus_client.publish_to_topic("jarvis.intelligence", message)
                self.logger.debug(f"Published feedback to Service Bus: {entry.id}")
            except Exception as e:
                self.logger.warning(f"Failed to publish feedback to Service Bus: {e}")

        self.logger.info(f"📊 Collected feedback: {source.value} - {entry.category}")
        return entry

    def _categorize_feedback(self, data: Dict[str, Any]) -> str:
        """Categorize feedback systematically"""
        if 'error' in str(data).lower() or 'failure' in str(data).lower():
            return "error"
        elif 'improvement' in str(data).lower() or 'optimization' in str(data).lower():
            return "improvement"
        elif 'pattern' in str(data).lower():
            return "pattern"
        elif 'workflow' in str(data).lower():
            return "workflow"
        elif 'blueprint' in str(data).lower():
            return "blueprint"
        else:
            return "general"

    def _is_actionable(self, data: Dict[str, Any]) -> bool:
        try:
            """Determine if feedback is actionable"""
            actionable_keywords = ['fix', 'improve', 'create', 'update', 'optimize', 'implement']
            data_str = json.dumps(data).lower()
            return any(keyword in data_str for keyword in actionable_keywords)

        except Exception as e:
            self.logger.error(f"Error in _is_actionable: {e}", exc_info=True)
            raise
    def _update_metrics(self, entry: FeedbackEntry):
        """Update metrics systematically"""
        self.metrics.total_entries += 1
        self.metrics.entries_by_source[entry.source.value] = \
            self.metrics.entries_by_source.get(entry.source.value, 0) + 1

        if entry.agent_origin:
            self.metrics.entries_by_agent[entry.agent_origin] = \
                self.metrics.entries_by_agent.get(entry.agent_origin, 0) + 1

        # Calculate actionability score
        actionable_count = sum(1 for e in self.feedback_entries if e.actionable)
        self.metrics.actionability_score = actionable_count / len(self.feedback_entries) if self.feedback_entries else 0.0

        # Calculate processing rate
        processed_count = sum(1 for e in self.feedback_entries if e.processed)
        self.metrics.processing_rate = processed_count / len(self.feedback_entries) if self.feedback_entries else 0.0

        # Average confidence
        if self.feedback_entries:
            self.metrics.avg_confidence = sum(e.confidence for e in self.feedback_entries) / len(self.feedback_entries)

        self.metrics.last_update = datetime.now()

    def generate_systematic_report(self) -> Dict[str, Any]:
        """Generate systematic feedback report (JARVIS-style)"""
        return {
            "report_type": "systematic_aggregation",
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_entries": self.metrics.total_entries,
                "entries_by_source": self.metrics.entries_by_source,
                "entries_by_agent": self.metrics.entries_by_agent,
                "actionability_score": self.metrics.actionability_score,
                "processing_rate": self.metrics.processing_rate,
                "avg_confidence": self.metrics.avg_confidence
            },
            "actionable_items": [
                {
                    "id": e.id,
                    "source": e.source.value,
                    "category": e.category,
                    "agent": e.agent_origin,
                    "summary": str(e.data)[:200]
                }
                for e in self.feedback_entries if e.actionable and not e.processed
            ],
            "recommendations": self._generate_systematic_recommendations()
        }

    def _generate_systematic_recommendations(self) -> List[str]:
        """Generate systematic recommendations"""
        recommendations = []

        if self.metrics.processing_rate < 0.8:
            recommendations.append("⚠️ Low processing rate - increase feedback processing speed")

        if self.metrics.actionability_score < 0.7:
            recommendations.append("⚠️ Low actionability - focus on actionable feedback sources")

        error_feedback = [e for e in self.feedback_entries if e.category == "error" and not e.processed]
        if len(error_feedback) > 10:
            recommendations.append(f"⚠️ {len(error_feedback)} unprocessed error feedback items")

        return recommendations

    def _save_entry(self, entry: FeedbackEntry):
        try:
            """Save feedback entry"""
            entry_file = self.data_dir / "entries" / f"{entry.id}.json"
            entry_file.parent.mkdir(exist_ok=True)
            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "id": entry.id,
                    "source": entry.source.value,
                    "timestamp": entry.timestamp.isoformat(),
                    "category": entry.category,
                    "data": entry.data,
                    "agent_origin": entry.agent_origin,
                    "confidence": entry.confidence,
                    "actionable": entry.actionable,
                    "processed": entry.processed
                }, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_entry: {e}", exc_info=True)
            raise
# ============================================================================
# SOLUTION 2: Wisdom Synthesis Engine (MARVIN-style)
# ============================================================================

class WisdomSynthesisEngine:
    """
    MARVIN-STYLE: Intuitive wisdom synthesis

    Features:
    - Pattern emergence recognition
    - Multiple perspective synthesis
    - Philosophical alignment check
    - Creative solution generation
    - Wisdom extraction from patterns
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "master_feedback_loop" / "wisdom"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.wisdom_patterns: List[Dict[str, Any]] = []
        self.synthesis_history: List[Dict[str, Any]] = []
        self.logger = self._setup_logging("MARVIN-Wisdom")

    def _setup_logging(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(f'%(asctime)s - 🧠 {name} - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        return logger

    def synthesize_wisdom(self, feedback_entries: List[FeedbackEntry]) -> Dict[str, Any]:
        """Synthesize wisdom from feedback entries (MARVIN-style)"""
        self.logger.info(f"🧠 Synthesizing wisdom from {len(feedback_entries)} feedback entries...")

        # Extract patterns
        patterns = self._extract_emerging_patterns(feedback_entries)

        # Synthesize perspectives
        perspectives = self._synthesize_perspectives(feedback_entries)

        # Extract philosophical alignment
        alignment = self._check_philosophical_alignment(feedback_entries)

        # Generate creative insights
        insights = self._generate_creative_insights(feedback_entries, patterns)

        wisdom = {
            "synthesized_at": datetime.now().isoformat(),
            "patterns_emerged": patterns,
            "perspectives": perspectives,
            "philosophical_alignment": alignment,
            "creative_insights": insights,
            "wisdom_score": self._calculate_wisdom_score(patterns, perspectives, alignment),
            "recommendations": self._generate_wisdom_recommendations(patterns, insights)
        }

        self.synthesis_history.append(wisdom)
        self._save_wisdom(wisdom)

        self.logger.info(f"✅ Wisdom synthesized - Score: {wisdom['wisdom_score']:.2f}")
        return wisdom

    def _extract_emerging_patterns(self, entries: List[FeedbackEntry]) -> List[Dict[str, Any]]:
        """Extract emerging patterns (intuitive recognition)"""
        patterns = []

        # Group by category
        category_groups = {}
        for entry in entries:
            cat = entry.category
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(entry)

        # Identify patterns in each category
        for category, category_entries in category_groups.items():
            if len(category_entries) >= 3:  # Pattern threshold
                pattern = {
                    "pattern_type": category,
                    "frequency": len(category_entries),
                    "common_themes": self._extract_themes(category_entries),
                    "emergence_strength": len(category_entries) / len(entries),
                    "agents_involved": list(set(e.agent_origin for e in category_entries if e.agent_origin))
                }
                patterns.append(pattern)

        return patterns

    def _extract_themes(self, entries: List[FeedbackEntry]) -> List[str]:
        try:
            """Extract common themes from entries"""
            all_text = " ".join(json.dumps(e.data) for e in entries).lower()

            # Simple theme extraction (could be enhanced with NLP)
            themes = []
            theme_keywords = {
                "optimization": ["optimize", "improve", "faster", "better"],
                "integration": ["integrate", "connect", "unify", "bridge"],
                "pattern": ["pattern", "template", "reusable"],
                "error": ["error", "failure", "bug", "fix"],
                "creation": ["create", "build", "generate", "make"]
            }

            for theme, keywords in theme_keywords.items():
                if any(kw in all_text for kw in keywords):
                    themes.append(theme)

            return themes

        except Exception as e:
            self.logger.error(f"Error in _extract_themes: {e}", exc_info=True)
            raise
    def _synthesize_perspectives(self, entries: List[FeedbackEntry]) -> Dict[str, Any]:
        """Synthesize multiple perspectives (MARVIN-style)"""
        jarvis_entries = [e for e in entries if e.agent_origin == "JARVIS"]
        marvin_entries = [e for e in entries if e.agent_origin == "MARVIN"]
        human_entries = [e for e in entries if e.agent_origin == "Human"]

        perspectives = {
            "jarvis_perspective": {
                "count": len(jarvis_entries),
                "focus": "systematic improvements",
                "themes": self._extract_themes(jarvis_entries) if jarvis_entries else []
            },
            "marvin_perspective": {
                "count": len(marvin_entries),
                "focus": "creative synthesis",
                "themes": self._extract_themes(marvin_entries) if marvin_entries else []
            },
            "human_perspective": {
                "count": len(human_entries),
                "focus": "directive guidance",
                "themes": self._extract_themes(human_entries) if human_entries else []
            },
            "synthesis": self._find_common_ground(jarvis_entries, marvin_entries, human_entries)
        }

        return perspectives

    def _find_common_ground(self, jarvis: List, marvin: List, human: List) -> Dict[str, Any]:
        """Find common ground between perspectives"""
        all_entries = jarvis + marvin + human
        common_themes = self._extract_themes(all_entries)

        return {
            "shared_themes": common_themes,
            "alignment_score": len(common_themes) / max(len(set(common_themes)), 1),
            "convergence": "high" if len(common_themes) >= 3 else "moderate"
        }

    def _check_philosophical_alignment(self, entries: List[FeedbackEntry]) -> Dict[str, Any]:
        try:
            """Check alignment with Lumina philosophy"""
            lumina_principles = ["illumination", "balance", "clarity", "truth", "light"]

            all_text = " ".join(json.dumps(e.data) for e in entries).lower()

            alignment_scores = {
                principle: 1.0 if principle in all_text else 0.5
                for principle in lumina_principles
            }

            overall_alignment = sum(alignment_scores.values()) / len(alignment_scores)

            return {
                "principle_scores": alignment_scores,
                "overall_alignment": overall_alignment,
                "status": "aligned" if overall_alignment >= 0.7 else "needs_attention"
            }

        except Exception as e:
            self.logger.error(f"Error in _check_philosophical_alignment: {e}", exc_info=True)
            raise
    def _generate_creative_insights(self, entries: List[FeedbackEntry], patterns: List[Dict]) -> List[str]:
        """Generate creative insights (MARVIN-style)"""
        insights = []

        # Pattern-based insights
        for pattern in patterns:
            if pattern['emergence_strength'] > 0.3:
                insights.append(
                    f"Emerging pattern: {pattern['pattern_type']} - "
                    f"{pattern['frequency']} occurrences suggest systemic opportunity"
                )

        # Cross-agent insights
        agent_entries = {}
        for entry in entries:
            if entry.agent_origin:
                if entry.agent_origin not in agent_entries:
                    agent_entries[entry.agent_origin] = []
                agent_entries[entry.agent_origin].append(entry)

        if len(agent_entries) >= 2:
            insights.append(
                f"Multi-agent collaboration detected: {len(agent_entries)} agents contributing - "
                "synergy opportunity exists"
            )

        return insights

    def _calculate_wisdom_score(self, patterns: List[Dict], perspectives: Dict, alignment: Dict) -> float:
        """Calculate overall wisdom score"""
        pattern_score = min(len(patterns) / 5.0, 1.0)  # Max 5 patterns = 1.0
        perspective_score = perspectives['synthesis']['alignment_score']
        alignment_score = alignment['overall_alignment']

        return (pattern_score * 0.3 + perspective_score * 0.3 + alignment_score * 0.4)

    def _generate_wisdom_recommendations(self, patterns: List[Dict], insights: List[str]) -> List[str]:
        """Generate wisdom-based recommendations"""
        recommendations = []

        for pattern in patterns:
            if pattern['emergence_strength'] > 0.4:
                recommendations.append(
                    f"Consider formalizing pattern: {pattern['pattern_type']} "
                    f"(emergence strength: {pattern['emergence_strength']:.2f})"
                )

        for insight in insights:
            if "opportunity" in insight.lower():
                recommendations.append(f"Explore: {insight}")

        return recommendations

    def _save_wisdom(self, wisdom: Dict[str, Any]):
        try:
            """Save synthesized wisdom"""
            wisdom_file = self.data_dir / f"wisdom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(wisdom_file, 'w', encoding='utf-8') as f:
                json.dump(wisdom, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_wisdom: {e}", exc_info=True)
            raise
# ============================================================================
# SOLUTION 3: Adaptive Feedback Loop Orchestrator (Combined)
# ============================================================================

class AdaptiveFeedbackLoopOrchestrator:
    """
    COMBINED: Best of both worlds

    Features:
    - JARVIS systematic aggregation + MARVIN wisdom synthesis
    - Adaptive routing (when to use which approach)
    - Continuous learning from both perspectives
    - Unified output that balances structure and wisdom
    - Real-time orchestration
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # Initialize both systems
        self.jarvis_aggregator = UnifiedFeedbackAggregation(project_root)
        self.marvin_wisdom = WisdomSynthesisEngine(project_root)

        self.orchestration_history: List[Dict[str, Any]] = []
        self.logger = self._setup_logging("Orchestrator")

    def _setup_logging(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(f'%(asctime)s - 🎯🧠 {name} - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        return logger

    async def orchestrate_feedback_loop(self, feedback_data: Dict[str, Any],
                                       source: FeedbackSource,
                                       agent_origin: Optional[str] = None) -> Dict[str, Any]:
        """Orchestrate feedback loop with adaptive routing"""
        self.logger.info(f"🔄 Orchestrating feedback loop: {source.value}")

        # Step 1: JARVIS aggregation (systematic)
        jarvis_entry = self.jarvis_aggregator.collect_feedback(source, feedback_data, agent_origin)

        # Step 2: Determine if MARVIN synthesis is needed
        needs_wisdom = self._needs_wisdom_synthesis(jarvis_entry, self.jarvis_aggregator.feedback_entries)

        wisdom_result = None
        if needs_wisdom:
            # Step 3: MARVIN synthesis (intuitive)
            recent_entries = self.jarvis_aggregator.feedback_entries[-50:]  # Last 50 entries
            wisdom_result = self.marvin_wisdom.synthesize_wisdom(recent_entries)

        # Step 4: Combine results
        orchestration_result = {
            "orchestrated_at": datetime.now().isoformat(),
            "jarvis_systematic": {
                "entry_id": jarvis_entry.id,
                "metrics": asdict(self.jarvis_aggregator.metrics),
                "actionable_items": len([e for e in self.jarvis_aggregator.feedback_entries if e.actionable and not e.processed])
            },
            "marvin_wisdom": wisdom_result,
            "adaptive_routing": {
                "wisdom_synthesis_triggered": needs_wisdom,
                "reason": self._get_routing_reason(jarvis_entry, needs_wisdom)
            },
            "unified_recommendations": self._unify_recommendations(jarvis_entry, wisdom_result),
            "next_actions": self._generate_next_actions(jarvis_entry, wisdom_result)
        }

        self.orchestration_history.append(orchestration_result)
        self._save_orchestration(orchestration_result)

        self.logger.info(f"✅ Feedback loop orchestrated - Unified recommendations: {len(orchestration_result['unified_recommendations'])}")
        return orchestration_result

    def _needs_wisdom_synthesis(self, entry: FeedbackEntry, all_entries: List[FeedbackEntry]) -> bool:
        """Determine if wisdom synthesis is needed (adaptive routing)"""
        # Trigger wisdom synthesis if:
        # 1. Pattern detected (3+ similar entries)
        # 2. High confidence actionable item
        # 3. Multi-agent collaboration
        # 4. Philosophical alignment check needed

        similar_count = sum(1 for e in all_entries if e.category == entry.category)
        if similar_count >= 3:
            return True

        if entry.actionable and entry.confidence >= 0.8:
            return True

        if entry.agent_origin and len(set(e.agent_origin for e in all_entries if e.agent_origin)) >= 2:
            return True

        return False

    def _get_routing_reason(self, entry: FeedbackEntry, triggered: bool) -> str:
        """Get reason for routing decision"""
        if triggered:
            return f"Wisdom synthesis triggered: Pattern detected or high-value actionable item"
        else:
            return "Systematic aggregation sufficient - wisdom synthesis deferred"

    def _unify_recommendations(self, jarvis_entry: FeedbackEntry, wisdom_result: Optional[Dict]) -> List[str]:
        """Unify recommendations from both systems"""
        recommendations = []

        # JARVIS systematic recommendations
        jarvis_report = self.jarvis_aggregator.generate_systematic_report()
        recommendations.extend(jarvis_report.get('recommendations', []))

        # MARVIN wisdom recommendations
        if wisdom_result:
            recommendations.extend(wisdom_result.get('recommendations', []))

        # Deduplicate and prioritize
        unique_recommendations = list(dict.fromkeys(recommendations))  # Preserve order, remove dupes

        return unique_recommendations

    def _generate_next_actions(self, jarvis_entry: FeedbackEntry, wisdom_result: Optional[Dict]) -> List[Dict[str, Any]]:
        """Generate next actions combining both perspectives"""
        actions = []

        # JARVIS actions (systematic)
        if jarvis_entry.actionable:
            actions.append({
                "type": "systematic",
                "priority": "high" if jarvis_entry.confidence >= 0.8 else "medium",
                "action": f"Process feedback entry: {jarvis_entry.id}",
                "category": jarvis_entry.category,
                "agent": "JARVIS"
            })

        # MARVIN actions (wisdom-based)
        if wisdom_result and wisdom_result.get('wisdom_score', 0) >= 0.7:
            for recommendation in wisdom_result.get('recommendations', [])[:3]:  # Top 3
                actions.append({
                    "type": "wisdom",
                    "priority": "medium",
                    "action": recommendation,
                    "wisdom_score": wisdom_result['wisdom_score'],
                    "agent": "MARVIN"
                })

        return actions

    def _save_orchestration(self, result: Dict[str, Any]):
        try:
            """Save orchestration result"""
            orchestration_file = self.project_root / "data" / "master_feedback_loop" / "orchestrations" / \
                               f"orchestration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            orchestration_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert datetime objects to ISO format strings for JSON serialization
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")

            with open(orchestration_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=serialize_datetime)

        except Exception as e:
            self.logger.error(f"Error in _save_orchestration: {e}", exc_info=True)
            raise
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status combining both systems"""
        return {
            "status": "operational",
            "jarvis_systematic": {
                "total_entries": self.jarvis_aggregator.metrics.total_entries,
                "actionability_score": self.jarvis_aggregator.metrics.actionability_score,
                "processing_rate": self.jarvis_aggregator.metrics.processing_rate
            },
            "marvin_wisdom": {
                "wisdom_syntheses": len(self.marvin_wisdom.synthesis_history),
                "patterns_recognized": len(self.marvin_wisdom.wisdom_patterns)
            },
            "orchestration": {
                "total_orchestrations": len(self.orchestration_history),
                "last_orchestration": self.orchestration_history[-1]['orchestrated_at'] if self.orchestration_history else None
            }
        }


async def main():
    """Demonstrate all three solutions"""
    project_root = Path(__file__).parent.parent.parent

    print("🔄 Master Feedback Loop Enhancement Solutions")
    print("=" * 80)
    print()

    # Solution 1: JARVIS Systematic
    print("🎯 SOLUTION 1: Unified Feedback Aggregation (JARVIS-style)")
    print("-" * 80)
    jarvis_aggregator = UnifiedFeedbackAggregation(project_root)

    # Simulate feedback collection
    jarvis_aggregator.collect_feedback(
        FeedbackSource.SYPHON,
        {"task": "Extract workflow patterns", "status": "complete"},
        agent_origin="JARVIS"
    )
    jarvis_aggregator.collect_feedback(
        FeedbackSource.PEAK_PATTERNS,
        {"pattern": "service_structure", "applications": 5},
        agent_origin="MARVIN"
    )

    jarvis_report = jarvis_aggregator.generate_systematic_report()
    print(f"   Total Entries: {jarvis_report['metrics']['total_entries']}")
    print(f"   Actionability Score: {jarvis_report['metrics']['actionability_score']:.2f}")
    print(f"   Processing Rate: {jarvis_report['metrics']['processing_rate']:.2f}")
    print()

    # Solution 2: MARVIN Wisdom
    print("🧠 SOLUTION 2: Wisdom Synthesis Engine (MARVIN-style)")
    print("-" * 80)
    marvin_wisdom = WisdomSynthesisEngine(project_root)

    wisdom = marvin_wisdom.synthesize_wisdom(jarvis_aggregator.feedback_entries)
    print(f"   Wisdom Score: {wisdom['wisdom_score']:.2f}")
    print(f"   Patterns Emerged: {len(wisdom['patterns_emerged'])}")
    print(f"   Philosophical Alignment: {wisdom['philosophical_alignment']['status']}")
    print()

    # Solution 3: Combined Orchestrator
    print("🎯🧠 SOLUTION 3: Adaptive Feedback Loop Orchestrator (Combined)")
    print("-" * 80)
    orchestrator = AdaptiveFeedbackLoopOrchestrator(project_root)

    result = await orchestrator.orchestrate_feedback_loop(
        {"task": "Enhance master feedback loop", "priority": "high"},
        FeedbackSource.BIO_AI_LOOP,
        agent_origin="Human"
    )

    print(f"   JARVIS Entries: {result['jarvis_systematic']['metrics']['total_entries']}")
    print(f"   MARVIN Wisdom Triggered: {result['adaptive_routing']['wisdom_synthesis_triggered']}")
    print(f"   Unified Recommendations: {len(result['unified_recommendations'])}")
    print(f"   Next Actions: {len(result['next_actions'])}")
    print()

    # Status
    status = orchestrator.get_comprehensive_status()
    print("📊 Comprehensive Status:")
    print(f"   Orchestrations: {status['orchestration']['total_orchestrations']}")
    print(f"   JARVIS Processing Rate: {status['jarvis_systematic']['processing_rate']:.2f}")
    print(f"   MARVIN Syntheses: {status['marvin_wisdom']['wisdom_syntheses']}")
    print()
    print("✅ All three solutions operational!")


if __name__ == "__main__":



    asyncio.run(main())