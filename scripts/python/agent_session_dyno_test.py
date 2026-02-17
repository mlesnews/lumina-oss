#!/usr/bin/env python3
"""
Agent Session DYNO Performance Test
Part of DYNO Performance Testing Framework

Tests concurrent agent sessions (3, 4, 5) to determine Goldilocks zone.
Measures performance, statistics, and metrics to guide scaling decisions.

DYNO System Component:
- Part of Performance Engineering & Capacity Management Team
- Integrates with main DYNO framework (dyno_performance_test.py)
- Finds MIN/MAX capacity bounds and calibrates to Goldilocks Zone

Based on user determination: 4 sessions = Goldilocks zone
- 3 sessions: Full bore baseline
- 4 sessions: Goldilocks zone (optimal)
- 5 sessions: Nitrous mode (stress test)

Tags: #DYNO #PERFORMANCE #AGENT_SESSIONS #GOLDILOCKS #METRICS @JARVIS @LUMINA
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

logger = get_logger("AgentSessionDyno")


@dataclass
class AgentSessionMetrics:
    """Metrics for a single agent session"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: float = 0.0

    # System metrics (sampled over time)
    cpu_samples: List[float] = field(default_factory=list)
    memory_samples_mb: List[float] = field(default_factory=list)
    disk_io_read_mb: List[float] = field(default_factory=list)
    disk_io_write_mb: List[float] = field(default_factory=list)
    network_sent_mb: List[float] = field(default_factory=list)
    network_recv_mb: List[float] = field(default_factory=list)

    # Performance metrics
    response_times_ms: List[float] = field(default_factory=list)
    operations_count: int = 0
    errors_count: int = 0
    success_rate: float = 1.0

    # Aggregated stats
    avg_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0
    max_cpu_percent: float = 0.0
    max_memory_mb: float = 0.0
    avg_response_time_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0


@dataclass
class DynoTestConfiguration:
    """Configuration for a DYNO test run"""
    test_name: str
    concurrent_sessions: int  # 3, 4, or 5
    duration_seconds: int = 300  # 5 minutes default
    sample_interval_seconds: float = 1.0
    warmup_seconds: int = 30  # Warmup period before measurement


@dataclass
class DynoTestResult:
    """Results from a DYNO test run"""
    test_id: str
    config: DynoTestConfiguration
    start_time: float
    end_time: float
    duration_seconds: float

    # Individual session metrics
    session_metrics: List[AgentSessionMetrics] = field(default_factory=list)

    # System-wide aggregated metrics
    system_cpu_avg: float = 0.0
    system_cpu_max: float = 0.0
    system_memory_avg_mb: float = 0.0
    system_memory_max_mb: float = 0.0
    system_disk_io_avg_mb_per_sec: float = 0.0
    system_network_avg_mb_per_sec: float = 0.0

    # Performance metrics
    overall_throughput_ops_per_sec: float = 0.0
    overall_avg_response_time_ms: float = 0.0
    overall_error_rate: float = 0.0
    overall_success_rate: float = 1.0

    # Zone classification
    zone: str = "UNKNOWN"  # TOO_COLD, GOLDILOCKS, TOO_HOT
    stability_score: float = 0.0  # 0-1, higher = more stable

    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)


