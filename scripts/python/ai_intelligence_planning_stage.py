#!/usr/bin/env python3
"""
AI Intelligence Planning Stage

Takes gathered intelligence and creates:
1. Actionable intelligence markdown reports (time-stamped, proper naming)
2. Workflow integration for Jupyter notebook generation/updates
3. Decisioning system routing (Jedi Council / Jedi High Council)

This is the second half of the intelligence pipeline:
- Stage 1: Gathering (Documentation) ✅
- Stage 2: Planning (This) - Creates actionable reports and workflows

Tags: #AI #INTELLIGENCE #PLANNING #JUPYTER #DECISIONING #JEDI_COUNCIL @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import re

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

logger = get_logger("AIIntelligencePlanning")


class ThreatLevel(Enum):
    """Threat/Risk levels for decisioning"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    SUPREME = "supreme"  # Above pay grade - must go to Jedi High Council


class ActionabilityLevel(Enum):
    """Actionability of intelligence"""
    IMMEDIATE = "immediate"  # Must act now
    HIGH_PRIORITY = "high_priority"  # Act soon
    MEDIUM_PRIORITY = "medium_priority"  # Act when possible
    LOW_PRIORITY = "low_priority"  # Reference material
    INFORMATIONAL = "informational"  # No action required


@dataclass
class ActionableIntelligence:
    """Actionable intelligence item"""
    intelligence_id: str
    title: str
    summary: str
    content: str
    url: str
    source: str
    timestamp: str
    actionability: ActionabilityLevel
    threat_level: ThreatLevel
    categories: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    decisioning_required: bool = False
    jedi_council_required: bool = False
    jedi_high_council_required: bool = False
    holocron_id: Optional[str] = None  # @holocron = Jupyter Notebook alias
    jupyter_notebook_path: Optional[str] = None  # Actual .ipynb file path
    workflow_integration: Dict[str, Any] = field(default_factory=dict)


