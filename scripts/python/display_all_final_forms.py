#!/usr/bin/env python3
"""
Display All Avatar Final Forms

Shows all avatars in their final forms with appropriate power levels.
Each avatar has a complete evolution spectrum: Base -> Intermediate -> Final Form.

Tags: #AVATAR #FINAL_FORM #POWER_LEVELS #EVOLUTION #SPECTRUM @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("DisplayAllFinalForms")

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    logger.error("tkinter not available")

try:
    from avatar_final_forms_system import (
        AvatarFinalFormsRegistry,
        AvatarForm,
        PowerLevel,
        FormType
    )
    from character_avatar_registry import CharacterAvatarRegistry
    FINAL_FORMS_AVAILABLE = True
except ImportError:
    FINAL_FORMS_AVAILABLE = False
    logger.warning("Final forms system not available")


class FinalFormWindow:
    """Window for displaying an absolute form avatar (Level 10)"""

    def __init__(self, form: AvatarForm, position: Dict[str, int]):
        self.form = form
        self.position = position
        self.root = None
        self.canvas = None

        if TKINTER_AVAILABLE:
            try:
                from iron_man_humanoid_system import (
                    IronManHumanoidRenderer,
                    IronManActionPhaseManager,
                    IronManActionPhase
                )

                persona_colors = {
                    "primary": form.primary_color,
                    "secondary": form.secondary_color,
                    "glow": "#ff3300",
                    "outline": "#ffffff",
                    "energy": "#ffff00"
                }

                self.humanoid_renderer = IronManHumanoidRenderer(persona_colors)
                self.action_manager = IronManActionPhaseManager()
                self.action_manager.random_actions_enabled = True
                self.action_manager.current_phase = self.action_manager.get_random_action_phase()
                self.action_manager.phase_duration = 3.0
            except Exception as e:
                logger.warning(f"Could not initialize renderer: {e}")
                self.humanoid_renderer = None
                self.action_manager = None

    def create_window(self):
        """Create final form window"""
        if not TKINTER_AVAILABLE:
            return False

        self.root = tk.Toplevel()
        self.root.title(f"{self.form.form_name} - Final Form")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        # Size based on power level (Extended to Level 10)
        power_scale = {
            PowerLevel.BASE: (200, 300),
            PowerLevel.INTERMEDIATE: (250, 300),
            PowerLevel.ADVANCED: (280, 380),
            PowerLevel.ENLIGHTENED: (300, 400),
            PowerLevel.ULTIMATE: (320, 420),
            PowerLevel.FINAL_FORM: (350, 450),
            PowerLevel.TRANSCENDENT: (400, 500),
            PowerLevel.COSMIC: (450, 550),
            PowerLevel.DIVINE: (500, 600),
            PowerLevel.ABSOLUTE: (550, 650)  # Maximum size
        }

        width, height = power_scale.get(self.form.power_level, (300, 400))

        x = self.position.get("x", 100)
        y = self.position.get("y", 100)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_form()
        self.animate()

        return True

    def draw_form(self):
        """Draw final form"""
        if not self.canvas:
            return

        self.canvas.delete("all")
        self.canvas.delete("final_form")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = width / 2
        cy = height / 2

        if self.humanoid_renderer and self.action_manager:
            self.action_manager.update(0.033)

            pose = self.action_manager.get_pose_for_phase(
                self.action_manager.current_phase,
                self.action_manager.animation_frame
            )

            self.humanoid_renderer.draw_humanoid(
                canvas=self.canvas,
                cx=cx,
                cy=cy,
                scale=self.form.scale,
                pose=pose,
                combat_mode=True,
                detail_level="high"
            )

        # Form name
        self.canvas.create_text(
            cx, height - 50,
            text=self.form.form_name,
            fill=self.form.primary_color,
            font=("Arial", 14, "bold"),
            tags="final_form"
        )

        # Power level
        power_text = f"Power Level: {self.form.power_level.name} ({self.form.power_level.value})"
        self.canvas.create_text(
            cx, height - 30,
            text=power_text,
            fill="#00ffff",
            font=("Arial", 10),
            tags="final_form"
        )

        # Catchphrase
        if self.form.catchphrase:
            self.canvas.create_text(
                cx, height - 10,
                text=self.form.catchphrase,
                fill="#00ffff",
                font=("Arial", 8),
                tags="final_form"
            )

    def animate(self):
        """Animation loop"""
        if not self.root or not self.canvas:
            return
        self.draw_form()
        self.root.after(33, self.animate)

    def destroy(self):
        """Close window"""
        if self.root:
            self.root.destroy()


class AllFinalFormsDisplay:
    """Display all avatar absolute forms (Level 10 - Maximum)"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.final_forms_registry = AvatarFinalFormsRegistry(project_root=project_root)
        self.windows: Dict[str, FinalFormWindow] = {}

    def display_all_final_forms(self):
        """Display all final forms"""
        if not TKINTER_AVAILABLE:
            logger.error("tkinter not available")
            return

        main_root = tk.Tk()
        main_root.withdraw()

        final_forms = self.final_forms_registry.get_all_final_forms()

        logger.info(f"🎭 Displaying {len(final_forms)} final forms")

        # Grid layout
        cols = 3
        spacing_x = 400
        spacing_y = 500
        start_x = 50
        start_y = 50

        for idx, form in enumerate(final_forms):
            row = idx // cols
            col = idx % cols
            x = start_x + (col * spacing_x)
            y = start_y + (row * spacing_y)

            position = {"x": x, "y": y}

            window = FinalFormWindow(form, position)
            if window.create_window():
                self.windows[form.form_id] = window
                logger.info(f"   ✅ Displayed {form.form_name} (Power Level {form.power_level.value})")

        logger.info(f"✅ Displayed {len(self.windows)} absolute forms (Level 10 - Maximum)")

        try:
            main_root.mainloop()
        except KeyboardInterrupt:
            logger.info("Stopping...")
            for window in self.windows.values():
                window.destroy()
            main_root.destroy()

    def list_all_spectra(self):
        """List all evolution spectra"""
        print("=" * 80)
        print("🌟 ALL AVATAR EVOLUTION SPECTRA")
        print("=" * 80)
        print()

        for char_id, spectrum in self.final_forms_registry.spectra.items():
            print(f"📊 {spectrum.base_character_name} ({char_id})")
            print(f"   Evolution Path:")

            for form in spectrum.forms:
                power_icon = "⭐" * form.power_level.value
                form_type_icon = "🔥" if form.form_type == FormType.FINAL_FORM else "→"
                print(f"   {form_type_icon} {form.form_name}")
                print(f"      Power Level: {form.power_level.name} ({form.power_level.value})")
                print(f"      Scale: {form.scale}x")
                print(f"      Type: {form.form_type.value}")
                if form.special_abilities:
                    print(f"      Abilities: {', '.join(form.special_abilities)}")
                print()

            final_form = spectrum.get_final_form()
            if final_form:
                max_icon = "⭐ MAXIMUM" if final_form.power_level == PowerLevel.ABSOLUTE else "⭐"
                print(f"   {max_icon} ABSOLUTE FORM: {final_form.form_name}")
                print(f"      Power Level: {final_form.power_level.name} ({final_form.power_level.value})")
                print(f"      Scale: {final_form.scale}x")
                if final_form.power_level == PowerLevel.ABSOLUTE:
                    print(f"      Status: MAXIMUM POWER - The Ultimate Endpoint")
                print()

            print()


def main():
    """Main entry point"""
    print("=" * 80)
    print("🌟 DISPLAYING ALL AVATAR ABSOLUTE FORMS (Level 10 - Maximum)")
    print("=" * 80)
    print()
    print("Each avatar has a complete evolution spectrum (Levels 1-10) with appropriate power levels")
    print("Showing Absolute forms (Level 10 - Maximum Power)")
    print()

    display = AllFinalFormsDisplay()

    # List all spectra
    display.list_all_spectra()

    print("=" * 80)
    print("🚀 DISPLAYING ALL ABSOLUTE FORMS ON SCREEN (Level 10)")
    print("=" * 80)
    print()
    print("Opening absolute form windows (Level 10 - Maximum Power)...")
    print("(Close windows to stop)")
    print()

    display.display_all_final_forms()


if __name__ == "__main__":


    main()