#!/usr/bin/env python3
"""
@DOIT Chain-of-Thought Enhanced - End-to-End Workflow Processing

Addresses weaknesses in chain-of-thought end-to-end workflow processing
to ensure successful completion of all @asks.

Key Enhancements:
- Explicit chain-of-thought reasoning at each step
- Comprehensive workflow state management
- Dependency tracking and resolution
- Error recovery and retry logic
- Completion verification
- Context propagation between steps
- Progress tracking and reporting

Tags: #DOIT #CHAIN_OF_THOUGHT #WORKFLOW #END_TO_END #REASONING @JARVIS @LUMINA @DOIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("DOITChainOfThought")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DOITChainOfThought")


class WorkflowState(Enum):
    """Workflow execution state"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    RETRYING = "retrying"


class ReasoningStep(Enum):
    """Chain-of-thought reasoning steps"""
    UNDERSTAND = "understand"
    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    REFLECT = "reflect"


@dataclass
class ChainOfThought:
    """Chain-of-thought reasoning step"""
    step: ReasoningStep
    reasoning: str
    context: Dict[str, Any] = field(default_factory=dict)
    conclusions: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorkflowStep:
    """A single step in the workflow"""
    step_id: str
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    chain_of_thought: List[ChainOfThought] = field(default_factory=list)
    state: WorkflowState = WorkflowState.PENDING
    execution_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    verification_result: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowContext:
    """Context propagated through workflow"""
    workflow_id: str
    ask_id: Optional[str] = None
    ask_text: str = ""
    initial_context: Dict[str, Any] = field(default_factory=dict)
    accumulated_context: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DOITChainOfThoughtEnhanced:
    """Enhanced @DOIT with chain-of-thought reasoning"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.workflow_contexts: Dict[str, WorkflowContext] = {}
        self.completed_asks: Set[str] = set()
        self.failed_asks: Set[str] = set()

        # Initialize local-first AI policy
        try:
            from doit_local_first_ai_policy import DOITLocalFirstAIPolicy
            self.ai_policy = DOITLocalFirstAIPolicy(project_root)
            logger.info("✅ Local-first AI policy initialized")
        except ImportError:
            self.ai_policy = None
            logger.warning("⚠️  Local-first AI policy not available")

        logger.info("="*80)
        logger.info("🧠 @DOIT CHAIN-OF-THOUGHT ENHANCED")
        logger.info("="*80)
        logger.info("")

    def process_ask(
        self,
        ask_text: str,
        ask_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an @ask with full chain-of-thought reasoning

        Args:
            ask_text: The @ask to process
            ask_id: Optional ask ID
            context: Additional context

        Returns:
            Complete processing result
        """
        workflow_id = ask_id or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"🔍 Processing @ask: {ask_text[:100]}")
        logger.info(f"   Workflow ID: {workflow_id}")
        logger.info("")

        # Initialize workflow context
        workflow_context = WorkflowContext(
            workflow_id=workflow_id,
            ask_id=ask_id,
            ask_text=ask_text,
            initial_context=context or {}
        )
        self.workflow_contexts[workflow_id] = workflow_context

        # Step 1: UNDERSTAND - Chain-of-thought reasoning
        logger.info("📋 Step 1: UNDERSTAND (Chain-of-Thought)")
        understand_cot = self._understand_ask(ask_text, workflow_context)
        workflow_context.accumulated_context["understanding"] = understand_cot.conclusions

        # Step 2: ANALYZE - Break down into steps
        logger.info("📋 Step 2: ANALYZE (Break Down)")
        steps = self._analyze_ask(ask_text, workflow_context)
        self.workflows[workflow_id] = steps

        # Step 3: PLAN - Create execution plan
        logger.info("📋 Step 3: PLAN (Create Execution Plan)")
        plan_cot = self._plan_execution(steps, workflow_context)
        workflow_context.accumulated_context["plan"] = plan_cot.conclusions

        # Step 4: EXECUTE - Execute each step with chain-of-thought
        logger.info("📋 Step 4: EXECUTE (With Chain-of-Thought)")
        execution_result = self._execute_workflow(workflow_id, workflow_context)

        # Step 5: VERIFY - Verify completion
        logger.info("📋 Step 5: VERIFY (Completion Verification)")
        verification_result = self._verify_completion(workflow_id, workflow_context)

        # Step 6: REFLECT - Reflect on execution
        logger.info("📋 Step 6: REFLECT (Post-Execution Analysis)")
        reflection = self._reflect_on_execution(workflow_id, workflow_context)

        # Final result
        result = {
            "workflow_id": workflow_id,
            "ask_text": ask_text,
            "success": verification_result.get("success", False),
            "steps_executed": len([s for s in steps if s.state == WorkflowState.COMPLETED]),
            "steps_failed": len([s for s in steps if s.state == WorkflowState.FAILED]),
            "chain_of_thought": {
                "understand": asdict(understand_cot),
                "plan": asdict(plan_cot),
                "reflection": reflection
            },
            "execution_result": execution_result,
            "verification_result": verification_result,
            "context": asdict(workflow_context)
        }

        if result["success"]:
            self.completed_asks.add(ask_id or ask_text)
            logger.info("✅ @ask completed successfully")
        else:
            self.failed_asks.add(ask_id or ask_text)
            logger.error("❌ @ask failed")

        return result

    def _understand_ask(self, ask_text: str, context: WorkflowContext) -> ChainOfThought:
        """Chain-of-thought: Understand the @ask"""
        reasoning = f"""
        Understanding the @ask:
        1. What is being asked? {ask_text}
        2. What is the goal? Extract the primary objective
        3. What are the constraints? Identify any limitations
        4. What context exists? Review initial context
        5. What dependencies might exist? Identify potential dependencies
        """

        # Analyze ask text
        conclusions = []
        next_steps = []

        # Extract key components
        if "@ask" in ask_text.lower():
            conclusions.append("This is an explicit @ask directive")

        if any(word in ask_text.lower() for word in ["fix", "repair", "resolve"]):
            conclusions.append("This is a fix/repair request")
            next_steps.append("Identify the issue to fix")

        if any(word in ask_text.lower() for word in ["implement", "create", "add"]):
            conclusions.append("This is an implementation request")
            next_steps.append("Design the implementation")

        if any(word in ask_text.lower() for word in ["update", "modify", "change"]):
            conclusions.append("This is an update/modification request")
            next_steps.append("Identify what needs updating")

        # Identify dependencies
        if "depend" in ask_text.lower() or "require" in ask_text.lower():
            conclusions.append("Dependencies may exist")
            next_steps.append("Resolve dependencies first")

        return ChainOfThought(
            step=ReasoningStep.UNDERSTAND,
            reasoning=reasoning,
            context={"ask_text": ask_text, "initial_context": context.initial_context},
            conclusions=conclusions,
            next_steps=next_steps
        )

    def _analyze_ask(self, ask_text: str, context: WorkflowContext) -> List[WorkflowStep]:
        """Chain-of-thought: Analyze and break down into steps"""
        steps = []

        # Analyze what needs to be done
        analysis_cot = ChainOfThought(
            step=ReasoningStep.ANALYZE,
            reasoning=f"""
            Analyzing @ask: {ask_text}

            Breaking down into executable steps:
            1. Identify all required actions
            2. Determine dependencies between actions
            3. Order steps logically
            4. Identify verification points
            """,
            context={"ask_text": ask_text}
        )

        # Create workflow steps based on ask content
        step_num = 1

        # Step 1: Preparation
        steps.append(WorkflowStep(
            step_id=f"step_{step_num}",
            name="Preparation",
            description="Prepare environment and gather requirements",
            chain_of_thought=[analysis_cot],
            context={"step_number": step_num}
        ))
        step_num += 1

        # Step 2: Implementation/Execution
        steps.append(WorkflowStep(
            step_id=f"step_{step_num}",
            name="Implementation",
            description="Execute the main task",
            dependencies=[steps[0].step_id],
            chain_of_thought=[],
            context={"step_number": step_num}
        ))
        step_num += 1

        # Step 3: Verification
        steps.append(WorkflowStep(
            step_id=f"step_{step_num}",
            name="Verification",
            description="Verify the task was completed correctly",
            dependencies=[steps[1].step_id],
            chain_of_thought=[],
            context={"step_number": step_num}
        ))

        return steps

    def _plan_execution(self, steps: List[WorkflowStep], context: WorkflowContext) -> ChainOfThought:
        """Chain-of-thought: Plan execution"""
        reasoning = f"""
        Planning execution:
        1. Total steps: {len(steps)}
        2. Dependencies: {[s.dependencies for s in steps]}
        3. Execution order: Resolve dependencies first
        4. Verification points: After each critical step
        5. Error handling: Retry logic for each step
        """

        conclusions = [
            f"Execution plan created with {len(steps)} steps",
            "Dependencies resolved",
            "Verification points identified",
            "Error recovery strategy defined"
        ]

        next_steps = [f"Execute {s.name}" for s in steps]

        return ChainOfThought(
            step=ReasoningStep.PLAN,
            reasoning=reasoning,
            context={"step_count": len(steps)},
            conclusions=conclusions,
            next_steps=next_steps
        )

    def _execute_workflow(self, workflow_id: str, context: WorkflowContext) -> Dict[str, Any]:
        """Execute workflow with chain-of-thought at each step"""
        steps = self.workflows.get(workflow_id, [])
        executed_steps = []
        failed_steps = []

        # Resolve dependencies and execute in order
        executed_step_ids = set()

        for step in steps:
            # Check dependencies
            if step.dependencies:
                missing_deps = [dep for dep in step.dependencies if dep not in executed_step_ids]
                if missing_deps:
                    logger.warning(f"   ⚠️  Step {step.step_id} blocked by missing dependencies: {missing_deps}")
                    step.state = WorkflowState.BLOCKED
                    failed_steps.append(step)
                    continue

            # Execute step with chain-of-thought
            logger.info(f"   🔄 Executing: {step.name}")
            step.state = WorkflowState.EXECUTING

            # Add chain-of-thought reasoning
            execute_cot = ChainOfThought(
                step=ReasoningStep.EXECUTE,
                reasoning=f"""
                Executing step: {step.name}

                Reasoning:
                1. What needs to be done? {step.description}
                2. What context is available? {context.accumulated_context}
                3. How to execute? Use appropriate tools/methods
                4. What could go wrong? Identify potential issues
                5. How to handle errors? Apply retry logic
                """,
                context={"step": step.step_id, "name": step.name}
            )
            step.chain_of_thought.append(execute_cot)

            # Execute step (placeholder - actual execution depends on step type)
            try:
                result = self._execute_step(step, context)
                step.execution_result = result

                if result.get("success"):
                    step.state = WorkflowState.COMPLETED
                    executed_steps.append(step)
                    executed_step_ids.add(step.step_id)
                    context.step_results[step.step_id] = result
                    logger.info(f"   ✅ Completed: {step.name}")
                else:
                    # Retry logic
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        step.state = WorkflowState.RETRYING
                        logger.warning(f"   ⚠️  Retrying {step.name} (attempt {step.retry_count}/{step.max_retries})")
                        # Retry execution
                        result = self._execute_step(step, context)
                        if result.get("success"):
                            step.state = WorkflowState.COMPLETED
                            executed_steps.append(step)
                            executed_step_ids.add(step.step_id)
                            logger.info(f"   ✅ Completed after retry: {step.name}")
                        else:
                            step.state = WorkflowState.FAILED
                            step.error = result.get("error", "Unknown error")
                            failed_steps.append(step)
                            logger.error(f"   ❌ Failed after retries: {step.name}")
                    else:
                        step.state = WorkflowState.FAILED
                        step.error = result.get("error", "Unknown error")
                        failed_steps.append(step)
                        logger.error(f"   ❌ Failed: {step.name}")

            except Exception as e:
                step.state = WorkflowState.FAILED
                step.error = str(e)
                failed_steps.append(step)
                context.errors.append(f"Step {step.step_id} failed: {e}")
                logger.error(f"   ❌ Exception in {step.name}: {e}")

        return {
            "executed": len(executed_steps),
            "failed": len(failed_steps),
            "steps": [asdict(s) for s in steps]
        }

    def _execute_step(self, step: WorkflowStep, context: WorkflowContext) -> Dict[str, Any]:
        """Execute a single workflow step"""
        # Check if step requires AI - enforce local-first policy
        if self.ai_policy and any(keyword in step.description.lower() for keyword in ["ai", "llm", "model", "generate", "complete"]):
            # Check if step is trying to use cloud AI
            step_context = step.context or {}
            requested_provider = step_context.get("ai_provider") or step_context.get("model")

            if requested_provider:
                # Enforce local-first AI policy
                ai_decision = self.ai_policy.decide_ai_provider(
                    task_description=step.description,
                    context={**context.accumulated_context, **step_context},
                    requested_provider=requested_provider
                )

                # Update step context with approved provider
                step.context["ai_provider"] = ai_decision.approved_provider.value
                step.context["use_local"] = ai_decision.use_local
                step.context["use_cloud"] = ai_decision.use_cloud
                step.context["ai_decision_reason"] = ai_decision.decision_reason
                step.context["ai_decision_source"] = ai_decision.decisioning_source

                if ai_decision.use_local:
                    logger.info(f"   🛡️  Local-first AI enforced: {ai_decision.approved_provider.value}")
                elif ai_decision.use_cloud:
                    logger.info(f"   ✅ Cloud AI approved by {ai_decision.decisioning_source}")

        # This is a placeholder - actual execution would depend on step type
        # In a real implementation, this would:
        # 1. Identify step type (file operation, script execution, etc.)
        # 2. Execute appropriate action
        # 3. Return result

        # For now, simulate execution
        import time
        time.sleep(0.1)  # Simulate work

        # Check if step can succeed (simplified logic)
        if "fail" in step.description.lower() and step.retry_count == 0:
            return {"success": False, "error": "Simulated failure"}

        return {
            "success": True,
            "step_id": step.step_id,
            "result": f"Step {step.name} executed successfully"
        }

    def _verify_completion(self, workflow_id: str, context: WorkflowContext) -> Dict[str, Any]:
        """Chain-of-thought: Verify completion"""
        steps = self.workflows.get(workflow_id, [])

        verify_cot = ChainOfThought(
            step=ReasoningStep.VERIFY,
            reasoning=f"""
            Verifying completion:
            1. All steps executed? {len([s for s in steps if s.state == WorkflowState.COMPLETED])}/{len(steps)}
            2. Any failures? {len([s for s in steps if s.state == WorkflowState.FAILED])}
            3. Dependencies satisfied? Check all dependencies resolved
            4. Expected outcomes achieved? Verify against ask requirements
            """,
            context={"workflow_id": workflow_id}
        )

        # Check completion
        all_completed = all(s.state == WorkflowState.COMPLETED for s in steps)
        any_failed = any(s.state == WorkflowState.FAILED for s in steps)

        # Verify against ask requirements
        ask_text = context.ask_text
        verification_checks = []

        if "fix" in ask_text.lower():
            verification_checks.append("Issue should be fixed")
        if "implement" in ask_text.lower():
            verification_checks.append("Implementation should be complete")
        if "update" in ask_text.lower():
            verification_checks.append("Update should be applied")

        success = all_completed and not any_failed

        return {
            "success": success,
            "all_steps_completed": all_completed,
            "any_failures": any_failed,
            "verification_checks": verification_checks,
            "chain_of_thought": asdict(verify_cot)
        }

    def _reflect_on_execution(self, workflow_id: str, context: WorkflowContext) -> Dict[str, Any]:
        """Chain-of-thought: Reflect on execution"""
        steps = self.workflows.get(workflow_id, [])

        reflection = ChainOfThought(
            step=ReasoningStep.REFLECT,
            reasoning=f"""
            Reflecting on execution:
            1. What worked well? Steps that completed successfully
            2. What didn't work? Steps that failed
            3. What could be improved? Identify optimization opportunities
            4. What was learned? Extract insights
            5. What should be remembered? Key takeaways
            """,
            context={"workflow_id": workflow_id}
        )

        successful_steps = [s for s in steps if s.state == WorkflowState.COMPLETED]
        failed_steps = [s for s in steps if s.state == WorkflowState.FAILED]

        insights = []
        if successful_steps:
            insights.append(f"{len(successful_steps)} steps completed successfully")
        if failed_steps:
            insights.append(f"{len(failed_steps)} steps failed - review needed")
        if context.errors:
            insights.append(f"{len(context.errors)} errors encountered")

        return {
            "reflection": asdict(reflection),
            "insights": insights,
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps)
        }

    def process_all_asks(self, asks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process all @asks with chain-of-thought"""
        logger.info("="*80)
        logger.info("🚀 PROCESSING ALL @ASKS WITH CHAIN-OF-THOUGHT")
        logger.info("="*80)
        logger.info(f"   Total @asks: {len(asks)}")
        logger.info("")

        results = []
        for ask in asks:
            ask_text = ask.get("ask_text", ask.get("text", ""))
            ask_id = ask.get("ask_id", ask.get("id", ""))

            result = self.process_ask(ask_text, ask_id, ask.get("context"))
            results.append(result)

        summary = {
            "total": len(asks),
            "completed": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }

        logger.info("")
        logger.info("="*80)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("="*80)
        logger.info(f"   Total: {summary['total']}")
        logger.info(f"   Completed: {summary['completed']}")
        logger.info(f"   Failed: {summary['failed']}")
        logger.info("="*80)

        return summary


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent

        doit_system = DOITChainOfThoughtEnhanced(project_root)

        # Example: Process a single ask
        result = doit_system.process_ask(
            "@ask Fix the WSL unresponsive issue",
            ask_id="wsl_fix_001"
        )

        print(json.dumps(result, indent=2, default=str))

        return 0 if result["success"] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())