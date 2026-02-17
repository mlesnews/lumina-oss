#!/usr/bin/env python3
"""
Enable DEBUG Mode - Maximum Logging

Turns on maximum logging detail and DEBUG mode for testing.
All systems will log at DEBUG/TRACE level.

Tags: #DEBUG #TESTING #LOGGING #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger
import logging

logger = get_adaptive_logger("EnableDebugMode")

# Set to maximum detail immediately
logger.update_system_state("critical", issue_count=999)  # Force maximum detail

# Set underlying logger to DEBUG
if hasattr(logger, 'logger'):
    logger.logger.setLevel(logging.DEBUG)
    for handler in logger.logger.handlers:
        handler.setLevel(logging.DEBUG)

# Also set root logger to DEBUG
logging.root.setLevel(logging.DEBUG)

# Set all known loggers to DEBUG
KNOWN_LOGGERS = [
    "LuminaServiceManager",
    "PostRebootEvaluation",
    "StartupHealthCheck",
    "LuminaHolisticEvaluation",
    "ErrorRecovery",
    "DecisioningEngine",
    "VoiceFilterSystem",
    "ServiceManager",
    "FirstBootInit",
    "StartupLauncher",
    "AutomationProgress",
    "UnifiedWorkflow",
    "EnableDebugMode"
]

for logger_name in KNOWN_LOGGERS:
    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG)
    for handler in log.handlers:
        handler.setLevel(logging.DEBUG)

logger.info("="*80)
logger.info("🔍 DEBUG MODE ENABLED - MAXIMUM LOGGING")
logger.info("="*80)
logger.info("")
logger.info("   ✅ All loggers set to DEBUG level")
logger.info("   ✅ Maximum detail enabled")
logger.info("   ✅ Testing mode active")
logger.info("")
logger.debug("   🔍 DEBUG: This is a debug message")
logger.debug("   🔍 DEBUG: All systems logging at maximum detail")
logger.info("")


def enable_debug_mode():
    """Enable debug mode system-wide"""
    # Create debug config file
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)

    debug_config = {
        "debug_mode": True,
        "log_level": "DEBUG",
        "maximum_detail": True,
        "testing_mode": True,
        "adaptive_logging": False,  # Disable adaptive - always show everything
        "noise_reduction": False,  # Disable noise reduction - show all messages
        "description": "DEBUG MODE - Maximum logging for testing",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

    config_file = config_dir / "debug_mode.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(debug_config, f, indent=2)
        logger.info(f"   ✅ Debug config saved: {config_file}")
    except Exception as e:
        logger.error(f"   ❌ Failed to save debug config: {e}")

    return debug_config


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Enable DEBUG Mode")
        parser.add_argument("--enable", action="store_true", help="Enable debug mode")
        parser.add_argument("--disable", action="store_true", help="Disable debug mode")

        args = parser.parse_args()

        if args.enable:
            config = enable_debug_mode()
            logger.info("")
            logger.info("="*80)
            logger.info("✅ DEBUG MODE ENABLED")
            logger.info("="*80)
            logger.info("")
            logger.info("   🔍 Maximum logging detail: ACTIVE")
            logger.info("   🔍 DEBUG level: ACTIVE")
            logger.info("   🔍 Testing mode: ACTIVE")
            logger.info("   🔍 All systems logging at maximum detail")
            logger.info("")
            return 0
        elif args.disable:
            config_file = project_root / "config" / "debug_mode.json"
            if config_file.exists():
                config_file.unlink()
                logger.info("   ✅ Debug mode disabled")
            return 0
        else:
            parser.print_help()
            return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())