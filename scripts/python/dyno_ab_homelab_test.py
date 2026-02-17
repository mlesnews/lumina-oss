#!/usr/bin/env python3
"""
DYNO A/B Homelab Test - Real vs Simulated

A/B testing between:
- A: Containerized inference layer with real homelab connections
- B: Animatrix-simulated homelab (full simulation)

Features:
- Progressive dynamic scaling
- Infinite bell curve progression
- Inference adjustments based on comparisons
- Real-time A/B testing

Tags: #DYNO #AB_TESTING #HOMELAB #ANIMATRIX #SIMULATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

from scripts.python.dyno_lumina_jarvis import DYNOLuminaJARVIS
from lumina.ai_connection import AIConnectionManager
from lumina.ab_testing import ABTestManager, TestGroup, TestResult
from lumina.curve_grading import ProgressiveCurveGrading
from lumina.animatrix_simulator import AnimatrixSimulator, AnimatrixStory
from lumina.dynamic_scaling import DynamicScalingModule
from scripts.python.dyno_case_based_loop import CaseBasedLoop, LoopStrategy

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DYNOABHomelabTest")


class SimulatedHomelab:
    """
    Robust & Comprehensive Simulated Homelab

    Uses RobustHomelabSimulator for realistic behavior.
    Falls back to Animatrix for story-driven responses.
    """

    def __init__(self, use_robust: bool = True):
        """
        Initialize simulated homelab.

        Args:
            use_robust: Use robust simulator (default: True)
        """
        logger.info("🎬 Initializing Robust Simulated Homelab...")

        self.use_robust = use_robust
        self.animatrix = AnimatrixSimulator()

        # Try to use robust simulator
        if use_robust:
            try:
                from lumina.robust_homelab_simulator import RobustHomelabSimulator
                self.robust_simulator = RobustHomelabSimulator()
                self.robust_simulator.start_monitoring()
                logger.info("✅ Using Robust Homelab Simulator")
            except ImportError:
                logger.warning("⚠️  Robust simulator not available, using basic")
                self.use_robust = False
                self.robust_simulator = None
        else:
            self.robust_simulator = None

        # Simulated services (for compatibility)
        self.simulated_services = {
            'ultron': {
                'url': 'http://simulated-ultron:11434',
                'available': True,
                'type': 'ollama',
                'simulated': True
            },
            'kaiju': {
                'url': 'http://simulated-kaiju:11434',
                'available': True,
                'type': 'ollama',
                'simulated': True
            },
            'nas': {
                'url': 'http://simulated-nas:5001',
                'available': True,
                'type': 'storage',
                'simulated': True
            }
        }

        logger.info("✅ Simulated Homelab initialized")

    def simulate_ai_inference(self, query: str, service: str = "ultron") -> Dict[str, Any]:
        """
        Simulate AI inference with robust behavior.

        Args:
            query: Query to simulate
            service: Service to use (ultron, kaiju)

        Returns:
            Simulated inference result
        """
        # Use robust simulator if available
        if self.use_robust and self.robust_simulator:
            result = self.robust_simulator.simulate_ai_inference(query, service)

            # Enhance with Animatrix story for richer responses
            try:
                story_result = self.animatrix.simulate_story(
                    AnimatrixStory.PROGRAM,
                    {
                        'query': query,
                        'service': service,
                        'context': 'ai_inference'
                    }
                )
                # Merge story outcome into response
                if 'response' in result and story_result.get('outcome'):
                    result['response'] = f"{result['response']}\n\n[Story Context]: {story_result.get('outcome')}"
            except Exception as e:
                logger.debug(f"Could not enhance with Animatrix: {e}")

            return result
        else:
            # Fallback to basic Animatrix simulation
            story_result = self.animatrix.simulate_story(
                AnimatrixStory.PROGRAM,
                {
                    'query': query,
                    'service': service,
                    'context': 'ai_inference'
                }
            )

            return {
                'success': True,
                'response': story_result.get('outcome', f'Simulated response for: {query}'),
                'model': f'simulated-{service}',
                'source': f'Animatrix-Simulated-{service.upper()}',
                'simulated': True,
                'story': story_result
            }

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive simulated homelab status"""
        if self.use_robust and self.robust_simulator:
            return self.robust_simulator.get_status()
        else:
            return {
                'simulated': True,
                'services': self.simulated_services,
                'available': True,
                'timestamp': datetime.now().isoformat(),
                'simulator_type': 'basic'
            }


