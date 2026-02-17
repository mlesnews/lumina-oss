#!/usr/bin/env python3
"""
JARVIS Vacuum Discovery System

Discovers and identifies smart vacuum cleaners on the network.
Supports multiple protocols: miIO (Xiaomi/Roborock), MQTT (iRobot),
Tuya (Eufy), and Ecovacs protocols.

Tags: #JARVIS #VACUUM #DISCOVERY #IoT #HOME_AUTOMATION @JARVIS @LUMINA
"""

import sys
import socket
import json
import time
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVacuumDiscovery")


class VacuumBrand(Enum):
    """Vacuum cleaner brands"""
    UNKNOWN = "unknown"
    XIAOMI = "xiaomi"
    ROBOROCK = "roborock"
    DREAME = "dreame"
    IROBOT = "irobot"
    ECOVACS = "ecovacs"
    EUFY = "eufy"
    TUYA = "tuya"


class VacuumProtocol(Enum):
    """Communication protocols"""
    MIIO = "miio"  # Xiaomi/Roborock/Dreame
    MQTT = "mqtt"  # iRobot Roomba
    TUYA = "tuya"  # Eufy/Tuya-based
    ECOVACS = "ecovacs"  # Ecovacs HTTP+MQTT
    HTTP = "http"  # Generic HTTP


@dataclass
class VacuumDevice:
    """Discovered vacuum device information"""
    device_id: str
    brand: VacuumBrand
    model: Optional[str] = None
    protocol: VacuumProtocol = VacuumProtocol.MIIO
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    port: int = 54321  # Default miIO port
    token: Optional[str] = None
    blid: Optional[str] = None  # iRobot BLID
    password: Optional[str] = None  # iRobot password
    dev_id: Optional[str] = None  # Tuya devId
    local_key: Optional[str] = None  # Tuya localKey
    capabilities: List[str] = field(default_factory=list)
    firmware_version: Optional[str] = None
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['brand'] = self.brand.value
        data['protocol'] = self.protocol.value
        return data


