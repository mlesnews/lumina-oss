#!/usr/bin/env python3
"""
JARVIS DYNO Performance Tuner
Performance testing and tuning system for JARVIS (like a dynamometer for engines)

Features:
- Concurrent session performance testing (3-4 sessions)
- Operator input learning and mapping (@OP inputs)
- Performance metrics collection
- Automatic tuning recommendations
- JARVIS analysis and action

@JARVIS @DYNO #TESTING #PERFORMANCE #TUNING @OP
"""

import sys
import json
import time
import threading
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# R5 Integration for session learning
try:
    from scripts.python.r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None

logger = get_logger("JARVISDYNO")


@dataclass
class OperatorInput:
    """Operator input mapping"""
    input_id: str
    session_id: str
    timestamp: float
    input_type: str  # command, query, request, etc.
    input_text: str
    context: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: float = 0.0
    success: bool = True
    patterns: List[str] = field(default_factory=list)


@dataclass
class SessionMetrics:
    """Session performance metrics"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    operator_inputs: List[OperatorInput] = field(default_factory=list)
    cpu_usage_percent: List[float] = field(default_factory=list)
    memory_usage_mb: List[float] = field(default_factory=list)
    response_times_ms: List[float] = field(default_factory=list)
    throughput_ops_per_sec: float = 0.0
    error_count: int = 0
    success_count: int = 0


@dataclass
class DynoTestResult:
    """DYNO test result"""
    test_id: str
    test_name: str
    timestamp: float
    concurrent_sessions: int
    session_metrics: List[SessionMetrics] = field(default_factory=list)
    overall_cpu_avg: float = 0.0
    overall_memory_avg: float = 0.0
    overall_throughput: float = 0.0
    overall_error_rate: float = 0.0
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OperatorInputPattern:
    """Learned operator input pattern"""
    pattern_id: str
    pattern_type: str
    frequency: int
    avg_response_time_ms: float
    success_rate: float
    common_contexts: List[str] = field(default_factory=list)
    mapped_to: Optional[str] = None  # Mapped to JARVIS action/command


class JARVISDynoPerformanceTuner:
    """
    JARVIS DYNO Performance Tuner

    Like a dynamometer for engines, this system:
    - Tests performance under load (concurrent sessions)
    - Measures metrics (CPU, memory, response time, throughput)
    - Learns operator input patterns
    - Maps inputs to actions
    - Provides tuning recommendations
    - Enables JARVIS analysis and action
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS DYNO Performance Tuner"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Storage
        self.dyno_dir = self.project_root / "data" / "jarvis_dyno"
        self.dyno_dir.mkdir(parents=True, exist_ok=True)
        self.tests_dir = self.dyno_dir / "tests"
        self.tests_dir.mkdir(exist_ok=True)
        self.operator_inputs_dir = self.dyno_dir / "operator_inputs"
        self.operator_inputs_dir.mkdir(exist_ok=True)
        self.patterns_dir = self.dyno_dir / "patterns"
        self.patterns_dir.mkdir(exist_ok=True)

        # Active sessions
        self.active_sessions: Dict[str, SessionMetrics] = {}
        self.session_lock = threading.Lock()

        # Operator input learning
        self.operator_inputs: List[OperatorInput] = []
        self.input_patterns: Dict[str, OperatorInputPattern] = {}

        # Performance metrics
        self.metrics_history: List[DynoTestResult] = []

        # Tuning parameters
        self.tuning_config = {
            "max_concurrent_sessions": 4,
            "target_cpu_percent": 75.0,
            "target_memory_percent": 80.0,
            "max_response_time_ms": 5000.0,
            "min_throughput_ops_per_sec": 1.0
        }

        # R5 Integration for session learning
        self.r5_system = None
        if R5_AVAILABLE:
            try:
                self.r5_system = R5LivingContextMatrix(project_root=self.project_root)
                logger.info("✅ R5 Living Context Matrix integrated for session learning")
            except Exception as e:
                logger.warning(f"⚠️  R5 not available: {e}")

        logger.info("✅ JARVIS DYNO Performance Tuner initialized")
        logger.info(f"   Storage: {self.dyno_dir}")
        logger.info(f"   Max Concurrent Sessions: {self.tuning_config['max_concurrent_sessions']}")

    def start_session(self, session_id: str) -> SessionMetrics:
        """Start a new session for performance testing"""
        with self.session_lock:
            if session_id in self.active_sessions:
                logger.warning(f"Session {session_id} already active")
                return self.active_sessions[session_id]

            session = SessionMetrics(
                session_id=session_id,
                start_time=time.time()
            )
            self.active_sessions[session_id] = session
            logger.info(f"🚀 Started session: {session_id}")
            return session

    def record_operator_input(
        self,
        session_id: str,
        input_text: str,
        input_type: str = "command",
        context: Optional[Dict[str, Any]] = None,
        response_time_ms: float = 0.0,
        success: bool = True
    ) -> OperatorInput:
        """Record operator input for learning and mapping"""
        input_id = f"input_{session_id}_{int(time.time() * 1000)}"

        operator_input = OperatorInput(
            input_id=input_id,
            session_id=session_id,
            timestamp=time.time(),
            input_type=input_type,
            input_text=input_text,
            context=context or {},
            response_time_ms=response_time_ms,
            success=success
        )

        # Extract patterns
        patterns = self._extract_input_patterns(input_text, context)
        operator_input.patterns = patterns

        # Store input
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].operator_inputs.append(operator_input)
            self.operator_inputs.append(operator_input)

        # Learn pattern
        self._learn_input_pattern(operator_input)

        # Save input
        self._save_operator_input(operator_input)

        # Ingest to R5 for session learning
        if self.r5_system:
            try:
                self.r5_system.ingest_session({
                    "session_id": session_id,
                    "messages": [
                        {"role": "user", "content": input_text},
                        {"role": "assistant", "content": f"Response time: {response_time_ms}ms, Success: {success}"}
                    ],
                    "metadata": {
                        "source": "dyno_performance_tuner",
                        "input_type": input_type,
                        "response_time_ms": response_time_ms,
                        "success": success,
                        "patterns": patterns
                    }
                })
                logger.debug(f"📚 Ingested operator input to R5 for session learning")
            except Exception as e:
                logger.debug(f"R5 ingestion error (non-critical): {e}")

        logger.debug(f"📝 Recorded operator input: {input_text[:50]}... (session: {session_id})")

        return operator_input

    def _extract_input_patterns(self, input_text: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Extract patterns from operator input"""
        patterns = []

        # Common patterns
        if "@" in input_text:
            patterns.append("tag_usage")
        if "#" in input_text:
            patterns.append("hashtag_usage")
        if any(word in input_text.lower() for word in ["create", "make", "build", "generate"]):
            patterns.append("creation_request")
        if any(word in input_text.lower() for word in ["fix", "repair", "debug", "error"]):
            patterns.append("fix_request")
        if any(word in input_text.lower() for word in ["enhance", "improve", "optimize", "tune"]):
            patterns.append("optimization_request")
        if any(word in input_text.lower() for word in ["analyze", "check", "verify", "test"]):
            patterns.append("analysis_request")

        # Context patterns
        if context:
            if "concurrent_sessions" in context:
                patterns.append("concurrent_session_context")
            if "performance" in context:
                patterns.append("performance_context")

        return patterns

    def _learn_input_pattern(self, operator_input: OperatorInput):
        """Learn and update input patterns"""
        # Group by pattern type
        for pattern_type in operator_input.patterns:
            if pattern_type not in self.input_patterns:
                self.input_patterns[pattern_type] = OperatorInputPattern(
                    pattern_id=f"pattern_{pattern_type}_{int(time.time())}",
                    pattern_type=pattern_type,
                    frequency=1,
                    avg_response_time_ms=operator_input.response_time_ms,
                    success_rate=1.0 if operator_input.success else 0.0,
                    common_contexts=[str(operator_input.context)]
                )
            else:
                pattern = self.input_patterns[pattern_type]
                pattern.frequency += 1
                # Update average response time
                pattern.avg_response_time_ms = (
                    (pattern.avg_response_time_ms * (pattern.frequency - 1) + operator_input.response_time_ms) /
                    pattern.frequency
                )
                # Update success rate
                total_attempts = pattern.frequency
                if operator_input.success:
                    pattern.success_rate = (
                        (pattern.success_rate * (total_attempts - 1) + 1.0) / total_attempts
                    )
                else:
                    pattern.success_rate = (
                        (pattern.success_rate * (total_attempts - 1)) / total_attempts
                    )
                # Update contexts
                context_str = str(operator_input.context)
                if context_str not in pattern.common_contexts:
                    pattern.common_contexts.append(context_str)

    def _save_operator_input(self, operator_input: OperatorInput):
        """Save operator input to disk"""
        try:
            input_file = self.operator_inputs_dir / f"{operator_input.input_id}.json"
            with open(input_file, "w", encoding="utf-8") as f:
                json.dump(asdict(operator_input), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving operator input: {e}")

    def collect_metrics(self, session_id: str):
        """Collect performance metrics for a session"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                return

            session = self.active_sessions[session_id]

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            session.cpu_usage_percent.append(cpu_percent)

            # Memory usage
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / (1024 * 1024)
            session.memory_usage_mb.append(memory_mb)

            # Response times
            if session.operator_inputs:
                latest_input = session.operator_inputs[-1]
                session.response_times_ms.append(latest_input.response_time_ms)

            # Throughput
            if session.operator_inputs:
                elapsed_time = time.time() - session.start_time
                if elapsed_time > 0:
                    session.throughput_ops_per_sec = len(session.operator_inputs) / elapsed_time

            # Success/error counts
            session.success_count = sum(1 for inp in session.operator_inputs if inp.success)
            session.error_count = sum(1 for inp in session.operator_inputs if not inp.success)

    def run_dyno_test(
        self,
        test_name: str,
        concurrent_sessions: int = 4,
        duration_seconds: int = 60
    ) -> DynoTestResult:
        """
        Run a DYNO performance test (like a dynamometer for engines)

        Args:
            test_name: Name of the test
            concurrent_sessions: Number of concurrent sessions (3-4)
            duration_seconds: Test duration in seconds

        Returns:
            DynoTestResult with performance metrics
        """
        logger.info(f"🔧 Starting DYNO test: {test_name}")
        logger.info(f"   Concurrent sessions: {concurrent_sessions}")
        logger.info(f"   Duration: {duration_seconds}s")

        test_id = f"dyno_test_{int(time.time())}"

        # Start sessions
        sessions = []
        for i in range(concurrent_sessions):
            session_id = f"{test_id}_session_{i+1}"
            session = self.start_session(session_id)
            sessions.append(session)

        # Run test
        start_time = time.time()
        end_time = start_time + duration_seconds

        while time.time() < end_time:
            # Collect metrics for all sessions
            for session in sessions:
                self.collect_metrics(session.session_id)

            time.sleep(1.0)  # Collect every second

        # Finalize sessions
        session_metrics = []
        for session in sessions:
            session.end_time = time.time()
            session_metrics.append(session)
            with self.session_lock:
                if session.session_id in self.active_sessions:
                    del self.active_sessions[session.session_id]

        # Calculate overall metrics
        overall_cpu = sum(
            sum(s.cpu_usage_percent) / len(s.cpu_usage_percent) if s.cpu_usage_percent else 0
            for s in session_metrics
        ) / len(session_metrics) if session_metrics else 0.0

        overall_memory = sum(
            sum(s.memory_usage_mb) / len(s.memory_usage_mb) if s.memory_usage_mb else 0
            for s in session_metrics
        ) / len(session_metrics) if session_metrics else 0.0

        overall_throughput = sum(s.throughput_ops_per_sec for s in session_metrics)

        total_errors = sum(s.error_count for s in session_metrics)
        total_operations = sum(len(s.operator_inputs) for s in session_metrics)
        overall_error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0.0

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(session_metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_cpu, overall_memory, overall_throughput, overall_error_rate, bottlenecks
        )

        # Create test result
        test_result = DynoTestResult(
            test_id=test_id,
            test_name=test_name,
            timestamp=time.time(),
            concurrent_sessions=concurrent_sessions,
            session_metrics=session_metrics,
            overall_cpu_avg=overall_cpu,
            overall_memory_avg=overall_memory,
            overall_throughput=overall_throughput,
            overall_error_rate=overall_error_rate,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )

        # Save test result
        self._save_test_result(test_result)
        self.metrics_history.append(test_result)

        logger.info(f"✅ DYNO test complete: {test_name}")
        logger.info(f"   CPU Avg: {overall_cpu:.1f}%")
        logger.info(f"   Memory Avg: {overall_memory:.1f} MB")
        logger.info(f"   Throughput: {overall_throughput:.2f} ops/sec")
        logger.info(f"   Error Rate: {overall_error_rate:.2f}%")
        logger.info(f"   Bottlenecks: {len(bottlenecks)}")
        logger.info(f"   Recommendations: {len(recommendations)}")

        return test_result

    def _identify_bottlenecks(self, session_metrics: List[SessionMetrics]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Check CPU
        max_cpu = max(
            max(s.cpu_usage_percent) if s.cpu_usage_percent else 0
            for s in session_metrics
        )
        if max_cpu > self.tuning_config["target_cpu_percent"]:
            bottlenecks.append(f"High CPU usage: {max_cpu:.1f}% (target: {self.tuning_config['target_cpu_percent']}%)")

        # Check memory
        max_memory = max(
            max(s.memory_usage_mb) if s.memory_usage_mb else 0
            for s in session_metrics
        )
        if max_memory > (self.tuning_config["target_memory_percent"] / 100 * psutil.virtual_memory().total / (1024 * 1024)):
            bottlenecks.append(f"High memory usage: {max_memory:.1f} MB")

        # Check response times
        max_response_time = max(
            max(s.response_times_ms) if s.response_times_ms else 0
            for s in session_metrics
        )
        if max_response_time > self.tuning_config["max_response_time_ms"]:
            bottlenecks.append(f"Slow response time: {max_response_time:.1f}ms (target: {self.tuning_config['max_response_time_ms']}ms)")

        # Check error rate
        total_errors = sum(s.error_count for s in session_metrics)
        total_ops = sum(len(s.operator_inputs) for s in session_metrics)
        if total_ops > 0 and (total_errors / total_ops) > 0.1:
            bottlenecks.append(f"High error rate: {(total_errors / total_ops * 100):.1f}%")

        return bottlenecks

    def _generate_recommendations(
        self,
        cpu_avg: float,
        memory_avg: float,
        throughput: float,
        error_rate: float,
        bottlenecks: List[str]
    ) -> List[str]:
        """Generate performance tuning recommendations"""
        recommendations = []

        if cpu_avg > self.tuning_config["target_cpu_percent"]:
            recommendations.append("Consider reducing concurrent sessions or optimizing CPU-intensive operations")

        if memory_avg > (self.tuning_config["target_memory_percent"] / 100 * psutil.virtual_memory().total / (1024 * 1024)):
            recommendations.append("Consider implementing memory caching or reducing memory footprint")

        if throughput < self.tuning_config["min_throughput_ops_per_sec"]:
            recommendations.append("Consider optimizing response times or parallelizing operations")

        if error_rate > 10.0:
            recommendations.append("Investigate and fix error sources to improve reliability")

        if not bottlenecks:
            recommendations.append("Performance is within target parameters - consider increasing load for stress testing")

        return recommendations

    def _save_test_result(self, test_result: DynoTestResult):
        """Save test result to disk"""
        try:
            test_file = self.tests_dir / f"{test_result.test_id}.json"

            # Convert to dict (handle nested dataclasses)
            result_dict = {
                "test_id": test_result.test_id,
                "test_name": test_result.test_name,
                "timestamp": test_result.timestamp,
                "concurrent_sessions": test_result.concurrent_sessions,
                "overall_cpu_avg": test_result.overall_cpu_avg,
                "overall_memory_avg": test_result.overall_memory_avg,
                "overall_throughput": test_result.overall_throughput,
                "overall_error_rate": test_result.overall_error_rate,
                "bottlenecks": test_result.bottlenecks,
                "recommendations": test_result.recommendations,
                "session_metrics": [
                    {
                        "session_id": s.session_id,
                        "start_time": s.start_time,
                        "end_time": s.end_time,
                        "throughput_ops_per_sec": s.throughput_ops_per_sec,
                        "error_count": s.error_count,
                        "success_count": s.success_count,
                        "operator_inputs_count": len(s.operator_inputs)
                    }
                    for s in test_result.session_metrics
                ]
            }

            with open(test_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved test result: {test_file}")
        except Exception as e:
            logger.error(f"Error saving test result: {e}")

    def get_operator_input_patterns(self) -> Dict[str, OperatorInputPattern]:
        """Get learned operator input patterns"""
        return self.input_patterns

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for JARVIS analysis"""
        if not self.metrics_history:
            return {"status": "no_tests", "message": "No DYNO tests run yet"}

        latest_test = self.metrics_history[-1]

        return {
            "status": "active",
            "latest_test": {
                "test_name": latest_test.test_name,
                "concurrent_sessions": latest_test.concurrent_sessions,
                "cpu_avg": latest_test.overall_cpu_avg,
                "memory_avg": latest_test.overall_memory_avg,
                "throughput": latest_test.overall_throughput,
                "error_rate": latest_test.overall_error_rate
            },
            "bottlenecks": latest_test.bottlenecks,
            "recommendations": latest_test.recommendations,
            "operator_input_patterns": {
                pattern_id: {
                    "pattern_type": pattern.pattern_type,
                    "frequency": pattern.frequency,
                    "avg_response_time_ms": pattern.avg_response_time_ms,
                    "success_rate": pattern.success_rate
                }
                for pattern_id, pattern in self.input_patterns.items()
            },
            "total_tests": len(self.metrics_history),
            "total_operator_inputs": len(self.operator_inputs)
        }

    def analyze_and_take_action(self) -> Dict[str, Any]:
        """
        JARVIS analysis and action based on DYNO test results

        Returns:
            Analysis results and actions taken
        """
        logger.info("🔍 JARVIS analyzing DYNO performance data...")

        summary = self.get_performance_summary()

        if summary["status"] == "no_tests":
            return {
                "action": "no_action",
                "reason": "No tests available for analysis",
                "recommendation": "Run DYNO test first"
            }

        actions_taken = []

        # Analyze bottlenecks
        if summary["bottlenecks"]:
            logger.warning(f"⚠️  {len(summary['bottlenecks'])} bottleneck(s) detected")
            actions_taken.append({
                "action": "bottleneck_alert",
                "bottlenecks": summary["bottlenecks"],
                "priority": "high"
            })

        # Analyze recommendations
        if summary["recommendations"]:
            logger.info(f"💡 {len(summary['recommendations'])} recommendation(s) generated")
            actions_taken.append({
                "action": "tuning_recommendations",
                "recommendations": summary["recommendations"],
                "priority": "medium"
            })

        # Analyze operator input patterns
        if summary["operator_input_patterns"]:
            logger.info(f"📊 {len(summary['operator_input_patterns'])} operator input pattern(s) learned")
            actions_taken.append({
                "action": "pattern_analysis",
                "patterns": summary["operator_input_patterns"],
                "priority": "low"
            })

        # Performance status
        latest = summary["latest_test"]
        performance_status = "good"
        if latest["cpu_avg"] > self.tuning_config["target_cpu_percent"]:
            performance_status = "needs_tuning"
        if latest["error_rate"] > 10.0:
            performance_status = "needs_attention"

        return {
            "action": "analysis_complete",
            "performance_status": performance_status,
            "actions_taken": actions_taken,
            "summary": summary
        }


def main():
    """Example usage"""
    print("=" * 70)
    print("🔧 JARVIS DYNO Performance Tuner")
    print("=" * 70)
    print()

    dyno = JARVISDynoPerformanceTuner()

    # Simulate concurrent sessions
    print("🚀 Simulating 4 concurrent sessions...")

    # Start sessions
    sessions = []
    for i in range(4):
        session_id = f"test_session_{i+1}"
        session = dyno.start_session(session_id)
        sessions.append(session_id)

    # Simulate operator inputs
    print("📝 Recording operator inputs...")
    test_inputs = [
        ("@JARVIS create a new workflow", "command"),
        ("#PERFORMANCE tune the system", "optimization_request"),
        ("@SYPHON extract patterns from code", "analysis_request"),
        ("Fix the error in the integration", "fix_request"),
    ]

    for session_id in sessions:
        for input_text, input_type in test_inputs:
            dyno.record_operator_input(
                session_id=session_id,
                input_text=input_text,
                input_type=input_type,
                response_time_ms=100.0 + (hash(input_text) % 500),
                success=True
            )
            time.sleep(0.1)

    # Run DYNO test
    print("🔧 Running DYNO test...")
    result = dyno.run_dyno_test(
        test_name="Concurrent Session Performance Test",
        concurrent_sessions=4,
        duration_seconds=10
    )

    print()
    print("📊 Test Results:")
    print(f"   CPU Avg: {result.overall_cpu_avg:.1f}%")
    print(f"   Memory Avg: {result.overall_memory_avg:.1f} MB")
    print(f"   Throughput: {result.overall_throughput:.2f} ops/sec")
    print(f"   Error Rate: {result.overall_error_rate:.2f}%")
    print()

    if result.bottlenecks:
        print("⚠️  Bottlenecks:")
        for bottleneck in result.bottlenecks:
            print(f"   - {bottleneck}")
        print()

    if result.recommendations:
        print("💡 Recommendations:")
        for rec in result.recommendations:
            print(f"   - {rec}")
        print()

    # JARVIS analysis
    print("🔍 JARVIS analyzing and taking action...")
    analysis = dyno.analyze_and_take_action()

    print(f"   Performance Status: {analysis['performance_status']}")
    print(f"   Actions Taken: {len(analysis['actions_taken'])}")
    print()

    # Operator input patterns
    patterns = dyno.get_operator_input_patterns()
    if patterns:
        print("📊 Learned Operator Input Patterns:")
        for pattern_id, pattern in patterns.items():
            print(f"   {pattern.pattern_type}:")
            print(f"      Frequency: {pattern.frequency}")
            print(f"      Avg Response Time: {pattern.avg_response_time_ms:.1f}ms")
            print(f"      Success Rate: {pattern.success_rate:.1%}")
        print()

    print("=" * 70)
    print("✅ JARVIS DYNO Performance Tuner Complete!")
    print("=" * 70)


if __name__ == "__main__":


    main()