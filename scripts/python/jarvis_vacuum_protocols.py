#!/usr/bin/env python3
"""
JARVIS Vacuum Protocol Handlers

Protocol implementations for different vacuum cleaner brands:
- miIO (Xiaomi/Roborock/Dreame)
- MQTT (iRobot Roomba)
- Tuya (Eufy)
- Ecovacs

Tags: #JARVIS #VACUUM #PROTOCOL #IoT @JARVIS @LUMINA
"""

import sys
import socket
import json
import time
import struct
import hashlib
import hmac
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging

# Crypto imports for miIO encryption
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    CRYPTO_AVAILABLE = True
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import padding
        CRYPTO_AVAILABLE = True
        CRYPTO_BACKEND = "cryptography"
    except ImportError:
        CRYPTO_AVAILABLE = False
        CRYPTO_BACKEND = None

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

logger = get_logger("JARVISVacuumProtocols")


class VacuumState(Enum):
    """Vacuum cleaner states"""
    IDLE = "idle"
    CLEANING = "cleaning"
    RETURNING = "returning"
    CHARGING = "charging"
    PAUSED = "paused"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class VacuumStatus:
    """Vacuum cleaner status"""
    state: VacuumState
    battery_level: Optional[int] = None  # 0-100
    is_charging: bool = False
    is_docked: bool = False
    cleaning_time: Optional[int] = None  # seconds
    area_cleaned: Optional[float] = None  # square meters
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    fan_speed: Optional[int] = None
    water_level: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VacuumProtocolHandler(ABC):
    """Base class for vacuum protocol handlers"""

    def __init__(self, ip_address: str, port: int = 54321):
        self.ip_address = ip_address
        self.port = port
        self.logger = get_logger(f"VacuumProtocol_{self.__class__.__name__}")

    @abstractmethod
    def connect(self) -> bool:
        """Connect to vacuum cleaner"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from vacuum cleaner"""
        pass

    @abstractmethod
    def get_status(self) -> Optional[VacuumStatus]:
        """Get current vacuum status"""
        pass

    @abstractmethod
    def start_cleaning(self) -> bool:
        """Start cleaning"""
        pass

    @abstractmethod
    def stop_cleaning(self) -> bool:
        """Stop cleaning"""
        pass

    @abstractmethod
    def return_to_dock(self) -> bool:
        """Return to charging dock"""
        pass

    @abstractmethod
    def pause(self) -> bool:
        """Pause cleaning"""
        pass

    @abstractmethod
    def resume(self) -> bool:
        """Resume cleaning"""
        pass


