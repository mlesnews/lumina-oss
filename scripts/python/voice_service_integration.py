#!/usr/bin/env python3
"""
Voice Service Integration Wrapper

Provides easy integration of Voice Service Manager into existing systems.
This wrapper makes it simple to replace direct ElevenLabs calls with the manager.

Tags: #INTEGRATION #VOICE_SERVICES #WRAPPER @JARVIS @LUMINA #PEAK
"""

import sys
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_voice_service_manager import VoiceServiceManager, VoiceServiceResult
    VOICE_MANAGER_AVAILABLE = True
except ImportError:
    VOICE_MANAGER_AVAILABLE = False
    VoiceServiceManager = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VoiceServiceIntegration")


# Global manager instance (singleton)
_voice_manager: Optional[VoiceServiceManager] = None


def get_voice_manager() -> Optional[VoiceServiceManager]:
    """Get or create Voice Service Manager instance (singleton)"""
    global _voice_manager

    if not VOICE_MANAGER_AVAILABLE:
        logger.warning("⚠️  Voice Service Manager not available")
        return None

    if _voice_manager is None:
        try:
            _voice_manager = VoiceServiceManager()
            logger.info("✅ Voice Service Manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Voice Service Manager: {e}")
            return None

    return _voice_manager


def speak(text: str, preferred_provider: Optional[str] = None) -> bool:
    """
    Speak text using Voice Service Manager (with automatic fallbacks).

    This is a drop-in replacement for direct ElevenLabs calls.

    Args:
        text: Text to speak
        preferred_provider: Preferred provider name (optional)

    Returns:
        True if successful, False otherwise
    """
    manager = get_voice_manager()
    if not manager:
        logger.warning("⚠️  Voice Service Manager not available - cannot speak")
        return False

    result = manager.speak(text, preferred_provider=preferred_provider)
    return result.success


def speak_with_result(text: str, preferred_provider: Optional[str] = None) -> Optional[VoiceServiceResult]:
    """
    Speak text and return detailed result.

    Args:
        text: Text to speak
        preferred_provider: Preferred provider name (optional)

    Returns:
        VoiceServiceResult with details, or None if failed
    """
    manager = get_voice_manager()
    if not manager:
        return None

    return manager.speak(text, preferred_provider=preferred_provider)


def list_available_services():
    """List available voice services"""
    manager = get_voice_manager()
    if not manager:
        return []

    return manager.list_available_services()


def get_voice_stats():
    """Get voice service statistics"""
    manager = get_voice_manager()
    if not manager:
        return {}

    return manager.get_stats()


# Backward compatibility: Provide same interface as JARVISElevenLabsVoice
class VoiceServiceWrapper:
    """
    Wrapper class that provides same interface as JARVISElevenLabsVoice
    but uses Voice Service Manager internally (with fallbacks).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize wrapper"""
        self.manager = get_voice_manager()
        self.logger = get_logger("VoiceServiceWrapper")

        if self.manager:
            self.logger.info("✅ Voice Service Wrapper initialized (with fallbacks)")
        else:
            self.logger.warning("⚠️  Voice Service Manager not available")

    def speak(self, text: str, voice_id: Optional[str] = None,
              model: Optional[str] = None, save_audio: bool = False) -> Optional[bytes]:
        """
        Speak text (compatible with JARVISElevenLabsVoice interface).

        Note: voice_id and model are ignored (manager handles provider selection).
        save_audio is not yet supported in manager.
        """
        if not self.manager:
            self.logger.warning("⚠️  Voice Service Manager not available")
            return None

        result = self.manager.speak(text)

        if result.success:
            return result.audio_data
        else:
            self.logger.warning(f"⚠️  Voice output failed: {result.error}")
            return None

    def is_available(self) -> bool:
        """Check if voice service is available"""
        return self.manager is not None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Service Integration")
    parser.add_argument("--speak", type=str, help="Text to speak")
    parser.add_argument("--provider", type=str, help="Preferred provider")
    parser.add_argument("--list", action="store_true", help="List available services")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    if args.list:
        services = list_available_services()
        print("\n🎤 Available Voice Services:")
        print("=" * 80)
        for service in services:
            status = "✅" if service["available"] else "❌"
            print(f"  {status} {service['name']} (Priority: {service['priority']}, Quality: {service['quality']:.2f})")
        print("=" * 80)

    elif args.stats:
        stats = get_voice_stats()
        print("\n📊 Voice Service Statistics:")
        print("=" * 80)
        print(f"  Total Requests: {stats.get('total_requests', 0)}")
        print(f"  Successful: {stats.get('successful', 0)}")
        print(f"  Failed: {stats.get('failed', 0)}")
        print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
        print(f"  Fallback Rate: {stats.get('fallback_rate', 0):.1f}%")
        print(f"\n  Provider Usage:")
        for provider, count in stats.get('provider_usage', {}).items():
            print(f"    • {provider}: {count}")
        print("=" * 80)

    elif args.speak:
        success = speak(args.speak, preferred_provider=args.provider)
        if success:
            print("✅ Voice output successful")
        else:
            print("❌ Voice output failed")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()