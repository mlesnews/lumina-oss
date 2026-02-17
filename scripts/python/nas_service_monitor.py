#!/usr/bin/env python3
"""
NAS Service Monitor with Heartbeat and Master Coordination

Monitors NAS services with configurable heartbeat intervals, API availability checks,
and ping-pong communication with master service coordination.
"""

import sys
import time
import threading
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
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
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    from nas_certificate_manager import NASCertificateManager
    CERT_MANAGER_AVAILABLE = True
except ImportError:
    CERT_MANAGER_AVAILABLE = False
    NASCertificateManager = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Service health metrics"""
    service_id: str
    status: ServiceStatus
    last_heartbeat: datetime
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    response_time_ms: Optional[float] = None
    api_available: bool = False
    ssh_available: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        if self.last_success:
            data['last_success'] = self.last_success.isoformat()
        if self.last_failure:
            data['last_failure'] = self.last_failure.isoformat()
        return data


@dataclass
class HeartbeatMessage:
    """Heartbeat message for ping-pong communication"""
    service_id: str
    timestamp: datetime
    status: ServiceStatus
    health: Dict[str, Any]
    sequence: int = 0
    response_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'service_id': self.service_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'health': self.health,
            'sequence': self.sequence,
            'response_required': self.response_required
        }


class NASServiceMonitor:
    """
    NAS Service Monitor with heartbeat and master coordination

    Features:
    - Configurable heartbeat intervals (longer for reduced overhead)
    - NAS API availability checks
    - SSH connectivity checks
    - Ping-pong communication with master service
    - Status reporting and aggregation
    """

    def __init__(
        self,
        service_id: str,
        nas_config: Dict[str, Any],
        heartbeat_interval: int = 300,  # 5 minutes default (longer heartbeat)
        master_endpoint: Optional[str] = None,
        status_callback: Optional[Callable[[ServiceHealth], None]] = None
    ):
        """
        Initialize NAS Service Monitor

        Args:
            service_id: Unique identifier for this service
            nas_config: NAS configuration (host, port, credentials, etc.)
            heartbeat_interval: Heartbeat interval in seconds (default: 300 = 5 min)
            master_endpoint: Master service endpoint for status reporting
            status_callback: Optional callback for status updates
        """
        self.service_id = service_id
        self.nas_config = nas_config
        self.heartbeat_interval = heartbeat_interval
        self.master_endpoint = master_endpoint
        self.status_callback = status_callback

        self.logger = get_logger(f"NASServiceMonitor-{service_id}")

        # Service health tracking
        self.health: Optional[ServiceHealth] = None
        self.sequence_number = 0
        self.ping_pong_history: List[Dict[str, Any]] = []

        # Threading
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()

        # NAS connection info
        self.nas_host = nas_config.get('host', '<NAS_PRIMARY_IP>')
        self.nas_port = nas_config.get('port', 5001)
        self.nas_api_port = nas_config.get('api_port', 5001)
        self.nas_ssh_port = nas_config.get('ssh_port', 22)

        # Initialize certificate manager
        self.cert_manager = None
        if CERT_MANAGER_AVAILABLE and NASCertificateManager:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.cert_manager = NASCertificateManager(project_root=project_root)
                self.logger.info("✅ Certificate manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Certificate manager initialization failed: {e}")

        # Initialize health
        self._initialize_health()

        self.logger.info(f"NAS Service Monitor initialized (heartbeat: {heartbeat_interval}s)")

    def _initialize_health(self) -> None:
        """Initialize service health"""
        self.health = ServiceHealth(
            service_id=self.service_id,
            status=ServiceStatus.UNKNOWN,
            last_heartbeat=datetime.now()
        )

    def start(self) -> None:
        """Start monitoring"""
        if self._running:
            self.logger.warning("Monitor already running")
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info(f"✅ NAS Service Monitor started (heartbeat: {self.heartbeat_interval}s)")

    def stop(self) -> None:
        """Stop monitoring"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=10)
        self.logger.info("NAS Service Monitor stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self._running:
            try:
                # Perform health check
                health = self._check_service_health()

                # Update health status
                with self._lock:
                    self.health = health

                # Send heartbeat to master (ping)
                if self.master_endpoint:
                    self._send_heartbeat(health)

                # Call status callback if provided
                if self.status_callback:
                    try:
                        self.status_callback(health)
                    except Exception as e:
                        self.logger.debug(f"Status callback error: {e}")

                # Wait for next heartbeat
                time.sleep(self.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)  # Wait 1 minute on error before retry

    def _check_service_health(self) -> ServiceHealth:
        """Check NAS service health"""
        start_time = time.time()
        health = ServiceHealth(
            service_id=self.service_id,
            status=ServiceStatus.UNKNOWN,
            last_heartbeat=datetime.now(),
            success_count=self.health.success_count if self.health else 0,
            failure_count=self.health.failure_count if self.health else 0
        )

        # Check API availability
        api_available = False
        try:
            api_available = self._check_nas_api()
            health.api_available = api_available
        except Exception as e:
            health.error_message = f"API check failed: {e}"
            self.logger.debug(f"NAS API check failed: {e}")

        # Check SSH availability
        ssh_available = False
        try:
            ssh_available = self._check_nas_ssh()
            health.ssh_available = ssh_available
        except Exception as e:
            if not health.error_message:
                health.error_message = f"SSH check failed: {e}"
            self.logger.debug(f"NAS SSH check failed: {e}")

        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        health.response_time_ms = response_time

        # Determine overall status
        if api_available or ssh_available:
            if response_time < 1000:  # < 1 second
                health.status = ServiceStatus.HEALTHY
            elif response_time < 5000:  # < 5 seconds
                health.status = ServiceStatus.DEGRADED
            else:
                health.status = ServiceStatus.UNHEALTHY

            health.last_success = datetime.now()
            health.success_count += 1
        else:
            health.status = ServiceStatus.OFFLINE
            health.last_failure = datetime.now()
            health.failure_count += 1

        # Update metadata
        health.metadata = {
            'nas_host': self.nas_host,
            'nas_port': self.nas_port,
            'api_port': self.nas_api_port,
            'ssh_port': self.nas_ssh_port,
            'check_timestamp': datetime.now().isoformat()
        }

        return health

    def _check_nas_api(self) -> bool:
        """Check NAS API availability"""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            # Try to connect to NAS API endpoint
            # Synology DSM typically uses port 5001 for HTTPS
            api_url = f"https://{self.nas_host}:{self.nas_api_port}/webapi/query.cgi"

            # Get certificate verification setting
            verify_setting = False  # Default fallback
            if self.cert_manager:
                verify_setting = self.cert_manager.get_requests_verify_setting(
                    self.nas_host,
                    self.nas_api_port,
                    auto_download=True,  # Auto-download certificate if not found
                    auto_generate=True   # Auto-generate self-signed certificate if download fails
                )

            # Simple connectivity check (with short timeout)
            response = requests.get(
                api_url,
                params={'api': 'SYNO.API.Info', 'version': '1', 'method': 'query'},
                timeout=5,
                verify=verify_setting  # Use certificate if available
            )

            return response.status_code in [200, 401, 403]  # 401/403 means API is up, just auth needed

        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception as e:
            self.logger.debug(f"NAS API check exception: {e}")
            return False

    def _check_nas_ssh(self) -> bool:
        """Check NAS SSH availability"""
        if not PARAMIKO_AVAILABLE:
            return False

        try:
            # Get credentials from config or vault
            password = self.nas_config.get('password')
            username = self.nas_config.get('username') or self.nas_config.get('user', 'backupadm')

            if not password:
                return False

            # Quick SSH connection test
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.nas_host,
                port=self.nas_ssh_port,
                username=username,
                password=password,
                timeout=5,
                allow_agent=False,
                look_for_keys=False
            )
            client.close()
            return True

        except Exception as e:
            self.logger.debug(f"NAS SSH check exception: {e}")
            return False

    def _send_heartbeat(self, health: ServiceHealth) -> None:
        """Send heartbeat (ping) to master service"""
        if not self.master_endpoint or not REQUESTS_AVAILABLE:
            return

        try:
            self.sequence_number += 1

            heartbeat = HeartbeatMessage(
                service_id=self.service_id,
                timestamp=datetime.now(),
                status=health.status,
                health=health.to_dict(),
                sequence=self.sequence_number,
                response_required=True
            )

            # Send ping to master
            response = requests.post(
                f"{self.master_endpoint}/heartbeat",
                json=heartbeat.to_dict(),
                timeout=10
            )

            if response.status_code == 200:
                # Received pong response
                pong_data = response.json()
                self._handle_pong(pong_data)
                self.logger.debug(f"✅ Heartbeat sent and acknowledged (seq: {self.sequence_number})")
            else:
                self.logger.debug(f"⚠️  Heartbeat sent but got status {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.debug("Heartbeat timeout - master may be unavailable")
        except requests.exceptions.ConnectionError:
            self.logger.debug("Heartbeat connection error - master may be offline")
        except Exception as e:
            self.logger.debug(f"Heartbeat error: {e}")

    def _handle_pong(self, pong_data: Dict[str, Any]) -> None:
        """Handle pong response from master"""
        with self._lock:
            self.ping_pong_history.append({
                'timestamp': datetime.now().isoformat(),
                'pong': pong_data,
                'sequence': self.sequence_number
            })

            # Keep only last 100 ping-pong exchanges
            if len(self.ping_pong_history) > 100:
                self.ping_pong_history.pop(0)

            # Update metadata with master response
            if self.health:
                self.health.metadata['last_pong'] = pong_data
                self.health.metadata['master_acknowledged'] = True

    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        with self._lock:
            if not self.health:
                return {
                    'service_id': self.service_id,
                    'status': 'unknown',
                    'monitoring': False
                }

            return {
                'service_id': self.service_id,
                'monitoring': self._running,
                'heartbeat_interval': self.heartbeat_interval,
                'health': self.health.to_dict(),
                'ping_pong_count': len(self.ping_pong_history),
                'last_ping_pong': self.ping_pong_history[-1] if self.ping_pong_history else None
            }

    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for reporting"""
        with self._lock:
            if not self.health:
                return {}

            total_checks = self.health.success_count + self.health.failure_count
            success_rate = (self.health.success_count / total_checks * 100) if total_checks > 0 else 0

            return {
                'service_id': self.service_id,
                'status': self.health.status.value,
                'success_rate': f"{success_rate:.1f}%",
                'total_checks': total_checks,
                'success_count': self.health.success_count,
                'failure_count': self.health.failure_count,
                'api_available': self.health.api_available,
                'ssh_available': self.health.ssh_available,
                'response_time_ms': self.health.response_time_ms,
                'last_success': self.health.last_success.isoformat() if self.health.last_success else None,
                'last_failure': self.health.last_failure.isoformat() if self.health.last_failure else None
            }


class NASMasterCoordinator:
    """
    Master service coordinator for NAS service monitoring

    Aggregates status from multiple NAS service monitors and provides
    centralized coordination and reporting.
    """

    def __init__(self, coordinator_id: str = "nas-master"):
        """Initialize master coordinator"""
        self.coordinator_id = coordinator_id
        self.logger = get_logger(f"NASMasterCoordinator-{coordinator_id}")

        # Service registry
        self.registered_services: Dict[str, NASServiceMonitor] = {}
        self.service_status: Dict[str, ServiceHealth] = {}

        # Ping-pong tracking
        self.heartbeat_history: Dict[str, List[Dict[str, Any]]] = {}

        self._lock = threading.RLock()

    def register_service(self, monitor: NASServiceMonitor) -> None:
        """Register a service monitor"""
        with self._lock:
            self.registered_services[monitor.service_id] = monitor
            self.logger.info(f"Registered service: {monitor.service_id}")

    def unregister_service(self, service_id: str) -> None:
        """Unregister a service monitor"""
        with self._lock:
            if service_id in self.registered_services:
                del self.registered_services[service_id]
            if service_id in self.service_status:
                del self.service_status[service_id]
            self.logger.info(f"Unregistered service: {service_id}")

    def update_service_status(self, service_id: str, health: ServiceHealth) -> None:
        """Update service status (called by monitors)"""
        with self._lock:
            self.service_status[service_id] = health

            # Track heartbeat history
            if service_id not in self.heartbeat_history:
                self.heartbeat_history[service_id] = []

            self.heartbeat_history[service_id].append({
                'timestamp': datetime.now().isoformat(),
                'health': health.to_dict()
            })

            # Keep only last 1000 heartbeats per service
            if len(self.heartbeat_history[service_id]) > 1000:
                self.heartbeat_history[service_id].pop(0)

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all registered services"""
        with self._lock:
            status_summary = {}
            for service_id, monitor in self.registered_services.items():
                status_summary[service_id] = monitor.get_health_summary()

            return {
                'coordinator_id': self.coordinator_id,
                'timestamp': datetime.now().isoformat(),
                'services': status_summary,
                'total_services': len(self.registered_services),
                'healthy_count': sum(1 for s in status_summary.values() 
                                    if s.get('status') == 'healthy'),
                'degraded_count': sum(1 for s in status_summary.values() 
                                    if s.get('status') == 'degraded'),
                'unhealthy_count': sum(1 for s in status_summary.values() 
                                     if s.get('status') == 'unhealthy'),
                'offline_count': sum(1 for s in status_summary.values() 
                                    if s.get('status') == 'offline')
            }

    def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific service"""
        with self._lock:
            if service_id in self.registered_services:
                return self.registered_services[service_id].get_health_summary()
            return None


# Global master coordinator instance
_global_master_coordinator: Optional[NASMasterCoordinator] = None


def get_master_coordinator() -> NASMasterCoordinator:
    """Get or create global master coordinator"""
    global _global_master_coordinator
    if _global_master_coordinator is None:
        _global_master_coordinator = NASMasterCoordinator()
    return _global_master_coordinator


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="NAS Service Monitor")
    parser.add_argument("--service-id", default="nas-cache-service", help="Service ID")
    parser.add_argument("--heartbeat", type=int, default=300, help="Heartbeat interval (seconds)")
    parser.add_argument("--master", help="Master service endpoint")
    parser.add_argument("--nas-host", default="<NAS_PRIMARY_IP>", help="NAS host")
    parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")

    args = parser.parse_args()

    nas_config = {
        'host': args.nas_host,
        'port': args.nas_port,
        'api_port': 5001,
        'ssh_port': 22
    }

    monitor = NASServiceMonitor(
        service_id=args.service_id,
        nas_config=nas_config,
        heartbeat_interval=args.heartbeat,
        master_endpoint=args.master
    )

    # Register with master coordinator
    master = get_master_coordinator()
    master.register_service(monitor)

    # Start monitoring
    monitor.start()

    try:
        # Run for a while
        import time
        while True:
            status = monitor.get_status()
            print(f"\n📊 Service Status: {json.dumps(status, indent=2)}")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        monitor.stop()

