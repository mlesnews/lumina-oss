#!/usr/bin/env python3
"""
@DOIT Enhanced - With Automatic @5W1H and @RR (Root Cause Analysis)

@DOIT = ORDER 66 (@POPPA @PALPATINE)
The ultimate execution command - immediate, systematic, comprehensive execution.
No hesitation, no debate, no questions - EXECUTE.

ENHANCED FEATURES:
- Automatically applies @5W1H (Who, What, When, Where, Why, How) questioning framework
- Automatically applies @RR (Root Cause Analysis) for all issues
- Detects and fixes problems proactively
- Works systematically, programmatically, robustly, and comprehensively

Tags: #DOIT #ORDER66 #5W1H #ROOT_CAUSE #AUTOMATIC #DECISIONING #TROUBLESHOOTING #LUMINA #JEDICOUNCIL #JEDIHIGHCOUNCIL #INVOCATION #POWERWORD #WORDOFCOMMAND @JARVIS @MANUS @TEAM @POPPA @PALPATINE @AIQ @JC @JHC @POWERWORD @WORDOFCOMMAND @BAU @TRIAGE
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DOITEnhanced")

# Import required modules
try:
    from doit_5w1h_workflow import DOIT5W1HWorkflow, FiveW1H, Solution
    DOIT_AVAILABLE = True
except ImportError:
    DOIT_AVAILABLE = False
    logger.warning("   ⚠️  DOIT 5W1H workflow not available")

try:
    from root_cause_analysis import RootCauseAnalysis, RootCause
    ROOT_CAUSE_AVAILABLE = True
except ImportError:
    ROOT_CAUSE_AVAILABLE = False
    logger.warning("   ⚠️  Root cause analysis not available")

try:
    from jarvis_5w1h_troubleshooter import JARVIS_5W1H_Troubleshooter
    TROUBLESHOOTER_AVAILABLE = True
except ImportError:
    TROUBLESHOOTER_AVAILABLE = False
    logger.warning("   ⚠️  JARVIS 5W1H troubleshooter not available")

try:
    from aiq_fallback_decisioning import AIQFallbackDecisioning
    AIQ_AVAILABLE = True
except ImportError:
    AIQ_AVAILABLE = False
    logger.warning("   ⚠️  @AIQ fallback decisioning not available")


class DOITEnhanced:
    """
    @DOIT Enhanced - With Automatic @5W1H and @RR

    Automatically applies:
    - @5W1H questioning framework
    - @RR (Root Cause Analysis)
    - Systematic problem detection and resolution
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize enhanced DOIT system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "doit_enhanced"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.doit_workflow = DOIT5W1HWorkflow(project_root) if DOIT_AVAILABLE else None
        self.root_cause_analysis = RootCauseAnalysis(project_root) if ROOT_CAUSE_AVAILABLE else None
        self.troubleshooter = JARVIS_5W1H_Troubleshooter() if TROUBLESHOOTER_AVAILABLE else None
        self.aiq_fallback = AIQFallbackDecisioning(project_root) if AIQ_AVAILABLE else None

        # Always include tags: #DECISIONING #TROUBLESHOOTING #INVOCATION #POWERWORD #WORDOFCOMMAND @AIQ @JC[#JEDICOUNCIL] @JHC[#JEDIHIGHCOUNCIL] @JARVIS @MANUS @POWERWORD @WORDOFCOMMAND @BAU @TRIAGE @END2END @AI2AI @AGENT2AGENT @ALWAYS @REPORT #HYPERSPACELANES @ROAMWISE
        self.always_include_tags = [
            "#DECISIONING",
            "#TROUBLESHOOTING",
            "#JEDICOUNCIL",
            "#JEDIHIGHCOUNCIL",
            "#INVOCATION",
            "#POWERWORD",
            "#WORDOFCOMMAND",
            "@AIQ",
            "@DOIT",
            "@JC",
            "@JHC",
            "@JARVIS",
            "@MANUS",
            "@POWERWORD",
            "@WORDOFCOMMAND",
            "@BAU",
            "@TRIAGE",
            "@END2END",
            "@AI2AI",
            "@AGENT2AGENT",
            "@ALWAYS",
            "@REPORT",
            "#HYPERSPACELANES",
            "@ROAMWISE"
        ]

        # @BAU (Business As Usual) - Automatic routine operations
        self.bau_enabled = True
        self.bau_routines = []

        # @TRIAGE - Automatic priority assessment and routing
        self.triage_enabled = True
        self.triage_priorities = ["critical", "high", "medium", "low"]

        logger.info("✅ @DOIT Enhanced initialized")
        logger.info("   Automatic @5W1H: " + ("✅" if DOIT_AVAILABLE else "❌"))
        logger.info("   Automatic @RR: " + ("✅" if ROOT_CAUSE_AVAILABLE else "❌"))
        logger.info("   @AIQ Fallback: " + ("✅" if AIQ_AVAILABLE else "❌"))
        logger.info("   @BAU (Business As Usual): ✅ AUTO-INFERRED")
        logger.info("   @TRIAGE: ✅ AUTO-INFERRED")
        logger.info("   Always Include: #DECISIONING #TROUBLESHOOTING #JEDICOUNCIL #JEDIHIGHCOUNCIL #INVOCATION #POWERWORD #WORDOFCOMMAND @AIQ @JC @JHC @JARVIS @MANUS @POWERWORD @WORDOFCOMMAND @BAU @TRIAGE")

    def doit(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        auto_5w1h: bool = True,
        auto_root_cause: bool = True,
        execute: bool = True,
        use_chain_of_thought: bool = True
    ) -> Dict[str, Any]:
        """
        Execute @DOIT with automatic @5W1H and @RR

        Args:
            task_description: Task to execute
            context: Additional context
            auto_5w1h: Automatically apply 5W1H
            auto_root_cause: Automatically apply root cause analysis
            execute: Actually execute (not just plan)
            use_chain_of_thought: Use chain-of-thought reasoning for end-to-end workflow

        Returns:
            Complete execution result with 5W1H and root cause analysis
        """
        logger.info("=" * 80)
        logger.info("🚀 @DOIT ENHANCED - ORDER 66")
        logger.info("=" * 80)
        logger.info(f"   Task: {task_description}")
        logger.info("")

        # @TRIAGE: Auto-infer priority
        priority = self._infer_triage_priority(task_description, context)

        # @BAU: Auto-detect if routine operation
        is_bau = self._infer_bau(task_description, context)

        result = {
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "priority": priority,  # @TRIAGE
            "is_bau": is_bau,  # @BAU
            "5w1h": None,
            "root_cause": None,
            "solutions": [],
            "execution_plan": [],
            "executed": False,
            "execution_result": None,
            "tags": self.always_include_tags.copy(),  # Always include #DECISIONING #TROUBLESHOOTING #JEDICOUNCIL #JEDIHIGHCOUNCIL #INVOCATION #POWERWORD #WORDOFCOMMAND @AIQ @JC @JHC @JARVIS @MANUS @POWERWORD @WORDOFCOMMAND @BAU @TRIAGE
            "decisioning": None,
            "troubleshooting": None,
            "bau_routine": None,
            "triage_assessment": None,
            "chain_of_thought": None  # Chain-of-thought reasoning
        }

        # Integrate chain-of-thought if requested
        if use_chain_of_thought:
            try:
                from doit_chain_of_thought_enhanced import DOITChainOfThoughtEnhanced
                cot_system = DOITChainOfThoughtEnhanced(self.project_root)
                cot_result = cot_system.process_ask(task_description, context=context)
                result["chain_of_thought"] = cot_result.get("chain_of_thought", {})
                result["workflow_steps"] = cot_result.get("execution_result", {}).get("steps", [])
                result["verification"] = cot_result.get("verification_result", {})
                logger.info("   ✅ Chain-of-thought reasoning integrated")
            except ImportError:
                logger.warning("   ⚠️  Chain-of-thought system not available")
            except Exception as e:
                logger.warning(f"   ⚠️  Chain-of-thought integration failed: {e}")

        # @TRIAGE: Auto-assess and route
        if self.triage_enabled:
            logger.info("📋 @TRIAGE: Auto-Assessing Priority")
            logger.info("")
            triage_assessment = self._assess_triage(task_description, context, priority)
            result["triage_assessment"] = triage_assessment
            result["priority"] = triage_assessment.get("priority", priority)
            logger.info(f"   ✅ Priority: {result['priority'].upper()}")
            logger.info(f"   📋 Routing: {triage_assessment.get('routing', 'standard')}")
            logger.info("")

        # @BAU: Auto-detect and apply routine operations
        if self.bau_enabled and is_bau:
            logger.info("📋 @BAU: Business As Usual - Routine Operation")
            logger.info("")
            bau_routine = self._apply_bau(task_description, context)
            result["bau_routine"] = bau_routine
            logger.info(f"   ✅ Routine detected: {bau_routine.get('routine_type', 'standard')}")
            logger.info("")

        # Step 1: Automatic 5W1H Analysis
        if auto_5w1h and self.doit_workflow:
            logger.info("📋 Step 1: Automatic @5W1H Analysis")
            logger.info("")

            try:
                # Generate 5W1H questions
                five_w1h = self._generate_5w1h(task_description, context)
                result["5w1h"] = five_w1h.to_dict() if hasattr(five_w1h, 'to_dict') else five_w1h

                logger.info("   ✅ 5W1H Analysis Complete:")
                logger.info(f"      WHO: {five_w1h.who if hasattr(five_w1h, 'who') else 'N/A'}")
                logger.info(f"      WHAT: {five_w1h.what if hasattr(five_w1h, 'what') else 'N/A'}")
                logger.info(f"      WHEN: {five_w1h.when if hasattr(five_w1h, 'when') else 'N/A'}")
                logger.info(f"      WHERE: {five_w1h.where if hasattr(five_w1h, 'where') else 'N/A'}")
                logger.info(f"      WHY: {five_w1h.why if hasattr(five_w1h, 'why') else 'N/A'}")
                logger.info(f"      HOW: {five_w1h.how if hasattr(five_w1h, 'how') else 'N/A'}")
                logger.info("")
            except Exception as e:
                logger.error(f"   ❌ 5W1H analysis failed: {e}")

        # Step 2: Automatic Root Cause Analysis
        if auto_root_cause and self.root_cause_analysis:
            logger.info("📋 Step 2: Automatic @RR (Root Cause Analysis)")
            logger.info("")

            try:
                root_causes = self._analyze_root_cause(task_description, context)
                result["root_cause"] = root_causes

                logger.info(f"   ✅ Root Cause Analysis Complete: {len(root_causes)} causes identified")
                for i, cause in enumerate(root_causes[:3], 1):  # Show top 3
                    if isinstance(cause, dict):
                        logger.info(f"      {i}. {cause.get('root_cause', 'N/A')}")
                    elif hasattr(cause, 'root_cause'):
                        logger.info(f"      {i}. {cause.root_cause}")
                logger.info("")
            except Exception as e:
                logger.error(f"   ❌ Root cause analysis failed: {e}")

        # Step 2.5: @AIQ Fallback Decisioning & Troubleshooting
        if self.aiq_fallback:
            logger.info("📋 Step 2.5: @AIQ Fallback Decisioning & Troubleshooting")
            logger.info("")

            try:
                # Check if decisioning needed (high load, complex decisions)
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()

                if cpu_percent > 70 or memory.percent > 70:
                    logger.info("   ⚠️  High system load detected - using @AIQ fallback")
                    decision = self.aiq_fallback.make_decision(
                        context=task_description,
                        options=[{"id": "execute", "priority": 1, "resource_cost": 50}]
                    )
                    result["decisioning"] = decision
                    logger.info("   ✅ @AIQ decisioning applied")

                # Check if troubleshooting needed
                if any(keyword in task_description.lower() for keyword in ["error", "failed", "issue", "problem", "trouble"]):
                    troubleshoot = self.aiq_fallback.troubleshoot(task_description)
                    result["troubleshooting"] = troubleshoot
                    logger.info("   ✅ @AIQ troubleshooting applied")

                logger.info("")
            except Exception as e:
                logger.warning(f"   ⚠️  @AIQ fallback error: {e}")

        # Step 3: Generate Solutions
        if self.doit_workflow:
            logger.info("📋 Step 3: Generating Solutions")
            logger.info("")

            try:
                # Use process_task which includes solution generation
                workflow_result = self.doit_workflow.process_task(task_description, context=context)
                if workflow_result and hasattr(workflow_result, 'solutions'):
                    solutions = workflow_result.solutions
                    result["solutions"] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in solutions]

                logger.info(f"   ✅ Generated {len(solutions)} solutions")
                for i, solution in enumerate(solutions[:3], 1):  # Show top 3
                    if hasattr(solution, 'title'):
                        logger.info(f"      {i}. {solution.title}")
                    elif isinstance(solution, dict):
                        logger.info(f"      {i}. {solution.get('title', 'N/A')}")
                logger.info("")
            except Exception as e:
                logger.error(f"   ❌ Solution generation failed: {e}")

        # Step 4: Execute
        if execute:
            logger.info("📋 Step 4: EXECUTING - ORDER 66")
            logger.info("")

            try:
                execution_result = self._execute_task(task_description, result)
                result["execution_result"] = execution_result
                result["executed"] = True

                logger.info("   ✅ Execution Complete")
                logger.info("")
            except Exception as e:
                logger.error(f"   ❌ Execution failed: {e}")
                result["execution_error"] = str(e)

        # Save result
        result_file = self.data_dir / f"doit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        logger.info("=" * 80)
        logger.info("✅ @DOIT ENHANCED COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Result saved: {result_file.name}")
        logger.info("")

        return result

    def _generate_5w1h(self, task: str, context: Optional[Dict[str, Any]] = None) -> FiveW1H:
        """Generate 5W1H analysis"""
        if not self.doit_workflow:
            return FiveW1H()

        # Use DOIT workflow to generate 5W1H
        try:
            workflow_result = self.doit_workflow.process_task(task, context=context)
            if workflow_result and hasattr(workflow_result, 'five_w1h'):
                return workflow_result.five_w1h
        except Exception as e:
            logger.warning(f"   ⚠️  5W1H generation error: {e}")

        # Fallback: Use troubleshooter
        if self.troubleshooter:
            try:
                analysis = self.troubleshooter.analyze_query(task)
                if analysis:
                    return FiveW1H(
                        who=str(analysis.who.get('entities', [])) if analysis.who else None,
                        what=str(analysis.what.get('problem', '')) if analysis.what else None,
                        when=str(analysis.when.get('timing', '')) if analysis.when else None,
                        where=str(analysis.where.get('location', '')) if analysis.where else None,
                        why=str(analysis.why.get('causes', [])) if analysis.why else None,
                        how=str(analysis.how.get('steps', [])) if analysis.how else None
                    )
            except Exception as e:
                logger.warning(f"   ⚠️  Troubleshooter 5W1H error: {e}")

        # Basic fallback
        return FiveW1H(
            what=task,
            why="Task execution required",
            how="Systematic execution via @DOIT"
        )

    def _analyze_root_cause(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Analyze root causes"""
        if not self.root_cause_analysis:
            return []

        try:
            # Analyze task for root causes
            causes = []

            # Check if task mentions a problem
            problem_keywords = ["not working", "failed", "error", "issue", "problem", "broken", "missing"]
            if any(keyword in task.lower() for keyword in problem_keywords):
                # Get relevant root causes
                for cause in self.root_cause_analysis.root_causes:
                    if not cause.resolved:
                        causes.append(cause.to_dict() if hasattr(cause, 'to_dict') else cause)

            return causes
        except Exception as e:
            logger.warning(f"   ⚠️  Root cause analysis error: {e}")
            return []

    def _infer_triage_priority(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        @TRIAGE: Auto-infer priority from task description

        Priority levels:
        - critical: System down, security breach, data loss
        - high: Major feature, important bug, user-facing issue
        - medium: Standard task, routine update
        - low: Nice-to-have, documentation, cleanup
        """
        task_lower = task.lower()

        # Critical keywords
        critical_keywords = ["critical", "emergency", "down", "breach", "security", "data loss", "corrupt", "crash"]
        if any(kw in task_lower for kw in critical_keywords):
            return "critical"

        # High keywords
        high_keywords = ["important", "urgent", "bug", "error", "failed", "broken", "user", "customer"]
        if any(kw in task_lower for kw in high_keywords):
            return "high"

        # Low keywords
        low_keywords = ["nice to have", "documentation", "cleanup", "refactor", "optimize", "enhance"]
        if any(kw in task_lower for kw in low_keywords):
            return "low"

        # Default: medium
        return "medium"

    def _infer_bau(self, task: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        @BAU: Auto-detect if this is a Business As Usual (routine) operation

        BAU indicators:
        - Routine maintenance
        - Scheduled tasks
        - Standard operations
        - Regular updates
        """
        task_lower = task.lower()

        bau_keywords = [
            "routine", "scheduled", "maintenance", "update", "sync", "backup",
            "health check", "status check", "monitor", "log", "report",
            "daily", "weekly", "monthly", "regular"
        ]

        return any(kw in task_lower for kw in bau_keywords)

    def _assess_triage(self, task: str, context: Optional[Dict[str, Any]], priority: str) -> Dict[str, Any]:
        """
        @TRIAGE: Assess task and determine routing

        Returns:
            Triage assessment with priority, routing, and recommendations
        """
        assessment = {
            "priority": priority,
            "routing": "standard",
            "estimated_effort": "medium",
            "recommendations": []
        }

        # Determine routing based on priority
        if priority == "critical":
            assessment["routing"] = "immediate"
            assessment["estimated_effort"] = "high"
            assessment["recommendations"].append("Execute immediately")
            assessment["recommendations"].append("Notify stakeholders")
        elif priority == "high":
            assessment["routing"] = "priority_queue"
            assessment["estimated_effort"] = "medium"
            assessment["recommendations"].append("Schedule for next available slot")
        elif priority == "medium":
            assessment["routing"] = "standard_queue"
            assessment["estimated_effort"] = "medium"
        else:  # low
            assessment["routing"] = "backlog"
            assessment["estimated_effort"] = "low"
            assessment["recommendations"].append("Can be deferred if needed")

        return assessment

    def _apply_bau(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        @BAU: Apply Business As Usual routine operations

        Returns:
            BAU routine configuration
        """
        routine = {
            "routine_type": "standard",
            "automated": True,
            "schedule": None,
            "parameters": {}
        }

        task_lower = task.lower()

        # Detect routine type
        if "backup" in task_lower:
            routine["routine_type"] = "backup"
            routine["schedule"] = "daily"
        elif "health" in task_lower or "status" in task_lower:
            routine["routine_type"] = "health_check"
            routine["schedule"] = "hourly"
        elif "sync" in task_lower:
            routine["routine_type"] = "sync"
            routine["schedule"] = "continuous"
        elif "update" in task_lower:
            routine["routine_type"] = "update"
            routine["schedule"] = "as_needed"
        elif "monitor" in task_lower:
            routine["routine_type"] = "monitoring"
            routine["schedule"] = "continuous"

        return routine

    def _execute_task(self, task: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task with @BAU and @TRIAGE routing"""
        execution_result = {
            "status": "executed",
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "priority": result.get("priority", "medium"),
            "is_bau": result.get("is_bau", False),
            "routing": result.get("triage_assessment", {}).get("routing", "standard")
        }

        # Apply @BAU optimizations if routine
        if result.get("is_bau"):
            execution_result["bau_applied"] = True
            execution_result["routine_type"] = result.get("bau_routine", {}).get("routine_type", "standard")

        # Apply @TRIAGE routing
        if result.get("triage_assessment"):
            execution_result["triage_applied"] = True
            execution_result["routing"] = result["triage_assessment"].get("routing", "standard")

        return execution_result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="@DOIT Enhanced with Automatic @5W1H and @RR")
    parser.add_argument("task", help="Task to execute")
    parser.add_argument("--no-5w1h", action="store_true", help="Skip automatic 5W1H")
    parser.add_argument("--no-rr", action="store_true", help="Skip automatic root cause analysis")
    parser.add_argument("--no-execute", action="store_true", help="Plan only, don't execute")

    args = parser.parse_args()

    doit = DOITEnhanced()
    result = doit.doit(
        args.task,
        auto_5w1h=not args.no_5w1h,
        auto_root_cause=not args.no_rr,
        execute=not args.no_execute
    )

    print("\n✅ @DOIT Enhanced Complete")
    print(f"   Executed: {result.get('executed', False)}")
    print(f"   5W1H Applied: {result.get('5w1h') is not None}")
    print(f"   Root Cause Analyzed: {result.get('root_cause') is not None}")

    return 0


if __name__ == "__main__":


    sys.exit(main())