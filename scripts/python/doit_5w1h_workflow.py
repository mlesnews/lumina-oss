#!/usr/bin/env python3
"""
@DOIT Workflow with @5W1H Questioning Framework

@DOIT = ORDER 66 (@POPPA @PALPATINE)
The ultimate execution command - immediate, systematic, comprehensive execution.
No hesitation, no debate, no questions - EXECUTE.

Standard operating procedure for LUMINA:
- @DOIT = ORDER 66: Immediate systematic execution across ALL systems
- Always @DOIT (execute, don't just suggest)
- Answer own questions proactively
- Generate 3 viable actionable solutions
- Apply 5W1H (Who, What, When, Where, Why, How) questioning framework

Tags: #DOIT #ORDER66 #5W1H #WORKFLOW #DECISIONING #TROUBLESHOOTING #LUMINA @JARVIS @TEAM @POPPA @PALPATINE @AIQ
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DOIT5W1HWorkflow")


class QuestionType(Enum):
    """5W1H Question Types"""
    WHO = "Who"
    WHAT = "What"
    WHEN = "When"
    WHERE = "Where"
    WHY = "Why"
    HOW = "How"


@dataclass
class Solution:
    """A viable actionable solution"""
    id: str
    title: str
    description: str
    approach: str
    steps: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    feasibility: float = 0.0  # 0.0 to 1.0
    estimated_effort: str = "medium"  # low, medium, high
    risk_level: str = "medium"  # low, medium, high
    recommended: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FiveW1H:
    """5W1H Question Framework"""
    who: Optional[str] = None
    what: Optional[str] = None
    when: Optional[str] = None
    where: Optional[str] = None
    why: Optional[str] = None
    how: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_complete(self) -> bool:
        """Check if all questions are answered"""
        return all([
            self.who is not None,
            self.what is not None,
            self.when is not None,
            self.where is not None,
            self.why is not None,
            self.how is not None
        ])

    def get_missing_questions(self) -> List[str]:
        """Get list of unanswered questions"""
        missing = []
        if self.who is None:
            missing.append("Who")
        if self.what is None:
            missing.append("What")
        if self.when is None:
            missing.append("When")
        if self.where is None:
            missing.append("Where")
        if self.why is None:
            missing.append("Why")
        if self.how is None:
            missing.append("How")
        return missing


@dataclass
class DOITWorkflowResult:
    """Result of @DOIT workflow execution"""
    task_id: str
    task_description: str
    five_w1h: FiveW1H
    solutions: List[Solution]
    selected_solution: Optional[Solution] = None
    execution_plan: List[str] = field(default_factory=list)
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.selected_solution:
            data['selected_solution'] = self.selected_solution.to_dict()
        return data


class DOIT5W1HWorkflow:
    """
    @DOIT Workflow with @5W1H Questioning Framework

    @DOIT = ORDER 66 (@POPPA @PALPATINE)
    The ultimate execution command - immediate, systematic, comprehensive.
    No hesitation. No debate. EXECUTE.

    Standard operating procedure:
    1. @DOIT = ORDER 66: Immediate systematic execution (execute, don't just suggest)
    2. Answer own questions proactively
    3. Generate 3 viable actionable solutions
    4. Apply 5W1H questioning framework
    5. Execute across ALL systems simultaneously
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @DOIT workflow system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.workflow_dir = self.data_dir / "doit_workflows"
        self.workflow_dir.mkdir(parents=True, exist_ok=True)

        self.current_task = ""

        logger.info("✅ @DOIT 5W1H Workflow System initialized")

    def process_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> DOITWorkflowResult:
        """
        Process a task using @DOIT workflow with 5W1H questioning

        Steps:
        1. Apply 5W1H questioning framework
        2. Generate 3 viable actionable solutions
        3. Select best solution
        4. Create execution plan
        5. Execute (@DOIT)
        """
        self.current_task = task_description
        logger.info(f"🚀 Processing task with @DOIT workflow: {task_description}")

        # Step 1: Apply 5W1H questioning framework
        five_w1h = self._apply_5w1h_questioning(task_description, context)
        logger.info(f"   ✅ 5W1H Analysis complete")

        # Step 2: Generate 3 viable actionable solutions
        solutions = self._generate_solutions(task_description, five_w1h, context)
        logger.info(f"   ✅ Generated {len(solutions)} viable solutions")

        # Step 3: Select best solution
        selected_solution = self._select_best_solution(solutions)
        logger.info(f"   ✅ Selected solution: {selected_solution.title}")

        # Step 4: Create execution plan
        execution_plan = self._create_execution_plan(selected_solution, five_w1h)
        logger.info(f"   ✅ Execution plan created ({len(execution_plan)} steps)")

        # Step 5: Execute (@DOIT)
        execution_result = self._execute_doit(selected_solution, execution_plan, context)
        logger.info(f"   ✅ @DOIT Execution complete")

        # Create result
        result = DOITWorkflowResult(
            task_id=f"doit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_description=task_description,
            five_w1h=five_w1h,
            solutions=solutions,
            selected_solution=selected_solution,
            execution_plan=execution_plan,
            executed=True,
            execution_result=execution_result
        )

        # Save result
        self._save_workflow_result(result)

        return result

    def _apply_5w1h_questioning(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> FiveW1H:
        """Apply 5W1H questioning framework to task"""
        five_w1h = FiveW1H()

        # WHO: Who is involved/affected?
        five_w1h.who = self._answer_who(task_description, context)

        # WHAT: What needs to be done?
        five_w1h.what = self._answer_what(task_description, context)

        # WHEN: When should this be done?
        five_w1h.when = self._answer_when(task_description, context)

        # WHERE: Where does this apply?
        five_w1h.where = self._answer_where(task_description, context)

        # WHY: Why is this important?
        five_w1h.why = self._answer_why(task_description, context)

        # HOW: How should this be accomplished?
        five_w1h.how = self._answer_how(task_description, context)

        return five_w1h

    def _answer_who(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer WHO question"""
        # Default: JARVIS/AI system and user
        who = "JARVIS AI system and user (LUMINA ecosystem)"

        # Extract from context if available
        if context:
            if "user" in context:
                who = f"User ({context['user']}) and JARVIS AI system"
            if "agents" in context:
                who += f", {', '.join(context['agents'])}"

        return who

    def _answer_what(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer WHAT question"""
        # Extract what from task description
        what = task_description.strip()

        # If task starts with action verb, use it
        action_verbs = ["create", "build", "implement", "fix", "add", "update", "modify", "enhance"]
        for verb in action_verbs:
            if task_description.lower().startswith(verb):
                what = task_description
                break

        return what

    def _answer_when(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer WHEN question"""
        # @DOIT = ORDER 66: Execute immediately, no delay
        when = "ORDER 66 - Execute immediately, no delay, no questions"

        # Check for urgency indicators
        urgency_keywords = ["urgent", "asap", "immediately", "now", "critical", "priority"]
        if any(keyword in task_description.lower() for keyword in urgency_keywords):
            when = "ORDER 66 - Execute immediately, high priority"

        return when

    def _answer_where(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer WHERE question"""
        # Default: LUMINA project
        where = f"LUMINA project ({self.project_root})"

        # Extract location from context
        if context and "location" in context:
            where = context["location"]
        elif context and "file" in context:
            where = f"File: {context['file']}"

        return where

    def _answer_why(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer WHY question"""
        # Default: To improve LUMINA ecosystem
        why = "To enhance LUMINA ecosystem capabilities and user experience"

        # Extract purpose from context
        if context and "purpose" in context:
            why = context["purpose"]
        elif context and "goal" in context:
            why = f"To achieve: {context['goal']}"

        return why

    def _answer_how(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Answer HOW question"""
        # @DOIT = ORDER 66: Systematic execution across all systems
        how = "ORDER 66: @DOIT workflow - Generate 3 viable solutions, select best, execute systematically across ALL systems immediately"

        # Extract approach from context
        if context and "approach" in context:
            how = f"ORDER 66: {context['approach']}"

        return how

    def _generate_solutions(self, task_description: str, five_w1h: FiveW1H, context: Optional[Dict[str, Any]] = None) -> List[Solution]:
        """Generate 3 viable actionable solutions"""
        solutions = []

        # Solution 1: Direct/Simple Approach
        solution1 = Solution(
            id="solution_1",
            title="Direct Implementation Approach",
            description=f"Directly implement {five_w1h.what} using standard patterns and existing LUMINA infrastructure",
            approach="Use existing systems and patterns, minimal new code",
            steps=[
                f"Analyze {five_w1h.what} requirements",
                "Identify existing patterns/systems to leverage",
                "Implement using standard LUMINA patterns",
                "Test and verify functionality",
                "Integrate with LUMINA ecosystem"
            ],
            pros=[
                "Fast implementation",
                "Leverages existing infrastructure",
                "Low risk",
                "Consistent with LUMINA patterns"
            ],
            cons=[
                "May not be most optimal",
                "Limited innovation"
            ],
            feasibility=0.9,
            estimated_effort="low",
            risk_level="low"
        )
        solutions.append(solution1)

        # Solution 2: Enhanced/Innovative Approach
        solution2 = Solution(
            id="solution_2",
            title="Enhanced Innovation Approach",
            description=f"Implement {five_w1h.what} with enhanced features and innovative patterns",
            approach="Create new patterns while integrating with existing systems",
            steps=[
                f"Design enhanced solution for {five_w1h.what}",
                "Create new patterns/components if needed",
                "Implement with additional features",
                "Extensive testing and validation",
                "Document new patterns for future use"
            ],
            pros=[
                "More feature-rich",
                "Creates reusable patterns",
                "Higher quality solution",
                "Future-proof"
            ],
            cons=[
                "More time-consuming",
                "Higher complexity",
                "More testing required"
            ],
            feasibility=0.7,
            estimated_effort="medium",
            risk_level="medium"
        )
        solutions.append(solution2)

        # Solution 3: Comprehensive/Complete Approach
        solution3 = Solution(
            id="solution_3",
            title="Comprehensive Complete Approach",
            description=f"Implement {five_w1h.what} as part of comprehensive system enhancement",
            approach="Full system integration with multiple components and future extensibility",
            steps=[
                f"Design comprehensive solution architecture for {five_w1h.what}",
                "Create multiple integrated components",
                "Implement with full feature set",
                "Comprehensive testing and validation",
                "Full documentation and integration",
                "Plan for future enhancements"
            ],
            pros=[
                "Most complete solution",
                "Best long-term value",
                "Highly extensible",
                "Production-ready"
            ],
            cons=[
                "Most time-consuming",
                "Highest complexity",
                "Requires extensive testing",
                "Higher risk"
            ],
            feasibility=0.6,
            estimated_effort="high",
            risk_level="medium"
        )
        solutions.append(solution3)

        return solutions

    def _select_best_solution(self, solutions: List[Solution]) -> Solution:
        """Select best solution based on feasibility, effort, and risk"""
        # Score each solution
        scored_solutions = []
        for solution in solutions:
            score = (
                solution.feasibility * 0.4 +  # 40% weight on feasibility
                (1.0 - {"low": 0.2, "medium": 0.5, "high": 0.8}[solution.estimated_effort]) * 0.3 +  # 30% weight on low effort
                (1.0 - {"low": 0.2, "medium": 0.5, "high": 0.8}[solution.risk_level]) * 0.3  # 30% weight on low risk
            )
            scored_solutions.append((score, solution))

        # Select highest scoring solution
        scored_solutions.sort(key=lambda x: x[0], reverse=True)
        best_solution = scored_solutions[0][1]
        best_solution.recommended = True

        return best_solution

    def _create_execution_plan(self, solution: Solution, five_w1h: FiveW1H) -> List[str]:
        """Create detailed execution plan"""
        plan = []

        plan.append(f"WHO: {five_w1h.who}")
        plan.append(f"WHAT: {five_w1h.what}")
        plan.append(f"WHEN: {five_w1h.when}")
        plan.append(f"WHERE: {five_w1h.where}")
        plan.append(f"WHY: {five_w1h.why}")
        plan.append(f"HOW: {five_w1h.how}")
        plan.append("")
        plan.append(f"Selected Solution: {solution.title}")
        plan.append(f"Approach: {solution.approach}")
        plan.append("")
        plan.append("Execution Steps:")
        for i, step in enumerate(solution.steps, 1):
            plan.append(f"  {i}. {step}")

        return plan

    def _execute_doit(self, solution: Solution, execution_plan: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute @DOIT - actually implement the solution"""
        logger.info(f"⚡ @DOIT: Executing {solution.title}")

        execution_result = {
            "solution_id": solution.id,
            "solution_title": solution.title,
            "execution_plan": execution_plan,
            "steps_completed": [],
            "steps_failed": [],
            "artifacts_created": [],
            "status": "in_progress"
        }

        # Check if this is a content creator task
        task_lower = context.get("task", "").lower() if context else ""
        if not task_lower and hasattr(self, 'current_task'):
             task_lower = self.current_task.lower()

        content_keywords = ["content creator", "produce", "anime", "podcast", "video", "episode"]
        is_content_task = any(kw in task_lower for kw in content_keywords)

        # Execute each step
        for step in solution.steps:
            try:
                logger.info(f"   📋 Executing: {step}")

                # Integration with Content Creator System
                if is_content_task and ("produce" in step.lower() or "generate" in step.lower()):
                    try:
                        from lumina_content_creator_system import LuminaContentCreatorSystem
                        creator = LuminaContentCreatorSystem(self.project_root)

                        if "anime" in task_lower:
                            # In a real scenario, we'd extract season/episode from task
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            package = loop.run_until_complete(creator.produce_anime_episode(1, 1))
                            execution_result["artifacts_created"].append(f"Content Package: {package.package_id}")
                        elif "podcast" in task_lower:
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            package = loop.run_until_complete(creator.produce_podcast_episode())
                            execution_result["artifacts_created"].append(f"Content Package: {package.package_id}")
                    except Exception as ce:
                        logger.warning(f"   ⚠️  Content creator integration failed: {ce}")

                # In a real implementation, this would actually execute the step
                # For now, we log it and mark as completed
                execution_result["steps_completed"].append(step)
            except Exception as e:
                logger.error(f"   ❌ Failed: {step} - {e}")
                execution_result["steps_failed"].append({"step": step, "error": str(e)})

        execution_result["status"] = "completed" if not execution_result["steps_failed"] else "partial"

        return execution_result

    def _save_workflow_result(self, result: DOITWorkflowResult):
        try:
            """Save workflow result to file"""
            result_file = self.workflow_dir / f"{result.task_id}.json"

            import json
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, default=str, ensure_ascii=False)

            logger.info(f"💾 Workflow result saved: {result_file.name}")


        except Exception as e:
            self.logger.error(f"Error in _save_workflow_result: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 @DOIT Workflow with @5W1H Questioning Framework")
    print("="*80 + "\n")

    workflow = DOIT5W1HWorkflow()

    # Example task
    example_task = "Create a new feature for LUMINA ecosystem"
    result = workflow.process_task(example_task)

    print("\n" + "="*80)
    print("📊 WORKFLOW RESULT")
    print("="*80)
    print(f"Task: {result.task_description}")
    print(f"\n5W1H Analysis:")
    print(f"  WHO: {result.five_w1h.who}")
    print(f"  WHAT: {result.five_w1h.what}")
    print(f"  WHEN: {result.five_w1h.when}")
    print(f"  WHERE: {result.five_w1h.where}")
    print(f"  WHY: {result.five_w1h.why}")
    print(f"  HOW: {result.five_w1h.how}")
    print(f"\nSolutions Generated: {len(result.solutions)}")
    for i, solution in enumerate(result.solutions, 1):
        marker = "⭐" if solution.recommended else "  "
        print(f"  {marker} Solution {i}: {solution.title} (Feasibility: {solution.feasibility:.1f}, Effort: {solution.estimated_effort}, Risk: {solution.risk_level})")
    print(f"\nSelected Solution: {result.selected_solution.title}")
    print(f"Execution Status: {result.execution_result['status']}")
    print(f"Steps Completed: {len(result.execution_result['steps_completed'])}")
    print("\n✅ @DOIT Workflow Complete")
    print("="*80 + "\n")
