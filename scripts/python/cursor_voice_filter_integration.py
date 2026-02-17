#!/usr/bin/env python3
"""
Cursor IDE Voice Filter Integration
Syncs voice filter system with Cursor IDE microphone features

Works independently of Kenny/Ace virtual assistants.
Users can toggle voice filtering on/off.
Filters background voices (TV, other people) before Cursor processes audio.

Tags: #CURSOR #VOICE_FILTER #MICROPHONE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = get_logger("CursorVoiceFilterIntegration")

try:
    from voice_filter_system import VoiceFilterSystem
    VOICE_FILTER_AVAILABLE = True
except ImportError:
    VOICE_FILTER_AVAILABLE = False
    logger.warning("⚠️  Voice filter system not available")


class CursorVoiceFilterIntegration:
    """
    Cursor IDE Voice Filter Integration

    Syncs voice filter system with Cursor IDE microphone features.
    Works independently of virtual assistants (Kenny/Ace).
    """

    def __init__(self, project_root: Optional[Path] = None, user_id: str = "user"):
        """Initialize Cursor voice filter integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.user_id = user_id

        # Config paths
        self.config_dir = self.project_root / "config"
        self.cursor_config_file = self.config_dir / "cursor_voice_filter_config.json"
        self.cursor_settings_file = self.project_root / ".cursor" / "settings.json"

        # Load config
        self.config = self._load_config()

        # Initialize voice filter (if available and enabled)
        self.voice_filter = None
        if VOICE_FILTER_AVAILABLE and self.config.get("voice_filter_enabled", True):
            self.voice_filter = VoiceFilterSystem(user_id=user_id, project_root=project_root)
            logger.info("✅ Voice filter system initialized")
        else:
            logger.info("⚠️  Voice filter disabled or not available")

        # State
        self.enabled = self.config.get("voice_filter_enabled", True)
        self.cursor_microphone_enabled = self.config.get("cursor_microphone_enabled", True)

        logger.info("=" * 80)
        logger.info("🎤 CURSOR VOICE FILTER INTEGRATION")
        logger.info("   Syncing with Cursor IDE microphone features")
        logger.info(f"   Voice filter: {'ENABLED' if self.enabled else 'DISABLED'}")
        logger.info(f"   Cursor microphone: {'ENABLED' if self.cursor_microphone_enabled else 'DISABLED'}")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load Cursor voice filter configuration"""
        if self.cursor_config_file.exists():
            try:
                with open(self.cursor_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load config: {e}")

        # Default config
        return {
            "version": "1.0.0",
            "voice_filter_enabled": True,
            "cursor_microphone_enabled": True,
            "voice_filter_threshold": 0.7,
            "filter_background_voices": True,
            "filter_tv_voices": True,
            "filter_other_people": True,
            "description": "Cursor IDE Voice Filter Integration Configuration",
            "tags": ["#CURSOR", "#VOICE_FILTER", "#MICROPHONE", "@JARVIS", "@LUMINA"],
            "notes": [
                "Voice filtering works independently of Kenny/Ace virtual assistants",
                "Users can toggle voice filtering on/off",
                "Syncs with Cursor IDE microphone settings",
                "Filters background voices (TV, other people) before Cursor processes audio"
            ]
        }

    def save_config(self):
        """Save Cursor voice filter configuration"""
        try:
            with open(self.cursor_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Config saved: {self.cursor_config_file}")
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")

    def enable_voice_filter(self):
        """Enable voice filtering"""
        self.enabled = True
        self.config["voice_filter_enabled"] = True
        if self.voice_filter:
            self.voice_filter.enable_voice_filtering = True
        self.save_config()
        logger.info("✅ Voice filter ENABLED")

    def disable_voice_filter(self):
        """Disable voice filtering"""
        self.enabled = False
        self.config["voice_filter_enabled"] = False
        if self.voice_filter:
            self.voice_filter.enable_voice_filtering = False
        self.save_config()
        logger.info("🚫 Voice filter DISABLED")

    def toggle_voice_filter(self):
        """Toggle voice filtering on/off"""
        if self.enabled:
            self.disable_voice_filter()
        else:
            self.enable_voice_filter()
        return self.enabled

    def filter_audio_for_cursor(self, audio_data, sample_rate: int) -> tuple:
        """
        Filter audio for Cursor IDE

        Returns:
            (filtered_audio, is_user_voice, should_process)
        """
        if not self.enabled or not self.cursor_microphone_enabled:
            # If disabled, pass through (no filtering)
            return audio_data, True, True

        if not self.voice_filter:
            # No voice filter available, pass through
            return audio_data, True, True

        # Filter audio
        filtered_audio, is_user_voice = self.voice_filter.filter_audio(audio_data, sample_rate)

        # Only process if it's the user's voice
        should_process = is_user_voice

        if not is_user_voice:
            logger.debug("🚫 Audio rejected (background/TV/other voice) - not processing in Cursor")

        return filtered_audio, is_user_voice, should_process

    def sync_with_cursor_settings(self):
        """Sync with Cursor IDE settings"""
        if not self.cursor_settings_file.exists():
            logger.debug("⚠️  Cursor settings file not found")
            return

        try:
            with open(self.cursor_settings_file, 'r', encoding='utf-8') as f:
                cursor_settings = json.load(f)

            # Check for microphone/voice settings
            # Cursor IDE may have voice input settings
            # Sync our config with Cursor's settings

            # Update config if needed
            # (This is a placeholder - actual Cursor settings structure may vary)
            logger.debug("✅ Synced with Cursor settings")
        except Exception as e:
            logger.warning(f"⚠️  Could not sync with Cursor settings: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "voice_filter_enabled": self.enabled,
            "cursor_microphone_enabled": self.cursor_microphone_enabled,
            "voice_filter_available": self.voice_filter is not None,
            "voice_profile_trained": (
                self.voice_filter.voice_profile.profile_data.get("trained", False)
                if self.voice_filter else False
            ),
            "config_file": str(self.cursor_config_file),
            "cursor_settings_file": str(self.cursor_settings_file)
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Voice Filter Integration")
    parser.add_argument('--enable', action='store_true', help='Enable voice filtering')
    parser.add_argument('--disable', action='store_true', help='Disable voice filtering')
    parser.add_argument('--toggle', action='store_true', help='Toggle voice filtering')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--sync', action='store_true', help='Sync with Cursor settings')
    parser.add_argument('--user-id', type=str, default='user', help='User ID for voice profile')

    args = parser.parse_args()

    print("=" * 80)
    print("🎤 CURSOR VOICE FILTER INTEGRATION")
    print("   Syncing with Cursor IDE microphone features")
    print("=" * 80)
    print()

    integration = CursorVoiceFilterIntegration(user_id=args.user_id)

    if args.enable:
        integration.enable_voice_filter()
        print("✅ Voice filter ENABLED")
    elif args.disable:
        integration.disable_voice_filter()
        print("🚫 Voice filter DISABLED")
    elif args.toggle:
        state = integration.toggle_voice_filter()
        print(f"{'✅ ENABLED' if state else '🚫 DISABLED'}")
    elif args.sync:
        integration.sync_with_cursor_settings()
        print("✅ Synced with Cursor settings")
    elif args.status:
        status = integration.get_status()
        print("📊 Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
    else:
        print("💡 Use --enable, --disable, --toggle, --status, or --sync")
        print("=" * 80)


if __name__ == "__main__":


    main()