class AgentSessionDynoTest:
    """
    Agent Session DYNO Performance Test

    Like a dynamometer for engines - stress testing for maximum performance.
    Tests concurrent agent sessions to find optimal configuration.

    DYNO = Dynamometer:
    - Put system on DYNO (stress test it)
    - Test at different loads (3, 4, 5 sessions)
    - Measure performance (horsepower/torque equivalent)
    - Find maximum performance
    - Tune for best results
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize DYNO test system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Storage (integrated with DYNO system)
        self.dyno_dir = self.project_root / "data" / "performance_metrics" / "agent_sessions"
        self.dyno_dir.mkdir(parents=True, exist_ok=True)
        self.tests_dir = self.dyno_dir / "tests"
        self.tests_dir.mkdir(exist_ok=True)
        self.reports_dir = self.dyno_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Integration with main DYNO framework
        try:
            from dyno_performance_test import DynoPerformanceTest, GoldilocksZone
            self.main_dyno = DynoPerformanceTest()
            self.goldilocks_zone = self.main_dyno.goldilocks
            logger.info("✅ Integrated with main DYNO Performance Testing Framework")
        except ImportError:
            self.main_dyno = None
            self.goldilocks_zone = None
            logger.debug("Main DYNO framework not available (optional integration)")

        # Test state
        self.active_test: Optional[DynoTestResult] = None
        self.test_lock = threading.Lock()
        self.monitoring_active = False

        # Goldilocks zone thresholds (based on 4 sessions = optimal)
        self.goldilocks_thresholds = {
            "cpu_max_percent": 85.0,
            "cpu_avg_percent": 70.0,
            "memory_max_mb": 8000,  # 8GB max
            "memory_avg_mb": 6000,  # 6GB avg
            "response_time_max_ms": 5000.0,
            "response_time_avg_ms": 2000.0,
            "error_rate_max": 5.0,  # 5% max error rate
            "stability_min": 0.85  # 85% stability score
        }

        logger.info("✅ Agent Session DYNO Test initialized")
        logger.info(f"   Storage: {self.dyno_dir}")
        logger.info(f"   Goldilocks Zone: 4 concurrent sessions (user determined)")
        logger.info(f"   Part of DYNO Performance Testing Framework")

    def run_test(self, config: DynoTestConfiguration) -> DynoTestResult:
        """
        Run a DYNO performance test

        Args:
            config: Test configuration

        Returns:
            DynoTestResult with comprehensive metrics
        """
        test_id = f"dyno_{config.concurrent_sessions}sessions_{int(time.time())}"

        logger.info("=" * 80)
        logger.info(f"🔧 STARTING DYNO TEST: {config.test_name}")
        logger.info("=" * 80)
        logger.info(f"   Concurrent Sessions: {config.concurrent_sessions}")
        logger.info(f"   Duration: {config.duration_seconds}s ({config.duration_seconds/60:.1f} minutes)")
        logger.info(f"   Sample Interval: {config.sample_interval_seconds}s")
        logger.info(f"   Warmup: {config.warmup_seconds}s")
        logger.info("=" * 80)

        # Initialize test result
        test_result = DynoTestResult(
            test_id=test_id,
            config=config,
            start_time=time.time(),
            end_time=0.0,
            duration_seconds=0.0
        )

        with self.test_lock:
            self.active_test = test_result
            self.monitoring_active = True

        # Start monitoring thread
        monitoring_thread = threading.Thread(
            target=self._monitor_sessions,
            args=(test_result, config),
            daemon=True
        )
        monitoring_thread.start()

        # Warmup period
        if config.warmup_seconds > 0:
            logger.info(f"🔥 Warmup period: {config.warmup_seconds}s")
            time.sleep(config.warmup_seconds)

        # Main test period
        logger.info(f"📊 Starting measurement period: {config.duration_seconds}s")
        test_start = time.time()
        test_end = test_start + config.duration_seconds

        # Simulate agent sessions (in real implementation, these would be actual agent sessions)
        session_threads = []
        for i in range(config.concurrent_sessions):
            session_id = f"{test_id}_session_{i+1}"
            thread = threading.Thread(
                target=self._simulate_agent_session,
                args=(session_id, test_result, test_end),
                daemon=True
            )
            thread.start()
            session_threads.append(thread)

        # Wait for test to complete
        while time.time() < test_end:
            time.sleep(1)

        # Stop monitoring
        with self.test_lock:
            self.monitoring_active = False

        # Wait for threads to finish
        for thread in session_threads:
            thread.join(timeout=5)

        # Finalize test
        test_result.end_time = time.time()
        test_result.duration_seconds = test_result.end_time - test_result.start_time

        # Calculate aggregated metrics
        self._calculate_aggregated_metrics(test_result)

        # Classify zone
        test_result.zone = self._classify_zone(test_result)

        # Calculate stability score
        test_result.stability_score = self._calculate_stability_score(test_result)

        # Identify bottlenecks
        test_result.bottlenecks = self._identify_bottlenecks(test_result)

        # Generate recommendations
        test_result.recommendations = self._generate_recommendations(test_result)

        # Save test result
        self._save_test_result(test_result)

        # Print summary
        self._print_test_summary(test_result)

        with self.test_lock:
            self.active_test = None

        return test_result

    def _simulate_agent_session(
        self,
        session_id: str,
        test_result: DynoTestResult,
        end_time: float
    ):
        """Simulate an agent session (placeholder - replace with actual agent session)"""
        session_metrics = AgentSessionMetrics(
            session_id=session_id,
            start_time=time.time()
        )

        operation_count = 0

        while time.time() < end_time:
            # Simulate agent operation
            operation_start = time.time()

            # Simulate work (CPU-bound, memory-bound, I/O-bound)
            time.sleep(0.1 + (hash(session_id) % 100) / 1000)  # Variable work time

            operation_end = time.time()
            response_time = (operation_end - operation_start) * 1000  # ms

            session_metrics.response_times_ms.append(response_time)
            session_metrics.operations_count += 1
            operation_count += 1

            # Simulate occasional errors (5% error rate)
            if operation_count % 20 == 0:
                session_metrics.errors_count += 1
            else:
                session_metrics.success_count = session_metrics.operations_count - session_metrics.errors_count

            time.sleep(0.5)  # Between operations

        session_metrics.end_time = time.time()
        session_metrics.duration_seconds = session_metrics.end_time - session_metrics.start_time

        # Calculate session stats
        if session_metrics.cpu_samples:
            session_metrics.avg_cpu_percent = sum(session_metrics.cpu_samples) / len(session_metrics.cpu_samples)
            session_metrics.max_cpu_percent = max(session_metrics.cpu_samples)

        if session_metrics.memory_samples_mb:
            session_metrics.avg_memory_mb = sum(session_metrics.memory_samples_mb) / len(session_metrics.memory_samples_mb)
            session_metrics.max_memory_mb = max(session_metrics.memory_samples_mb)

        if session_metrics.response_times_ms:
            session_metrics.avg_response_time_ms = sum(session_metrics.response_times_ms) / len(session_metrics.response_times_ms)

        if session_metrics.duration_seconds > 0:
            session_metrics.throughput_ops_per_sec = session_metrics.operations_count / session_metrics.duration_seconds

        if session_metrics.operations_count > 0:
            session_metrics.success_rate = session_metrics.success_count / session_metrics.operations_count

        with self.test_lock:
            test_result.session_metrics.append(session_metrics)

    def _monitor_sessions(
        self,
        test_result: DynoTestResult,
        config: DynoTestConfiguration
    ):
        """Monitor system metrics during test"""
        last_disk_io = psutil.disk_io_counters()
        last_net_io = psutil.net_io_counters()

        while self.monitoring_active:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)

            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io and last_disk_io:
                disk_read_mb = (disk_io.read_bytes - last_disk_io.read_bytes) / (1024 * 1024)
                disk_write_mb = (disk_io.write_bytes - last_disk_io.write_bytes) / (1024 * 1024)
            else:
                disk_read_mb = 0.0
                disk_write_mb = 0.0
            last_disk_io = disk_io

            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io and last_net_io:
                net_sent_mb = (net_io.bytes_sent - last_net_io.bytes_sent) / (1024 * 1024)
                net_recv_mb = (net_io.bytes_recv - last_net_io.bytes_recv) / (1024 * 1024)
            else:
                net_sent_mb = 0.0
                net_recv_mb = 0.0
            last_net_io = net_io

            # Update session metrics (distribute system metrics across sessions)
            with self.test_lock:
                if test_result.session_metrics:
                    sessions_count = len(test_result.session_metrics)
                    for session in test_result.session_metrics:
                        session.cpu_samples.append(cpu_percent / sessions_count)
                        session.memory_samples_mb.append(memory_mb / sessions_count)
                        session.disk_io_read_mb.append(disk_read_mb / sessions_count)
                        session.disk_io_write_mb.append(disk_write_mb / sessions_count)
                        session.network_sent_mb.append(net_sent_mb / sessions_count)
                        session.network_recv_mb.append(net_recv_mb / sessions_count)

            time.sleep(config.sample_interval_seconds)

    def _calculate_aggregated_metrics(self, test_result: DynoTestResult):
        """Calculate system-wide aggregated metrics"""
        if not test_result.session_metrics:
            return

        # CPU
        all_cpu_samples = []
        for session in test_result.session_metrics:
            all_cpu_samples.extend(session.cpu_samples)

        if all_cpu_samples:
            test_result.system_cpu_avg = sum(all_cpu_samples) / len(all_cpu_samples)
            test_result.system_cpu_max = max(all_cpu_samples)

        # Memory
        all_memory_samples = []
        for session in test_result.session_metrics:
            all_memory_samples.extend(session.memory_samples_mb)

        if all_memory_samples:
            test_result.system_memory_avg_mb = sum(all_memory_samples) / len(all_memory_samples)
            test_result.system_memory_max_mb = max(all_memory_samples)

        # Disk I/O
        all_disk_read = []
        all_disk_write = []
        for session in test_result.session_metrics:
            if session.disk_io_read_mb:
                all_disk_read.extend(session.disk_io_read_mb)
            if session.disk_io_write_mb:
                all_disk_write.extend(session.disk_io_write_mb)

        if all_disk_read:
            test_result.system_disk_io_avg_mb_per_sec = sum(all_disk_read) / len(all_disk_read)

        # Network
        all_net_sent = []
        all_net_recv = []
        for session in test_result.session_metrics:
            if session.network_sent_mb:
                all_net_sent.extend(session.network_sent_mb)
            if session.network_recv_mb:
                all_net_recv.extend(session.network_recv_mb)

        if all_net_sent:
            test_result.system_network_avg_mb_per_sec = sum(all_net_sent) / len(all_net_sent)

        # Performance metrics
        total_operations = sum(s.operations_count for s in test_result.session_metrics)
        total_errors = sum(s.errors_count for s in test_result.session_metrics)
        total_response_times = []
        for session in test_result.session_metrics:
            total_response_times.extend(session.response_times_ms)

        if test_result.duration_seconds > 0:
            test_result.overall_throughput_ops_per_sec = total_operations / test_result.duration_seconds

        if total_response_times:
            test_result.overall_avg_response_time_ms = sum(total_response_times) / len(total_response_times)

        if total_operations > 0:
            test_result.overall_error_rate = (total_errors / total_operations) * 100
            test_result.overall_success_rate = ((total_operations - total_errors) / total_operations) * 100

    def _classify_zone(self, test_result: DynoTestResult) -> str:
        """Classify performance zone: TOO_COLD, GOLDILOCKS, or TOO_HOT"""
        thresholds = self.goldilocks_thresholds

        # Check for TOO_HOT
        if (test_result.system_cpu_max > thresholds["cpu_max_percent"] or
            test_result.system_memory_max_mb > thresholds["memory_max_mb"] or
            test_result.overall_avg_response_time_ms > thresholds["response_time_max_ms"] or
            test_result.overall_error_rate > thresholds["error_rate_max"]):
            return "TOO_HOT"

        # Check for TOO_COLD
        if (test_result.system_cpu_avg < 30.0 and
            test_result.system_memory_avg_mb < 2000 and
            test_result.overall_throughput_ops_per_sec < 0.5):
            return "TOO_COLD"

        # Otherwise GOLDILOCKS
        return "GOLDILOCKS"

    def _calculate_stability_score(self, test_result: DynoTestResult) -> float:
        """Calculate stability score (0-1, higher = more stable)"""
        if not test_result.session_metrics:
            return 0.0

        # Calculate variance in metrics
        cpu_variances = []
        memory_variances = []
        response_time_variances = []

        for session in test_result.session_metrics:
            if len(session.cpu_samples) > 1:
                mean = sum(session.cpu_samples) / len(session.cpu_samples)
                variance = sum((x - mean) ** 2 for x in session.cpu_samples) / len(session.cpu_samples)
                cpu_variances.append(variance)

            if len(session.memory_samples_mb) > 1:
                mean = sum(session.memory_samples_mb) / len(session.memory_samples_mb)
                variance = sum((x - mean) ** 2 for x in session.memory_samples_mb) / len(session.memory_samples_mb)
                memory_variances.append(variance)

            if len(session.response_times_ms) > 1:
                mean = sum(session.response_times_ms) / len(session.response_times_ms)
                variance = sum((x - mean) ** 2 for x in session.response_times_ms) / len(session.response_times_ms)
                response_time_variances.append(variance)

        # Normalize variances (lower variance = higher stability)
        # Simple heuristic: if variance is low, stability is high
        avg_cpu_variance = sum(cpu_variances) / len(cpu_variances) if cpu_variances else 100.0
        avg_memory_variance = sum(memory_variances) / len(memory_variances) if memory_variances else 1000000.0
        avg_response_variance = sum(response_time_variances) / len(response_time_variances) if response_time_variances else 1000000.0

        # Convert to stability score (inverse relationship)
        cpu_stability = max(0.0, 1.0 - (avg_cpu_variance / 100.0))
        memory_stability = max(0.0, 1.0 - (avg_memory_variance / 1000000.0))
        response_stability = max(0.0, 1.0 - (avg_response_variance / 1000000.0))

        # Overall stability (weighted average)
        stability = (cpu_stability * 0.4 + memory_stability * 0.3 + response_stability * 0.3)

        return min(1.0, max(0.0, stability))

    def _identify_bottlenecks(self, test_result: DynoTestResult) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        thresholds = self.goldilocks_thresholds

        if test_result.system_cpu_max > thresholds["cpu_max_percent"]:
            bottlenecks.append(f"CPU bottleneck: {test_result.system_cpu_max:.1f}% max (threshold: {thresholds['cpu_max_percent']}%)")

        if test_result.system_memory_max_mb > thresholds["memory_max_mb"]:
            bottlenecks.append(f"Memory bottleneck: {test_result.system_memory_max_mb:.0f}MB max (threshold: {thresholds['memory_max_mb']}MB)")

        if test_result.overall_avg_response_time_ms > thresholds["response_time_avg_ms"]:
            bottlenecks.append(f"Response time bottleneck: {test_result.overall_avg_response_time_ms:.1f}ms avg (threshold: {thresholds['response_time_avg_ms']}ms)")

        if test_result.overall_error_rate > thresholds["error_rate_max"]:
            bottlenecks.append(f"Error rate bottleneck: {test_result.overall_error_rate:.1f}% (threshold: {thresholds['error_rate_max']}%)")

        if test_result.stability_score < thresholds["stability_min"]:
            bottlenecks.append(f"Stability bottleneck: {test_result.stability_score:.2f} score (threshold: {thresholds['stability_min']})")

        return bottlenecks

    def _generate_recommendations(self, test_result: DynoTestResult) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        if test_result.zone == "TOO_HOT":
            recommendations.append(f"⚠️  System is TOO_HOT with {test_result.config.concurrent_sessions} sessions")
            recommendations.append("   → Reduce concurrent sessions or optimize resource usage")
            if test_result.system_cpu_max > 90:
                recommendations.append("   → CPU is critically high - reduce load immediately")
            if test_result.system_memory_max_mb > 8000:
                recommendations.append("   → Memory is critically high - implement memory optimization")

        elif test_result.zone == "TOO_COLD":
            recommendations.append(f"✅ System is TOO_COLD with {test_result.config.concurrent_sessions} sessions")
            recommendations.append("   → Can safely increase concurrent sessions")
            recommendations.append("   → System has headroom for more load")

        elif test_result.zone == "GOLDILOCKS":
            recommendations.append(f"🎯 System is in GOLDILOCKS zone with {test_result.config.concurrent_sessions} sessions")
            recommendations.append("   → This is the optimal configuration")
            recommendations.append("   → Maintain current session count")

        if test_result.bottlenecks:
            recommendations.append(f"   → Address {len(test_result.bottlenecks)} bottleneck(s) identified")

        if test_result.stability_score < 0.85:
            recommendations.append("   → Improve stability through optimization")

        return recommendations

    def _save_test_result(self, test_result: DynoTestResult):
        """Save test result to disk"""
        try:
            result_file = self.tests_dir / f"{test_result.test_id}.json"

            # Convert to dict
            result_dict = {
                "test_id": test_result.test_id,
                "config": {
                    "test_name": test_result.config.test_name,
                    "concurrent_sessions": test_result.config.concurrent_sessions,
                    "duration_seconds": test_result.config.duration_seconds
                },
                "timing": {
                    "start_time": test_result.start_time,
                    "end_time": test_result.end_time,
                    "duration_seconds": test_result.duration_seconds
                },
                "system_metrics": {
                    "cpu_avg": test_result.system_cpu_avg,
                    "cpu_max": test_result.system_cpu_max,
                    "memory_avg_mb": test_result.system_memory_avg_mb,
                    "memory_max_mb": test_result.system_memory_max_mb,
                    "disk_io_avg_mb_per_sec": test_result.system_disk_io_avg_mb_per_sec,
                    "network_avg_mb_per_sec": test_result.system_network_avg_mb_per_sec
                },
                "performance_metrics": {
                    "throughput_ops_per_sec": test_result.overall_throughput_ops_per_sec,
                    "avg_response_time_ms": test_result.overall_avg_response_time_ms,
                    "error_rate": test_result.overall_error_rate,
                    "success_rate": test_result.overall_success_rate
                },
                "zone": test_result.zone,
                "stability_score": test_result.stability_score,
                "bottlenecks": test_result.bottlenecks,
                "recommendations": test_result.recommendations,
                "session_count": len(test_result.session_metrics),
                "sessions": [
                    {
                        "session_id": s.session_id,
                        "operations_count": s.operations_count,
                        "errors_count": s.errors_count,
                        "success_rate": s.success_rate,
                        "avg_cpu_percent": s.avg_cpu_percent,
                        "avg_memory_mb": s.avg_memory_mb,
                        "avg_response_time_ms": s.avg_response_time_ms,
                        "throughput_ops_per_sec": s.throughput_ops_per_sec
                    }
                    for s in test_result.session_metrics
                ]
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved test result: {result_file}")
        except Exception as e:
            logger.error(f"Error saving test result: {e}")

    def _print_test_summary(self, test_result: DynoTestResult):
        """Print test summary"""
        print()
        print("=" * 80)
        print(f"📊 DYNO TEST SUMMARY: {test_result.config.test_name}")
        print("=" * 80)
        print(f"   Concurrent Sessions: {test_result.config.concurrent_sessions}")
        print(f"   Duration: {test_result.duration_seconds:.1f}s")
        print()
        print("   SYSTEM METRICS:")
        print(f"      CPU: {test_result.system_cpu_avg:.1f}% avg, {test_result.system_cpu_max:.1f}% max")
        print(f"      Memory: {test_result.system_memory_avg_mb:.0f}MB avg, {test_result.system_memory_max_mb:.0f}MB max")
        print(f"      Disk I/O: {test_result.system_disk_io_avg_mb_per_sec:.2f}MB/s")
        print(f"      Network: {test_result.system_network_avg_mb_per_sec:.2f}MB/s")
        print()
        print("   PERFORMANCE METRICS:")
        print(f"      Throughput: {test_result.overall_throughput_ops_per_sec:.2f} ops/sec")
        print(f"      Avg Response Time: {test_result.overall_avg_response_time_ms:.1f}ms")
        print(f"      Error Rate: {test_result.overall_error_rate:.2f}%")
        print(f"      Success Rate: {test_result.overall_success_rate:.2f}%")
        print()
        print(f"   ZONE: {test_result.zone}")
        print(f"   STABILITY: {test_result.stability_score:.2%}")
        print()

        if test_result.bottlenecks:
            print("   ⚠️  BOTTLENECKS:")
            for bottleneck in test_result.bottlenecks:
                print(f"      - {bottleneck}")
            print()

        if test_result.recommendations:
            print("   💡 RECOMMENDATIONS:")
            for rec in test_result.recommendations:
                print(f"      {rec}")
            print()

        print("=" * 80)

    def run_goldilocks_suite(self) -> Dict[str, DynoTestResult]:
        """
        Run full Goldilocks suite: 3, 4, and 5 sessions

        Returns:
            Dict mapping session count to test result
        """
        logger.info("=" * 80)
        logger.info("🔧 RUNNING GOLDILOCKS SUITE")
        logger.info("=" * 80)
        logger.info("   Testing: 3 sessions (full bore), 4 sessions (Goldilocks), 5 sessions (nitrous)")
        logger.info("=" * 80)

        results = {}

        # Test 3 sessions (full bore)
        config_3 = DynoTestConfiguration(
            test_name="3 Sessions - Full Bore",
            concurrent_sessions=3,
            duration_seconds=300  # 5 minutes
        )
        result_3 = self.run_test(config_3)
        results[3] = result_3

        # Wait between tests
        logger.info("⏸️  Waiting 60s between tests...")
        time.sleep(60)

        # Test 4 sessions (Goldilocks)
        config_4 = DynoTestConfiguration(
            test_name="4 Sessions - Goldilocks Zone",
            concurrent_sessions=4,
            duration_seconds=300
        )
        result_4 = self.run_test(config_4)
        results[4] = result_4

        # Wait between tests
        logger.info("⏸️  Waiting 60s between tests...")
        time.sleep(60)

        # Test 5 sessions (nitrous)
        config_5 = DynoTestConfiguration(
            test_name="5 Sessions - Nitrous Mode",
            concurrent_sessions=5,
            duration_seconds=300
        )
        result_5 = self.run_test(config_5)
        results[5] = result_5

        # Generate comparison report
        self._generate_comparison_report(results)

        return results

    def _generate_comparison_report(self, results: Dict[int, DynoTestResult]):
        try:
            """Generate comparison report for all test results"""
            report_file = self.reports_dir / f"goldilocks_comparison_{int(time.time())}.json"

            comparison = {
                "generated": datetime.now().isoformat(),
                "tests": {
                    str(sessions): {
                        "zone": result.zone,
                        "stability_score": result.stability_score,
                        "system_cpu_avg": result.system_cpu_avg,
                        "system_cpu_max": result.system_cpu_max,
                        "system_memory_avg_mb": result.system_memory_avg_mb,
                        "system_memory_max_mb": result.system_memory_max_mb,
                        "throughput_ops_per_sec": result.overall_throughput_ops_per_sec,
                        "avg_response_time_ms": result.overall_avg_response_time_ms,
                        "error_rate": result.overall_error_rate,
                        "bottlenecks_count": len(result.bottlenecks)
                    }
                    for sessions, result in results.items()
                },
                "recommendation": self._determine_optimal_config(results)
            }

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 Comparison report saved: {report_file}")

            # Print comparison
            print()
            print("=" * 80)
            print("📊 GOLDILOCKS SUITE COMPARISON")
            print("=" * 80)
            for sessions, result in sorted(results.items()):
                print(f"   {sessions} Sessions: {result.zone} | Stability: {result.stability_score:.2%} | CPU: {result.system_cpu_avg:.1f}% | Throughput: {result.overall_throughput_ops_per_sec:.2f} ops/sec")
            print()
            print(f"   RECOMMENDATION: {comparison['recommendation']}")
            print("=" * 80)

        except Exception as e:
            self.logger.error(f"Error in _generate_comparison_report: {e}", exc_info=True)
            raise
    def _determine_optimal_config(self, results: Dict[int, DynoTestResult]) -> str:
        """Determine optimal configuration based on test results"""
        # Find best stability in GOLDILOCKS zone
        goldilocks_results = {s: r for s, r in results.items() if r.zone == "GOLDILOCKS"}

        if goldilocks_results:
            # Best is highest stability with good performance
            best = max(goldilocks_results.items(), key=lambda x: x[1].stability_score)
            return f"{best[0]} sessions (Goldilocks zone, stability: {best[1].stability_score:.2%})"

        # If no GOLDILOCKS, find least TOO_HOT
        hot_results = {s: r for s, r in results.items() if r.zone == "TOO_HOT"}
        if hot_results:
            best = min(hot_results.items(), key=lambda x: x[1].system_cpu_max)
            return f"{best[0]} sessions (least hot, but still TOO_HOT - reduce further)"

        # If all TOO_COLD, recommend highest
        cold_results = {s: r for s, r in results.items() if r.zone == "TOO_COLD"}
        if cold_results:
            best = max(cold_results.items(), key=lambda x: x[0])
            return f"{best[0]} sessions (all too cold, can increase further)"

        return "Unable to determine optimal configuration"


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Session DYNO Performance Test")
    parser.add_argument("--sessions", type=int, choices=[3, 4, 5], help="Number of concurrent sessions to test")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds (default: 300)")
    parser.add_argument("--suite", action="store_true", help="Run full Goldilocks suite (3, 4, 5 sessions)")

    args = parser.parse_args()

    dyno = AgentSessionDynoTest()

    if args.suite:
        # Run full suite
        results = dyno.run_goldilocks_suite()
    elif args.sessions:
        # Run single test
        config = DynoTestConfiguration(
            test_name=f"{args.sessions} Sessions Test",
            concurrent_sessions=args.sessions,
            duration_seconds=args.duration
        )
        result = dyno.run_test(config)
    else:
        # Default: run Goldilocks suite
        print("Running default Goldilocks suite (3, 4, 5 sessions)...")
        results = dyno.run_goldilocks_suite()


if __name__ == "__main__":


    main()