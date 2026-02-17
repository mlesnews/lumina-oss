#!/usr/bin/env python3
"""
Headless VA Service - Runs Virtual Assistants as background service

Runs VAs without GUI, as part of watchdog-guarded processes.
Monitors VA health and maintains service state.

Tags: #HEADLESS #SERVICE #WATCHDOG #BACKGROUND @JARVIS @LUMINA
"""

import sys
import time
import json
import signal
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from va_visibility_system import VAVisibilitySystem
    from va_desktop_visualization import VADesktopVisualization
    from va_coordination_system import VACoordinationSystem
    from va_health_monitoring import VAHealthMonitoring
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"⚠️  Some imports failed: {e}")

logger = get_logger("VAHeadlessService")


class HeadlessVAService:
    """Headless Virtual Assistant Service"""

    def __init__(self):
        """Initialize headless VA service"""
        self.running = False
        self.shutdown_requested = False

        # Service state
        self.state_file = project_root / "data" / "va_service" / "service_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize VA systems
        try:
            self.registry = CharacterAvatarRegistry()
            self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)
            self.viz = VADesktopVisualization(self.registry)
            self.coord = VACoordinationSystem(self.registry)
            self.health = VAHealthMonitoring(self.registry)

            logger.info("=" * 80)
            logger.info("🤖 HEADLESS VA SERVICE INITIALIZED")
            logger.info("=" * 80)
            logger.info(f"   VAs Registered: {len(self.vas)}")
            logger.info("   Service ready")
            logger.info("=" * 80)
        except Exception as e:
            logger.error(f"❌ Failed to initialize VA systems: {e}")
            raise

        # Service metrics
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "uptime_seconds": 0,
            "va_status": {},
            "restart_count": 0,
            "last_health_check": None
        }

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True

    def initialize_vas(self):
        """Initialize all Virtual Assistants"""
        logger.info("Initializing Virtual Assistants...")

        for va in self.vas:
            try:
                # Ensure widget exists
                widgets = self.viz.get_va_widgets(va.character_id)
                if not widgets:
                    widget = self.viz.create_va_widget(va.character_id)
                    logger.info(f"  ✅ Created widget for {va.name}")
                else:
                    widget = widgets[0]
                    logger.info(f"  ✅ Widget exists for {va.name}")

                # Ensure visible
                widget.visible = True

                # Update status
                self.viz.show_va_status(va.character_id, {
                    "status": "active",
                    "service_mode": "headless",
                    "last_update": datetime.now().isoformat()
                })

                # Initialize health monitoring
                self.health.update_health(va.character_id, {
                    "status": "healthy",
                    "service_running": True
                })

                logger.info(f"  ✅ {va.name} initialized and active")

            except Exception as e:
                logger.error(f"  ❌ Failed to initialize {va.name}: {e}")

        logger.info(f"✅ Initialized {len(self.vas)} Virtual Assistant(s)")

    def health_check(self):
        """Perform health check on all VAs"""
        logger.debug("Performing health check...")

        for va in self.vas:
            try:
                # Check widget status
                widgets = self.viz.get_va_widgets(va.character_id)
                if not widgets:
                    logger.warning(f"⚠️  {va.name} has no widgets")
                    continue

                widget = widgets[0]

                # Update health metrics
                health_data = {
                    "status": "healthy" if widget.visible else "inactive",
                    "widget_exists": True,
                    "last_check": datetime.now().isoformat()
                }

                self.health.update_health(va.character_id, health_data)

                # Update service metrics
                self.metrics["va_status"][va.character_id] = {
                    "name": va.name,
                    "status": "healthy" if widget.visible else "inactive",
                    "widget_id": widget.widget_id,
                    "last_update": datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"❌ Health check failed for {va.name}: {e}")

        self.metrics["last_health_check"] = datetime.now().isoformat()

    def save_state(self):
        """Save service state to disk"""
        try:
            state = {
                "running": self.running,
                "metrics": self.metrics,
                "timestamp": datetime.now().isoformat()
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.debug(f"💾 State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")

    def run(self):
        """Run the headless service"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING HEADLESS VA SERVICE")
        logger.info("=" * 80)
        logger.info()

        self.running = True

        # Initialize VAs
        self.initialize_vas()

        # Main service loop
        logger.info("Service running (headless mode)...")
        logger.info("Press Ctrl+C to stop")
        logger.info()

        last_health_check = time.time()
        last_state_save = time.time()
        start_time = time.time()

        try:
            while self.running and not self.shutdown_requested:
                current_time = time.time()

                # Health check every 30 seconds
                if current_time - last_health_check >= 30:
                    self.health_check()
                    last_health_check = current_time

                # Save state every 60 seconds
                if current_time - last_state_save >= 60:
                    self.metrics["uptime_seconds"] = int(current_time - start_time)
                    self.save_state()
                    last_state_save = current_time

                # Sleep briefly
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("📡 Keyboard interrupt received")
            self.shutdown_requested = True

        # Shutdown
        logger.info()
        logger.info("=" * 80)
        logger.info("🛑 SHUTTING DOWN HEADLESS VA SERVICE")
        logger.info("=" * 80)

        self.running = False
        self.save_state()

        logger.info("✅ Service stopped gracefully")
        logger.info("=" * 80)


def main():
    """Main entry point"""
    try:
        service = HeadlessVAService()
        service.run()
        return 0
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    sys.exit(main())