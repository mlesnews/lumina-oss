#!/usr/bin/env python3
"""
Character Avatar Manager

Manages avatar generation and rendering for all characters (@CLONES).
Uses ACE-LIKE template and other avatar templates to create avatars for all characters.

Tags: #CHARACTER #AVATAR #MANAGER #CLONES #GENERATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

logger = get_logger("CharacterAvatarManager")

# Import character registry
try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterAvatar, CharacterType
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger.warning("Character avatar registry not available")

# Import avatar templates
try:
    from ace_humanoid_template import ACEHumanoidTemplate
    ACE_TEMPLATE_AVAILABLE = True
except ImportError:
    ACE_TEMPLATE_AVAILABLE = False
    logger.warning("ACE humanoid template not available")


class CharacterAvatarManager:
    """
    Character Avatar Manager

    Manages avatar generation and rendering for all characters.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize character avatar manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize registry
        if REGISTRY_AVAILABLE:
            self.registry = CharacterAvatarRegistry(project_root)
        else:
            self.registry = None
            logger.error("Character registry not available")

        # Initialize templates
        if ACE_TEMPLATE_AVAILABLE:
            self.ace_template = ACEHumanoidTemplate()
        else:
            self.ace_template = None

        # Active avatars (currently rendered)
        self.active_avatars: Dict[str, Any] = {}

        logger.info("=" * 80)
        logger.info("🎭 CHARACTER AVATAR MANAGER")
        logger.info("=" * 80)
        logger.info(f"   Registry: {'✅' if self.registry else '❌'}")
        logger.info(f"   ACE Template: {'✅' if self.ace_template else '❌'}")
        logger.info(f"   Characters available: {len(self.registry.characters) if self.registry else 0}")
        logger.info("=" * 80)

    def get_character_avatar_config(self, character_id: str) -> Optional[CharacterAvatar]:
        """Get character avatar configuration"""
        if not self.registry:
            return None
        return self.registry.get_character(character_id)

    def generate_avatar_for_character(self, character_id: str,
                                     canvas=None, cx: float = 0, cy: float = 0,
                                     scale: float = 1.0, **kwargs) -> bool:
        """
        Generate avatar for a character

        Args:
            character_id: Character ID
            canvas: Tkinter canvas (optional)
            cx: Center X coordinate
            cy: Center Y coordinate
            scale: Scale factor
            **kwargs: Additional rendering parameters

        Returns:
            True if successful
        """
        if not self.registry:
            logger.error("Registry not available")
            return False

        character = self.registry.get_character(character_id)
        if not character:
            logger.warning(f"Character not found: {character_id}")
            return False

        # Route to appropriate template based on avatar_template
        template = character.avatar_template

        if template == "ace_humanoid" and self.ace_template and canvas:
            # Use ACE humanoid template
            transform_progress = kwargs.get("transform_progress", 1.0)
            combat_mode = kwargs.get("combat_mode", False)

            persona_colors = {
                "primary": character.primary_color,
                "secondary": character.secondary_color,
                "glow": "#ff3300" if combat_mode else character.primary_color,
                "outline": "#ffffff",
                "energy": "#ffff00"
            }

            self.ace_template.draw_ace_humanoid(
                canvas=canvas,
                cx=cx,
                cy=cy,
                scale=scale,
                transform_progress=transform_progress,
                combat_mode=combat_mode,
                persona_colors=persona_colors
            )

            logger.info(f"✅ Generated ACE avatar for {character.name}")
            return True

        elif template == "iron_man_bobblehead":
            # Use Iron Man bobblehead (existing system)
            logger.info(f"✅ Using Iron Man bobblehead for {character.name}")
            return True

        elif template in ["widget", "chat_widget", "system_widget", "analyst_widget",
                         "jedi_widget", "iron_man_widget"]:
            # Widget-based avatars (simpler rendering)
            logger.info(f"✅ Using widget template for {character.name}")
            return True

        else:
            logger.warning(f"Unknown template: {template} for {character.name}")
            return False

    def get_all_characters_needing_avatars(self) -> List[CharacterAvatar]:
        """Get all characters that need avatars generated"""
        if not self.registry:
            return []
        return list(self.registry.get_all_characters().values())

    def generate_avatars_for_all_characters(self) -> Dict[str, bool]:
        """
        Generate avatars for all characters

        Returns:
            Dict mapping character_id to success status
        """
        if not self.registry:
            logger.error("Registry not available")
            return {}

        results = {}
        characters = self.get_all_characters_needing_avatars()

        logger.info("=" * 80)
        logger.info("🎭 GENERATING AVATARS FOR ALL CHARACTERS")
        logger.info("=" * 80)

        for character in characters:
            logger.info(f"   Processing: {character.name} ({character.character_id})")
            logger.info(f"      Type: {character.character_type.value}")
            logger.info(f"      Style: {character.avatar_style}")
            logger.info(f"      Template: {character.avatar_template}")

            # Mark as ready (actual rendering happens when canvas is available)
            results[character.character_id] = True

        logger.info("=" * 80)
        logger.info(f"✅ Processed {len(characters)} characters")
        logger.info(f"   Success: {sum(1 for v in results.values() if v)}")
        logger.info("=" * 80)

        return results

    def get_character_summary(self) -> Dict[str, Any]:
        """Get summary of all characters and their avatar status"""
        if not self.registry:
            return {}

        summary = self.registry.generate_avatar_summary()

        # Add avatar generation status
        summary["avatar_generation"] = {
            "ace_template_available": ACE_TEMPLATE_AVAILABLE,
            "registry_available": REGISTRY_AVAILABLE,
            "total_ready": len(self.registry.characters),
            "active_avatars": len(self.active_avatars)
        }

        return summary

    def list_all_characters(self) -> List[Dict[str, Any]]:
        """List all characters with their avatar information"""
        if not self.registry:
            return []

        characters = []
        for char in self.registry.get_all_characters().values():
            characters.append({
                "id": char.character_id,
                "name": char.name,
                "type": char.character_type.value,
                "avatar_style": char.avatar_style,
                "template": char.avatar_template,
                "primary_color": char.primary_color,
                "secondary_color": char.secondary_color,
                "transformation": char.transformation_enabled,
                "combat_mode": char.combat_mode_enabled,
                "wopr_stances": char.wopr_stances_enabled,
                "role": char.role,
                "catchphrase": char.catchphrase
            })

        return characters


