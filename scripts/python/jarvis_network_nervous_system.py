#!/usr/bin/env python3
"""
JARVIS Network Nervous System

Maps the home lab as JARVIS's body, with all network devices, domain devices,
and hosts as the nervous system. Complete device inventory and management.

Concept:
- Home Lab = JARVIS's Body
- Network = Nervous System
- Devices/Hosts = Neurons/Nodes
- Domain = Central Nervous System
"""

import sys
import json
import socket
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
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



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DeviceType(Enum):
    """Device types in the nervous system"""
    HOST = "host"
    NAS = "nas"
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    SERVER = "server"
    WORKSTATION = "workstation"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    IOT = "iot"
    PRINTER = "printer"
    STORAGE = "storage"
    HYPERVISOR = "hypervisor"
    CONTAINER = "container"
    SERVICE = "service"
    API = "api"
    UNKNOWN = "unknown"


class DeviceStatus(Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class NervousSystemRole(Enum):
    """Role in the nervous system"""
    CORE = "core"  # Critical system (brain stem)
    PROCESSOR = "processor"  # Processing node (neuron)
    STORAGE = "storage"  # Memory/storage (synapse)
    GATEWAY = "gateway"  # Network gateway (spinal cord)
    SENSOR = "sensor"  # Monitoring/sensing (sensory neuron)
    ACTUATOR = "actuator"  # Action/control (motor neuron)
    COORDINATOR = "coordinator"  # Coordination (cerebellum)


@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str
    ip_address: str
    mac_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: List[str] = field(default_factory=list)
    status: str = "unknown"
    speed_mbps: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Device:
    """Network device in the nervous system"""
    device_id: str
    name: str
    device_type: DeviceType
    nervous_role: NervousSystemRole
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    domain: Optional[str] = None
    status: DeviceStatus = DeviceStatus.UNKNOWN
    interfaces: List[NetworkInterface] = field(default_factory=list)
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    services: List[str] = field(default_factory=list)
    ports: Dict[int, str] = field(default_factory=dict)  # port -> service
    capabilities: List[str] = field(default_factory=list)
    last_seen: Optional[datetime] = None
    first_discovered: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['device_type'] = self.device_type.value
        data['nervous_role'] = self.nervous_role.value
        data['status'] = self.status.value
        data['interfaces'] = [iface.to_dict() for iface in self.interfaces]
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        if self.first_discovered:
            data['first_discovered'] = self.first_discovered.isoformat()
        return data


@dataclass
class NetworkTopology:
    """Network topology mapping"""
    network_id: str
    network_name: str
    subnet: str
    gateway: str
    dns_servers: List[str] = field(default_factory=list)
    devices: Dict[str, Device] = field(default_factory=dict)
    connections: List[Dict[str, str]] = field(default_factory=list)
    last_scan: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'network_id': self.network_id,
            'network_name': self.network_name,
            'subnet': self.subnet,
            'gateway': self.gateway,
            'dns_servers': self.dns_servers,
            'devices': {k: v.to_dict() for k, v in self.devices.items()},
            'connections': self.connections,
            'last_scan': self.last_scan.isoformat() if self.last_scan else None,
            'device_count': len(self.devices)
        }