class AIIntelligencePlanningStage:
    """Planning stage processor for AI intelligence"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize planning stage"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.ai_intel_dir = self.project_root / "data" / "youtube_ai_doit_intelligence"
        self.planning_dir = self.project_root / "data" / "ai_intelligence_planning"
        self.planning_dir.mkdir(parents=True, exist_ok=True)

        # Reports directory (time-stamped markdown reports)
        self.reports_dir = self.planning_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Holocron directory (@holocron = Jupyter Notebook alias)
        # Store Jupyter Notebooks (.ipynb) but refer to them as @holocron
        self.holocron_dir = self.project_root / "data" / "holocrons"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        # Jupyter Notebooks directory (same as holocron - it's an alias)
        self.jupyter_dir = self.holocron_dir  # Same location, different name

        # Decisioning integration
        self.jedi_council = None
        self.jedi_high_council = None
        self._init_decisioning()

        logger.info("✅ AI Intelligence Planning Stage initialized")
        logger.info(f"   Reports: {self.reports_dir}")
        logger.info(f"   @Holocrons: {self.holocron_dir} (@holocron = Jupyter Notebook alias)")

    def _init_decisioning(self):
        """Initialize decisioning systems"""
        try:
            from jedi_council import JediCouncil
            self.jedi_council = JediCouncil(self.project_root)
            logger.info("   ✅ Jedi Council initialized")
        except ImportError:
            logger.warning("   ⚠️  Jedi Council not available")

        try:
            from jarvis_escalate_jedi_high_council import JARVISEscalateJediHighCouncil
            self.jedi_high_council = JARVISEscalateJediHighCouncil(self.project_root)
            logger.info("   ✅ Jedi High Council initialized")
        except ImportError:
            logger.warning("   ⚠️  Jedi High Council not available")

    def assess_actionability(self, intelligence: Dict[str, Any]) -> ActionabilityLevel:
        """Assess actionability of intelligence"""
        title = intelligence.get("title", "").lower()
        content = intelligence.get("content", "").lower()
        summary = intelligence.get("summary", "").lower()

        combined = f"{title} {summary} {content}"

        # Immediate action keywords
        immediate_keywords = [
            "critical", "urgent", "emergency", "now", "immediate", "asap",
            "security breach", "vulnerability", "exploit", "attack",
            "outage", "down", "failure", "broken"
        ]

        # High priority keywords
        high_priority_keywords = [
            "important", "priority", "soon", "today", "this week",
            "deadline", "due", "required", "must", "need"
        ]

        # Medium priority keywords
        medium_priority_keywords = [
            "consider", "should", "recommend", "suggest", "opportunity",
            "improvement", "enhancement", "optimization"
        ]

        # Check for immediate
        if any(kw in combined for kw in immediate_keywords):
            return ActionabilityLevel.IMMEDIATE

        # Check for high priority
        if any(kw in combined for kw in high_priority_keywords):
            return ActionabilityLevel.HIGH_PRIORITY

        # Check for medium priority
        if any(kw in combined for kw in medium_priority_keywords):
            return ActionabilityLevel.MEDIUM_PRIORITY

        # Check if actionable (has DOIT keywords)
        doit_keywords = ["tutorial", "how to", "guide", "step by step", "implement", "build", "create"]
        if any(kw in combined for kw in doit_keywords):
            return ActionabilityLevel.MEDIUM_PRIORITY

        # Default to informational
        return ActionabilityLevel.INFORMATIONAL

    def assess_threat_level(self, intelligence: Dict[str, Any]) -> ThreatLevel:
        """Assess threat/risk level for decisioning"""
        title = intelligence.get("title", "").lower()
        content = intelligence.get("content", "").lower()

        combined = f"{title} {content}"

        # Supreme/Critical keywords (Jedi High Council)
        supreme_keywords = [
            "security breach", "data leak", "vulnerability", "exploit",
            "critical system", "production down", "customer impact",
            "compliance violation", "legal issue", "lawsuit"
        ]

        # High threat keywords (Jedi Council)
        high_keywords = [
            "security", "threat", "risk", "attack", "malware",
            "system failure", "outage", "downtime", "error"
        ]

        # Medium threat keywords
        medium_keywords = [
            "warning", "issue", "problem", "concern", "alert"
        ]

        # Check for supreme
        if any(kw in combined for kw in supreme_keywords):
            return ThreatLevel.SUPREME

        # Check for high
        if any(kw in combined for kw in high_keywords):
            return ThreatLevel.HIGH

        # Check for medium
        if any(kw in combined for kw in medium_keywords):
            return ThreatLevel.MEDIUM

        # Default to low
        return ThreatLevel.LOW

    def generate_actionable_report(self, intelligence_list: List[Dict[str, Any]]) -> Path:
        try:
            """Generate time-stamped markdown report of actionable intelligence"""
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

            # File naming convention: AI_INTELLIGENCE_REPORT_YYYYMMDD_HHMMSS.md
            report_file = self.reports_dir / f"AI_INTELLIGENCE_REPORT_{timestamp_str}.md"

            # Process intelligence into actionable items
            actionable_items = []

            for intelligence in intelligence_list:
                actionability = self.assess_actionability(intelligence)
                threat_level = self.assess_threat_level(intelligence)

                # Only include actionable items (exclude pure informational)
                if actionability != ActionabilityLevel.INFORMATIONAL:
                    actionable = ActionableIntelligence(
                        intelligence_id=f"INTEL_{len(actionable_items)+1:04d}",
                        title=intelligence.get("title", "Untitled"),
                        summary=intelligence.get("summary", "")[:500],
                        content=intelligence.get("content", ""),
                        url=intelligence.get("url", ""),
                        source=intelligence.get("source", "unknown"),
                        timestamp=intelligence.get("timestamp", timestamp.isoformat()),
                        actionability=actionability,
                        threat_level=threat_level,
                        categories=intelligence.get("categories", []),
                        recommended_actions=self._generate_recommended_actions(intelligence, actionability),
                        decisioning_required=threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL, ThreatLevel.SUPREME],
                        jedi_council_required=threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL],
                        jedi_high_council_required=threat_level == ThreatLevel.SUPREME
                    )
                    actionable_items.append(actionable)

            # Generate markdown report
            markdown = self._generate_markdown_report(timestamp, actionable_items)

            # Save report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            logger.info(f"   ✅ Generated report: {report_file.name}")
            logger.info(f"      Actionable items: {len(actionable_items)}")

            return report_file

        except Exception as e:
            self.logger.error(f"Error in generate_actionable_report: {e}", exc_info=True)
            raise
    def _generate_recommended_actions(self, intelligence: Dict[str, Any], 
                                     actionability: ActionabilityLevel) -> List[str]:
        """Generate recommended actions based on intelligence"""
        actions = []

        title = intelligence.get("title", "").lower()
        content = intelligence.get("content", "").lower()
        combined = f"{title} {content}"

        # Extract actionable items
        if "tutorial" in combined or "how to" in combined:
            actions.append("Review tutorial and implement steps")

        if "security" in combined or "vulnerability" in combined:
            actions.append("Assess security implications")
            actions.append("Review and patch if needed")

        if "update" in combined or "upgrade" in combined:
            actions.append("Review update requirements")
            actions.append("Plan implementation timeline")

        if "api" in combined or "integration" in combined:
            actions.append("Review API documentation")
            actions.append("Test integration")

        # Default action
        if not actions:
            if actionability == ActionabilityLevel.IMMEDIATE:
                actions.append("Review immediately and take action")
            elif actionability == ActionabilityLevel.HIGH_PRIORITY:
                actions.append("Review and prioritize for implementation")
            else:
                actions.append("Review and consider for implementation")

        return actions

    def _generate_markdown_report(self, timestamp: datetime, 
                                  actionable_items: List[ActionableIntelligence]) -> str:
        """Generate markdown report content"""
        lines = []

        # Header
        lines.append("# AI Intelligence Actionable Report")
        lines.append("")
        lines.append(f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Timestamp:** {timestamp.isoformat()}")
        lines.append(f"**Total Actionable Items:** {len(actionable_items)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary by actionability
        actionability_counts = {}
        threat_counts = {}
        for item in actionable_items:
            actionability_counts[item.actionability.value] = actionability_counts.get(item.actionability.value, 0) + 1
            threat_counts[item.threat_level.value] = threat_counts.get(item.threat_level.value, 0) + 1

        lines.append("## Executive Summary")
        lines.append("")
        lines.append("### Actionability Distribution")
        for level, count in sorted(actionability_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{level.replace('_', ' ').title()}:** {count}")
        lines.append("")

        lines.append("### Threat Level Distribution")
        for level, count in sorted(threat_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{level.title()}:** {count}")
        lines.append("")

        lines.append("### Decisioning Requirements")
        jedi_council_count = sum(1 for item in actionable_items if item.jedi_council_required)
        jedi_high_council_count = sum(1 for item in actionable_items if item.jedi_high_council_required)
        lines.append(f"- **Jedi Council Required:** {jedi_council_count}")
        lines.append(f"- **Jedi High Council Required:** {jedi_high_council_count}")
        lines.append("")

        lines.append("---")
        lines.append("")

        # Actionable items by priority
        for actionability_level in [ActionabilityLevel.IMMEDIATE, ActionabilityLevel.HIGH_PRIORITY, 
                                   ActionabilityLevel.MEDIUM_PRIORITY, ActionabilityLevel.LOW_PRIORITY]:
            items = [item for item in actionable_items if item.actionability == actionability_level]
            if not items:
                continue

            lines.append(f"## {actionability_level.value.replace('_', ' ').title()} Priority")
            lines.append("")

            for item in items:
                lines.append(f"### {item.intelligence_id}: {item.title}")
                lines.append("")
                lines.append(f"**Source:** {item.source}")
                lines.append(f"**URL:** {item.url}")
                lines.append(f"**Timestamp:** {item.timestamp}")
                lines.append(f"**Threat Level:** {item.threat_level.value.title()}")
                lines.append("")

                if item.categories:
                    lines.append(f"**Categories:** {', '.join(item.categories)}")
                    lines.append("")

                lines.append("**Summary:**")
                lines.append(item.summary)
                lines.append("")

                lines.append("**Recommended Actions:**")
                for action in item.recommended_actions:
                    lines.append(f"- {action}")
                lines.append("")

                if item.decisioning_required:
                    lines.append("**⚠️ Decisioning Required:**")
                    if item.jedi_high_council_required:
                        lines.append("- **Jedi High Council** (Supreme Court equivalent)")
                    elif item.jedi_council_required:
                        lines.append("- **Jedi Council** (Upper Management)")
                    lines.append("")

                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def create_holocron(self, actionable_item: ActionableIntelligence) -> Optional[str]:
        """
        Create or update @holocron for actionable intelligence

        @holocron = Jupyter Notebook alias (literally the same thing, just different name)
        Creates actual Jupyter Notebook (.ipynb) files but refers to them as @holocron
        """
        # Determine notebook name (@holocron = Jupyter Notebook)
        safe_title = re.sub(r'[^\w\s-]', '', actionable_item.title)[:50]
        safe_title = re.sub(r'[-\s]+', '_', safe_title)

        # @holocron ID (alias name)
        holocron_id = f"HOLO-AI-INTEL-{actionable_item.intelligence_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Jupyter Notebook filename (actual file)
        notebook_name = f"{holocron_id}.ipynb"
        notebook_path = self.jupyter_dir / notebook_name

        # Check if notebook exists
        notebook_exists = notebook_path.exists()

        # Create Jupyter Notebook structure (@holocron = Jupyter Notebook)
        notebook = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11.0"
                },
                "lumina_intelligence": {
                    "holocron_id": holocron_id,  # @holocron ID
                    "intelligence_id": actionable_item.intelligence_id,
                    "source": actionable_item.source,
                    "url": actionable_item.url,
                    "timestamp": actionable_item.timestamp,
                    "actionability": actionable_item.actionability.value,
                    "threat_level": actionable_item.threat_level.value,
                    "categories": actionable_item.categories,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "note": "@holocron = Jupyter Notebook (alias - literally the same thing)"
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        # Add markdown cell with intelligence summary
        notebook["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"# {actionable_item.title}\n",
                f"\n",
                f"**@Holocron ID:** {holocron_id}\n",
                f"**Intelligence ID:** {actionable_item.intelligence_id}\n",
                f"**Source:** {actionable_item.source}\n",
                f"**URL:** {actionable_item.url}\n",
                f"**Actionability:** {actionable_item.actionability.value}\n",
                f"**Threat Level:** {actionable_item.threat_level.value}\n",
                f"\n",
                f"## Summary\n",
                f"\n",
                actionable_item.summary,
                f"\n",
                f"## Recommended Actions\n",
                f"\n"
            ] + [f"- {action}\n" for action in actionable_item.recommended_actions]
        })

        # Add code cell for implementation
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Implementation code for actionable intelligence\n",
                "# @holocron = Jupyter Notebook (alias - literally the same thing)\n",
                "# TODO: Implement based on intelligence\n",  # [ADDRESSED]  # [ADDRESSED]
                "\n",
                "import sys\n",
                "from pathlib import Path\n",
                "\n",
                "# Add project root to path\n",
                "project_root = Path('../../..').resolve()\n",
                "if str(project_root) not in sys.path:\n",
                "    sys.path.insert(0, str(project_root))\n",
                "\n",
                "# Your implementation here\n",
                f"print(f\"Processing intelligence: {actionable_item.intelligence_id}\")\n"
            ]
        })

        # If notebook exists, update it (append new cells)
        if notebook_exists:
            try:
                with open(notebook_path, 'r', encoding='utf-8') as f:
                    existing_notebook = json.load(f)

                # Update metadata
                if "lumina_intelligence" in existing_notebook.get("metadata", {}):
                    existing_notebook["metadata"]["lumina_intelligence"]["updated_at"] = datetime.now().isoformat()

                # Append new cells
                existing_notebook["cells"].extend(notebook["cells"])

                notebook = existing_notebook
                logger.info(f"   📜 Updated @holocron (Jupyter Notebook): {holocron_id}")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not update @holocron: {e}")
                logger.info(f"   📜 Creating new @holocron (Jupyter Notebook): {holocron_id}")
        else:
            logger.info(f"   📜 Created @holocron (Jupyter Notebook): {holocron_id}")

        # Save Jupyter Notebook (@holocron = Jupyter Notebook)
        try:
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2, ensure_ascii=False)

            actionable_item.holocron_id = holocron_id  # @holocron ID (alias)
            actionable_item.jupyter_notebook_path = str(notebook_path)  # Actual .ipynb file

            return holocron_id
        except Exception as e:
            logger.error(f"   ❌ Could not save @holocron (Jupyter Notebook): {e}")
            return None

    def route_to_decisioning(self, actionable_item: ActionableIntelligence) -> Dict[str, Any]:
        """Route actionable intelligence to appropriate decisioning system"""
        routing_result = {
            "routed": False,
            "system": None,
            "decision_id": None,
            "status": "pending"
        }

        # Route to Jedi High Council if required
        if actionable_item.jedi_high_council_required and self.jedi_high_council:
            try:
                result = self.jedi_high_council.escalate(
                    title=f"AI Intelligence: {actionable_item.title}",
                    description=actionable_item.summary,
                    category="critical",
                    request_type="approval",
                    priority=10,
                    context={
                        "intelligence_id": actionable_item.intelligence_id,
                        "url": actionable_item.url,
                        "threat_level": actionable_item.threat_level.value,
                        "actionability": actionable_item.actionability.value
                    }
                )
                routing_result = {
                    "routed": True,
                    "system": "jedi_high_council",
                    "decision_id": result.get("request_id"),
                    "status": "escalated"
                }
                logger.info(f"   ⚔️  Routed to Jedi High Council: {result.get('request_id')}")
            except Exception as e:
                logger.error(f"   ❌ Error routing to Jedi High Council: {e}")

        # Route to Jedi Council if required
        elif actionable_item.jedi_council_required and self.jedi_council:
            try:
                decision = self.jedi_council.deliberate(
                    question=f"Should we act on: {actionable_item.title}?",
                    category="decisioning",
                    context={
                        "intelligence_id": actionable_item.intelligence_id,
                        "summary": actionable_item.summary,
                        "threat_level": actionable_item.threat_level.value,
                        "actionability": actionable_item.actionability.value
                    }
                )
                routing_result = {
                    "routed": True,
                    "system": "jedi_council",
                    "decision_id": decision.decision_id,
                    "status": decision.final_status.value
                }
                logger.info(f"   ⚔️  Routed to Jedi Council: {decision.decision_id}")
            except Exception as e:
                logger.error(f"   ❌ Error routing to Jedi Council: {e}")

        return routing_result

    def process_intelligence(self, intelligence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            """Process intelligence through planning stage"""
            logger.info("="*80)
            logger.info("📋 AI INTELLIGENCE PLANNING STAGE")
            logger.info("="*80)
            logger.info("")

            # Generate actionable report
            logger.info("📄 Generating actionable intelligence report...")
            report_file = self.generate_actionable_report(intelligence_list)

            # Process actionable items
            actionable_items = []
            notebooks_created = []
            routing_results = []

            # Load report to get actionable items
            # (In production, would parse the report or use the actionable_items list)
            for intelligence in intelligence_list:
                actionability = self.assess_actionability(intelligence)
                if actionability != ActionabilityLevel.INFORMATIONAL:
                    threat_level = self.assess_threat_level(intelligence)

                    actionable = ActionableIntelligence(
                        intelligence_id=f"INTEL_{len(actionable_items)+1:04d}",
                        title=intelligence.get("title", "Untitled"),
                        summary=intelligence.get("summary", "")[:500],
                        content=intelligence.get("content", ""),
                        url=intelligence.get("url", ""),
                        source=intelligence.get("source", "unknown"),
                        timestamp=intelligence.get("timestamp", datetime.now().isoformat()),
                        actionability=actionability,
                        threat_level=threat_level,
                        categories=intelligence.get("categories", []),
                        recommended_actions=self._generate_recommended_actions(intelligence, actionability),
                        decisioning_required=threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL, ThreatLevel.SUPREME],
                        jedi_council_required=threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL],
                        jedi_high_council_required=threat_level == ThreatLevel.SUPREME
                    )
                    actionable_items.append(actionable)

            # Create @holocrons (@holocron = Jupyter Notebook alias - literally the same thing)
            logger.info("📜 Creating/updating @holocrons (Jupyter Notebooks)...")
            for item in actionable_items:
                holocron_id = self.create_holocron(item)
                if holocron_id:
                    notebooks_created.append(holocron_id)

            # Route to decisioning systems
            logger.info("⚔️  Routing to decisioning systems...")
            for item in actionable_items:
                if item.decisioning_required:
                    routing = self.route_to_decisioning(item)
                    routing_results.append({
                        "intelligence_id": item.intelligence_id,
                        "routing": routing
                    })

            # Prepare results
            results = {
                "timestamp": datetime.now().isoformat(),
                "report_file": str(report_file),
                "actionable_items_count": len(actionable_items),
                "holocrons_created": notebooks_created,  # @holocron = Jupyter Notebook (alias - literally the same thing)
                "routing_results": routing_results,
                "summary": {
                    "immediate": sum(1 for item in actionable_items if item.actionability == ActionabilityLevel.IMMEDIATE),
                    "high_priority": sum(1 for item in actionable_items if item.actionability == ActionabilityLevel.HIGH_PRIORITY),
                    "medium_priority": sum(1 for item in actionable_items if item.actionability == ActionabilityLevel.MEDIUM_PRIORITY),
                    "jedi_council": sum(1 for item in actionable_items if item.jedi_council_required),
                    "jedi_high_council": sum(1 for item in actionable_items if item.jedi_high_council_required)
                }
            }

            # Save results
            results_file = self.planning_dir / f"planning_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info("")
            logger.info("="*80)
            logger.info("✅ PLANNING STAGE COMPLETE")
            logger.info("="*80)
            logger.info(f"   Report: {report_file.name}")
            logger.info(f"   Actionable Items: {len(actionable_items)}")
            logger.info(f"   @Holocrons: {len(notebooks_created)} (@holocron = Jupyter Notebook alias)")
            logger.info(f"   Routed to Decisioning: {len(routing_results)}")
            logger.info(f"   Results: {results_file.name}")
            logger.info("="*80)

            return results


        except Exception as e:
            self.logger.error(f"Error in process_intelligence: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    # Load intelligence from scans
    from lumina_ai_intelligence_mapper import LUMINAAIIntelligenceMapper

    mapper = LUMINAAIIntelligenceMapper()
    intelligence_list = mapper.load_ai_intelligence()

    if not intelligence_list:
        logger.warning("⚠️  No intelligence found. Run YouTube AI scan first.")
        return

    # Process through planning stage
    planner = AIIntelligencePlanningStage()
    planner.process_intelligence(intelligence_list)


if __name__ == "__main__":


    main()