class DYNOABHomelabTest:
    """
    DYNO A/B Homelab Test Manager with God Feedback Loop

    Manages A/B testing between real and simulated homelab.
    Includes controlled feedback loop with breakout conditions.
    """

    def __init__(
        self,
        max_iterations: int = 100,
        convergence_threshold: float = 0.05,
        significance_threshold: float = 0.1,
        min_iterations: int = 10
    ):
        """
        Initialize A/B test manager with God Feedback Loop.

        Args:
            max_iterations: Maximum iterations before forced breakout
            convergence_threshold: Score variance threshold for convergence (0.05 = 5%)
            significance_threshold: Minimum difference to consider significant (0.1 = 10%)
            min_iterations: Minimum iterations before allowing breakout
        """
        logger.info("🧪 Initializing DYNO A/B Homelab Test with God Feedback Loop...")

        # Group A: Real homelab (containerized with real connections)
        self.group_a = DYNOLuminaJARVIS()
        self.group_a_manager = AIConnectionManager()

        # Group B: Simulated homelab (Animatrix)
        self.group_b = SimulatedHomelab()

        # A/B Testing
        self.ab_manager = ABTestManager()
        self.curve_grading = ProgressiveCurveGrading()
        self.dynamic_scaling = DynamicScalingModule()

        # Case-Based Loop System
        self.case_loop = CaseBasedLoop()

        # Test configuration
        self.test_name = "dyno_homelab_real_vs_simulated"
        self.test_config = self.ab_manager.create_test(
            name=self.test_name,
            control_config={
                'type': 'real_homelab',
                'description': 'Containerized with real homelab connections',
                'dyno': self.group_a
            },
            experiment_config={
                'type': 'simulated_homelab',
                'description': 'Animatrix-simulated homelab',
                'simulated': self.group_b
            },
            sample_size=1000,
            significance_level=0.05
        )

        # God Feedback Loop parameters
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.significance_threshold = significance_threshold
        self.min_iterations = min_iterations

        # Loop state
        self.current_iteration = 0
        self.loop_active = False
        self.breakout_reason = None
        self.score_history = []  # Track scores over iterations
        self.convergence_detected = False

        logger.info("✅ DYNO A/B Homelab Test initialized")
        logger.info("   A: Real homelab (containerized)")
        logger.info("   B: Simulated homelab (Animatrix)")
        logger.info(f"   God Feedback Loop: max={max_iterations}, convergence={convergence_threshold}, significance={significance_threshold}")

    def run_comparison_test(
        self,
        query: str,
        user_id: Optional[str] = None,
        auto_assign: bool = True
    ) -> Dict[str, Any]:
        """
        Run a comparison test between A and B.

        Args:
            query: Query to test
            user_id: User ID (optional)
            auto_assign: Auto-assign to group

        Returns:
            Comparison results
        """
        logger.info(f"🧪 Running comparison test: {query[:50]}...")

        # Assign to group
        if auto_assign:
            group = self.ab_manager.assign_user(
                self.test_name,
                user_id or f"test_{datetime.now().timestamp()}"
            )
        else:
            # Run both for comparison
            group = None

        results = {}

        # Run Group A (Real)
        logger.info("🔵 Running Group A (Real Homelab)...")
        try:
            a_result = self.group_a_manager.infer(query)
            a_score = self._score_result(a_result, 'real')
            results['group_a'] = {
                'result': a_result,
                'score': a_score,
                'group': 'A',
                'type': 'real_homelab'
            }
        except Exception as e:
            logger.error(f"Group A error: {e}")
            results['group_a'] = {
                'error': str(e),
                'score': 0.0,
                'group': 'A'
            }

        # Run Group B (Simulated)
        logger.info("🟢 Running Group B (Simulated Homelab)...")
        try:
            b_result = self.group_b.simulate_ai_inference(query)
            b_score = self._score_result(b_result, 'simulated')
            results['group_b'] = {
                'result': b_result,
                'score': b_score,
                'group': 'B',
                'type': 'simulated_homelab'
            }
        except Exception as e:
            logger.error(f"Group B error: {e}")
            results['group_b'] = {
                'error': str(e),
                'score': 0.0,
                'group': 'B'
            }

        # Compare results
        comparison = self._compare_results(results['group_a'], results['group_b'])
        results['comparison'] = comparison

        # Calculate curve progression
        scores = [results['group_a']['score'], results['group_b']['score']]
        curve = self.curve_grading.calculate_curve(
            scores,
            curve_type="infinite",
            progression=True
        )
        results['curve'] = curve

        # Dynamic scaling decision
        scaling_decision = self.dynamic_scaling.make_scaling_decision(
            metrics={
                'a_score': results['group_a']['score'],
                'b_score': results['group_b']['score'],
                'difference': abs(results['group_a']['score'] - results['group_b']['score'])
            }
        )
        results['scaling'] = scaling_decision

        # Record results
        if user_id:
            self.ab_manager.record_result(
                self.test_name,
                user_id,
                group or TestGroup.CONTROL,
                query,
                results,
                results['group_a']['score'] if group == TestGroup.CONTROL else results['group_b']['score']
            )

        logger.info(f"✅ Comparison complete: A={results['group_a']['score']:.2f}, B={results['group_b']['score']:.2f}")

        return results

    def _score_result(self, result: Dict[str, Any], result_type: str) -> float:
        """Score a result (0.0 to 1.0)"""
        if 'error' in result:
            return 0.0

        score = 0.5  # Base score

        # Real homelab scoring
        if result_type == 'real':
            if result.get('success'):
                score += 0.3
            if 'response' in result and result['response']:
                score += 0.2
            if result.get('source'):
                score += 0.1

        # Simulated scoring
        elif result_type == 'simulated':
            if result.get('success'):
                score += 0.2
            if result.get('story'):
                score += 0.3
            if result.get('simulated'):
                score += 0.1

        return min(1.0, score)

    def _compare_results(self, a_result: Dict, b_result: Dict) -> Dict[str, Any]:
        """Compare A and B results"""
        a_score = a_result.get('score', 0.0)
        b_score = b_result.get('score', 0.0)

        difference = abs(a_score - b_score)
        winner = 'A' if a_score > b_score else 'B' if b_score > a_score else 'Tie'

        return {
            'a_score': a_score,
            'b_score': b_score,
            'difference': difference,
            'winner': winner,
            'significance': difference > 0.1,  # 10% threshold
            'timestamp': datetime.now().isoformat()
        }

    def get_test_statistics(self) -> Dict[str, Any]:
        """Get A/B test statistics"""
        stats = self.ab_manager.get_test_statistics(self.test_name)

        # Add curve progression
        if stats and 'results' in stats:
            scores = [r.score for r in stats['results']]
            if scores:
                curve = self.curve_grading.calculate_curve(
                    scores,
                    curve_type="infinite",
                    progression=True
                )
                stats['curve_progression'] = curve

        return stats

    def _check_breakout_conditions(self, a_score: float, b_score: float) -> tuple[bool, Optional[str]]:
        """
        Check if God Feedback Loop should break out.

        Args:
            a_score: Group A score
            b_score: Group B score

        Returns:
            (should_breakout, reason)
        """
        self.current_iteration += 1
        self.score_history.append({'a': a_score, 'b': b_score, 'iteration': self.current_iteration})

        # Condition 1: Maximum iterations reached
        if self.current_iteration >= self.max_iterations:
            return True, f"Maximum iterations reached ({self.max_iterations})"

        # Condition 2: Minimum iterations not met
        if self.current_iteration < self.min_iterations:
            return False, None

        # Condition 3: Significance threshold met
        difference = abs(a_score - b_score)
        if difference >= self.significance_threshold:
            return True, f"Significant difference detected: {difference:.2f} >= {self.significance_threshold}"

        # Condition 4: Convergence detected (scores stabilizing)
        if len(self.score_history) >= 5:
            recent_scores = self.score_history[-5:]
            a_scores = [s['a'] for s in recent_scores]
            b_scores = [s['b'] for s in recent_scores]

            # Calculate variance
            a_variance = self._calculate_variance(a_scores)
            b_variance = self._calculate_variance(b_scores)
            max_variance = max(a_variance, b_variance)

            if max_variance <= self.convergence_threshold:
                self.convergence_detected = True
                return True, f"Convergence detected: variance {max_variance:.4f} <= {self.convergence_threshold}"

        # Condition 5: Dynamic scaling recommends termination
        scaling_metrics = self.dynamic_scaling.monitor_resources()
        scaling_decision = self.dynamic_scaling.should_scale(scaling_metrics)

        # If scaling maintains and we have enough data, consider breakout
        if (scaling_decision.direction.value == 'maintain' and 
            self.current_iteration >= self.min_iterations and
            len(self.score_history) >= 3):
            # Check if recent scores are stable
            recent = self.score_history[-3:]
            if all(abs(s['a'] - recent[0]['a']) < 0.05 for s in recent):
                return True, "Stable performance with optimal scaling"

        return False, None

    def _calculate_variance(self, scores: List[float]) -> float:
        """Calculate variance of scores"""
        if not scores or len(scores) < 2:
            return 1.0  # High variance if not enough data

        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance

    def run_god_feedback_loop(
        self,
        test_queries: List[str],
        max_iterations: Optional[int] = None,
        strategy: Optional[LoopStrategy] = None
    ) -> Dict[str, Any]:
        """
        Run God Feedback Loop - controlled A/B testing with case-based breakout conditions.

        Uses case-based loop system with strategies determined by syphon and WOPR.

        Args:
            test_queries: List of queries to test
            max_iterations: Override max iterations (optional)
            strategy: Specific strategy to use (auto-select if None)

        Returns:
            Complete test results with loop information
        """
        if max_iterations:
            self.max_iterations = max_iterations

        logger.info("🔮 Starting God Feedback Loop (Case-Based)...")
        logger.info(f"   Max iterations: {self.max_iterations}")
        logger.info(f"   Convergence threshold: {self.convergence_threshold}")
        logger.info(f"   Significance threshold: {self.significance_threshold}")

        # Use case-based loop for strategy selection and execution
        # Combine queries into context
        combined_query = " | ".join(test_queries[:3])  # Use first 3 queries for context

        # Run case-based loop
        case_results = self.case_loop.run_case_loop(
            strategy=strategy,
            query=combined_query,
            context={
                'ab_testing': True,
                'queries': test_queries,
                'max_iterations': self.max_iterations
            }
        )

        # Extract A/B test results from case loop
        all_results = []
        score_history = []

        # Run A/B comparisons for each query
        for i, query in enumerate(test_queries):
            if i >= self.max_iterations:
                break

            logger.info(f"\n🔮 A/B Test - Query {i+1}/{len(test_queries)}")
            logger.info(f"   Testing: {query[:50]}...")

            result = self.run_comparison_test(
                query,
                user_id=f"god_loop_{i+1}",
                auto_assign=False
            )

            all_results.append(result)
            a_score = result['group_a']['score']
            b_score = result['group_b']['score']
            score_history.append({'a': a_score, 'b': b_score, 'iteration': i+1})

            # Check breakout conditions
            should_breakout, reason = self._check_breakout_conditions(a_score, b_score)

            if should_breakout:
                self.breakout_reason = reason
                logger.info(f"\n✅ God Feedback Loop Breakout: {reason}")
                break

        # Final analysis
        final_adjustments = self.adjust_inference_based_on_results()
        final_stats = self.get_test_statistics()

        # Curve progression
        all_scores = [r['group_a']['score'] for r in all_results] + [r['group_b']['score'] for r in all_results]
        final_curve = self.curve_grading.calculate_curve(
            all_scores,
            curve_type="infinite",
            progression=True
        )

        logger.info(f"\n🔮 God Feedback Loop Complete")
        logger.info(f"   Strategy used: {case_results.get('strategy', 'adaptive')}")
        logger.info(f"   Total iterations: {len(all_results)}")
        logger.info(f"   Breakout reason: {self.breakout_reason or case_results.get('breakout_reason', 'Max iterations reached')}")

        return {
            'loop_complete': True,
            'strategy': case_results.get('strategy', 'adaptive'),
            'total_iterations': len(all_results),
            'breakout_reason': self.breakout_reason or case_results.get('breakout_reason'),
            'convergence_detected': self.convergence_detected,
            'final_results': all_results[-1] if all_results else None,
            'all_results': all_results,
            'score_history': score_history,
            'case_loop_results': case_results,
            'final_adjustments': final_adjustments,
            'final_statistics': final_stats,
            'curve_progression': final_curve,
            'timestamp': datetime.now().isoformat()
        }

    def adjust_inference_based_on_results(self) -> Dict[str, Any]:
        """
        Adjust inference parameters based on A/B test results.

        Uses progressive curve and dynamic scaling to optimize.
        """
        logger.info("📊 Adjusting inference based on A/B test results...")

        stats = self.get_test_statistics()

        if not stats or 'results' not in stats:
            return {'error': 'No test results available'}

        # Analyze results
        a_results = [r for r in stats['results'] if r.group == TestGroup.CONTROL]
        b_results = [r for r in stats['results'] if r.group == TestGroup.EXPERIMENT]

        a_avg = sum(r.score for r in a_results) / len(a_results) if a_results else 0.0
        b_avg = sum(r.score for r in b_results) / len(b_results) if b_results else 0.0

        # Calculate adjustments
        adjustments = {
            'prefer_real': a_avg > b_avg,
            'prefer_simulated': b_avg > a_avg,
            'confidence': abs(a_avg - b_avg),
            'recommendation': 'real' if a_avg > b_avg else 'simulated' if b_avg > a_avg else 'balanced',
            'a_average': a_avg,
            'b_average': b_avg,
            'timestamp': datetime.now().isoformat()
        }

        # Dynamic scaling adjustments
        # Use resource metrics for scaling decision
        resource_metrics = self.dynamic_scaling.monitor_resources()
        scaling_decision = self.dynamic_scaling.should_scale(resource_metrics)
        adjustments['scaling'] = {
            'direction': scaling_decision.direction.value,
            'scale_factor': scaling_decision.scale_factor,
            'reason': scaling_decision.reason
        }

        logger.info(f"✅ Inference adjustments: {adjustments['recommendation']} (confidence: {adjustments['confidence']:.2f})")

        return adjustments


