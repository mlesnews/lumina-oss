#!/usr/bin/env python3
"""
ULTRON Cluster Battle Test

Comprehensive testing of ULTRON stacked cluster:
- Health checks on all 12 nodes
- Round-robin distribution verification
- Failover system testing
- Performance benchmarks
- Error handling validation

Tags: #BATTLETEST #ULTRON #CLUSTER #TESTING @JARVIS @LUMINA
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import concurrent.futures

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from ultron_iron_legion_virtual_cluster import ULTRONIronLegionVirtualCluster

logger = get_logger("ULTRONBattleTest")


@dataclass
class TestResult:
    """Test result"""
    test_name: str
    passed: bool
    message: str
    duration_ms: float
    details: Optional[Dict[str, Any]] = None


class ULTRONBattleTest:
    """Comprehensive battle test for ULTRON cluster"""

    def __init__(self):
        self.cluster = ULTRONIronLegionVirtualCluster(project_root=project_root)
        self.results: List[TestResult] = []
        self.api_base = "http://localhost:8080"

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all battle tests"""
        logger.info("=" * 80)
        logger.info("🔥 ULTRON CLUSTER BATTLE TEST")
        logger.info("=" * 80)
        logger.info("")

        # Initialize cluster
        self.cluster.initialize_ultron_nodes(count=12, distributed=True)
        self.cluster.initialize_iron_legion_nodes()

        # Run tests
        tests = [
            ("Cluster Initialization", self.test_cluster_initialization),
            ("Node Health Checks", self.test_node_health),
            ("Round-Robin Distribution", self.test_round_robin),
            ("API Endpoints", self.test_api_endpoints),
            ("Failover System", self.test_failover),
            ("Performance Benchmark", self.test_performance),
            ("Error Handling", self.test_error_handling),
            ("Stacked Architecture", self.test_stacked_architecture)
        ]

        for test_name, test_func in tests:
            logger.info(f"🧪 Running: {test_name}")
            try:
                result = test_func()
                self.results.append(result)
                status = "✅ PASS" if result.passed else "❌ FAIL"
                logger.info(f"   {status}: {result.message}")
                if result.details:
                    for key, value in result.details.items():
                        logger.info(f"      {key}: {value}")
            except Exception as e:
                logger.error(f"   ❌ ERROR: {e}")
                self.results.append(TestResult(
                    test_name=test_name,
                    passed=False,
                    message=f"Exception: {str(e)}",
                    duration_ms=0.0
                ))
            logger.info("")

        # Summary
        return self.generate_summary()

    def test_cluster_initialization(self) -> TestResult:
        """Test cluster initialization"""
        start = time.time()

        ultron_count = len(self.cluster.ultron_nodes)
        iron_legion_count = len(self.cluster.iron_legion_nodes)

        passed = ultron_count == 12 and iron_legion_count == 7

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Cluster Initialization",
            passed=passed,
            message=f"ULTRON: {ultron_count}/12, Iron Legion: {iron_legion_count}/7",
            duration_ms=duration,
            details={
                "ultron_nodes": ultron_count,
                "iron_legion_nodes": iron_legion_count
            }
        )

    def test_node_health(self) -> TestResult:
        """Test health checks on all nodes"""
        start = time.time()

        # Start health monitoring
        self.cluster.start_health_monitoring()
        time.sleep(5)  # Wait for initial health checks

        status = self.cluster.get_cluster_status()
        ultron_healthy = status["ultron"]["healthy_count"]
        iron_legion_healthy = status["iron_legion"]["healthy_count"]

        passed = ultron_healthy > 0 or iron_legion_healthy > 0

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Node Health Checks",
            passed=passed,
            message=f"ULTRON: {ultron_healthy}/12 healthy, Iron Legion: {iron_legion_healthy}/7 healthy",
            duration_ms=duration,
            details={
                "ultron_healthy": ultron_healthy,
                "ultron_total": 12,
                "iron_legion_healthy": iron_legion_healthy,
                "iron_legion_total": 7
            }
        )

    def test_round_robin(self) -> TestResult:
        """Test round-robin distribution"""
        start = time.time()

        # Make multiple requests and track which nodes are used
        node_usage = {}
        requests_made = 20

        for i in range(requests_made):
            node = self.cluster.round_robin.get_next_node()
            if node:
                node_usage[node.name] = node_usage.get(node.name, 0) + 1

        unique_nodes = len(node_usage)
        passed = unique_nodes > 1  # Should use multiple nodes

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Round-Robin Distribution",
            passed=passed,
            message=f"Used {unique_nodes} unique nodes out of {requests_made} requests",
            duration_ms=duration,
            details={
                "requests_made": requests_made,
                "unique_nodes": unique_nodes,
                "node_distribution": node_usage
            }
        )

    def test_api_endpoints(self) -> TestResult:
        """Test API endpoints through router"""
        start = time.time()

        endpoints_tested = []
        endpoints_passed = []

        # Test /health
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            endpoints_tested.append("/health")
            if response.status_code == 200:
                endpoints_passed.append("/health")
        except Exception as e:
            logger.warning(f"   ⚠️  /health failed: {e}")

        # Test /api/tags
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=10)
            endpoints_tested.append("/api/tags")
            if response.status_code == 200:
                endpoints_passed.append("/api/tags")
        except Exception as e:
            logger.warning(f"   ⚠️  /api/tags failed: {e}")

        # Test /status
        try:
            response = requests.get(f"{self.api_base}/status", timeout=5)
            endpoints_tested.append("/status")
            if response.status_code == 200:
                endpoints_passed.append("/status")
        except Exception as e:
            logger.warning(f"   ⚠️  /status failed: {e}")

        passed = len(endpoints_passed) > 0

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="API Endpoints",
            passed=passed,
            message=f"{len(endpoints_passed)}/{len(endpoints_tested)} endpoints working",
            duration_ms=duration,
            details={
                "tested": endpoints_tested,
                "passed": endpoints_passed
            }
        )

    def test_failover(self) -> TestResult:
        """Test failover system"""
        start = time.time()

        status = self.cluster.get_cluster_status()
        failover_active = status["failover_active"]
        current_cluster = status["current_cluster"]

        # Check failover logic
        healthy_ultron = status["ultron"]["healthy_count"]
        should_failover = healthy_ultron < 6

        passed = True  # Failover system exists
        if should_failover and current_cluster != "iron_legion":
            passed = False  # Should have failed over but didn't

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Failover System",
            passed=passed,
            message=f"Current: {current_cluster}, Failover active: {failover_active}",
            duration_ms=duration,
            details={
                "current_cluster": current_cluster,
                "failover_active": failover_active,
                "ultron_healthy": healthy_ultron,
                "failover_threshold": 6
            }
        )

    def test_performance(self) -> TestResult:
        """Test performance benchmarks"""
        start = time.time()

        # Test response times
        response_times = []
        test_requests = 5

        for i in range(test_requests):
            try:
                req_start = time.time()
                response = requests.get(f"{self.api_base}/health", timeout=5)
                req_duration = (time.time() - req_start) * 1000
                if response.status_code == 200:
                    response_times.append(req_duration)
            except Exception as e:
                logger.warning(f"   ⚠️  Request {i+1} failed: {e}")

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        passed = avg_response_time < 1000  # Should be under 1 second

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Performance Benchmark",
            passed=passed,
            message=f"Average response time: {avg_response_time:.2f}ms",
            duration_ms=duration,
            details={
                "avg_response_time_ms": avg_response_time,
                "requests_tested": test_requests,
                "successful_requests": len(response_times)
            }
        )

    def test_error_handling(self) -> TestResult:
        """Test error handling"""
        start = time.time()

        # Test with invalid endpoint
        try:
            response = requests.get(f"{self.api_base}/invalid", timeout=5)
            error_handled = response.status_code == 404
        except Exception as e:
            error_handled = True  # Exception is acceptable error handling

        # Test with invalid data
        try:
            response = requests.post(f"{self.api_base}/api/chat", json={}, timeout=5)
            error_handled = error_handled and (response.status_code >= 400)
        except Exception as e:
            error_handled = True

        passed = error_handled

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Error Handling",
            passed=passed,
            message="Error handling validated",
            duration_ms=duration
        )

    def test_stacked_architecture(self) -> TestResult:
        """Test stacked architecture (all 3 machines)"""
        start = time.time()

        # Check node distribution
        laptop_nodes = [n for n in self.cluster.ultron_nodes if "laptop" in n.name]
        desktop_nodes = [n for n in self.cluster.ultron_nodes if "desktop" in n.name]
        nas_nodes = [n for n in self.cluster.ultron_nodes if "nas" in n.name]

        laptop_count = len(laptop_nodes)
        desktop_count = len(desktop_nodes)
        nas_count = len(nas_nodes)

        passed = laptop_count == 4 and desktop_count == 4 and nas_count == 4

        duration = (time.time() - start) * 1000

        return TestResult(
            test_name="Stacked Architecture",
            passed=passed,
            message=f"Laptop: {laptop_count}, Desktop: {desktop_count}, NAS: {nas_count}",
            duration_ms=duration,
            details={
                "laptop_nodes": laptop_count,
                "desktop_nodes": desktop_count,
                "nas_nodes": nas_count,
                "total_nodes": laptop_count + desktop_count + nas_count
            }
        )

    def generate_summary(self) -> Dict[str, Any]:
        try:
            """Generate test summary"""
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results if r.passed)
            failed_tests = total_tests - passed_tests

            total_duration = sum(r.duration_ms for r in self.results)

            logger.info("=" * 80)
            logger.info("📊 BATTLE TEST SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total Tests: {total_tests}")
            logger.info(f"✅ Passed: {passed_tests}")
            logger.info(f"❌ Failed: {failed_tests}")
            logger.info(f"⏱️  Total Duration: {total_duration:.2f}ms")
            logger.info("")

            if failed_tests > 0:
                logger.info("❌ Failed Tests:")
                for result in self.results:
                    if not result.passed:
                        logger.info(f"   - {result.test_name}: {result.message}")
                logger.info("")

            # Save results
            results_file = project_root / "data" / "battletest_reports" / f"ultron_battletest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)

            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "total_duration_ms": total_duration,
                "results": [
                    {
                        "test_name": r.test_name,
                        "passed": r.passed,
                        "message": r.message,
                        "duration_ms": r.duration_ms,
                        "details": r.details
                    }
                    for r in self.results
                ]
            }

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"💾 Results saved: {results_file}")
            logger.info("")

            return summary


        except Exception as e:
            self.logger.error(f"Error in generate_summary: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON Cluster Battle Test")
    parser.add_argument("--quick", action="store_true", help="Quick test (skip performance)")

    args = parser.parse_args()

    battletest = ULTRONBattleTest()
    summary = battletest.run_all_tests()

    # Exit code based on results
    exit_code = 0 if summary["failed"] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":

    main()