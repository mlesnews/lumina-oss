#!/usr/bin/env python3
"""
Aggregate All Workflows to Master Workflow

Aggregates all discovered workflows into a single master workflow
under one agent chat session.

Tags: #WORKFLOW #AGGREGATE #MASTER #CHAT #SESSION @JARVIS @DOIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AggregateWorkflowsToMaster")

# Import required systems
try:
    from jarvis_workflow_archive_automation import JARVISWorkflowArchiveAutomation
    WORKFLOW_ARCHIVE_AVAILABLE = True
except ImportError:
    WORKFLOW_ARCHIVE_AVAILABLE = False
    logger.warning("⚠️  Workflow archive automation not available")

try:
    from jarvis_master_chat_session import JARVISMasterChatSession
    MASTER_CHAT_AVAILABLE = True
except ImportError:
    MASTER_CHAT_AVAILABLE = False
    logger.warning("⚠️  Master chat session not available")

try:
    from cursor_chat_session_workflow_manager import CursorChatSessionWorkflowManager
    WORKFLOW_MANAGER_AVAILABLE = True
except ImportError:
    WORKFLOW_MANAGER_AVAILABLE = False
    logger.warning("⚠️  Workflow manager not available")


class WorkflowAggregator:
    """
    Aggregates all workflows into a single master workflow.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow aggregator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "workflow_aggregation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize workflow archive automation
        self.workflow_archive = None
        if WORKFLOW_ARCHIVE_AVAILABLE:
            try:
                self.workflow_archive = JARVISWorkflowArchiveAutomation(
                    project_root=self.project_root,
                    fullauto=True
                )
                logger.info("✅ Workflow archive automation initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize workflow archive: {e}")

        # Initialize master chat session
        self.master_chat = None
        if MASTER_CHAT_AVAILABLE:
            try:
                self.master_chat = JARVISMasterChatSession(project_root=self.project_root)
                logger.info("✅ Master chat session initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize master chat: {e}")

        # Initialize workflow manager
        self.workflow_manager = None
        if WORKFLOW_MANAGER_AVAILABLE:
            try:
                self.workflow_manager = CursorChatSessionWorkflowManager(
                    project_root=self.project_root
                )
                logger.info("✅ Workflow manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize workflow manager: {e}")

        logger.info("✅ Workflow Aggregator initialized")

    def load_all_workflows(self) -> List[Dict[str, Any]]:
        """
        Load all workflows from session files.

        Returns:
            List of workflow data dictionaries
        """
        workflows = []
        session_dir = self.project_root / "data" / "agent_chat_sessions"

        if not session_dir.exists():
            logger.warning(f"⚠️  Session directory not found: {session_dir}")
            return workflows

        session_files = list(session_dir.glob("*.json"))
        logger.info(f"🔍 Loading {len(session_files)} workflow sessions...")

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                workflow_data = {
                    "workflow_id": session_file.stem,
                    "workflow_name": session_data.get("session_name", session_file.stem),
                    "source_file": str(session_file),
                    "created_at": session_data.get("inception_time", datetime.now().isoformat()),
                    "messages": session_data.get("messages", []),
                    "agents_involved": session_data.get("agents_involved", []),
                    "metadata": {
                        "message_count": len(session_data.get("messages", [])),
                        "session_data_keys": list(session_data.keys()),
                        "model": session_data.get("model"),
                        "provider": session_data.get("provider")
                    },
                    "raw_data": session_data  # Keep full data for aggregation
                }

                workflows.append(workflow_data)

            except Exception as e:
                logger.debug(f"Error loading {session_file}: {e}")

        logger.info(f"✅ Loaded {len(workflows)} workflows")
        return workflows

    def aggregate_to_master_workflow(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate all workflows into a single master workflow.

        Args:
            workflows: List of workflow data dictionaries

        Returns:
            Master workflow dictionary
        """
        logger.info(f"🔄 Aggregating {len(workflows)} workflows into master workflow...")

        # Collect all messages from all workflows
        all_messages = []
        all_agents = set()
        workflow_summaries = []

        for workflow in workflows:
            # Add workflow summary
            workflow_summaries.append({
                "workflow_id": workflow["workflow_id"],
                "workflow_name": workflow["workflow_name"],
                "message_count": workflow["metadata"]["message_count"],
                "created_at": workflow["created_at"]
            })

            # Collect agents
            for agent in workflow.get("agents_involved", []):
                all_agents.add(agent)

            # Collect messages with workflow context
            for msg in workflow.get("messages", []):
                # Add workflow context to message
                enriched_msg = {
                    **msg,
                    "workflow_id": workflow["workflow_id"],
                    "workflow_name": workflow["workflow_name"],
                    "source_workflow": workflow["workflow_id"]
                }
                all_messages.append(enriched_msg)

        # Create master workflow
        master_workflow = {
            "master_workflow_id": f"master_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "master_workflow_name": "Master Workflow - All Aggregated Workflows",
            "created_at": datetime.now().isoformat(),
            "aggregated_from": len(workflows),
            "workflow_summaries": workflow_summaries,
            "total_messages": len(all_messages),
            "agents_involved": sorted(list(all_agents)),
            "messages": all_messages,
            "metadata": {
                "aggregation_timestamp": datetime.now().isoformat(),
                "source_workflows": [w["workflow_id"] for w in workflows],
                "total_workflows": len(workflows),
                "total_agents": len(all_agents)
            }
        }

        logger.info(f"✅ Master workflow created:")
        logger.info(f"   - Aggregated from: {len(workflows)} workflows")
        logger.info(f"   - Total messages: {len(all_messages)}")
        logger.info(f"   - Agents involved: {len(all_agents)}")

        return master_workflow

    def save_master_workflow(self, master_workflow: Dict[str, Any]) -> Path:
        """
        Save master workflow to file.

        Args:
            master_workflow: Master workflow dictionary

        Returns:
            Path to saved file
        """
        master_file = self.data_dir / f"{master_workflow['master_workflow_id']}.json"

        try:
            with open(master_file, 'w', encoding='utf-8') as f:
                json.dump(master_workflow, f, indent=2, default=str)

            logger.info(f"✅ Master workflow saved: {master_file}")
            return master_file

        except Exception as e:
            logger.error(f"❌ Error saving master workflow: {e}")
            raise

    def create_master_chat_session(self, master_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create master agent chat session from aggregated workflow.

        Args:
            master_workflow: Master workflow dictionary

        Returns:
            Session creation result
        """
        if not self.master_chat:
            logger.warning("⚠️  Master chat session not available")
            return {"success": False, "error": "Master chat not available"}

        try:
            logger.info("🔄 Creating master agent chat session...")

            # Prepare session data
            session_name = f"Master Workflow - {master_workflow['aggregated_from']} Workflows"

            # Create consolidated message for master session
            consolidated_message = f"""# Master Workflow Aggregation

**Aggregated from**: {master_workflow['aggregated_from']} workflows
**Total Messages**: {master_workflow['total_messages']}
**Agents Involved**: {', '.join(master_workflow['agents_involved'])}

## Workflow Summary

"""

            for summary in master_workflow['workflow_summaries']:
                consolidated_message += f"- **{summary['workflow_name']}** ({summary['workflow_id']})\n"
                consolidated_message += f"  - Messages: {summary['message_count']}\n"
                consolidated_message += f"  - Created: {summary['created_at']}\n\n"

            consolidated_message += f"""
## All Messages Aggregated

All {master_workflow['total_messages']} messages from {master_workflow['aggregated_from']} workflows have been consolidated into this master session.

**Master Workflow ID**: `{master_workflow['master_workflow_id']}`
**Created**: {master_workflow['created_at']}
"""

            # Add message to master chat session
            result = self.master_chat.add_message(
                agent_id="JARVIS",
                agent_name="JARVIS (Master Workflow Aggregator)",
                message=consolidated_message,
                message_type="aggregation"
            )

            # Also add individual workflow messages (first 100 to avoid overwhelming)
            messages_added = 0
            for msg in master_workflow['messages'][:100]:  # Limit to first 100 messages
                try:
                    msg_text = msg.get("content", msg.get("text", str(msg)))
                    if isinstance(msg_text, dict):
                        msg_text = json.dumps(msg_text, indent=2)

                    workflow_context = f"[From: {msg.get('workflow_name', 'Unknown')}] "
                    self.master_chat.add_message(
                        agent_id=msg.get("role", "assistant"),
                        agent_name=msg.get("workflow_name", "Workflow"),
                        message=workflow_context + str(msg_text)[:500],  # Truncate long messages
                        message_type="workflow_message",
                        metadata={
                            "workflow_id": msg.get("workflow_id"),
                            "source_workflow": msg.get("source_workflow")
                        }
                    )
                    messages_added += 1
                except Exception as e:
                    logger.debug(f"Error adding message: {e}")

            logger.info(f"✅ Added {messages_added} messages to master chat session")

            # Save master session
            self.master_chat._save_session()

            return {
                "success": True,
                "session_id": self.master_chat.master_session.session_id,
                "messages_added": messages_added,
                "workflows_aggregated": master_workflow['aggregated_from']
            }

        except Exception as e:
            logger.error(f"❌ Error creating master chat session: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def aggregate_all(self) -> Dict[str, Any]:
        """
        Main method: Aggregate all workflows into master workflow and chat session.

        Returns:
            Aggregation result dictionary
        """
        logger.info("="*80)
        logger.info("🔄 AGGREGATING ALL WORKFLOWS TO MASTER WORKFLOW")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "workflows_loaded": 0,
            "workflows_aggregated": 0,
            "master_workflow_id": None,
            "master_chat_session": None
        }

        try:
            # Step 1: Load all workflows
            workflows = self.load_all_workflows()
            result["workflows_loaded"] = len(workflows)

            if not workflows:
                logger.warning("⚠️  No workflows found to aggregate")
                return result

            # Step 2: Aggregate to master workflow
            master_workflow = self.aggregate_to_master_workflow(workflows)
            result["workflows_aggregated"] = len(workflows)
            result["master_workflow_id"] = master_workflow["master_workflow_id"]

            # Step 3: Save master workflow
            master_file = self.save_master_workflow(master_workflow)
            result["master_workflow_file"] = str(master_file)

            # Step 4: Create master chat session
            chat_result = self.create_master_chat_session(master_workflow)
            if chat_result.get("success"):
                result["master_chat_session"] = chat_result.get("session_id")
                result["messages_added"] = chat_result.get("messages_added", 0)

            result["success"] = True

            logger.info("="*80)
            logger.info("✅ AGGREGATION COMPLETE")
            logger.info("="*80)
            logger.info(f"   Workflows aggregated: {result['workflows_aggregated']}")
            logger.info(f"   Master workflow ID: {result['master_workflow_id']}")
            logger.info(f"   Master chat session: {result.get('master_chat_session', 'N/A')}")
            logger.info("")

        except Exception as e:
            logger.error(f"❌ Error during aggregation: {e}", exc_info=True)
            result["error"] = str(e)

        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate All Workflows to Master Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Aggregate all workflows to master
  python aggregate_workflows_to_master.py

  # Just load and show workflows (dry run)
  python aggregate_workflows_to_master.py --dry-run
        """
    )

    parser.add_argument("--dry-run", action="store_true",
                       help="Load workflows but don't aggregate (dry run)")

    args = parser.parse_args()

    aggregator = WorkflowAggregator()

    if args.dry_run:
        # Just load and show
        workflows = aggregator.load_all_workflows()
        print("\n" + "="*80)
        print("📋 WORKFLOWS FOUND")
        print("="*80)
        print(f"   Total workflows: {len(workflows)}")
        for wf in workflows[:10]:  # Show first 10
            print(f"   - {wf['workflow_name']} ({wf['workflow_id']})")
        if len(workflows) > 10:
            print(f"   ... and {len(workflows) - 10} more")
        print()
    else:
        # Full aggregation
        result = aggregator.aggregate_all()

        print("\n" + "="*80)
        print("📊 AGGREGATION RESULTS")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        print()


if __name__ == "__main__":


    main()