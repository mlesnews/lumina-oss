#!/usr/bin/env python3
"""
#BATTLETEST - ULTRON & IRON LEGION AI Clusters
                    -LUM THE MODERN

Comprehensive battle testing of both ULTRON and IRON LEGION AI clusters.
Tests availability, performance, throughput, and reliability.

@SCOTTY @PEAK @LUMINA @DT -LUM_THE_MODERN
"""

import sys
import json
import time
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("BattleTest")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("BattleTest")

try:
    import requests
except ImportError:
    logger.error("❌ requests library not installed. Install with: pip install requests")
    sys.exit(1)


class TestStatus(Enum):
    """Test status"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️  WARN"
    SKIP = "⏭️  SKIP"


@dataclass
class TestResult:
    """Test result"""
    name: str
    status: TestStatus
    latency_ms: float = 0.0
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusterNode:
    """Cluster node definition"""
    name: str
    endpoint: str
    model: Optional[str] = None
    role: str = "node"
    priority: int = 5


class BattleTestULTRONIronLegion:
    """
    Battle test both ULTRON and IRON LEGION AI clusters.

    Tests:
    - Endpoint availability
    - Model availability
    - Response times
    - Throughput
    - Error rates
    - Load handling
    - Failover capabilities
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.results: List[TestResult] = []

        # ULTRON Cluster nodes
        self.ultron_nodes = [
            ClusterNode("ULTRON Local", "http://localhost:11434", "qwen2.5:72b", "primary", 1),
            ClusterNode("ULTRON KAIJU", "http://<NAS_PRIMARY_IP>:11434", "llama3.2:11b", "secondary", 2),
            ClusterNode("ULTRON KUBE", "http://<NAS_PRIMARY_IP>:8000/v1", "qwen2.5:72b", "kube", 1)
        ]

        # IRON LEGION Cluster nodes (7 models)
        self.iron_legion_nodes = [
            ClusterNode("Mark I - Code", "http://<NAS_IP>:3001", "codellama:13b", "expert", 1),
            ClusterNode("Mark II - General", "http://<NAS_IP>:3002", "llama3.2:11b", "expert", 2),
            ClusterNode("Mark III - Quick", "http://<NAS_IP>:3003", "qwen2.5-coder:1.5b-base", "expert", 3),
            ClusterNode("Mark IV - Balanced", "http://<NAS_IP>:3004", "llama3:8b", "expert", 2),
            ClusterNode("Mark V - Reasoning", "http://<NAS_IP>:3005", "mistral:7b", "expert", 1),
            ClusterNode("Mark VI - Complex", "http://<NAS_IP>:3006", "mixtral:8x7b", "expert", 1),
            ClusterNode("Mark VII - Fallback", "http://<NAS_IP>:3007", "gemma:2b", "expert", 4)
        ]

        # Test prompts
        self.test_prompts = [
            "Hello, how are you?",
            "Write a Python function to calculate fibonacci numbers.",
            "Explain quantum computing in simple terms.",
            "What is the capital of France?",
            "Write a SQL query to find all users created in the last 30 days."
        ]

        logger.info("=" * 80)
        logger.info("⚔️  #BATTLETEST - ULTRON & IRON LEGION AI CLUSTERS")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info(f"   ULTRON Nodes: {len(self.ultron_nodes)}")
        logger.info(f"   IRON LEGION Nodes: {len(self.iron_legion_nodes)}")
        logger.info("=" * 80)

    def check_endpoint_health(self, node: ClusterNode) -> TestResult:
        """Check if endpoint is healthy"""
        start_time = time.time()

        try:
            # Try health check endpoint
            health_url = f"{node.endpoint}/api/tags" if "ollama" in node.endpoint or ":11434" in node.endpoint or ":300" in node.endpoint else f"{node.endpoint}/health"

            response = requests.get(health_url, timeout=5)
            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return TestResult(
                    name=f"{node.name} Health Check",
                    status=TestStatus.PASS,
                    latency_ms=latency_ms,
                    details={"status_code": response.status_code, "endpoint": node.endpoint}
                )
            else:
                return TestResult(
                    name=f"{node.name} Health Check",
                    status=TestStatus.FAIL,
                    latency_ms=latency_ms,
                    error=f"HTTP {response.status_code}",
                    details={"status_code": response.status_code}
                )

        except requests.exceptions.Timeout:
            return TestResult(
                name=f"{node.name} Health Check",
                status=TestStatus.FAIL,
                latency_ms=5000.0,
                error="Timeout (5s)",
                details={"timeout": True}
            )

        except requests.exceptions.ConnectionError:
            return TestResult(
                name=f"{node.name} Health Check",
                status=TestStatus.FAIL,
                latency_ms=(time.time() - start_time) * 1000,
                error="Connection refused",
                details={"connection_error": True}
            )

        except Exception as e:
            return TestResult(
                name=f"{node.name} Health Check",
                status=TestStatus.FAIL,
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e),
                details={"exception": str(e)}
            )

    def test_model_inference(self, node: ClusterNode, prompt: str) -> TestResult:
        """Test model inference"""
        start_time = time.time()

        try:
            # Determine API format
            if "/v1" in node.endpoint:
                # OpenAI-compatible API
                api_url = f"{node.endpoint}/chat/completions"
                payload = {
                    "model": node.model or "default",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.7
                }
            else:
                # Ollama API
                api_url = f"{node.endpoint}/api/generate"
                payload = {
                    "model": node.model or "default",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 100}
                }

            response = requests.post(api_url, json=payload, timeout=30)
            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    name=f"{node.name} Inference",
                    status=TestStatus.PASS,
                    latency_ms=latency_ms,
                    details={
                        "response_length": len(str(data)),
                        "model": node.model,
                        "prompt_length": len(prompt)
                    }
                )
            else:
                return TestResult(
                    name=f"{node.name} Inference",
                    status=TestStatus.FAIL,
                    latency_ms=latency_ms,
                    error=f"HTTP {response.status_code}",
                    details={"status_code": response.status_code, "response": response.text[:200]}
                )

        except requests.exceptions.Timeout:
            return TestResult(
                name=f"{node.name} Inference",
                status=TestStatus.FAIL,
                latency_ms=30000.0,
                error="Timeout (30s)",
                details={"timeout": True}
            )

        except Exception as e:
            return TestResult(
                name=f"{node.name} Inference",
                status=TestStatus.FAIL,
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e),
                details={"exception": str(e)}
            )

    def test_cluster_throughput(self, nodes: List[ClusterNode], concurrent_requests: int = 5) -> TestResult:
        """Test cluster throughput with concurrent requests"""
        logger.info(f"   Testing throughput with {concurrent_requests} concurrent requests...")

        start_time = time.time()
        prompt = self.test_prompts[0]
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            for node in nodes:
                future = executor.submit(self.test_model_inference, node, prompt)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(TestResult(
                        name="Throughput Test",
                        status=TestStatus.FAIL,
                        error=str(e)
                    ))

        total_time = (time.time() - start_time) * 1000
        passed = sum(1 for r in results if r.status == TestStatus.PASS)
        failed = len(results) - passed

        avg_latency = sum(r.latency_ms for r in results if r.latency_ms > 0) / max(len([r for r in results if r.latency_ms > 0]), 1)
        throughput = (passed / total_time * 1000) if total_time > 0 else 0

        return TestResult(
            name="Throughput Test",
            status=TestStatus.PASS if passed > 0 else TestStatus.FAIL,
            latency_ms=total_time,
            details={
                "concurrent_requests": concurrent_requests,
                "passed": passed,
                "failed": failed,
                "total_nodes": len(nodes),
                "avg_latency_ms": avg_latency,
                "throughput_rps": throughput
            }
        )

    def test_ultron_cluster(self) -> List[TestResult]:
        """Test ULTRON cluster"""
        logger.info("\n" + "=" * 80)
        logger.info("🚀 TESTING ULTRON CLUSTER")
        logger.info("=" * 80)

        results = []

        # Test each node
        for node in self.ultron_nodes:
            logger.info(f"\n📡 Testing: {node.name} ({node.endpoint})")

            # Health check
            health_result = self.check_endpoint_health(node)
            results.append(health_result)
            logger.info(f"   {health_result.status.value}: {health_result.name} ({health_result.latency_ms:.2f}ms)")

            if health_result.status == TestStatus.PASS:
                # Test inference
                inference_result = self.test_model_inference(node, self.test_prompts[0])
                results.append(inference_result)
                logger.info(f"   {inference_result.status.value}: {inference_result.name} ({inference_result.latency_ms:.2f}ms)")

        # Test throughput
        available_nodes = [n for n in self.ultron_nodes if any(r.name == f"{n.name} Health Check" and r.status == TestStatus.PASS for r in results)]
        if available_nodes:
            throughput_result = self.test_cluster_throughput(available_nodes, concurrent_requests=3)
            results.append(throughput_result)
            logger.info(f"\n   {throughput_result.status.value}: {throughput_result.name}")
            logger.info(f"      Throughput: {throughput_result.details.get('throughput_rps', 0):.2f} req/s")
            logger.info(f"      Avg Latency: {throughput_result.details.get('avg_latency_ms', 0):.2f}ms")

        return results

    def test_iron_legion_cluster(self) -> List[TestResult]:
        """Test IRON LEGION cluster"""
        logger.info("\n" + "=" * 80)
        logger.info("⚔️  TESTING IRON LEGION CLUSTER")
        logger.info("=" * 80)

        results = []

        # Test each Mark
        for node in self.iron_legion_nodes:
            logger.info(f"\n📡 Testing: {node.name} ({node.endpoint})")

            # Health check
            health_result = self.check_endpoint_health(node)
            results.append(health_result)
            logger.info(f"   {health_result.status.value}: {health_result.name} ({health_result.latency_ms:.2f}ms)")

            if health_result.status == TestStatus.PASS:
                # Test inference
                inference_result = self.test_model_inference(node, self.test_prompts[0])
                results.append(inference_result)
                logger.info(f"   {inference_result.status.value}: {inference_result.name} ({inference_result.latency_ms:.2f}ms)")

        # Test throughput
        available_nodes = [n for n in self.iron_legion_nodes if any(r.name == f"{n.name} Health Check" and r.status == TestStatus.PASS for r in results)]
        if available_nodes:
            throughput_result = self.test_cluster_throughput(available_nodes, concurrent_requests=5)
            results.append(throughput_result)
            logger.info(f"\n   {throughput_result.status.value}: {throughput_result.name}")
            logger.info(f"      Throughput: {throughput_result.details.get('throughput_rps', 0):.2f} req/s")
            logger.info(f"      Avg Latency: {throughput_result.details.get('avg_latency_ms', 0):.2f}ms")

        return results

    def generate_report(self, ultron_results: List[TestResult], iron_legion_results: List[TestResult]) -> Dict[str, Any]:
        """Generate battle test report"""
        all_results = ultron_results + iron_legion_results

        passed = sum(1 for r in all_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in all_results if r.status == TestStatus.FAIL)
        warned = sum(1 for r in all_results if r.status == TestStatus.WARN)

        ultron_passed = sum(1 for r in ultron_results if r.status == TestStatus.PASS)
        ultron_failed = sum(1 for r in ultron_results if r.status == TestStatus.FAIL)

        iron_legion_passed = sum(1 for r in iron_legion_results if r.status == TestStatus.PASS)
        iron_legion_failed = sum(1 for r in iron_legion_results if r.status == TestStatus.FAIL)

        avg_latency = sum(r.latency_ms for r in all_results if r.latency_ms > 0) / max(len([r for r in all_results if r.latency_ms > 0]), 1)

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(all_results),
                "passed": passed,
                "failed": failed,
                "warned": warned,
                "pass_rate": (passed / len(all_results) * 100) if all_results else 0,
                "avg_latency_ms": avg_latency
            },
            "ultron_cluster": {
                "total_tests": len(ultron_results),
                "passed": ultron_passed,
                "failed": ultron_failed,
                "pass_rate": (ultron_passed / len(ultron_results) * 100) if ultron_results else 0,
                "results": [{
                    "name": r.name,
                    "status": r.status.value,
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                    "details": r.details
                } for r in ultron_results]
            },
            "iron_legion_cluster": {
                "total_tests": len(iron_legion_results),
                "passed": iron_legion_passed,
                "failed": iron_legion_failed,
                "pass_rate": (iron_legion_passed / len(iron_legion_results) * 100) if iron_legion_results else 0,
                "results": [{
                    "name": r.name,
                    "status": r.status.value,
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                    "details": r.details
                } for r in iron_legion_results]
            }
        }

        return report

    def battletest_all(self) -> Dict[str, Any]:
        try:
            """Run complete battle test"""
            logger.info("\n" + "=" * 80)
            logger.info("⚔️  STARTING #BATTLETEST")
            logger.info("=" * 80)

            # Test ULTRON
            ultron_results = self.test_ultron_cluster()

            # Test IRON LEGION
            iron_legion_results = self.test_iron_legion_cluster()

            # Generate report
            report = self.generate_report(ultron_results, iron_legion_results)

            # Display summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 #BATTLETEST RESULTS")
            logger.info("=" * 80)
            logger.info(f"\n🎯 OVERALL SUMMARY")
            logger.info(f"   Total Tests: {report['summary']['total_tests']}")
            logger.info(f"   ✅ Passed: {report['summary']['passed']}")
            logger.info(f"   ❌ Failed: {report['summary']['failed']}")
            logger.info(f"   Pass Rate: {report['summary']['pass_rate']:.1f}%")
            logger.info(f"   Avg Latency: {report['summary']['avg_latency_ms']:.2f}ms")

            logger.info(f"\n🚀 ULTRON CLUSTER")
            logger.info(f"   Tests: {report['ultron_cluster']['total_tests']}")
            logger.info(f"   ✅ Passed: {report['ultron_cluster']['passed']}")
            logger.info(f"   ❌ Failed: {report['ultron_cluster']['failed']}")
            logger.info(f"   Pass Rate: {report['ultron_cluster']['pass_rate']:.1f}%")

            logger.info(f"\n⚔️  IRON LEGION CLUSTER")
            logger.info(f"   Tests: {report['iron_legion_cluster']['total_tests']}")
            logger.info(f"   ✅ Passed: {report['iron_legion_cluster']['passed']}")
            logger.info(f"   ❌ Failed: {report['iron_legion_cluster']['failed']}")
            logger.info(f"   Pass Rate: {report['iron_legion_cluster']['pass_rate']:.1f}%")

            # Save report
            report_path = self.project_root / "data" / "battletest_reports"
            report_path.mkdir(parents=True, exist_ok=True)

            report_file = report_path / f"battletest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"\n💾 Report saved: {report_file}")
            logger.info("=" * 80)

            return report


        except Exception as e:
            self.logger.error(f"Error in battletest_all: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="#BATTLETEST ULTRON & IRON LEGION")
    parser.add_argument("--ultron-only", action="store_true", help="Test ULTRON only")
    parser.add_argument("--iron-legion-only", action="store_true", help="Test IRON LEGION only")

    args = parser.parse_args()

    battletest = BattleTestULTRONIronLegion()

    if args.ultron_only:
        results = battletest.test_ultron_cluster()
        logger.info(f"\n✅ ULTRON battle test complete: {sum(1 for r in results if r.status == TestStatus.PASS)}/{len(results)} passed")
    elif args.iron_legion_only:
        results = battletest.test_iron_legion_cluster()
        logger.info(f"\n✅ IRON LEGION battle test complete: {sum(1 for r in results if r.status == TestStatus.PASS)}/{len(results)} passed")
    else:
        report = battletest.battletest_all()

        if report['summary']['pass_rate'] >= 80:
            print("\n✅ #BATTLETEST PASSED!")
            sys.exit(0)
        else:
            print("\n⚠️  #BATTLETEST WARNINGS - Some tests failed")
            sys.exit(1)


if __name__ == "__main__":


    main()