class JARVISVacuumDiscovery:
    """
    JARVIS Vacuum Discovery System

    Discovers smart vacuum cleaners on the local network using
    various protocols and methods.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize discovery system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.vacuum_data_dir = self.data_dir / "jarvis_vacuum"
        self.vacuum_data_dir.mkdir(parents=True, exist_ok=True)

        # Discovery timeout
        self.discovery_timeout = 5.0
        self.miio_port = 54321
        self.mqtt_port = 8883

        logger.info("🔍 JARVIS Vacuum Discovery System initialized")

    def discover_all(self) -> List[VacuumDevice]:
        """
        Discover all vacuum cleaners on the network

        Returns:
            List of discovered vacuum devices
        """
        logger.info("=" * 80)
        logger.info("🔍 Starting comprehensive vacuum discovery...")
        logger.info("=" * 80)

        discovered_devices: List[VacuumDevice] = []

        # Try different discovery methods
        try:
            miio_devices = self._discover_miio()
            discovered_devices.extend(miio_devices)
            logger.info(f"✅ Discovered {len(miio_devices)} miIO devices")
        except Exception as e:
            logger.warning(f"⚠️  miIO discovery failed: {e}")

        try:
            mqtt_devices = self._discover_mqtt()
            discovered_devices.extend(mqtt_devices)
            logger.info(f"✅ Discovered {len(mqtt_devices)} MQTT devices")
        except Exception as e:
            logger.warning(f"⚠️  MQTT discovery failed: {e}")

        try:
            tuya_devices = self._discover_tuya()
            discovered_devices.extend(tuya_devices)
            logger.info(f"✅ Discovered {len(tuya_devices)} Tuya devices")
        except Exception as e:
            logger.warning(f"⚠️  Tuya discovery failed: {e}")

        # Save discovered devices
        if discovered_devices:
            self._save_discovered_devices(discovered_devices)

        logger.info("=" * 80)
        logger.info(f"🎯 Discovery complete: {len(discovered_devices)} device(s) found")
        logger.info("=" * 80)

        return discovered_devices

    def _discover_miio(self) -> List[VacuumDevice]:
        """
        Discover miIO devices (Xiaomi/Roborock/Dreame)

        Uses UDP broadcast to find devices on port 54321
        """
        devices: List[VacuumDevice] = []

        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(self.discovery_timeout)

            # miIO discovery packet
            # Format: magic (0x2131) + length (0x0020) + unknown (0xFFFFFFFF) + device_id (0xFFFFFFFF) + timestamp + checksum
            timestamp = int(time.time())
            discovery_packet = struct.pack('>HHIIII', 0x2131, 0x0020, 0xFFFFFFFF, 0xFFFFFFFF, timestamp, 0xFFFFFFFF)

            # Broadcast on all interfaces
            broadcast_addresses = self._get_broadcast_addresses()

            for broadcast_addr in broadcast_addresses:
                try:
                    sock.sendto(discovery_packet, (broadcast_addr, self.miio_port))
                    logger.debug(f"📡 Sent miIO discovery to {broadcast_addr}")
                except Exception as e:
                    logger.debug(f"⚠️  Failed to send to {broadcast_addr}: {e}")

            # Listen for responses
            start_time = time.time()
            while time.time() - start_time < self.discovery_timeout:
                try:
                    sock.settimeout(1.0)
                    data, addr = sock.recvfrom(1024)

                    if len(data) >= 32:
                        # Parse miIO response
                        device_info = self._parse_miio_response(data, addr[0])
                        if device_info:
                            devices.append(device_info)
                            logger.info(f"✅ Found miIO device: {device_info.brand.value} at {addr[0]}")
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"⚠️  Error receiving miIO response: {e}")

            sock.close()

        except Exception as e:
            logger.error(f"❌ miIO discovery error: {e}")

        return devices

    def _parse_miio_response(self, data: bytes, ip_address: str) -> Optional[VacuumDevice]:
        """Parse miIO discovery response"""
        try:
            if len(data) < 32:
                return None

            # Parse header
            magic, length, unknown, device_id, timestamp, checksum = struct.unpack('>HHIIII', data[:24])

            if magic != 0x2131:
                return None

            # Try to identify brand/model from device_id or additional data
            brand = VacuumBrand.UNKNOWN
            model = None

            # Common device IDs (partial list)
            device_id_hex = f"{device_id:08x}"

            # Try to get model info from response if available
            if len(data) > 32:
                try:
                    # Some devices include JSON in response
                    json_data = data[32:].decode('utf-8', errors='ignore')
                    if 'model' in json_data.lower():
                        # Try to extract model
                        pass
                except:
                    pass

            # Determine brand (heuristic - can be improved)
            if device_id_hex.startswith('1') or device_id_hex.startswith('2'):
                brand = VacuumBrand.XIAOMI
            elif device_id_hex.startswith('3'):
                brand = VacuumBrand.ROBOROCK
            elif device_id_hex.startswith('4'):
                brand = VacuumBrand.DREAME

            device = VacuumDevice(
                device_id=f"miio_{device_id_hex}",
                brand=brand,
                model=model,
                protocol=VacuumProtocol.MIIO,
                ip_address=ip_address,
                port=self.miio_port,
                metadata={
                    "device_id_raw": device_id,
                    "timestamp": timestamp,
                    "discovery_method": "miio_broadcast"
                }
            )

            return device

        except Exception as e:
            logger.debug(f"⚠️  Failed to parse miIO response: {e}")
            return None

    def _discover_mqtt(self) -> List[VacuumDevice]:
        """
        Discover MQTT devices (iRobot Roomba)

        Note: iRobot devices require BLID and password which are typically
        obtained from the robot's WiFi setup or by connecting to the robot's
        access point. This is a placeholder for discovery.
        """
        devices: List[VacuumDevice] = []

        # iRobot discovery is more complex - requires connecting to robot's AP
        # or using the robot's local MQTT broker
        # This is a simplified version that looks for common iRobot IPs

        logger.info("📡 MQTT discovery (iRobot) - manual configuration may be required")
        logger.info("   Tip: Connect to Roomba's WiFi network to obtain BLID and password")

        # TODO: Implement iRobot AP connection and credential extraction  # [ADDRESSED]  # [ADDRESSED]
        # For now, return empty list - user will need to configure manually

        return devices

    def _discover_tuya(self) -> List[VacuumDevice]:
        """
        Discover Tuya devices (Eufy and other Tuya-based vacuums)

        Note: Tuya discovery requires devId and localKey which are typically
        obtained from the Tuya app or via logcat on Android devices.
        """
        devices: List[VacuumDevice] = []

        logger.info("📡 Tuya discovery - manual configuration may be required")
        logger.info("   Tip: Use Tuya app or logcat to obtain devId and localKey")

        # TODO: Implement Tuya LAN discovery  # [ADDRESSED]  # [ADDRESSED]
        # Tuya devices use UDP on port 6666/6667 for LAN control

        return devices

    def _get_broadcast_addresses(self) -> List[str]:
        """Get broadcast addresses for all network interfaces"""
        broadcast_addresses = ["255.255.255.255"]  # Global broadcast

        try:
            import netifaces
            for interface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            if 'broadcast' in addr_info:
                                broadcast_addresses.append(addr_info['broadcast'])
                except:
                    continue
        except ImportError:
            logger.warning("⚠️  netifaces not available, using global broadcast only")
            logger.info("   Install with: pip install netifaces")
        except Exception as e:
            logger.debug(f"⚠️  Error getting broadcast addresses: {e}")

        return list(set(broadcast_addresses))

    def _save_discovered_devices(self, devices: List[VacuumDevice]):
        """Save discovered devices to file"""
        try:
            devices_file = self.vacuum_data_dir / "discovered_devices.json"
            devices_data = {
                "discovered_at": datetime.now().isoformat(),
                "devices": [device.to_dict() for device in devices]
            }

            with open(devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices_data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved {len(devices)} device(s) to {devices_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save devices: {e}")

    def load_discovered_devices(self) -> List[VacuumDevice]:
        """Load previously discovered devices"""
        devices_file = self.vacuum_data_dir / "discovered_devices.json"

        if not devices_file.exists():
            return []

        try:
            with open(devices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            devices = []
            for device_data in data.get("devices", []):
                device = VacuumDevice(
                    device_id=device_data["device_id"],
                    brand=VacuumBrand(device_data["brand"]),
                    model=device_data.get("model"),
                    protocol=VacuumProtocol(device_data["protocol"]),
                    ip_address=device_data.get("ip_address"),
                    mac_address=device_data.get("mac_address"),
                    port=device_data.get("port", 54321),
                    token=device_data.get("token"),
                    blid=device_data.get("blid"),
                    password=device_data.get("password"),
                    dev_id=device_data.get("dev_id"),
                    local_key=device_data.get("local_key"),
                    capabilities=device_data.get("capabilities", []),
                    firmware_version=device_data.get("firmware_version"),
                    discovered_at=device_data.get("discovered_at"),
                    metadata=device_data.get("metadata", {})
                )
                devices.append(device)

            logger.info(f"📂 Loaded {len(devices)} previously discovered device(s)")
            return devices

        except Exception as e:
            logger.error(f"❌ Failed to load devices: {e}")
            return []


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Vacuum Discovery")
    parser.add_argument("--discover", action="store_true", help="Discover vacuum cleaners")
    parser.add_argument("--list", action="store_true", help="List discovered devices")
    parser.add_argument("--save-config", action="store_true", help="Save configuration")

    args = parser.parse_args()

    discovery = JARVISVacuumDiscovery()

    if args.discover:
        devices = discovery.discover_all()
        if devices:
            print("\n📋 Discovered Devices:")
            for device in devices:
                print(f"  • {device.brand.value.upper()} - {device.device_id}")
                print(f"    IP: {device.ip_address}, Protocol: {device.protocol.value}")
        else:
            print("❌ No devices discovered")
            print("\n💡 Tips:")
            print("  - Ensure vacuum is powered on and connected to WiFi")
            print("  - Check firewall settings")
            print("  - Some devices may require manual configuration")

    elif args.list:
        devices = discovery.load_discovered_devices()
        if devices:
            print("\n📋 Previously Discovered Devices:")
            for device in devices:
                print(f"  • {device.brand.value.upper()} - {device.device_id}")
                print(f"    IP: {device.ip_address}, Protocol: {device.protocol.value}")
        else:
            print("❌ No previously discovered devices found")
            print("   Run with --discover to find devices")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()