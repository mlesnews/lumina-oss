#!/usr/bin/env python3
"""
IDE Workflow Optimizer
@MARVIN @OP @ADM @PEAK

Optimizes IDE analyst/engineer workflows for peak @ask per second rate and flow.
Tracks metrics, identifies bottlenecks, and provides optimization recommendations.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import deque
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [IDEWorkflow] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class WorkflowPhase(Enum):
    """Workflow phases for rate tracking"""
    ANALYSIS = "analysis"
    QUESTION = "question"  # @ask mode
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    WAITING = "waiting"


@dataclass
class AskMetric:
    """Metrics for @ask rate tracking"""
    timestamp: datetime
    question_id: str
    question_length: int
    response_time: float
    phase: WorkflowPhase
    mode: str  # agent, plan, debug, ask
    context_size: int = 0
    tokens_used: int = 0


@dataclass
class WorkflowMetrics:
    """Workflow performance metrics"""
    asks_per_second: float = 0.0
    total_asks: int = 0
    avg_response_time: float = 0.0
    peak_ask_rate: float = 0.0
    flow_efficiency: float = 0.0  # 0-1 scale
    bottleneck_phases: List[str] = field(default_factory=list)
    optimization_score: float = 0.0  # 0-100


@dataclass
class FlowOptimization:
    """Flow optimization recommendations"""
    phase: WorkflowPhase
    current_rate: float
    target_rate: float
    optimization_actions: List[str]
    expected_improvement: float


class IDEWorkflowOptimizer:
    """
    IDE Workflow Optimizer for @peak @ask per second rate optimization.

    Tracks:
    - Ask rate (questions per second)
    - Response times
    - Workflow phases
    - Bottlenecks
    - Flow efficiency
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.data_dir = self.project_root / "data" / "ide_workflow_metrics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Metrics storage
        self.ask_metrics: deque = deque(maxlen=10000)  # Last 10k asks
        self.workflow_phases: deque = deque(maxlen=1000)

        # Configuration
        self.config_path = self.project_root / "config" / "ide_workflow_optimization.json"
        self.config = self._load_config()

        # Performance targets
        self.target_ask_rate = self.config.get("target_ask_rate_per_second", 5.0)
        self.target_response_time = self.config.get("target_response_time_ms", 2000.0)
        self.peak_mode_threshold = self.config.get("peak_mode_threshold", 3.0)

        logger.info("✅ IDE Workflow Optimizer initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load optimization configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        # Default configuration
        return {
            "target_ask_rate_per_second": 5.0,
            "target_response_time_ms": 2000.0,
            "peak_mode_threshold": 3.0,
            "flow_window_seconds": 60,
            "bottleneck_threshold": 1.0,  # seconds
            "optimization_modes": {
                "peak": {
                    "enabled": True,
                    "target_rate": 5.0,
                    "flow_priority": "throughput"
                },
                "balanced": {
                    "enabled": True,
                    "target_rate": 3.0,
                    "flow_priority": "quality"
                }
            }
        }

    def record_ask(
        self,
        question_id: str,
        question_length: int,
        response_time: float,
        mode: str = "ask",
        context_size: int = 0,
        tokens_used: int = 0
    ):
        """
        Record an @ask interaction for rate tracking.

        Args:
            question_id: Unique identifier for the question
            question_length: Length of question in characters
            response_time: Response time in seconds
            mode: Mode used (agent, plan, debug, ask)
            context_size: Size of context used
            tokens_used: Number of tokens used
        """
        metric = AskMetric(
            timestamp=datetime.now(),
            question_id=question_id,
            question_length=question_length,
            response_time=response_time,
            phase=WorkflowPhase.QUESTION,
            mode=mode,
            context_size=context_size,
            tokens_used=tokens_used
        )

        self.ask_metrics.append(metric)
        logger.debug(f"Recorded ask: {question_id}, response_time: {response_time:.2f}s")

    def calculate_ask_rate(self, window_seconds: int = 60) -> float:
        """
        Calculate current ask rate (questions per second) over time window.

        Args:
            window_seconds: Time window in seconds

        Returns:
            Ask rate (questions per second)
        """
        if not self.ask_metrics:
            return 0.0

        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        recent_asks = [
            m for m in self.ask_metrics
            if m.timestamp >= cutoff_time
        ]

        if not recent_asks:
            return 0.0

        time_span = (recent_asks[-1].timestamp - recent_asks[0].timestamp).total_seconds()
        if time_span == 0:
            time_span = window_seconds

        rate = len(recent_asks) / time_span
        return rate

    def calculate_peak_ask_rate(self) -> float:
        """Calculate peak ask rate from history"""
        if not self.ask_metrics:
            return 0.0

        # Calculate rates in 10-second windows
        window_seconds = 10
        rates = []

        for i in range(len(self.ask_metrics) - 1):
            window_start = self.ask_metrics[i].timestamp
            window_end = window_start + timedelta(seconds=window_seconds)

            window_asks = [
                m for m in self.ask_metrics
                if window_start <= m.timestamp <= window_end
            ]

            if window_asks:
                time_span = (window_asks[-1].timestamp - window_asks[0].timestamp).total_seconds()
                if time_span > 0:
                    rate = len(window_asks) / time_span
                    rates.append(rate)

        return max(rates) if rates else 0.0

    def calculate_flow_efficiency(self) -> float:
        """
        Calculate workflow flow efficiency (0-1 scale).

        Factors:
        - Ask rate vs target
        - Response times vs target
        - Consistency (low variance)
        - Bottleneck absence
        """
        if not self.ask_metrics:
            return 0.0

        # Get recent metrics (last 5 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_metrics = [
            m for m in self.ask_metrics
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return 0.0

        # Factor 1: Ask rate efficiency
        current_rate = self.calculate_ask_rate(60)
        rate_efficiency = min(current_rate / self.target_ask_rate, 1.0)

        # Factor 2: Response time efficiency
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        response_efficiency = max(0, 1.0 - (avg_response_time / (self.target_response_time / 1000.0)))

        # Factor 3: Consistency (inverse of variance)
        response_times = [m.response_time for m in recent_metrics]
        if len(response_times) > 1:
            mean_rt = sum(response_times) / len(response_times)
            variance = sum((rt - mean_rt) ** 2 for rt in response_times) / len(response_times)
            std_dev = variance ** 0.5
            consistency = max(0, 1.0 - (std_dev / mean_rt)) if mean_rt > 0 else 0.0
        else:
            consistency = 1.0

        # Combined efficiency (weighted average)
        efficiency = (
            rate_efficiency * 0.4 +
            response_efficiency * 0.4 +
            consistency * 0.2
        )

        return efficiency

    def identify_bottlenecks(self) -> List[str]:
        """Identify workflow bottlenecks"""
        bottlenecks = []

        if not self.ask_metrics:
            return bottlenecks

        # Get recent metrics
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_metrics = [
            m for m in self.ask_metrics
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return bottlenecks

        # Check response time bottleneck
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        if avg_response_time > (self.target_response_time / 1000.0):
            bottlenecks.append(f"High response time: {avg_response_time:.2f}s (target: {self.target_response_time/1000.0:.2f}s)")

        # Check rate bottleneck
        current_rate = self.calculate_ask_rate(60)
        if current_rate < self.target_ask_rate * 0.5:  # Less than 50% of target
            bottlenecks.append(f"Low ask rate: {current_rate:.2f}/s (target: {self.target_ask_rate}/s)")

        # Check mode efficiency
        mode_counts = {}
        for m in recent_metrics:
            mode_counts[m.mode] = mode_counts.get(m.mode, 0) + 1

        # If using inefficient modes, flag it
        inefficient_modes = ["debug", "plan"]  # These are slower
        for mode in inefficient_modes:
            if mode_counts.get(mode, 0) > len(recent_metrics) * 0.3:  # >30% usage
                bottlenecks.append(f"High usage of slow mode: {mode}")

        return bottlenecks

    def get_workflow_metrics(self) -> WorkflowMetrics:
        """Get comprehensive workflow metrics"""
        current_rate = self.calculate_ask_rate(60)
        peak_rate = self.calculate_peak_ask_rate()
        flow_efficiency = self.calculate_flow_efficiency()
        bottlenecks = self.identify_bottlenecks()

        # Calculate average response time
        if self.ask_metrics:
            recent_metrics = list(self.ask_metrics)[-100:]  # Last 100
            avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        else:
            avg_response_time = 0.0

        # Optimization score (0-100)
        optimization_score = (
            (current_rate / self.target_ask_rate) * 40 +
            flow_efficiency * 40 +
            (1.0 - len(bottlenecks) / 5.0) * 20  # Fewer bottlenecks = better
        )
        optimization_score = max(0, min(100, optimization_score))

        return WorkflowMetrics(
            asks_per_second=current_rate,
            total_asks=len(self.ask_metrics),
            avg_response_time=avg_response_time,
            peak_ask_rate=peak_rate,
            flow_efficiency=flow_efficiency,
            bottleneck_phases=bottlenecks,
            optimization_score=optimization_score
        )

    def generate_optimization_recommendations(self) -> List[FlowOptimization]:
        """Generate flow optimization recommendations"""
        recommendations = []
        metrics = self.get_workflow_metrics()

        # Rate optimization
        if metrics.asks_per_second < self.target_ask_rate:
            improvement = self.target_ask_rate - metrics.asks_per_second
            recommendations.append(FlowOptimization(
                phase=WorkflowPhase.QUESTION,
                current_rate=metrics.asks_per_second,
                target_rate=self.target_ask_rate,
                optimization_actions=[
                    "Batch related questions together",
                    "Use @ask mode for quick queries",
                    "Pre-load context to reduce setup time",
                    "Cache common question patterns",
                    "Reduce context size for faster responses"
                ],
                expected_improvement=improvement
            ))

        # Response time optimization
        if metrics.avg_response_time > (self.target_response_time / 1000.0):
            recommendations.append(FlowOptimization(
                phase=WorkflowPhase.QUESTION,
                current_rate=metrics.avg_response_time,
                target_rate=self.target_response_time / 1000.0,
                optimization_actions=[
                    "Use lighter models for simple questions",
                    "Reduce context window size",
                    "Enable response caching",
                    "Use streaming responses",
                    "Optimize prompt length"
                ],
                expected_improvement=metrics.avg_response_time - (self.target_response_time / 1000.0)
            ))

        return recommendations

    def optimize_for_peak_flow(self) -> Dict[str, Any]:
        """
        Optimize workflow for @peak @ask per second rate.

        Returns:
            Optimization results with recommendations
        """
        metrics = self.get_workflow_metrics()
        recommendations = self.generate_optimization_recommendations()

        # Determine if we're in peak mode
        is_peak_mode = metrics.asks_per_second >= self.peak_mode_threshold

        return {
            "current_metrics": asdict(metrics),
            "is_peak_mode": is_peak_mode,
            "recommendations": [asdict(r) for r in recommendations],
            "optimization_actions": self._generate_action_plan(recommendations),
            "target_rate": self.target_ask_rate,
            "current_rate": metrics.asks_per_second,
            "rate_efficiency": metrics.asks_per_second / self.target_ask_rate if self.target_ask_rate > 0 else 0.0
        }

    def _generate_action_plan(self, recommendations: List[FlowOptimization]) -> List[str]:
        """Generate actionable optimization plan"""
        actions = []

        for rec in recommendations:
            if rec.current_rate < rec.target_rate:
                # Prioritize actions by expected improvement
                top_actions = rec.optimization_actions[:3]  # Top 3 actions
                actions.extend(top_actions)

        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)

        return unique_actions

    def save_metrics(self):
        """Save metrics to disk"""
        metrics_file = self.data_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"

        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": asdict(self.get_workflow_metrics()),
            "ask_count": len(self.ask_metrics)
        }

        try:
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            logger.info(f"Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="IDE Workflow Optimizer")
    parser.add_argument("--metrics", action="store_true", help="Show current metrics")
    parser.add_argument("--optimize", action="store_true", help="Optimize for peak flow")
    parser.add_argument("--rate", action="store_true", help="Show current ask rate")
    parser.add_argument("--recommendations", action="store_true", help="Show optimization recommendations")
    parser.add_argument("--record", type=str, help="Record an ask (JSON format)")
    parser.add_argument("--save", action="store_true", help="Save metrics to disk")

    args = parser.parse_args()

    optimizer = IDEWorkflowOptimizer()

    if args.record:
        try:
            data = json.loads(args.record)
            optimizer.record_ask(
                question_id=data.get("question_id", str(time.time())),
                question_length=data.get("question_length", 0),
                response_time=data.get("response_time", 0.0),
                mode=data.get("mode", "ask"),
                context_size=data.get("context_size", 0),
                tokens_used=data.get("tokens_used", 0)
            )
            print("✅ Ask recorded")
        except Exception as e:
            print(f"❌ Failed to record: {e}")

    if args.rate:
        rate = optimizer.calculate_ask_rate(60)
        print(f"Current ask rate: {rate:.2f} questions/second")
        print(f"Target rate: {optimizer.target_ask_rate} questions/second")
        print(f"Efficiency: {(rate / optimizer.target_ask_rate * 100):.1f}%")

    if args.metrics:
        metrics = optimizer.get_workflow_metrics()
        print(json.dumps(asdict(metrics), indent=2, default=str))

    if args.recommendations:
        recommendations = optimizer.generate_optimization_recommendations()
        for rec in recommendations:
            print(f"\nPhase: {rec.phase.value}")
            print(f"Current rate: {rec.current_rate:.2f}, Target: {rec.target_rate:.2f}")
            print("Actions:")
            for action in rec.optimization_actions:
                print(f"  - {action}")

    if args.optimize:
        result = optimizer.optimize_for_peak_flow()
        print(json.dumps(result, indent=2, default=str))

    if args.save:
        optimizer.save_metrics()
        print("✅ Metrics saved")

    if not any([args.record, args.rate, args.metrics, args.recommendations, args.optimize, args.save]):
        # Default: show optimization summary
        result = optimizer.optimize_for_peak_flow()
        print("📊 IDE Workflow Optimization Summary")
        print("=" * 60)
        print(f"Current Ask Rate: {result['current_rate']:.2f}/s")
        print(f"Target Rate: {result['target_rate']}/s")
        print(f"Rate Efficiency: {result['rate_efficiency']*100:.1f}%")
        print(f"Peak Mode: {'✅ Yes' if result['is_peak_mode'] else '❌ No'}")
        print(f"\nOptimization Score: {result['current_metrics']['optimization_score']:.1f}/100")
        print(f"Flow Efficiency: {result['current_metrics']['flow_efficiency']*100:.1f}%")

        if result['recommendations']:
            print("\n📋 Recommendations:")
            for rec in result['recommendations']:
                print(f"\n  {rec['phase']}:")
                for action in rec['optimization_actions'][:3]:
                    print(f"    - {action}")


if __name__ == "__main__":



    main()