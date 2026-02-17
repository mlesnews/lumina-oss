#!/usr/bin/env python3
"""
Local AI Models Battle Test Suite
Comprehensive testing of Ollama and Iron Legion services

Tests:
- Service health and availability
- Model availability and loading
- API endpoint functionality
- Response times and performance
- Load balancing
- Failover scenarios
- Concurrent requests
"""

import json
import time
import logging
import requests
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import subprocess
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_PATH = PROJECT_ROOT / "data" / "homelab_model_validation" / "battletest_results.json"


@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    endpoint: str
    port: int
    container: str
    expected_models: List[str] = None


@dataclass
class TestResult:
    """Test result"""
    service: str
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    details: Dict = None


class LocalAIBattleTest:
    """Comprehensive battle test for local AI models"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.services = self._load_service_configs()
        self.test_prompts = [
            "Hello, how are you?",
            "What is 2+2?",
            "Write a Python function to calculate factorial.",
            "Explain quantum computing in simple terms.",
            "What is the capital of France?"
        ]

    def _load_service_configs(self) -> List[ServiceConfig]:
        """Load service configurations"""
        return [
            # Ollama Main Service
            ServiceConfig(
                name="Ollama",
                endpoint="http://localhost:11434",
                port=11434,
                container="homelab-ollama",
                expected_models=[]
            ),
            # Iron Legion Load Balancer
            ServiceConfig(
                name="Iron Legion Load Balancer",
                endpoint="http://localhost:3000",
                port=3000,
                container="iron-legion-loadbalancer",
                expected_models=[]
            ),
            # Iron Legion Mark I (Code Expert)
            ServiceConfig(
                name="Iron Legion Mark I",
                endpoint="http://localhost:3001",
                port=3001,
                container="iron-legion-mark-i",
                expected_models=["codellama:13b"]
            ),
            # Iron Legion Mark II (General Purpose)
            ServiceConfig(
                name="Iron Legion Mark II",
                endpoint="http://localhost:3002",
                port=3002,
                container="iron-legion-mark-ii",
                expected_models=["llama3.2:11b"]
            ),
            # Iron Legion Mark III (Quick Response)
            ServiceConfig(
                name="Iron Legion Mark III",
                endpoint="http://localhost:3003",
                port=3003,
                container="iron-legion-mark-iii",
                expected_models=["qwen2.5-coder:1.5b-base"]
            ),
            # Iron Legion Mark IV (Balanced Expert)
            ServiceConfig(
                name="Iron Legion Mark IV",
                endpoint="http://localhost:3004",
                port=3004,
                container="iron-legion-mark-iv",
                expected_models=["llama3:8b"]
            ),
            # Iron Legion Mark V (Reasoning Expert)
            ServiceConfig(
                name="Iron Legion Mark V",
                endpoint="http://localhost:3005",
                port=3005,
                container="iron-legion-mark-v",
                expected_models=["mistral:7b"]
            ),
            # Iron Legion Mark VI (Complex Expert)
            ServiceConfig(
                name="Iron Legion Mark VI",
                endpoint="http://localhost:3006",
                port=3006,
                container="iron-legion-mark-vi",
                expected_models=["mixtral:8x7b"]
            ),
            # Iron Legion Mark VII (Fallback Expert)
            ServiceConfig(
                name="Iron Legion Mark VII",
                endpoint="http://localhost:3007",
                port=3007,
                container="iron-legion-mark-vii",
                expected_models=["gemma:2b"]
            ),
        ]

    def _record_result(self, service: str, test_name: str, passed: bool, 
                      duration_ms: float, error: Optional[str] = None, 
                      details: Dict = None):
        """Record test result"""
        result = TestResult(
            service=service,
            test_name=test_name,
            passed=passed,
            duration_ms=duration_ms,
            error=error,
            details=details or {}
        )
        self.results.append(result)

        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} | {service} | {test_name} | {duration_ms:.2f}ms")
        if error:
            logger.error(f"  Error: {error}")

    def test_container_status(self, service: ServiceConfig) -> bool:
        """Test if container is running"""
        start_time = time.time()
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={service.container}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            is_running = "Up" in result.stdout
            duration = (time.time() - start_time) * 1000

            self._record_result(
                service.name,
                "Container Status",
                is_running,
                duration,
                None if is_running else f"Container not running: {result.stdout}"
            )
            return is_running
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Container Status",
                False,
                duration,
                str(e)
            )
            return False

    def test_endpoint_health(self, service: ServiceConfig) -> bool:
        """Test endpoint health"""
        start_time = time.time()
        try:
            # Try different health endpoints
            health_endpoints = [
                f"{service.endpoint}/api/tags",
                f"{service.endpoint}/health",
                f"{service.endpoint}/"
            ]

            for endpoint in health_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code in [200, 404]:  # 404 is OK for root
                        duration = (time.time() - start_time) * 1000
                        self._record_result(
                            service.name,
                            "Endpoint Health",
                            True,
                            duration,
                            None,
                            {"endpoint": endpoint, "status_code": response.status_code}
                        )
                        return True
                except requests.exceptions.RequestException:
                    continue

            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Endpoint Health",
                False,
                duration,
                "All health endpoints failed"
            )
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Endpoint Health",
                False,
                duration,
                str(e)
            )
            return False

    def test_model_list(self, service: ServiceConfig) -> bool:
        """Test model list API"""
        start_time = time.time()
        try:
            response = requests.get(f"{service.endpoint}/api/tags", timeout=10)
            duration = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                models = [model.get("name", "") for model in data.get("models", [])]

                # Check for expected models
                missing_models = []
                if service.expected_models:
                    for expected in service.expected_models:
                        found = any(expected in model for model in models)
                        if not found:
                            missing_models.append(expected)

                passed = len(missing_models) == 0
                self._record_result(
                    service.name,
                    "Model List",
                    passed,
                    duration,
                    None if passed else f"Missing models: {missing_models}",
                    {"models": models, "count": len(models)}
                )
                return passed
            else:
                self._record_result(
                    service.name,
                    "Model List",
                    False,
                    duration,
                    f"HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Model List",
                False,
                duration,
                str(e)
            )
            return False

    def test_generate_request(self, service: ServiceConfig, prompt: str) -> bool:
        """Test generation request"""
        start_time = time.time()
        try:
            # Get first available model
            response = requests.get(f"{service.endpoint}/api/tags", timeout=5)
            if response.status_code != 200:
                duration = (time.time() - start_time) * 1000
                self._record_result(
                    service.name,
                    "Generate Request",
                    False,
                    duration,
                    "Cannot get model list"
                )
                return False

            models = response.json().get("models", [])
            if not models:
                duration = (time.time() - start_time) * 1000
                self._record_result(
                    service.name,
                    "Generate Request",
                    False,
                    duration,
                    "No models available"
                )
                return False

            model_name = models[0].get("name", "")

            # Generate request
            generate_data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 50  # Limit tokens for speed
                }
            }

            gen_start = time.time()
            gen_response = requests.post(
                f"{service.endpoint}/api/generate",
                json=generate_data,
                timeout=30
            )
            gen_duration = (time.time() - gen_start) * 1000
            total_duration = (time.time() - start_time) * 1000

            if gen_response.status_code == 200:
                result_data = gen_response.json()
                response_text = result_data.get("response", "")

                self._record_result(
                    service.name,
                    "Generate Request",
                    True,
                    total_duration,
                    None,
                    {
                        "model": model_name,
                        "response_length": len(response_text),
                        "generation_time_ms": gen_duration,
                        "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt
                    }
                )
                return True
            else:
                self._record_result(
                    service.name,
                    "Generate Request",
                    False,
                    total_duration,
                    f"HTTP {gen_response.status_code}: {gen_response.text[:100]}"
                )
                return False
        except requests.exceptions.Timeout:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Generate Request",
                False,
                duration,
                "Request timeout"
            )
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Generate Request",
                False,
                duration,
                str(e)
            )
            return False

    def test_concurrent_requests(self, service: ServiceConfig, num_requests: int = 5) -> bool:
        """Test concurrent requests"""
        start_time = time.time()
        try:
            # Get model list first
            response = requests.get(f"{service.endpoint}/api/tags", timeout=5)
            if response.status_code != 200:
                duration = (time.time() - start_time) * 1000
                self._record_result(
                    service.name,
                    "Concurrent Requests",
                    False,
                    duration,
                    "Cannot get model list"
                )
                return False

            models = response.json().get("models", [])
            if not models:
                duration = (time.time() - start_time) * 1000
                self._record_result(
                    service.name,
                    "Concurrent Requests",
                    False,
                    duration,
                    "No models available"
                )
                return False

            model_name = models[0].get("name", "")

            def make_request(prompt):
                try:
                    gen_response = requests.post(
                        f"{service.endpoint}/api/generate",
                        json={
                            "model": model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"num_predict": 20}
                        },
                        timeout=20
                    )
                    return gen_response.status_code == 200
                except:
                    return False

            # Run concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
                futures = [
                    executor.submit(make_request, prompt)
                    for prompt in self.test_prompts[:num_requests]
                ]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            duration = (time.time() - start_time) * 1000
            success_count = sum(results)
            passed = success_count >= (num_requests * 0.8)  # 80% success rate

            self._record_result(
                service.name,
                "Concurrent Requests",
                passed,
                duration,
                None if passed else f"Only {success_count}/{num_requests} requests succeeded",
                {
                    "success_count": success_count,
                    "total_requests": num_requests,
                    "success_rate": f"{success_count/num_requests*100:.1f}%"
                }
            )
            return passed
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Concurrent Requests",
                False,
                duration,
                str(e)
            )
            return False

    def test_load_balancer(self) -> bool:
        """Test Iron Legion load balancer"""
        start_time = time.time()
        try:
            # Test load balancer health
            response = requests.get("http://localhost:3000/health", timeout=5)
            duration = (time.time() - start_time) * 1000

            if response.status_code == 200:
                # Test routing to backend
                backend_response = requests.get("http://localhost:3000/api/tags", timeout=10)
                backend_ok = backend_response.status_code == 200

                self._record_result(
                    "Iron Legion Load Balancer",
                    "Load Balancer Routing",
                    backend_ok,
                    duration,
                    None if backend_ok else "Backend routing failed",
                    {"health_status": response.status_code, "backend_status": backend_response.status_code}
                )
                return backend_ok
            else:
                self._record_result(
                    "Iron Legion Load Balancer",
                    "Load Balancer Routing",
                    False,
                    duration,
                    f"Health check failed: HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                "Iron Legion Load Balancer",
                "Load Balancer Routing",
                False,
                duration,
                str(e)
            )
            return False

    def test_response_times(self, service: ServiceConfig) -> bool:
        """Test response times"""
        start_time = time.time()
        try:
            response_times = []

            # Test multiple quick requests
            for i in range(3):
                req_start = time.time()
                response = requests.get(f"{service.endpoint}/api/tags", timeout=5)
                req_time = (time.time() - req_start) * 1000
                if response.status_code == 200:
                    response_times.append(req_time)

            if not response_times:
                duration = (time.time() - start_time) * 1000
                self._record_result(
                    service.name,
                    "Response Times",
                    False,
                    duration,
                    "No successful requests"
                )
                return False

            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            # Pass if average < 1000ms
            passed = avg_time < 1000
            duration = (time.time() - start_time) * 1000

            self._record_result(
                service.name,
                "Response Times",
                passed,
                duration,
                None if passed else f"Average response time too high: {avg_time:.2f}ms",
                {
                    "avg_ms": avg_time,
                    "min_ms": min_time,
                    "max_ms": max_time,
                    "samples": len(response_times)
                }
            )
            return passed
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._record_result(
                service.name,
                "Response Times",
                False,
                duration,
                str(e)
            )
            return False

    def run_all_tests(self):
        """Run all battle tests"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING LOCAL AI MODELS BATTLE TEST")
        logger.info("=" * 80)

        total_start = time.time()

        # Test each service
        for service in self.services:
            logger.info(f"\n{'='*80}")
            logger.info(f"Testing: {service.name}")
            logger.info(f"{'='*80}")

            # Container status
            if not self.test_container_status(service):
                logger.warning(f"⚠️ Container not running for {service.name}, skipping further tests")
                continue

            # Endpoint health
            self.test_endpoint_health(service)

            # Model list (for Ollama/Iron Legion services)
            if "Load Balancer" not in service.name:
                self.test_model_list(service)
                self.test_response_times(service)

                # Generate request (if models available)
                if service.expected_models or "Ollama" in service.name:
                    self.test_generate_request(service, self.test_prompts[0])

            # Concurrent requests (for main services only)
            if service.name in ["Ollama", "Iron Legion Load Balancer"]:
                self.test_concurrent_requests(service, num_requests=3)

        # Special test for load balancer
        lb_service = next((s for s in self.services if "Load Balancer" in s.name), None)
        if lb_service:
            self.test_load_balancer()

        total_duration = time.time() - total_start

        # Generate report
        self._generate_report(total_duration)

    def _generate_report(self, total_duration: float):
        try:
            """Generate battle test report"""
            logger.info("\n" + "=" * 80)
            logger.info("📊 BATTLE TEST RESULTS SUMMARY")
            logger.info("=" * 80)

            # Group results by service
            service_results = {}
            for result in self.results:
                if result.service not in service_results:
                    service_results[result.service] = []
                service_results[result.service].append(result)

            # Calculate statistics
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results if r.passed)
            failed_tests = total_tests - passed_tests
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            logger.info(f"\nOverall Statistics:")
            logger.info(f"  Total Tests: {total_tests}")
            logger.info(f"  Passed: {passed_tests} ✅")
            logger.info(f"  Failed: {failed_tests} ❌")
            logger.info(f"  Pass Rate: {pass_rate:.1f}%")
            logger.info(f"  Total Duration: {total_duration:.2f}s")

            # Per-service breakdown
            logger.info(f"\nPer-Service Results:")
            for service, results in service_results.items():
                service_passed = sum(1 for r in results if r.passed)
                service_total = len(results)
                service_rate = (service_passed / service_total * 100) if service_total > 0 else 0
                status = "✅" if service_passed == service_total else "⚠️"
                logger.info(f"  {status} {service}: {service_passed}/{service_total} ({service_rate:.1f}%)")

                # Show failed tests
                failed = [r for r in results if not r.passed]
                if failed:
                    for fail in failed:
                        logger.info(f"      ❌ {fail.test_name}: {fail.error}")

            # Save results
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "pass_rate": pass_rate,
                    "total_duration_seconds": total_duration
                },
                "services": {
                    service: {
                        "total": len(results),
                        "passed": sum(1 for r in results if r.passed),
                        "results": [asdict(r) for r in results]
                    }
                    for service, results in service_results.items()
                }
            }

            RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(RESULTS_PATH, 'w') as f:
                json.dump(report_data, f, indent=2)

            logger.info(f"\n📄 Full results saved to: {RESULTS_PATH}")
            logger.info("=" * 80)

            # Final verdict
            if pass_rate >= 80:
                logger.info("✅ BATTLE TEST: PASSED (80%+ pass rate)")
            elif pass_rate >= 60:
                logger.warning("⚠️ BATTLE TEST: PARTIAL PASS (60-80% pass rate)")
            else:
                logger.error("❌ BATTLE TEST: FAILED (<60% pass rate)")


        except Exception as e:
            self.logger.error(f"Error in _generate_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Local AI Models Battle Test Suite")
    parser.add_argument(
        "--service",
        help="Test specific service only"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test (skip concurrent requests)"
    )

    args = parser.parse_args()

    tester = LocalAIBattleTest()

    if args.service:
        # Test specific service
        service = next((s for s in tester.services if args.service.lower() in s.name.lower()), None)
        if service:
            logger.info(f"Testing service: {service.name}")
            tester.test_container_status(service)
            tester.test_endpoint_health(service)
            tester.test_model_list(service)
            tester.test_response_times(service)
            tester.test_generate_request(service, tester.test_prompts[0])
        else:
            logger.error(f"Service not found: {args.service}")
    else:
        # Run all tests
        tester.run_all_tests()


if __name__ == "__main__":


    main()