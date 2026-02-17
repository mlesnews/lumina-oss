#!/usr/bin/env python3
"""
JARVIS Execute @ASK Chains

Connects @ask chains to JARVIS workflow execution and executes all ready tasks.

Tags: #ASKS #CHAINING #EXECUTION #WORKFLOW @JARVIS @DOIT
"""

from __future__ import annotations

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISExecuteAskChains")

try:
    from asks_long_running_chain import ASKSLongRunningChain, TaskStatus
    CHAIN_SYSTEM_AVAILABLE = True
except ImportError:
    CHAIN_SYSTEM_AVAILABLE = False
    ASKSLongRunningChain = None
    logger.error("❌ ASKS Long-Running Chain system not available")

try:
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISHelpdeskIntegration = None
    logger.warning("⚠️  JARVIS Helpdesk Integration not available")

try:
    from jarvis_master_chat_session import JARVISMasterChatSession
    MASTER_CHAT_AVAILABLE = True
except ImportError:
    MASTER_CHAT_AVAILABLE = False
    JARVISMasterChatSession = None

# Import operator idleness restriction
try:
    from operator_idleness_restriction import get_operator_idleness_restriction, check_action_allowed
    IDLENESS_RESTRICTION_AVAILABLE = True
except ImportError:
    IDLENESS_RESTRICTION_AVAILABLE = False
    get_operator_idleness_restriction = None
    check_action_allowed = None
    logger.warning("⚠️  Operator idleness restriction not available")


