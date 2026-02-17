#!/usr/bin/env python3
"""
Symbiotic Cluster Coordinator - Iron Legion

Treats local and target host (Kaiju cluster) as one symbiotic organism.
Implements holistic resource utilization (97% target as @gandalf),
automatic failover, load balancing, and degradation mitigation.

@marvin Analysis: Making both hosts two halves of the same cluster enables:
- Automatic compensation if one host is lost
- Load balancing across both hosts
- Degradation mitigation
- Holistic resource utilization
"""

import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from dynamic_timeout_scaling import post_with_dynamic_timeout, get_with_dynamic_timeout
    DYNAMIC_TIMEOUT_AVAILABLE = True
except ImportError:
    DYNAMIC_TIMEOUT_AVAILABLE = False
    post_with_dynamic_timeout = None
    get_with_dynamic_timeout = None

try:
    from ide_session_load_balancer import IDESessionLoadBalancer
    IDE_BALANCER_AVAILABLE = True
except ImportError:
    IDE_BALANCER_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class HostStatus(Enum):
    """Host status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ClusterMode(Enum):
    """Cluster operation mode"""
    SYMBIOTIC = "symbiotic"  # Both hosts as one organism
    PRIMARY_SECONDARY = "primary_secondary"  # Primary with backup
    LOAD_BALANCED = "load_balanced"  # Equal distribution
    FAILOVER = "failover"  # One active, one standby


@dataclass
class HostMetrics:
    """Host performance metrics"""
    host_id: str
    endpoint: str
    status: HostStatus
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    active_requests: int = 0
    queue_length: int = 0
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    available_models: List[str] = field(default_factory=list)
    last_check: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.last_check:
            data['last_check'] = self.last_check.isoformat()
        return data

    def get_capacity(self) -> float:
        """Get available capacity (0-1)"""
        # Capacity based on CPU, memory, and queue
        cpu_factor = 1.0 - (self.cpu_usage / 100.0)
        memory_factor = 1.0 - (self.memory_usage / 100.0)
        queue_factor = max(0, 1.0 - (self.queue_length / 100.0))

        # Weighted average
        capacity = (cpu_factor * 0.4 + memory_factor * 0.4 + queue_factor * 0.2)
        return max(0.0, min(1.0, capacity))

    def get_utilization(self) -> float:
        """Get current utilization (0-100%)"""
        return (self.cpu_usage + self.memory_usage) / 2.0


@dataclass
class ClusterState:
    """Symbiotic cluster state"""
    cluster_id: str
    mode: ClusterMode
    target_utilization: float = 97.0  # @gandalf target
    current_utilization: float = 0.0
    hosts: Dict[str, HostMetrics] = field(default_factory=dict)
    active_hosts: List[str] = field(default_factory=list)
    load_distribution: Dict[str, float] = field(default_factory=dict)
    last_balance: Optional[datetime] = None
    failover_count: int = 0
    total_requests: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'cluster_id': self.cluster_id,
            'mode': self.mode.value,
            'target_utilization': self.target_utilization,
            'current_utilization': self.current_utilization,
            'hosts': {k: v.to_dict() for k, v in self.hosts.items()},
            'active_hosts': self.active_hosts,
            'load_distribution': self.load_distribution,
            'last_balance': self.last_balance.isoformat() if self.last_balance else None,
            'failover_count': self.failover_count,
            'total_requests': self.total_requests
        }


class SymbioticClusterCoordinator:
    """
    Symbiotic Cluster Coordinator

    Treats local and target host (Kaiju Iron Legion) as one symbiotic organism.
    Implements holistic resource management with 97% utilization target (@gandalf),
    automatic failover, load balancing, and degradation mitigation.

    @marvin Analysis: Both hosts are two halves of the same cluster, enabling:
    - Automatic compensation if one host is lost
    - Load balancing across both hosts
    - Degradation mitigation
    - Holistic resource utilization
    """

    def __init__(
        self,
        local_endpoint: str = "http://localhost:11437",
        target_endpoint: str = "http://kaiju_no_8:11437",
        target_utilization: float = 97.0,
        balance_interval: int = 30
    ):
        """
        Initialize symbiotic cluster coordinator

        Args:
            local_endpoint: Local host endpoint
            target_endpoint: Target host (Kaiju) endpoint
            target_utilization: Target utilization percentage (default: 97% as @gandalf)
            balance_interval: Load balancing interval in seconds
        """
        self.logger = get_logger("SymbioticCluster")

        # Cluster configuration
        self.local_endpoint = local_endpoint
        self.target_endpoint = target_endpoint
        self.target_utilization = target_utilization

        # Cluster state
        self.cluster_state = ClusterState(
            cluster_id="llama3_2_3b_symbiotic",
            mode=ClusterMode.SYMBIOTIC,
            target_utilization=target_utilization
        )

        # Initialize hosts
        self.cluster_state.hosts['local'] = HostMetrics(
            host_id='local',
            endpoint=local_endpoint,
            status=HostStatus.UNKNOWN
        )
        self.cluster_state.hosts['target'] = HostMetrics(
            host_id='target',
            endpoint=target_endpoint,
            status=HostStatus.UNKNOWN
        )

        # Initialize IDE session load balancer (if available)
        self.ide_balancer = None
        if IDE_BALANCER_AVAILABLE:
            try:
                self.ide_balancer = IDESessionLoadBalancer(self.project_root)
                self.logger.info("✅ IDE session load balancer integrated")
            except Exception as e:
                self.logger.debug(f"IDE balancer not available: {e}")

        # Load balancing
        self.balance_interval = balance_interval
        self._balance_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.RLock()

        # Request routing
        self.request_history: List[Dict[str, Any]] = []

        self.logger.info("✅ Symbiotic Cluster Coordinator initialized")
        self.logger.info(f"   Local: {local_endpoint}")
        self.logger.info(f"   Target: {target_endpoint}")
        self.logger.info(f"   Target Utilization: {target_utilization}% (@gandalf)")

    def start(self) -> None:
        """Start cluster coordination"""
        if self._running:
            return

        self._running = True

        # Start health monitoring
        self._monitor_hosts()

        # Start load balancing
        self._balance_thread = threading.Thread(target=self._balance_loop, daemon=True)
        self._balance_thread.start()

        self.logger.info("✅ Symbiotic cluster coordination started")

    def stop(self) -> None:
        """Stop cluster coordination"""
        self._running = False
        if self._balance_thread:
            self._balance_thread.join(timeout=10)
        self.logger.info("Symbiotic cluster coordination stopped")

    def _monitor_hosts(self) -> None:
        """Monitor host health and metrics"""
        with self._lock:
            for host_id, host in self.cluster_state.hosts.items():
                try:
                    metrics = self._check_host_health(host.endpoint)
                    if metrics:
                        host.status = metrics['status']
                        host.cpu_usage = metrics.get('cpu_usage', 0.0)
                        host.memory_usage = metrics.get('memory_usage', 0.0)
                        host.gpu_usage = metrics.get('gpu_usage', 0.0)
                        host.active_requests = metrics.get('active_requests', 0)
                        host.queue_length = metrics.get('queue_length', 0)
                        host.response_time_ms = metrics.get('response_time_ms', 0.0)
                        host.available_models = metrics.get('available_models', [])
                        host.last_check = datetime.now()

                        if host.status == HostStatus.HEALTHY:
                            if host_id not in self.cluster_state.active_hosts:
                                self.cluster_state.active_hosts.append(host_id)
                        else:
                            if host_id in self.cluster_state.active_hosts:
                                self.cluster_state.active_hosts.remove(host_id)
                                if host.status == HostStatus.OFFLINE:
                                    self.cluster_state.failover_count += 1
                                    self.logger.warning(f"⚠️  Host {host_id} went offline - automatic compensation")
                except Exception as e:
                    self.logger.debug(f"Host {host_id} check failed: {e}")
                    host.status = HostStatus.OFFLINE
                    if host_id in self.cluster_state.active_hosts:
                        self.cluster_state.active_hosts.remove(host_id)

    def _check_host_health(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Check host health and metrics"""
        if not REQUESTS_AVAILABLE:
            return None

        # Try multiple endpoints with fallback
        endpoints_to_try = [
            endpoint,  # Primary endpoint
            endpoint.replace("kaiju_no_8", "localhost"),  # Fallback to localhost
            endpoint.replace("kaiju_no_8", "127.0.0.1"),  # Fallback to IP
        ]

        last_error = None
        for attempt_endpoint in endpoints_to_try:
            try:
                # Check if endpoint is reachable with dynamic timeout
                start_time = time.time()
                if DYNAMIC_TIMEOUT_AVAILABLE and get_with_dynamic_timeout:
                    response = get_with_dynamic_timeout(
                        system="symbiotic_cluster",
                        operation="check_endpoint",
                        url=f"{attempt_endpoint}/api/tags"
                    )
                else:
                    response = requests.get(f"{attempt_endpoint}/api/tags", timeout=5)
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    models = [m.get('name', '') for m in data.get('models', [])]

                    # Estimate metrics (would need actual metrics endpoint)
                    # For now, use response time and queue as indicators
                    status = HostStatus.HEALTHY
                    if response_time > 1000:
                        status = HostStatus.DEGRADED
                    elif response_time > 5000:
                        status = HostStatus.OVERLOADED

                    # Estimate utilization (would need actual metrics)
                    cpu_usage = min(95.0, response_time / 10.0)  # Rough estimate
                    memory_usage = min(95.0, len(models) * 10.0)  # Rough estimate

                    # Log successful connection
                    if attempt_endpoint != endpoint:
                        self.logger.info(f"✅ Connected to Iron Legion via fallback: {attempt_endpoint}")

                    return {
                        'status': status,
                        'cpu_usage': cpu_usage,
                        'memory_usage': memory_usage,
                        'gpu_usage': 0.0,  # Would need GPU metrics
                        'active_requests': 0,  # Would need request queue metrics
                        'queue_length': 0,
                        'response_time_ms': response_time,
                        'available_models': models,
                        'error_rate': 0.0,
                        'endpoint_used': attempt_endpoint
                    }
                else:
                    last_error = f"HTTP {response.status_code}"
                    continue  # Try next endpoint
            except requests.exceptions.Timeout:
                last_error = "Timeout"
                continue  # Try next endpoint
            except requests.exceptions.ConnectionError as e:
                last_error = f"ConnectionError: {str(e)}"
                continue  # Try next endpoint
            except Exception as e:
                last_error = f"Exception: {str(e)}"
                continue  # Try next endpoint

        # All endpoints failed
        self.logger.warning(f"⚠️  All Iron Legion endpoints failed. Last error: {last_error}")
        self.logger.warning(f"   Tried: {', '.join(endpoints_to_try)}")
        return {'status': HostStatus.OFFLINE, 'error': last_error}

    def _balance_loop(self) -> None:
        """Load balancing loop"""
        while self._running:
            try:
                self._balance_load()
                time.sleep(self.balance_interval)
            except Exception as e:
                self.logger.error(f"Balance loop error: {e}")
                time.sleep(60)

    def _balance_load(self) -> None:
        """Balance load across hosts to achieve target utilization"""
        with self._lock:
            # Update host metrics
            self._monitor_hosts()

            # Calculate current cluster utilization
            active_hosts = [h for h in self.cluster_state.hosts.values() 
                           if h.status in [HostStatus.HEALTHY, HostStatus.DEGRADED]]

            if not active_hosts:
                self.logger.warning("⚠️  No active hosts available")
                return

            # Calculate average utilization
            total_utilization = sum(h.get_utilization() for h in active_hosts)
            avg_utilization = total_utilization / len(active_hosts) if active_hosts else 0.0
            self.cluster_state.current_utilization = avg_utilization

            # Calculate load distribution to reach target utilization
            target_per_host = self.target_utilization / len(active_hosts)

            load_distribution = {}
            for host in active_hosts:
                current_util = host.get_utilization()
                capacity = host.get_capacity()

                # Calculate desired load for this host
                if avg_utilization < self.target_utilization:
                    # Increase load to reach target
                    desired_load = min(target_per_host, current_util + (self.target_utilization - avg_utilization) / len(active_hosts))
                else:
                    # Reduce load if over target
                    desired_load = max(0, current_util - (avg_utilization - self.target_utilization) / len(active_hosts))

                load_distribution[host.host_id] = desired_load

            self.cluster_state.load_distribution = load_distribution
            self.cluster_state.last_balance = datetime.now()

            # Log balancing decision
            if abs(avg_utilization - self.target_utilization) > 5.0:
                self.logger.info(f"📊 Cluster utilization: {avg_utilization:.1f}% (target: {self.target_utilization}%)")
                self.logger.info(f"   Load distribution: {load_distribution}")

    def select_host(self, model: Optional[str] = None, priority: str = "balanced") -> Optional[str]:
        """
        Select best host for request (symbiotic routing with IDE session awareness)

        Args:
            model: Required model name
            priority: "balanced", "local", "target", "fastest"

        Returns:
            Selected host ID or None
        """
        with self._lock:
            # Check IDE session load balancer if using local host
            if self.ide_balancer and priority in ["local", "balanced"]:
                # Check if local host can accept request
                if not self.ide_balancer.can_accept_request():
                    self.logger.warning("⚠️  Local host overloaded - checking alternatives")
                    # Try to find least loaded session
                    least_loaded = self.ide_balancer.get_least_loaded_session()
                    if not least_loaded:
                        # Local host overloaded, prefer target if available
                        priority = "target"

            # Filter hosts by availability and model
            available_hosts = []
            for host_id, host in self.cluster_state.hosts.items():
                if host.status in [HostStatus.HEALTHY, HostStatus.DEGRADED]:
                    if not model or model in host.available_models:
                        available_hosts.append((host_id, host))

            if not available_hosts:
                self.logger.warning("⚠️  No available hosts")
                return None

            # Select based on priority
            if priority == "local":
                # Check IDE session load before selecting local
                if self.ide_balancer:
                    if not self.ide_balancer.can_accept_request():
                        # Local overloaded, try target
                        for host_id, host in available_hosts:
                            if host_id == "target":
                                return host_id

                for host_id, host in available_hosts:
                    if host_id == "local":
                        return host_id
                return available_hosts[0][0]  # Fallback

            elif priority == "target":
                for host_id, host in available_hosts:
                    if host_id == "target":
                        return host_id
                return available_hosts[0][0]  # Fallback

            elif priority == "fastest":
                # Select host with lowest response time
                fastest = min(available_hosts, key=lambda x: x[1].response_time_ms)
                return fastest[0]

            else:  # balanced (default)
                # Use load distribution with IDE session awareness
                if self.ide_balancer:
                    # Adjust local host load based on IDE sessions
                    local_host = None
                    for host_id, host in available_hosts:
                        if host_id == "local":
                            local_host = host
                            break

                    if local_host:
                        # Get IDE session load
                        ide_status = self.ide_balancer.get_load_balance_status()
                        total_sessions = ide_status.get('total_sessions', 0)
                        stalled_sessions = ide_status.get('stalled_sessions', 0)

                        # Adjust utilization based on IDE session load
                        if total_sessions > 0:
                            session_load_factor = 1.0 + (stalled_sessions / total_sessions) * 0.5
                            local_host.cpu_usage = min(100.0, local_host.cpu_usage * session_load_factor)

                # Use load distribution to select host
                if self.cluster_state.load_distribution:
                    # Select host with lowest current load relative to target
                    best_host = None
                    best_score = float('inf')

                    for host_id, host in available_hosts:
                        current_load = host.get_utilization()
                        target_load = self.cluster_state.load_distribution.get(host_id, 50.0)
                        score = abs(current_load - target_load)

                        if score < best_score:
                            best_score = score
                            best_host = host_id

                    return best_host or available_hosts[0][0]

                # Fallback: round-robin or least loaded
                least_loaded = min(available_hosts, key=lambda x: x[1].get_utilization())
                return least_loaded[0]

    def route_request(
        self,
        model: str,
        endpoint: str = "/api/generate",
        data: Optional[Dict[str, Any]] = None,
        priority: str = "balanced"
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Route request to best host (symbiotic routing)

        Returns:
            (host_id, response_data) or (None, None) if failed
        """
        # Select host
        host_id = self.select_host(model, priority)
        if not host_id:
            return None, None

        host = self.cluster_state.hosts[host_id]

        # Record request in IDE balancer if using local host
        if host_id == "local" and self.ide_balancer:
            self.ide_balancer.record_request()

        # Make request with dynamic timeout scaling
        try:
            url = f"{host.endpoint}{endpoint}"

            # Use dynamic timeout scaling if available
            if DYNAMIC_TIMEOUT_AVAILABLE and post_with_dynamic_timeout:
                self.logger.debug(f"  ⏱️  Using dynamic timeout scaling for {host_id}")
                response = post_with_dynamic_timeout(
                    system="symbiotic_cluster",
                    operation=f"route_request_{host_id}",
                    url=url,
                    json=data
                )
            else:
                # Fallback to standard requests with retry logic
                max_retries = 3
                retry_delay = 1.0
                response = None

                for retry in range(max_retries):
                    try:
                        response = requests.post(url, json=data, timeout=60)
                        break  # Success, exit retry loop
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                        if retry < max_retries - 1:
                            self.logger.warning(f"⚠️  Request to {host_id} failed (attempt {retry + 1}/{max_retries}): {e}")
                            time.sleep(retry_delay * (retry + 1))  # Exponential backoff
                            continue
                        else:
                            raise  # Re-raise on final attempt
                    except Exception as e:
                        raise  # Re-raise non-network errors immediately

                if not response:
                    raise Exception("Request failed after all retries")

            if response.status_code == 200:
                # Update metrics
                with self._lock:
                    host.total_requests += 1
                    host.successful_requests += 1
                    self.cluster_state.total_requests += 1

                # Complete request in IDE balancer
                if host_id == "local" and self.ide_balancer:
                    self.ide_balancer.complete_request()

                return host_id, response.json()
            else:
                with self._lock:
                    host.total_requests += 1
                    host.failed_requests += 1
                    host.error_rate = host.failed_requests / host.total_requests if host.total_requests > 0 else 0.0

                # Complete request in IDE balancer (even on failure)
                if host_id == "local" and self.ide_balancer:
                    self.ide_balancer.complete_request()

                # Try failover
                if host_id == "local":
                    return self.route_request(model, endpoint, data, priority="target")
                elif host_id == "target":
                    return self.route_request(model, endpoint, data, priority="local")

                return None, None
        except Exception as e:
            self.logger.error(f"Request routing error: {e}")

            # Complete request in IDE balancer on error
            if host_id == "local" and self.ide_balancer:
                self.ide_balancer.complete_request()

            # Try failover
            if host_id == "local":
                return self.route_request(model, endpoint, data, priority="target")
            elif host_id == "target":
                return self.route_request(model, endpoint, data, priority="local")

            return None, None

        except Exception as e:
            self.logger.debug(f"Request to {host_id} failed: {e}")

            # Automatic failover
            with self._lock:
                host.failed_requests += 1
                host.error_rate = host.failed_requests / host.total_requests if host.total_requests > 0 else 0.0

                # Try other host
                if host_id == "local" and "target" in self.cluster_state.active_hosts:
                    return self.route_request(model, endpoint, data, priority="target")
                elif host_id == "target" and "local" in self.cluster_state.active_hosts:
                    return self.route_request(model, endpoint, data, priority="local")

            return None, None

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        with self._lock:
            return self.cluster_state.to_dict()

    def get_utilization_report(self) -> Dict[str, Any]:
        """Get utilization report (@gandalf style)"""
        with self._lock:
            active_hosts = [h for h in self.cluster_state.hosts.values() 
                           if h.status in [HostStatus.HEALTHY, HostStatus.DEGRADED]]

            report = {
                'cluster_id': self.cluster_state.cluster_id,
                'target_utilization': self.target_utilization,
                'current_utilization': self.cluster_state.current_utilization,
                'utilization_gap': abs(self.cluster_state.current_utilization - self.target_utilization),
                'active_hosts': len(active_hosts),
                'total_hosts': len(self.cluster_state.hosts),
                'failover_count': self.cluster_state.failover_count,
                'total_requests': self.cluster_state.total_requests,
                'hosts': {}
            }

            for host_id, host in self.cluster_state.hosts.items():
                report['hosts'][host_id] = {
                    'status': host.status.value,
                    'utilization': host.get_utilization(),
                    'capacity': host.get_capacity(),
                    'cpu_usage': host.cpu_usage,
                    'memory_usage': host.memory_usage,
                    'response_time_ms': host.response_time_ms,
                    'total_requests': host.total_requests,
                    'success_rate': (host.successful_requests / host.total_requests * 100) if host.total_requests > 0 else 0.0
                }

            return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Symbiotic Cluster Coordinator")
    parser.add_argument("--local", default="http://localhost:11437", help="Local endpoint")
    parser.add_argument("--target", default="http://kaiju_no_8:11437", help="Target endpoint")
    parser.add_argument("--target-util", type=float, default=97.0, help="Target utilization %")
    parser.add_argument("--status", action="store_true", help="Show cluster status")
    parser.add_argument("--utilization", action="store_true", help="Show utilization report")

    args = parser.parse_args()

    coordinator = SymbioticClusterCoordinator(
        local_endpoint=args.local,
        target_endpoint=args.target,
        target_utilization=args.target_util
    )

    coordinator.start()

    try:
        if args.status:
            status = coordinator.get_cluster_status()
            print("\n📊 Cluster Status:")
            print(json.dumps(status, indent=2))

        if args.utilization:
            report = coordinator.get_utilization_report()
            print("\n📈 Utilization Report (@gandalf):")
            print(json.dumps(report, indent=2))

        if not args.status and not args.utilization:
            # Keep running
            import time
            while True:
                time.sleep(60)
                report = coordinator.get_utilization_report()
                print(f"\n📊 Utilization: {report['current_utilization']:.1f}% (target: {report['target_utilization']}%)")

    except KeyboardInterrupt:
        print("\n🛑 Stopping coordinator...")
        coordinator.stop()

