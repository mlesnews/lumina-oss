#!/usr/bin/env python3
"""
Avatar Display System

Displays all avatars (JARVIS, ACE, and others) in the HUD/dashboard.
Ensures avatars are always visible and integrated with the replica AI system.

Tags: #AVATAR #DISPLAY #HUD #REPLICA #JARVIS #ACE @JARVIS @LUMINA
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

logger = get_logger("AvatarDisplaySystem")

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterAvatar
    from character_avatar_manager import CharacterAvatarManager
    AVATAR_SYSTEM_AVAILABLE = True
except ImportError:
    AVATAR_SYSTEM_AVAILABLE = False
    logger.warning("Avatar system not available")

try:
    from replica_inspired_hybrid_system import ReplicaInspiredHybrid
    REPLICA_SYSTEM_AVAILABLE = True
except ImportError:
    REPLICA_SYSTEM_AVAILABLE = False
    logger.warning("Replica system not available")


@dataclass
class AvatarDisplay:
    """Avatar display configuration"""
    character_id: str
    name: str
    visible: bool = True
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    size: Dict[str, float] = field(default_factory=lambda: {"width": 100, "height": 100})
    opacity: float = 1.0
    z_index: int = 1000
    status: str = "active"  # active, idle, speaking, thinking
    last_interaction: Optional[str] = None
    replica_connected: bool = False


class AvatarDisplaySystem:
    """
    Avatar Display System

    Manages display of all avatars in HUD/dashboard.
    Ensures JARVIS, ACE, and all avatars are always visible.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize avatar display system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "avatar_display"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize avatar systems
        if AVATAR_SYSTEM_AVAILABLE:
            try:
                self.avatar_registry = CharacterAvatarRegistry(project_root=self.project_root)
                self.avatar_manager = CharacterAvatarManager(project_root=self.project_root)
                logger.info("✅ Avatar registry and manager initialized")
            except Exception as e:
                logger.warning(f"Could not initialize avatar systems: {e}")
                self.avatar_registry = None
                self.avatar_manager = None
        else:
            self.avatar_registry = None
            self.avatar_manager = None

        # Initialize replica system
        if REPLICA_SYSTEM_AVAILABLE:
            try:
                self.replica_system = ReplicaInspiredHybrid(project_root=self.project_root)
                logger.info("✅ Replica system initialized")
            except Exception as e:
                logger.warning(f"Could not initialize replica system: {e}")
                self.replica_system = None
        else:
            self.replica_system = None

        # Active avatar displays
        self.active_displays: Dict[str, AvatarDisplay] = {}

        # Load and initialize displays
        self._initialize_avatar_displays()

        logger.info("✅ Avatar Display System initialized")
        logger.info(f"   Active avatars: {len(self.active_displays)}")
        logger.info("   Avatars always visible: Enabled")

    def _initialize_avatar_displays(self):
        """Initialize avatar displays from registry"""
        if not self.avatar_registry:
            logger.warning("Avatar registry not available - cannot initialize displays")
            return

        # Get all characters
        characters = self.avatar_registry.get_all_characters()

        # Create displays for each character
        positions = self._calculate_avatar_positions(len(characters))

        for idx, (char_id, character) in enumerate(characters.items()):
            # Only show characters (not inanimate objects or mobs)
            if not character.is_character or character.is_mob:
                continue

            display = AvatarDisplay(
                character_id=char_id,
                name=character.name,
                visible=True,  # Always visible
                position=positions[idx] if idx < len(positions) else {"x": 0, "y": 0},
                size={"width": 120, "height": 120},
                opacity=1.0,
                z_index=1000 + idx,
                status="active",
                replica_connected=self.replica_system is not None
            )

            self.active_displays[char_id] = display

        logger.info(f"✅ Initialized {len(self.active_displays)} avatar displays")

        # Ensure JARVIS and ACE are prioritized
        if "jarvis" in self.active_displays:
            self.active_displays["jarvis"].z_index = 2000
            self.active_displays["jarvis"].position = {"x": 50, "y": 50}  # Top-left priority
            logger.info("   ✅ JARVIS avatar prioritized")

        if "ace" in self.active_displays:
            self.active_displays["ace"].z_index = 1900
            self.active_displays["ace"].position = {"x": 180, "y": 50}  # Next to JARVIS
            logger.info("   ✅ ACE avatar prioritized")

    def _calculate_avatar_positions(self, count: int) -> List[Dict[str, float]]:
        """Calculate positions for avatars in a grid"""
        positions = []

        # Grid layout: 4 columns, rows as needed
        cols = 4
        spacing_x = 150
        spacing_y = 150
        start_x = 50
        start_y = 50

        for i in range(count):
            row = i // cols
            col = i % cols
            x = start_x + (col * spacing_x)
            y = start_y + (row * spacing_y)
            positions.append({"x": x, "y": y})

        return positions

    def get_avatar_displays(self) -> Dict[str, Dict[str, Any]]:
        """Get all avatar displays for rendering"""
        displays = {}

        for char_id, display in self.active_displays.items():
            if not display.visible:
                continue

            # Get character details from registry
            character = None
            if self.avatar_registry:
                character = self.avatar_registry.get_character(char_id)

            displays[char_id] = {
                "character_id": display.character_id,
                "name": display.name,
                "visible": display.visible,
                "position": display.position,
                "size": display.size,
                "opacity": display.opacity,
                "z_index": display.z_index,
                "status": display.status,
                "last_interaction": display.last_interaction,
                "replica_connected": display.replica_connected,
                # Character details
                "character_type": character.character_type.value if character else "unknown",
                "avatar_template": character.avatar_template if character else "default",
                "avatar_style": character.avatar_style if character else "default",
                "primary_color": character.primary_color if character else "#00ff00",
                "secondary_color": character.secondary_color if character else "#00ffff",
                "catchphrase": character.catchphrase if character else "",
                "role": character.role if character else ""
            }

        return displays

    def update_avatar_status(self, character_id: str, status: str):
        """Update avatar status (active, idle, speaking, thinking)"""
        if character_id in self.active_displays:
            self.active_displays[character_id].status = status
            self.active_displays[character_id].last_interaction = datetime.now().isoformat()
            logger.debug(f"Updated {character_id} status: {status}")

    def show_avatar(self, character_id: str):
        """Show an avatar"""
        if character_id in self.active_displays:
            self.active_displays[character_id].visible = True
            logger.info(f"✅ Showing avatar: {character_id}")

    def hide_avatar(self, character_id: str):
        """Hide an avatar (but keep in system)"""
        if character_id in self.active_displays:
            self.active_displays[character_id].visible = False
            logger.info(f"🔇 Hiding avatar: {character_id}")

    def ensure_all_avatars_visible(self):
        """Ensure all avatars are visible (user requirement)"""
        for display in self.active_displays.values():
            display.visible = True
        logger.info("✅ All avatars set to visible")

    def get_avatar_display_data(self) -> Dict[str, Any]:
        """Get complete avatar display data for HUD integration"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_avatars": len(self.active_displays),
            "visible_avatars": sum(1 for d in self.active_displays.values() if d.visible),
            "avatars": self.get_avatar_displays(),
            "replica_system_connected": self.replica_system is not None,
            "avatar_system_available": AVATAR_SYSTEM_AVAILABLE
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Avatar Display System")
        parser.add_argument("--list", action="store_true", help="List all avatars")
        parser.add_argument("--show-all", action="store_true", help="Show all avatars")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = AvatarDisplaySystem()

        if args.show_all:
            system.ensure_all_avatars_visible()
            print("✅ All avatars set to visible")

        if args.list or not args.show_all:
            displays = system.get_avatar_display_data()

            if args.json:
                print(json.dumps(displays, indent=2, default=str))
            else:
                print("=" * 80)
                print("🎭 AVATAR DISPLAY SYSTEM")
                print("=" * 80)
                print(f"Total Avatars: {displays['total_avatars']}")
                print(f"Visible Avatars: {displays['visible_avatars']}")
                print(f"Replica System: {'✅ Connected' if displays['replica_system_connected'] else '❌ Not Connected'}")
                print()
                print("Avatars:")
                for char_id, avatar in displays['avatars'].items():
                    status_icon = "✅" if avatar['visible'] else "⏸️"
                    replica_icon = "🔗" if avatar['replica_connected'] else ""
                    print(f"  {status_icon} {avatar['name']} ({char_id}) {replica_icon}")
                    print(f"      Status: {avatar['status']}")
                    print(f"      Position: ({avatar['position']['x']}, {avatar['position']['y']})")
                    print(f"      Template: {avatar['avatar_template']}")
                    print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()