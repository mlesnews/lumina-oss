#!/usr/bin/env python3
"""
AOS HID (Human Interface Device) Abstraction Layer

Unified interface for all human interface devices:
- Phones, watches, AR/VR glasses
- Keyboard, mouse, touch, voice
- Brain-computer interfaces (future)

Tags: #AOS #HID #VR #AR #MOBILE #UNIFIED @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import json

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AOSHIDAbstraction")


class DeviceType(Enum):
    """Types of human interface devices"""
    PHONE = 'phone'
    WATCH = 'watch'
    TABLET = 'tablet'
    VR_HEADSET = 'vr_headset'
    AR_GLASSES = 'ar_glasses'
    KEYBOARD = 'keyboard'
    MOUSE = 'mouse'
    TOUCH = 'touch'
    VOICE = 'voice'
    EYE_TRACKING = 'eye_tracking'
    HAPTIC = 'haptic'
    BCI = 'bci'  # Brain-Computer Interface


class InputType(Enum):
    """Types of input"""
    TOUCH = 'touch'
    GESTURE = 'gesture'
    VOICE = 'voice'
    GAZE = 'gaze'
    KEYBOARD = 'keyboard'
    MOUSE = 'mouse'
    BUTTON = 'button'
    NEURAL = 'neural'  # Future: BCI


class OutputType(Enum):
    """Types of output"""
    VISUAL = 'visual'
    AUDIO = 'audio'
    HAPTIC = 'haptic'
    TEXT = 'text'
    SPATIAL = 'spatial'  # 3D/VR space


@dataclass
class Device:
    """Represents a human interface device"""
    device_id: str
    device_type: DeviceType
    platform: str  # 'ios', 'android', 'steamvr', 'windows', etc.
    capabilities: Dict[str, Any]
    is_connected: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class InputEvent:
    """Input event from a device"""
    device_id: str
    input_type: InputType
    data: Dict[str, Any]
    timestamp: float
    metadata: Dict[str, Any] = None


@dataclass
class OutputEvent:
    """Output event to a device"""
    device_id: str
    output_type: OutputType
    content: Any
    metadata: Dict[str, Any] = None


class HIDAbstractionLayer:
    """
    Unified Human Interface Device Abstraction Layer.

    Provides single interface for all human interface devices:
    - Phones, watches, tablets
    - AR/VR headsets (SteamVR, Apple Vision Pro, etc.)
    - Traditional HIDs (keyboard, mouse, touch)
    - Emerging interfaces (BCI, haptic, etc.)
    """

    def __init__(self):
        """Initialize HID abstraction layer"""
        self.devices: Dict[str, Device] = {}
        self.input_handlers: Dict[str, Callable] = {}
        self.output_handlers: Dict[str, Callable] = {}
        self.lumina_inference = None  # Will be set when Lumina is available
        self.lock = threading.Lock()
        logger.info("👤 AOS HID Abstraction Layer initialized")

    def register_device(
        self,
        device_id: str,
        device_type: DeviceType,
        platform: str,
        capabilities: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Device:
        """
        Register a human interface device.

        Args:
            device_id: Unique device identifier
            device_type: Type of device
            platform: Platform (ios, android, steamvr, etc.)
            capabilities: Device capabilities
            metadata: Additional metadata

        Returns:
            Registered Device object
        """
        with self.lock:
            device = Device(
                device_id=device_id,
                device_type=device_type,
                platform=platform,
                capabilities=capabilities,
                is_connected=True,
                metadata=metadata or {}
            )

            self.devices[device_id] = device
            logger.info(f"Registered device: {device_id} ({device_type.value} on {platform})")

            return device

    def unregister_device(self, device_id: str) -> None:
        """Unregister a device"""
        with self.lock:
            if device_id in self.devices:
                self.devices[device_id].is_connected = False
                del self.devices[device_id]
                logger.info(f"Unregistered device: {device_id}")

    def handle_input(
        self,
        device_id: str,
        input_type: InputType,
        data: Dict[str, Any],
        route_to_lumina: bool = True
    ) -> Dict[str, Any]:
        """
        Handle input from any device.

        Args:
            device_id: Device that sent input
            input_type: Type of input
            data: Input data
            route_to_lumina: Whether to route to Lumina inference

        Returns:
            Processed result
        """
        if device_id not in self.devices:
            logger.warning(f"Unknown device: {device_id}")
            return {'error': 'Unknown device'}

        device = self.devices[device_id]

        # Create input event
        import time
        event = InputEvent(
            device_id=device_id,
            input_type=input_type,
            data=data,
            timestamp=time.time()
        )

        # Route to Lumina inference if enabled
        if route_to_lumina and self.lumina_inference:
            result = self.lumina_inference.process_input(
                device_type=device.device_type,
                input_type=input_type,
                data=data
            )

            # Route output back to device(s)
            if 'output' in result:
                self.render_output(device_id, result['output'])

            return result

        # Default: just log
        logger.debug(f"Input from {device_id}: {input_type.value} - {data}")
        return {'status': 'processed'}

    def render_output(
        self,
        device_id: str,
        output_type: OutputType,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Render output to a device.

        Args:
            device_id: Target device
            output_type: Type of output
            content: Content to render
            metadata: Additional metadata
        """
        if device_id not in self.devices:
            logger.warning(f"Unknown device: {device_id}")
            return

        device = self.devices[device_id]

        # Create output event
        event = OutputEvent(
            device_id=device_id,
            output_type=output_type,
            content=content,
            metadata=metadata or {}
        )

        # Route to device-specific handler
        if device_id in self.output_handlers:
            try:
                self.output_handlers[device_id](event)
            except Exception as e:
                logger.error(f"Error rendering to {device_id}: {e}")
        else:
            logger.debug(f"Output to {device_id}: {output_type.value} - {content}")

    def register_input_handler(
        self,
        device_id: str,
        handler: Callable[[InputEvent], None]
    ) -> None:
        """Register input handler for device"""
        self.input_handlers[device_id] = handler
        logger.debug(f"Registered input handler for {device_id}")

    def register_output_handler(
        self,
        device_id: str,
        handler: Callable[[OutputEvent], None]
    ) -> None:
        """Register output handler for device"""
        self.output_handlers[device_id] = handler
        logger.debug(f"Registered output handler for {device_id}")

    def set_lumina_inference(self, lumina_inference):
        """Set Lumina inference layer"""
        self.lumina_inference = lumina_inference
        logger.info("Connected Lumina inference layer")

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)

    def list_devices(self, device_type: Optional[DeviceType] = None) -> List[Device]:
        """List all devices, optionally filtered by type"""
        devices = list(self.devices.values())
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        return devices

    def sync_state(self, source_device_id: str, target_device_id: str) -> None:
        """Synchronize state between devices"""
        if source_device_id not in self.devices or target_device_id not in self.devices:
            logger.warning(f"Cannot sync: devices not found")
            return

        # Get state from source device
        source_device = self.devices[source_device_id]
        state = source_device.metadata.get('state', {})

        # Apply to target device
        target_device = self.devices[target_device_id]
        target_device.metadata['state'] = state

        logger.info(f"Synced state from {source_device_id} to {target_device_id}")