def main():
    """Example usage with God Feedback Loop"""
    print("=" * 80)
    print("🧪 DYNO A/B HOMELAB TEST - God Feedback Loop")
    print("   Real vs Simulated Homelab Comparison")
    print("=" * 80)
    print()

    # Initialize test with God Feedback Loop parameters
    test = DYNOABHomelabTest(
        max_iterations=50,  # Max iterations before forced breakout
        convergence_threshold=0.05,  # 5% variance for convergence
        significance_threshold=0.1,  # 10% difference for significance
        min_iterations=5  # Minimum iterations before allowing breakout
    )

    # Test queries
    test_queries = [
        "What is the meaning of balance in software development?",
        "Explain quantum entanglement in simple terms",
        "What are the principles of good system design?",
        "How does dynamic scaling work?",
        "What is the difference between real and simulated systems?"
    ]

    # Run God Feedback Loop
    print("🔮 Running God Feedback Loop...")
    print("-" * 80)
    loop_results = test.run_god_feedback_loop(test_queries, max_iterations=50)

    print("\n" + "=" * 80)
    print("🔮 GOD FEEDBACK LOOP RESULTS")
    print("=" * 80)
    print(f"Total Iterations: {loop_results['total_iterations']}")
    print(f"Breakout Reason: {loop_results['breakout_reason']}")
    print(f"Convergence Detected: {loop_results['convergence_detected']}")

    if loop_results['final_results']:
        final = loop_results['final_results']
        print(f"\nFinal Scores:")
        print(f"  Group A (Real): {final['group_a']['score']:.2f}")
        print(f"  Group B (Simulated): {final['group_b']['score']:.2f}")
        print(f"  Winner: {final['comparison']['winner']}")

    if loop_results['final_adjustments']:
        adj = loop_results['final_adjustments']
        print(f"\nFinal Adjustments:")
        print(f"  Recommendation: {adj['recommendation']}")
        print(f"  Confidence: {adj['confidence']:.2f}")
        print(f"  A Average: {adj['a_average']:.2f}")
        print(f"  B Average: {adj['b_average']:.2f}")

    print("\n" + "=" * 80)
    print("✅ God Feedback Loop Complete!")
    print("=" * 80)


if __name__ == "__main__":


    main()