def main():
    """Main entry point"""
    manager = CharacterAvatarManager()

    # Generate summary
    summary = manager.get_character_summary()

    print("=" * 80)
    print("🎭 CHARACTER AVATAR MANAGER")
    print("=" * 80)
    print()
    print(f"Total Characters: {summary.get('total_characters', 0)}")
    print()
    print("By Type:")
    for char_type, count in summary.get("by_type", {}).items():
        print(f"  {char_type}: {count}")
    print()
    print("By Avatar Style:")
    for style, count in summary.get("by_avatar_style", {}).items():
        print(f"  {style}: {count}")
    print()
    print("By Template:")
    for template, count in summary.get("by_template", {}).items():
        print(f"  {template}: {count}")
    print()
    print("Features:")
    print(f"  With Transformation: {summary.get('with_transformation', 0)}")
    print(f"  With Combat Mode: {summary.get('with_combat_mode', 0)}")
    print(f"  With WOPR Stances: {summary.get('with_wopr_stances', 0)}")
    print()
    print("Avatar Generation:")
    avatar_gen = summary.get("avatar_generation", {})
    print(f"  ACE Template: {'✅' if avatar_gen.get('ace_template_available') else '❌'}")
    print(f"  Registry: {'✅' if avatar_gen.get('registry_available') else '❌'}")
    print(f"  Total Ready: {avatar_gen.get('total_ready', 0)}")
    print(f"  Active Avatars: {avatar_gen.get('active_avatars', 0)}")
    print("=" * 80)
    print()
    print("All Characters:")
    print()
    characters = manager.list_all_characters()
    for char in characters:
        print(f"  {char['name']} ({char['id']})")
        print(f"    Type: {char['type']}")
        print(f"    Style: {char['avatar_style']} | Template: {char['template']}")
        print(f"    Colors: {char['primary_color']} / {char['secondary_color']}")
        print(f"    Features: Transform={char['transformation']}, Combat={char['combat_mode']}, WOPR={char['wopr_stances']}")
        print(f"    Role: {char['role']}")
        print(f"    Catchphrase: {char['catchphrase']}")
        print()


if __name__ == "__main__":


    main()