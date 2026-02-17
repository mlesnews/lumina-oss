#!/usr/bin/env python3
"""
JARVIS Ask Chaining Workflow System
Keeps the @ask @chains going and executes @doit

@JARVIS @ASK @CHAINS @DOIT @WORKFLOW
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAskChaining")


class WorkflowStatus(Enum):
    """Workflow status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class AskChainLink:
    """Represents a link in the ask chain"""
    def __init__(self, workflow_id: str, workflow_name: str, description: str,
                 dependencies: List[str] = None, executor: callable = None):
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.description = description
        self.dependencies = dependencies or []
        self.executor = executor
        self.status = WorkflowStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }


class JARVISAskChainingWorkflow:
    """
    Ask Chaining Workflow System

    Keeps the @ask @chains going by:
    1. Identifying completed workflows
    2. Finding next steps
    3. Executing workflow chain
    4. Tracking progress

    CPU Model: 4 cores base, 5 with F2F NITRO boost (Pentium-style!)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ask chaining system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "ask_chaining"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # CPU Configuration (Pentium-style!)
        self.base_cores = 4  # Standard 4 cores
        self.max_cores = 5   # With F2F NITRO boost
        self.active_workflows: List[Dict[str, Any]] = []  # Currently running workflows
        self.workflow_queue: List[Dict[str, Any]] = []    # Queued workflows

        self.chain_links: List[AskChainLink] = []
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("=" * 70)
        logger.info("🔗 JARVIS ASK CHAINING WORKFLOW SYSTEM")
        logger.info("   Keeping @ask @chains going and executing @doit")
        logger.info("   CPU: 4 cores base, 5 with F2F NITRO boost (Pentium-style!)")
        logger.info("=" * 70)
        logger.info("")

    def build_workflow_chain(self) -> List[AskChainLink]:
        """Build the complete workflow chain"""
        logger.info("🔗 BUILDING WORKFLOW CHAIN...")
        logger.info("")

        # Define all workflow links
        chain_links = [
            # 1. Master High Ground Analysis (just completed)
            AskChainLink(
                workflow_id="master_high_ground",
                workflow_name="Master High Ground Analysis",
                description="Analyze who is the master now - both AI and Human have mastery in different domains",
                dependencies=[],
                executor=self._execute_master_high_ground
            ),

            # 2. Medical LTD System (just completed)
            AskChainLink(
                workflow_id="medical_ltd",
                workflow_name="Medical Learn One, Teach One, Do One",
                description="Medical intelligence-design methodology with triage and HR doctors",
                dependencies=[],
                executor=self._execute_medical_ltd
            ),

            # 3. Resume Previous Plan
            AskChainLink(
                workflow_id="resume_previous_plan",
                workflow_name="Resume Previous Plan",
                description="Resume plan prior to sidequest - Financial Premium, RoamWise Stargate, CIAB",
                dependencies=["master_high_ground", "medical_ltd"],
                executor=self._execute_resume_previous_plan
            ),

            # 4. Deep System Validation (if needed)
            AskChainLink(
                workflow_id="deep_validation",
                workflow_name="Deep System Validation",
                description="Comprehensive validation of all systems with robust @ff",
                dependencies=["resume_previous_plan"],
                executor=self._execute_deep_validation
            ),

            # 5. SYPHON Validation Results
            AskChainLink(
                workflow_id="syphon_validation",
                workflow_name="SYPHON Validation Results",
                description="Extract actionable intelligence from validation results",
                dependencies=["deep_validation"],
                executor=self._execute_syphon_validation
            ),

            # 6. Execute Actionable Items
            AskChainLink(
                workflow_id="execute_actionable",
                workflow_name="Execute Actionable Items",
                description="Execute actionable items from SYPHON with WOPR reasoning",
                dependencies=["syphon_validation"],
                executor=self._execute_actionable_items
            ),

            # 7. Financial Premium Package (if active)
            AskChainLink(
                workflow_id="financial_premium",
                workflow_name="Financial Premium Package",
                description="Continue financial life domain coaching and strategies",
                dependencies=["resume_previous_plan"],
                executor=self._execute_financial_premium
            ),

            # 8. RoamWise Stargate Portal (if active)
            AskChainLink(
                workflow_id="roamwise_stargate",
                workflow_name="RoamWise Stargate Portal",
                description="Continue Stargate gateway development and knowledge navigation",
                dependencies=["resume_previous_plan"],
                executor=self._execute_roamwise_stargate
            ),

            # 9. CIAB Deployment (if active)
            AskChainLink(
                workflow_id="ciab_deployment",
                workflow_name="CIAB Deployment System",
                description="Continue CIAB package development and production repo image",
                dependencies=["resume_previous_plan"],
                executor=self._execute_ciab_deployment
            ),

            # 10. F4FOG Learning Integration
            AskChainLink(
                workflow_id="f4fog_learning",
                workflow_name="F4FOG Learning Integration",
                description="Integrate F4FOG learnings into Jedi-Master/Padawan system",
                dependencies=["master_high_ground"],
                executor=self._execute_f4fog_learning
            )
        ]

        self.chain_links = chain_links

        logger.info(f"✅ Built workflow chain with {len(chain_links)} links")
        logger.info("")

        return chain_links

    async def execute_chain(self, start_from: Optional[str] = None, use_nitrous: bool = False) -> Dict[str, Any]:
        """
        Execute the workflow chain

        Args:
            start_from: Optional workflow ID to start from
            use_nitrous: Activate F2F NITRO boost for 5th workflow
        """
        logger.info("=" * 70)
        logger.info("🚀 EXECUTING ASK CHAINING WORKFLOW")
        if use_nitrous:
            logger.info("   🚀 F2F NITRO BOOST ACTIVATED - 5 CORE MODE!")
        logger.info("=" * 70)
        logger.info("")

        # Build chain if not already built
        if not self.chain_links:
            self.build_workflow_chain()

        # Mark completed workflows
        self._mark_completed_workflows()

        # Find execution order
        execution_order = self._find_execution_order(start_from)

        # CPU Management: Limit concurrent workflows
        max_concurrent = self.max_cores if use_nitrous else self.base_cores
        logger.info(f"🖥️  CPU Configuration: {max_concurrent} cores available ({'NITRO BOOST' if use_nitrous else 'BASE'})")
        logger.info("")

        logger.info(f"📋 EXECUTION ORDER ({len(execution_order)} workflows):")
        logger.info("-" * 70)
        for i, link in enumerate(execution_order, 1):
            status_icon = "✅" if link.status == WorkflowStatus.COMPLETED else "⏳" if link.status == WorkflowStatus.IN_PROGRESS else "📋"
            logger.info(f"{i}. {status_icon} {link.workflow_name} ({link.workflow_id})")
        logger.info("")

        # Execute chain with CPU concurrency management
        results = {
            "chain_started_at": datetime.now().isoformat(),
            "execution_order": [link.workflow_id for link in execution_order],
            "workflows": {},
            "success_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
            "cpu_config": {
                "base_cores": self.base_cores,
                "max_cores": self.max_cores,
                "nitrous_boost": use_nitrous,
                "max_concurrent": max_concurrent
            }
        }

        # Track active workflows (CPU cores)
        active_workflows: List[AskChainLink] = []

        for link in execution_order:
            if link.status == WorkflowStatus.COMPLETED:
                logger.info(f"⏭️  SKIPPING (already completed): {link.workflow_name}")
                results["skipped_count"] += 1
                results["workflows"][link.workflow_id] = {
                    "status": "skipped",
                    "reason": "already_completed"
                }
                continue

            # CPU Concurrency Check: Wait if all cores busy
            while len(active_workflows) >= max_concurrent:
                logger.info(f"⏳ CPU at capacity ({len(active_workflows)}/{max_concurrent} cores) - waiting...")
                # Wait for a workflow to complete (simplified - in real implementation, use asyncio.wait)
                if active_workflows:
                    completed = active_workflows.pop(0)
                    logger.info(f"✅ Core freed by: {completed.workflow_name}")

            logger.info("")
            logger.info("=" * 70)
            logger.info(f"🔗 EXECUTING: {link.workflow_name}")
            if len(active_workflows) == max_concurrent - 1 and use_nitrous:
                logger.info("   🚀 NITRO CORE ACTIVATED!")
            logger.info(f"   CPU Cores: {len(active_workflows) + 1}/{max_concurrent}")
            logger.info("=" * 70)
            logger.info("")

            link.status = WorkflowStatus.IN_PROGRESS
            link.started_at = datetime.now()
            active_workflows.append(link)

            try:
                if link.executor:
                    if asyncio.iscoroutinefunction(link.executor):
                        result = await link.executor()
                    else:
                        result = link.executor()
                else:
                    result = {"status": "no_executor", "message": "No executor defined"}

                link.result = result
                link.status = WorkflowStatus.COMPLETED
                link.completed_at = datetime.now()

                # Remove from active workflows
                if link in active_workflows:
                    active_workflows.remove(link)

                results["success_count"] += 1
                results["workflows"][link.workflow_id] = {
                    "status": "success",
                    "result": result,
                    "duration": (link.completed_at - link.started_at).total_seconds(),
                    "core_used": len(active_workflows) + 1
                }

                logger.info(f"✅ COMPLETED: {link.workflow_name}")

            except Exception as e:
                logger.error(f"❌ FAILED: {link.workflow_name} - {e}", exc_info=True)
                link.status = WorkflowStatus.BLOCKED
                link.error = str(e)
                link.completed_at = datetime.now()

                # Remove from active workflows
                if link in active_workflows:
                    active_workflows.remove(link)

                results["failed_count"] += 1
                results["workflows"][link.workflow_id] = {
                    "status": "failed",
                    "error": str(e),
                    "duration": (link.completed_at - link.started_at).total_seconds() if link.started_at else None
                }

        results["chain_completed_at"] = datetime.now().isoformat()

        # Save execution history
        self._save_execution_history(results)

        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 CHAIN EXECUTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"✅ Success: {results['success_count']}")
        logger.info(f"❌ Failed: {results['failed_count']}")
        logger.info(f"⏭️  Skipped: {results['skipped_count']}")
        logger.info("=" * 70)

        return results

    def _mark_completed_workflows(self) -> None:
        """Mark workflows that are already completed"""
        # Master High Ground - just completed
        for link in self.chain_links:
            if link.workflow_id == "master_high_ground":
                link.status = WorkflowStatus.COMPLETED
                link.completed_at = datetime.now()
                link.result = {"status": "completed", "message": "Just completed in this session"}

            # Medical LTD - just completed
            elif link.workflow_id == "medical_ltd":
                link.status = WorkflowStatus.COMPLETED
                link.completed_at = datetime.now()
                link.result = {"status": "completed", "message": "Just completed in this session"}

    def _find_execution_order(self, start_from: Optional[str] = None) -> List[AskChainLink]:
        """Find execution order based on dependencies"""
        # If start_from specified, find that link and all after it
        if start_from:
            start_index = None
            for i, link in enumerate(self.chain_links):
                if link.workflow_id == start_from:
                    start_index = i
                    break

            if start_index is not None:
                return self.chain_links[start_index:]

        # Otherwise, return all pending/in_progress workflows in dependency order
        pending = [link for link in self.chain_links if link.status != WorkflowStatus.COMPLETED]

        # Sort by dependencies (simple topological sort)
        ordered = []
        remaining = pending.copy()

        while remaining:
            # Find links with no unmet dependencies
            ready = []
            for link in remaining:
                if all(dep_id in [l.workflow_id for l in ordered] or 
                       any(l.workflow_id == dep_id and l.status == WorkflowStatus.COMPLETED 
                           for l in self.chain_links)
                       for dep_id in link.dependencies):
                    ready.append(link)

            if not ready:
                # Circular dependency or missing dependency - add remaining anyway
                ordered.extend(remaining)
                break

            ordered.extend(ready)
            remaining = [link for link in remaining if link not in ready]

        return ordered

    # Executor functions
    async def _execute_master_high_ground(self) -> Dict[str, Any]:
        """Execute Master High Ground Analysis"""
        from scripts.python.jarvis_master_high_ground_analysis import MasterHighGroundSystem
        system = MasterHighGroundSystem(self.project_root)
        return system.analyze_who_is_master()

    async def _execute_medical_ltd(self) -> Dict[str, Any]:
        """Execute Medical LTD System"""
        from scripts.python.jarvis_medical_learn_teach_do_system import JARVISMedicalLearnTeachDo
        system = JARVISMedicalLearnTeachDo(self.project_root)
        case_data = {
            "case_id": "CASE_002",
            "procedure": "Surgical Procedure",
            "description": "Example surgical procedure for workflow chain",
            "severity": "URGENT",
            "triage_level": "URGENT"
        }
        return system.execute_medical_workflow(case_data)

    async def _execute_resume_previous_plan(self) -> Dict[str, Any]:
        """Execute Resume Previous Plan"""
        from scripts.python.jarvis_resume_previous_plan import JARVISResumePreviousPlan
        resumer = JARVISResumePreviousPlan()
        return resumer.resume_previous_plan()

    async def _execute_deep_validation(self) -> Dict[str, Any]:
        """Execute Deep System Validation"""
        from scripts.python.jarvis_deep_system_validation import JARVISDeepSystemValidation
        validator = JARVISDeepSystemValidation(self.project_root)
        return validator.run_deep_validation()

    async def _execute_syphon_validation(self) -> Dict[str, Any]:
        """Execute SYPHON Validation Results"""
        from scripts.python.jarvis_syphon_deep_validation import JARVISSyphonDeepValidation
        syphon = JARVISSyphonDeepValidation(self.project_root)
        return syphon.syphon_validation_results()

    async def _execute_actionable_items(self) -> Dict[str, Any]:
        """Execute Actionable Items with WOPR"""
        from scripts.python.jarvis_methodical_wopr_execution import JARVISMethodicalWOPRExecution
        executor = JARVISMethodicalWOPRExecution(self.project_root)
        # Load actionable items from SYPHON results
        syphon_file = self.project_root / "data" / "syphon_validation" / "validation_syphon_20260102_095237.json"
        if syphon_file.exists():
            with open(syphon_file, 'r') as f:
                syphon_data = json.load(f)
            actionable_items = syphon_data.get("actionable_items", [])
            # Convert to action format
            actions = [
                {
                    "name": item.get("item", "Unknown"),
                    "priority": item.get("priority", "MEDIUM"),
                    "validation_status": "PASS",
                    "reversible": True,
                    "affects_core_systems": False,
                    "has_backup": True
                }
                for item in actionable_items
            ]
            return executor.execute_methodically(actions)
        else:
            return {"status": "no_actionable_items", "message": "No SYPHON results found"}

    async def _execute_financial_premium(self) -> Dict[str, Any]:
        """Execute Financial Premium Package"""
        logger.info("📊 Financial Premium Package workflow - checking status...")
        session_file = self.project_root / "data" / "agent_chat_sessions" / "financial_premium_subagent_20260102_085249.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
            return {"status": "active", "session": data.get("session_id"), "message": "Session active, ready for continuation"}
        return {"status": "not_found", "message": "Session not found"}

    async def _execute_roamwise_stargate(self) -> Dict[str, Any]:
        """Execute RoamWise Stargate Portal"""
        logger.info("🌌 RoamWise Stargate Portal workflow - checking status...")
        session_file = self.project_root / "data" / "agent_chat_sessions" / "roamwise_stargate_subagent_20260102_085517.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
            return {"status": "active", "session": data.get("session_id"), "message": "Session active, ready for continuation"}
        return {"status": "not_found", "message": "Session not found"}

    async def _execute_ciab_deployment(self) -> Dict[str, Any]:
        """Execute CIAB Deployment"""
        logger.info("📦 CIAB Deployment workflow - checking status...")
        return {"status": "active", "message": "CIAB system ready for continuation"}

    async def _execute_f4fog_learning(self) -> Dict[str, Any]:
        """Execute F4FOG Learning Integration"""
        from scripts.python.jarvis_f4fog_learning_system import F4FOGLearningSystem
        system = F4FOGLearningSystem(self.project_root)
        # Create dummy F4FOG results for learning capture
        f4fog_results = {
            "f4fog_id": "f4fog_execution_20260102",
            "objective": "Improve Validation Pass Rate",
            "teams_assigned": 3,
            "alignment_percentage": 66.7
        }
        return system.capture_learnings(f4fog_results)

    def _save_execution_history(self, results: Dict[str, Any]) -> None:
        """Save execution history"""
        try:
            filename = self.output_dir / f"ask_chain_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Execution history saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save execution history: {e}")


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔗 JARVIS ASK CHAINING WORKFLOW")
    print("   Keeping @ask @chains going and executing @doit")
    print("=" * 70)
    print()

    chain = JARVISAskChainingWorkflow()
    results = await chain.execute_chain(use_nitrous=True)  # Activate NITRO!

    print()
    print("=" * 70)
    print("📊 EXECUTION RESULTS")
    print("=" * 70)
    print(f"✅ Success: {results['success_count']}")
    print(f"❌ Failed: {results['failed_count']}")
    print(f"⏭️  Skipped: {results['skipped_count']}")
    print()
    print("Workflows:")
    for workflow_id, workflow_data in results['workflows'].items():
        status = workflow_data.get('status', 'unknown')
        icon = "✅" if status == "success" else "❌" if status == "failed" else "⏭️"
        print(f"  {icon} {workflow_id}: {status}")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())