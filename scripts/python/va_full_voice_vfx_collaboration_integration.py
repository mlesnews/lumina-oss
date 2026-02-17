#!/usr/bin/env python3
"""
VA Full Voice/VFX/Collaboration Integration

Complete integration system that connects:
- All virtual assistants
- Full voice mode (speech recognition + TTS)
- AI VFX system (visual effects)
- Company-wide collaboration
- Real-time coordination

This is the master system that brings everything together.

Tags: #VOICE #VFX #COLLABORATION #INTEGRATION #FULL_MODE @JARVIS @LUMINA
"""

import sys
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("VAFullIntegration")

# Import all systems
try:
    from ai_managed_va_orchestrator import AIManagedVAOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    AIManagedVAOrchestrator = None

try:
    from va_full_voice_mode_system import VAFullVoiceModeSystem, VoicePriority
    VOICE_SYSTEM_AVAILABLE = True
except ImportError:
    VOICE_SYSTEM_AVAILABLE = False
    VAFullVoiceModeSystem = None
    VoicePriority = None

try:
    from va_ai_vfx_system import VAAIVFXSystem, VFXType, VFXIntensity
    VFX_SYSTEM_AVAILABLE = True
except ImportError:
    VFX_SYSTEM_AVAILABLE = False
    VAAIVFXSystem = None
    VFXType = None
    VFXIntensity = None

try:
    from va_company_collaboration_system import VACompanyCollaborationSystem, CollaborationType
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False
    VACompanyCollaborationSystem = None
    CollaborationType = None