class MiIOProtocolHandler(VacuumProtocolHandler):
    """
    miIO Protocol Handler (Xiaomi/Roborock/Dreame)

    Uses UDP on port 54321 with token-based authentication
    """

    def __init__(self, ip_address: str, token: Optional[str] = None, port: int = 54321):
        super().__init__(ip_address, port)
        self.token = token
        self.socket: Optional[socket.socket] = None
        self.device_id = 0xFFFFFFFF
        self.stamp = 0

    def connect(self) -> bool:
        """Connect to miIO device"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)

            # If no token, try to get one via handshake
            if not self.token:
                self.logger.warning("⚠️  No token provided, attempting handshake...")
                # Handshake would go here - requires device interaction

            return True
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from device"""
        if self.socket:
            self.socket.close()
            self.socket = None

    def _send_command(self, method: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """Send miIO command"""
        if not self.socket:
            if not self.connect():
                return None

        if params is None:
            params = []

        # Build JSON-RPC request
        request = {
            "id": int(time.time()),
            "method": method,
            "params": params
        }

        # Encode request
        request_json = json.dumps(request, separators=(',', ':')).encode('utf-8')

        # Build miIO packet
        packet = self._build_miio_packet(request_json)

        try:
            # Send packet
            self.socket.sendto(packet, (self.ip_address, self.port))

            # Receive response
            data, addr = self.socket.recvfrom(4096)

            # Parse response
            response = self._parse_miio_packet(data)
            return response

        except socket.timeout:
            self.logger.error("❌ Request timeout")
            return None
        except Exception as e:
            self.logger.error(f"❌ Command failed: {e}")
            return None

    def _build_miio_packet(self, data: bytes) -> bytes:
        """Build miIO protocol packet"""
        # miIO packet format:
        # Header (32 bytes): magic, length, unknown, device_id, stamp, checksum
        # Data: encrypted JSON

        stamp = int(time.time())

        # If we have a token, encrypt the data
        if self.token:
            encrypted_data = self._encrypt_miio(data, self.token, stamp)
        else:
            # Without token, send unencrypted (handshake)
            encrypted_data = data

        length = 32 + len(encrypted_data)

        # Build header with placeholder checksum
        header = struct.pack('>HHIIII',
            0x2131,  # magic
            length,
            0xFFFFFFFF,  # unknown
            self.device_id,
            stamp,
            0xFFFFFFFF  # checksum (will be calculated)
        )

        # Calculate checksum over header + encrypted data
        packet_data = header + encrypted_data
        checksum = self._calculate_miio_checksum(packet_data)

        # Rebuild header with actual checksum
        header = struct.pack('>HHIIII',
            0x2131,
            length,
            0xFFFFFFFF,
            self.device_id,
            stamp,
            checksum
        )

        return header + encrypted_data

    def _parse_miio_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parse miIO protocol packet"""
        if len(data) < 32:
            return None

        try:
            # Parse header
            magic, length, unknown, device_id, stamp, checksum = struct.unpack('>HHIIII', data[:32])

            if magic != 0x2131:
                return None

            # Verify packet length
            if len(data) < length:
                return None

            # Verify checksum
            calculated_checksum = self._calculate_miio_checksum(data)
            if calculated_checksum != checksum:
                self.logger.warning("⚠️  Checksum mismatch in miIO packet")

            # Extract encrypted data
            encrypted_data = data[32:length]

            # Decrypt if we have token
            if self.token:
                decrypted_data = self._decrypt_miio(encrypted_data, self.token, stamp)
            else:
                decrypted_data = encrypted_data

            # Parse JSON
            try:
                response = json.loads(decrypted_data.decode('utf-8', errors='ignore'))
                return response
            except json.JSONDecodeError as e:
                self.logger.debug(f"⚠️  JSON decode error: {e}")
                return None
        except struct.error as e:
            self.logger.debug(f"⚠️  Packet parse error: {e}")
            return None

    def _encrypt_miio(self, data: bytes, token: str, stamp: int) -> bytes:
        """Encrypt miIO data using AES-128-CBC"""
        if not CRYPTO_AVAILABLE:
            self.logger.error("❌ Crypto library not available. Install pycryptodome or cryptography")
            return data

        try:
            # Convert token to bytes
            if len(token) == 32 and all(c in '0123456789abcdefABCDEF' for c in token):
                token_bytes = bytes.fromhex(token)
            else:
                token_bytes = token.encode('utf-8')[:16].ljust(16, b'\x00')

            # Generate key and IV as per miIO protocol
            key = hashlib.md5(token_bytes).digest()
            iv = hashlib.md5(key + struct.pack('>I', stamp)).digest()[:16]

            # Pad data to AES block size (16 bytes)
            if CRYPTO_BACKEND == "cryptography":
                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(data) + padder.finalize()
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                encryptor = cipher.encryptor()
                encrypted = encryptor.update(padded_data) + encryptor.finalize()
            else:
                # PyCryptoDome
                padded_data = pad(data, AES.block_size)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                encrypted = cipher.encrypt(padded_data)

            return encrypted
        except Exception as e:
            self.logger.error(f"❌ Encryption failed: {e}")
            return data

    def _decrypt_miio(self, data: bytes, token: str, stamp: int) -> bytes:
        """Decrypt miIO data using AES-128-CBC"""
        if not CRYPTO_AVAILABLE:
            self.logger.error("❌ Crypto library not available. Install pycryptodome or cryptography")
            return data

        try:
            # Convert token to bytes
            if len(token) == 32 and all(c in '0123456789abcdefABCDEF' for c in token):
                token_bytes = bytes.fromhex(token)
            else:
                token_bytes = token.encode('utf-8')[:16].ljust(16, b'\x00')

            # Generate key and IV as per miIO protocol
            key = hashlib.md5(token_bytes).digest()
            iv = hashlib.md5(key + struct.pack('>I', stamp)).digest()[:16]

            # Decrypt
            if CRYPTO_BACKEND == "cryptography":
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted = decryptor.update(data) + decryptor.finalize()
                unpadder = padding.PKCS7(128).unpadder()
                unpadded = unpadder.update(decrypted) + unpadder.finalize()
            else:
                # PyCryptoDome
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(data)
                unpadded = unpad(decrypted, AES.block_size)

            return unpadded
        except Exception as e:
            self.logger.error(f"❌ Decryption failed: {e}")
            return data

    def _calculate_miio_checksum(self, data: bytes) -> int:
        """Calculate miIO packet checksum (CRC32 of data)"""
        try:
            import zlib
            checksum = zlib.crc32(data) & 0xFFFFFFFF
            return checksum
        except Exception:
            # Fallback to simple sum
            return sum(data) & 0xFFFFFFFF

    def get_status(self) -> Optional[VacuumStatus]:
        """Get vacuum status"""
        # Try multiple status commands for different device types
        status_commands = ["get_status", "get_prop", "get_clean_state"]

        response = None
        for cmd in status_commands:
            response = self._send_command(cmd)
            if response and 'result' in response:
                break

        if not response or 'result' not in response:
            self.logger.warning("⚠️  Failed to get status from device")
            return VacuumStatus(
                state=VacuumState.UNKNOWN,
                metadata={"error": "No response from device"}
            )

        result = response['result']
        metadata = {"raw_response": result, "command_used": cmd}

        # Parse status based on device type
        # Different models return different formats
        if isinstance(result, list):
            if len(result) > 0:
                state_value = result[0]
            else:
                state_value = None
        elif isinstance(result, dict):
            state_value = result.get("state", result.get("clean_state", None))
        else:
            state_value = result

        # Map miIO states to VacuumState
        state_map = {
            1: VacuumState.IDLE,
            2: VacuumState.CLEANING,
            3: VacuumState.RETURNING,
            4: VacuumState.CHARGING,
            5: VacuumState.ERROR,
            6: VacuumState.PAUSED,
            "idle": VacuumState.IDLE,
            "cleaning": VacuumState.CLEANING,
            "returning": VacuumState.RETURNING,
            "charging": VacuumState.CHARGING,
            "error": VacuumState.ERROR,
            "paused": VacuumState.PAUSED,
        }

        state = state_map.get(state_value, VacuumState.UNKNOWN)

        # Extract battery, cleaning time, area, etc.
        battery = None
        is_charging = False
        is_docked = False
        cleaning_time = None
        area_cleaned = None
        fan_speed = None

        if isinstance(result, list):
            if len(result) > 1:
                battery = result[1] if isinstance(result[1], (int, float)) else None
            if len(result) > 2:
                is_charging = result[2] == 1 if isinstance(result[2], int) else False
            if len(result) > 3:
                is_docked = result[3] == 1 if isinstance(result[3], int) else False
        elif isinstance(result, dict):
            battery = result.get("battery", result.get("battery_level", None))
            is_charging = result.get("is_charging", result.get("charging", False))
            is_docked = result.get("is_docked", result.get("docked", False))
            cleaning_time = result.get("clean_time", result.get("cleaning_time", None))
            area_cleaned = result.get("area", result.get("area_cleaned", None))
            fan_speed = result.get("fan_speed", result.get("fan_power", None))

        return VacuumStatus(
            state=state,
            battery_level=battery,
            is_charging=is_charging,
            is_docked=is_docked,
            cleaning_time=cleaning_time,
            area_cleaned=area_cleaned,
            fan_speed=fan_speed,
            metadata=metadata
        )

    def start_cleaning(self) -> bool:
        """Start cleaning"""
        commands = ["app_start", "start", "app_zoned_clean"]
        for cmd in commands:
            response = self._send_command(cmd)
            if response and 'result' in response:
                result = response['result']
                if result == ['ok'] or result == 'ok' or (isinstance(result, list) and len(result) > 0 and result[0] == 'ok'):
                    return True
        return False

    def stop_cleaning(self) -> bool:
        """Stop cleaning"""
        commands = ["app_stop", "stop"]
        for cmd in commands:
            response = self._send_command(cmd)
            if response and 'result' in response:
                result = response['result']
                if result == ['ok'] or result == 'ok' or (isinstance(result, list) and len(result) > 0 and result[0] == 'ok'):
                    return True
        return False

    def return_to_dock(self) -> bool:
        """Return to charging dock"""
        commands = ["app_charge", "app_goto_target", "charge"]
        for cmd in commands:
            response = self._send_command(cmd)
            if response and 'result' in response:
                result = response['result']
                if result == ['ok'] or result == 'ok' or (isinstance(result, list) and len(result) > 0 and result[0] == 'ok'):
                    return True
        return False

    def pause(self) -> bool:
        """Pause cleaning"""
        commands = ["app_pause", "pause"]
        for cmd in commands:
            response = self._send_command(cmd)
            if response and 'result' in response:
                result = response['result']
                if result == ['ok'] or result == 'ok' or (isinstance(result, list) and len(result) > 0 and result[0] == 'ok'):
                    return True
        return False

    def resume(self) -> bool:
        """Resume cleaning"""
        commands = ["app_resume", "resume", "app_start"]
        for cmd in commands:
            response = self._send_command(cmd)
            if response and 'result' in response:
                result = response['result']
                if result == ['ok'] or result == 'ok' or (isinstance(result, list) and len(result) > 0 and result[0] == 'ok'):
                    return True
        return False


class MQTTProtocolHandler(VacuumProtocolHandler):
    """
    MQTT Protocol Handler (iRobot Roomba)

    Uses local MQTT broker on the robot
    """

    def __init__(self, ip_address: str, blid: str, password: str, port: int = 8883):
        super().__init__(ip_address, port)
        self.blid = blid
        self.password = password
        self.client = None
        self._last_message = None

    def connect(self) -> bool:
        """Connect to Roomba MQTT broker"""
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            self.logger.error("❌ paho-mqtt not installed. Install with: pip install paho-mqtt")
            return False

        try:
            # Create MQTT client with BLID as client ID
            self.client = mqtt.Client(client_id=self.blid, protocol=mqtt.MQTTv311)
            self.client.username_pw_set(self.blid, self.password)

            # Set callbacks for connection
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    logger.info("✅ Connected to Roomba MQTT broker")
                    # Subscribe to status topics
                    client.subscribe("delta")
                    client.subscribe("state")
                else:
                    logger.error(f"❌ MQTT connection failed with code {rc}")

            def on_message(client, userdata, msg):
                # Store latest message for status retrieval
                self._last_message = msg.payload.decode('utf-8')
                logger.debug(f"📨 Received: {msg.topic} = {self._last_message}")

            self.client.on_connect = on_connect
            self.client.on_message = on_message

            # Connect to Roomba's MQTT broker
            self.client.connect(self.ip_address, self.port, 60)
            self.client.loop_start()

            # Wait for connection
            import time
            timeout = 5
            start = time.time()
            while not self.client.is_connected() and (time.time() - start) < timeout:
                time.sleep(0.1)

            if self.client.is_connected():
                return True
            else:
                self.logger.error("❌ MQTT connection timeout")
                return False

        except Exception as e:
            self.logger.error(f"❌ MQTT connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None

    def _publish_command(self, command: str, value: str = "") -> bool:
        """Publish command to Roomba"""
        if not self.client or not self.client.is_connected():
            if not self.connect():
                return False

        try:
            import paho.mqtt.client as mqtt
            # Roomba uses "cmd" topic with JSON payload
            import json
            if value:
                payload = json.dumps({"command": command, "value": value})
            else:
                payload = command

            result = self.client.publish("cmd", payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"✅ Published command: {command}")
                return True
            else:
                self.logger.error(f"❌ Failed to publish command: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Command failed: {e}")
            return False

    def get_status(self) -> Optional[VacuumStatus]:
        """Get Roomba status via MQTT"""
        if not self.client:
            return VacuumStatus(
                state=VacuumState.UNKNOWN,
                metadata={"error": "Not connected"}
            )

        try:
            # Subscribe to status topics
            status_data = {}

            # Request state update
            self.client.publish("cmd", "get_state")

            # Wait briefly for response (in real implementation, would use callbacks)
            import time
            time.sleep(0.5)

            # In full implementation, status would come from MQTT message callbacks
            # For now, return basic status
            return VacuumStatus(
                state=VacuumState.UNKNOWN,
                metadata={
                    "protocol": "mqtt",
                    "blid": self.blid,
                    "note": "Full status requires MQTT subscription callbacks"
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Status retrieval failed: {e}")
            return VacuumStatus(
                state=VacuumState.ERROR,
                error_message=str(e),
                metadata={"protocol": "mqtt"}
            )

    def start_cleaning(self) -> bool:
        """Start cleaning"""
        return self._publish_command("start", "")

    def stop_cleaning(self) -> bool:
        """Stop cleaning"""
        return self._publish_command("stop", "")

    def return_to_dock(self) -> bool:
        """Return to dock"""
        return self._publish_command("dock", "")

    def pause(self) -> bool:
        """Pause cleaning"""
        return self._publish_command("pause", "")

    def resume(self) -> bool:
        """Resume cleaning"""
        return self._publish_command("resume", "")


def create_protocol_handler(protocol: str, ip_address: str, **kwargs) -> Optional[VacuumProtocolHandler]:
    """
    Factory function to create appropriate protocol handler

    Args:
        protocol: Protocol type ('miio', 'mqtt', 'tuya', 'ecovacs')
        ip_address: Device IP address
        **kwargs: Protocol-specific parameters

    Returns:
        Protocol handler instance or None
    """
    if protocol.lower() == 'miio':
        return MiIOProtocolHandler(
            ip_address,
            token=kwargs.get('token'),
            port=kwargs.get('port', 54321)
        )
    elif protocol.lower() == 'mqtt':
        return MQTTProtocolHandler(
            ip_address,
            blid=kwargs.get('blid', ''),
            password=kwargs.get('password', ''),
            port=kwargs.get('port', 8883)
        )
    else:
        logger.error(f"❌ Unsupported protocol: {protocol}")
        return None
