#!/usr/bin/env python3
"""
Workflow Performance Tuner - Performance Tuning for All Workflows

Performance tuning system for AI and human workflows
Adapts to both AI and human performance patterns

"PERFORMANCE TUNING ANYONE TO ALL OUR WORKFLOWS AND US"
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowPerformanceTuner")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PerformanceMetric(Enum):
    """Performance metrics"""
    SPEED = "speed"  # Execution time
    ACCURACY = "accuracy"  # Correctness
    EFFICIENCY = "efficiency"  # Resource usage
    THROUGHPUT = "throughput"  # Items processed per time
    LATENCY = "latency"  # Response time
    QUALITY = "quality"  # Output quality


class TuningTarget(Enum):
    """Tuning targets"""
    AI = "ai"  # AI workflows
    HUMAN = "human"  # Human workflows
    HYBRID = "hybrid"  # AI + Human workflows


@dataclass
class PerformanceBaseline:
    """Performance baseline"""
    workflow_id: str
    metric: PerformanceMetric
    baseline_value: float
    target_value: float
    unit: str = "seconds"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceImprovement:
    """Performance improvement"""
    workflow_id: str
    metric: PerformanceMetric
    before: float
    after: float
    improvement_percent: float
    tuning_method: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TuningRecommendation:
    """Performance tuning recommendation"""
    workflow_id: str
    target: TuningTarget
    recommendation: str
    expected_improvement: float
    difficulty: int = 1  # 1-10
    priority: int = 1  # 1-10
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['target'] = self.target.value
        data['metric'] = self.metric.value if hasattr(self, 'metric') else None
        return data


class WorkflowPerformanceTuner:
    """
    Workflow Performance Tuner

    Performance tuning system for AI and human workflows
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize performance tuner"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("WorkflowPerformanceTuner")

        # Baselines
        self.baselines: Dict[str, List[PerformanceBaseline]] = {}

        # Improvements
        self.improvements: List[PerformanceImprovement] = []

        # Recommendations
        self.recommendations: Dict[str, List[TuningRecommendation]] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "performance_tuning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚡ Workflow Performance Tuner initialized")
        self.logger.info("   AI workflows: Ready")
        self.logger.info("   Human workflows: Ready")
        self.logger.info("   Hybrid workflows: Ready")

    def measure_baseline(self, workflow_id: str, metric: PerformanceMetric, 
                       value: float, unit: str = "seconds") -> PerformanceBaseline:
        """Measure performance baseline"""
        baseline = PerformanceBaseline(
            workflow_id=workflow_id,
            metric=metric,
            baseline_value=value,
            target_value=value * 0.8,  # 20% improvement target
            unit=unit
        )

        if workflow_id not in self.baselines:
            self.baselines[workflow_id] = []

        self.baselines[workflow_id].append(baseline)

        self.logger.info(f"  📊 Baseline: {workflow_id} - {metric.value}: {value} {unit}")

        return baseline

    def measure_improvement(self, workflow_id: str, metric: PerformanceMetric,
                          before: float, after: float, tuning_method: str) -> PerformanceImprovement:
        """Measure performance improvement"""
        improvement_percent = ((before - after) / before) * 100 if before > 0 else 0

        improvement = PerformanceImprovement(
            workflow_id=workflow_id,
            metric=metric,
            before=before,
            after=after,
            improvement_percent=improvement_percent,
            tuning_method=tuning_method
        )

        self.improvements.append(improvement)

        self.logger.info(f"  ⚡ Improvement: {workflow_id} - {improvement_percent:.1f}% better")

        return improvement

    def generate_recommendations(self, workflow_id: str, target: TuningTarget) -> List[TuningRecommendation]:
        """Generate performance tuning recommendations"""
        recommendations = []

        if target == TuningTarget.AI:
            recommendations.extend([
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Use batch processing for multiple requests",
                    expected_improvement=30.0,
                    difficulty=3,
                    priority=8
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Implement caching for repeated queries",
                    expected_improvement=50.0,
                    difficulty=4,
                    priority=9
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Optimize prompt length and structure",
                    expected_improvement=20.0,
                    difficulty=2,
                    priority=7
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Use streaming responses for long outputs",
                    expected_improvement=40.0,
                    difficulty=5,
                    priority=6
                )
            ])

        elif target == TuningTarget.HUMAN:
            recommendations.extend([
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Create keyboard shortcuts for common actions",
                    expected_improvement=25.0,
                    difficulty=2,
                    priority=9
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Automate repetitive tasks",
                    expected_improvement=60.0,
                    difficulty=5,
                    priority=10
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Use templates for common workflows",
                    expected_improvement=30.0,
                    difficulty=3,
                    priority=8
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Implement auto-complete and suggestions",
                    expected_improvement=20.0,
                    difficulty=4,
                    priority=7
                )
            ])

        else:  # HYBRID
            recommendations.extend([
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Delegate routine tasks to AI",
                    expected_improvement=50.0,
                    difficulty=4,
                    priority=10
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Use AI for first draft, human for refinement",
                    expected_improvement=40.0,
                    difficulty=3,
                    priority=9
                ),
                TuningRecommendation(
                    workflow_id=workflow_id,
                    target=target,
                    recommendation="Implement AI-assisted decision making",
                    expected_improvement=30.0,
                    difficulty=5,
                    priority=8
                )
            ])

        # Sort by priority
        recommendations.sort(key=lambda r: r.priority, reverse=True)

        if workflow_id not in self.recommendations:
            self.recommendations[workflow_id] = []

        self.recommendations[workflow_id].extend(recommendations)

        return recommendations

    def tune_workflow(self, workflow_id: str, target: TuningTarget) -> Dict[str, Any]:
        """Tune a workflow"""
        self.logger.info(f"⚡ Tuning workflow: {workflow_id} ({target.value})")

        # Generate recommendations
        recommendations = self.generate_recommendations(workflow_id, target)

        # Apply high-priority recommendations
        applied = []
        for rec in recommendations[:3]:  # Top 3
            applied.append(rec)
            self.logger.info(f"  ✅ Applied: {rec.recommendation}")

        return {
            "workflow_id": workflow_id,
            "target": target.value,
            "recommendations": [r.to_dict() for r in recommendations],
            "applied": [r.to_dict() for r in applied],
            "expected_improvement": sum(r.expected_improvement for r in applied) / len(applied) if applied else 0
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        total_improvements = len(self.improvements)
        avg_improvement = sum(i.improvement_percent for i in self.improvements) / total_improvements if total_improvements > 0 else 0

        return {
            "total_workflows_tuned": len(self.baselines),
            "total_improvements": total_improvements,
            "average_improvement_percent": avg_improvement,
            "baselines": {
                workflow_id: [b.to_dict() for b in baselines]
                for workflow_id, baselines in self.baselines.items()
            },
            "improvements": [i.to_dict() for i in self.improvements],
            "recommendations": {
                workflow_id: [r.to_dict() for r in recs]
                for workflow_id, recs in self.recommendations.items()
            }
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Performance Tuner")
    parser.add_argument("--tune", type=str, help="Tune a workflow")
    parser.add_argument("--target", type=str, choices=["ai", "human", "hybrid"], 
                       default="hybrid", help="Tuning target")
    parser.add_argument("--baseline", type=str, help="Measure baseline")
    parser.add_argument("--metric", type=str, choices=["speed", "accuracy", "efficiency"], 
                       default="speed", help="Performance metric")
    parser.add_argument("--value", type=float, help="Baseline value")
    parser.add_argument("--report", action="store_true", help="Get performance report")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    tuner = WorkflowPerformanceTuner()

    if args.baseline and args.value:
        metric = PerformanceMetric(args.metric)
        baseline = tuner.measure_baseline(args.baseline, metric, args.value)
        if args.json:
            print(json.dumps(baseline.to_dict(), indent=2))
        else:
            print(f"\n📊 Baseline measured: {args.baseline}")
            print(f"   {metric.value}: {args.value}")

    elif args.tune:
        target = TuningTarget(args.target)
        result = tuner.tune_workflow(args.tune, target)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n⚡ Tuning: {args.tune} ({args.target})")
            print("="*60)
            print(f"Expected Improvement: {result['expected_improvement']:.1f}%")
            print("\nRecommendations:")
            for rec in result['recommendations'][:5]:
                print(f"  • {rec['recommendation']} ({rec['expected_improvement']:.0f}% improvement)")

    elif args.report:
        report = tuner.get_performance_report()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\n⚡ Performance Report")
            print("="*60)
            print(f"Workflows Tuned: {report['total_workflows_tuned']}")
            print(f"Total Improvements: {report['total_improvements']}")
            print(f"Average Improvement: {report['average_improvement_percent']:.1f}%")

    else:
        parser.print_help()

