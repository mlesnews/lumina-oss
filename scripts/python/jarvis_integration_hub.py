#!/usr/bin/env python3
"""
JARVIS Integration Hub

Central integration point for all JARVIS systems and external services.
Provides unified communication, data sharing, and coordination between systems.

MCU JARVIS Capability: System integration and coordination.

@JARVIS @INTEGRATION @HUB @MCU_FEATURE
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import threading
import time
import tempfile
import shutil

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISIntegrationHub")


class IntegrationStatus(Enum):
    """Integration status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DEGRADED = "degraded"


class ServiceType(Enum):
    """Service types"""
    JARVIS_SYSTEM = "jarvis_system"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    CLOUD = "cloud"


@dataclass
class IntegratedService:
    """Integrated service"""
    service_id: str
    service_name: str
    service_type: ServiceType
    status: IntegrationStatus
    endpoint: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    capabilities: List[str] = field(default_factory=list)
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['service_type'] = self.service_type.value
        data['status'] = self.status.value
        if self.last_heartbeat:
            data['last_heartbeat'] = self.last_heartbeat.isoformat()
        # Don't expose credentials in dict
        if 'credentials' in data:
            data['credentials'] = "***" if data['credentials'] else None
        return data


class JARVISIntegrationHub:
    """
    JARVIS Integration Hub

    Central integration point for all JARVIS systems and external services.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize integration hub"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISIntegrationHub")

        # Integrated services
        self.services: Dict[str, IntegratedService] = {}

        # Integration state
        self.hub_active = False
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.heartbeat_interval = 60  # 1 minute

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "integration"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.services_file = self.data_dir / "services.json"

        # Integration handlers
        self.integration_handlers: Dict[str, Callable] = {}

        # Load state
        self._load_state()

        # Auto-register JARVIS systems
        self._register_jarvis_systems()

        self.logger.info("🔗 JARVIS Integration Hub initialized")
        self.logger.info(f"   Integrated services: {len(self.services)}")

    def _register_jarvis_systems(self):
        """Auto-register all JARVIS systems"""
        jarvis_systems = [
            {
                "id": "jarvis_core_intelligence",
                "name": "JARVIS Core Intelligence",
                "capabilities": ["intent_recognition", "memory_management", "context_awareness"]
            },
            {
                "id": "jarvis_proactive_monitoring",
                "name": "JARVIS Proactive Monitoring",
                "capabilities": ["system_monitoring", "predictive_analytics", "remediation"]
            },
            {
                "id": "jarvis_ai_coordination",
                "name": "JARVIS AI Coordination",
                "capabilities": ["ai_sync", "coordination", "strategic_advantage"]
            },
            {
                "id": "jarvis_security_surveillance",
                "name": "JARVIS Security Surveillance",
                "capabilities": ["threat_detection", "anomaly_detection", "security_automation"]
            },
            {
                "id": "jarvis_performance_optimizer",
                "name": "JARVIS Performance Optimizer",
                "capabilities": ["performance_monitoring", "optimization", "resource_management"]
            },
            {
                "id": "jarvis_unified_api",
                "name": "JARVIS Unified API",
                "capabilities": ["api_gateway", "request_routing", "system_communication"]
            },
            {
                "id": "jarvis_command_center",
                "name": "JARVIS Command Center",
                "capabilities": ["dashboard", "system_visualization", "user_interface"]
            }
        ]

        for system_info in jarvis_systems:
            self.register_service(
                service_id=system_info["id"],
                service_name=system_info["name"],
                service_type=ServiceType.JARVIS_SYSTEM,
                capabilities=system_info["capabilities"]
            )

    def register_service(self, service_id: str, service_name: str,
                        service_type: ServiceType, endpoint: Optional[str] = None,
                        credentials: Optional[Dict[str, Any]] = None,
                        capabilities: List[str] = None):
        """Register a service with the integration hub"""
        service = IntegratedService(
            service_id=service_id,
            service_name=service_name,
            service_type=service_type,
            status=IntegrationStatus.CONNECTED,
            endpoint=endpoint,
            credentials=credentials,
            capabilities=capabilities or [],
            last_heartbeat=datetime.now()
        )

        self.services[service_id] = service
        self._save_state()

        self.logger.info(f"📝 Registered service: {service_name} ({service_id})")

    def unregister_service(self, service_id: str):
        """Unregister a service"""
        if service_id in self.services:
            service_name = self.services[service_id].service_name
            del self.services[service_id]
            self._save_state()
            self.logger.info(f"🗑️ Unregistered service: {service_name} ({service_id})")

    def update_service_status(self, service_id: str, status: IntegrationStatus):
        """Update service status"""
        if service_id in self.services:
            self.services[service_id].status = status
            self.services[service_id].last_heartbeat = datetime.now()
            self._save_state()
            self.logger.debug(f"📊 Updated status for {service_id}: {status.value}")

    def get_service(self, service_id: str) -> Optional[IntegratedService]:
        """Get service by ID"""
        return self.services.get(service_id)

    def get_services_by_type(self, service_type: ServiceType) -> List[IntegratedService]:
        """Get all services of a specific type"""
        return [s for s in self.services.values() if s.service_type == service_type]

    def get_services_by_capability(self, capability: str) -> List[IntegratedService]:
        """Get all services with a specific capability"""
        return [s for s in self.services.values() if capability in s.capabilities]

    def route_request(self, capability: str, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route a request to a service with the required capability

        Args:
            capability: Required capability
            request: Request data

        Returns:
            Response from service or None
        """
        # Find services with the capability
        capable_services = self.get_services_by_capability(capability)

        if not capable_services:
            self.logger.warning(f"No service found with capability: {capability}")
            return None

        # Select best service (prefer connected, then by type)
        best_service = None
        for service in capable_services:
            if service.status == IntegrationStatus.CONNECTED:
                if not best_service or service.service_type == ServiceType.JARVIS_SYSTEM:
                    best_service = service
                break

        if not best_service:
            # Try degraded services
            for service in capable_services:
                if service.status == IntegrationStatus.DEGRADED:
                    best_service = service
                    break

        if best_service:
            self.logger.debug(f"Routing request to {best_service.service_name} for capability: {capability}")
            # Would implement actual routing logic here
            return {"service": best_service.service_id, "status": "routed"}

        return None

    def broadcast_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast an event to all connected services"""
        self.logger.info(f"📢 Broadcasting event: {event_type}")

        for service_id, service in self.services.items():
            if service.status == IntegrationStatus.CONNECTED:
                try:
                    # Would implement actual event broadcasting
                    self.logger.debug(f"  → {service.service_name}")
                except Exception as e:
                    self.logger.error(f"Error broadcasting to {service_id}: {e}")

    def start_hub(self):
        """Start the integration hub"""
        if self.hub_active:
            return

        self.hub_active = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        self.logger.info("🔗 Integration hub started")

    def stop_hub(self):
        """Stop the integration hub"""
        self.hub_active = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        self.logger.info("🔗 Integration hub stopped")

    def _heartbeat_loop(self):
        """Heartbeat loop to check service status"""
        while self.hub_active:
            try:
                for service_id, service in self.services.items():
                    # Check if service is still alive
                    if service.last_heartbeat:
                        time_since_heartbeat = (datetime.now() - service.last_heartbeat).total_seconds()

                        # Mark as degraded if no heartbeat for 5 minutes
                        if time_since_heartbeat > 300 and service.status == IntegrationStatus.CONNECTED:
                            self.update_service_status(service_id, IntegrationStatus.DEGRADED)
                            self.logger.warning(f"⚠️ Service degraded: {service.service_name}")

                        # Mark as disconnected if no heartbeat for 15 minutes
                        if time_since_heartbeat > 900:
                            self.update_service_status(service_id, IntegrationStatus.DISCONNECTED)
                            self.logger.error(f"❌ Service disconnected: {service.service_name}")

                    # Update heartbeat for JARVIS systems (they're always available)
                    if service.service_type == ServiceType.JARVIS_SYSTEM:
                        service.last_heartbeat = datetime.now()

                time.sleep(self.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")
                time.sleep(self.heartbeat_interval)

    def _load_state(self):
        """Load integration state"""
        try:
            if self.services_file.exists():
                with open(self.services_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for service_data in data.get("services", []):
                        service = IntegratedService(
                            service_id=service_data['service_id'],
                            service_name=service_data['service_name'],
                            service_type=ServiceType(service_data['service_type']),
                            status=IntegrationStatus(service_data.get('status', 'disconnected')),
                            endpoint=service_data.get('endpoint'),
                            credentials=service_data.get('credentials'),
                            capabilities=service_data.get('capabilities', []),
                            last_heartbeat=datetime.fromisoformat(service_data['last_heartbeat']) if service_data.get('last_heartbeat') else None,
                            metadata=service_data.get('metadata', {})
                        )
                        self.services[service.service_id] = service
                self.logger.info(f"   Loaded {len(self.services)} services")
        except Exception as e:
            self.logger.error(f"Error loading integration state: {e}")

    def _save_state(self):
        """Save integration state using atomic writes"""
        max_retries = 3
        retry_delay = 0.5

        state = {
            "services": [s.to_dict() for s in self.services.values()],
            "last_updated": datetime.now().isoformat()
        }

        self._atomic_write_file(
            self.services_file,
            state,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _atomic_write_file(self, file_path: Path, data: Any, max_retries: int = 3, retry_delay: float = 0.5):
        """Atomically write data to a file with retry logic"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file = file_path.parent / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Directory not writable: {file_path.parent} - {e}")
                return
        except Exception as e:
            self.logger.error(f"Error creating directory {file_path.parent}: {e}")
            return

        for attempt in range(max_retries):
            try:
                temp_file = file_path.parent / f".{file_path.name}.tmp"

                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                if file_path.exists():
                    try:
                        file_path.unlink()
                    except PermissionError:
                        time.sleep(retry_delay * (attempt + 1))
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise

                temp_file.replace(file_path)
                return

            except PermissionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.debug(f"Permission denied, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: Permission denied after {max_retries} attempts - {e}")
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception as e:
                self.logger.error(f"Error saving state to {file_path}: {e}")
                if 'temp_file' in locals() and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                return

    def get_status_report(self) -> Dict[str, Any]:
        """Get integration hub status report"""
        status_counts = {
            status.value: len([s for s in self.services.values() if s.status == status])
            for status in IntegrationStatus
        }

        service_types = {
            service_type.value: len(self.get_services_by_type(service_type))
            for service_type in ServiceType
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "hub_active": self.hub_active,
            "total_services": len(self.services),
            "status_counts": status_counts,
            "service_types": service_types,
            "connected_services": [s.service_id for s in self.services.values() if s.status == IntegrationStatus.CONNECTED],
            "services": [s.to_dict() for s in self.services.values()]
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Integration Hub")
    parser.add_argument("--status", action="store_true", help="Get hub status")
    parser.add_argument("--start", action="store_true", help="Start integration hub")
    parser.add_argument("--stop", action="store_true", help="Stop integration hub")
    parser.add_argument("--register", nargs=4, metavar=("ID", "NAME", "TYPE", "ENDPOINT"),
                       help="Register a service")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    hub = JARVISIntegrationHub()

    if args.status:
        status = hub.get_status_report()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🔗 JARVIS Integration Hub Status")
            print("="*60)
            print(f"Hub Active: {status['hub_active']}")
            print(f"Total Services: {status['total_services']}")
            print(f"Connected: {status['status_counts']['connected']}")
            print(f"Degraded: {status['status_counts']['degraded']}")
            print(f"Disconnected: {status['status_counts']['disconnected']}")
            print("\nServices:")
            for service in status['services']:
                status_icon = "✅" if service['status'] == 'connected' else "⚠️" if service['status'] == 'degraded' else "❌"
                print(f"  {status_icon} {service['service_name']} ({service['service_type']}) - {service['status']}")

    elif args.start:
        hub.start_hub()
        print("✅ Integration hub started")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            hub.stop_hub()

    elif args.stop:
        hub.stop_hub()
        print("✅ Integration hub stopped")

    elif args.register:
        service_id, service_name, service_type_str, endpoint = args.register
        try:
            service_type = ServiceType(service_type_str)
            hub.register_service(service_id, service_name, service_type, endpoint)
            print(f"✅ Registered: {service_name} ({service_id})")
        except ValueError:
            print(f"❌ Unknown service type: {service_type_str}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()