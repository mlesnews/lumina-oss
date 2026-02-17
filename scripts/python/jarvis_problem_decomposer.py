#!/usr/bin/env python3
"""
JARVIS Problem Decomposer

Breaks complex problems into manageable steps, identifies dependencies,
and plans solution paths. Part of Phase 2 (Toddler → Child).

Tags: #JARVIS #PROBLEM_DECOMPOSITION #PHASE2 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
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

logger = get_logger("JARVISProblemDecomposer")


class ProblemComplexity(Enum):
    """Problem complexity levels"""
    SIMPLE = "simple"  # Single step
    MODERATE = "moderate"  # 2-5 steps
    COMPLEX = "complex"  # 6-15 steps
    VERY_COMPLEX = "very_complex"  # 16+ steps


@dataclass
class ProblemStep:
    """A decomposed step in solving a problem"""
    step_id: str
    description: str
    dependencies: List[str]  # IDs of steps that must complete first
    estimated_difficulty: float  # 0-1
    required_resources: List[str] = field(default_factory=list)
    expected_duration: Optional[float] = None  # seconds
    priority: int = 5  # 1-10, higher = more important


@dataclass
class DecomposedProblem:
    """A problem broken down into steps"""
    problem_id: str
    original_problem: str
    steps: List[ProblemStep]
    complexity: ProblemComplexity
    estimated_total_duration: Optional[float] = None
    dependencies_graph: Dict[str, List[str]] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISProblemDecomposer:
    """
    Decomposes complex problems into manageable steps

    Identifies:
    - Sub-problems
    - Dependencies between steps
    - Execution order
    - Resource requirements
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize problem decomposer"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_problem_decomposition"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.decompositions_file = self.data_dir / "decompositions.json"

        self.decompositions: List[DecomposedProblem] = []

        # Load existing data
        self._load_data()

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
        logger.info("🔧 JARVIS PROBLEM DECOMPOSER")
        logger.info("=" * 80)
        logger.info("   Break complex problems into manageable steps")
        logger.info("   Identify dependencies and plan solution paths")
        logger.info("")

    def decompose_problem(self, problem: str, context: Dict[str, Any] = None) -> DecomposedProblem:
        """
        Decompose a problem into steps

        Args:
            problem: The problem to decompose
            context: Additional context

        Returns:
            DecomposedProblem with steps and dependencies
        """
        problem_id = f"problem_{int(time.time() * 1000)}"
        context = context or {}

        # Analyze problem complexity
        complexity = self._assess_complexity(problem)

        # Extract key components
        steps = self._extract_steps(problem, context)

        # Identify dependencies
        dependencies_graph = self._build_dependencies_graph(steps)

        # Calculate estimated duration
        estimated_duration = sum(
            step.expected_duration or 60.0  # Default 60 seconds per step
            for step in steps
        )

        decomposition = DecomposedProblem(
            problem_id=problem_id,
            original_problem=problem,
            steps=steps,
            complexity=complexity,
            estimated_total_duration=estimated_duration,
            dependencies_graph=dependencies_graph
        )

        self.decompositions.append(decomposition)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="problem_decomposition",
                context={"problem": problem, "context": context},
                data={
                    "problem_id": problem_id,
                    "steps": len(steps),
                    "complexity": complexity.value,
                    "estimated_duration": estimated_duration
                }
            )

        logger.info(f"🔧 Decomposed problem: {len(steps)} steps, complexity: {complexity.value}")
        return decomposition

    def _assess_complexity(self, problem: str) -> ProblemComplexity:
        """Assess problem complexity"""
        # Simple heuristics
        keywords_complex = ["multiple", "several", "many", "various", "complex", "integrate"]
        keywords_very_complex = ["system", "architecture", "framework", "comprehensive", "complete"]

        problem_lower = problem.lower()

        complex_count = sum(1 for kw in keywords_complex if kw in problem_lower)
        very_complex_count = sum(1 for kw in keywords_very_complex if kw in problem_lower)

        if very_complex_count >= 2:
            return ProblemComplexity.VERY_COMPLEX
        elif complex_count >= 2 or very_complex_count >= 1:
            return ProblemComplexity.COMPLEX
        elif complex_count >= 1:
            return ProblemComplexity.MODERATE
        else:
            return ProblemComplexity.SIMPLE

    def _extract_steps(self, problem: str, context: Dict[str, Any]) -> List[ProblemStep]:
        """Extract steps from problem description"""
        steps = []

        # Look for numbered steps, bullet points, or sequential actions
        problem_lower = problem.lower()

        # Check for explicit step markers
        if "step" in problem_lower or "1." in problem or "first" in problem_lower:
            # Try to extract numbered steps
            lines = problem.split("\n")
            step_num = 0
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if it's a step marker
                if any(marker in line.lower() for marker in ["step", "first", "second", "third", "then", "next"]):
                    step_num += 1
                    step_id = f"step_{step_num}"

                    # Extract step description
                    description = line
                    for marker in ["step", "first", "second", "third", "fourth", "fifth", "then", "next", ":", "-", "1.", "2.", "3.", "4.", "5."]:
                        description = description.lower().replace(marker, "").strip()

                    if description:
                        step = ProblemStep(
                            step_id=step_id,
                            description=description,
                            dependencies=[],
                            estimated_difficulty=0.5,
                            priority=10 - step_num  # Earlier steps have higher priority
                        )
                        steps.append(step)
        else:
            # No explicit steps - decompose based on keywords
            # Look for action verbs
            action_verbs = ["implement", "create", "build", "develop", "integrate", "configure", "setup", "install", "test", "verify"]

            found_actions = []
            for verb in action_verbs:
                if verb in problem_lower:
                    # Find the phrase containing this verb
                    idx = problem_lower.find(verb)
                    # Extract sentence or phrase
                    start = max(0, idx - 50)
                    end = min(len(problem), idx + 100)
                    phrase = problem[start:end].strip()
                    found_actions.append((verb, phrase))

            if found_actions:
                for i, (verb, phrase) in enumerate(found_actions, 1):
                    step = ProblemStep(
                        step_id=f"step_{i}",
                        description=phrase,
                        dependencies=[],
                        estimated_difficulty=0.5,
                        priority=10 - i
                    )
                    steps.append(step)
            else:
                # Single step - problem is simple
                step = ProblemStep(
                    step_id="step_1",
                    description=problem,
                    dependencies=[],
                    estimated_difficulty=0.5,
                    priority=10
                )
                steps.append(step)

        # If no steps found, create a default single step
        if not steps:
            step = ProblemStep(
                step_id="step_1",
                description=problem,
                dependencies=[],
                estimated_difficulty=0.5,
                priority=10
            )
            steps.append(step)

        return steps

    def _build_dependencies_graph(self, steps: List[ProblemStep]) -> Dict[str, List[str]]:
        """Build dependency graph between steps"""
        graph = {}

        # Simple dependency detection: later steps depend on earlier ones
        for i, step in enumerate(steps):
            dependencies = []

            # Check for explicit dependencies in description
            if "after" in step.description.lower() or "following" in step.description.lower():
                # Try to find referenced step
                for j, other_step in enumerate(steps):
                    if j < i and other_step.step_id in step.description.lower():
                        dependencies.append(other_step.step_id)

            # Default: sequential dependencies
            if not dependencies and i > 0:
                # Each step depends on previous step
                dependencies.append(steps[i-1].step_id)

            graph[step.step_id] = dependencies
            step.dependencies = dependencies

        return graph

    def get_execution_order(self, decomposition: DecomposedProblem) -> List[str]:
        """
        Get optimal execution order for steps (topological sort)

        Args:
            decomposition: The decomposed problem

        Returns:
            List of step IDs in execution order
        """
        # Topological sort
        in_degree = {step.step_id: len(step.dependencies) for step in decomposition.steps}
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort by priority (higher priority first)
            queue.sort(key=lambda sid: next(
                s.priority for s in decomposition.steps if s.step_id == sid
            ), reverse=True)

            current = queue.pop(0)
            result.append(current)

            # Update dependencies
            for step in decomposition.steps:
                if current in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step.step_id)

        # Add any remaining steps (cycles or isolated)
        remaining = [s.step_id for s in decomposition.steps if s.step_id not in result]
        result.extend(remaining)

        return result

    def _load_data(self):
        """Load decomposition data from disk"""
        try:
            if self.decompositions_file.exists():
                with open(self.decompositions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decompositions = [
                        DecomposedProblem(
                            **{
                                **decomp_data,
                                "complexity": ProblemComplexity(decomp_data["complexity"]),
                                "steps": [
                                    ProblemStep(**step_data)
                                    for step_data in decomp_data["steps"]
                                ]
                            }
                        )
                        for decomp_data in data.get("decompositions", [])
                    ]
                    logger.debug(f"Loaded {len(self.decompositions)} problem decompositions")
        except Exception as e:
            logger.debug(f"Could not load decomposition data: {e}")

    def _save_data(self):
        """Save decomposition data to disk"""
        try:
            data = {
                "decompositions": [
                    {
                        **asdict(decomp),
                        "complexity": decomp.complexity.value
                    }
                    for decomp in self.decompositions
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.decompositions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save decomposition data: {e}")


# Singleton pattern
_decomposer_instance: Optional[JARVISProblemDecomposer] = None


def get_jarvis_problem_decomposer(project_root: Optional[Path] = None) -> JARVISProblemDecomposer:
    """Get singleton problem decomposer instance"""
    global _decomposer_instance
    if _decomposer_instance is None:
        _decomposer_instance = JARVISProblemDecomposer(project_root)
    return _decomposer_instance


if __name__ == "__main__":
    decomposer = get_jarvis_problem_decomposer()

    # Test decomposition
    problem = "Implement a new feature: First, create the database schema. Then, build the API endpoints. Finally, create the frontend interface."
    decomposition = decomposer.decompose_problem(problem)

    print(f"Problem: {decomposition.original_problem}")
    print(f"Complexity: {decomposition.complexity.value}")
    print(f"Steps: {len(decomposition.steps)}")
    print(f"Execution order: {decomposer.get_execution_order(decomposition)}")
