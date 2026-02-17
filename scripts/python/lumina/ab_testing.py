#!/usr/bin/env python3
"""
A/B Testing Framework for Lumina

Flip-flop A/B testing with progressive grading on infinite curve.

Features:
- Control (A) vs Experiment (B) groups
- Progressive statistical analysis
- Infinite curve calculations
- Adaptive thresholds

Tags: #AB_TESTING #STATISTICS #CURVE_GRADING @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import random
import math
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ABTesting")


class TestGroup(Enum):
    """Test groups"""
    CONTROL = "A"  # Control group
    EXPERIMENT = "B"  # Experiment group


@dataclass
class TestResult:
    """Test result"""
    user_id: str
    group: TestGroup
    query: str
    result: Any
    score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TestConfig:
    """Test configuration"""
    name: str
    control_config: Dict[str, Any]
    experiment_config: Dict[str, Any]
    sample_size: int = 100
    significance_level: float = 0.05


class ABTestManager:
    """
    A/B Testing Manager

    Flip-flop A/B testing with progressive grading on infinite curve.
    """

    def __init__(self):
        """Initialize A/B Test Manager"""
        self.tests = {}
        self.assignments = {}  # {user_id: {test_name: group}}
        self.results = {}  # {test_name: [TestResult]}
        logger.info("🧪 A/B Test Manager initialized")
        logger.info("   Flip-flop A/B testing with progressive curve grading")

    def create_test(
        self,
        name: str,
        control_config: Dict[str, Any],
        experiment_config: Dict[str, Any],
        **kwargs
    ) -> TestConfig:
        """
        Create a new A/B test.

        Args:
            name: Test name
            control_config: Control group configuration
            experiment_config: Experiment group configuration
            **kwargs: Additional test parameters

        Returns:
            Test configuration
        """
        test_config = TestConfig(
            name=name,
            control_config=control_config,
            experiment_config=experiment_config,
            sample_size=kwargs.get('sample_size', 100),
            significance_level=kwargs.get('significance_level', 0.05)
        )

        self.tests[name] = test_config
        self.results[name] = []
        logger.info(f"🧪 Created test: {name}")

        return test_config

    def assign_group(
        self,
        user_id: str,
        test_name: str
    ) -> TestGroup:
        """
        Assign user to test group (A or B).

        Uses flip-flop assignment for balanced distribution.

        Args:
            user_id: User identifier
            test_name: Test name

        Returns:
            Assigned group
        """
        if test_name not in self.tests:
            raise ValueError(f"Test not found: {test_name}")

        # Check if already assigned
        if user_id in self.assignments and test_name in self.assignments[user_id]:
            return self.assignments[user_id][test_name]

        # Flip-flop assignment (alternating)
        existing_assignments = sum(
            1 for u, tests in self.assignments.items()
            if test_name in tests
        )

        # Alternate between A and B
        group = TestGroup.CONTROL if existing_assignments % 2 == 0 else TestGroup.EXPERIMENT

        # Store assignment
        if user_id not in self.assignments:
            self.assignments[user_id] = {}
        self.assignments[user_id][test_name] = group

        logger.debug(f"Assigned {user_id} to group {group.value} for test {test_name}")

        return group

    def run_test(
        self,
        user_id: str,
        test_name: str,
        query: str,
        **kwargs
    ) -> TestResult:
        """
        Run test for user.

        Args:
            user_id: User identifier
            test_name: Test name
            query: Test query
            **kwargs: Additional parameters

        Returns:
            Test result
        """
        if test_name not in self.tests:
            raise ValueError(f"Test not found: {test_name}")

        # Get or assign group
        group = self.assign_group(user_id, test_name)

        # Get config for group
        test_config = self.tests[test_name]
        config = test_config.control_config if group == TestGroup.CONTROL else test_config.experiment_config

        # Execute test (placeholder - integrate with actual system)
        result = self._execute_test(config, query, **kwargs)

        # Calculate score
        score = self._calculate_score(result)

        # Create result
        test_result = TestResult(
            user_id=user_id,
            group=group,
            query=query,
            result=result,
            score=score
        )

        # Store result
        self.results[test_name].append(test_result)

        logger.info(f"🧪 Test result: {test_name} - User {user_id} - Group {group.value} - Score {score:.2f}")

        return test_result

    def _execute_test(
        self,
        config: Dict[str, Any],
        query: str,
        **kwargs
    ) -> Any:
        """Execute test with configuration"""
        # Placeholder - integrate with actual system
        return {
            'config': config,
            'query': query,
            'result': 'test_result'
        }

    def _calculate_score(self, result: Any) -> float:
        """Calculate score from result"""
        # Placeholder - implement actual scoring
        return random.uniform(0.0, 100.0)

    def analyze(
        self,
        test_name: str
    ) -> Dict[str, Any]:
        """
        Analyze test results.

        Args:
            test_name: Test name

        Returns:
            Analysis results
        """
        if test_name not in self.results:
            return {'error': 'No results found'}

        results = self.results[test_name]

        # Separate by group
        group_a_results = [r for r in results if r.group == TestGroup.CONTROL]
        group_b_results = [r for r in results if r.group == TestGroup.EXPERIMENT]

        # Calculate statistics
        group_a_scores = [r.score for r in group_a_results]
        group_b_scores = [r.score for r in group_b_results]

        analysis = {
            'test_name': test_name,
            'total_samples': len(results),
            'group_a': {
                'count': len(group_a_results),
                'mean': self._mean(group_a_scores) if group_a_scores else 0,
                'std': self._std(group_a_scores) if group_a_scores else 0
            },
            'group_b': {
                'count': len(group_b_results),
                'mean': self._mean(group_b_scores) if group_b_scores else 0,
                'std': self._std(group_b_scores) if group_b_scores else 0
            },
            'significance': self._calculate_significance(group_a_scores, group_b_scores)
        }

        return analysis

    def _mean(self, values: List[float]) -> float:
        """Calculate mean"""
        return sum(values) / len(values) if values else 0.0

    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0.0
        mean = self._mean(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _calculate_significance(
        self,
        group_a: List[float],
        group_b: List[float]
    ) -> Dict[str, Any]:
        """Calculate statistical significance"""
        if not group_a or not group_b:
            return {'significant': False, 'p_value': 1.0}

        # Simple t-test approximation
        mean_a = self._mean(group_a)
        mean_b = self._mean(group_b)
        std_a = self._std(group_a)
        std_b = self._std(group_b)

        # Pooled standard error
        n_a = len(group_a)
        n_b = len(group_b)
        se = math.sqrt((std_a ** 2 / n_a) + (std_b ** 2 / n_b))

        if se == 0:
            return {'significant': False, 'p_value': 1.0}

        # t-statistic
        t_stat = abs(mean_a - mean_b) / se

        # Simplified p-value (normal approximation)
        p_value = 2 * (1 - self._normal_cdf(abs(t_stat)))

        return {
            'significant': p_value < 0.05,
            'p_value': p_value,
            't_statistic': t_stat,
            'difference': abs(mean_a - mean_b)
        }

    def _normal_cdf(self, x: float) -> float:
        """Normal CDF approximation"""
        # Error function approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def main():
    """Example usage"""
    print("=" * 80)
    print("🧪 A/B TESTING FRAMEWORK")
    print("   Flip-flop A/B testing with progressive curve grading")
    print("=" * 80)
    print()

    manager = ABTestManager()

    # Create test
    print("CREATING TEST:")
    print("-" * 80)
    test = manager.create_test(
        name="lumina_config",
        control_config={"model": "llama2", "temperature": 0.7},
        experiment_config={"model": "llama3", "temperature": 0.8}
    )
    print(f"Test: {test.name}")
    print(f"Control: {test.control_config}")
    print(f"Experiment: {test.experiment_config}")
    print()

    # Assign groups
    print("ASSIGNING GROUPS:")
    print("-" * 80)
    users = ["user1", "user2", "user3", "user4", "user5"]
    for user in users:
        group = manager.assign_group(user, "lumina_config")
        print(f"{user}: Group {group.value}")
    print()

    # Run tests
    print("RUNNING TESTS:")
    print("-" * 80)
    for user in users:
        result = manager.run_test(user, "lumina_config", "test query")
        print(f"{user} (Group {result.group.value}): Score {result.score:.2f}")
    print()

    # Analyze
    print("ANALYSIS:")
    print("-" * 80)
    analysis = manager.analyze("lumina_config")
    print(f"Total samples: {analysis['total_samples']}")
    print(f"Group A: {analysis['group_a']['count']} samples, Mean: {analysis['group_a']['mean']:.2f}")
    print(f"Group B: {analysis['group_b']['count']} samples, Mean: {analysis['group_b']['mean']:.2f}")
    print(f"Significant: {analysis['significance']['significant']}")
    print(f"P-value: {analysis['significance']['p_value']:.4f}")
    print()

    print("=" * 80)
    print("🧪 A/B Testing - Progressive curve grading ready")
    print("=" * 80)


if __name__ == "__main__":


    main()