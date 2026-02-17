#!/usr/bin/env python3
"""
SYPHON Workflow Intelligence Integration

Intelligently analyzes processed workflows using SYPHON extraction,
then integrates the extracted intelligence into the master workflow system.

Tags: #SYPHON #WORKFLOW #INTELLIGENCE #MASTER #INTEGRATION @JARVIS @DOIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SYPHONWorkflowIntelligenceIntegration")

# Import required systems
try:
    from syphon.core import SYPHONSystem, SYPHONConfig
    from syphon.models import DataSourceType
    try:
        from syphon.config import SubscriptionTier
    except ImportError:
        from syphon.core import SubscriptionTier
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from syphon import SYPHONSystem, SYPHONConfig, SubscriptionTier, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("⚠️  SYPHON system not available")

try:
    from jarvis_master_chat_session import JARVISMasterChatSession, AgentMessage
    MASTER_CHAT_AVAILABLE = True
except ImportError:
    MASTER_CHAT_AVAILABLE = False
    logger.warning("⚠️  Master chat session not available")

try:
    from aggregate_workflows_to_master import WorkflowAggregator
    AGGREGATOR_AVAILABLE = True
except ImportError:
    AGGREGATOR_AVAILABLE = False
    logger.warning("⚠️  Workflow aggregator not available")


class SYPHONWorkflowIntelligenceIntegration:
    """
    SYPHON Workflow Intelligence Integration

    Analyzes workflows using SYPHON extraction and integrates
    intelligence into the master workflow system.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize intelligence integration system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_workflow_intelligence"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True
                )
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize SYPHON: {e}")

        # Initialize master chat session
        self.master_chat = None
        if MASTER_CHAT_AVAILABLE:
            try:
                self.master_chat = JARVISMasterChatSession(project_root=self.project_root)
                logger.info("✅ Master chat session initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize master chat: {e}")

        # Initialize workflow aggregator
        self.aggregator = None
        if AGGREGATOR_AVAILABLE:
            try:
                self.aggregator = WorkflowAggregator(project_root=self.project_root)
                logger.info("✅ Workflow aggregator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize aggregator: {e}")

        logger.info("✅ SYPHON Workflow Intelligence Integration initialized")

    def load_processed_workflows(self) -> List[Dict[str, Any]]:
        """Load all processed workflows"""
        if not self.aggregator:
            logger.error("❌ Aggregator not available")
            return []

        workflows = self.aggregator.load_all_workflows()
        logger.info(f"✅ Loaded {len(workflows)} workflows for analysis")
        return workflows

    def extract_workflow_intelligence(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract intelligence from a single workflow using SYPHON.

        Returns extracted actionable items, tasks, decisions, and patterns.
        """
        workflow_id = workflow.get("workflow_id", "unknown")
        workflow_name = workflow.get("workflow_name", "Unknown Workflow")
        messages = workflow.get("messages", [])

        logger.info(f"🔍 SYPHON extracting intelligence from: {workflow_name}")

        # Combine all messages into content for SYPHON extraction
        content_parts = []
        for msg in messages:
            msg_content = msg.get("content") or msg.get("text") or msg.get("message", "")
            agent_name = msg.get("agent_name") or msg.get("agent_id", "unknown")
            timestamp = msg.get("timestamp", "")

            content_parts.append(f"[{timestamp}] {agent_name}: {msg_content}")

        content = "\n".join(content_parts)

        # Use SYPHON to extract intelligence
        intelligence_result = {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "extracted_at": datetime.now().isoformat(),
            "actionable_items": [],
            "tasks": [],
            "decisions": [],
            "patterns": [],
            "insights": [],
            "metadata": {}
        }

        if self.syphon:
            try:
                # Extract using SYPHON's workflow extractor
                extraction_result = self.syphon.extract(
                    source_type=DataSourceType.WORKFLOW,
                    content=content,
                    metadata={
                        "workflow_name": workflow_name,
                        "workflow_id": workflow_id,
                        "message_count": len(messages),
                        "agents": workflow.get("agents_involved", [])
                    }
                )

                if extraction_result and extraction_result.success and extraction_result.data:
                    syphon_data = extraction_result.data

                    # Extract actionable items
                    actionable = syphon_data.actionable_items or []
                    intelligence_result["actionable_items"] = [
                        {
                            "item": item if isinstance(item, str) else item.get("item", str(item)),
                            "priority": "medium",
                            "category": "general"
                        }
                        for item in actionable
                    ]

                    # Extract tasks
                    tasks = syphon_data.tasks or []
                    intelligence_result["tasks"] = [
                        {
                            "task": task.get("task", str(task)) if isinstance(task, dict) else str(task),
                            "status": task.get("status", "pending") if isinstance(task, dict) else "pending",
                            "assignee": task.get("assignee", "unassigned") if isinstance(task, dict) else "unassigned"
                        }
                        for task in tasks
                    ]

                    # Extract decisions
                    decisions = syphon_data.decisions or []
                    intelligence_result["decisions"] = [
                        {
                            "decision": decision.get("decision", str(decision)) if isinstance(decision, dict) else str(decision),
                            "context": decision.get("context", "") if isinstance(decision, dict) else "",
                            "impact": decision.get("impact", "unknown") if isinstance(decision, dict) else "unknown"
                        }
                        for decision in decisions
                    ]

                    # Extract patterns and insights
                    intelligence = syphon_data.intelligence or []
                    intelligence_result["patterns"] = [
                        {
                            "pattern": pattern.get("pattern", str(pattern)) if isinstance(pattern, dict) else str(pattern),
                            "frequency": pattern.get("frequency", 1) if isinstance(pattern, dict) else 1,
                            "significance": pattern.get("significance", "medium") if isinstance(pattern, dict) else "medium"
                        }
                        for pattern in intelligence
                    ]

                    logger.info(f"✅ SYPHON extracted: {len(actionable)} actionable, {len(tasks)} tasks, {len(decisions)} decisions")
                else:
                    logger.warning(f"⚠️  SYPHON extraction returned no results for {workflow_id}")

            except Exception as e:
                logger.error(f"❌ Error extracting intelligence from {workflow_id}: {e}")
        else:
            # Fallback: Basic pattern extraction without SYPHON
            logger.warning("⚠️  SYPHON not available, using basic extraction")

            # Basic keyword-based extraction
            content_lower = content.lower()

            # Extract potential tasks (lines with action verbs)
            action_verbs = ["create", "implement", "fix", "update", "add", "remove", "complete", "finish"]
            for verb in action_verbs:
                if verb in content_lower:
                    intelligence_result["tasks"].append({
                        "task": f"Action identified: {verb}",
                        "status": "pending",
                        "assignee": "unassigned"
                    })

            # Extract potential decisions (lines with decision keywords)
            decision_keywords = ["decide", "choose", "select", "option", "prefer", "recommend"]
            for keyword in decision_keywords:
                if keyword in content_lower:
                    intelligence_result["decisions"].append({
                        "decision": f"Decision point: {keyword}",
                        "context": "Workflow conversation",
                        "impact": "unknown"
                    })

        return intelligence_result

    def analyze_all_workflows(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all workflows and extract intelligence.

        Returns aggregated intelligence from all workflows.
        """
        logger.info("="*80)
        logger.info("🔍 SYPHON INTELLIGENCE EXTRACTION")
        logger.info("="*80)
        logger.info(f"   Analyzing {len(workflows)} workflows...")
        logger.info("")

        all_intelligence = {
            "extraction_timestamp": datetime.now().isoformat(),
            "total_workflows": len(workflows),
            "workflow_intelligence": [],
            "aggregated": {
                "total_actionable_items": 0,
                "total_tasks": 0,
                "total_decisions": 0,
                "total_patterns": 0,
                "unique_agents": set(),
                "categories": {}
            }
        }

        for workflow in workflows:
            intelligence = self.extract_workflow_intelligence(workflow)
            all_intelligence["workflow_intelligence"].append(intelligence)

            # Aggregate statistics
            all_intelligence["aggregated"]["total_actionable_items"] += len(intelligence["actionable_items"])
            all_intelligence["aggregated"]["total_tasks"] += len(intelligence["tasks"])
            all_intelligence["aggregated"]["total_decisions"] += len(intelligence["decisions"])
            all_intelligence["aggregated"]["total_patterns"] += len(intelligence["patterns"])

            # Track agents
            agents = workflow.get("agents_involved", [])
            for agent in agents:
                all_intelligence["aggregated"]["unique_agents"].add(agent)

        # Convert set to list for JSON serialization
        all_intelligence["aggregated"]["unique_agents"] = sorted(list(all_intelligence["aggregated"]["unique_agents"]))

        logger.info("")
        logger.info("✅ SYPHON EXTRACTION COMPLETE")
        logger.info(f"   Total actionable items: {all_intelligence['aggregated']['total_actionable_items']}")
        logger.info(f"   Total tasks: {all_intelligence['aggregated']['total_tasks']}")
        logger.info(f"   Total decisions: {all_intelligence['aggregated']['total_decisions']}")
        logger.info(f"   Total patterns: {all_intelligence['aggregated']['total_patterns']}")
        logger.info(f"   Unique agents: {len(all_intelligence['aggregated']['unique_agents'])}")
        logger.info("")

        return all_intelligence

    def integrate_into_master_workflow(self, intelligence: Dict[str, Any]) -> Optional[str]:
        """
        Integrate extracted intelligence into the master workflow system.

        Adds intelligence summaries and insights to the master chat session.
        """
        if not self.master_chat:
            logger.error("❌ Master chat session not available")
            return None

        logger.info("="*80)
        logger.info("🔄 INTEGRATING INTELLIGENCE INTO MASTER WORKFLOW")
        logger.info("="*80)

        # Get master session
        master_session = self.master_chat.master_session

        # Create intelligence summary message
        summary_parts = [
            f"📊 SYPHON Intelligence Extraction Summary",
            f"   Extracted from: {intelligence['total_workflows']} workflows",
            f"   Actionable Items: {intelligence['aggregated']['total_actionable_items']}",
            f"   Tasks: {intelligence['aggregated']['total_tasks']}",
            f"   Decisions: {intelligence['aggregated']['total_decisions']}",
            f"   Patterns: {intelligence['aggregated']['total_patterns']}",
            f"   Agents Involved: {', '.join(intelligence['aggregated']['unique_agents'])}",
            "",
            "🔍 Key Intelligence Extracted:"
        ]

        # Add top actionable items
        all_actionable = []
        for wf_intel in intelligence["workflow_intelligence"]:
            for item in wf_intel["actionable_items"]:
                all_actionable.append(item)

        # Sort by priority and take top 10
        all_actionable.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1))
        top_actionable = all_actionable[:10]

        for i, item in enumerate(top_actionable, 1):
            summary_parts.append(f"   {i}. [{item.get('priority', 'medium').upper()}] {item.get('item', 'N/A')}")

        # Add top tasks
        all_tasks = []
        for wf_intel in intelligence["workflow_intelligence"]:
            for task in wf_intel["tasks"]:
                all_tasks.append(task)

        if all_tasks:
            summary_parts.append("")
            summary_parts.append("📋 Key Tasks Identified:")
            for i, task in enumerate(all_tasks[:10], 1):
                summary_parts.append(f"   {i}. {task.get('task', 'N/A')} [{task.get('status', 'pending')}]")

        # Add top decisions
        all_decisions = []
        for wf_intel in intelligence["workflow_intelligence"]:
            for decision in wf_intel["decisions"]:
                all_decisions.append(decision)

        if all_decisions:
            summary_parts.append("")
            summary_parts.append("🎯 Key Decisions Made:")
            for i, decision in enumerate(all_decisions[:10], 1):
                summary_parts.append(f"   {i}. {decision.get('decision', 'N/A')}")

        summary_message = "\n".join(summary_parts)

        # Create agent message for master session
        intelligence_message = AgentMessage(
            agent_id="SYPHON",
            agent_name="SYPHON Intelligence Extractor",
            message=summary_message,
            timestamp=datetime.now().isoformat(),
            message_type="intelligence",
            metadata={
                "extraction_timestamp": intelligence["extraction_timestamp"],
                "workflows_analyzed": intelligence["total_workflows"],
                "intelligence_summary": {
                    "actionable_items": intelligence["aggregated"]["total_actionable_items"],
                    "tasks": intelligence["aggregated"]["total_tasks"],
                    "decisions": intelligence["aggregated"]["total_decisions"],
                    "patterns": intelligence["aggregated"]["total_patterns"]
                }
            }
        )

        # Add to master session
        master_session.messages.append(intelligence_message)
        master_session.last_activity = datetime.now().isoformat()

        # Save master session
        try:
            self.master_chat._save_session(master_session)
            logger.info(f"✅ Intelligence integrated into master workflow: {master_session.session_id}")
            return master_session.session_id
        except Exception as e:
            logger.error(f"❌ Error saving master session: {e}")
            return None

    def save_intelligence_report(self, intelligence: Dict[str, Any]) -> Path:
        """Save intelligence report to file"""
        report_file = self.data_dir / f"intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(intelligence, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"✅ Intelligence report saved: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"❌ Error saving intelligence report: {e}")
            raise

    def execute_full_pipeline(self) -> Dict[str, Any]:
        """
        Execute the full pipeline: Load → Extract → Integrate
        """
        logger.info("="*80)
        logger.info("🚀 SYPHON WORKFLOW INTELLIGENCE INTEGRATION")
        logger.info("="*80)
        logger.info("")

        pipeline_result = {
            "started_at": datetime.now().isoformat(),
            "success": False
        }

        try:
            # Step 1: Load processed workflows
            logger.info("STEP 1: Loading processed workflows...")
            workflows = self.load_processed_workflows()
            if not workflows:
                logger.error("❌ No workflows loaded")
                return pipeline_result

            pipeline_result["workflows_loaded"] = len(workflows)

            # Step 2: Extract intelligence using SYPHON
            logger.info("")
            logger.info("STEP 2: Extracting intelligence with SYPHON...")
            intelligence = self.analyze_all_workflows(workflows)

            # Save intelligence report
            report_file = self.save_intelligence_report(intelligence)
            pipeline_result["intelligence_report"] = str(report_file)

            # Step 3: Integrate into master workflow
            logger.info("")
            logger.info("STEP 3: Integrating intelligence into master workflow...")
            master_session_id = self.integrate_into_master_workflow(intelligence)
            pipeline_result["master_session_id"] = master_session_id

            pipeline_result["success"] = True
            pipeline_result["completed_at"] = datetime.now().isoformat()

            logger.info("")
            logger.info("="*80)
            logger.info("✅ FULL PIPELINE COMPLETE")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}", exc_info=True)
            pipeline_result["error"] = str(e)

        return pipeline_result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SYPHON Workflow Intelligence Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python syphon_workflow_intelligence_integration.py

  # Extract intelligence only (no integration)
  python syphon_workflow_intelligence_integration.py --extract-only
        """
    )

    parser.add_argument("--extract-only", action="store_true",
                       help="Only extract intelligence, don't integrate")

    args = parser.parse_args()

    # Initialize system
    integrator = SYPHONWorkflowIntelligenceIntegration()

    if args.extract_only:
        # Just extract
        workflows = integrator.load_processed_workflows()
        intelligence = integrator.analyze_all_workflows(workflows)
        integrator.save_intelligence_report(intelligence)

        print("\n" + "="*80)
        print("📊 INTELLIGENCE EXTRACTION RESULTS")
        print("="*80)
        print(f"   Workflows analyzed: {intelligence['total_workflows']}")
        print(f"   Actionable items: {intelligence['aggregated']['total_actionable_items']}")
        print(f"   Tasks: {intelligence['aggregated']['total_tasks']}")
        print(f"   Decisions: {intelligence['aggregated']['total_decisions']}")
        print(f"   Patterns: {intelligence['aggregated']['total_patterns']}")
        print()
    else:
        # Full pipeline
        result = integrator.execute_full_pipeline()

        print("\n" + "="*80)
        print("📊 PIPELINE RESULTS")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        print()


if __name__ == "__main__":


    main()