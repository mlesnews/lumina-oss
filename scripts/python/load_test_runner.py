#!/usr/bin/env python3
"""
Load Test Runner
Runs load tests against the API server

Tests API performance under load.
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LoadTestRunner")


class LoadTestRunner:
    """Runs load tests"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results_dir = project_root / "data" / "load_test_results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.access_token = None

    def authenticate(self) -> bool:
        """Authenticate and get access token"""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": "load_test_user",
                    "password": "load_test_password"
                },
                timeout=5
            )
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                return True
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")

        return False

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a single API request"""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests not available"}

        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        kwargs["headers"] = headers

        start_time = time.time()
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            elapsed_time = time.time() - start_time

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": elapsed_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": elapsed_time,
                "timestamp": datetime.now().isoformat()
            }

    def run_load_test(
        self,
        endpoint: str,
        method: str = "GET",
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        **request_kwargs
    ) -> Dict[str, Any]:
        """Run load test for an endpoint"""
        logger.info(f"Running load test: {endpoint} ({concurrent_users} users, {requests_per_user} requests each)")

        results = []
        start_time = time.time()

        def user_workload():
            user_results = []
            for _ in range(requests_per_user):
                result = self.make_request(method, endpoint, **request_kwargs)
                user_results.append(result)
            return user_results

        # Run concurrent requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_workload) for _ in range(concurrent_users)]

            for future in as_completed(futures):
                results.extend(future.result())

        total_time = time.time() - start_time
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.get("success"))
        failed_requests = total_requests - successful_requests

        response_times = [r["response_time"] for r in results if r.get("response_time")]
        response_times.sort()

        metrics = {
            "endpoint": endpoint,
            "method": method,
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "average": sum(response_times) / len(response_times) if response_times else 0,
                "p50": response_times[len(response_times) // 2] if response_times else 0,
                "p95": response_times[int(len(response_times) * 0.95)] if response_times else 0,
                "p99": response_times[int(len(response_times) * 0.99)] if response_times else 0
            }
        }

        return metrics

    def run_comprehensive_load_test(self) -> Dict[str, Any]:
        try:
            """Run comprehensive load test suite"""
            logger.info("Starting comprehensive load test suite...")

            # Authenticate first
            if not self.authenticate():
                logger.warning("Authentication failed - some tests may fail")

            test_results = {
                "test_date": datetime.now().isoformat(),
                "base_url": self.base_url,
                "endpoints": {}
            }

            # Test health endpoint (no auth required)
            test_results["endpoints"]["health"] = self.run_load_test(
                "/api/v1/system/health",
                method="GET",
                concurrent_users=20,
                requests_per_user=5
            )

            if self.access_token:
                # Test workflow endpoints
                test_results["endpoints"]["list_workflows"] = self.run_load_test(
                    "/api/v1/workflows",
                    method="GET",
                    concurrent_users=10,
                    requests_per_user=10
                )

                # Test chat endpoints
                test_results["endpoints"]["list_conversations"] = self.run_load_test(
                    "/api/v1/chat/conversations",
                    method="GET",
                    concurrent_users=10,
                    requests_per_user=10
                )

            # Calculate overall metrics
            all_response_times = []
            for endpoint_results in test_results["endpoints"].values():
                response_times = endpoint_results.get("response_times", {})
                if response_times.get("average"):
                    all_response_times.append(response_times["average"])

            test_results["overall_metrics"] = {
                "average_response_time": sum(all_response_times) / len(all_response_times) if all_response_times else 0,
                "total_endpoints_tested": len(test_results["endpoints"])
            }

            # Save results
            results_file = self.results_dir / f"load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2)

            logger.info(f"Load test complete. Results saved to: {results_file}")

            return test_results


        except Exception as e:
            self.logger.error(f"Error in run_comprehensive_load_test: {e}", exc_info=True)
            raise
def main():
    """Main load test function"""
    import argparse

    parser = argparse.ArgumentParser(description="Run load tests against API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--endpoint", help="Specific endpoint to test")
    parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    parser.add_argument("--requests", type=int, default=10, help="Requests per user")

    args = parser.parse_args()

    runner = LoadTestRunner(base_url=args.url)

    print("=" * 60)
    print("Load Test Runner")
    print("=" * 60)

    if args.endpoint:
        # Test specific endpoint
        result = runner.run_load_test(
            args.endpoint,
            concurrent_users=args.users,
            requests_per_user=args.requests
        )
        print(f"\nEndpoint: {result['endpoint']}")
        print(f"Success Rate: {result['success_rate']:.2%}")
        print(f"Requests/Second: {result['requests_per_second']:.2f}")
        print(f"Average Response Time: {result['response_times']['average']:.3f}s")
        print(f"P95 Response Time: {result['response_times']['p95']:.3f}s")
    else:
        # Run comprehensive test
        results = runner.run_comprehensive_load_test()
        print(f"\nTotal Endpoints Tested: {results['overall_metrics']['total_endpoints_tested']}")
        print(f"Overall Average Response Time: {results['overall_metrics']['average_response_time']:.3f}s")

    print("=" * 60)


if __name__ == "__main__":


    main()