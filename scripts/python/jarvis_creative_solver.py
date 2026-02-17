#!/usr/bin/env python3
"""
JARVIS Creative Problem Solver

Generates novel solutions, thinks outside the box, combines disparate concepts.
Part of Phase 2 (Toddler → Child).

Tags: #JARVIS #CREATIVE_SOLVING #PHASE2 @JARVIS @LUMINA
"""

import sys
import json
import time
import random
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

logger = get_logger("JARVISCreativeSolver")


class CreativityLevel(Enum):
    """Creativity levels"""
    CONVENTIONAL = "conventional"  # Standard solutions
    INNOVATIVE = "innovative"  # New approaches
    CREATIVE = "creative"  # Novel combinations
    BREAKTHROUGH = "breakthrough"  # Revolutionary ideas


@dataclass
class CreativeSolution:
    """A creative solution to a problem"""
    solution_id: str
    problem: str
    solution: str
    creativity_level: CreativityLevel
    novelty_score: float  # 0-1, how novel is this solution
    feasibility_score: float  # 0-1, how feasible is this solution
    quality_score: float  # 0-1, overall quality
    concepts_combined: List[str] = field(default_factory=list)
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISCreativeSolver:
    """
    Creative problem-solving system

    Capabilities:
    - Generate novel solutions
    - Think outside the box
    - Combine disparate concepts
    - Evaluate and refine solutions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize creative solver"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_creative_solutions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.solutions_file = self.data_dir / "creative_solutions.json"

        self.solutions: List[CreativeSolution] = []
        self.concept_library: Dict[str, List[str]] = {}  # Domain -> concepts

        # Load existing data
        self._load_data()

        # Initialize concept library
        self._initialize_concept_library()

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
        logger.info("🎨 JARVIS CREATIVE SOLVER")
        logger.info("=" * 80)
        logger.info("   Generate novel solutions, think outside the box")
        logger.info("   Combine disparate concepts creatively")
        logger.info("")

    def generate_creative_solutions(self, problem: str, num_solutions: int = 5, creativity_level: CreativityLevel = CreativityLevel.CREATIVE) -> List[CreativeSolution]:
        """
        Generate creative solutions to a problem

        Args:
            problem: The problem to solve
            num_solutions: Number of solutions to generate
            creativity_level: Desired creativity level

        Returns:
            List of CreativeSolution objects
        """
        solutions = []

        for i in range(num_solutions):
            solution_id = f"creative_{int(time.time() * 1000)}_{i}"

            # Generate solution based on creativity level
            if creativity_level == CreativityLevel.CONVENTIONAL:
                solution = self._generate_conventional_solution(problem)
                novelty = 0.3
            elif creativity_level == CreativityLevel.INNOVATIVE:
                solution = self._generate_innovative_solution(problem)
                novelty = 0.6
            elif creativity_level == CreativityLevel.CREATIVE:
                solution = self._generate_creative_solution(problem)
                novelty = 0.8
            else:  # BREAKTHROUGH
                solution = self._generate_breakthrough_solution(problem)
                novelty = 0.95

            # Evaluate solution
            feasibility = self._evaluate_feasibility(solution, problem)
            quality = (novelty + feasibility) / 2

            # Extract concepts
            concepts = self._extract_concepts(solution, problem)

            creative_solution = CreativeSolution(
                solution_id=solution_id,
                problem=problem,
                solution=solution,
                creativity_level=creativity_level,
                novelty_score=novelty,
                feasibility_score=feasibility,
                quality_score=quality,
                concepts_combined=concepts,
                reasoning=f"Generated using {creativity_level.value} approach"
            )

            solutions.append(creative_solution)
            self.solutions.append(creative_solution)

        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            for sol in solutions:
                self.learning_pipeline.collect_learning_data(
                    LearningDataType.REASONING,
                    source="creative_solving",
                    context={"problem": problem, "creativity_level": creativity_level.value},
                    data={
                        "solution_id": sol.solution_id,
                        "novelty": sol.novelty_score,
                        "feasibility": sol.feasibility_score,
                        "quality": sol.quality_score
                    }
                )

        logger.info(f"🎨 Generated {len(solutions)} creative solutions (level: {creativity_level.value})")
        return solutions

    def _generate_conventional_solution(self, problem: str) -> str:
        """Generate conventional solution"""
        # Standard approaches
        templates = [
            f"Use standard approach: {problem}",
            f"Apply best practices to: {problem}",
            f"Follow established pattern for: {problem}"
        ]
        return random.choice(templates)

    def _generate_innovative_solution(self, problem: str) -> str:
        """Generate innovative solution"""
        # New approaches but grounded
        templates = [
            f"Apply modern techniques to: {problem}",
            f"Use innovative approach combining best practices: {problem}",
            f"Leverage new technologies for: {problem}"
        ]
        return random.choice(templates)

    def _generate_creative_solution(self, problem: str) -> str:
        """Generate creative solution"""
        # Combine concepts from different domains
        concepts = self._get_random_concepts(2)
        combined = " + ".join(concepts)

        return f"Combine {combined} to solve: {problem}"

    def _generate_breakthrough_solution(self, problem: str) -> str:
        """Generate breakthrough solution"""
        # Revolutionary approach
        concepts = self._get_random_concepts(3)
        combined = " + ".join(concepts)

        return f"Revolutionary approach: Combine {combined} in novel way to solve: {problem}"

    def _get_random_concepts(self, count: int) -> List[str]:
        """Get random concepts from library"""
        all_concepts = []
        for domain_concepts in self.concept_library.values():
            all_concepts.extend(domain_concepts)

        if len(all_concepts) < count:
            # Fallback concepts
            all_concepts.extend([
                "modular design", "distributed systems", "event-driven architecture",
                "microservices", "containerization", "automation", "machine learning",
                "real-time processing", "scalable architecture", "resilient design"
            ])

        return random.sample(all_concepts, min(count, len(all_concepts)))

    def _extract_concepts(self, solution: str, problem: str) -> List[str]:
        """Extract concepts from solution"""
        concepts = []

        # Look for known concepts
        for domain, domain_concepts in self.concept_library.items():
            for concept in domain_concepts:
                if concept.lower() in solution.lower():
                    concepts.append(concept)

        return concepts[:5]  # Limit to 5 concepts

    def _evaluate_feasibility(self, solution: str, problem: str) -> float:
        """Evaluate solution feasibility"""
        # Simple heuristics
        feasibility_indicators = ["standard", "proven", "established", "tested", "reliable"]
        risk_indicators = ["experimental", "untested", "novel", "unproven", "risky"]

        solution_lower = solution.lower()

        feasibility_count = sum(1 for ind in feasibility_indicators if ind in solution_lower)
        risk_count = sum(1 for ind in risk_indicators if ind in solution_lower)

        base_feasibility = 0.7
        feasibility = base_feasibility + (feasibility_count * 0.1) - (risk_count * 0.15)

        return max(0.0, min(1.0, feasibility))

    def evaluate_solutions(self, solutions: List[CreativeSolution]) -> List[CreativeSolution]:
        """
        Evaluate and rank solutions

        Args:
            solutions: List of solutions to evaluate

        Returns:
            Sorted list (best first)
        """
        # Sort by quality score (descending)
        return sorted(solutions, key=lambda s: s.quality_score, reverse=True)

    def refine_solution(self, solution: CreativeSolution, feedback: Optional[str] = None) -> CreativeSolution:
        """
        Refine a solution based on feedback

        Args:
            solution: The solution to refine
            feedback: Optional feedback to incorporate

        Returns:
            Refined CreativeSolution
        """
        # Create refined version
        refined_id = f"{solution.solution_id}_refined"

        # Improve based on feedback
        if feedback:
            if "feasibility" in feedback.lower() or "practical" in feedback.lower():
                # Improve feasibility
                refined_solution = CreativeSolution(
                    solution_id=refined_id,
                    problem=solution.problem,
                    solution=f"{solution.solution} (refined for practicality)",
                    creativity_level=solution.creativity_level,
                    novelty_score=solution.novelty_score * 0.9,  # Slight decrease
                    feasibility_score=min(1.0, solution.feasibility_score + 0.2),  # Increase
                    quality_score=0.0,  # Will recalculate
                    concepts_combined=solution.concepts_combined,
                    reasoning=f"Refined based on feedback: {feedback}"
                )
            else:
                # Improve novelty
                refined_solution = CreativeSolution(
                    solution_id=refined_id,
                    problem=solution.problem,
                    solution=f"{solution.solution} (enhanced creativity)",
                    creativity_level=CreativityLevel.BREAKTHROUGH if solution.creativity_level == CreativityLevel.CREATIVE else solution.creativity_level,
                    novelty_score=min(1.0, solution.novelty_score + 0.1),
                    feasibility_score=solution.feasibility_score * 0.95,  # Slight decrease
                    quality_score=0.0,
                    concepts_combined=solution.concepts_combined + self._get_random_concepts(1),
                    reasoning=f"Refined based on feedback: {feedback}"
                )
        else:
            # General refinement - balance novelty and feasibility
            refined_solution = CreativeSolution(
                solution_id=refined_id,
                problem=solution.problem,
                solution=f"{solution.solution} (refined)",
                creativity_level=solution.creativity_level,
                novelty_score=solution.novelty_score,
                feasibility_score=min(1.0, solution.feasibility_score + 0.1),
                quality_score=0.0,
                concepts_combined=solution.concepts_combined,
                reasoning="General refinement"
            )

        # Recalculate quality
        refined_solution.quality_score = (refined_solution.novelty_score + refined_solution.feasibility_score) / 2

        self.solutions.append(refined_solution)
        self._save_data()

        logger.info(f"✨ Refined solution: quality {refined_solution.quality_score:.2%} (was {solution.quality_score:.2%})")
        return refined_solution

    def _initialize_concept_library(self):
        """Initialize concept library with domain concepts"""
        self.concept_library = {
            "architecture": [
                "microservices", "monolith", "serverless", "event-driven", "layered architecture",
                "hexagonal architecture", "CQRS", "event sourcing", "API gateway"
            ],
            "data": [
                "relational database", "NoSQL", "data warehouse", "data lake", "streaming",
                "batch processing", "ETL", "data pipeline", "real-time analytics"
            ],
            "deployment": [
                "containers", "Kubernetes", "Docker", "CI/CD", "blue-green deployment",
                "canary release", "infrastructure as code", "automation"
            ],
            "communication": [
                "REST API", "GraphQL", "gRPC", "message queue", "pub/sub", "webhooks",
                "synchronous", "asynchronous", "event streaming"
            ],
            "security": [
                "authentication", "authorization", "encryption", "OAuth", "JWT",
                "rate limiting", "input validation", "security headers"
            ],
            "performance": [
                "caching", "CDN", "load balancing", "scaling", "optimization",
                "profiling", "monitoring", "performance testing"
            ]
        }

    def _load_data(self):
        """Load solutions from disk"""
        try:
            if self.solutions_file.exists():
                with open(self.solutions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.solutions = [
                        CreativeSolution(
                            **{
                                **sol_data,
                                "creativity_level": CreativityLevel(sol_data["creativity_level"])
                            }
                        )
                        for sol_data in data.get("solutions", [])
                    ]
                    logger.debug(f"Loaded {len(self.solutions)} creative solutions")
        except Exception as e:
            logger.debug(f"Could not load solution data: {e}")

    def _save_data(self):
        """Save solutions to disk"""
        try:
            data = {
                "solutions": [
                    {
                        **asdict(sol),
                        "creativity_level": sol.creativity_level.value
                    }
                    for sol in self.solutions
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.solutions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save solution data: {e}")


# Singleton pattern
_creative_solver_instance: Optional[JARVISCreativeSolver] = None


def get_jarvis_creative_solver(project_root: Optional[Path] = None) -> JARVISCreativeSolver:
    """Get singleton creative solver instance"""
    global _creative_solver_instance
    if _creative_solver_instance is None:
        _creative_solver_instance = JARVISCreativeSolver(project_root)
    return _creative_solver_instance


if __name__ == "__main__":
    solver = get_jarvis_creative_solver()

    # Test creative solution generation
    solutions = solver.generate_creative_solutions(
        "Improve system performance",
        num_solutions=3,
        creativity_level=CreativityLevel.CREATIVE
    )

    for sol in solutions:
        print(f"Solution: {sol.solution}")
        print(f"  Novelty: {sol.novelty_score:.2%}, Feasibility: {sol.feasibility_score:.2%}, Quality: {sol.quality_score:.2%}")
        print("")