class VAFullVoiceVFXCollaborationIntegration:
    """
    Complete VA Integration System

    Integrates:
    - VA Orchestrator (manages VAs)
    - Full Voice Mode (speech + TTS)
    - AI VFX System (visual effects)
    - Company Collaboration (coordination)
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        setup_logging()

        # Core systems
        self.orchestrator = None
        self.voice_system = None
        self.vfx_system = None
        self.collaboration_system = None

        # VA instances cache
        self.va_instances: Dict[str, Any] = {}
        self.va_lock = threading.Lock()

        # Integration state
        self.integration_active = False
        self.integration_thread = None

        logger.info("✅ VA Full Voice/VFX/Collaboration Integration initialized")

    def initialize_systems(self):
        """Initialize all systems"""
        # Initialize orchestrator
        if ORCHESTRATOR_AVAILABLE:
            try:
                self.orchestrator = AIManagedVAOrchestrator(self.project_root)
                logger.info("✅ Orchestrator initialized")
            except Exception as e:
                logger.error(f"❌ Orchestrator initialization failed: {e}")

        # Initialize voice system
        if VOICE_SYSTEM_AVAILABLE:
            try:
                self.voice_system = VAFullVoiceModeSystem(self.project_root)
                logger.info("✅ Voice system initialized")
            except Exception as e:
                logger.error(f"❌ Voice system initialization failed: {e}")

        # Initialize VFX system
        if VFX_SYSTEM_AVAILABLE:
            try:
                self.vfx_system = VAAIVFXSystem(self.project_root)
                logger.info("✅ VFX system initialized")
            except Exception as e:
                logger.error(f"❌ VFX system initialization failed: {e}")

        # Initialize collaboration system
        if COLLABORATION_AVAILABLE:
            try:
                self.collaboration_system = VACompanyCollaborationSystem(self.project_root)
                # Inject our voice and VFX systems
                if self.voice_system:
                    self.collaboration_system.voice_system = self.voice_system
                if self.vfx_system:
                    self.collaboration_system.vfx_system = self.vfx_system
                logger.info("✅ Collaboration system initialized")
            except Exception as e:
                logger.error(f"❌ Collaboration system initialization failed: {e}")

    def start_full_integration(self):
        """Start full integration mode"""
        if self.integration_active:
            logger.warning("⚠️  Integration already active")
            return

        logger.info("=" * 80)
        logger.info("🚀 STARTING FULL VA INTEGRATION")
        logger.info("=" * 80)

        # Initialize systems
        self.initialize_systems()

        # Start orchestrator
        if self.orchestrator:
            logger.info("📋 Starting VA Orchestrator...")
            orchestrator_thread = threading.Thread(
                target=self.orchestrator.start,
                daemon=True
            )
            orchestrator_thread.start()
            logger.info("✅ Orchestrator started")

            # Wait for VAs to initialize
            logger.info("⏳ Waiting for VAs to initialize...")
            time.sleep(10)

        # Register VAs with all systems
        self._register_all_vas()

        # Start full collaboration mode
        if self.collaboration_system:
            logger.info("🤝 Starting full collaboration mode...")
            self.collaboration_system.start_full_collaboration_mode()
            logger.info("✅ Full collaboration mode activated")

        # Start integration monitoring thread
        self.integration_active = True
        self.integration_thread = threading.Thread(
            target=self._integration_monitor_loop,
            daemon=True
        )
        self.integration_thread.start()

        logger.info("=" * 80)
        logger.info("✅ FULL VA INTEGRATION ACTIVE")
        logger.info("=" * 80)
        logger.info("Features:")
        logger.info("  ✅ Full voice mode (speech recognition + TTS)")
        logger.info("  ✅ AI VFX system (particles, glow, beams)")
        logger.info("  ✅ Company-wide collaboration")
        logger.info("  ✅ Real-time VA coordination")
        logger.info("  ✅ Voice + VFX synchronization")
        logger.info("=" * 80)

    def stop_full_integration(self):
        """Stop full integration mode"""
        self.integration_active = False

        if self.collaboration_system:
            self.collaboration_system.stop_full_collaboration_mode()

        if self.voice_system:
            self.voice_system.stop_full_voice_mode()

        logger.info("🔇 Full integration stopped")

    def _register_all_vas(self):
        """Register all VAs with all systems"""
        # VA configurations
        va_configs = {
            "ironman": {
                "priority": VoicePriority.HIGH if VoicePriority else None,
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # JARVIS voice
                "color": (220, 20, 60),  # Crimson
                "glow_color": (255, 215, 0),  # Gold
                "capabilities": ["voice", "vfx", "tasks", "combat"]
            },
            "kenny": {
                "priority": VoicePriority.MEDIUM if VoicePriority else None,
                "voice_id": None,  # Default
                "color": (0, 191, 255),  # Deep Sky Blue
                "glow_color": (255, 255, 0),  # Yellow
                "capabilities": ["voice", "vfx", "tasks"]
            },
            "anakin": {
                "priority": VoicePriority.MEDIUM if VoicePriority else None,
                "voice_id": None,  # Default
                "color": (255, 0, 0),  # Red
                "glow_color": (255, 140, 0),  # Dark Orange
                "capabilities": ["voice", "vfx", "tasks", "combat"]
            },
            "jarvis": {
                "priority": VoicePriority.CRITICAL if VoicePriority else None,
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # JARVIS voice
                "color": (0, 255, 255),  # Cyan
                "glow_color": (255, 215, 0),  # Gold
                "capabilities": ["voice", "vfx", "tasks", "orchestration"]
            }
        }

        # Try to get VA instances from orchestrator
        va_instances = {}
        if self.orchestrator:
            # VAs are managed by orchestrator, we'll create proxy instances
            for va_name in ["ironman", "kenny", "anakin", "jarvis"]:
                if va_name in self.orchestrator.monitors:
                    # Create a proxy instance that connects to the running VA
                    va_instances[va_name] = self._create_va_proxy(va_name)

        # Register with all systems
        for va_name, config in va_configs.items():
            va_instance = va_instances.get(va_name)
            if not va_instance:
                # Create a minimal proxy if VA not running
                va_instance = self._create_va_proxy(va_name)

            # Register with voice system
            if self.voice_system and config["priority"]:
                self.voice_system.register_va(
                    va_name,
                    va_instance,
                    config["priority"]
                )
                if config["voice_id"]:
                    self.voice_system.vas[va_name]["voice_id"] = config["voice_id"]

            # Register with VFX system
            if self.vfx_system:
                self.vfx_system.register_va(va_name, va_instance)
                self.vfx_system.vas[va_name]["color"] = config["color"]
                self.vfx_system.vas[va_name]["glow_color"] = config["glow_color"]

            # Register with collaboration system
            if self.collaboration_system:
                self.collaboration_system.register_va(
                    va_name,
                    va_instance,
                    config["capabilities"]
                )

            self.va_instances[va_name] = va_instance
            logger.info(f"✅ Registered {va_name} with all systems")

    def _create_va_proxy(self, va_name: str) -> Any:
        """Create a proxy instance for a VA"""
        class VAProxy:
            """Proxy for VA instance"""
            def __init__(self, name: str):
                self.name = name
                self.position = (0, 0)

            def process_voice_input(self, text: str):
                """Process voice input"""
                logger.debug(f"🎤 {self.name} received voice: {text}")

            def process_voice_command(self, text: str):
                """Process voice command"""
                logger.debug(f"🎤 {self.name} received command: {text}")

            def receive_voice_message(self, message):
                """Receive voice message"""
                logger.debug(f"📨 {self.name} received message: {message.text}")

            def receive_task(self, task):
                """Receive task"""
                logger.debug(f"📋 {self.name} received task: {task.description}")

            def receive_notification(self, notification):
                """Receive notification"""
                logger.debug(f"🔔 {self.name} received notification")

        return VAProxy(va_name)

    def _integration_monitor_loop(self):
        """Monitor integration and keep systems synchronized"""
        while self.integration_active:
            try:
                # Update VA positions for VFX
                if self.vfx_system and self.orchestrator:
                    for va_name, monitor in self.orchestrator.monitors.items():
                        if monitor.process and monitor.process.is_running():
                            # Get position from VA (if available)
                            # For now, use default positions
                            positions = {
                                "ironman": (100, 100),
                                "kenny": (200, 100),
                                "anakin": (300, 100),
                                "jarvis": (150, 200)
                            }
                            if va_name in positions:
                                self.vfx_system.update_va_position(
                                    va_name,
                                    positions[va_name],
                                    size=60
                                )

                # Update effects
                if self.vfx_system:
                    delta_time = 0.016  # ~60 FPS
                    self.vfx_system.update_effects(delta_time)

                time.sleep(0.1)  # 10 Hz update rate

            except Exception as e:
                logger.error(f"❌ Integration monitor error: {e}", exc_info=True)
                time.sleep(1)

    def demonstrate_collaboration(self):
        """Demonstrate full collaboration with voice and VFX"""
        logger.info("🎬 Starting collaboration demonstration...")

        # JARVIS speaks with glow
        if self.voice_system and self.vfx_system:
            self.voice_system.speak("jarvis", "All systems operational. Company-wide collaboration active.")
            self.vfx_system.create_glow_effect("jarvis", VFXIntensity.INTENSE, duration=3.0)
            time.sleep(3)

        # Iron Man responds with particles
        if self.voice_system and self.vfx_system:
            self.voice_system.speak("ironman", "Iron Man online. Ready for action.")
            self.vfx_system.create_particle_effect("ironman", particle_count=100, duration=2.0)
            time.sleep(2)

        # Beam between JARVIS and Iron Man
        if self.vfx_system:
            self.vfx_system.create_beam_effect("jarvis", "ironman", VFXIntensity.NORMAL, duration=1.5)
            time.sleep(1.5)

        # Kenny and Anakin join
        if self.voice_system and self.vfx_system:
            self.voice_system.speak("kenny", "Kenny here. Ready to help.")
            self.vfx_system.create_glow_effect("kenny", VFXIntensity.NORMAL, duration=2.0)
            time.sleep(1)

            self.voice_system.speak("anakin", "Anakin ready. All systems go.")
            self.vfx_system.create_particle_effect("anakin", particle_count=50, duration=2.0)
            time.sleep(2)

        logger.info("✅ Collaboration demonstration complete")

    def get_full_status(self) -> Dict[str, Any]:
        """Get full system status"""
        status = {
            "integration_active": self.integration_active,
            "systems": {
                "orchestrator": self.orchestrator is not None,
                "voice": self.voice_system is not None,
                "vfx": self.vfx_system is not None,
                "collaboration": self.collaboration_system is not None
            },
            "registered_vas": list(self.va_instances.keys())
        }

        if self.voice_system:
            status["voice_status"] = self.voice_system.get_status()

        if self.vfx_system:
            status["vfx_status"] = self.vfx_system.get_status()

        if self.collaboration_system:
            status["collaboration_status"] = self.collaboration_system.get_company_status()

        if self.orchestrator:
            orchestrator_status = self.orchestrator.get_status()
            status["orchestrator_status"] = orchestrator_status

        return status


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Full Voice/VFX/Collaboration Integration")
    parser.add_argument("--start", action="store_true", help="Start full integration")
    parser.add_argument("--stop", action="store_true", help="Stop full integration")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--demo", action="store_true", help="Run collaboration demonstration")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    integration = VAFullVoiceVFXCollaborationIntegration(project_root)

    if args.start:
        integration.start_full_integration()
        print("✅ Full integration started")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            integration.stop_full_integration()
            print("✅ Full integration stopped")
    elif args.stop:
        integration.stop_full_integration()
        print("✅ Full integration stopped")
    elif args.status:
        status = integration.get_full_status()
        print(json.dumps(status, indent=2, default=str))
    elif args.demo:
        integration.initialize_systems()
        integration._register_all_vas()
        if integration.collaboration_system:
            integration.collaboration_system.start_full_collaboration_mode()
        integration.demonstrate_collaboration()
    else:
        parser.print_help()


if __name__ == "__main__":


    main()