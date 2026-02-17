#!/usr/bin/env python3
"""
Auto Voice Input with Camera Monitor

REQUIRED: Automatically activates voice input and monitors camera
to detect when user has to manually reach for keyboard (automation failure).

Tags: #VOICE_INPUT #CAMERA #AUTOMATION_MONITORING #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from manus_voice_input_button import MANUSVoiceInputButton
    from camera_keyboard_reach_detector import CameraKeyboardReachDetector
    VOICE_INPUT_AVAILABLE = True
    CAMERA_AVAILABLE = True
except ImportError as e:
    VOICE_INPUT_AVAILABLE = False
    CAMERA_AVAILABLE = False
    logger = get_logger("AutoVoiceCamera")
    logger.warning(f"⚠️  Missing dependencies: {e}")

logger = get_logger("AutoVoiceCamera")


class AutoVoiceInputWithCameraMonitor:
    """
    REQUIRED: Automatically activates voice input and monitors for manual interventions

    Uses camera to detect when user reaches for keyboard, indicating
    automation failure (user had to manually click).
    """

    def __init__(self):
        """Initialize auto voice input with camera monitoring"""
        self.running = False
        self.voice_automator = None
        self.camera_detector = None
        self.monitor_thread = None

        # Voice input state
        self.voice_active = False
        self.activation_attempts = 0
        self.last_activation_time = 0
        self.activation_interval = 5.0  # Try to activate every 5 seconds if not active

        # Statistics
        self.stats = {
            "voice_activations": 0,
            "keyboard_reaches": 0,
            "automation_failures": 0,
            "correlations": []
        }

        # Initialize components
        if VOICE_INPUT_AVAILABLE:
            try:
                self.voice_automator = MANUSVoiceInputButton()
                logger.info("✅ Voice input automator initialized")
            except Exception as e:
                logger.error(f"❌ Voice automator init failed: {e}")

        if CAMERA_AVAILABLE:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.camera_detector = CameraKeyboardReachDetector(project_root)
                logger.info("✅ Camera detector initialized")
            except Exception as e:
                logger.error(f"❌ Camera detector init failed: {e}")

        logger.info("✅ Auto Voice Input with Camera Monitor initialized")

    def _activate_voice_input(self) -> bool:
        """Activate voice input (REQUIRED - not optional)"""
        if not self.voice_automator:
            logger.error("❌ Voice automator not available")
            return False

        try:
            logger.info("🎤 Activating voice input (REQUIRED)...")
            success = self.voice_automator.activate_voice_input()

            if success:
                self.voice_active = True
                self.activation_attempts = 0
                self.stats["voice_activations"] += 1
                logger.info("✅ Voice input activated")
                return True
            else:
                self.activation_attempts += 1
                logger.warning(f"⚠️  Voice activation failed (attempt {self.activation_attempts})")
                return False

        except Exception as e:
            logger.error(f"❌ Voice activation error: {e}")
            return False

    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("👀 Starting monitoring loop...")
        logger.info("   - Auto-activating voice input (REQUIRED)")
        logger.info("   - Monitoring camera for keyboard reaches")
        logger.info("   - Correlating reaches with automation failures")

        # Start camera monitoring
        if self.camera_detector:
            self.camera_detector.start()

        # Initial voice activation
        self._activate_voice_input()

        last_check = time.time()
        check_interval = 2.0  # Check every 2 seconds

        while self.running:
            try:
                current_time = time.time()

                # Check if enough time has passed
                if current_time - last_check >= check_interval:
                    # Check if voice input needs reactivation
                    if not self.voice_active or (current_time - self.last_activation_time) > self.activation_interval:
                        logger.info("🔄 Reactivating voice input...")
                        if self._activate_voice_input():
                            self.last_activation_time = current_time

                    # Check camera for keyboard reaches
                    if self.camera_detector:
                        camera_stats = self.camera_detector.get_stats()
                        current_reaches = camera_stats.get("current_reach_count", 0)

                        # If reach count increased, user had to manually intervene
                        if current_reaches > self.stats["keyboard_reaches"]:
                            new_reaches = current_reaches - self.stats["keyboard_reaches"]
                            self.stats["keyboard_reaches"] = current_reaches

                            # This indicates automation failure
                            self.stats["automation_failures"] += new_reaches

                            logger.warning(f"⚠️  KEYBOARD REACH DETECTED! ({new_reaches} new reach(es))")
                            logger.warning(f"   This indicates automation failure - user had to manually click")
                            logger.warning(f"   Total automation failures: {self.stats['automation_failures']}")

                            # Correlate with voice activation status
                            correlation = {
                                "timestamp": time.time(),
                                "reaches": new_reaches,
                                "voice_active": self.voice_active,
                                "automation_failure": True
                            }
                            self.stats["correlations"].append(correlation)

                            # Keep only last 50 correlations
                            if len(self.stats["correlations"]) > 50:
                                self.stats["correlations"].pop(0)

                            # Try to reactivate voice input immediately
                            logger.info("🔄 Attempting immediate voice reactivation...")
                            self._activate_voice_input()

                    last_check = current_time

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(1)

        # Stop camera monitoring
        if self.camera_detector:
            self.camera_detector.stop()

    def start(self):
        """Start auto voice input with camera monitoring (REQUIRED)"""
        if self.running:
            logger.warning("⚠️  Already running")
            return True

        if not VOICE_INPUT_AVAILABLE:
            logger.error("❌ Voice input automation not available - REQUIRED")
            return False

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✅ Auto voice input with camera monitoring started (REQUIRED)")
        return True

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("👋 Monitoring stopped")

    def get_stats(self):
        """Get monitoring statistics"""
        camera_stats = {}
        if self.camera_detector:
            camera_stats = self.camera_detector.get_stats()

        return {
            **self.stats,
            "voice_active": self.voice_active,
            "activation_attempts": self.activation_attempts,
            "camera_stats": camera_stats
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto Voice Input with Camera Monitor (REQUIRED)")
    parser.add_argument("--start", action="store_true", help="Start monitoring (REQUIRED)")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    try:
        monitor = AutoVoiceInputWithCameraMonitor()

        if args.stats:
            stats = monitor.get_stats()
            print("="*80)
            print("📊 AUTO VOICE INPUT MONITORING STATISTICS")
            print("="*80)
            print(f"Voice Activations: {stats['voice_activations']}")
            print(f"Keyboard Reaches: {stats['keyboard_reaches']}")
            print(f"Automation Failures: {stats['automation_failures']}")
            print(f"Voice Active: {stats['voice_active']}")
            print(f"Activation Attempts: {stats['activation_attempts']}")
            if stats.get('camera_stats'):
                print(f"Camera Reaches: {stats['camera_stats'].get('total_reaches', 0)}")
            return 0

        if args.start or not args.stats:
            print("="*80)
            print("🎤 AUTO VOICE INPUT WITH CAMERA MONITOR (REQUIRED)")
            print("="*80)
            print()
            print("This will:")
            print("  - Automatically activate voice input (REQUIRED)")
            print("  - Monitor camera for keyboard reaches")
            print("  - Detect automation failures")
            print()
            print("Press Ctrl+C to stop")
            print("-"*80)
            print()

            monitor.start()

            try:
                while True:
                    time.sleep(5)
                    # Print stats every 30 seconds
                    stats = monitor.get_stats()
                    print(f"Voice: {'✅' if stats['voice_active'] else '❌'} | "
                          f"Reaches: {stats['keyboard_reaches']} | "
                          f"Failures: {stats['automation_failures']}")
            except KeyboardInterrupt:
                pass

            monitor.stop()
            return 0

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)