class LuminaHIDInference:
    """
    Lumina inference integration for HID understanding.

    Processes inputs through JARVIS, R5, MARVIN to understand
    user intent across all devices.
    """

    def __init__(self, jarvis=None, r5=None, marvin=None):
        """Initialize Lumina HID inference"""
        self.jarvis = jarvis
        self.r5 = r5
        self.marvin = marvin
        logger.info("🧠 Lumina HID Inference initialized")

    def process_input(
        self,
        device_type: DeviceType,
        input_type: InputType,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process input through Lumina inference.

        Args:
            device_type: Type of device
            input_type: Type of input
            data: Input data

        Returns:
            Processed result with intent, context, response
        """
        # Get context from R5
        context = {}
        if self.r5:
            try:
                context = self.r5.get_context(device_type.value)
            except Exception as e:
                logger.debug(f"R5 context error: {e}")

        # Understand intent with JARVIS
        intent = {}
        if self.jarvis:
            try:
                intent = self.jarvis.understand_intent(
                    device_type=device_type.value,
                    input_type=input_type.value,
                    data=data
                )
            except Exception as e:
                logger.debug(f"JARVIS intent error: {e}")

        # Validate with MARVIN
        secure = True
        if self.marvin:
            try:
                secure = self.marvin.validate_input(data)
            except Exception as e:
                logger.debug(f"MARVIN validation error: {e}")

        # Generate response
        response = self._generate_response(intent, context, device_type)

        return {
            'intent': intent,
            'context': context,
            'secure': secure,
            'response': response,
            'device_type': device_type.value,
            'input_type': input_type.value
        }

    def _generate_response(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        device_type: DeviceType
    ) -> Dict[str, Any]:
        """Generate response based on intent and context"""
        # Simple response generation
        # In production, this would use JARVIS to generate intelligent responses

        return {
            'type': 'acknowledgment',
            'content': f"Processed {device_type.value} input",
            'actions': []
        }


def main():
    """Example usage"""
    hid = HIDAbstractionLayer()

    # Register devices
    hid.register_device(
        'phone_001',
        DeviceType.PHONE,
        'ios',
        {'touch': True, 'voice': True, 'camera': True}
    )

    hid.register_device(
        'vr_001',
        DeviceType.VR_HEADSET,
        'steamvr',
        {'hand_tracking': True, 'eye_tracking': True, 'spatial': True}
    )

    # Set up Lumina inference
    lumina_inference = LuminaHIDInference()
    hid.set_lumina_inference(lumina_inference)

    # Handle input
    result = hid.handle_input(
        'phone_001',
        InputType.VOICE,
        {'text': 'Start JARVIS workflow'}
    )

    print(f"Result: {result}")

    # Render output
    hid.render_output(
        'vr_001',
        OutputType.SPATIAL,
        {'content': 'Workflow started', 'position': [0, 0, -1]}
    )


if __name__ == "__main__":


    main()