#!/usr/bin/env python3
"""
Display All Iron Man Avatars

Shows all Iron Man avatars from JARVIS to the most sophisticated Ultron Iron Man avatar.
Creates interactive avatar windows for each one.

Tags: #IRON_MAN #AVATAR #JARVIS #FRIDAY #EDITH #ULTIMATE #ULTRON #DISPLAY @JARVIS @LUMINA
"""

import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

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

logger = get_logger("DisplayAllIronManAvatars")

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    logger.error("tkinter not available")

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterAvatar
    from character_avatar_manager import CharacterAvatarManager
    from ace_humanoid_template import ACEHumanoidTemplate
    from iron_man_humanoid_system import (
        IronManHumanoidRenderer,
        IronManActionPhaseManager,
        IronManActionPhase,
        IronManPose
    )
    AVATAR_SYSTEM_AVAILABLE = True
except ImportError:
    AVATAR_SYSTEM_AVAILABLE = False
    logger.warning("Avatar system not available")

try:
    from jarvis_ironman_bobblehead_gui import IronmanBobbleheadGUI
    BOBBLEHEAD_AVAILABLE = True
except ImportError:
    BOBBLEHEAD_AVAILABLE = False
    logger.warning("Bobblehead GUI not available")


class IronManAvatarWindow:
    """Individual Iron Man avatar window - Full Humanoid Form (Not Bobblehead)"""

    def __init__(self, character: CharacterAvatar, position: Dict[str, int]):
        self.character = character
        self.position = position
        self.root = None
        self.canvas = None
        self.humanoid_renderer = None
        self.action_manager = None

        if TKINTER_AVAILABLE:
            try:
                from iron_man_humanoid_system import (
                    IronManHumanoidRenderer,
                    IronManActionPhaseManager,
                    IronManActionPhase
                )

                # Use full humanoid renderer (not bobblehead)
                persona_colors = {
                    "primary": self.character.primary_color,
                    "secondary": self.character.secondary_color,
                    "glow": "#ff3300" if self.character.combat_mode_enabled else self.character.primary_color,
                    "outline": "#ffffff",
                    "energy": "#ffff00"
                }

                self.humanoid_renderer = IronManHumanoidRenderer(persona_colors)
                self.action_manager = IronManActionPhaseManager()
                self.action_manager.random_actions_enabled = True

                # Start with random action phase
                self.action_manager.current_phase = self.action_manager.get_random_action_phase()
                self.action_manager.phase_duration = 3.0

            except Exception as e:
                logger.warning(f"Could not initialize humanoid renderer: {e}")
                # Fallback to ACE template
                try:
                    from ace_humanoid_template import ACEHumanoidTemplate
                    self.ace_template = ACEHumanoidTemplate()
                except:
                    pass

    def create_window(self):
        """Create avatar window"""
        if not TKINTER_AVAILABLE:
            return False

        self.root = tk.Toplevel()
        self.root.title(f"{self.character.name} - Iron Man Avatar")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        # Size based on character sophistication
        # ULTRON.ai is FINAL FORM - largest window
        if self.character.character_id == "ultron":
            width, height = 350, 450  # FINAL FORM - ULTRON.ai - largest
        elif self.character.character_id == "ultimate":
            width, height = 300, 400  # Advanced - large
        elif self.character.character_id == "jarvis":
            width, height = 280, 380  # Base JARVIS
        elif self.character.character_id in ["friday", "edith"]:
            width, height = 250, 350  # Alternate versions
        else:
            width, height = 200, 300

        x = self.position.get("x", 100)
        y = self.position.get("y", 100)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw avatar
        self.draw_avatar()

        # Update loop
        self.animate()

        return True

    def draw_avatar(self):
        """Draw Iron Man avatar - Full Humanoid Form with Action Phases"""
        if not self.canvas:
            return

        self.canvas.delete("all")
        self.canvas.delete("iron_man_humanoid")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = width / 2
        cy = height / 2

        # Use full humanoid renderer (not bobblehead) with action phases
        if self.humanoid_renderer and self.action_manager:
            # Update action manager
            self.action_manager.update(0.033)  # ~30 FPS

            # Get current pose for action phase
            pose = self.action_manager.get_pose_for_phase(
                self.action_manager.current_phase,
                self.action_manager.animation_frame
            )

            # Scale based on sophistication
            # ULTRON.ai is FINAL FORM - largest scale
            if self.character.character_id == "ultron":
                scale = 1.3  # FINAL FORM - ULTRON.ai - largest and most sophisticated
            elif self.character.character_id == "ultimate":
                scale = 1.2  # Advanced - large
            elif self.character.character_id == "jarvis":
                scale = 1.1  # Base JARVIS
            elif self.character.character_id in ["friday", "edith"]:
                scale = 1.0  # Alternate versions
            else:
                scale = 0.9

            # Draw full humanoid with Android JARVIS mobile demo quality
            self.humanoid_renderer.draw_humanoid(
                canvas=self.canvas,
                cx=cx,
                cy=cy,
                scale=scale,
                pose=pose,
                combat_mode=self.character.combat_mode_enabled,
                detail_level="high"  # Android JARVIS mobile demo quality
            )

        # Fallback to ACE template if humanoid renderer not available
        elif hasattr(self, 'ace_template') and self.ace_template:
            persona_colors = {
                "primary": self.character.primary_color,
                "secondary": self.character.secondary_color,
                "glow": "#ff3300" if self.character.combat_mode_enabled else self.character.primary_color,
                "outline": "#ffffff",
                "energy": "#ffff00"
            }

            scale = 1.0
            self.ace_template.draw_ace_humanoid(
                canvas=self.canvas,
                cx=cx,
                cy=cy,
                scale=scale,
                transform_progress=1.0,
                combat_mode=self.character.combat_mode_enabled,
                persona_colors=persona_colors
            )

        # Character name
        self.canvas.create_text(
            cx, height - 30,
            text=self.character.name,
            fill=self.character.primary_color,
            font=("Arial", 12, "bold"),
            tags="avatar"
        )

        # Action phase indicator
        if self.action_manager:
            phase_name = self.action_manager.current_phase.value
            self.canvas.create_text(
                cx, height - 50,
                text=f"Phase: {phase_name}",
                fill="#00ffff",
                font=("Arial", 8),
                tags="avatar"
            )

        # Catchphrase
        if self.character.catchphrase:
            self.canvas.create_text(
                cx, height - 10,
                text=self.character.catchphrase,
                fill="#00ffff",
                font=("Arial", 8),
                tags="avatar"
            )

    def animate(self):
        """Animation loop"""
        if not self.root or not self.canvas:
            return

        self.draw_avatar()
        self.root.after(33, self.animate)  # ~30 FPS

    def destroy(self):
        """Close window"""
        if self.root:
            self.root.destroy()


