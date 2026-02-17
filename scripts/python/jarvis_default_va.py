#!/usr/bin/env python3
"""
JARVIS Default Virtual Assistant
Iron Man equivalent - walking around screen like Ace (ACVA)

Default layout and configuration for JARVIS VA.
Restores Kenny/Jarvis functionality with Iron Man theme.

Tags: #JARVIS #VA #IRON_MAN #DEFAULT #KENNY @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDefaultVA")

# Try to import Iron Man VA (from archived)
try:
    sys.path.insert(0, str(script_dir / "_archived_consolidated"))
    from ironman_virtual_assistant import IronManVirtualAssistant
    IRON_MAN_VA_AVAILABLE = True
except ImportError:
    IRON_MAN_VA_AVAILABLE = False
    IronManVirtualAssistant = None
    logger.warning("Iron Man VA not found in archived - will use Kenny enhanced")

# Try to import Kenny enhanced
try:
    from kenny_imva_enhanced import KennyIMVAEnhanced
    KENNY_AVAILABLE = True
except ImportError:
    KENNY_AVAILABLE = False
    KennyIMVAEnhanced = None
    logger.warning("Kenny enhanced not available")

# Try to import JARVIS IMVA Kenny Mode
try:
    from jarvis_imva_kenny_mode import IMVAKennyMode
    KENNY_MODE_AVAILABLE = True
except ImportError:
    KENNY_MODE_AVAILABLE = False
    IMVAKennyMode = None


class JARVISDefaultVA:
    """
    JARVIS Default Virtual Assistant

    Iron Man equivalent - walking around screen like Ace (ACVA).
    Default layout and configuration.
    """

    def __init__(self, mode: str = "iron_man"):
        """
        Initialize JARVIS Default VA.

        Args:
            mode: "iron_man" (default) or "kenny" or "auto"
        """
        logger.info("=" * 80)
        logger.info("🦾 JARVIS DEFAULT VIRTUAL ASSISTANT")
        logger.info("=" * 80)

        self.mode = mode
        self.va_instance = None
        self.va_thread = None
        self.running = False

        # Default configuration
        self.config = {
            'theme': 'iron_man',
            'walking_enabled': True,
            'screen_overlay': True,
            'always_on_top': True,
            'transparent': True,
            'position': 'bottom_right',  # Like Ace
            'size': 'medium',
            'animations': True,
            'voice_enabled': True,
            'wake_word': 'Hey Jarvis',
            'integrations': {
                'lumina': True,
                'jarvis_system': True,
                'r5': True,
                'syphon': True
            }
        }

        logger.info(f"Mode: {mode}")
        logger.info(f"Config: {self.config}")

    def start(self):
        """Start JARVIS VA"""
        logger.info("🚀 Starting JARVIS Default VA...")

        if self.mode == "iron_man" and IRON_MAN_VA_AVAILABLE:
            logger.info("Starting Iron Man VA...")
            self.va_instance = IronManVirtualAssistant()
            self.va_thread = threading.Thread(target=self._run_iron_man, daemon=True)
            self.va_thread.start()

        elif self.mode == "kenny" and KENNY_AVAILABLE:
            logger.info("Starting Kenny Enhanced VA...")
            self.va_instance = KennyIMVAEnhanced()
            self.va_thread = threading.Thread(target=self._run_kenny, daemon=True)
            self.va_thread.start()

        elif self.mode == "auto":
            # Auto-detect: prefer Iron Man, fallback to Kenny
            if IRON_MAN_VA_AVAILABLE:
                logger.info("Auto-selected: Iron Man VA")
                self.mode = "iron_man"
                self.va_instance = IronManVirtualAssistant()
                self.va_thread = threading.Thread(target=self._run_iron_man, daemon=True)
                self.va_thread.start()
            elif KENNY_AVAILABLE:
                logger.info("Auto-selected: Kenny Enhanced VA")
                self.mode = "kenny"
                self.va_instance = KennyIMVAEnhanced()
                self.va_thread = threading.Thread(target=self._run_kenny, daemon=True)
                self.va_thread.start()
            else:
                logger.error("❌ No VA available!")
                return False
        else:
            logger.error(f"❌ Mode '{self.mode}' not available")
            return False

        self.running = True
        logger.info("✅ JARVIS Default VA started")
        return True

    def _run_iron_man(self):
        """Run Iron Man VA"""
        try:
            if self.va_instance:
                self.va_instance.run()
        except Exception as e:
            logger.error(f"Error running Iron Man VA: {e}", exc_info=True)

    def _run_kenny(self):
        """Run Kenny Enhanced VA"""
        try:
            if self.va_instance:
                self.va_instance.run()
        except Exception as e:
            logger.error(f"Error running Kenny VA: {e}", exc_info=True)

    def stop(self):
        """Stop JARVIS VA"""
        logger.info("🛑 Stopping JARVIS Default VA...")
        self.running = False

        if self.va_instance:
            try:
                if hasattr(self.va_instance, 'stop'):
                    self.va_instance.stop()
                elif hasattr(self.va_instance, 'close'):
                    self.va_instance.close()
            except Exception as e:
                logger.error(f"Error stopping VA: {e}")

        logger.info("✅ JARVIS Default VA stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get VA status"""
        return {
            'running': self.running,
            'mode': self.mode,
            'config': self.config,
            'available': {
                'iron_man': IRON_MAN_VA_AVAILABLE,
                'kenny': KENNY_AVAILABLE,
                'kenny_mode': KENNY_MODE_AVAILABLE
            }
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='JARVIS Default Virtual Assistant')
    parser.add_argument('--mode', choices=['iron_man', 'kenny', 'auto'], default='auto',
                       help='VA mode (default: auto)')
    parser.add_argument('--config', help='Config file path')

    args = parser.parse_args()

    va = JARVISDefaultVA(mode=args.mode)

    try:
        if va.start():
            logger.info("✅ JARVIS Default VA running")
            logger.info("Press Ctrl+C to stop")

            # Keep running
            while va.running:
                time.sleep(1)
        else:
            logger.error("❌ Failed to start JARVIS Default VA")
            return 1
    except KeyboardInterrupt:
        logger.info("Stopping...")
        va.stop()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":


    sys.exit(main())