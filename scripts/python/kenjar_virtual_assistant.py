#!/usr/bin/env python3
"""
Kenjar Virtual Assistant - JARVIS-Focused Virtual Assistant

Kenjar = Kenny + JARVIS
Always JARVIS, not Kenny (Kenny is "basically chopped" - deprecated)

Fully functional virtual assistant dedicated to JARVIS.

Tags: #KENJAR #JARVIS #VIRTUAL_ASSISTANT #KENNY_DEPRECATED @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

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

logger = get_logger("KenjarAssistant")


@dataclass
class KenjarConfig:
    """Kenjar configuration"""
    name: str = "Kenjar"
    identity: str = "JARVIS"  # Always JARVIS, not Kenny
    personality: str = "professional, helpful, efficient"
    voice_enabled: bool = True
    voice_provider: str = "elevenlabs"  # ElevenLabs for JARVIS voice
    capabilities: List[str] = field(default_factory=lambda: [
        "voice_commands",
        "text_processing",
        "ide_control",
        "file_operations",
        "web_search",
        "knowledge_retrieval",
        "task_management"
    ])
    kenny_deprecated: bool = True  # Kenny is "basically chopped"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KenjarVirtualAssistant:
    """
    Kenjar Virtual Assistant

    JARVIS-focused virtual assistant.
    Always JARVIS, not Kenny (Kenny is deprecated).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Kenjar"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        self.config_file = self.config_dir / "kenjar_config.json"
        self.config = KenjarConfig()
        self._load_config()

        # JARVIS integrations
        self.voice_interface = None
        self.elevenlabs_voice = None
        self.hands_free_control = None

        # Initialize components
        self._initialize_components()

        logger.info("=" * 80)
        logger.info("🤖 KENJAR VIRTUAL ASSISTANT")
        logger.info("=" * 80)
        logger.info(f"   Name: {self.config.name}")
        logger.info(f"   Identity: {self.config.identity} (NOT Kenny - Kenny is deprecated)")
        logger.info(f"   Voice: {'✅ Enabled' if self.config.voice_enabled else '❌ Disabled'}")
        logger.info(f"   Voice Provider: {self.config.voice_provider}")
        logger.info(f"   Capabilities: {len(self.config.capabilities)}")
        logger.info("=" * 80)

    def _load_config(self):
        """Load Kenjar configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = KenjarConfig(**data)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")
                self._save_config()
        else:
            self._save_config()

    def _save_config(self):
        """Save Kenjar configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving config: {e}")

    def _initialize_components(self):
        """Initialize JARVIS components"""
        # Voice interface
        if self.config.voice_enabled:
            try:
                from jarvis_voice_interface import JARVISVoiceInterface
                self.voice_interface = JARVISVoiceInterface(self.project_root)
                logger.info("   ✅ Voice interface initialized")
            except Exception as e:
                logger.warning(f"   ⚠️  Voice interface not available: {e}")

            # ElevenLabs voice
            if self.config.voice_provider == "elevenlabs":
                try:
                    from jarvis_elevenlabs_voice import JARVISElevenLabsVoice
                    self.elevenlabs_voice = JARVISElevenLabsVoice(self.project_root)
                    logger.info("   ✅ ElevenLabs voice initialized")
                except Exception as e:
                    logger.warning(f"   ⚠️  ElevenLabs voice not available: {e}")

        # Hands-free control
        try:
            from jarvis_hands_free_voice_control import JARVISHandsFreeVoiceControl
            self.hands_free_control = JARVISHandsFreeVoiceControl(self.project_root)
            logger.info("   ✅ Hands-free control initialized")
        except Exception as e:
            logger.warning(f"   ⚠️  Hands-free control not available: {e}")

    def process_request(self, request: str, request_type: str = "text") -> Dict[str, Any]:
        """
        Process request as JARVIS (not Kenny)

        Args:
            request: Request text
            request_type: Type of request (text, voice)

        Returns:
            Response dictionary
        """
        logger.info(f"   📥 Processing request as {self.config.identity}: {request[:50]}...")

        # Process via hands-free control
        if self.hands_free_control:
            try:
                result = self.hands_free_control.process_voice_input(request)
                return {
                    "status": "success",
                    "identity": self.config.identity,
                    "response": result,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"   ❌ Processing error: {e}")
                return {
                    "status": "error",
                    "identity": self.config.identity,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

        return {
            "status": "error",
            "identity": self.config.identity,
            "error": "Hands-free control not available",
            "timestamp": datetime.now().isoformat()
        }

    def speak(self, text: str, use_elevenlabs: bool = True) -> bool:
        """
        Speak as JARVIS (not Kenny)

        Args:
            text: Text to speak
            use_elevenlabs: Use ElevenLabs if available

        Returns:
            True if spoken, False otherwise
        """
        if not self.config.voice_enabled:
            return False

        # Use ElevenLabs if available and requested
        if use_elevenlabs and self.elevenlabs_voice:
            try:
                self.elevenlabs_voice.speak(text)
                logger.info(f"   🎤 JARVIS spoke (ElevenLabs): {text[:50]}...")
                return True
            except Exception as e:
                logger.warning(f"   ⚠️  ElevenLabs error: {e}")

        # Fallback to regular voice interface
        if self.voice_interface:
            try:
                self.voice_interface.speak(text)
                logger.info(f"   🎤 JARVIS spoke: {text[:50]}...")
                return True
            except Exception as e:
                logger.warning(f"   ⚠️  Voice interface error: {e}")

        return False

    def listen(self) -> Optional[str]:
        """
        Listen for voice input

        Returns:
            Recognized text or None
        """
        if not self.voice_interface:
            return None

        try:
            text = self.voice_interface.listen()
            if text:
                logger.info(f"   👂 JARVIS heard: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"   ❌ Listen error: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get Kenjar status"""
        return {
            "name": self.config.name,
            "identity": self.config.identity,
            "kenny_deprecated": self.config.kenny_deprecated,
            "voice_enabled": self.config.voice_enabled,
            "voice_provider": self.config.voice_provider,
            "capabilities": self.config.capabilities,
            "components": {
                "voice_interface": self.voice_interface is not None,
                "elevenlabs_voice": self.elevenlabs_voice is not None,
                "hands_free_control": self.hands_free_control is not None
            },
            "timestamp": datetime.now().isoformat()
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Kenjar Virtual Assistant")
        parser.add_argument("--request", type=str, help="Process request")
        parser.add_argument("--speak", type=str, help="Speak text")
        parser.add_argument("--listen", action="store_true", help="Listen for voice")
        parser.add_argument("--status", action="store_true", help="Get status")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        kenjar = KenjarVirtualAssistant()

        if args.request:
            result = kenjar.process_request(args.request)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"✅ Processed as {result['identity']}: {result.get('status')}")

        elif args.speak:
            spoken = kenjar.speak(args.speak)
            if args.json:
                print(json.dumps({"spoken": spoken}, indent=2))
            else:
                print(f"{'✅ Spoken' if spoken else '❌ Could not speak'}")

        elif args.listen:
            text = kenjar.listen()
            if args.json:
                print(json.dumps({"text": text}, indent=2))
            else:
                print(f"👂 Heard: {text if text else 'Nothing'}")

        elif args.status or not any([args.request, args.speak, args.listen]):
            status = kenjar.get_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print("=" * 80)
                print("🤖 KENJAR VIRTUAL ASSISTANT STATUS")
                print("=" * 80)
                print(f"Name: {status['name']}")
                print(f"Identity: {status['identity']} (NOT Kenny - Kenny is deprecated)")
                print(f"Voice: {'✅ Enabled' if status['voice_enabled'] else '❌ Disabled'}")
                print(f"Voice Provider: {status['voice_provider']}")
                print(f"Capabilities: {len(status['capabilities'])}")
                print("\nComponents:")
                for comp, available in status['components'].items():
                    print(f"  • {comp}: {'✅' if available else '❌'}")
                print("=" * 80)

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()