class JARVISNetworkNervousSystem:
    """
    JARVIS Network Nervous System

    Maps the home lab as JARVIS's body, with all network devices, domain devices,
    and hosts as the nervous system. Complete device inventory and management.

    Concept:
    - Home Lab = JARVIS's Body
    - Network = Nervous System
    - Devices/Hosts = Neurons/Nodes
    - Domain = Central Nervous System
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize network nervous system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISNervousSystem")

        # Data directories
        self.data_dir = self.project_root / "data" / "network_nervous_system"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir = self.project_root / "config"

        # Nervous system state
        self.devices: Dict[str, Device] = {}
        self.networks: Dict[str, NetworkTopology] = {}
        self.domain_devices: Set[str] = set()

        # Known devices from configuration
        self.known_devices = self._load_known_devices()

        # Discovery state
        self._discovery_running = False
        self._discovery_thread: Optional[threading.Thread] = None

        # Load existing inventory
        self._load_inventory()

        self.logger.info("✅ JARVIS Network Nervous System initialized")
        self.logger.info(f"   Devices: {len(self.devices)}")
        self.logger.info(f"   Networks: {len(self.networks)}")

    def _load_known_devices(self) -> Dict[str, Dict[str, Any]]:
        """Load known devices from configuration"""
        known = {}

        # Load from homelab config
        try:
            homelab_config = self.config_dir / "homelab_ai_ecosystem.json"
            if homelab_config.exists():
                with open(homelab_config, 'r') as f:
                    data = json.load(f)
                    # Extract device information
                    if 'ecosystem' in data:
                        for category, items in data['ecosystem'].items():
                            if isinstance(items, dict):
                                for item_id, item_data in items.items():
                                    if isinstance(item_data, dict):
                                        known[item_id] = item_data
        except Exception as e:
            self.logger.debug(f"Could not load homelab config: {e}")

        # Load from NAS config
        try:
            nas_config = self.config_dir / "lumina_nas_ssh_config.json"
            if nas_config.exists():
                with open(nas_config, 'r') as f:
                    data = json.load(f)
                    if 'nas' in data:
                        nas_data = data['nas']
                        known['nas'] = {
                            'name': 'NAS',
                            'host': nas_data.get('host', '<NAS_PRIMARY_IP>'),
                            'device_type': DeviceType.NAS.value,
                            'nervous_role': NervousSystemRole.STORAGE.value
                        }
        except Exception as e:
            self.logger.debug(f"Could not load NAS config: {e}")

        # Load from Kaiju config
        try:
            kaiju_config = self.config_dir / "kaiju_iron_legion_config.json"
            if kaiju_config.exists():
                with open(kaiju_config, 'r') as f:
                    data = json.load(f)
                    if 'endpoints' in data:
                        endpoints = data['endpoints']
                        known['kaiju'] = {
                            'name': 'KAIJU',
                            'host': endpoints.get('primary', '').replace('http://', '').replace(':11437', ''),
                            'device_type': DeviceType.HOST.value,
                            'nervous_role': NervousSystemRole.PROCESSOR.value
                        }
        except Exception as e:
            self.logger.debug(f"Could not load Kaiju config: {e}")

        return known

    def _load_inventory(self) -> None:
        """Load device inventory from disk"""
        inventory_file = self.data_dir / "device_inventory.json"
        if inventory_file.exists():
            try:
                with open(inventory_file, 'r') as f:
                    data = json.load(f)

                    # Load devices
                    if 'devices' in data:
                        for device_id, device_data in data['devices'].items():
                            device = self._device_from_dict(device_data)
                            self.devices[device_id] = device

                    # Load networks
                    if 'networks' in data:
                        for network_id, network_data in data['networks'].items():
                            network = NetworkTopology(**network_data)
                            if 'devices' in network_data:
                                for device_id, device_data in network_data['devices'].items():
                                    device = self._device_from_dict(device_data)
                                    network.devices[device_id] = device
                            self.networks[network_id] = network
            except Exception as e:
                self.logger.debug(f"Could not load inventory: {e}")

    def _device_from_dict(self, data: Dict[str, Any]) -> Device:
        """Create device from dictionary"""
        device = Device(
            device_id=data.get('device_id', ''),
            name=data.get('name', ''),
            device_type=DeviceType(data.get('device_type', 'unknown')),
            nervous_role=NervousSystemRole(data.get('nervous_role', 'processor')),
            ip_address=data.get('ip_address', ''),
            mac_address=data.get('mac_address'),
            hostname=data.get('hostname'),
            domain=data.get('domain'),
            status=DeviceStatus(data.get('status', 'unknown')),
            os_type=data.get('os_type'),
            os_version=data.get('os_version'),
            services=data.get('services', []),
            ports=data.get('ports', {}),
            capabilities=data.get('capabilities', []),
            metadata=data.get('metadata', {})
        )

        # Parse dates
        if data.get('last_seen'):
            device.last_seen = datetime.fromisoformat(data['last_seen'])
        if data.get('first_discovered'):
            device.first_discovered = datetime.fromisoformat(data['first_discovered'])

        # Load interfaces
        if 'interfaces' in data:
            for iface_data in data['interfaces']:
                iface = NetworkInterface(**iface_data)
                device.interfaces.append(iface)

        return device

    def discover_devices(self, subnet: Optional[str] = None, timeout: int = 2) -> List[Device]:
        """
        Discover devices on the network

        Args:
            subnet: Subnet to scan (e.g., "<NAS_IP>/24")
            timeout: Timeout for each host check

        Returns:
            List of discovered devices
        """
        self.logger.info("🔍 Starting network device discovery...")

        discovered = []

        # Get local network info
        if not subnet:
            subnet = self._detect_local_subnet()

        if not subnet:
            self.logger.warning("Could not detect subnet, using known devices")
            return self._discover_known_devices()

        # Scan subnet
        network_base = subnet.rsplit('.', 1)[0] if '.' in subnet else subnet

        self.logger.info(f"Scanning network: {network_base}.0/24")

        # Scan common IP ranges
        for i in range(1, 255):
            ip = f"{network_base}.{i}"
            device = self._probe_device(ip, timeout)
            if device:
                discovered.append(device)
                self.devices[device.device_id] = device
                # Update existing device if found
                if device.device_id in self.devices:
                    existing = self.devices[device.device_id]
                    existing.last_seen = datetime.now()
                    existing.status = DeviceStatus.ONLINE
                else:
                    self.devices[device.device_id] = device

        # Save inventory after discovery
        self._save_inventory()

        self.logger.info(f"✅ Discovered {len(discovered)} devices")
        return discovered

    def _detect_local_subnet(self) -> Optional[str]:
        """Detect local subnet"""
        try:
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # Extract subnet
            parts = local_ip.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except Exception as e:
            self.logger.debug(f"Could not detect subnet: {e}")

        return None

    def _probe_device(self, ip: str, timeout: int = 2) -> Optional[Device]:
        """Probe a device at IP address"""
        try:
            # Try to connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 22))  # Try SSH
            sock.close()

            if result == 0:
                # Device is reachable
                device_id = f"device_{ip.replace('.', '_')}"

                # Check if we know this device
                known_device = None
                for known_id, known_data in self.known_devices.items():
                    if known_data.get('host') == ip or known_data.get('hostname') == ip:
                        known_device = known_data
                        device_id = known_id
                        break

                # Determine device type
                device_type = DeviceType.UNKNOWN
                nervous_role = NervousSystemRole.PROCESSOR

                if known_device:
                    device_type = DeviceType(known_device.get('device_type', 'unknown'))
                    nervous_role = NervousSystemRole(known_device.get('nervous_role', 'processor'))
                elif '<NAS_PRIMARY_IP>' in ip:
                    device_type = DeviceType.NAS
                    nervous_role = NervousSystemRole.STORAGE
                elif 'kaiju' in ip.lower() or 'lesnewski' in ip.lower():
                    device_type = DeviceType.HOST
                    nervous_role = NervousSystemRole.PROCESSOR

                # Try to get hostname
                hostname = None
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    pass

                device = Device(
                    device_id=device_id,
                    name=known_device.get('name', hostname or ip) if known_device else (hostname or ip),
                    device_type=device_type,
                    nervous_role=nervous_role,
                    ip_address=ip,
                    hostname=hostname,
                    status=DeviceStatus.ONLINE,
                    first_discovered=datetime.now() if device_id not in self.devices else self.devices[device_id].first_discovered,
                    last_seen=datetime.now()
                )

                # Add interface
                iface = NetworkInterface(
                    name="primary",
                    ip_address=ip,
                    status="up"
                )
                device.interfaces.append(iface)

                # Probe services
                self._probe_services(device)

                return device
        except Exception as e:
            self.logger.debug(f"Probe {ip} failed: {e}")

        return None

    def _probe_services(self, device: Device) -> None:
        """Probe device for running services"""
        common_ports = {
            22: "ssh",
            80: "http",
            443: "https",
            8000: "api",
            11437: "ollama",
            5001: "synology",
            8080: "http-alt"
        }

        for port, service_name in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((device.ip_address, port))
                sock.close()

                if result == 0:
                    device.ports[port] = service_name
                    if service_name not in device.services:
                        device.services.append(service_name)
            except:
                pass

    def _discover_known_devices(self) -> List[Device]:
        """Discover devices from known configuration"""
        discovered = []

        for device_id, device_data in self.known_devices.items():
            host = device_data.get('host') or device_data.get('hostname')
            if not host:
                continue

            # Remove protocol if present
            host = host.replace('http://', '').replace('https://', '')
            host = host.split(':')[0]  # Remove port

            device = Device(
                device_id=device_id,
                name=device_data.get('name', device_id),
                device_type=DeviceType(device_data.get('device_type', 'host')),
                nervous_role=NervousSystemRole(device_data.get('nervous_role', 'processor')),
                ip_address=host,
                hostname=device_data.get('hostname'),
                status=DeviceStatus.ONLINE,
                first_discovered=datetime.now(),
                last_seen=datetime.now(),
                capabilities=device_data.get('capabilities', []),
                metadata=device_data
            )

            # Probe services
            self._probe_services(device)

            discovered.append(device)
            self.devices[device_id] = device

        return discovered

    def register_device(self, device: Device) -> None:
        """Register a device in the nervous system"""
        self.devices[device.device_id] = device
        if device.domain:
            self.domain_devices.add(device.device_id)
        self._save_inventory()

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)

    def get_devices_by_role(self, role: NervousSystemRole) -> List[Device]:
        """Get devices by nervous system role"""
        return [d for d in self.devices.values() if d.nervous_role == role]

    def get_devices_by_type(self, device_type: DeviceType) -> List[Device]:
        """Get devices by type"""
        return [d for d in self.devices.values() if d.device_type == device_type]

    def get_nervous_system_map(self) -> Dict[str, Any]:
        """Get complete nervous system map"""
        return {
            "timestamp": datetime.now().isoformat(),
            "concept": {
                "home_lab": "JARVIS's Body",
                "network": "Nervous System",
                "devices": "Neurons/Nodes",
                "domain": "Central Nervous System"
            },
            "devices": {k: v.to_dict() for k, v in self.devices.items()},
            "networks": {k: v.to_dict() for k, v in self.networks.items()},
            "statistics": {
                "total_devices": len(self.devices),
                "online_devices": sum(1 for d in self.devices.values() if d.status == DeviceStatus.ONLINE),
                "domain_devices": len(self.domain_devices),
                "by_role": {role.value: len(self.get_devices_by_role(role)) for role in NervousSystemRole},
                "by_type": {dtype.value: len(self.get_devices_by_type(dtype)) for dtype in DeviceType}
            }
        }

    def _save_inventory(self) -> None:
        try:
            """Save device inventory to disk"""
            inventory_file = self.data_dir / "device_inventory.json"

            data = {
                "timestamp": datetime.now().isoformat(),
                "devices": {k: v.to_dict() for k, v in self.devices.items()},
                "networks": {k: v.to_dict() for k, v in self.networks.items()},
                "domain_devices": list(self.domain_devices)
            }

            with open(inventory_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_inventory: {e}", exc_info=True)
            raise
    def start_continuous_discovery(self, interval: int = 3600) -> None:
        """Start continuous device discovery"""
        if self._discovery_running:
            return

        self._discovery_running = True
        self._discovery_thread = threading.Thread(
            target=self._discovery_loop,
            args=(interval,),
            daemon=True
        )
        self._discovery_thread.start()
        self.logger.info(f"✅ Continuous discovery started (interval: {interval}s)")

    def _discovery_loop(self, interval: int) -> None:
        """Discovery loop"""
        while self._discovery_running:
            try:
                self.discover_devices()
                self._save_inventory()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Discovery loop error: {e}")
                time.sleep(60)

    def stop_continuous_discovery(self) -> None:
        """Stop continuous discovery"""
        self._discovery_running = False
        if self._discovery_thread:
            self._discovery_thread.join(timeout=10)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Network Nervous System")
    parser.add_argument("--discover", action="store_true", help="Discover devices")
    parser.add_argument("--map", action="store_true", help="Show nervous system map")
    parser.add_argument("--devices", action="store_true", help="List all devices")
    parser.add_argument("--role", type=str, help="Filter by nervous role")
    parser.add_argument("--type", type=str, help="Filter by device type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    nervous_system = JARVISNetworkNervousSystem()

    if args.discover:
        print("\n🔍 Discovering devices...")
        devices = nervous_system.discover_devices()
        print(f"✅ Discovered {len(devices)} devices")
        for device in devices:
            print(f"  • {device.name} ({device.ip_address}) - {device.device_type.value} - {device.nervous_role.value}")

    elif args.map:
        map_data = nervous_system.get_nervous_system_map()
        if args.json:
            print(json.dumps(map_data, indent=2))
        else:
            print("\n🧠 JARVIS Network Nervous System Map")
            print("=" * 60)
            print(f"Concept: Home Lab = JARVIS's Body, Network = Nervous System")
            print(f"\nTotal Devices: {map_data['statistics']['total_devices']}")
            print(f"Online Devices: {map_data['statistics']['online_devices']}")
            print(f"Domain Devices: {map_data['statistics']['domain_devices']}")
            print("\nBy Nervous Role:")
            for role, count in map_data['statistics']['by_role'].items():
                if count > 0:
                    print(f"  • {role}: {count}")
            print("\nBy Device Type:")
            for dtype, count in map_data['statistics']['by_type'].items():
                if count > 0:
                    print(f"  • {dtype}: {count}")

    elif args.devices:
        devices = list(nervous_system.devices.values())
        if args.role:
            devices = [d for d in devices if d.nervous_role.value == args.role]
        if args.type:
            devices = [d for d in devices if d.device_type.value == args.type]

        if args.json:
            print(json.dumps([d.to_dict() for d in devices], indent=2))
        else:
            print("\n📱 Devices:")
            for device in devices:
                status_icon = "🟢" if device.status == DeviceStatus.ONLINE else "🔴"
                print(f"  {status_icon} {device.name} ({device.ip_address})")
                print(f"     Type: {device.device_type.value}, Role: {device.nervous_role.value}")
                if device.services:
                    print(f"     Services: {', '.join(device.services)}")

    else:
        parser.print_help()

