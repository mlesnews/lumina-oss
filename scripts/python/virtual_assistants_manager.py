#!/usr/bin/env python3
"""
Virtual Assistants Manager - Unified Manager for Kenny & Ace
Single entry point to manage both virtual assistants

Features:
- Start/stop both assistants
- Unified configuration
- Status monitoring
- Coordinated operations
- Collaboration orchestration

Tags: #KENNY #ACES #VIRTUAL_ASSISTANTS #MANAGER @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
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
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VirtualAssistantsManager")


class VirtualAssistantsManager:
    """
    Unified Manager for Kenny & Ace Virtual Assistants

    Manages:
    - Starting/stopping both assistants
    - Unified configuration
    - Status monitoring
    - Coordinated operations
    - Collaboration orchestration
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize virtual assistants manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_file = self.config_dir / "virtual_assistants_config.json"

        # Load configuration
        self.config = self._load_config()

        # Assistant instances
        self.kenny_instance = None
        self.kenny_thread = None
        self.ace_tracking_thread = None

        # Collaboration system
        try:
            from kenny_aces_collaboration import get_collaboration
            self.collaboration = get_collaboration()
            logger.info("✅ Collaboration system loaded")
        except Exception as e:
            logger.warning(f"⚠️  Collaboration system not available: {e}")
            self.collaboration = None

        # Status
        self.kenny_running = False
        self.ace_detected = False
        self.monitoring = False
        self.monitor_thread = None

        logger.info("=" * 80)
        logger.info("🎮 VIRTUAL ASSISTANTS MANAGER")
        logger.info("   Unified management for Kenny & Ace")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load config: {e}")

        # Default config
        return {
            "version": "1.0.0",
            "kenny": {
                "enabled": True,
                "auto_start": False,
                "match_ace_size": True,
                "tortoise_mode": True,
                "size": None,  # Auto-detect from Ace
                "scale": None
            },
            "ace": {
                "enabled": True,
                "auto_detect": True,
                "track_position": True,
                "update_interval": 0.5  # seconds
            },
            "collaboration": {
                "enabled": True,
                "collision_threshold": 100,  # pixels
                "auto_greeting": True
            },
            "monitoring": {
                "enabled": True,
                "update_interval": 1.0  # seconds
            }
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Config saved: {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")

    def start_kenny(self) -> bool:
        """Start Kenny virtual assistant"""
        if self.kenny_running:
            logger.info("⚠️  Kenny is already running")
            return True

        try:
            from kenny_imva_enhanced import KennyIMVAEnhanced

            # Get Kenny config
            kenny_config = self.config.get("kenny", {})

            # Determine size
            size = None
            scale = None

            if kenny_config.get("match_ace_size", True):
                # Try to match Ace's size
                try:
                    from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
                    ace = ACVAArmouryCrateIntegration()
                    ace_info = ace.get_acva_window_info()
                    if ace_info and ace_info.get('position'):
                        ace_width = ace_info['position'].get('width', 60)
                        ace_height = ace_info['position'].get('height', 60)
                        ace_size = int((ace_width + ace_height) / 2) if ace_width > 0 and ace_height > 0 else 60
                        size = ace_size
                        logger.info(f"✅ Detected Ace size: {ace_size}px - matching Kenny")
                except Exception as e:
                    logger.debug(f"Could not detect Ace size: {e}")
                    size = 60
            elif kenny_config.get("size"):
                size = kenny_config["size"]
            elif kenny_config.get("scale"):
                scale = kenny_config["scale"]

            # Create Kenny instance
            self.kenny_instance = KennyIMVAEnhanced(
                size=size,
                scale=scale,
                load_ecosystem=False  # Lightweight mode
            )

            # Start Kenny in separate thread
            def run_kenny():
                try:
                    self.kenny_instance.start()
                except Exception as e:
                    logger.error(f"❌ Error running Kenny: {e}")
                    self.kenny_running = False

            self.kenny_thread = threading.Thread(target=run_kenny, daemon=True)
            self.kenny_thread.start()

            self.kenny_running = True
            logger.info("✅ Kenny started!")

            # Send greeting to Ace if collaboration enabled
            if self.collaboration and self.config.get("collaboration", {}).get("auto_greeting", True):
                time.sleep(1.0)  # Wait for Kenny to initialize
                self.collaboration.send_message(
                    from_assistant="kenny",
                    to_assistant="ace",
                    message_type=type('MessageType', (), {'value': 'greeting'})(),
                    payload={"message": "Hello Ace! Kenny here! 🐢"}
                )
                logger.info("👋 Sent greeting to Ace from Kenny")

            return True
        except Exception as e:
            logger.error(f"❌ Error starting Kenny: {e}")
            return False

    def stop_kenny(self):
        """Stop Kenny virtual assistant"""
        if not self.kenny_running:
            logger.info("⚠️  Kenny is not running")
            return

        try:
            if self.kenny_instance:
                self.kenny_instance.stop()
            self.kenny_running = False
            logger.info("🛑 Kenny stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping Kenny: {e}")

    def start_ace_tracking(self):
        """Start tracking Ace's position"""
        if not self.config.get("ace", {}).get("track_position", True):
            return

        def track_ace():
            """Track Ace's position and update collaboration system"""
            try:
                from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
                ace = ACVAArmouryCrateIntegration()

                update_interval = self.config.get("ace", {}).get("update_interval", 0.5)

                while self.monitoring:
                    try:
                        ace_info = ace.get_acva_window_info()
                        if ace_info and ace_info.get('position'):
                            pos = ace_info['position']
                            ace_x = pos.get('x', 0)
                            ace_y = pos.get('y', 0)
                            ace_width = pos.get('width', 60)
                            ace_height = pos.get('height', 60)
                            ace_size = int((ace_width + ace_height) / 2) if ace_width > 0 and ace_height > 0 else 60

                            # Update collaboration system
                            if self.collaboration:
                                self.collaboration.update_ace_position(ace_x, ace_y, ace_size)

                            self.ace_detected = True
                        else:
                            self.ace_detected = False
                    except Exception as e:
                        logger.debug(f"Could not track Ace: {e}")
                        self.ace_detected = False

                    time.sleep(update_interval)
            except Exception as e:
                logger.error(f"❌ Error in Ace tracking: {e}")

        self.ace_tracking_thread = threading.Thread(target=track_ace, daemon=True)
        self.ace_tracking_thread.start()
        logger.info("✅ Ace position tracking started")

    def start_monitoring(self):
        """Start status monitoring"""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor():
            """Monitor both assistants"""
            while self.monitoring:
                try:
                    # Check Kenny status
                    if self.kenny_thread and not self.kenny_thread.is_alive():
                        self.kenny_running = False

                    # Log status periodically
                    logger.debug(f"📊 Status: Kenny={'🟢' if self.kenny_running else '🔴'} Ace={'🟢' if self.ace_detected else '🔴'}")

                    time.sleep(self.config.get("monitoring", {}).get("update_interval", 1.0))
                except Exception as e:
                    logger.error(f"❌ Error in monitoring: {e}")
                    time.sleep(1.0)

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

        # Start Ace tracking
        self.start_ace_tracking()

        logger.info("✅ Monitoring started")

    def stop_monitoring(self):
        """Stop status monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info("🛑 Monitoring stopped")

    def start_all(self):
        """Start both assistants and monitoring"""
        logger.info("🚀 Starting all virtual assistants...")

        # Start monitoring first
        self.start_monitoring()

        # Start Kenny
        if self.config.get("kenny", {}).get("enabled", True):
            self.start_kenny()

        logger.info("✅ All systems started!")

    def stop_all(self):
        """Stop all assistants and monitoring"""
        logger.info("🛑 Stopping all virtual assistants...")

        self.stop_kenny()
        self.stop_monitoring()

        logger.info("✅ All systems stopped!")

    def get_status(self) -> Dict[str, Any]:
        """Get status of both assistants"""
        status = {
            "kenny": {
                "running": self.kenny_running,
                "thread_alive": self.kenny_thread.is_alive() if self.kenny_thread else False
            },
            "ace": {
                "detected": self.ace_detected,
                "tracking": self.ace_tracking_thread.is_alive() if self.ace_tracking_thread else False
            },
            "collaboration": {
                "enabled": self.collaboration is not None,
                "relationship_state": (
                    self.collaboration.get_relationship_state().value
                    if self.collaboration else None
                )
            },
            "monitoring": {
                "enabled": self.monitoring
            }
        }

        return status


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Virtual Assistants Manager - Unified Manager for Kenny & Ace")
    parser.add_argument('--start', action='store_true', help='Start all assistants')
    parser.add_argument('--stop', action='store_true', help='Stop all assistants')
    parser.add_argument('--start-kenny', action='store_true', help='Start Kenny only')
    parser.add_argument('--stop-kenny', action='store_true', help='Stop Kenny only')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')

    args = parser.parse_args()

    print("=" * 80)
    print("🎮 VIRTUAL ASSISTANTS MANAGER")
    print("   Unified management for Kenny & Ace")
    print("=" * 80)
    print()

    manager = VirtualAssistantsManager()

    if args.start:
        manager.start_all()
        print("✅ All assistants started!")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_all()
            print("\n✅ Stopped")

    elif args.stop:
        manager.stop_all()
        print("✅ All assistants stopped")

    elif args.start_kenny:
        if manager.start_kenny():
            print("✅ Kenny started!")
        else:
            print("❌ Failed to start Kenny")

    elif args.stop_kenny:
        manager.stop_kenny()
        print("✅ Kenny stopped")

    elif args.monitor:
        manager.start_monitoring()
        print("✅ Monitoring started")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_monitoring()
            print("\n✅ Monitoring stopped")

    elif args.status:
        status = manager.get_status()
        print("📊 Status:")
        print(f"   Kenny: {'🟢 Running' if status['kenny']['running'] else '🔴 Stopped'}")
        print(f"   Ace: {'🟢 Detected' if status['ace']['detected'] else '🔴 Not detected'}")
        print(f"   Collaboration: {'🟢 Enabled' if status['collaboration']['enabled'] else '🔴 Disabled'}")
        if status['collaboration']['relationship_state']:
            print(f"   Relationship: {status['collaboration']['relationship_state']}")
        print(f"   Monitoring: {'🟢 Active' if status['monitoring']['enabled'] else '🔴 Inactive'}")
    else:
        print("💡 Use --start, --stop, --start-kenny, --stop-kenny, --status, or --monitor")
        print("=" * 80)


if __name__ == "__main__":


    main()