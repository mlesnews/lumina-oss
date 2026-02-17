#!/usr/bin/env python3
"""
Start Conversation Flow - Auto-Accept & Auto-Send

Ensures both auto-accept and auto-send are running to maintain
natural conversation flow without manual clicking.

Tags: #AUTOMATION #CONVERSATION_FLOW #AUTO_ACCEPT #AUTO_SEND
"""

import sys
import time
import threading
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConversationFlow")


def start_auto_accept():
    """Start auto-accept monitoring"""
    try:
        from cursor_ide_auto_accept import CursorIDEAutoAccept

        auto_accept = CursorIDEAutoAccept()

        def monitor_loop():
            logger.info("🔄 Starting auto-accept monitoring...")
            auto_accept.monitor_and_auto_accept(interval=2.0)

        thread = threading.Thread(target=monitor_loop, daemon=True, name="AutoAccept")
        thread.start()
        logger.info("✅ Auto-accept monitoring started")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start auto-accept: {e}")
        return False


def start_auto_send(pause_threshold: float = 10.0):
    """Start auto-send monitoring"""
    try:
        from cursor_auto_send_monitor import start_auto_send

        monitor = start_auto_send(pause_threshold=pause_threshold)
        logger.info(f"✅ Auto-send monitoring started (pause: {pause_threshold}s)")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start auto-send: {e}")
        return False


def start_xbox_controller():
    """Start Xbox controller mapping"""
    try:
        from xbox_controller_mapping import XboxControllerMapper

        mapper = XboxControllerMapper()

        def controller_loop():
            logger.info("🎮 Starting Xbox controller monitoring...")
            mapper.start_monitoring()

        thread = threading.Thread(target=controller_loop, daemon=True, name="XboxController")
        thread.start()
        logger.info("✅ Xbox controller monitoring started")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Xbox controller not available: {e}")
        logger.info("   Controller will be available when connected")
        return False


def main():
    """Start all conversation flow services"""
    logger.info("=" * 80)
    logger.info("🚀 STARTING CONVERSATION FLOW SERVICES")
    logger.info("=" * 80)
    logger.info("")

    # Start auto-accept
    logger.info("1️⃣  Auto-Accept (Keep All Changes)...")
    accept_started = start_auto_accept()

    # Start auto-send
    logger.info("")
    logger.info("2️⃣  Auto-Send (10s pause)...")
    send_started = start_auto_send(pause_threshold=10.0)

    # Start Xbox controller
    logger.info("")
    logger.info("3️⃣  Xbox Controller Mapping...")
    controller_started = start_xbox_controller()

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ CONVERSATION FLOW SERVICES STARTED")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📋 Status:")
    logger.info(f"   Auto-Accept: {'✅ Running' if accept_started else '❌ Failed'}")
    logger.info(f"   Auto-Send:   {'✅ Running' if send_started else '❌ Failed'}")
    logger.info(f"   Xbox Controller: {'✅ Running' if controller_started else '⚠️  Not connected'}")
    logger.info("")
    logger.info("💡 Services are running in background")
    logger.info("   - Auto-accept: Monitors for 'Keep All' button every 2s")
    logger.info("   - Auto-send: Sends message after 10s pause")
    logger.info("   - Xbox Controller: Maps buttons to LUMINA/Cursor functions")
    logger.info("")
    logger.info("Press Ctrl+C to stop all services")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Stopping services...")
        logger.info("✅ Services stopped")


if __name__ == "__main__":


    main()