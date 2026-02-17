#!/usr/bin/env python3
"""
🎯 **Lumina Jarvis Capability Router**

Routes tasks and requests to the optimal coding assistant or extension
based on capabilities, performance metrics, and contextual requirements.
Implements intelligent load balancing and failover mechanisms.

@V3_WORKFLOWED: True
@TEST_FIRST: True
@OPTIMAL_ROUTING: Enabled
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics

# Local imports
script_dir = Path(__file__).parent.parent.parent.parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("JarvisCapabilityRouter")


@dataclass
class CapabilityScore:
    """Scoring for a capability on an extension"""
    extension_name: str
    capability: str
    base_score: float = 0.0  # 0.0-1.0
    performance_score: float = 0.0  # Based on metrics
    context_relevance: float = 0.0  # Based on request context
    load_factor: float = 0.0  # Current load (lower is better)
    final_score: float = 0.0


@dataclass
class ExtensionMetrics:
    """Performance metrics for an extension"""
    extension_name: str
    total_requests: int = 0
    successful_requests: int = 0
    average_latency: float = 0.0
    average_quality: float = 0.0
    error_rate: float = 0.0
    last_used: Optional[datetime] = None
    consecutive_failures: int = 0
    current_load: int = 0  # Active requests


@dataclass
class RoutingDecision:
    """Decision made by the capability router"""
    capability: str
    selected_extension: str
    confidence_score: float
    reasoning: str
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    routing_metadata: Dict[str, Any] = field(default_factory=dict)


class JarvisCapabilityRouter:
    """
    Intelligent capability router for Jarvis extensions.

    Routes requests to the optimal extension based on:
    - Capability matching
    - Performance metrics
    - Context relevance
    - Load balancing
    - Failover support
    """

    def __init__(self):
        self.capabilities_map: Dict[str, List[str]] = {}  # capability -> [extension_names]
        self.extension_metrics: Dict[str, ExtensionMetrics] = {}
        self.routing_history: List[RoutingDecision] = []
        self.max_history_size = 1000

        # Routing weights (loaded from config or defaults)
        self.weights = self._load_weights()

        # Base capability scores per extension (loaded from config or defaults)
        self._base_scores = self._load_base_scores()

        # Circuit breaker settings
        self.circuit_breaker_threshold = 3  # Consecutive failures
        self.circuit_breaker_timeout = 300  # 5 minutes

        logger.info("✅ Jarvis Capability Router initialized")

    async def register_extension(self, extension_name: str, extension_info: Any):
        """Register an extension with the capability router"""
        # Initialize metrics for this extension
        self.extension_metrics[extension_name] = ExtensionMetrics(extension_name=extension_name)

        # Update capabilities map
        for capability in extension_info.capabilities:
            if capability not in self.capabilities_map:
                self.capabilities_map[capability] = []
            if extension_name not in self.capabilities_map[capability]:
                self.capabilities_map[capability].append(extension_name)

        logger.info(f"   📝 Registered extension {extension_name} with {len(extension_info.capabilities)} capabilities")

    async def find_optimal_extension(self, capability: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Find the optimal extension for a given capability and context

        Args:
            capability: The capability needed
            context: Request context (language, complexity, user preferences, etc.)

        Returns:
            Name of the optimal extension, or None if none available
        """

        if capability not in self.capabilities_map:
            logger.debug(f"   No extensions available for capability: {capability}")
            return None

        available_extensions = self.capabilities_map[capability]
        if not available_extensions:
            return None

        # Score each available extension
        scores = []
        for ext_name in available_extensions:
            score = await self._score_extension(ext_name, capability, context)
            scores.append(score)

        # Sort by final score (descending)
        scores.sort(key=lambda s: s.final_score, reverse=True)

        # Apply circuit breaker (skip extensions with too many failures)
        best_extension = None
        for score in scores:
            if not self._is_circuit_breaker_tripped(score.extension_name):
                best_extension = score.extension_name
                break

        if best_extension:
            # Record routing decision
            alternatives = [(s.extension_name, s.final_score) for s in scores[1:3]]  # Top 3 alternatives
            decision = RoutingDecision(
                capability=capability,
                selected_extension=best_extension,
                confidence_score=scores[0].final_score,
                reasoning=self._generate_reasoning(scores[0], context),
                alternatives=alternatives,
                routing_metadata={
                    'total_candidates': len(scores),
                    'context_factors': list(context.keys()),
                    'timestamp': datetime.now().isoformat()
                }
            )
            self.routing_history.append(decision)

            # Keep history size manageable
            if len(self.routing_history) > self.max_history_size:
                self.routing_history = self.routing_history[-self.max_history_size:]

            logger.debug(f"   🎯 Routed {capability} to {best_extension} (score: {scores[0].final_score:.3f})")
        else:
            logger.warning(f"   ⚠️  No available extensions for {capability} (all circuit breakers tripped)")

        return best_extension

    async def _score_extension(self, extension_name: str, capability: str,
                             context: Dict[str, Any]) -> CapabilityScore:
        """Score an extension for a specific capability and context"""

        score = CapabilityScore(extension_name, capability)

        # Base capability score (0.0-1.0)
        score.base_score = self._calculate_base_score(extension_name, capability)

        # Performance score based on metrics
        score.performance_score = self._calculate_performance_score(extension_name)

        # Context relevance score
        score.context_relevance = self._calculate_context_relevance(extension_name, capability, context)

        # Load factor (lower is better, so we invert it)
        score.load_factor = 1.0 - min(1.0, self.extension_metrics[extension_name].current_load / 10.0)

        # Calculate final weighted score
        score.final_score = (
            self.weights['base_score'] * score.base_score +
            self.weights['performance_score'] * score.performance_score +
            self.weights['context_relevance'] * score.context_relevance +
            self.weights['load_factor'] * score.load_factor
        )

        return score

    def _load_weights(self) -> Dict[str, float]:
        """Load routing weights from config file or return defaults."""
        config_path = script_dir / "config" / "capability_router_config.json"
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text())
                if "weights" in data:
                    return data["weights"]
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load router weights: {e}")

        return {
            'base_score': 0.3,
            'performance_score': 0.3,
            'context_relevance': 0.2,
            'load_factor': 0.2,
        }

    def _load_base_scores(self) -> Dict[str, Dict[str, float]]:
        """Load base capability scores from config file or return defaults."""
        config_path = script_dir / "config" / "capability_router_config.json"
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text())
                if "base_scores" in data:
                    return data["base_scores"]
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load base scores: {e}")

        return {
            'kilo_code': {'code_completion': 0.9, 'code_generation': 0.8},
            'rue_code': {'code_review': 0.95, 'security_analysis': 0.9},
            'klein_code': {'refactoring': 0.85, 'optimization': 0.8},
            'creator_1_code': {'code_generation': 0.9, 'scaffolding': 0.95},
            'cursor_ide': {'voice_integration': 0.95, 'real_time_editing': 0.9},
            'github_copilot': {'code_completion': 0.85, 'suggestions': 0.8},
        }

    def _save_config(self):
        """Persist current weights and base scores to config file."""
        config_path = script_dir / "config" / "capability_router_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "weights": self.weights,
            "base_scores": self._base_scores,
            "updated": datetime.now().isoformat(),
        }
        config_path.write_text(json.dumps(data, indent=2))

    def _calculate_base_score(self, extension_name: str, capability: str) -> float:
        """Calculate base capability score from loaded config."""
        return self._base_scores.get(extension_name, {}).get(capability, 0.7)

    def _calculate_performance_score(self, extension_name: str) -> float:
        """Calculate performance score based on metrics"""
        if extension_name not in self.extension_metrics:
            return 0.5

        metrics = self.extension_metrics[extension_name]

        if metrics.total_requests == 0:
            return 0.5  # Neutral score for new extensions

        # Performance factors
        success_rate = metrics.successful_requests / metrics.total_requests
        quality_score = metrics.average_quality
        latency_penalty = max(0, (metrics.average_latency - 1000) / 1000)  # Penalize >1s latency

        # Combine factors
        performance_score = (
            0.4 * success_rate +
            0.4 * quality_score +
            0.2 * (1.0 - min(1.0, latency_penalty))
        )

        return max(0.0, min(1.0, performance_score))

    def _calculate_context_relevance(self, extension_name: str, capability: str,
                                   context: Dict[str, Any]) -> float:
        """Calculate how relevant this extension is for the given context"""

        relevance_score = 0.5  # Base relevance

        # Language matching
        if 'language' in context:
            language = context['language'].lower()
            if extension_name == 'kilo_code' and language == 'python':
                relevance_score += 0.2
            elif extension_name == 'rue_code' and language in ['javascript', 'typescript']:
                relevance_score += 0.2

        # Complexity matching
        if 'complexity' in context:
            complexity = context['complexity']
            if extension_name == 'klein_code' and complexity == 'high':
                relevance_score += 0.15

        # User preferences
        if 'preferred_extensions' in context:
            if extension_name in context['preferred_extensions']:
                relevance_score += 0.3

        # Task type matching
        if 'task_type' in context:
            task_type = context['task_type']
            if extension_name == 'creator_1_code' and task_type == 'generation':
                relevance_score += 0.25

        return max(0.0, min(1.0, relevance_score))

    def _is_circuit_breaker_tripped(self, extension_name: str) -> bool:
        """Check if circuit breaker is tripped for an extension"""
        if extension_name not in self.extension_metrics:
            return False

        metrics = self.extension_metrics[extension_name]

        if metrics.consecutive_failures >= self.circuit_breaker_threshold:
            # Check if timeout has passed
            if metrics.last_used:
                time_since_last_failure = (datetime.now() - metrics.last_used).total_seconds()
                if time_since_last_failure < self.circuit_breaker_timeout:
                    return True  # Still tripped
                else:
                    # Reset circuit breaker
                    metrics.consecutive_failures = 0
                    return False
            return True  # No last_used time, assume still tripped

        return False

    def _generate_reasoning(self, best_score: CapabilityScore, context: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for routing decision"""

        reasons = []

        if best_score.base_score > 0.8:
            reasons.append(f"excellent base capability ({best_score.base_score:.2f})")
        elif best_score.base_score > 0.6:
            reasons.append(f"good base capability ({best_score.base_score:.2f})")

        if best_score.performance_score > 0.8:
            reasons.append(f"proven performance track record")
        elif best_score.performance_score < 0.4:
            reasons.append(f"needs performance monitoring")

        if best_score.context_relevance > 0.7:
            reasons.append(f"highly relevant for this context")
        elif best_score.context_relevance > 0.4:
            reasons.append(f"moderately relevant for this context")

        if best_score.load_factor > 0.8:
            reasons.append(f"low current load")
        elif best_score.load_factor < 0.3:
            reasons.append(f"high current load (but still optimal)")

        reasoning = f"Selected {best_score.extension_name} for {best_score.capability} because: " + ", ".join(reasons)

        if context:
            context_factors = []
            if 'language' in context:
                context_factors.append(f"language: {context['language']}")
            if 'complexity' in context:
                context_factors.append(f"complexity: {context['complexity']}")

            if context_factors:
                reasoning += f". Context factors: {', '.join(context_factors)}"

        return reasoning

    def record_request_result(self, extension_name: str, success: bool,
                            quality_score: float = 0.0, latency_ms: float = 0.0):
        """Record the result of a request for performance tracking"""

        if extension_name not in self.extension_metrics:
            self.extension_metrics[extension_name] = ExtensionMetrics(extension_name)

        metrics = self.extension_metrics[extension_name]

        # Update counters
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
            metrics.consecutive_failures = 0
        else:
            metrics.consecutive_failures += 1

        metrics.last_used = datetime.now()

        # Update averages
        if quality_score > 0:
            metrics.average_quality = (
                (metrics.average_quality * (metrics.total_requests - 1)) +
                quality_score
            ) / metrics.total_requests

        if latency_ms > 0:
            metrics.average_latency = (
                (metrics.average_latency * (metrics.total_requests - 1)) +
                latency_ms
            ) / metrics.total_requests

        # Update error rate
        if metrics.total_requests > 0:
            metrics.error_rate = (metrics.total_requests - metrics.successful_requests) / metrics.total_requests

        # Update load (decrement after completion)
        metrics.current_load = max(0, metrics.current_load - 1)

    def increment_load(self, extension_name: str):
        """Increment load counter when starting a request"""
        if extension_name in self.extension_metrics:
            self.extension_metrics[extension_name].current_load += 1

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics"""

        total_decisions = len(self.routing_history)
        if total_decisions == 0:
            return {'total_decisions': 0, 'message': 'No routing history available'}

        # Analyze recent decisions (last 100)
        recent_decisions = self.routing_history[-100:]

        # Capability distribution
        capability_counts = {}
        for decision in recent_decisions:
            capability_counts[decision.capability] = capability_counts.get(decision.capability, 0) + 1

        # Extension usage
        extension_usage = {}
        for decision in recent_decisions:
            extension_usage[decision.selected_extension] = extension_usage.get(decision.selected_extension, 0) + 1

        # Confidence distribution
        confidence_scores = [d.confidence_score for d in recent_decisions]
        confidence_stats = {
            'mean': statistics.mean(confidence_scores),
            'median': statistics.median(confidence_scores),
            'min': min(confidence_scores),
            'max': max(confidence_scores)
        }

        return {
            'total_decisions': total_decisions,
            'recent_decisions_analyzed': len(recent_decisions),
            'capability_distribution': capability_counts,
            'extension_usage': extension_usage,
            'confidence_statistics': confidence_stats,
            'circuit_breaker_status': {
                ext_name: self._is_circuit_breaker_tripped(ext_name)
                for ext_name in self.extension_metrics.keys()
            }
        }

    def optimize_weights(self):
        """Optimize routing weights based on historical performance.

        Analyzes routing history to find which weight dimensions correlate
        with successful, high-quality outcomes and adjusts weights accordingly.
        """
        if len(self.routing_history) < 20:
            logger.info("   Not enough routing history for optimization (need 20+)")
            return

        # Analyze which extensions performed well recently
        recent = self.routing_history[-100:]
        good_decisions = []
        poor_decisions = []

        for decision in recent:
            ext = decision.selected_extension
            if ext in self.extension_metrics:
                metrics = self.extension_metrics[ext]
                if metrics.total_requests > 0:
                    success_rate = metrics.successful_requests / metrics.total_requests
                    if success_rate >= 0.8 and metrics.average_quality >= 0.7:
                        good_decisions.append(decision)
                    elif success_rate < 0.5 or metrics.average_quality < 0.4:
                        poor_decisions.append(decision)

        if not good_decisions:
            logger.info("   No high-performing decisions to learn from")
            return

        # Increase weight for dimensions that distinguish good from poor
        good_avg_conf = statistics.mean(d.confidence_score for d in good_decisions)
        if poor_decisions:
            poor_avg_conf = statistics.mean(d.confidence_score for d in poor_decisions)
            # If performance score is the differentiator, boost it
            if good_avg_conf > poor_avg_conf + 0.1:
                self.weights['performance_score'] = min(0.5, self.weights['performance_score'] + 0.02)
                self.weights['base_score'] = max(0.15, self.weights['base_score'] - 0.01)
                self.weights['context_relevance'] = max(0.1, self.weights['context_relevance'] - 0.005)
                self.weights['load_factor'] = max(0.1, self.weights['load_factor'] - 0.005)

        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

        self._save_config()
        logger.info(
            f"   Weights optimized: base={self.weights['base_score']:.3f} "
            f"perf={self.weights['performance_score']:.3f} "
            f"ctx={self.weights['context_relevance']:.3f} "
            f"load={self.weights['load_factor']:.3f}"
        )

    def export_routing_data(self) -> Dict[str, Any]:
        """Export routing data for analysis"""
        return {
            'routing_history': [
                {
                    'capability': d.capability,
                    'selected_extension': d.selected_extension,
                    'confidence_score': d.confidence_score,
                    'reasoning': d.reasoning,
                    'alternatives': d.alternatives,
                    'metadata': d.routing_metadata
                }
                for d in self.routing_history[-100:]  # Last 100 decisions
            ],
            'extension_metrics': {
                name: {
                    'total_requests': m.total_requests,
                    'successful_requests': m.successful_requests,
                    'average_latency': m.average_latency,
                    'average_quality': m.average_quality,
                    'error_rate': m.error_rate,
                    'current_load': m.current_load
                }
                for name, m in self.extension_metrics.items()
            },
            'capabilities_map': self.capabilities_map,
            'export_timestamp': datetime.now().isoformat()
        }


# Global instance
_capability_router = None


def get_capability_router() -> JarvisCapabilityRouter:
    """Get or create capability router instance"""
    global _capability_router
    if _capability_router is None:
        _capability_router = JarvisCapabilityRouter()
    return _capability_router


if __name__ == "__main__":
    # Test the capability router
    import asyncio

    async def test():
        print("🎯 **Jarvis Capability Router Test**")
        print("=" * 50)

        router = get_capability_router()

        # Simulate some test data
        print("\n🧪 Testing Routing Logic...")

        # Test cases
        test_cases = [
            {
                'capability': 'code_completion',
                'context': {'language': 'python', 'complexity': 'medium'}
            },
            {
                'capability': 'code_review',
                'context': {'language': 'javascript', 'focus': 'security'}
            },
            {
                'capability': 'refactoring',
                'context': {'language': 'python', 'complexity': 'high'}
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['capability']}")
            print(f"   Context: {test_case['context']}")

            extension = await router.find_optimal_extension(
                test_case['capability'],
                test_case['context']
            )

            if extension:
                print(f"   ✅ Routed to: {extension}")
            else:
                print("   ❌ No extension available")

        # Show statistics
        stats = router.get_routing_statistics()
        print("\n📊 Routing Statistics:")
        print(f"   Total Decisions: {stats['total_decisions']}")

        if stats['total_decisions'] > 0:
            print(f"   Confidence - Mean: {stats['confidence_statistics']['mean']:.3f}")
            print(f"   Confidence - Range: {stats['confidence_statistics']['min']:.3f} - {stats['confidence_statistics']['max']:.3f}")

    asyncio.run(test())