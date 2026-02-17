#!/usr/bin/env python3
"""
Comprehensive Agent Chat History Assessment & Intent Fulfillment Analysis

Analyzes all agent chat histories, maps intents to fulfillment status,
and prioritizes unsatisfied intents according to TRIAGE and BAU protocols.

Tags: #ASSESSMENT #INTENT_FULFILLMENT #TRIAGE #BAU #PRIORITIZATION @JARVIS @LUMINA
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("AgentChatHistoryAssessment")


class PriorityLevel(Enum):
    """Priority levels for triage/BAU"""
    CRITICAL = "critical"  # Immediate action required (TRIAGE)
    HIGH = "high"  # High priority (TRIAGE)
    MEDIUM = "medium"  # Medium priority (BAU)
    LOW = "low"  # Low priority (BAU)
    BACKLOG = "backlog"  # Future consideration


class FulfillmentStatus(Enum):
    """Intent fulfillment status"""
    FULFILLED = "fulfilled"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    IN_PROGRESS = "in_progress"
    NOT_STARTED = "not_started"
    UNKNOWN = "unknown"
    OVERLOOKED = "overlooked"
    PENDING = "pending"


class AgentChatHistoryAssessment:
    """
    Comprehensive assessment of agent chat histories and intent fulfillment.

    Analyzes:
    - All agent chat sessions
    - Intent extraction and mapping
    - Fulfillment status tracking
    - TRIAGE/BAU prioritization
    - Work stack generation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize assessment system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        # Directories
        self.intent_dir = self.data_dir / "user_intents"
        self.chat_dir = self.data_dir / "syphon" / "cursor_agent_chat"
        self.sessions_dir = self.data_dir / "agent_chat_sessions"
        self.agent_sessions_dir = self.data_dir / "agent_sessions"
        self.r5_sessions_dir = self.project_root / "scripts" / "data" / "r5_living_matrix" / "sessions"

        # Output directory
        self.output_dir = self.data_dir / "agent_assessments"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🔍 Agent Chat History Assessment initialized")
        logger.info(f"   Intent data: {self.intent_dir}")
        logger.info(f"   Chat data: {self.chat_dir}")
        logger.info(f"   Output: {self.output_dir}")

    def load_intent_tracking(self) -> Dict[str, Any]:
        """Load intent fulfillment tracking data"""
        tracking_file = self.intent_dir / "intent_fulfillment_tracking.json"
        database_file = self.intent_dir / "intent_fulfillment_database.json"

        tracking_data = {}
        database_data = {}

        if tracking_file.exists():
            try:
                with open(tracking_file, encoding="utf-8") as f:
                    tracking_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load intent tracking: {e}")

        if database_file.exists():
            try:
                with open(database_file, encoding="utf-8") as f:
                    database_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load intent database: {e}")

        return {
            "tracking": tracking_data,
            "database": database_data
        }

    def discover_chat_histories(self) -> List[Path]:
        try:
            """Discover all agent chat history files"""
            histories = []

            # Cursor agent chat analyses
            if self.chat_dir.exists():
                for file in self.chat_dir.glob("*.json"):
                    histories.append(file)

            # Agent chat sessions
            if self.sessions_dir.exists():
                for file in self.sessions_dir.glob("*.json"):
                    histories.append(file)

            if self.agent_sessions_dir.exists():
                for file in self.agent_sessions_dir.glob("*.json"):
                    histories.append(file)

            # R5 living matrix sessions
            if self.r5_sessions_dir.exists():
                for file in self.r5_sessions_dir.glob("*.json"):
                    histories.append(file)

            logger.info(f"📊 Discovered {len(histories)} chat history files")
            return histories

        except Exception as e:
            self.logger.error(f"Error in discover_chat_histories: {e}", exc_info=True)
            raise
    def analyze_chat_history(self, history_path: Path) -> Dict[str, Any]:
        """Analyze a single chat history file"""
        try:
            with open(history_path, encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

            analysis = {
                "file": str(history_path),
                "timestamp": datetime.now().isoformat(),
                "intents_mentioned": [],
                "agents_involved": [],
                "requests": [],
                "completions": [],
                "errors": [],
                "tools_used": []
            }

            # Extract intents mentioned
            content_str = json.dumps(data, default=str)

            # Look for intent patterns
            intent_patterns = [
                r'intent[_\s]*(\d+)',
                r'@ASK',
                r'@DOIT',
                r'@TRIAGE',
                r'@BAU',
                r'@SLA',
                r'pm\d+',
                r'PM\d+',
                r'T\d+',
                r'CR-\d+'
            ]

            for pattern in intent_patterns:
                import re
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                analysis["intents_mentioned"].extend(matches)

            # Extract agents
            if isinstance(data, dict):
                if "agents" in data:
                    analysis["agents_involved"] = list(data["agents"].keys()) if isinstance(data["agents"], dict) else data["agents"]
                if "aggregated" in data and "agents" in data["aggregated"]:
                    analysis["agents_involved"] = list(data["aggregated"]["agents"].keys())

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {history_path}: {e}")
            return {
                "file": str(history_path),
                "error": str(e)
            }

    def map_intents_to_fulfillment(self, intent_data: Dict[str, Any], chat_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map intents to their fulfillment status from chat histories"""
        intent_mapping = {}

        # Get intents from tracking
        tracking = intent_data.get("tracking", {}).get("intents", {})
        database = intent_data.get("database", {}).get("fulfillments", {})

        all_intents = {}
        all_intents.update(tracking)
        all_intents.update(database)

        for intent_id, intent_info in all_intents.items():
            if isinstance(intent_info, dict):
                fulfillment_status = intent_info.get("fulfillment_status", "unknown")
                implementation_status = intent_info.get("implementation_status", "unknown")
                priority = intent_info.get("priority", "low")

                # Determine if satisfied
                is_satisfied = (
                    fulfillment_status in ["fulfilled", "completed"] or
                    implementation_status in ["completed", "fulfilled"]
                )

                # Check chat histories for evidence
                evidence = []
                for chat_analysis in chat_analyses:
                    if intent_id in str(chat_analysis.get("intents_mentioned", [])):
                        evidence.append({
                            "source": chat_analysis.get("file"),
                            "timestamp": chat_analysis.get("timestamp")
                        })

                intent_mapping[intent_id] = {
                    "intent_id": intent_id,
                    "intent_text": intent_info.get("intent_text", ""),
                    "fulfillment_status": fulfillment_status,
                    "implementation_status": implementation_status,
                    "priority": priority,
                    "is_satisfied": is_satisfied,
                    "related_asks": intent_info.get("related_asks", []),
                    "related_tickets": intent_info.get("related_tickets", []),
                    "fulfillment_evidence": intent_info.get("fulfillment_evidence", []) + evidence,
                    "repetition_count": intent_info.get("repetition_count", 1),
                    "first_seen": intent_info.get("first_seen"),
                    "last_seen": intent_info.get("last_seen")
                }

        return intent_mapping

    def prioritize_unsatisfied_intents(self, intent_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize unsatisfied intents according to TRIAGE/BAU"""
        unsatisfied = []

        for intent_id, intent_info in intent_mapping.items():
            if not intent_info.get("is_satisfied", False):
                unsatisfied.append(intent_info)

        # Prioritization logic
        def get_priority_score(intent: Dict[str, Any]) -> Tuple[int, str]:
            """Calculate priority score (higher = more urgent)"""
            score = 0
            priority_level = PriorityLevel.LOW

            # Priority from existing data
            existing_priority = intent.get("priority", "low").lower()
            if existing_priority == "critical":
                score += 100
                priority_level = PriorityLevel.CRITICAL
            elif existing_priority == "high":
                score += 50
                priority_level = PriorityLevel.HIGH
            elif existing_priority == "medium":
                score += 25
                priority_level = PriorityLevel.MEDIUM

            # Repetition count (more mentions = higher priority)
            repetition = intent.get("repetition_count", 1)
            score += min(repetition * 5, 30)

            # Related tickets/asks (more connections = higher priority)
            related_count = len(intent.get("related_tickets", [])) + len(intent.get("related_asks", []))
            score += min(related_count * 3, 20)

            # Status-based scoring
            status = intent.get("fulfillment_status", "unknown").lower()
            if status == "overlooked":
                score += 40
                if priority_level == PriorityLevel.LOW:
                    priority_level = PriorityLevel.HIGH
            elif status == "in_progress":
                score += 20
            elif status == "partially_completed":
                score += 15

            # Keywords indicating urgency
            intent_text = str(intent.get("intent_text", "")).lower()
            urgent_keywords = ["critical", "urgent", "immediate", "fix", "error", "broken", "required"]
            if any(kw in intent_text for kw in urgent_keywords):
                score += 30
                if priority_level.value in ["low", "medium"]:
                    priority_level = PriorityLevel.HIGH

            # TRIAGE indicators
            if "@TRIAGE" in intent_text or "triage" in intent_text:
                score += 50
                priority_level = PriorityLevel.CRITICAL if priority_level == PriorityLevel.LOW else PriorityLevel.HIGH

            # BAU indicators
            if "@BAU" in intent_text or "bau" in intent_text:
                score += 10
                if priority_level == PriorityLevel.LOW:
                    priority_level = PriorityLevel.MEDIUM

            return (score, priority_level.value)

        # Sort by priority score
        prioritized = sorted(unsatisfied, key=lambda x: get_priority_score(x)[0], reverse=True)

        # Add priority scores
        for intent in prioritized:
            score, priority = get_priority_score(intent)
            intent["priority_score"] = score
            intent["assigned_priority"] = priority

        return prioritized

    def generate_work_stack(self, prioritized_intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate prioritized work stack"""
        work_stack = {
            "generated_at": datetime.now().isoformat(),
            "total_unsatisfied": len(prioritized_intents),
            "by_priority": defaultdict(list),
            "work_items": []
        }

        for intent in prioritized_intents:
            priority = intent.get("assigned_priority", "low")
            work_stack["by_priority"][priority].append(intent)

            work_item = {
                "id": intent.get("intent_id"),
                "title": intent.get("intent_text", "")[:100],  # Truncate
                "priority": priority,
                "priority_score": intent.get("priority_score", 0),
                "status": intent.get("fulfillment_status", "unknown"),
                "related_tickets": intent.get("related_tickets", []),
                "related_asks": intent.get("related_asks", []),
                "repetition_count": intent.get("repetition_count", 1),
                "first_seen": intent.get("first_seen"),
                "last_seen": intent.get("last_seen")
            }
            work_stack["work_items"].append(work_item)

        return work_stack

    def run_comprehensive_assessment(self) -> Dict[str, Any]:
        try:
            """Run comprehensive assessment of all agent chat histories"""
            logger.info("🔍 Starting comprehensive agent chat history assessment...")

            # Load intent data
            logger.info("📊 Loading intent tracking data...")
            intent_data = self.load_intent_tracking()

            # Discover chat histories
            logger.info("📂 Discovering chat history files...")
            chat_histories = self.discover_chat_histories()

            # Analyze chat histories
            logger.info(f"🔬 Analyzing {len(chat_histories)} chat history files...")
            chat_analyses = []
            for i, history_path in enumerate(chat_histories, 1):
                if i % 10 == 0:
                    logger.info(f"   Progress: {i}/{len(chat_histories)}")
                analysis = self.analyze_chat_history(history_path)
                chat_analyses.append(analysis)

            # Map intents to fulfillment
            logger.info("🗺️  Mapping intents to fulfillment status...")
            intent_mapping = self.map_intents_to_fulfillment(intent_data, chat_analyses)

            # Prioritize unsatisfied intents
            logger.info("⚡ Prioritizing unsatisfied intents (TRIAGE/BAU)...")
            prioritized = self.prioritize_unsatisfied_intents(intent_mapping)

            # Generate work stack
            logger.info("📋 Generating prioritized work stack...")
            work_stack = self.generate_work_stack(prioritized)

            # Compile assessment report
            assessment = {
                "assessment_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_chat_histories": len(chat_histories),
                    "total_intents_analyzed": len(intent_mapping),
                    "unsatisfied_intents": len(prioritized),
                    "satisfied_intents": len(intent_mapping) - len(prioritized)
                },
                "intent_mapping": intent_mapping,
                "prioritized_work_stack": work_stack,
                "chat_analyses_summary": {
                    "total_analyses": len(chat_analyses),
                    "agents_found": list(set(
                        agent for analysis in chat_analyses
                        for agent in analysis.get("agents_involved", [])
                    ))
                }
            }

            # Save assessment
            output_file = self.output_dir / f"comprehensive_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(assessment, f, indent=2, default=str)

            logger.info(f"✅ Assessment complete: {output_file}")

            # Generate summary report
            self.generate_summary_report(assessment, output_file.parent / f"assessment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

            return assessment

        except Exception as e:
            self.logger.error(f"Error in run_comprehensive_assessment: {e}", exc_info=True)
            raise
    def generate_summary_report(self, assessment: Dict[str, Any], output_path: Path):
        try:
            """Generate markdown summary report"""
            lines = []
            lines.append("# Agent Chat History Comprehensive Assessment")
            lines.append("")
            lines.append(f"**Generated:** {assessment['assessment_metadata']['generated_at']}")
            lines.append("")
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Total Chat Histories Analyzed:** {assessment['assessment_metadata']['total_chat_histories']}")
            lines.append(f"- **Total Intents Analyzed:** {assessment['assessment_metadata']['total_intents_analyzed']}")
            lines.append(f"- **Satisfied Intents:** {assessment['assessment_metadata']['satisfied_intents']}")
            lines.append(f"- **Unsatisfied Intents:** {assessment['assessment_metadata']['unsatisfied_intents']}")
            lines.append("")

            # Prioritized work stack
            work_stack = assessment["prioritized_work_stack"]
            lines.append("## Prioritized Work Stack (TRIAGE/BAU)")
            lines.append("")

            for priority in ["critical", "high", "medium", "low", "backlog"]:
                items = work_stack["by_priority"].get(priority, [])
                if items:
                    lines.append(f"### {priority.upper()} Priority ({len(items)} items)")
                    lines.append("")
                    for item in items[:20]:  # Top 20 per priority
                        intent_id = item.get("intent_id", "unknown")
                        intent_text = item.get("intent_text", "")[:80]
                        score = item.get("priority_score", 0)
                        lines.append(f"- **{intent_id}** (Score: {score}): {intent_text}...")
                        if item.get("related_tickets"):
                            lines.append(f"  - Tickets: {', '.join(item['related_tickets'][:5])}")
                    lines.append("")

            # Top 20 overall
            lines.append("## Top 20 Highest Priority Items")
            lines.append("")
            top_items = work_stack["work_items"][:20]
            for i, item in enumerate(top_items, 1):
                lines.append(f"{i}. **{item['id']}** - {item['title']}")
                lines.append(f"   - Priority: {item['priority']} | Score: {item['priority_score']}")
                lines.append(f"   - Status: {item['status']}")
                if item.get("related_tickets"):
                    lines.append(f"   - Tickets: {', '.join(item['related_tickets'][:3])}")
                lines.append("")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info(f"📄 Summary report: {output_path}")


        except Exception as e:
            self.logger.error(f"Error in generate_summary_report: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    assessment = AgentChatHistoryAssessment()
    result = assessment.run_comprehensive_assessment()
    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE ASSESSMENT COMPLETE")
    print("=" * 80)
    print(f"\nTotal Intents: {result['assessment_metadata']['total_intents_analyzed']}")
    print(f"Unsatisfied: {result['assessment_metadata']['unsatisfied_intents']}")
    print(f"Satisfied: {result['assessment_metadata']['satisfied_intents']}")
    print(f"\nWork Stack Items: {len(result['prioritized_work_stack']['work_items'])}")
    print("\nTop 5 Priority Items:")
    for i, item in enumerate(result['prioritized_work_stack']['work_items'][:5], 1):
        print(f"  {i}. [{item['priority']}] {item['title'][:60]}...")
