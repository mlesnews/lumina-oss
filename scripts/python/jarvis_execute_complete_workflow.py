#!/usr/bin/env python3
"""
JARVIS Complete Workflow Execution Chain
Connects all @ask @chains and executes complete workflow

@JARVIS @DOIT @CHAINS @EXECUTE
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCompleteWorkflow")

# Import Proactive IDE Troubleshooter
try:
    from scripts.python.jarvis_proactive_ide_troubleshooter import JARVISProactiveIDETroubleshooter
    PROACTIVE_TROUBLESHOOTER_AVAILABLE = True
except ImportError:
    PROACTIVE_TROUBLESHOOTER_AVAILABLE = False
    JARVISProactiveIDETroubleshooter = None
    logger.warning("⚠️  Proactive IDE Troubleshooter not available")


class JARVISCompleteWorkflowChain:
    """
    Complete Workflow Execution Chain

    Connects all systems:
    - Lock Issue Coordination
    - GOD LOOP System
    - Workflow Execution
    - Session Tracking
    - Helpdesk Integration
    - SYPHON Intelligence
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize complete workflow chain"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Import all systems
        from scripts.python.jarvis_helpdesk_integration import JARVISHelpdeskIntegration
        from scripts.python.jarvis_lock_issue_helpdesk_coordination import LockIssueHelpdeskCoordination
        from scripts.python.jarvis_god_loop_lock_repair import JARVISGodLoop
        from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

        self.helpdesk = JARVISHelpdeskIntegration(project_root=self.project_root)
        self.coordinator = LockIssueHelpdeskCoordination(project_root=self.project_root)
        self.god_loop = JARVISGodLoop(project_root=self.project_root)
        self.armoury_crate = create_armoury_crate_integration()

        # Initialize Live Monitor & Maintenance (progressive percentage tracking)
        try:
            from scripts.python.jarvis_live_monitor_maintenance import get_live_monitor
            from scripts.python.jarvis_progress_tracker import get_progress_tracker
            self.live_monitor = get_live_monitor(project_root=self.project_root)
            self.progress_tracker = get_progress_tracker(project_root=self.project_root, mode="bau")
            logger.info("✅ Live Monitor & Progressive Percentage Tracking initialized")
        except Exception as e:
            logger.warning(f"⚠️  Live Monitor initialization failed: {e}")
            self.live_monitor = None
            self.progress_tracker = None

        # Initialize Proactive IDE Troubleshooter
        self.proactive_troubleshooter = None
        if PROACTIVE_TROUBLESHOOTER_AVAILABLE:
            try:
                self.proactive_troubleshooter = JARVISProactiveIDETroubleshooter(self.project_root)
                logger.info("✅ Proactive IDE Troubleshooter initialized")
            except Exception as e:
                logger.warning(f"⚠️  Proactive IDE Troubleshooter initialization failed: {e}")

        # Initialize SYPHON-enhanced troubleshooting
        try:
            from scripts.python.jarvis_syphon_enhanced_troubleshooting import JARVISSyphonEnhancedTroubleshooting
            self.syphon_troubleshooter = JARVISSyphonEnhancedTroubleshooting(self.project_root)
            logger.info("✅ SYPHON-enhanced troubleshooting initialized")
        except Exception as e:
            logger.warning(f"⚠️  SYPHON troubleshooting not available: {e}")
            self.syphon_troubleshooter = None

        # Initialize @ASKChain SYPHON integration
        try:
            from scripts.python.jarvis_askchain_syphon_integration import JARVISAskChainSyphonIntegration
            self.askchain_syphon = JARVISAskChainSyphonIntegration(self.project_root)
            logger.info("✅ @ASKChain SYPHON integration initialized")
        except Exception as e:
            logger.warning(f"⚠️  @ASKChain SYPHON not available: {e}")
            self.askchain_syphon = None

        # Initialize WOPR Operations
        try:
            from scripts.python.wopr_ops import WOPROperations
            from scripts.python.wopr_status_report import WOPRStatusReport
            wopr_path = self.project_root / "data" / "wopr_plans"
            holocron_path = self.project_root / "data" / "holocron"
            self.wopr_ops = WOPROperations(wopr_path, holocron_path)
            self.wopr_status = WOPRStatusReport(wopr_path)
            logger.info("✅ WOPR Operations initialized")
        except Exception as e:
            logger.warning(f"⚠️  WOPR not available: {e}")
            self.wopr_ops = None
            self.wopr_status = None

        logger.info("✅ Complete Workflow Chain initialized")

    async def execute_complete_chain(self) -> Dict[str, Any]:
        """
        Execute complete workflow chain

        Chain:
        1. Start session tracking
        2. Create helpdesk coordination
        3. Execute GOD LOOP (if needed)
        4. Run workflow with verification
        5. Track results
        6. Archive session
        """
        logger.info("=" * 70)
        logger.info("🔗 EXECUTING COMPLETE WORKFLOW CHAIN")
        logger.info("=" * 70)
        logger.info("   Progressive percentage tracking")
        logger.info("   Ongoing live monitoring & maintenance")
        logger.info("")

        results = {
            "chain_steps": [],
            "session_id": None,
            "success": False,
            "progressive_percentage": {},
            "system_health": {}
        }

        try:
            # STEP 0: Ensure live monitoring is active
            if self.live_monitor and not self.live_monitor.monitoring_active:
                logger.info("🔗 STEP 0: Starting live monitoring...")
                self.live_monitor.start_monitoring()
                logger.info("✅ Live monitoring active (updates every 0.5s)")
                results["chain_steps"].append({
                    "step": 0,
                    "name": "Live Monitoring",
                    "status": "success",
                    "monitoring": "active"
                })

            # STEP 1: Start session tracking
            logger.info("🔗 STEP 1: Starting session tracking...")
            session = self.coordinator.start_chat_session(
                agents=["JARVIS", "WORKFLOW", "HELPDESK", "GOD_LOOP", "SYPHON"]
            )
            results["session_id"] = session.session_id
            results["chain_steps"].append({
                "step": 1,
                "name": "Session Tracking",
                "status": "success",
                "session_id": session.session_id
            })

            self.coordinator.add_message_to_session(
                session.session_id,
                "JARVIS",
                "Complete workflow chain execution initiated",
                "system"
            )

            # STEP 1.5: Start Proactive IDE Troubleshooter
            if self.proactive_troubleshooter:
                logger.info("🔗 STEP 1.5: Starting Proactive IDE Troubleshooter...")
                self.proactive_troubleshooter.start_monitoring()
                results["chain_steps"].append({
                    "step": 1.5,
                    "name": "Proactive IDE Troubleshooter",
                    "status": "success",
                    "monitoring": "active"
                })
                logger.info("✅ Proactive IDE Troubleshooter monitoring started")

            # STEP 2: Helpdesk coordination
            logger.info("🔗 STEP 2: Executing helpdesk coordination...")
            try:
                coordination_result = await self.coordinator.coordinate_lock_issue_resolution()
                results["chain_steps"].append({
                    "step": 2,
                    "name": "Helpdesk Coordination",
                    "status": "success" if coordination_result.get("success") else "partial",
                    "result": coordination_result
                })

                self.coordinator.add_message_to_session(
                    session.session_id,
                    "HELPDESK",
                    f"Coordination complete: {coordination_result.get('message', 'Unknown')}"
                )
            except Exception as e:
                logger.warning(f"Helpdesk coordination had issues: {e}")
                results["chain_steps"].append({
                    "step": 2,
                    "name": "Helpdesk Coordination",
                    "status": "partial",
                    "error": str(e)
                })

            # STEP 3: Check if GOD LOOP needed
            logger.info("🔗 STEP 3: Checking if GOD LOOP needed...")
            lock_states = await self.god_loop._check_lock_states()

            needs_god_loop = False
            if lock_states:
                # Check if any locks are problematic
                for key, value in lock_states.items():
                    if isinstance(value, dict):
                        state = value.get('state', '')
                        if state in ['ON', 'UNKNOWN']:
                            needs_god_loop = True
                            break

            if needs_god_loop:
                logger.info("🔗 STEP 3b: Executing GOD LOOP...")
                self.coordinator.add_message_to_session(
                    session.session_id,
                    "GOD_LOOP",
                    "GOD LOOP initiated for continuous repair"
                )

                await self.god_loop.run_god_loop(
                    max_cycles=5,
                    cycle_interval=3.0,
                    stop_on_success=True
                )

                results["chain_steps"].append({
                    "step": 3,
                    "name": "GOD LOOP",
                    "status": "success",
                    "cycles": self.god_loop.cycle_count
                })
            else:
                logger.info("🔗 STEP 3: GOD LOOP not needed - locks appear OK")
                results["chain_steps"].append({
                    "step": 3,
                    "name": "GOD LOOP Check",
                    "status": "skipped",
                    "reason": "Locks appear OK"
                })

            # STEP 4: Execute workflow with verification
            logger.info("🔗 STEP 4: Executing workflow with verification...")

            def workflow_executor(data: Dict[str, Any]) -> Dict[str, Any]:
                """Workflow executor for disable lighting"""
                # Run async function in sync context
                try:
                    # Check if there's already a running event loop
                    loop = asyncio.get_running_loop()
                    # If we're in an async context, we need to use nest_asyncio or create_task
                    # For now, use a thread to run the async function
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.run(
                                self.armoury_crate.process_request({
                                    'action': 'disable_all_lighting'
                                })
                            )
                        )
                        result = future.result()
                        return result
                except RuntimeError:
                    # No running loop, we can create one
                    result = asyncio.run(
                        self.armoury_crate.process_request({
                            'action': 'disable_all_lighting'
                        })
                    )
                    return result

            workflow_data = {
                "workflow_id": f"disable_all_lighting_{session.session_id}",
                "workflow_name": "disable_all_lighting",
                "action": "disable_all_lighting"
            }

            success, workflow_results = self.helpdesk.execute_workflow_with_verification(
                workflow_data=workflow_data,
                workflow_executor=workflow_executor,
                track_session=True,
                enable_god_loop=False  # Already ran if needed
            )

            results["chain_steps"].append({
                "step": 4,
                "name": "Workflow Execution",
                "status": "success" if success else "failed",
                "result": workflow_results
            })

            self.coordinator.add_message_to_session(
                session.session_id,
                "WORKFLOW",
                f"Workflow execution: {'✅ Success' if success else '❌ Failed'}"
            )

            # STEP 5: Track results and add resolution
            logger.info("🔗 STEP 5: Tracking results...")

            try:
                if success:
                    resolution = "Complete workflow chain executed successfully"
                else:
                    resolution = f"Workflow chain completed with issues: {workflow_results.get('error', 'Unknown')}"

                # Add resolution to session
                self.coordinator.add_resolution_to_session(
                    session.session_id,
                    resolution
                )
            except Exception as e:
                logger.warning(f"Resolution tracking had issues: {e}")

            results["chain_steps"].append({
                "step": 5,
                "name": "Result Tracking",
                "status": "success"
            })

            # STEP 6: Save session
            logger.info("🔗 STEP 6: Saving session...")
            self.coordinator.save_session(session.session_id)

            results["chain_steps"].append({
                "step": 6,
                "name": "Session Save",
                "status": "success"
            })

            results["success"] = success

            # Get final progressive percentage and system health
            if self.live_monitor:
                live_status = self.live_monitor.get_live_status()
                results["progressive_percentage"] = live_status.get("progressive_percentage", {})
                results["system_health"] = live_status.get("system_health", {})

                progressive = results["progressive_percentage"]
                health = results["system_health"]

                logger.info("")
                logger.info("📊 PROGRESSIVE PERCENTAGE & SYSTEM HEALTH")
                logger.info(f"   Overall Progress: {progressive.get('overall', 0.0):.1f}%")
                logger.info(f"   System Health: {health.get('overall_health_percent', 0.0):.1f}%")
                logger.info(f"   Processes Running: {health.get('processes_running', 0)}")
                logger.info(f"   Active Processes: {progressive.get('active_processes', 0)}")
                logger.info(f"   Total Sources: {progressive.get('total_sources', 0)}")
                logger.info(f"   ETA: {progressive.get('eta', 'N/A')}")
                logger.info("")
                logger.info("✅ Live monitoring continues in background")

            logger.info("=" * 70)
            logger.info("✅ COMPLETE WORKFLOW CHAIN EXECUTED")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"Chain execution error: {e}", exc_info=True)
            results["success"] = False
            results["error"] = str(e)

            if results.get("session_id"):
                try:
                    self.coordinator.add_message_to_session(
                        results["session_id"],
                        "ERROR",
                        f"Chain execution failed: {str(e)}"
                    )
                    self.coordinator.save_session(results["session_id"])
                except:
                    pass

        return results


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔗 JARVIS COMPLETE WORKFLOW CHAIN EXECUTION")
    print("   Connecting all @ask @chains and executing @doit")
    print("=" * 70)
    print()

    chain = JARVISCompleteWorkflowChain()
    results = await chain.execute_complete_chain()

    print()
    print("=" * 70)
    print("📊 EXECUTION RESULTS")
    print("=" * 70)
    print(f"Success: {results.get('success', False)}")
    print(f"Session ID: {results.get('session_id', 'N/A')}")
    print(f"Chain Steps: {len(results.get('chain_steps', []))}")
    print()

    for step in results.get('chain_steps', []):
        status_icon = "✅" if step.get('status') == 'success' else "⚠️" if step.get('status') == 'partial' else "❌"
        print(f"{status_icon} Step {step.get('step')}: {step.get('name')} - {step.get('status')}")

    print()
    print("=" * 70)
    print("✅ COMPLETE WORKFLOW CHAIN EXECUTION FINISHED")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())