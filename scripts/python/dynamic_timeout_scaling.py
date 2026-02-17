#!/usr/bin/env python3
"""
Dynamic Timeout Scaling - Account for LUMINA System Latency

"SO I'M NOTICING THAT IF I GIVE IT A 'MOMENT' THAT @ASK SENDS AND RETRIES
THAT ENCOUNTER THE COMMUNICATION TIMEOUTS, IS JUST US NOT ACCOUNTING FOR
THE LATENCY OF THE LUMINA PROJECT AND ITS SYSTEMS. AND NOT MITIGATING FOR IT.
/FIX PLEASE? @DYNAMIC-SCALING OF TIMEOUTS? NOT A NEW CONCEPT FOR US EH?"

Dynamic timeout scaling based on:
- Measured LUMINA system latency
- Historical latency patterns
- System load
- Adaptive retry with exponential backoff
"""

import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from collections import deque
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DynamicTimeoutScaling")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class LatencyMeasurement:
    """Latency measurement for a system/operation"""
    system: str
    operation: str
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class TimeoutConfig:
    """Dynamic timeout configuration"""
    base_timeout: float  # Base timeout in seconds
    min_timeout: float  # Minimum timeout
    max_timeout: float  # Maximum timeout
    latency_multiplier: float = 3.0  # Multiply measured latency by this
    adaptive_factor: float = 1.5  # Additional adaptive factor
    retry_backoff_base: float = 2.0  # Exponential backoff base
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DynamicTimeoutScaling:
    """
    Dynamic Timeout Scaling - Account for LUMINA System Latency

    Measures latency, adapts timeouts, and provides retry logic with exponential backoff.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Dynamic Timeout Scaling"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("DynamicTimeoutScaling")

        # Latency measurements (rolling window)
        self.latency_history: Dict[str, deque] = {}  # system -> deque of LatencyMeasurement
        self.history_window_size = 100  # Keep last 100 measurements per system

        # Timeout configurations per system
        self.timeout_configs: Dict[str, TimeoutConfig] = {}

        # Default configuration
        self.default_config = TimeoutConfig(
            base_timeout=30.0,  # 30 seconds base
            min_timeout=10.0,  # Minimum 10 seconds
            max_timeout=300.0,  # Maximum 5 minutes
            latency_multiplier=3.0,
            adaptive_factor=1.5,
            retry_backoff_base=2.0,
            max_retries=3
        )

        # Data storage
        self.data_dir = self.project_root / "data" / "dynamic_timeout_scaling"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Persistent memory files
        self.latency_history_file = self.data_dir / "latency_history.json"
        self.timeout_configs_file = self.data_dir / "timeout_configs.json"
        self.feedback_loop_file = self.data_dir / "feedback_loop.json"

        # Load persistent memory
        self._load_persistent_memory()

        # Feedback loop state (cloud <-> local)
        self.feedback_loop_state: Dict[str, Any] = {
            "cloud_sync": False,
            "local_sync": False,
            "last_cloud_sync": None,
            "last_local_sync": None,
            "feedback_cycles": 0
        }

        self.logger.info("⏱️  Dynamic Timeout Scaling initialized")
        self.logger.info("   Accounting for LUMINA system latency")
        self.logger.info("   Adaptive timeout scaling enabled")
        self.logger.info("   Exponential backoff retry enabled")
        self.logger.info("   Persistent memory enabled (A Hobbit's Journey)")
        self.logger.info("   Feedback loop: Cloud <-> Local AI Models")
        self.logger.info("   'It gives us courage.' - @GANDALF")

    def measure_latency(self, system: str, operation: str, 
                       func: Callable, *args, **kwargs) -> tuple[Any, LatencyMeasurement]:
        """
        Measure latency of an operation and record it

        Returns:
            (result, latency_measurement)
        """
        start_time = time.time()
        success = True
        result = None
        error = None

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            success = False
            error = e
            raise
        finally:
            latency_ms = (time.time() - start_time) * 1000  # Convert to milliseconds

            measurement = LatencyMeasurement(
                system=system,
                operation=operation,
                latency_ms=latency_ms,
                success=success
            )

            # Store in history
            if system not in self.latency_history:
                self.latency_history[system] = deque(maxlen=self.history_window_size)

            self.latency_history[system].append(measurement)
            self._save_latency_measurement(measurement)

            self.logger.debug(f"  ⏱️  Latency: {system}/{operation}: {latency_ms:.2f}ms (success: {success})")

        return result, measurement

    def get_dynamic_timeout(self, system: str, operation: str = "default") -> float:
        """
        Get dynamic timeout based on measured latency

        Timeout = max(
            min_timeout,
            min(
                max_timeout,
                base_timeout * adaptive_factor * (avg_latency_ms / 1000) * latency_multiplier
            )
        )
        """
        config = self.timeout_configs.get(system, self.default_config)

        # Get average latency for this system
        avg_latency_ms = self._get_average_latency(system)

        if avg_latency_ms is None:
            # No history, use base timeout
            timeout = config.base_timeout
            self.logger.debug(f"  ⏱️  No latency history for {system}, using base timeout: {timeout}s")
        else:
            # Calculate dynamic timeout
            # Convert latency from ms to seconds, multiply by multiplier, add adaptive factor
            latency_seconds = (avg_latency_ms / 1000.0) * config.latency_multiplier
            timeout = config.base_timeout * config.adaptive_factor * (1 + latency_seconds)

            # Clamp to min/max
            timeout = max(config.min_timeout, min(config.max_timeout, timeout))

            self.logger.debug(f"  ⏱️  Dynamic timeout for {system}: {timeout:.2f}s (avg latency: {avg_latency_ms:.2f}ms)")

        return timeout

    def _get_average_latency(self, system: str, window: int = 10) -> Optional[float]:
        """Get average latency for a system (last N successful measurements)"""
        if system not in self.latency_history:
            return None

        history = self.latency_history[system]
        successful = [m.latency_ms for m in history if m.success][-window:]

        if not successful:
            return None

        return statistics.mean(successful)

    def execute_with_retry(self, system: str, operation: str,
                          func: Callable, *args, timeout: Optional[float] = None,
                          **kwargs) -> Any:
        """
        Execute function with dynamic timeout and exponential backoff retry

        Returns:
            Result of function call
        """
        config = self.timeout_configs.get(system, self.default_config)

        # Get dynamic timeout if not provided
        if timeout is None:
            timeout = self.get_dynamic_timeout(system, operation)

        last_error = None

        for attempt in range(config.max_retries):
            try:
                # Measure latency and execute
                result, measurement = self.measure_latency(system, operation, func, *args, **kwargs)

                # Success - return result
                if measurement.success:
                    if attempt > 0:
                        self.logger.info(f"  ✅ {system}/{operation} succeeded on attempt {attempt + 1}")
                    return result

            except Exception as e:
                last_error = e

                if attempt < config.max_retries - 1:
                    # Calculate exponential backoff
                    backoff_delay = config.retry_backoff_base ** attempt

                    # Adjust timeout based on latency
                    adjusted_timeout = timeout * (1 + (backoff_delay / 10))

                    self.logger.warning(
                        f"  ⚠️  {system}/{operation} failed (attempt {attempt + 1}/{config.max_retries}): {e}"
                    )
                    self.logger.info(f"     Retrying in {backoff_delay:.2f}s (timeout: {adjusted_timeout:.2f}s)")

                    time.sleep(backoff_delay)

                    # Update timeout for next attempt
                    timeout = adjusted_timeout
                else:
                    self.logger.error(f"  ❌ {system}/{operation} failed after {config.max_retries} attempts")
                    raise

        # If we get here, all retries failed
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"{system}/{operation} failed after {config.max_retries} attempts")

    def configure_system(self, system: str, config: TimeoutConfig) -> None:
        """Configure timeout settings for a specific system"""
        self.timeout_configs[system] = config
        self.logger.info(f"  ⚙️  Configured {system}: base={config.base_timeout}s, min={config.min_timeout}s, max={config.max_timeout}s")

    def get_statistics(self, system: Optional[str] = None) -> Dict[str, Any]:
        """Get latency and timeout statistics"""
        if system:
            systems = [system]
        else:
            systems = list(self.latency_history.keys())

        stats = {}
        for sys in systems:
            if sys not in self.latency_history:
                continue

            history = list(self.latency_history[sys])
            if not history:
                continue

            successful = [m.latency_ms for m in history if m.success]
            failed = [m.latency_ms for m in history if not m.success]

            config = self.timeout_configs.get(sys, self.default_config)
            current_timeout = self.get_dynamic_timeout(sys)

            stats[sys] = {
                "total_measurements": len(history),
                "successful": len(successful),
                "failed": len(failed),
                "avg_latency_ms": statistics.mean(successful) if successful else None,
                "median_latency_ms": statistics.median(successful) if successful else None,
                "max_latency_ms": max(successful) if successful else None,
                "min_latency_ms": min(successful) if successful else None,
                "current_timeout": current_timeout,
                "base_timeout": config.base_timeout,
                "min_timeout": config.min_timeout,
                "max_timeout": config.max_timeout
            }

        return stats

    def _save_latency_measurement(self, measurement: LatencyMeasurement) -> None:
        try:
            """Save latency measurement to file and update persistent memory"""
            # Save individual measurement
            measurement_file = self.data_dir / "latency_measurements" / f"{measurement.system}_{int(measurement.timestamp.timestamp())}.json"
            measurement_file.parent.mkdir(parents=True, exist_ok=True)
            with open(measurement_file, 'w', encoding='utf-8') as f:
                json.dump(measurement.to_dict(), f, indent=2)

            # Update persistent memory (save history periodically)
            self._save_persistent_memory()

        except Exception as e:
            self.logger.error(f"Error in _save_latency_measurement: {e}", exc_info=True)
            raise
    def _load_persistent_memory(self) -> None:
        """
        Load persistent memory from disk

        "A Hobbit's Journey. Because it gives us courage." - @GANDALF
        """
        # Load latency history
        if self.latency_history_file.exists():
            try:
                with open(self.latency_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Restore latency history
                    for system, measurements in data.get('latency_history', {}).items():
                        if system not in self.latency_history:
                            self.latency_history[system] = deque(maxlen=self.history_window_size)
                        for m_data in measurements[-self.history_window_size:]:  # Keep last N
                            measurement = LatencyMeasurement(
                                system=m_data['system'],
                                operation=m_data['operation'],
                                latency_ms=m_data['latency_ms'],
                                timestamp=datetime.fromisoformat(m_data['timestamp']),
                                success=m_data['success']
                            )
                            self.latency_history[system].append(measurement)
                self.logger.info(f"  📚 Loaded persistent memory: {sum(len(h) for h in self.latency_history.values())} measurements")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Failed to load latency history: {e}")

        # Load timeout configs
        if self.timeout_configs_file.exists():
            try:
                with open(self.timeout_configs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for system, config_data in data.get('timeout_configs', {}).items():
                        self.timeout_configs[system] = TimeoutConfig(**config_data)
                self.logger.info(f"  ⚙️  Loaded timeout configs: {len(self.timeout_configs)} systems")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Failed to load timeout configs: {e}")

        # Load feedback loop state
        if self.feedback_loop_file.exists():
            try:
                with open(self.feedback_loop_file, 'r', encoding='utf-8') as f:
                    self.feedback_loop_state = json.load(f)
                self.logger.info(f"  🔄 Loaded feedback loop state: {self.feedback_loop_state.get('feedback_cycles', 0)} cycles")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Failed to load feedback loop state: {e}")

    def _save_persistent_memory(self) -> None:
        """
        Save persistent memory to disk

        "A Hobbit's Journey. Because it gives us courage." - @GANDALF
        """
        try:
            # Save latency history (periodically, not every measurement)
            if len(self.latency_history) > 0:
                history_data = {
                    'latency_history': {
                        system: [
                            {
                                'system': m.system,
                                'operation': m.operation,
                                'latency_ms': m.latency_ms,
                                'timestamp': m.timestamp.isoformat(),
                                'success': m.success
                            }
                            for m in list(history)[-self.history_window_size:]  # Keep last N
                        ]
                        for system, history in self.latency_history.items()
                    },
                    'last_saved': datetime.now().isoformat()
                }
                with open(self.latency_history_file, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, indent=2)

            # Save timeout configs
            configs_data = {
                'timeout_configs': {
                    system: config.to_dict()
                    for system, config in self.timeout_configs.items()
                },
                'last_saved': datetime.now().isoformat()
            }
            with open(self.timeout_configs_file, 'w', encoding='utf-8') as f:
                json.dump(configs_data, f, indent=2)

            # Save feedback loop state
            self.feedback_loop_state['last_saved'] = datetime.now().isoformat()
            with open(self.feedback_loop_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_loop_state, f, indent=2)

        except Exception as e:
            self.logger.warning(f"  ⚠️  Failed to save persistent memory: {e}")

    def sync_to_cloud(self, cloud_endpoint: Optional[str] = None) -> bool:
        """
        Sync latency measurements and timeout configs to cloud

        Feedback loop: Local -> Cloud
        "A Hobbit's Journey. Because it gives us courage." - @GANDALF
        """
        try:
            # Prepare data for cloud sync
            sync_data = {
                'latency_history': {
                    system: [
                        {
                            'system': m.system,
                            'operation': m.operation,
                            'latency_ms': m.latency_ms,
                            'timestamp': m.timestamp.isoformat(),
                            'success': m.success
                        }
                        for m in list(history)[-50:]  # Last 50 per system
                    ]
                    for system, history in self.latency_history.items()
                },
                'timeout_configs': {
                    system: config.to_dict()
                    for system, config in self.timeout_configs.items()
                },
                'local_timestamp': datetime.now().isoformat()
            }

            # If cloud endpoint provided, sync via HTTP
            if cloud_endpoint and REQUESTS_AVAILABLE:
                try:
                    response = requests.post(
                        f"{cloud_endpoint}/api/timeout-scaling/sync",
                        json=sync_data,
                        timeout=30
                    )
                    if response.status_code == 200:
                        self.feedback_loop_state['cloud_sync'] = True
                        self.feedback_loop_state['last_cloud_sync'] = datetime.now().isoformat()
                        self._save_persistent_memory()
                        self.logger.info("  ☁️  Synced to cloud successfully")
                        return True
                except Exception as e:
                    self.logger.warning(f"  ⚠️  Cloud sync failed: {e}")

            # Otherwise, save to local file for later sync
            cloud_sync_file = self.data_dir / "cloud_sync_pending.json"
            with open(cloud_sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, indent=2)

            self.logger.info("  📤 Prepared for cloud sync (pending)")
            return True

        except Exception as e:
            self.logger.error(f"  ❌ Failed to sync to cloud: {e}")
            return False

    def sync_from_cloud(self, cloud_endpoint: Optional[str] = None) -> bool:
        """
        Sync latency measurements and timeout configs from cloud

        Feedback loop: Cloud -> Local
        "A Hobbit's Journey. Because it gives us courage." - @GANDALF
        """
        try:
            # If cloud endpoint provided, fetch from cloud
            if cloud_endpoint and REQUESTS_AVAILABLE:
                try:
                    response = requests.get(
                        f"{cloud_endpoint}/api/timeout-scaling/sync",
                        timeout=30
                    )
                    if response.status_code == 200:
                        cloud_data = response.json()
                        # Merge cloud data with local
                        self._merge_cloud_data(cloud_data)
                        self.feedback_loop_state['local_sync'] = True
                        self.feedback_loop_state['last_local_sync'] = datetime.now().isoformat()
                        self.feedback_loop_state['feedback_cycles'] = self.feedback_loop_state.get('feedback_cycles', 0) + 1
                        self._save_persistent_memory()
                        self.logger.info("  ☁️  Synced from cloud successfully")
                        return True
                except Exception as e:
                    self.logger.warning(f"  ⚠️  Cloud sync failed: {e}")

            # Otherwise, check for local sync file
            cloud_sync_file = self.data_dir / "cloud_sync_received.json"
            if cloud_sync_file.exists():
                with open(cloud_sync_file, 'r', encoding='utf-8') as f:
                    cloud_data = json.load(f)
                self._merge_cloud_data(cloud_data)
                self.feedback_loop_state['local_sync'] = True
                self.feedback_loop_state['last_local_sync'] = datetime.now().isoformat()
                self.feedback_loop_state['feedback_cycles'] = self.feedback_loop_state.get('feedback_cycles', 0) + 1
                self._save_persistent_memory()
                self.logger.info("  📥 Synced from cloud file")
                return True

            return False

        except Exception as e:
            self.logger.error(f"  ❌ Failed to sync from cloud: {e}")
            return False

    def _merge_cloud_data(self, cloud_data: Dict[str, Any]) -> None:
        """Merge cloud data with local data"""
        # Merge latency history
        for system, measurements in cloud_data.get('latency_history', {}).items():
            if system not in self.latency_history:
                self.latency_history[system] = deque(maxlen=self.history_window_size)

            for m_data in measurements:
                measurement = LatencyMeasurement(
                    system=m_data['system'],
                    operation=m_data['operation'],
                    latency_ms=m_data['latency_ms'],
                    timestamp=datetime.fromisoformat(m_data['timestamp']),
                    success=m_data['success']
                )
                # Add if not already present (avoid duplicates)
                if len(self.latency_history[system]) == 0 or \
                   self.latency_history[system][-1].timestamp != measurement.timestamp:
                    self.latency_history[system].append(measurement)

        # Merge timeout configs (cloud takes precedence if newer)
        for system, config_data in cloud_data.get('timeout_configs', {}).items():
            self.timeout_configs[system] = TimeoutConfig(**config_data)

        self.logger.info(f"  🔄 Merged cloud data: {len(cloud_data.get('latency_history', {}))} systems")

    def feedback_loop_cycle(self, cloud_endpoint: Optional[str] = None) -> bool:
        """
        Complete feedback loop cycle: Local -> Cloud -> Local

        "A Hobbit's Journey. Because it gives us courage." - @GANDALF
        """
        self.logger.info("  🔄 Starting feedback loop cycle...")
        self.logger.info("     'A Hobbit's Journey. Because it gives us courage.' - @GANDALF")

        # Sync to cloud
        sync_to_success = self.sync_to_cloud(cloud_endpoint)

        # Sync from cloud
        sync_from_success = self.sync_from_cloud(cloud_endpoint)

        if sync_to_success and sync_from_success:
            self.logger.info(f"  ✅ Feedback loop cycle complete: {self.feedback_loop_state['feedback_cycles']} cycles")
            return True
        else:
            self.logger.warning("  ⚠️  Feedback loop cycle incomplete")
            return False


# Global instance
_timeout_scaler: Optional[DynamicTimeoutScaling] = None


def get_timeout_scaler() -> DynamicTimeoutScaling:
    """Get global timeout scaler instance"""
    global _timeout_scaler
    if _timeout_scaler is None:
        _timeout_scaler = DynamicTimeoutScaling()
    return _timeout_scaler


# Requests wrapper with dynamic timeout scaling
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


def requests_with_dynamic_timeout(method: str, system: str, operation: str,
                                  url: str, timeout: Optional[float] = None,
                                  **kwargs) -> Any:
    """
    Execute requests method with dynamic timeout scaling

    Args:
        method: HTTP method (get, post, put, delete, etc.)
        system: System name for timeout configuration
        operation: Operation name for timeout configuration
        url: Request URL
        timeout: Optional fixed timeout (if None, uses dynamic timeout)
        **kwargs: Additional requests arguments

    Returns:
        Response object
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests library not available")

    scaler = get_timeout_scaler()

    # Get dynamic timeout if not provided
    if timeout is None:
        timeout = scaler.get_dynamic_timeout(system, operation)

    # Get the requests method
    req_method = getattr(requests, method.lower())

    # Execute with retry logic
    def make_request():
        return req_method(url, timeout=timeout, **kwargs)

    try:
        return scaler.execute_with_retry(system, operation, make_request, timeout=timeout)
    except Exception as e:
        logger.warning(f"  ⚠️  Request failed: {method} {url} - {e}")
        raise


