#!/usr/bin/env python3
"""
ULTRON Virtual Cluster - Burn-In Test with Tokens/Sec Gauge & Metrics/Analytics

Real-time performance testing with:
- AI tokens per second monitoring
- Real-time gauges and metrics
- Comprehensive analytics
- Load testing across all nodes
- Performance benchmarking

Tags: #BURN_IN #PERFORMANCE #METRICS #ANALYTICS #TOKENS_PER_SEC #GAUGE #ULTRON #VIRTUAL_CLUSTER @JARVIS @BONES @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import urllib.request
import urllib.error
import urllib.parse

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("UltronClusterBurnIn")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("UltronClusterBurnIn")


@dataclass
class TokenMetrics:
    """Token generation metrics"""
    tokens_generated: int = 0
    tokens_per_second: float = 0.0
    tokens_per_minute: float = 0.0
    total_time_seconds: float = 0.0
    average_tokens_per_second: float = 0.0
    peak_tokens_per_second: float = 0.0
    min_tokens_per_second: float = float('inf')


@dataclass
class NodePerformanceMetrics:
    """Performance metrics for a single node"""
    node_name: str
    endpoint: str
    requests_sent: int = 0
    requests_succeeded: int = 0
    requests_failed: int = 0
    total_tokens: int = 0
    total_response_time_ms: float = 0.0
    average_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0
    tokens_per_second: float = 0.0
    success_rate: float = 0.0
    errors: List[str] = None


@dataclass
class BurnInAnalytics:
    """Comprehensive burn-in analytics"""
    test_duration_seconds: float = 0.0
    total_requests: int = 0
    total_tokens: int = 0
    cluster_tokens_per_second: float = 0.0
    cluster_average_response_time_ms: float = 0.0
    cluster_success_rate: float = 0.0
    node_metrics: Dict[str, NodePerformanceMetrics] = None
    time_series_data: List[Dict[str, Any]] = None


class RealTimeGauge:
    """Real-time gauge display for tokens/sec"""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.token_history = deque(maxlen=window_size)
        self.time_history = deque(maxlen=window_size)
        self.lock = threading.Lock()

    def update(self, tokens: int, timestamp: float):
        """Update gauge with new token count"""
        with self.lock:
            self.token_history.append(tokens)
            self.time_history.append(timestamp)

    def get_current_tps(self) -> float:
        """Get current tokens per second"""
        with self.lock:
            if len(self.token_history) < 2:
                return 0.0

            tokens_diff = sum(self.token_history) - (self.token_history[0] if len(self.token_history) > 0 else 0)
            time_diff = self.time_history[-1] - self.time_history[0] if len(self.time_history) > 1 else 1.0

            if time_diff <= 0:
                return 0.0

            return tokens_diff / time_diff

    def display_gauge(self, label: str, current_tps: float, max_tps: float = 100.0):
        """Display ASCII gauge"""
        percentage = min(100, (current_tps / max_tps) * 100) if max_tps > 0 else 0
        bar_length = 50
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        return f"{label:25} [{bar}] {current_tps:6.2f} tokens/sec ({percentage:5.1f}%)"


class UltronClusterBurnInTest:
    """Burn-in test with real-time metrics and analytics"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize burn-in test"""
        self.project_root = Path(project_root) if project_root else script_dir.parent.parent
        self.nodes = {
            "ultron": {
                "name": "ULTRON Standalone",
                "endpoint": "http://localhost:11434",
                "model": "qwen2.5:72b"
            },
            "kaiju": {
                "name": "KAIJU/Iron Legion",
                "endpoint": "http://<NAS_IP>:3001",
                "model": "codellama:13b"
            },
            "falc": {
                "name": "FALC/Millennium Falcon",
                "endpoint": "http://localhost:11436",
                "model": "qwen2.5:72b"
            }
        }

        self.gauges = {node: RealTimeGauge() for node in self.nodes.keys()}
        self.metrics = {node: NodePerformanceMetrics(node_name=config["name"], endpoint=config["endpoint"])
                       for node, config in self.nodes.items()}
        self.analytics = BurnInAnalytics()
        self.analytics.node_metrics = {}
        self.analytics.time_series_data = []

        self.running = False
        self.test_start_time = None

    def run_burnin_test(
        self,
        duration_seconds: int = 60,
        requests_per_second: float = 1.0,
        max_tokens: int = 100,
        nodes_to_test: Optional[List[str]] = None
    ) -> BurnInAnalytics:
        """Run burn-in test with real-time monitoring"""
        logger.info("="*80)
        logger.info("🔥 ULTRON Virtual Cluster - BURN-IN TEST")
        logger.info("="*80)
        logger.info(f"Duration: {duration_seconds} seconds")
        logger.info(f"Request Rate: {requests_per_second} req/sec")
        logger.info(f"Max Tokens per Request: {max_tokens}")
        logger.info("")

        if nodes_to_test is None:
            nodes_to_test = list(self.nodes.keys())

        self.test_start_time = time.time()
        self.running = True

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_gauges, daemon=True)
        monitor_thread.start()

        # Start load generation threads for each node
        load_threads = []
        for node in nodes_to_test:
            if node in self.nodes:
                thread = threading.Thread(
                    target=self._generate_load,
                    args=(node, duration_seconds, requests_per_second, max_tokens),
                    daemon=True
                )
                thread.start()
                load_threads.append(thread)

        # Wait for test completion
        time.sleep(duration_seconds)
        self.running = False

        # Wait for threads to complete
        for thread in load_threads:
            thread.join(timeout=5)

        # Calculate final analytics
        self.analytics.test_duration_seconds = time.time() - self.test_start_time
        self._calculate_analytics()

        # Display final results
        self._display_final_results()

        return self.analytics

    def _generate_load(self, node: str, duration: int, req_per_sec: float, max_tokens: int):
        """Generate load on a specific node"""
        node_config = self.nodes[node]
        metrics = self.metrics[node]
        gauge = self.gauges[node]

        end_time = time.time() + duration
        request_interval = 1.0 / req_per_sec if req_per_sec > 0 else 1.0

        while time.time() < end_time and self.running:
            request_start = time.time()

            try:
                # Generate completion request
                prompt = "Generate a short response about artificial intelligence."
                response_data = self._send_completion_request(
                    node_config["endpoint"],
                    node_config["model"],
                    prompt,
                    max_tokens
                )

                request_time = (time.time() - request_start) * 1000
                tokens_generated = response_data.get("tokens_generated", 0)

                # Update metrics
                metrics.requests_sent += 1
                metrics.requests_succeeded += 1
                metrics.total_tokens += tokens_generated
                metrics.total_response_time_ms += request_time
                metrics.average_response_time_ms = metrics.total_response_time_ms / metrics.requests_succeeded
                metrics.min_response_time_ms = min(metrics.min_response_time_ms, request_time)
                metrics.max_response_time_ms = max(metrics.max_response_time_ms, request_time)

                # Update gauge
                gauge.update(tokens_generated, time.time())

                # Calculate tokens per second for this node
                elapsed = time.time() - self.test_start_time
                if elapsed > 0:
                    metrics.tokens_per_second = metrics.total_tokens / elapsed

            except Exception as e:
                metrics.requests_sent += 1
                metrics.requests_failed += 1
                if metrics.errors is None:
                    metrics.errors = []
                metrics.errors.append(str(e))

            # Calculate success rate
            if metrics.requests_sent > 0:
                metrics.success_rate = (metrics.requests_succeeded / metrics.requests_sent) * 100

            # Sleep to maintain request rate
            sleep_time = request_interval - (time.time() - request_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _send_completion_request(self, endpoint: str, model: str, prompt: str, max_tokens: int) -> Dict[str, Any]:
        try:
            """Send completion request to Ollama API"""
            api_url = f"{endpoint}/api/generate"

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }

            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())

                # Extract token count from response
                response_text = data.get("response", "")
                # Estimate tokens (rough: 1 token ≈ 4 characters)
                tokens_generated = len(response_text) // 4

                return {
                    "tokens_generated": tokens_generated,
                    "response": response_text,
                    "model": data.get("model", model)
                }

        except Exception as e:
            self.logger.error(f"Error in _send_completion_request: {e}", exc_info=True)
            raise
    def _monitor_gauges(self):
        """Monitor and display real-time gauges"""
        while self.running:
            time.sleep(1)  # Update every second

            # Clear screen (ANSI escape codes)
            print("\033[2J\033[H", end="")  # Clear screen and move to top

            # Display header
            elapsed = time.time() - self.test_start_time if self.test_start_time else 0
            print("="*80)
            print(f"🔥 ULTRON Virtual Cluster - BURN-IN TEST (Elapsed: {elapsed:.1f}s)")
            print("="*80)
            print()

            # Display gauges for each node
            print("📊 REAL-TIME TOKENS/SEC GAUGES:")
            print()

            max_tps = max(
                (gauge.get_current_tps() for gauge in self.gauges.values()),
                default=100.0
            ) * 1.2  # Add 20% headroom

            for node, gauge in self.gauges.items():
                current_tps = gauge.get_current_tps()
                node_name = self.nodes[node]["name"]
                print(gauge.display_gauge(node_name, current_tps, max_tps))

            print()
            print("="*80)
            print("METRICS SUMMARY:")
            print("="*80)

            # Display metrics summary
            for node, metrics in self.metrics.items():
                node_name = self.nodes[node]["name"]
                print(f"\n{node_name}:")
                print(f"  Requests: {metrics.requests_succeeded}/{metrics.requests_sent} "
                      f"({metrics.success_rate:.1f}% success)")
                print(f"  Tokens: {metrics.total_tokens:,} total, "
                      f"{metrics.tokens_per_second:.2f} tokens/sec")
                print(f"  Response Time: avg={metrics.average_response_time_ms:.2f}ms, "
                      f"min={metrics.min_response_time_ms:.2f}ms, "
                      f"max={metrics.max_response_time_ms:.2f}ms")

            print()
            print("="*80)
            print("Press Ctrl+C to stop early")
            print("="*80)

    def _calculate_analytics(self):
        """Calculate comprehensive analytics"""
        # Aggregate cluster metrics
        self.analytics.total_requests = sum(m.requests_sent for m in self.metrics.values())
        self.analytics.total_tokens = sum(m.total_tokens for m in self.metrics.values())

        if self.analytics.test_duration_seconds > 0:
            self.analytics.cluster_tokens_per_second = (
                self.analytics.total_tokens / self.analytics.test_duration_seconds
            )

        # Calculate average response time
        total_response_time = sum(m.total_response_time_ms for m in self.metrics.values())
        total_successful_requests = sum(m.requests_succeeded for m in self.metrics.values())
        if total_successful_requests > 0:
            self.analytics.cluster_average_response_time_ms = (
                total_response_time / total_successful_requests
            )

        # Calculate success rate
        if self.analytics.total_requests > 0:
            total_succeeded = sum(m.requests_succeeded for m in self.metrics.values())
            self.analytics.cluster_success_rate = (
                (total_succeeded / self.analytics.total_requests) * 100
            )

        # Store node metrics
        for node, metrics in self.metrics.items():
            self.analytics.node_metrics[node] = metrics

    def _display_final_results(self):
        """Display final test results"""
        logger.info("")
        logger.info("="*80)
        logger.info("📊 BURN-IN TEST RESULTS")
        logger.info("="*80)
        logger.info("")
        logger.info(f"Test Duration: {self.analytics.test_duration_seconds:.2f} seconds")
        logger.info(f"Total Requests: {self.analytics.total_requests:,}")
        logger.info(f"Total Tokens Generated: {self.analytics.total_tokens:,}")
        logger.info(f"Cluster Tokens/Sec: {self.analytics.cluster_tokens_per_second:.2f}")
        logger.info(f"Cluster Avg Response Time: {self.analytics.cluster_average_response_time_ms:.2f}ms")
        logger.info(f"Cluster Success Rate: {self.analytics.cluster_success_rate:.1f}%")
        logger.info("")
        logger.info("Node Performance:")
        logger.info("")

        for node, metrics in self.metrics.items():
            logger.info(f"  {metrics.node_name}:")
            logger.info(f"    Requests: {metrics.requests_succeeded:,}/{metrics.requests_sent:,} "
                       f"({metrics.success_rate:.1f}% success)")
            logger.info(f"    Tokens: {metrics.total_tokens:,} total, "
                       f"{metrics.tokens_per_second:.2f} tokens/sec")
            logger.info(f"    Response Time: avg={metrics.average_response_time_ms:.2f}ms, "
                       f"min={metrics.min_response_time_ms:.2f}ms, "
                       f"max={metrics.max_response_time_ms:.2f}ms")
            if metrics.errors:
                logger.info(f"    Errors: {len(metrics.errors)}")
            logger.info("")

    def save_analytics_report(self, output_path: Optional[Path] = None) -> Path:
        try:
            """Save analytics report to file"""
            if output_path is None:
                output_path = self.project_root / "data" / "burnin_tests" / f"ultron_cluster_burnin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to serializable format
            report = {
                "test_date": datetime.now().isoformat(),
                "analytics": {
                    "test_duration_seconds": self.analytics.test_duration_seconds,
                    "total_requests": self.analytics.total_requests,
                    "total_tokens": self.analytics.total_tokens,
                    "cluster_tokens_per_second": self.analytics.cluster_tokens_per_second,
                    "cluster_average_response_time_ms": self.analytics.cluster_average_response_time_ms,
                    "cluster_success_rate": self.analytics.cluster_success_rate
                },
                "node_metrics": {}
            }

            for node, metrics in self.metrics.items():
                report["node_metrics"][node] = {
                    "node_name": metrics.node_name,
                    "endpoint": metrics.endpoint,
                    "requests_sent": metrics.requests_sent,
                    "requests_succeeded": metrics.requests_succeeded,
                    "requests_failed": metrics.requests_failed,
                    "total_tokens": metrics.total_tokens,
                    "tokens_per_second": metrics.tokens_per_second,
                    "average_response_time_ms": metrics.average_response_time_ms,
                    "min_response_time_ms": metrics.min_response_time_ms,
                    "max_response_time_ms": metrics.max_response_time_ms,
                    "success_rate": metrics.success_rate,
                    "errors": metrics.errors or []
                }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 Analytics report saved: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_analytics_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ULTRON Virtual Cluster - Burn-In Test with Tokens/Sec Gauge & Metrics"
    )
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (default: 60)")
    parser.add_argument("--rate", type=float, default=1.0, help="Requests per second (default: 1.0)")
    parser.add_argument("--max-tokens", type=int, default=100, help="Max tokens per request (default: 100)")
    parser.add_argument("--nodes", type=str, nargs="+", help="Nodes to test (ultron, kaiju, falc)")
    parser.add_argument("--save-report", action="store_true", help="Save analytics report")
    parser.add_argument("--output", type=str, help="Output path for analytics report")

    args = parser.parse_args()

    burnin_test = UltronClusterBurnInTest()

    try:
        analytics = burnin_test.run_burnin_test(
            duration_seconds=args.duration,
            requests_per_second=args.rate,
            max_tokens=args.max_tokens,
            nodes_to_test=args.nodes
        )

        if args.save_report or args.output:
            output_path = Path(args.output) if args.output else None
            report_path = burnin_test.save_analytics_report(output_path)
            print(f"\n📄 Analytics report saved: {report_path}")

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Test interrupted by user")
        burnin_test.running = False
        if args.save_report:
            report_path = burnin_test.save_analytics_report()
            print(f"\n📄 Partial analytics report saved: {report_path}")


if __name__ == "__main__":


    main()