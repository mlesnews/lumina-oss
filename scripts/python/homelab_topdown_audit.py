#!/usr/bin/env python3
"""
Homelab Top-Down Audit System

Comprehensive audit of every feature, function, option, and characteristic
by device and operating system in the homelab. This is a LIVING, BREATHING
system that accounts for complexity drift in an autonomous, automatic,
symbiotic, homogeneous environment/ecosystem.

Ultimate form: Importable into MariaDB@NAS-DSM via Holocrons.

Tags: #HOMELAB #AUDIT #TOP_DOWN #LIVING #COMPLEXITY_DRIFT #MARIADB #HOLOCRON @JARVIS @LUMINA
"""

import json
import os
import platform
import socket
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pymysql

    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_topdown_audit")


@dataclass
class DeviceFeature:
    """Represents a single feature/function/option"""

    feature_id: str
    name: str
    category: str  # "hardware", "software", "service", "configuration", "capability"
    subcategory: Optional[str] = None
    description: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    enabled: bool = True
    configurable: bool = False
    default_value: Any = None
    current_value: Any = None
    dependencies: List[str] = field(default_factory=list)
    commands: List[Dict[str, Any]] = field(default_factory=list)  # Commands for this feature
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_verified: str = field(default_factory=lambda: datetime.now().isoformat())
    complexity_drift: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceAudit:
    """Complete audit of a single device"""

    device_id: str
    device_name: str
    device_type: str  # "server", "nas", "desktop", "laptop", "router", "switch", etc.
    hostname: str
    ip_address: str
    mac_address: Optional[str] = None
    operating_system: str = ""
    os_version: str = ""
    os_architecture: str = ""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    features: List[DeviceFeature] = field(default_factory=list)
    services: List[Dict[str, Any]] = field(default_factory=list)
    network_interfaces: List[Dict[str, Any]] = field(default_factory=list)
    storage_devices: List[Dict[str, Any]] = field(default_factory=list)
    installed_software: List[Dict[str, Any]] = field(default_factory=list)
    configuration_files: List[Dict[str, Any]] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_audited: str = field(default_factory=lambda: datetime.now().isoformat())
    audit_version: int = 1
    complexity_score: float = 0.0
    complexity_drift: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HomelabAudit:
    """Complete homelab audit"""

    audit_id: str
    audit_timestamp: str
    audit_version: str = "1.0.0"
    devices: List[DeviceAudit] = field(default_factory=list)
    network_topology: Dict[str, Any] = field(default_factory=dict)
    ecosystem_complexity: Dict[str, Any] = field(default_factory=dict)
    drift_detected: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeviceDiscovery:
    """Discovers devices in homelab"""

    def __init__(self):
        self.discovered_devices: List[DeviceAudit] = []

    def discover_local_device(self) -> DeviceAudit:
        """Discover local device (this machine)"""
        device = DeviceAudit(
            device_id=f"local_{socket.gethostname()}",
            device_name=socket.gethostname(),
            device_type=self._detect_device_type(),
            hostname=socket.gethostname(),
            ip_address=self._get_local_ip(),
            operating_system=platform.system(),
            os_version=platform.version(),
            os_architecture=platform.machine(),
        )

        # Get MAC address
        device.mac_address = self._get_mac_address()

        # Detect manufacturer/model
        device.manufacturer, device.model = self._detect_hardware_info()

        return device

    def discover_network_devices(self, network_range: List[str]) -> List[DeviceAudit]:
        """Discover devices on network"""
        devices = []

        # Known devices from config
        known_devices = self._load_known_devices()
        devices.extend(known_devices)

        # Network scan (ping sweep)
        for ip in network_range:
            if self._ping_host(ip):
                device = self._probe_device(ip)
                if device:
                    devices.append(device)

        return devices

    def _detect_device_type(self) -> str:
        """Detect device type"""
        system = platform.system().lower()
        if "windows" in system:
            return "desktop" if "server" not in platform.platform().lower() else "server"
        elif "linux" in system:
            # Check if NAS (Synology)
            if os.path.exists("/etc/synoinfo.conf"):
                return "nas"
            return "server"
        elif "darwin" in system:
            return "laptop"
        return "unknown"

    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _get_mac_address(self) -> Optional[str]:
        """Get MAC address"""
        try:
            import uuid

            return ":".join(
                [f"{(uuid.getnode() >> elements) & 0xFF:02x}" for elements in range(0, 2 * 6, 2)][
                    ::-1
                ]
            )
        except:
            return None

    def _detect_hardware_info(self) -> tuple:
        """Detect hardware manufacturer and model"""
        manufacturer = None
        model = None

        if platform.system() == "Windows":
            try:
                import wmi

                c = wmi.WMI()
                system = c.Win32_ComputerSystem()[0]
                manufacturer = system.Manufacturer
                model = system.Model
            except:
                pass
        elif platform.system() == "Linux":
            try:
                with open("/sys/class/dmi/id/product_name") as f:
                    model = f.read().strip()
                with open("/sys/class/dmi/id/sys_vendor") as f:
                    manufacturer = f.read().strip()
            except:
                pass

        return manufacturer, model

    def _load_known_devices(self) -> List[DeviceAudit]:
        """Load known devices from config"""
        devices = []

        # Load from homelab config
        config_path = project_root / "config" / "homelab_ai_ecosystem.json"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

                # Extract device info from infrastructure
                infrastructure = (
                    config.get("entity_taxonomy", {})
                    .get("technical_systems", {})
                    .get("infrastructure", {})
                )

                # Known IPs from endpoint registry
                registry_path = project_root / "config" / "cluster_endpoint_registry.json"
                if registry_path.exists():
                    with open(registry_path, encoding="utf-8") as f:
                        registry = json.load(f)
                        ip_mappings = registry.get("ip_mappings", {})

                        for name, ip in ip_mappings.items():
                            device = DeviceAudit(
                                device_id=f"known_{name}",
                                device_name=name,
                                device_type="nas" if "nas" in name.lower() else "server",
                                hostname=name,
                                ip_address=ip,
                                operating_system="Synology DSM"
                                if "nas" in name.lower()
                                else "Unknown",
                            )
                            devices.append(device)

        return devices

    def _ping_host(self, ip: str, timeout: float = 1.0) -> bool:
        """Ping host to check if alive"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip],
                    capture_output=True,
                    timeout=timeout + 1,
                )
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", str(timeout), ip],
                    capture_output=True,
                    timeout=timeout + 1,
                )
            return result.returncode == 0
        except:
            return False

    def _probe_device(self, ip: str) -> Optional[DeviceAudit]:
        """Probe device for information"""
        # Try SSH
        # Try HTTP/HTTPS
        # Try SNMP
        # Try WMI (Windows)
        # Return basic device info
        return DeviceAudit(
            device_id=f"discovered_{ip.replace('.', '_')}",
            device_name=f"Device-{ip}",
            device_type="unknown",
            hostname=ip,
            ip_address=ip,
            operating_system="Unknown",
        )


class FeatureEnumerator:
    """Enumerates all features/functions/options for a device"""

    def enumerate_device_features(self, device: DeviceAudit) -> DeviceAudit:
        """Enumerate all features for a device"""
        # Hardware features
        device.features.extend(self._enumerate_hardware_features(device))

        # Operating system features
        device.features.extend(self._enumerate_os_features(device))

        # Software features
        device.features.extend(self._enumerate_software_features(device))

        # Service features
        device.features.extend(self._enumerate_service_features(device))

        # Network features
        device.network_interfaces = self._enumerate_network_interfaces(device)

        # Storage features
        device.storage_devices = self._enumerate_storage_devices(device)

        # Configuration features
        device.configuration_files = self._enumerate_configuration_files(device)

        # Calculate complexity score
        device.complexity_score = self._calculate_complexity_score(device)

        return device

    def _enumerate_hardware_features(self, device: DeviceAudit) -> List[DeviceFeature]:
        """Enumerate hardware features"""
        features = []

        if device.device_type == "nas":
            # Synology NAS features
            features.extend(
                [
                    DeviceFeature(
                        feature_id=f"{device.device_id}_cpu_cores",
                        name="CPU Cores",
                        category="hardware",
                        subcategory="processor",
                        value=psutil.cpu_count() if device.device_id.startswith("local_") else None,
                        unit="cores",
                    ),
                    DeviceFeature(
                        feature_id=f"{device.device_id}_ram_total",
                        name="Total RAM",
                        category="hardware",
                        subcategory="memory",
                        value=psutil.virtual_memory().total
                        if device.device_id.startswith("local_")
                        else None,
                        unit="bytes",
                    ),
                    DeviceFeature(
                        feature_id=f"{device.device_id}_raid_level",
                        name="RAID Level",
                        category="hardware",
                        subcategory="storage",
                        value=None,  # To be discovered
                        configurable=True,
                    ),
                ]
            )

        return features

    def _enumerate_os_features(self, device: DeviceAudit) -> List[DeviceFeature]:
        """Enumerate OS features"""
        features = []

        if device.operating_system == "Windows":
            features.extend(
                [
                    DeviceFeature(
                        feature_id=f"{device.device_id}_windows_features",
                        name="Windows Features",
                        category="software",
                        subcategory="os_features",
                        value=self._get_windows_features(),
                        configurable=True,
                    )
                ]
            )
        elif "Synology" in device.operating_system or device.device_type == "nas":
            features.extend(
                [
                    DeviceFeature(
                        feature_id=f"{device.device_id}_dsm_packages",
                        name="DSM Packages",
                        category="software",
                        subcategory="packages",
                        value=self._get_dsm_packages(device),
                        configurable=True,
                    ),
                    DeviceFeature(
                        feature_id=f"{device.device_id}_dsm_services",
                        name="DSM Services",
                        category="service",
                        subcategory="dsm_services",
                        value=self._get_dsm_services(device),
                        configurable=True,
                    ),
                ]
            )

        return features

    def _enumerate_software_features(self, device: DeviceAudit) -> List[DeviceFeature]:
        """Enumerate installed software"""
        features = []

        if device.device_id.startswith("local_"):
            # Local device - can enumerate installed software
            installed_software = self._get_installed_software()
            for software in installed_software:
                features.append(
                    DeviceFeature(
                        feature_id=f"{device.device_id}_software_{software['name'].replace(' ', '_')}",
                        name=software["name"],
                        category="software",
                        subcategory="installed",
                        value=software.get("version"),
                        metadata=software,
                    )
                )

        return features

    def _enumerate_service_features(self, device: DeviceAudit) -> List[DeviceFeature]:
        """Enumerate running services"""
        features = []

        if device.device_id.startswith("local_"):
            services = self._get_running_services()
            for service in services:
                features.append(
                    DeviceFeature(
                        feature_id=f"{device.device_id}_service_{service['name']}",
                        name=service["name"],
                        category="service",
                        subcategory="running",
                        value=service.get("status"),
                        enabled=service.get("status") == "running",
                        metadata=service,
                    )
                )

        return features

    def _enumerate_network_interfaces(self, device: DeviceAudit) -> List[Dict[str, Any]]:
        """Enumerate network interfaces"""
        interfaces = []

        if device.device_id.startswith("local_"):
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()

            for iface_name, addrs in net_if_addrs.items():
                interface = {
                    "name": iface_name,
                    "addresses": [],
                    "is_up": net_if_stats.get(iface_name, {}).isup
                    if iface_name in net_if_stats
                    else False,
                    "speed": net_if_stats.get(iface_name, {}).speed
                    if iface_name in net_if_stats
                    else None,
                }

                for addr in addrs:
                    interface["addresses"].append(
                        {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        }
                    )

                interfaces.append(interface)

        return interfaces

    def _enumerate_storage_devices(self, device: DeviceAudit) -> List[Dict[str, Any]]:
        """Enumerate storage devices"""
        storage = []

        if device.device_id.startswith("local_"):
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    storage.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                        }
                    )
                except:
                    pass

        return storage

    def _enumerate_configuration_files(self, device: DeviceAudit) -> List[Dict[str, Any]]:
        """Enumerate configuration files"""
        config_files = []

        # Common config locations
        config_paths = [
            project_root / "config",
            Path("/etc") if device.operating_system == "Linux" else None,
            Path(os.environ.get("APPDATA", "")) / "Cursor" / "User"
            if device.operating_system == "Windows"
            else None,
        ]

        for config_path in config_paths:
            if config_path and config_path.exists():
                for config_file in config_path.rglob("*.json"):
                    config_files.append(
                        {
                            "path": str(config_file),
                            "size": config_file.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                config_file.stat().st_mtime
                            ).isoformat(),
                        }
                    )

        return config_files

    def _calculate_complexity_score(self, device: DeviceAudit) -> float:
        """Calculate complexity score"""
        score = 0.0

        # Base complexity
        score += len(device.features) * 0.1
        score += len(device.services) * 0.2
        score += len(device.network_interfaces) * 0.15
        score += len(device.storage_devices) * 0.1
        score += len(device.installed_software) * 0.05
        score += len(device.configuration_files) * 0.02

        # Configurable features add complexity
        configurable_count = sum(1 for f in device.features if f.configurable)
        score += configurable_count * 0.3

        return round(score, 2)

    def _get_windows_features(self) -> List[str]:
        """Get Windows features"""
        # Would use DISM or PowerShell
        return []

    def _get_dsm_packages(self, device: DeviceAudit) -> List[Dict[str, Any]]:
        """Get DSM packages via API"""
        packages = []

        try:
            # Try Synology DSM API
            response = requests.get(
                f"http://{device.ip_address}:5000/webapi/query.cgi?api=SYNO.Core.Package&method=list&version=1",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                packages = data.get("data", {}).get("packages", [])
        except:
            pass

        return packages

    def _get_dsm_services(self, device: DeviceAudit) -> List[Dict[str, Any]]:
        """Get DSM services via API"""
        services = []

        try:
            # Try Synology DSM API
            response = requests.get(
                f"http://{device.ip_address}:5000/webapi/query.cgi?api=SYNO.Core.Service&method=list&version=1",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                services = data.get("data", {}).get("services", [])
        except:
            pass

        return services

    def _get_installed_software(self) -> List[Dict[str, Any]]:
        """Get installed software"""
        software = []

        if platform.system() == "Windows":
            # Use PowerShell or registry
            pass
        elif platform.system() == "Linux":
            # Use package manager
            pass

        return software

    def _get_running_services(self) -> List[Dict[str, Any]]:
        """Get running services"""
        services = []

        try:
            for proc in psutil.process_iter(["pid", "name", "status"]):
                services.append(
                    {
                        "name": proc.info["name"],
                        "pid": proc.info["pid"],
                        "status": proc.info["status"],
                    }
                )
        except:
            pass

        return services


class ComplexityDriftTracker:
    """Tracks complexity drift over time"""

    def __init__(self):
        self.drift_history: Dict[str, List[Dict[str, Any]]] = {}

    def detect_drift(
        self, current_audit: DeviceAudit, previous_audit: Optional[DeviceAudit]
    ) -> Dict[str, Any]:
        """Detect complexity drift"""
        if not previous_audit:
            return {"drift_detected": False, "changes": []}

        changes = []

        # Feature count change
        if len(current_audit.features) != len(previous_audit.features):
            changes.append(
                {
                    "type": "feature_count",
                    "previous": len(previous_audit.features),
                    "current": len(current_audit.features),
                    "delta": len(current_audit.features) - len(previous_audit.features),
                }
            )

        # Complexity score change
        if current_audit.complexity_score != previous_audit.complexity_score:
            changes.append(
                {
                    "type": "complexity_score",
                    "previous": previous_audit.complexity_score,
                    "current": current_audit.complexity_score,
                    "delta": current_audit.complexity_score - previous_audit.complexity_score,
                }
            )

        # New features
        current_feature_ids = {f.feature_id for f in current_audit.features}
        previous_feature_ids = {f.feature_id for f in previous_audit.features}
        new_features = current_feature_ids - previous_feature_ids

        if new_features:
            changes.append(
                {"type": "new_features", "count": len(new_features), "features": list(new_features)}
            )

        # Removed features
        removed_features = previous_feature_ids - current_feature_ids
        if removed_features:
            changes.append(
                {
                    "type": "removed_features",
                    "count": len(removed_features),
                    "features": list(removed_features),
                }
            )

        return {
            "drift_detected": len(changes) > 0,
            "changes": changes,
            "timestamp": datetime.now().isoformat(),
        }


class HomelabTopDownAuditor:
    """Main auditor class"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.audit_dir = project_root / "data" / "homelab_audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.discovery = DeviceDiscovery()
        self.enumerator = FeatureEnumerator()
        self.drift_tracker = ComplexityDriftTracker()
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

    def run_full_audit(self, scan_network: bool = True) -> HomelabAudit:
        """Run complete top-down audit"""
        logger.info("Starting comprehensive homelab audit...")

        audit = HomelabAudit(
            audit_id=f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            audit_timestamp=datetime.now().isoformat(),
        )

        # Discover devices
        logger.info("Discovering devices...")
        devices = []

        # Local device
        local_device = self.discovery.discover_local_device()
        local_device = self.enumerator.enumerate_device_features(local_device)
        devices.append(local_device)

        # Network devices
        if scan_network:
            network_range = self._get_network_range()
            network_devices = self.discovery.discover_network_devices(network_range)
            for device in network_devices:
                device = self.enumerator.enumerate_device_features(device)
                devices.append(device)

        audit.devices = devices

        # Detect drift
        logger.info("Detecting complexity drift...")
        for device in devices:
            previous_audit = self._load_previous_audit(device.device_id)
            drift = self.drift_tracker.detect_drift(device, previous_audit)
            device.complexity_drift = drift
            if drift["drift_detected"]:
                audit.drift_detected.append(
                    {
                        "device_id": device.device_id,
                        "device_name": device.device_name,
                        "drift": drift,
                    }
                )

        # Calculate ecosystem complexity
        audit.ecosystem_complexity = self._calculate_ecosystem_complexity(audit)

        # Save audit
        self._save_audit(audit)

        logger.info(
            f"Audit complete: {len(devices)} devices, {sum(len(d.features) for d in devices)} features"
        )

        return audit

    def start_living_audit(self, interval_seconds: int = 3600):
        """Start living audit (auto-updates)"""
        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                try:
                    logger.info("Running scheduled audit...")
                    self.run_full_audit(scan_network=False)  # Local only for speed
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Retry after 1 minute

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Living audit started (interval: {interval_seconds}s)")

    def stop_living_audit(self):
        """Stop living audit"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Living audit stopped")

    def _get_network_range(self) -> List[str]:
        """Get network range to scan"""
        # From endpoint registry or config
        registry_path = project_root / "config" / "cluster_endpoint_registry.json"
        if registry_path.exists():
            with open(registry_path, encoding="utf-8") as f:
                registry = json.load(f)
                ip_mappings = registry.get("ip_mappings", {})
                return list(set(ip_mappings.values()))

        # Default: common homelab IPs
        return ["<NAS_IP>", "<NAS_PRIMARY_IP>", "<NAS_IP>", "<NAS_IP>"]

    def _load_previous_audit(self, device_id: str) -> Optional[DeviceAudit]:
        """Load previous audit for device"""
        # Find most recent audit file
        audit_files = sorted(self.audit_dir.glob("audit_*.json"), reverse=True)

        for audit_file in audit_files[:5]:  # Check last 5 audits
            try:
                with open(audit_file, encoding="utf-8") as f:
                    audit_data = json.load(f)
                    for device_data in audit_data.get("devices", []):
                        if device_data.get("device_id") == device_id:
                            # Convert back to DeviceAudit
                            return self._dict_to_device_audit(device_data)
            except:
                continue

        return None

    def _dict_to_device_audit(self, data: Dict[str, Any]) -> DeviceAudit:
        """Convert dict to DeviceAudit"""
        features = [DeviceFeature(**f) for f in data.get("features", [])]
        return DeviceAudit(
            device_id=data["device_id"],
            device_name=data["device_name"],
            device_type=data["device_type"],
            hostname=data["hostname"],
            ip_address=data["ip_address"],
            features=features,
            complexity_score=data.get("complexity_score", 0.0),
        )

    def _calculate_ecosystem_complexity(self, audit: HomelabAudit) -> Dict[str, Any]:
        """Calculate ecosystem-level complexity"""
        total_features = sum(len(d.features) for d in audit.devices)
        total_complexity = sum(d.complexity_score for d in audit.devices)
        avg_complexity = total_complexity / len(audit.devices) if audit.devices else 0

        return {
            "total_devices": len(audit.devices),
            "total_features": total_features,
            "total_complexity_score": total_complexity,
            "average_complexity_score": round(avg_complexity, 2),
            "complexity_trend": "increasing" if audit.drift_detected else "stable",
        }

    def _save_audit(self, audit: HomelabAudit):
        """Save audit to file"""
        audit_file = self.audit_dir / f"{audit.audit_id}.json"

        # Convert to dict
        audit_dict = {
            "audit_id": audit.audit_id,
            "audit_timestamp": audit.audit_timestamp,
            "audit_version": audit.audit_version,
            "devices": [asdict(d) for d in audit.devices],
            "ecosystem_complexity": audit.ecosystem_complexity,
            "drift_detected": audit.drift_detected,
            "metadata": audit.metadata,
        }

        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_dict, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Audit saved: {audit_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab Top-Down Audit System")
    parser.add_argument("--audit", action="store_true", help="Run full audit")
    parser.add_argument("--no-network-scan", action="store_true", help="Skip network scanning")
    parser.add_argument("--living", action="store_true", help="Start living audit (auto-updates)")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Living audit interval in seconds (default: 3600)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    auditor = HomelabTopDownAuditor(project_root)

    if args.living:
        auditor.start_living_audit(interval_seconds=args.interval)
        print("Living audit started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            auditor.stop_living_audit()
            print("\nLiving audit stopped.")
    elif args.audit:
        audit = auditor.run_full_audit(scan_network=not args.no_network_scan)

        if args.json:
            print(json.dumps(asdict(audit), indent=2, default=str))
        else:
            print(f"Audit complete: {audit.audit_id}")
            print(f"Devices: {len(audit.devices)}")
            print(f"Total Features: {sum(len(d.features) for d in audit.devices)}")
            print(f"Drift Detected: {len(audit.drift_detected)}")
    else:
        # Default: run audit
        audit = auditor.run_full_audit(scan_network=not args.no_network_scan)
        print(f"Audit complete: {audit.audit_id}")


if __name__ == "__main__":
    main()
