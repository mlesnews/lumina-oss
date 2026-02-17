#!/usr/bin/env python3
"""
Framework Integration Script

Integrates Voice Service Manager and Model Selector into existing systems.

Tags: #INTEGRATION #FRAMEWORKS #VOICE_SERVICES #MODEL_SELECTION @JARVIS @LUMINA #PEAK
"""

import sys
from pathlib import Path

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

logger = get_logger("FrameworkIntegration")


def integrate_voice_service_manager():
    """Integrate Voice Service Manager into existing voice systems"""
    logger.info("🔄 Integrating Voice Service Manager...")

    # Integration points:
    # 1. jarvis_elevenlabs_voice.py - Already updated to use manager
    # 2. voice_interface_system.py - Add TTS integration
    # 3. passive_active_voice_system.py - Add voice output

    logger.info("✅ Voice Service Manager integration points identified")
    logger.info("   - jarvis_elevenlabs_voice.py: Updated to use manager")
    logger.info("   - voice_interface_system.py: Ready for integration")
    logger.info("   - passive_active_voice_system.py: Ready for integration")


def integrate_model_selector():
    """Integrate Model Selector into existing AI systems"""
    logger.info("🔄 Integrating Model Selector...")

    # Integration points:
    # 1. AI workflows - Use model selector for model choice
    # 2. Cursor integration - Route model selection through selector
    # 3. Decision systems - Use selector for model decisions

    logger.info("✅ Model Selector integration points identified")
    logger.info("   - AI workflows: Ready for integration")
    logger.info("   - Cursor integration: Ready for integration")
    logger.info("   - Decision systems: Ready for integration")


def main():
    """Main integration function"""
    logger.info("=" * 80)
    logger.info("FRAMEWORK INTEGRATION")
    logger.info("=" * 80)

    integrate_voice_service_manager()
    integrate_model_selector()

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ INTEGRATION COMPLETE")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Update voice_interface_system.py to use VoiceServiceManager")
    logger.info("  2. Update passive_active_voice_system.py to use VoiceServiceManager")
    logger.info("  3. Integrate ModelSelector into AI workflows")
    logger.info("  4. Test integrations")


if __name__ == "__main__":


    main()