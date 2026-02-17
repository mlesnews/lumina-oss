#!/usr/bin/env python3
"""
JARVIS Solution Planner

Generates solution plans, evaluates feasibility, and executes/monitors plans.
Part of Phase 2 (Toddler → Child).

Tags: #JARVIS #SOLUTION_PLANNING #PHASE2 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

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

logger = get_logger("JARVISSolutionPlanner")


class PlanStatus(Enum):
    """Solution plan status"""
    DRAFT = "draft"
    VALIDATED = "validated"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlanFeasibility(Enum):
    """Plan feasibility assessment"""
    FEASIBLE = "feasible"
    RISKY = "risky"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"


@dataclass
class SolutionStep:
    """A step in a solution plan"""
    step_id: str
    description: str
    action: str  # What to do
    expected_outcome: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


@dataclass
class SolutionPlan:
    """A complete solution plan"""
    plan_id: str
    problem: str
    goal: str
    steps: List[SolutionStep]
    feasibility: PlanFeasibility
    confidence: float  # 0-1
    status: PlanStatus
    estimated_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    created_time: str = field(default_factory=lambda: datetime.now().isoformat())
    started_time: Optional[str] = None
    completed_time: Optional[str] = None


class JARVISSolutionPlanner:
    """
    Generates, evaluates, and executes solution plans

    Capabilities:
    - Generate solution plans from problems
    - Evaluate plan feasibility
    - Execute plans step-by-step
    - Monitor execution and handle failures
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize solution planner"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_solution_plans"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.plans_file = self.data_dir / "solution_plans.json"

        self.plans: List[SolutionPlan] = []
        self.active_plans: Dict[str, SolutionPlan] = {}

        # Load existing data
        self._load_data()

        # Integrate with problem decomposer
        try:
            from jarvis_problem_decomposer import get_jarvis_problem_decomposer
            self.problem_decomposer = get_jarvis_problem_decomposer(self.project_root)
        except ImportError:
            self.problem_decomposer = None

        # Integrate with reasoning engine
        try:
            from jarvis_reasoning_engine import get_jarvis_reasoning_engine
            self.reasoning_engine = get_jarvis_reasoning_engine(self.project_root)
        except ImportError:
            self.reasoning_engine = None

        # Integrate with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
        except ImportError:
            self.learning_pipeline = None

        logger.info("=" * 80)
        logger.info("📋 JARVIS SOLUTION PLANNER")
        logger.info("=" * 80)
        logger.info("   Generate, evaluate, and execute solution plans")
        logger.info("")

    def create_solution_plan(self, problem: str, goal: str, context: Dict[str, Any] = None) -> SolutionPlan:
        """
        Create a solution plan for a problem

        Args:
            problem: The problem to solve
            goal: The goal to achieve
            context: Additional context

        Returns:
            SolutionPlan with steps and feasibility assessment
        """
        plan_id = f"plan_{int(time.time() * 1000)}"
        context = context or {}

        # Decompose problem if decomposer available
        if self.problem_decomposer:
            decomposition = self.problem_decomposer.decompose_problem(problem, context)
            execution_order = self.problem_decomposer.get_execution_order(decomposition)

            # Convert decomposition steps to solution steps
            steps = []
            for step in decomposition.steps:
                solution_step = SolutionStep(
                    step_id=step.step_id,
                    description=step.description,
                    action=step.description,  # Action is the description
                    expected_outcome=f"Complete: {step.description}",
                    dependencies=step.dependencies,
                    status="pending"
                )
                steps.append(solution_step)
        else:
            # Simple single-step plan
            steps = [
                SolutionStep(
                    step_id="step_1",
                    description=problem,
                    action=problem,
                    expected_outcome=goal,
                    dependencies=[],
                    status="pending"
                )
            ]

        # Evaluate feasibility
        feasibility = self._evaluate_feasibility(problem, goal, steps, context)

        # Calculate confidence
        confidence = self._calculate_confidence(feasibility, steps)

        # Estimate duration
        estimated_duration = sum(
            60.0  # Default 60 seconds per step
            for _ in steps
        )

        plan = SolutionPlan(
            plan_id=plan_id,
            problem=problem,
            goal=goal,
            steps=steps,
            feasibility=feasibility,
            confidence=confidence,
            status=PlanStatus.DRAFT,
            estimated_duration=estimated_duration
        )

        self.plans.append(plan)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="solution_planning",
                context={"problem": problem, "goal": goal, "context": context},
                data={
                    "plan_id": plan_id,
                    "steps": len(steps),
                    "feasibility": feasibility.value,
                    "confidence": confidence
                }
            )

        logger.info(f"📋 Created solution plan: {len(steps)} steps, feasibility: {feasibility.value}, confidence: {confidence:.2%}")
        return plan

    def _evaluate_feasibility(self, problem: str, goal: str, steps: List[SolutionStep], context: Dict[str, Any]) -> PlanFeasibility:
        """Evaluate plan feasibility"""
        # Simple heuristics
        risk_keywords = ["unknown", "uncertain", "experimental", "untested", "complex"]
        infeasible_keywords = ["impossible", "cannot", "unable", "blocked", "missing"]

        problem_lower = problem.lower()
        goal_lower = goal.lower()

        # Check for infeasible indicators
        if any(kw in problem_lower or kw in goal_lower for kw in infeasible_keywords):
            return PlanFeasibility.INFEASIBLE

        # Check for risky indicators
        if any(kw in problem_lower or kw in goal_lower for kw in risk_keywords):
            return PlanFeasibility.RISKY

        # Check step count - too many steps = risky
        if len(steps) > 20:
            return PlanFeasibility.RISKY

        # Default: feasible
        return PlanFeasibility.FEASIBLE

    def _calculate_confidence(self, feasibility: PlanFeasibility, steps: List[SolutionStep]) -> float:
        """Calculate plan confidence"""
        base_confidence = {
            PlanFeasibility.FEASIBLE: 0.8,
            PlanFeasibility.RISKY: 0.5,
            PlanFeasibility.INFEASIBLE: 0.2,
            PlanFeasibility.UNKNOWN: 0.5
        }

        confidence = base_confidence[feasibility]

        # Adjust based on step count
        if len(steps) > 15:
            confidence *= 0.8  # More steps = lower confidence
        elif len(steps) < 3:
            confidence *= 1.1  # Fewer steps = higher confidence

        return min(1.0, max(0.0, confidence))

    def validate_plan(self, plan: SolutionPlan) -> bool:
        """
        Validate a plan before execution

        Args:
            plan: The plan to validate

        Returns:
            True if valid, False otherwise
        """
        # Check feasibility
        if plan.feasibility == PlanFeasibility.INFEASIBLE:
            logger.warning(f"⚠️  Plan {plan.plan_id} is infeasible")
            return False

        # Check for steps
        if not plan.steps:
            logger.warning(f"⚠️  Plan {plan.plan_id} has no steps")
            return False

        # Check dependencies
        step_ids = {step.step_id for step in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    logger.warning(f"⚠️  Plan {plan.plan_id} has broken dependency: {dep}")
                    return False

        # Plan is valid
        plan.status = PlanStatus.VALIDATED
        self._save_data()
        logger.info(f"✅ Plan {plan.plan_id} validated")
        return True

    def execute_plan(self, plan: SolutionPlan, executor: Optional[Callable[[SolutionStep], Any]] = None) -> bool:
        """
        Execute a solution plan

        Args:
            plan: The plan to execute
            executor: Optional function to execute each step

        Returns:
            True if successful, False otherwise
        """
        if plan.status != PlanStatus.VALIDATED:
            if not self.validate_plan(plan):
                return False

        plan.status = PlanStatus.EXECUTING
        plan.started_time = datetime.now().isoformat()
        self.active_plans[plan.plan_id] = plan
        self._save_data()

        logger.info(f"🚀 Executing plan {plan.plan_id}: {len(plan.steps)} steps")

        # Get execution order (topological sort)
        execution_order = self._get_execution_order(plan)

        success = True
        for step_id in execution_order:
            step = next(s for s in plan.steps if s.step_id == step_id)

            # Check dependencies
            if step.dependencies:
                deps_complete = all(
                    next(s for s in plan.steps if s.step_id == dep).status == "completed"
                    for dep in step.dependencies
                )
                if not deps_complete:
                    logger.warning(f"⚠️  Step {step_id} dependencies not met, skipping")
                    step.status = "failed"
                    step.error = "Dependencies not met"
                    success = False
                    continue

            # Execute step
            step.status = "executing"
            step.start_time = datetime.now().isoformat()
            self._save_data()

            try:
                if executor:
                    result = executor(step)
                    step.result = result
                else:
                    # Default: just mark as completed
                    step.result = {"status": "completed", "message": step.description}

                step.status = "completed"
                step.end_time = datetime.now().isoformat()
                logger.info(f"✅ Step {step_id} completed: {step.description}")
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                step.end_time = datetime.now().isoformat()
                logger.error(f"❌ Step {step_id} failed: {e}")
                success = False
                break

        # Finalize plan
        if success:
            plan.status = PlanStatus.COMPLETED
            logger.info(f"✅ Plan {plan.plan_id} completed successfully")
        else:
            plan.status = PlanStatus.FAILED
            logger.error(f"❌ Plan {plan.plan_id} failed")

        plan.completed_time = datetime.now().isoformat()

        # Calculate actual duration
        if plan.started_time and plan.completed_time:
            start = datetime.fromisoformat(plan.started_time)
            end = datetime.fromisoformat(plan.completed_time)
            plan.actual_duration = (end - start).total_seconds()

        if plan.plan_id in self.active_plans:
            del self.active_plans[plan.plan_id]

        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="plan_execution",
                context={"plan_id": plan.plan_id, "problem": plan.problem},
                data={
                    "success": success,
                    "steps_completed": sum(1 for s in plan.steps if s.status == "completed"),
                    "steps_total": len(plan.steps),
                    "duration": plan.actual_duration
                }
            )

        return success

    def _get_execution_order(self, plan: SolutionPlan) -> List[str]:
        """Get execution order for plan steps (topological sort)"""
        # Build dependency graph
        in_degree = {step.step_id: len(step.dependencies) for step in plan.steps}
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            # Update dependencies
            for step in plan.steps:
                if current in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step.step_id)

        # Add any remaining steps
        remaining = [s.step_id for s in plan.steps if s.step_id not in result]
        result.extend(remaining)

        return result

    def get_plan_status(self, plan_id: str) -> Optional[SolutionPlan]:
        """Get plan by ID"""
        for plan in self.plans:
            if plan.plan_id == plan_id:
                return plan
        return None

    def _load_data(self):
        """Load plans from disk"""
        try:
            if self.plans_file.exists():
                with open(self.plans_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.plans = [
                        SolutionPlan(
                            **{
                                **plan_data,
                                "feasibility": PlanFeasibility(plan_data["feasibility"]),
                                "status": PlanStatus(plan_data["status"]),
                                "steps": [
                                    SolutionStep(**step_data)
                                    for step_data in plan_data["steps"]
                                ]
                            }
                        )
                        for plan_data in data.get("plans", [])
                    ]
                    logger.debug(f"Loaded {len(self.plans)} solution plans")
        except Exception as e:
            logger.debug(f"Could not load plan data: {e}")

    def _save_data(self):
        """Save plans to disk"""
        try:
            data = {
                "plans": [
                    {
                        **asdict(plan),
                        "feasibility": plan.feasibility.value,
                        "status": plan.status.value
                    }
                    for plan in self.plans
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.plans_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save plan data: {e}")


# Singleton pattern
_planner_instance: Optional[JARVISSolutionPlanner] = None


def get_jarvis_solution_planner(project_root: Optional[Path] = None) -> JARVISSolutionPlanner:
    """Get singleton solution planner instance"""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = JARVISSolutionPlanner(project_root)
    return _planner_instance


if __name__ == "__main__":
    planner = get_jarvis_solution_planner()

    # Test plan creation
    plan = planner.create_solution_plan(
        "Implement a new feature with database, API, and frontend",
        "Feature is fully operational"
    )

    print(f"Plan: {plan.plan_id}")
    print(f"Feasibility: {plan.feasibility.value}")
    print(f"Confidence: {plan.confidence:.2%}")
    print(f"Steps: {len(plan.steps)}")

    # Validate
    if planner.validate_plan(plan):
        print("✅ Plan validated")
    else:
        print("❌ Plan validation failed")