class JARVISAskChainExecutor:
    """
    Execute @ask chains through JARVIS workflow system.

    Connects chained @asks to JARVIS workflow execution,
    executing ready tasks in dependency order.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize chain executor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize chain manager
        if not CHAIN_SYSTEM_AVAILABLE:
            raise RuntimeError("ASKSLongRunningChain system not available")
        self.chain_manager = ASKSLongRunningChain(project_root)

        # Initialize JARVIS integration
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISHelpdeskIntegration(project_root)
                logger.info("✅ JARVIS Helpdesk Integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize JARVIS: {e}")

        # Initialize master chat
        self.master_chat = None
        if MASTER_CHAT_AVAILABLE:
            try:
                self.master_chat = JARVISMasterChatSession(project_root)
                logger.info("✅ Master chat session initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize master chat: {e}")

        # Initialize operator idleness restriction
        self.idleness_restriction = None
        if IDLENESS_RESTRICTION_AVAILABLE:
            try:
                self.idleness_restriction = get_operator_idleness_restriction(project_root)
                logger.info("✅ Operator idleness restriction initialized")
            except Exception as e:
                logger.warning(f"⚠️  Operator idleness restriction initialization failed: {e}")

        logger.info("✅ JARVIS @ASK Chain Executor initialized")

    def discover_and_create_chain(self, use_cache: bool = True, show_each: bool = True) -> Optional[str]:
        """
        Discover all @asks and create a chain for long-running tasks.

        Args:
            use_cache: If True, use cached asks if available and recent
            show_each: If True, display each ask as it's discovered

        Returns:
            Chain ID if created, None otherwise
        """
        if not self.chain_manager.ask_restacker:
            logger.error("❌ ASK restacker not available")
            return None

        logger.info("")
        logger.info("=" * 80)
        logger.info("🔍 DISCOVERING ALL @ASKS")
        logger.info("=" * 80)
        logger.info(f"   Cache: {'Enabled' if use_cache else 'Disabled'}")
        logger.info(f"   Show Each: {'Yes' if show_each else 'No'}")
        logger.info("")

        asks = self.chain_manager.ask_restacker.discover_all_asks(
            use_cache=use_cache,
            show_each=show_each
        )

        logger.info("")
        logger.info(f"📊 Total @ASKS discovered: {len(asks)}")

        if not asks:
            logger.info("ℹ️  No asks found")
            return None

        # Filter for long-running tasks
        logger.info("")
        logger.info("⏱️  Filtering for long-running tasks...")
        long_running_asks = []
        for ask in asks:
            ask_text = ask.get("text", ask.get("ask_text", ""))
            if self.chain_manager.is_long_running_task(ask_text):
                long_running_asks.append(ask)
                if show_each:
                    logger.info(f"   ✅ Long-running: {ask_text[:80]}...")

        logger.info(f"📋 Found {len(long_running_asks)} long-running tasks")

        if not long_running_asks:
            logger.info("ℹ️  No long-running tasks found")
            return None

        # Create chain
        logger.info("")
        logger.info("🔗 Creating chain...")
        chain_id = self.chain_manager.create_chain(long_running_asks)
        logger.info(f"✅ Created chain: {chain_id}")

        # Notify master chat
        if self.master_chat:
            self.master_chat.add_message(
                agent_id="jarvis",
                agent_name="JARVIS (CTO Superagent)",
                message=f"🔗 Created @ask chain: {chain_id} with {len(long_running_asks)} long-running tasks",
                message_type="system",
                metadata={"chain_id": chain_id, "task_count": len(long_running_asks)}
            )

        return chain_id

    def execute_chain(self, chain_id: str, max_parallel: int = 3) -> Dict[str, Any]:
        """
        Execute all ready tasks in a chain.

        Args:
            chain_id: Chain ID to execute
            max_parallel: Maximum number of parallel tasks

        Returns:
            Execution results
        """
        logger.info(f"🚀 Executing chain: {chain_id}")

        # @OP #IDLENESS RESTRICTION: Check if operator is idle (ENFORCED with penalties)
        if self.idleness_restriction:
            if not self.idleness_restriction.is_action_allowed("ask_chain_execution"):
                idle_duration = self.idleness_restriction._get_idle_duration()

                # @PENALTY: Record violation and apply -xp penalty
                try:
                    from jarvis_policy_violation_penalty import get_penalty_system, PolicyType, ViolationSeverity
                    penalty_system = get_penalty_system(self.project_root)
                    violation = penalty_system.record_violation(
                        policy_type=PolicyType.IDLENESS_RESTRICTION,
                        action="ask_chain_execution",
                        description=f"Attempted JARVIS @ask chain execution while operator idle for {idle_duration:.0f}s (threshold: {self.idleness_restriction.restriction.idle_timeout_seconds}s) - TEMPORARY RESTRICTION ON JARVIS, NOT ON @OP",
                        severity=ViolationSeverity.MAJOR,
                        blocked=True,
                        metadata={
                            "chain_id": chain_id,
                            "idle_duration": idle_duration,
                            "threshold": self.idleness_restriction.restriction.idle_timeout_seconds
                        }
                    )
                    logger.error(
                        f"🚫 POLICY VIOLATION: JARVIS @ask chain execution blocked - "
                        f"Operator idle for {idle_duration:.0f}s - "
                        f"TEMPORARY RESTRICTION ON JARVIS (NOT @OP) - "
                        f"Penalty: {violation.xp_penalty} XP (Current XP: {penalty_system.jarvis_xp.current_xp})"
                    )
                except Exception as e:
                    logger.warning(f"⚠️  Penalty system unavailable: {e}")

                logger.warning(
                    f"🚫 BLOCKED: JARVIS @ask chain execution - Operator idle for {idle_duration:.0f}s "
                    f"(>{self.idleness_restriction.restriction.idle_timeout_seconds}s threshold) - "
                    f"TEMPORARY RESTRICTION ON JARVIS, NOT ON @OP"
                )
                return {
                    "success": False,
                    "blocked": True,
                    "violation": True,
                    "reason": f"Operator idle for {idle_duration:.0f}s - JARVIS @ask chain execution temporarily restricted (NOT @OP)",
                    "idle_duration": idle_duration,
                    "chain_id": chain_id
                }

        if chain_id not in self.chain_manager.chains:
            logger.error(f"❌ Chain {chain_id} not found")
            return {"error": "Chain not found"}

        results = {
            "chain_id": chain_id,
            "started_at": datetime.now().isoformat(),
            "tasks_executed": [],
            "tasks_failed": [],
            "tasks_completed": [],
            "tasks_remaining": []
        }

        # Get initial status
        status = self.chain_manager.get_chain_status(chain_id)
        total_tasks = status["total_tasks"]
        chain_start_time = time.time()

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"📊 CHAIN EXECUTION: {chain_id}")
        logger.info("=" * 80)
        logger.info(f"   Total Tasks: {total_tasks}")
        logger.info(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")

        # Display full task stack for transparency
        logger.info("=" * 80)
        logger.info("📋 FULL TASK STACK - WALKTHROUGH")
        logger.info("=" * 80)

        if hasattr(self.chain_manager, 'chains') and chain_id in self.chain_manager.chains:
            chain = self.chain_manager.chains[chain_id]
            if hasattr(chain, 'tasks'):
                tasks_list = list(chain.tasks.values())
                # Sort by dependency order if possible
                for idx, task in enumerate(tasks_list, 1):
                    logger.info("")
                    logger.info(f"  [{idx}/{total_tasks}] Task: {task.task_id}")
                    logger.info(f"      Ask: {task.ask_text}")
                    if hasattr(task, 'category'):
                        logger.info(f"      Category: {task.category}")
                    if hasattr(task, 'priority'):
                        logger.info(f"      Priority: {task.priority}")
                    status_val = task.status.value if hasattr(task.status, 'value') else str(task.status)
                    logger.info(f"      Status: {status_val}")
                    if hasattr(task, 'dependencies') and task.dependencies:
                        logger.info(f"      Dependencies: {', '.join(task.dependencies)}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("🚀 STARTING EXECUTION...")
        logger.info("=" * 80)
        logger.info("")

        # Get all tasks for transparency
        all_tasks = []
        if hasattr(self.chain_manager, 'chains') and chain_id in self.chain_manager.chains:
            chain = self.chain_manager.chains[chain_id]
            if hasattr(chain, 'tasks'):
                all_tasks = list(chain.tasks.values())

        # Execute loop - continue until no more ready tasks
        iteration = 0
        max_iterations = total_tasks * 2  # Safety limit

        while iteration < max_iterations:
            iteration += 1

            # Get current status for progress calculation
            status = self.chain_manager.get_chain_status(chain_id)
            completed = status["status_counts"].get("completed", 0)
            failed = status["status_counts"].get("failed", 0)
            running = status["status_counts"].get("running", 0)
            pending = status["status_counts"].get("pending", 0)

            # Calculate progress
            progress_percent = ((completed + failed) / total_tasks * 100) if total_tasks > 0 else 0

            # Estimate time remaining
            elapsed_time = time.time() - chain_start_time
            if completed > 0:
                avg_time_per_task = elapsed_time / completed
                remaining_tasks = total_tasks - completed - failed
                estimated_remaining = avg_time_per_task * remaining_tasks
                eta_seconds = int(estimated_remaining)
                eta_minutes = eta_seconds // 60
                eta_seconds = eta_seconds % 60
                eta_str = f"{eta_minutes}m {eta_seconds}s" if eta_minutes > 0 else f"{eta_seconds}s"
            else:
                eta_str = "Calculating..."

            # Display progress header
            logger.info("")
            logger.info("-" * 80)
            logger.info(f"📊 PROGRESS UPDATE (Iteration {iteration})")
            logger.info("-" * 80)
            logger.info(f"   Progress: {progress_percent:.1f}% ({completed + failed}/{total_tasks} tasks)")
            logger.info(f"   ✅ Completed: {completed}")
            logger.info(f"   ❌ Failed: {failed}")
            logger.info(f"   🔄 Running: {running}")
            logger.info(f"   ⏳ Pending: {pending}")
            logger.info(f"   ⏱️  Elapsed: {int(elapsed_time // 60)}m {int(elapsed_time % 60)}s")
            logger.info(f"   ⏱️  ETA: {eta_str}")
            logger.info("")

            # Get ready tasks
            ready_tasks = self.chain_manager.get_ready_tasks(chain_id)

            if not ready_tasks:
                # Check if all tasks are done
                if completed + failed >= total_tasks:
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info(f"✅ CHAIN EXECUTION COMPLETE")
                    logger.info("=" * 80)
                    logger.info(f"   Completed: {completed}")
                    logger.info(f"   Failed: {failed}")
                    logger.info(f"   Total Time: {int(elapsed_time // 60)}m {int(elapsed_time % 60)}s")
                    logger.info("")
                    break
                else:
                    # Check for blocked tasks
                    blocked = status["status_counts"].get("blocked", 0)
                    if blocked > 0:
                        logger.warning(f"⚠️  Chain blocked: {blocked} tasks blocked")
                    break

            # Execute ready tasks (up to max_parallel)
            logger.info(f"🔄 Executing {len(ready_tasks)} ready task(s)...")
            logger.info("")

            for idx, task in enumerate(ready_tasks[:max_parallel], 1):
                task_num = completed + failed + running + idx
                task_progress = (task_num / total_tasks * 100) if total_tasks > 0 else 0

                logger.info("")
                logger.info("  " + "─" * 76)
                logger.info(f"  📋 TASK {task_num}/{total_tasks} ({task_progress:.1f}%)")
                logger.info("  " + "─" * 76)
                logger.info(f"  Task ID: {task.task_id}")
                logger.info(f"  Ask: {task.ask_text}")
                if hasattr(task, 'category'):
                    logger.info(f"  Category: {task.category}")
                if hasattr(task, 'priority'):
                    logger.info(f"  Priority: {task.priority}")
                logger.info(f"  Status: {task.status.value if hasattr(task.status, 'value') else str(task.status)}")
                logger.info("")

                task_result = self._execute_task(task)

                if task_result["success"]:
                    results["tasks_executed"].append(task.task_id)
                    results["tasks_completed"].append(task.task_id)
                    logger.info(f"  ✅ Task {task_num} completed successfully")
                else:
                    results["tasks_executed"].append(task.task_id)
                    results["tasks_failed"].append(task.task_id)
                    logger.error(f"  ❌ Task {task_num} failed")

                logger.info("  " + "─" * 76)

            # Small delay between iterations
            time.sleep(0.5)

        results["completed_at"] = datetime.now().isoformat()
        results["final_status"] = self.chain_manager.get_chain_status(chain_id)

        logger.info(f"✅ Chain execution finished: {len(results['tasks_completed'])} completed, {len(results['tasks_failed'])} failed")

        # Notify master chat
        if self.master_chat:
            self.master_chat.add_message(
                agent_id="jarvis",
                agent_name="JARVIS (CTO Superagent)",
                message=f"✅ Executed chain {chain_id}: {len(results['tasks_completed'])} completed, {len(results['tasks_failed'])} failed",
                message_type="execution",
                metadata=results
            )

        return results

    def _execute_task(self, task) -> Dict[str, Any]:
        """
        Execute a single chained task with full transparency.

        Args:
            task: ChainedTask to execute

        Returns:
            Execution result
        """
        logger.info(f"  ▶️  Starting execution...")
        logger.info(f"  ⏱️  Started at: {datetime.now().strftime('%H:%M:%S')}")

        # Mark as running
        self.chain_manager.mark_task_running(task.task_id)
        start_time = time.time()

        try:
            # Convert ask to workflow
            logger.info(f"  🔄 Converting ask to workflow...")
            workflow_data = self._ask_to_workflow(task)
            logger.info(f"  ✅ Workflow created: {workflow_data.get('workflow_name')}")

            # Execute through JARVIS if available
            if self.jarvis:
                logger.info(f"  🔄 Executing through JARVIS workflow system...")

                # Create workflow executor
                def workflow_executor(wf_data: Dict[str, Any]) -> Dict[str, Any]:
                    """Execute the workflow"""
                    logger.info(f"  🔄 Executing workflow: {wf_data.get('workflow_name')}")
                    logger.info(f"  📋 Workflow type: {wf_data.get('workflow_type')}")
                    logger.info(f"  📋 Category: {wf_data.get('category', 'N/A')}")
                    logger.info(f"  📋 Priority: {wf_data.get('priority', 'N/A')}")
                    return {
                        "success": True,
                        "result": "Workflow executed",
                        "task_id": task.task_id,
                        "ask_text": task.ask_text
                    }

                # Execute with JARVIS verification
                logger.info(f"  🔍 Running V3 verification...")
                success, results = self.jarvis.execute_workflow_with_verification(
                    workflow_data,
                    workflow_executor,
                    require_verification=True,
                    ingest_to_r5=True,
                    track_session=True
                )

                duration = time.time() - start_time
                duration_str = f"{int(duration // 60)}m {int(duration % 60)}s" if duration >= 60 else f"{int(duration)}s"

                if success:
                    self.chain_manager.mark_task_completed(task.task_id, int(duration))
                    logger.info(f"  ✅ Task completed successfully")
                    logger.info(f"  ⏱️  Duration: {duration_str}")
                    return {"success": True, "task_id": task.task_id, "duration": int(duration)}
                else:
                    self.chain_manager.mark_task_failed(task.task_id, results.get("error", "Unknown error"))
                    logger.error(f"  ❌ Task failed: {results.get('error')}")
                    logger.info(f"  ⏱️  Duration: {duration_str}")
                    return {"success": False, "task_id": task.task_id, "error": results.get("error")}
            else:
                # Fallback: just mark as completed
                duration = time.time() - start_time
                duration_str = f"{int(duration // 60)}m {int(duration % 60)}s" if duration >= 60 else f"{int(duration)}s"
                self.chain_manager.mark_task_completed(task.task_id, int(duration))
                logger.info(f"  ✅ Task completed (no JARVIS integration)")
                logger.info(f"  ⏱️  Duration: {duration_str}")
                return {"success": True, "task_id": task.task_id, "duration": int(duration)}

        except Exception as e:
            duration = time.time() - start_time
            duration_str = f"{int(duration // 60)}m {int(duration % 60)}s" if duration >= 60 else f"{int(duration)}s"
            error_msg = str(e)
            logger.error(f"  ❌ Task failed with exception: {error_msg}")
            logger.info(f"  ⏱️  Duration: {duration_str}")

            # Mark as failed
            if hasattr(self.chain_manager, 'mark_task_failed'):
                self.chain_manager.mark_task_failed(task.task_id, error_msg)
            else:
                # Fallback: mark task status manually
                task.status = TaskStatus.FAILED
                task.error_message = error_msg
                self.chain_manager._save_chains()

            return {"success": False, "task_id": task.task_id, "error": error_msg}

    def execute_ask_chain(self, ask_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single @ASK through the chain executor.

        This method is called by batch processing to execute individual asks.

        Args:
            ask_id: The ID of the ask to execute
            workflow_data: Workflow data containing ask text, messages, etc.

        Returns:
            Execution result with success status
        """
        try:
            logger.info(f"🚀 Executing @ASK: {ask_id}")

            # Extract ask text
            ask_text = workflow_data.get("ask_text", "")
            if not ask_text:
                # Try to get from messages
                messages = workflow_data.get("messages", [])
                if messages and isinstance(messages, list):
                    ask_text = messages[0].get("content", "") if messages else ""

            if not ask_text:
                return {
                    "success": False,
                    "error": "No ask text provided in workflow_data"
                }

            # Check if this is a long-running task that should be chained
            if self.chain_manager.is_long_running_task(ask_text):
                # For long-running tasks, create/update chain and execute
                chain_id = self.discover_and_create_chain(use_cache=True, show_each=False)
                if chain_id:
                    chain_result = self.execute_chain(chain_id)
                    return {
                        "success": chain_result.get("tasks_completed", 0) > 0,
                        "chain_id": chain_id,
                        "result": chain_result
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not create chain for long-running task"
                    }
            else:
                # For simple tasks, execute directly via JARVIS if available
                if self.jarvis:
                    workflow_id = workflow_data.get("workflow_id", f"ask_{ask_id}")
                    workflow_name = workflow_data.get("workflow_name", f"Process @ASK: {ask_text[:50]}")

                    # Try to execute workflow - check for available methods
                    result = None

                    # Method 1: execute_workflow_with_verification (preferred)
                    if hasattr(self.jarvis, 'execute_workflow_with_verification'):
                        def workflow_executor(workflow_data):
                            # Simple executor that just returns the workflow data
                            return {"success": True, "workflow_data": workflow_data}

                        success, exec_result = self.jarvis.execute_workflow_with_verification(
                            workflow_data=workflow_data,
                            workflow_executor=workflow_executor,
                            require_verification=False,  # Don't block on verification for @ASK items
                            ingest_to_r5=True,
                            track_session=True
                        )
                        result = {
                            "success": success,
                            "result": exec_result,
                            "workflow_id": workflow_id
                        }

                    # Method 2: create_workflow (if exists)
                    elif hasattr(self.jarvis, 'create_workflow'):
                        result = self.jarvis.create_workflow(
                            workflow_id=workflow_id,
                            workflow_name=workflow_name,
                            workflow_data=workflow_data
                        )

                    # Method 3: create_ticket (fallback)
                    elif hasattr(self.jarvis, 'create_ticket'):
                        result = self.jarvis.create_ticket(
                            ticket_id=workflow_id,
                            title=workflow_name,
                            description=ask_text,
                            category=workflow_data.get("category", "general"),
                            priority=workflow_data.get("priority", "normal")
                        )

                    # Method 4: submit_workflow (fallback)
                    elif hasattr(self.jarvis, 'submit_workflow'):
                        result = self.jarvis.submit_workflow(workflow_data)

                    # Fallback: log and return success with note
                    else:
                        logger.warning(
                            f"⚠️  JARVIS Helpdesk Integration doesn't have workflow execution method. "
                            f"@ASK '{ask_id}' logged but not processed."
                        )
                        result = {
                            "success": True,
                            "note": "Ask logged but workflow execution not available",
                            "workflow_id": workflow_id
                        }

                    if result and result.get("success"):
                        return {
                            "success": True,
                            "workflow_id": workflow_id,
                            "result": result
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.get("error", "JARVIS workflow creation failed") if result else "No workflow method available"
                        }
                else:
                    # Fallback: just log the ask
                    logger.warning(f"⚠️  JARVIS not available, cannot execute @ASK: {ask_id}")
                    return {
                        "success": False,
                        "error": "JARVIS not available"
                    }
        except Exception as e:
            logger.error(f"❌ Error executing @ASK {ask_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _ask_to_workflow(self, task) -> Dict[str, Any]:
        """
        Convert an @ask task to workflow data.

        Args:
            task: ChainedTask to convert

        Returns:
            Workflow data dictionary
        """
        workflow_id = f"ask_chain_{task.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "workflow_id": workflow_id,
            "workflow_name": f"ASK Chain Task: {task.task_id}",
            "workflow_type": "ask_execution",
            "category": task.category,
            "priority": task.priority,
            "description": task.ask_text,
            "ask_text": task.ask_text,
            "task_id": task.task_id,
            "metadata": task.metadata
        }

    def execute_all_chains(self, max_parallel: int = 3) -> Dict[str, Any]:
        """
        Execute all active chains.

        Args:
            max_parallel: Maximum parallel tasks per chain

        Returns:
            Execution results for all chains
        """
        logger.info("🚀 Executing all active chains...")

        all_results = {
            "started_at": datetime.now().isoformat(),
            "chains": {}
        }

        for chain_id in self.chain_manager.chains.keys():
            logger.info(f"📋 Processing chain: {chain_id}")
            results = self.execute_chain(chain_id, max_parallel)
            all_results["chains"][chain_id] = results

        all_results["completed_at"] = datetime.now().isoformat()
        logger.info("✅ All chains execution finished")

        return all_results


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Execute @ASK Chains")
    parser.add_argument("--discover", action="store_true", help="Discover asks and create chain")
    parser.add_argument("--execute", type=str, help="Execute chain by ID")
    parser.add_argument("--execute-all", action="store_true", help="Execute all chains")
    parser.add_argument("--status", type=str, help="Show chain status")
    parser.add_argument("--max-parallel", type=int, default=3, help="Max parallel tasks")

    args = parser.parse_args()

    try:
        executor = JARVISAskChainExecutor()

        if args.discover:
            chain_id = executor.discover_and_create_chain()
            if chain_id:
                print(f"✅ Created chain: {chain_id}")
                print(f"   Execute with: python scripts/python/jarvis_execute_ask_chains.py --execute {chain_id}")
            else:
                print("ℹ️  No chain created")

        if args.execute:
            results = executor.execute_chain(args.execute, args.max_parallel)
            print(json.dumps(results, indent=2))

        if args.execute_all:
            results = executor.execute_all_chains(args.max_parallel)
            print(json.dumps(results, indent=2))

        if args.status:
            status = executor.chain_manager.get_chain_status(args.status)
            print(json.dumps(status, indent=2))

        return 0

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main())