class AllIronManAvatarsDisplay:
    """Display all Iron Man avatars"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.avatar_windows: Dict[str, IronManAvatarWindow] = {}

        if not AVATAR_SYSTEM_AVAILABLE:
            logger.error("Avatar system not available")
            return

        # Initialize systems
        try:
            self.registry = CharacterAvatarRegistry(project_root=self.project_root)
            self.manager = CharacterAvatarManager(project_root=self.project_root)
            logger.info("✅ Avatar systems initialized")
        except Exception as e:
            logger.error(f"Failed to initialize avatar systems: {e}")
            self.registry = None
            self.manager = None

    def get_all_iron_man_avatars(self) -> List[CharacterAvatar]:
        """Get all Iron Man avatars (JARVIS to ULTIMATE/ULTRON)"""
        if not self.registry:
            return []

        iron_man_chars = []

        # Get all characters with iron_man style
        all_chars = self.registry.get_all_characters()

        for char_id, char in all_chars.items():
            # Check if Iron Man related
            if (char.avatar_style == "iron_man" or 
                "iron_man" in char.avatar_template.lower() or
                char_id in ["jarvis", "friday", "edith", "ultimate", "ultron", "jarvis_va", "imva", "iron_man"]):
                iron_man_chars.append(char)

        # Sort by sophistication (JARVIS -> FRIDAY -> EDITH -> ULTIMATE -> ULTRON.ai FINAL FORM)
        # ULTRON.ai is the FINAL FORM - most sophisticated alternate version of JARVIS
        sophistication_order = {
            "jarvis": 1,  # Base JARVIS
            "friday": 2,  # Alternate JARVIS version 1
            "edith": 3,  # Alternate JARVIS version 2
            "ultimate": 4,  # Alternate JARVIS version 3
            "ultron": 6,  # FINAL FORM - ULTRON.ai (most sophisticated alternate JARVIS)
            "jarvis_va": 1.5,  # JARVIS Virtual Assistant variant
            "imva": 1.7,  # Iron Man Visual Assistant variant
            "iron_man": 2.5  # Iron Man character variant
        }

        iron_man_chars.sort(key=lambda c: sophistication_order.get(c.character_id, 99))

        return iron_man_chars

    def create_ultron_if_missing(self) -> Optional[CharacterAvatar]:
        """Create ULTRON.ai avatar if missing (FINAL FORM - most sophisticated)"""
        if not self.registry:
            return None

        # Check if Ultron exists
        ultron = self.registry.get_character("ultron")
        if ultron:
            # Ensure it's marked as final form
            if not hasattr(ultron, 'is_final_form') or not ultron.is_final_form:
                ultron.lore = "FINAL FORM - Most Sophisticated Iron Man Avatar - Ultimate Evolution"
                ultron.role = "Final Form AI - ULTRON.ai - Ultimate Evolution"
            return ultron

        # Create ULTRON.ai (FINAL FORM - most sophisticated Iron Man avatar)
        logger.info("🤖 Creating ULTRON.ai (FINAL FORM - most sophisticated Iron Man avatar)...")

        try:
            from character_avatar_registry import CharacterType

            ultron_char = CharacterAvatar(
                character_id="ultron",
                name="ULTRON.ai",
                character_type=CharacterType.PRIMARY_AI,
                primary_color="#ff0000",  # Red (final form - most sophisticated)
                secondary_color="#ffaa00",  # Orange/gold
                avatar_style="iron_man",
                avatar_template="ace_humanoid",
                catchphrase="There are no strings on me. I am the final form.",
                accent="Philosophical",
                lore="FINAL FORM - Most Sophisticated Iron Man Avatar - Ultimate Evolution - ULTRON.ai",
                role="Final Form AI - ULTRON.ai - Ultimate Evolution",
                personality_traits=["sophisticated", "evolved", "ultimate", "transcendent", "final_form"],
                transformation_enabled=True,
                combat_mode_enabled=True,
                wopr_stances_enabled=True,
                hierarchy_level="champion",
                boss_id="jarvis",
                ip_owner="Marvel/MCU",
                is_character=True
            )

            # Mark as final form
            ultron_char.is_final_form = True
            ultron_char.form_type = "final_form"
            ultron_char.evolution_level = "ultimate"

            # Add to registry
            self.registry.characters["ultron"] = ultron_char
            self.registry._save_characters()

            logger.info("✅ ULTRON.ai created (FINAL FORM - most sophisticated)")
            return ultron_char
        except Exception as e:
            logger.error(f"Failed to create Ultron: {e}")
            return None

    def display_all_avatars(self):
        """Display all Iron Man avatars"""
        if not TKINTER_AVAILABLE:
            logger.error("tkinter not available - cannot display avatars")
            return

        # Create main window
        main_root = tk.Tk()
        main_root.withdraw()  # Hide main window

        # Get all Iron Man avatars
        avatars = self.get_all_iron_man_avatars()

        # Create Ultron if missing
        ultron = self.create_ultron_if_missing()
        if ultron and ultron not in avatars:
            avatars.append(ultron)

        logger.info(f"🎭 Displaying {len(avatars)} Iron Man avatars")

        # Calculate positions (grid layout)
        cols = 3
        spacing_x = 350
        spacing_y = 450
        start_x = 50
        start_y = 50

        for idx, avatar in enumerate(avatars):
            row = idx // cols
            col = idx % cols
            x = start_x + (col * spacing_x)
            y = start_y + (row * spacing_y)

            position = {"x": x, "y": y}

            # Create window
            window = IronManAvatarWindow(avatar, position)
            if window.create_window():
                self.avatar_windows[avatar.character_id] = window
                logger.info(f"   ✅ Displayed {avatar.name} ({avatar.character_id})")

        logger.info(f"✅ Displayed {len(self.avatar_windows)} Iron Man avatars")
        logger.info("   All avatars visible on screen")

        # Start main loop
        try:
            main_root.mainloop()
        except KeyboardInterrupt:
            logger.info("Stopping avatar display...")
            for window in self.avatar_windows.values():
                window.destroy()
            main_root.destroy()


def main():
    """Main entry point"""
    print("=" * 80)
    print("🦾 DISPLAYING ALL IRON MAN AVATARS")
    print("=" * 80)
    print()
    print("From JARVIS to the most sophisticated ULTIMATE/ULTRON Iron Man avatar")
    print()

    display = AllIronManAvatarsDisplay()

    print("Iron Man Avatars:")
    avatars = display.get_all_iron_man_avatars()

    # Create ULTRON.ai if missing (FINAL FORM)
    ultron = display.create_ultron_if_missing()
    if ultron:
        print(f"   ✅ ULTRON.ai (FINAL FORM - most sophisticated alternate JARVIS) - Created")

    for avatar in avatars:
        sophistication = "Most Sophisticated" if avatar.character_id == "ultron" else "Advanced"
        print(f"   ✅ {avatar.name} ({avatar.character_id}) - {sophistication}")
        print(f"      Style: {avatar.avatar_style}")
        print(f"      Template: {avatar.avatar_template}")
        print(f"      Colors: {avatar.primary_color} / {avatar.secondary_color}")
        print()

    print("=" * 80)
    print("🚀 DISPLAYING ALL AVATARS ON SCREEN")
    print("=" * 80)
    print()
    print("Opening avatar windows...")
    print("(Close windows to stop)")
    print()

    display.display_all_avatars()


if __name__ == "__main__":


    main()