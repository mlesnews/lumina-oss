#!/usr/bin/env python3
"""
Character & Voice Actor Model Manager
Different @MARK @MODELS / VERSIONING for each @CHAR[#CHARACTER + @VOICE-ACTOR[#ACTING]]

Manages model versioning per character and voice actor combination.
Each character + voice actor gets their own model configuration and versioning.

Tags: #CHARACTER #VOICE-ACTOR #MODEL #VERSIONING @CHAR @ACTING @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CharacterVoiceActorModelManager")


@dataclass
class ModelVersion:
    """Model version information"""
    model_id: str
    model_name: str
    provider: str
    version: str
    mark: str
    display_name: str
    characteristics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VoiceConfig:
    """Voice configuration for voice actor"""
    elevenlabs_voice_id: str
    voice_name: str
    voice_style: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VoiceActorModels:
    """Model configuration for a voice actor"""
    voice_actor_name: str
    voice_actor_id: str
    primary_model: ModelVersion
    alternative_models: List[ModelVersion] = field(default_factory=list)
    voice_config: Optional[VoiceConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.voice_config:
            data['voice_config'] = self.voice_config.to_dict()
        return data


@dataclass
class CharacterModels:
    """Model configuration for a character"""
    character_name: str
    character_id: str
    voice_actors: Dict[str, VoiceActorModels] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'character_name': self.character_name,
            'character_id': self.character_id,
            'voice_actors': {
                va_id: va.to_dict() for va_id, va in self.voice_actors.items()
            }
        }
        return data


class CharacterVoiceActorModelManager:
    """
    Character & Voice Actor Model Manager

    Manages different @MARK @MODELS / VERSIONING for each 
    @CHAR[#CHARACTER + @VOICE-ACTOR[#ACTING]]
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize character/voice-actor model manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "character_voice_actor_models.json"

        self.characters: Dict[str, CharacterModels] = {}
        self.default_model: Optional[ModelVersion] = None

        self._load_config()

        logger.info("✅ Character/Voice-Actor Model Manager initialized")

    def _load_config(self):
        """Load configuration from JSON file"""
        if not self.config_file.exists():
            logger.warning(f"Config file not found: {self.config_file}")
            logger.info("Creating default configuration...")
            self._create_default_config()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            char_models_config = config_data.get("character_voice_actor_models", {})
            characters_config = char_models_config.get("characters", {})

            # Load character configurations
            for char_id, char_config in characters_config.items():
                char_name = char_config.get("character_name", char_id)

                # Load voice actors
                voice_actors = {}
                for va_id, va_config in char_config.get("voice_actors", {}).items():
                    va_name = va_config.get("voice_actor_name", va_id)

                    # Primary model
                    primary_config = va_config["models"]["primary"]
                    primary_model = ModelVersion(
                        model_id=primary_config["model_id"],
                        model_name=primary_config["model_name"],
                        provider=primary_config["provider"],
                        version=primary_config["version"],
                        mark=primary_config["mark"],
                        display_name=primary_config["display_name"],
                        characteristics=primary_config.get("characteristics", [])
                    )

                    # Alternative models
                    alternatives = []
                    for alt_config in va_config["models"].get("alternatives", []):
                        alt_model = ModelVersion(
                            model_id=alt_config["model_id"],
                            model_name=alt_config["model_name"],
                            provider=alt_config["provider"],
                            version=alt_config["version"],
                            mark=alt_config["mark"],
                            display_name=alt_config["display_name"],
                            characteristics=alt_config.get("characteristics", [])
                        )
                        alternatives.append(alt_model)

                    # Voice config
                    voice_config = None
                    if "voice_config" in va_config:
                        vc = va_config["voice_config"]
                        voice_config = VoiceConfig(
                            elevenlabs_voice_id=vc["elevenlabs_voice_id"],
                            voice_name=vc["voice_name"],
                            voice_style=vc["voice_style"]
                        )

                    voice_actors[va_id] = VoiceActorModels(
                        voice_actor_name=va_name,
                        voice_actor_id=va_id,
                        primary_model=primary_model,
                        alternative_models=alternatives,
                        voice_config=voice_config
                    )

                self.characters[char_id] = CharacterModels(
                    character_name=char_name,
                    character_id=char_id,
                    voice_actors=voice_actors
                )

            # Default model
            default_config = char_models_config.get("default_model", {})
            if default_config:
                self.default_model = ModelVersion(
                    model_id=default_config["model_id"],
                    model_name=default_config["model_name"],
                    provider=default_config["provider"],
                    version=default_config["version"],
                    mark=default_config["mark"],
                    display_name=default_config["display_name"]
                )

            logger.info(f"✅ Loaded {len(self.characters)} character configurations")
            total_voice_actors = sum(len(c.voice_actors) for c in self.characters.values())
            logger.info(f"   {total_voice_actors} voice actor configurations")

        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Use the config we just created
            self._load_config()
        except Exception as e:
            logger.error(f"Error creating default config: {e}", exc_info=True)

    def get_model(self, character_id: str, voice_actor_id: str, use_alternative: int = 0) -> Optional[ModelVersion]:
        """
        Get model for character + voice actor combination

        Args:
            character_id: Character ID (e.g., "@tony", "@mace", "@gandalf")
            voice_actor_id: Voice actor ID (e.g., "rdj", "samuel_jackson")
            use_alternative: Which alternative model to use (0 = primary, 1+ = alternative index)

        Returns:
            ModelVersion or None if not found
        """
        if character_id not in self.characters:
            logger.warning(f"Character not found: {character_id}, using default model")
            return self.default_model

        character = self.characters[character_id]

        if voice_actor_id not in character.voice_actors:
            logger.warning(f"Voice actor {voice_actor_id} not found for {character_id}, using default model")
            return self.default_model

        voice_actor = character.voice_actors[voice_actor_id]

        if use_alternative == 0:
            return voice_actor.primary_model
        else:
            alt_index = use_alternative - 1
            if alt_index < len(voice_actor.alternative_models):
                return voice_actor.alternative_models[alt_index]
            else:
                logger.warning(f"Alternative model {use_alternative} not available, using primary")
                return voice_actor.primary_model

    def get_voice_config(self, character_id: str, voice_actor_id: str) -> Optional[VoiceConfig]:
        """
        Get voice configuration for character + voice actor

        Args:
            character_id: Character ID
            voice_actor_id: Voice actor ID

        Returns:
            VoiceConfig or None
        """
        if character_id not in self.characters:
            return None

        character = self.characters[character_id]

        if voice_actor_id not in character.voice_actors:
            return None

        return character.voice_actors[voice_actor_id].voice_config

    def get_available_models(self, character_id: str, voice_actor_id: str) -> List[ModelVersion]:
        """
        Get all available models for character + voice actor

        Args:
            character_id: Character ID
            voice_actor_id: Voice actor ID

        Returns:
            List of ModelVersion (primary + alternatives)
        """
        if character_id not in self.characters:
            if self.default_model:
                return [self.default_model]
            return []

        character = self.characters[character_id]

        if voice_actor_id not in character.voice_actors:
            if self.default_model:
                return [self.default_model]
            return []

        voice_actor = character.voice_actors[voice_actor_id]
        models = [voice_actor.primary_model]
        models.extend(voice_actor.alternative_models)
        return models

    def list_characters(self) -> List[str]:
        """List all available character IDs"""
        return list(self.characters.keys())

    def list_voice_actors(self, character_id: str) -> List[str]:
        """List all voice actors for a character"""
        if character_id not in self.characters:
            return []
        return list(self.characters[character_id].voice_actors.keys())

    def get_model_info(self, character_id: str, voice_actor_id: str) -> Dict[str, Any]:
        """
        Get full model information for character + voice actor

        Returns:
            Dict with model info, voice config, and available models
        """
        model = self.get_model(character_id, voice_actor_id)
        voice_config = self.get_voice_config(character_id, voice_actor_id)
        available_models = self.get_available_models(character_id, voice_actor_id)

        return {
            "character_id": character_id,
            "voice_actor_id": voice_actor_id,
            "primary_model": model.to_dict() if model else None,
            "voice_config": voice_config.to_dict() if voice_config else None,
            "available_models": [m.to_dict() for m in available_models],
            "model_count": len(available_models)
        }


if __name__ == "__main__":
    # Test the manager
    manager = CharacterVoiceActorModelManager()

    print("\n" + "="*80)
    print("Character/Voice-Actor Model Manager Test")
    print("="*80 + "\n")

    # List characters
    print("Available Characters:")
    for char_id in manager.list_characters():
        print(f"  - {char_id}")
        va_list = manager.list_voice_actors(char_id)
        for va_id in va_list:
            print(f"    Voice Actors: {', '.join(va_list)}")
            model_info = manager.get_model_info(char_id, va_id)
            print(f"    Primary Model: {model_info['primary_model']['display_name']}")
            print(f"    Available Models: {model_info['model_count']}")
            print()

    # Test model retrieval
    print("\n" + "-"*80)
    print("Model Retrieval Tests:")
    print("-"*80 + "\n")

    test_combinations = [
        ("@tony", "rdj"),
        ("@mace", "samuel_jackson"),
        ("@gandalf", "ian_mckellen"),
        ("@jarvis", "paul_bettany")
    ]

    for char_id, va_id in test_combinations:
        model = manager.get_model(char_id, va_id)
        if model:
            print(f"{char_id} + {va_id}:")
            print(f"  Model: {model.display_name}")
            print(f"  Mark: {model.mark}")
            print(f"  Version: {model.version}")
            print(f"  Provider: {model.provider}")
            print()
        else:
            print(f"{char_id} + {va_id}: Model not found")
            print()
