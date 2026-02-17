#!/usr/bin/env python3
"""
JARVIS Solution Evaluator

Evaluates solution quality, compares alternatives, selects best approach.
Part of Phase 2 (Toddler → Child).

Tags: #JARVIS #SOLUTION_EVALUATION #PHASE2 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
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

logger = get_logger("JARVISSolutionEvaluator")


class EvaluationCriteria(Enum):
    """Solution evaluation criteria"""
    FEASIBILITY = "feasibility"
    EFFICIENCY = "efficiency"
    COST = "cost"
    MAINTAINABILITY = "maintainability"
    SCALABILITY = "scalability"
    RELIABILITY = "reliability"
    NOVELTY = "novelty"
    QUALITY = "quality"


@dataclass
class SolutionEvaluation:
    """Evaluation of a solution"""
    evaluation_id: str
    solution_id: str
    criteria_scores: Dict[EvaluationCriteria, float]  # 0-1 for each criterion
    overall_score: float  # 0-1, weighted average
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SolutionComparison:
    """Comparison of multiple solutions"""
    comparison_id: str
    problem: str
    solutions: List[str]  # Solution IDs
    evaluations: Dict[str, SolutionEvaluation]  # solution_id -> evaluation
    best_solution_id: Optional[str] = None
    ranking: List[Tuple[str, float]] = field(default_factory=list)  # (solution_id, score)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISSolutionEvaluator:
    """
    Evaluates and compares solutions

    Capabilities:
    - Evaluate solution quality across multiple criteria
    - Compare alternative solutions
    - Select best approach
    - Provide recommendations
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize solution evaluator"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_solution_evaluations"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.evaluations_file = self.data_dir / "evaluations.json"
        self.comparisons_file = self.data_dir / "comparisons.json"

        self.evaluations: List[SolutionEvaluation] = []
        self.comparisons: List[SolutionComparison] = []

        # Criteria weights (can be customized)
        self.criteria_weights = {
            EvaluationCriteria.FEASIBILITY: 0.25,
            EvaluationCriteria.EFFICIENCY: 0.15,
            EvaluationCriteria.COST: 0.10,
            EvaluationCriteria.MAINTAINABILITY: 0.15,
            EvaluationCriteria.SCALABILITY: 0.10,
            EvaluationCriteria.RELIABILITY: 0.15,
            EvaluationCriteria.NOVELTY: 0.05,
            EvaluationCriteria.QUALITY: 0.05
        }

        # Load existing data
        self._load_data()

        # Integrate with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
        except ImportError:
            self.learning_pipeline = None

        logger.info("=" * 80)
        logger.info("📊 JARVIS SOLUTION EVALUATOR")
        logger.info("=" * 80)
        logger.info("   Evaluate solution quality, compare alternatives")
        logger.info("   Select best approach")
        logger.info("")

    def evaluate_solution(self, solution_id: str, solution: str, problem: str, context: Dict[str, Any] = None) -> SolutionEvaluation:
        """
        Evaluate a solution across multiple criteria

        Args:
            solution_id: ID of the solution
            solution: The solution description
            problem: The problem it solves
            context: Additional context

        Returns:
            SolutionEvaluation with scores and analysis
        """
        evaluation_id = f"eval_{int(time.time() * 1000)}"
        context = context or {}

        # Evaluate each criterion
        criteria_scores = {}

        # Feasibility
        criteria_scores[EvaluationCriteria.FEASIBILITY] = self._evaluate_feasibility(solution, problem)

        # Efficiency
        criteria_scores[EvaluationCriteria.EFFICIENCY] = self._evaluate_efficiency(solution, problem)

        # Cost
        criteria_scores[EvaluationCriteria.COST] = self._evaluate_cost(solution, problem)

        # Maintainability
        criteria_scores[EvaluationCriteria.MAINTAINABILITY] = self._evaluate_maintainability(solution, problem)

        # Scalability
        criteria_scores[EvaluationCriteria.SCALABILITY] = self._evaluate_scalability(solution, problem)

        # Reliability
        criteria_scores[EvaluationCriteria.RELIABILITY] = self._evaluate_reliability(solution, problem)

        # Novelty
        criteria_scores[EvaluationCriteria.NOVELTY] = self._evaluate_novelty(solution, problem)

        # Overall Quality
        criteria_scores[EvaluationCriteria.QUALITY] = self._evaluate_quality(solution, problem)

        # Calculate weighted overall score
        overall_score = sum(
            self.criteria_weights.get(criterion, 0.1) * score
            for criterion, score in criteria_scores.items()
        )

        # Identify strengths and weaknesses
        strengths = [
            criterion.value for criterion, score in criteria_scores.items()
            if score >= 0.8
        ]
        weaknesses = [
            criterion.value for criterion, score in criteria_scores.items()
            if score < 0.5
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(criteria_scores, solution, problem)

        evaluation = SolutionEvaluation(
            evaluation_id=evaluation_id,
            solution_id=solution_id,
            criteria_scores=criteria_scores,
            overall_score=overall_score,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )

        self.evaluations.append(evaluation)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="solution_evaluation",
                context={"solution_id": solution_id, "problem": problem, "context": context},
                data={
                    "evaluation_id": evaluation_id,
                    "overall_score": overall_score,
                    "criteria_scores": {k.value: v for k, v in criteria_scores.items()}
                }
            )

        logger.info(f"📊 Evaluated solution {solution_id}: overall score {overall_score:.2%}")
        return evaluation

    def compare_solutions(self, problem: str, solutions: List[Dict[str, str]]) -> SolutionComparison:
        """
        Compare multiple solutions

        Args:
            problem: The problem being solved
            solutions: List of {solution_id, solution_description} dicts

        Returns:
            SolutionComparison with rankings
        """
        comparison_id = f"comparison_{int(time.time() * 1000)}"

        # Evaluate each solution
        evaluations = {}
        for sol_dict in solutions:
            solution_id = sol_dict["solution_id"]
            solution = sol_dict["solution"]

            evaluation = self.evaluate_solution(solution_id, solution, problem)
            evaluations[solution_id] = evaluation

        # Rank solutions by overall score
        ranking = sorted(
            [(sid, eval.overall_score) for sid, eval in evaluations.items()],
            key=lambda x: x[1],
            reverse=True
        )

        best_solution_id = ranking[0][0] if ranking else None

        comparison = SolutionComparison(
            comparison_id=comparison_id,
            problem=problem,
            solutions=[sol["solution_id"] for sol in solutions],
            evaluations=evaluations,
            best_solution_id=best_solution_id,
            ranking=ranking
        )

        self.comparisons.append(comparison)
        self._save_data()

        logger.info(f"📊 Compared {len(solutions)} solutions, best: {best_solution_id} (score: {ranking[0][1]:.2%})")
        return comparison

    def _evaluate_feasibility(self, solution: str, problem: str) -> float:
        """Evaluate feasibility (0-1)"""
        feasibility_keywords = ["standard", "proven", "established", "tested", "reliable", "practical"]
        risk_keywords = ["experimental", "untested", "novel", "unproven", "risky", "complex"]

        solution_lower = solution.lower()

        feasibility_score = 0.6  # Base
        feasibility_score += sum(0.1 for kw in feasibility_keywords if kw in solution_lower)
        feasibility_score -= sum(0.15 for kw in risk_keywords if kw in solution_lower)

        return max(0.0, min(1.0, feasibility_score))

    def _evaluate_efficiency(self, solution: str, problem: str) -> float:
        """Evaluate efficiency (0-1)"""
        efficiency_keywords = ["optimized", "efficient", "fast", "quick", "streamlined", "automated"]
        inefficiency_keywords = ["slow", "inefficient", "manual", "tedious", "redundant"]

        solution_lower = solution.lower()

        efficiency_score = 0.6
        efficiency_score += sum(0.1 for kw in efficiency_keywords if kw in solution_lower)
        efficiency_score -= sum(0.1 for kw in inefficiency_keywords if kw in solution_lower)

        return max(0.0, min(1.0, efficiency_score))

    def _evaluate_cost(self, solution: str, problem: str) -> float:
        """Evaluate cost-effectiveness (0-1, higher = lower cost)"""
        cost_keywords = ["free", "low-cost", "efficient", "minimal", "open-source", "standard"]
        expensive_keywords = ["expensive", "costly", "premium", "enterprise", "complex"]

        solution_lower = solution.lower()

        cost_score = 0.6
        cost_score += sum(0.1 for kw in cost_keywords if kw in solution_lower)
        cost_score -= sum(0.1 for kw in expensive_keywords if kw in solution_lower)

        return max(0.0, min(1.0, cost_score))

    def _evaluate_maintainability(self, solution: str, problem: str) -> float:
        """Evaluate maintainability (0-1)"""
        maintainability_keywords = ["simple", "clean", "modular", "documented", "standard", "maintainable"]
        complexity_keywords = ["complex", "monolithic", "legacy", "undocumented", "spaghetti"]

        solution_lower = solution.lower()

        maintainability_score = 0.6
        maintainability_score += sum(0.1 for kw in maintainability_keywords if kw in solution_lower)
        maintainability_score -= sum(0.1 for kw in complexity_keywords if kw in solution_lower)

        return max(0.0, min(1.0, maintainability_score))

    def _evaluate_scalability(self, solution: str, problem: str) -> float:
        """Evaluate scalability (0-1)"""
        scalability_keywords = ["scalable", "distributed", "horizontal", "elastic", "cloud", "microservices"]
        scalability_issues = ["monolithic", "single-server", "bottleneck", "limited"]

        solution_lower = solution.lower()

        scalability_score = 0.6
        scalability_score += sum(0.1 for kw in scalability_keywords if kw in solution_lower)
        scalability_score -= sum(0.1 for kw in scalability_issues if kw in solution_lower)

        return max(0.0, min(1.0, scalability_score))

    def _evaluate_reliability(self, solution: str, problem: str) -> float:
        """Evaluate reliability (0-1)"""
        reliability_keywords = ["reliable", "robust", "fault-tolerant", "resilient", "tested", "proven"]
        reliability_issues = ["fragile", "unstable", "experimental", "untested"]

        solution_lower = solution.lower()

        reliability_score = 0.6
        reliability_score += sum(0.1 for kw in reliability_keywords if kw in solution_lower)
        reliability_score -= sum(0.15 for kw in reliability_issues if kw in solution_lower)

        return max(0.0, min(1.0, reliability_score))

    def _evaluate_novelty(self, solution: str, problem: str) -> float:
        """Evaluate novelty (0-1)"""
        novelty_keywords = ["novel", "innovative", "creative", "breakthrough", "revolutionary", "new"]
        conventional_keywords = ["standard", "conventional", "traditional", "established"]

        solution_lower = solution.lower()

        novelty_score = 0.5
        novelty_score += sum(0.15 for kw in novelty_keywords if kw in solution_lower)
        novelty_score -= sum(0.1 for kw in conventional_keywords if kw in solution_lower)

        return max(0.0, min(1.0, novelty_score))

    def _evaluate_quality(self, solution: str, problem: str) -> float:
        """Evaluate overall quality (0-1)"""
        quality_keywords = ["high-quality", "well-designed", "best-practice", "professional", "polished"]
        quality_issues = ["hacky", "quick-fix", "temporary", "workaround"]

        solution_lower = solution.lower()

        quality_score = 0.6
        quality_score += sum(0.1 for kw in quality_keywords if kw in solution_lower)
        quality_score -= sum(0.15 for kw in quality_issues if kw in solution_lower)

        return max(0.0, min(1.0, quality_score))

    def _generate_recommendations(self, criteria_scores: Dict[EvaluationCriteria, float], solution: str, problem: str) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []

        # Recommend improvements for low-scoring criteria
        for criterion, score in criteria_scores.items():
            if score < 0.6:
                if criterion == EvaluationCriteria.FEASIBILITY:
                    recommendations.append("Consider more proven/established approaches to improve feasibility")
                elif criterion == EvaluationCriteria.EFFICIENCY:
                    recommendations.append("Optimize solution for better efficiency")
                elif criterion == EvaluationCriteria.COST:
                    recommendations.append("Look for cost-effective alternatives")
                elif criterion == EvaluationCriteria.MAINTAINABILITY:
                    recommendations.append("Simplify solution for better maintainability")
                elif criterion == EvaluationCriteria.SCALABILITY:
                    recommendations.append("Design for scalability from the start")
                elif criterion == EvaluationCriteria.RELIABILITY:
                    recommendations.append("Add fault-tolerance and testing for reliability")

        return recommendations

    def _load_data(self):
        """Load evaluations from disk"""
        try:
            if self.evaluations_file.exists():
                with open(self.evaluations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.evaluations = [
                        SolutionEvaluation(
                            **{
                                **eval_data,
                                "criteria_scores": {
                                    EvaluationCriteria(k): v
                                    for k, v in eval_data["criteria_scores"].items()
                                }
                            }
                        )
                        for eval_data in data.get("evaluations", [])
                    ]
                    logger.debug(f"Loaded {len(self.evaluations)} solution evaluations")
        except Exception as e:
            logger.debug(f"Could not load evaluation data: {e}")

        try:
            if self.comparisons_file.exists():
                with open(self.comparisons_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load comparisons (simplified - would need full evaluation objects)
                    logger.debug(f"Loaded {len(data.get('comparisons', []))} solution comparisons")
        except Exception as e:
            logger.debug(f"Could not load comparison data: {e}")

    def _save_data(self):
        """Save evaluations to disk"""
        try:
            data = {
                "evaluations": [
                    {
                        **asdict(eval),
                        "criteria_scores": {k.value: v for k, v in eval.criteria_scores.items()}
                    }
                    for eval in self.evaluations
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.evaluations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save evaluation data: {e}")

        try:
            data = {
                "comparisons": [
                    {
                        **asdict(comp),
                        "evaluations": {
                            sid: {
                                **asdict(eval),
                                "criteria_scores": {k.value: v for k, v in eval.criteria_scores.items()}
                            }
                            for sid, eval in comp.evaluations.items()
                        }
                    }
                    for comp in self.comparisons
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.comparisons_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save comparison data: {e}")


# Singleton pattern
_evaluator_instance: Optional[JARVISSolutionEvaluator] = None


def get_jarvis_solution_evaluator(project_root: Optional[Path] = None) -> JARVISSolutionEvaluator:
    """Get singleton solution evaluator instance"""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = JARVISSolutionEvaluator(project_root)
    return _evaluator_instance


if __name__ == "__main__":
    evaluator = get_jarvis_solution_evaluator()

    # Test evaluation
    evaluation = evaluator.evaluate_solution(
        "sol_1",
        "Use microservices architecture with containerization for scalable deployment",
        "Build a scalable web application"
    )

    print(f"Solution evaluation:")
    print(f"  Overall score: {evaluation.overall_score:.2%}")
    print(f"  Strengths: {evaluation.strengths}")
    print(f"  Weaknesses: {evaluation.weaknesses}")
    print(f"  Recommendations: {evaluation.recommendations}")