# Convenience functions
def get_with_dynamic_timeout(system: str, operation: str, url: str,
                             timeout: Optional[float] = None, **kwargs) -> Any:
    """GET request with dynamic timeout"""
    return requests_with_dynamic_timeout("get", system, operation, url, timeout, **kwargs)


def post_with_dynamic_timeout(system: str, operation: str, url: str,
                              timeout: Optional[float] = None, **kwargs) -> Any:
    """POST request with dynamic timeout"""
    return requests_with_dynamic_timeout("post", system, operation, url, timeout, **kwargs)


def put_with_dynamic_timeout(system: str, operation: str, url: str,
                             timeout: Optional[float] = None, **kwargs) -> Any:
    """PUT request with dynamic timeout"""
    return requests_with_dynamic_timeout("put", system, operation, url, timeout, **kwargs)


def delete_with_dynamic_timeout(system: str, operation: str, url: str,
                                timeout: Optional[float] = None, **kwargs) -> Any:
    """DELETE request with dynamic timeout"""
    return requests_with_dynamic_timeout("delete", system, operation, url, timeout, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic Timeout Scaling - Account for LUMINA System Latency")
    parser.add_argument("--configure", nargs=5, metavar=("SYSTEM", "BASE", "MIN", "MAX", "MULTIPLIER"),
                       help="Configure system timeout (base, min, max, multiplier)")
    parser.add_argument("--get-timeout", nargs=2, metavar=("SYSTEM", "OPERATION"),
                       help="Get dynamic timeout for system/operation")
    parser.add_argument("--statistics", type=str, nargs='?', const="", help="Get statistics (optional system)")
    parser.add_argument("--sync-to-cloud", type=str, help="Sync to cloud (cloud endpoint URL)")
    parser.add_argument("--sync-from-cloud", type=str, help="Sync from cloud (cloud endpoint URL)")
    parser.add_argument("--feedback-loop", type=str, help="Complete feedback loop cycle (cloud endpoint URL)")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    scaler = DynamicTimeoutScaling()

    if args.configure:
        system, base, min_to, max_to, multiplier = args.configure
        config = TimeoutConfig(
            base_timeout=float(base),
            min_timeout=float(min_to),
            max_timeout=float(max_to),
            latency_multiplier=float(multiplier)
        )
        scaler.configure_system(system, config)
        if args.json:
            print(json.dumps({"configured": system, "config": config.to_dict()}, indent=2))
        else:
            print(f"\n⚙️  Configured {system}")
            print(f"   Base Timeout: {config.base_timeout}s")
            print(f"   Min Timeout: {config.min_timeout}s")
            print(f"   Max Timeout: {config.max_timeout}s")
            print(f"   Latency Multiplier: {config.latency_multiplier}x")

    elif args.get_timeout:
        system, operation = args.get_timeout
        timeout = scaler.get_dynamic_timeout(system, operation)
        if args.json:
            print(json.dumps({"system": system, "operation": operation, "timeout": timeout}, indent=2))
        else:
            print(f"\n⏱️  Dynamic Timeout")
            print(f"   System: {system}")
            print(f"   Operation: {operation}")
            print(f"   Timeout: {timeout:.2f}s")

    elif args.statistics is not None:
        system = args.statistics if args.statistics else None
        stats = scaler.get_statistics(system)
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n📊 Dynamic Timeout Scaling Statistics")
            for sys, sys_stats in stats.items():
                print(f"\n   System: {sys}")
                print(f"   Total Measurements: {sys_stats['total_measurements']}")
                print(f"   Successful: {sys_stats['successful']}")
                print(f"   Failed: {sys_stats['failed']}")
                if sys_stats['avg_latency_ms']:
                    print(f"   Avg Latency: {sys_stats['avg_latency_ms']:.2f}ms")
                    print(f"   Median Latency: {sys_stats['median_latency_ms']:.2f}ms")
                    print(f"   Max Latency: {sys_stats['max_latency_ms']:.2f}ms")
                    print(f"   Min Latency: {sys_stats['min_latency_ms']:.2f}ms")
                print(f"   Current Timeout: {sys_stats['current_timeout']:.2f}s")
                print(f"   Base Timeout: {sys_stats['base_timeout']:.2f}s")
                print(f"   Min Timeout: {sys_stats['min_timeout']:.2f}s")
                print(f"   Max Timeout: {sys_stats['max_timeout']:.2f}s")

    elif args.sync_to_cloud:
        success = scaler.sync_to_cloud(args.sync_to_cloud)
        if args.json:
            print(json.dumps({"success": success, "state": scaler.feedback_loop_state}, indent=2))
        else:
            print(f"\n☁️  Sync to Cloud")
            print(f"   Success: {success}")
            print(f"   Last Cloud Sync: {scaler.feedback_loop_state.get('last_cloud_sync', 'Never')}")
            print(f"   'A Hobbit's Journey. Because it gives us courage.' - @GANDALF")

    elif args.sync_from_cloud:
        success = scaler.sync_from_cloud(args.sync_from_cloud)
        if args.json:
            print(json.dumps({"success": success, "state": scaler.feedback_loop_state}, indent=2))
        else:
            print(f"\n☁️  Sync from Cloud")
            print(f"   Success: {success}")
            print(f"   Last Local Sync: {scaler.feedback_loop_state.get('last_local_sync', 'Never')}")
            print(f"   Feedback Cycles: {scaler.feedback_loop_state.get('feedback_cycles', 0)}")
            print(f"   'A Hobbit's Journey. Because it gives us courage.' - @GANDALF")

    elif args.feedback_loop:
        success = scaler.feedback_loop_cycle(args.feedback_loop)
        if args.json:
            print(json.dumps({"success": success, "state": scaler.feedback_loop_state}, indent=2))
        else:
            print(f"\n🔄 Feedback Loop Cycle")
            print(f"   Success: {success}")
            print(f"   Feedback Cycles: {scaler.feedback_loop_state.get('feedback_cycles', 0)}")
            print(f"   Last Cloud Sync: {scaler.feedback_loop_state.get('last_cloud_sync', 'Never')}")
            print(f"   Last Local Sync: {scaler.feedback_loop_state.get('last_local_sync', 'Never')}")
            print(f"   'A Hobbit's Journey. Because it gives us courage.' - @GANDALF")

    else:
        parser.print_help()
        print("\n⏱️  Dynamic Timeout Scaling - Account for LUMINA System Latency")
        print("   Accounting for LUMINA system latency")
        print("   Adaptive timeout scaling enabled")
        print("   Exponential backoff retry enabled")
        print("   Persistent memory enabled (A Hobbit's Journey)")
        print("   Feedback loop: Cloud <-> Local AI Models")
        print("   'It gives us courage.' - @GANDALF")

