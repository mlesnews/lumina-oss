#!/usr/bin/env python3
"""
Iron Man Armor: Mark V Desktop Assistant - The Suitcase Suit

The Mark V (also known as the "Suitcase Suit" or "Football") is Tony Stark's
fifth Iron Man suit, designed for portability and quick deployment. It's lighter,
has less armaments, but breaks down into a briefcase-sized bundle.

Inspired by: https://marvelcinematicuniverse.fandom.com/wiki/Iron_Man_Armor:_Mark_V

Tags: #MARK_V #SUITCASE_SUIT #PORTABLE #JARVIS #IRON_MAN @JARVIS @LUMINA
"""

import sys
import os
import time
import threading
import random
import math
from pathlib import Path
from typing import Optional, Dict, Any
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

logger = get_logger("MarkVAssistant")

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Iron Man Assistant Manager (singleton)
try:
    from iron_man_assistant_manager import IronManAssistantManager
    MANAGER_AVAILABLE = True
except ImportError:
    MANAGER_AVAILABLE = False
    IronManAssistantManager = None


class MarkVDesktopAssistant:
    """
    Iron Man Armor: Mark V Desktop Assistant - The Suitcase Suit

    Characteristics:
    - Portable and compact (briefcase-sized)
    - Red and gold classic Iron Man colors
    - Lighter design with less armaments
    - Quick deployment capability
    - Always ready for rapid response
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available")
            raise ImportError("tkinter required")

        if not PIL_AVAILABLE:
            logger.error("❌ PIL not available")
            raise ImportError("PIL required")

        # Register with manager (singleton pattern)
        self.manager = None
        if MANAGER_AVAILABLE:
            try:
                self.manager = IronManAssistantManager(project_root=project_root)
                # Check if we can activate
                can_activate, reason = self.manager.can_activate("mark_v")
                if not can_activate:
                    logger.warning(f"⚠️  Cannot activate: {reason}")
                    # Deactivate existing and activate this one
                    if self.manager.get_active_assistant():
                        self.manager.deactivate()
            except Exception as e:
                logger.warning(f"⚠️  Manager not available: {e}")

        # Window properties - slightly smaller for portability theme
        self.size = 100  # Compact size (smaller than Ultimate)
        self.root = None
        self.canvas = None

        # Position
        screen_width = 1920
        screen_height = 1080
        self.x = random.randint(100, screen_width - 220)
        self.y = random.randint(100, screen_height - 220)

        # Animation
        self.animation_running = False
        self.arc_reactor_pulse = 0.0
        self.briefcase_mode = False  # Toggle between briefcase and deployed
        self.transformation_progress = 0.0  # 0.0 = briefcase, 1.0 = fully deployed
        self.briefcase_open = False  # Whether briefcase is opening/opened
        self.suit_up_sequence = False  # Whether in suit-up animation

        # Mark V colors (vibrant red with silver/chrome accents)
        self.colors = {
            "primary": "#DC143C",  # Vibrant metallic red
            "secondary": "#C0C0C0",  # Silver/chrome
            "accent": "#FFD700",  # Gold accents
            "glow": "#FFFFFF",  # White glow (arc reactor)
            "outline": "#FFFFFF",  # White outline
            "mechanical": "#2F2F2F"  # Dark grey for mechanical parts
        }

        logger.info("✅ Iron Man Armor: Mark V Desktop Assistant initialized")
        logger.info("   'It's lighter, has less armaments, but breaks down into a smaller bundle the size of a briefcase.'")

    def create_window(self):
        """Create frameless transparent window"""
        self.root = tk.Tk()
        self.root.title("Iron Man Armor: Mark V - Suitcase Suit")

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Update position
        self.x = max(50, min(int(self.x), screen_width - self.size - 50))
        self.y = max(50, min(int(self.y), screen_height - self.size - 50))

        # Position window
        self.root.geometry(f"{self.size}x{self.size}+{self.x}+{self.y}")

        # Frameless, transparent, always on top
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        # Transparency (Windows)
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = self.root.winfo_id()
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x80000
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)

                LWA_COLORKEY = 0x1
                LWA_ALPHA = 0x2
                alpha_value = 255
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, alpha_value, LWA_COLORKEY | LWA_ALPHA)
            except Exception:
                self.root.attributes('-transparentcolor', 'black')
        else:
            self.root.attributes('-transparentcolor', 'black')

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.size,
            height=self.size,
            bg='black',
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack()

        # Bind drag events
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        # Double-click to toggle briefcase mode
        self.canvas.bind("<Double-Button-1>", self._toggle_briefcase_mode)

        # Activate with manager (requires magic words "Jarvis Iron Legion")
        if self.manager:
            # Check magic words before activating
            activated = self.manager.activate("mark_v", os.getpid(), bypass_magic_words=False)
            if activated:
                logger.info("✅ Registered with Iron Man Assistant Manager")
            else:
                logger.warning("⚠️  Magic words not detected - assistant will not activate")
                logger.warning("   Say 'Jarvis Iron Legion' to activate")
                # Close window if magic words not detected
                self.root.quit()
                return

    def _on_drag_start(self, event):
        """Start dragging"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        """Handle dragging"""
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.x += dx
        self.y += dy
        self.root.geometry(f"+{self.x}+{self.y}")

    def _toggle_briefcase_mode(self, event):
        """Toggle between briefcase and deployed mode"""
        self.briefcase_mode = not self.briefcase_mode
        logger.info(f"🔄 Toggled to {'briefcase' if self.briefcase_mode else 'deployed'} mode")

    def _draw_mark_v(self):
        """Draw Mark V armor with briefcase transformation capability"""
        self.canvas.delete("all")

        center_x = self.size / 2
        center_y = self.size / 2

        # 3x render scale for high quality
        scale = 3
        img_size = int(self.size * scale)
        img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Scale coordinates
        center_x_scaled = center_x * scale
        center_y_scaled = center_y * scale

        # Animate transformation with suit-up sequence
        if self.briefcase_mode:
            # Collapsing back to briefcase
            if self.transformation_progress > 0.3:
                self.briefcase_open = True
            self.transformation_progress = max(0.0, self.transformation_progress - 0.05)
            if self.transformation_progress < 0.3:
                self.briefcase_open = False
        else:
            # Suiting up - briefcase opens first, then armor deploys
            if self.transformation_progress < 0.2:
                self.briefcase_open = True  # Briefcase opening
                self.transformation_progress = min(0.2, self.transformation_progress + 0.08)
            elif self.transformation_progress < 0.3:
                # Briefcase fully open, armor starting to unfold
                self.briefcase_open = True
                self.transformation_progress = min(0.3, self.transformation_progress + 0.08)
            else:
                # Armor deploying
                self.transformation_progress = min(1.0, self.transformation_progress + 0.05)

        # Briefcase mode (collapsed, opening, or open with armor visible)
        if self.transformation_progress < 0.3:
            # Briefcase dimensions
            briefcase_width = int(40 * scale)
            briefcase_height = int(30 * scale)

            # Briefcase opening angle (0 = closed, 1 = fully open)
            open_progress = min(1.0, self.transformation_progress / 0.2) if self.briefcase_open else 0.0
            lid_angle = open_progress * 0.8  # Max 80% open

            # Briefcase base (bottom half)
            draw.rectangle(
                [center_x_scaled - briefcase_width // 2, center_y_scaled,
                 center_x_scaled + briefcase_width // 2, center_y_scaled + briefcase_height // 2],
                fill=(139, 69, 19, 255),  # Brown
                outline=(0, 0, 0, 255),
                width=int(2 * scale)
            )

            # Briefcase lid (top half - opens upward)
            lid_bottom = center_y_scaled
            lid_top = center_y_scaled - int(briefcase_height // 2 * (1 - lid_angle))
            draw.rectangle(
                [center_x_scaled - briefcase_width // 2, lid_top,
                 center_x_scaled + briefcase_width // 2, lid_bottom],
                fill=(139, 69, 19, 255),  # Brown
                outline=(0, 0, 0, 255),
                width=int(2 * scale)
            )

            # Briefcase handle (only visible when closed)
            if open_progress < 0.3:
                handle_width = int(20 * scale)
                handle_height = int(8 * scale)
                draw.rectangle(
                    [center_x_scaled - handle_width // 2, lid_top - handle_height,
                     center_x_scaled + handle_width // 2, lid_top],
                    fill=(101, 67, 33, 255),  # Dark brown
                    outline=(0, 0, 0, 255),
                    width=int(1 * scale)
                )

            # Briefcase latches (gold) - visible when closed
            if open_progress < 0.5:
                latch_size = int(4 * scale)
                latch_alpha = int(255 * (1 - open_progress * 2))
                draw.ellipse(
                    [center_x_scaled - briefcase_width // 2 - latch_size, center_y_scaled - latch_size,
                     center_x_scaled - briefcase_width // 2 + latch_size, center_y_scaled + latch_size],
                    fill=(255, 215, 0, latch_alpha)  # Gold
                )
                draw.ellipse(
                    [center_x_scaled + briefcase_width // 2 - latch_size, center_y_scaled - latch_size,
                     center_x_scaled + briefcase_width // 2 + latch_size, center_y_scaled + latch_size],
                    fill=(255, 215, 0, latch_alpha)  # Gold
                )

            # Show armor plates starting to emerge when briefcase opens
            if open_progress > 0.3 and self.transformation_progress > 0.15:
                # Initial armor pieces visible inside briefcase
                plate_alpha = int(150 * (self.transformation_progress - 0.15) / 0.15)
                # Small red plate visible
                plate_size = int(8 * scale * open_progress)
                draw.ellipse(
                    [center_x_scaled - plate_size, center_y_scaled - plate_size,
                     center_x_scaled + plate_size, center_y_scaled + plate_size],
                    fill=(220, 20, 60, plate_alpha),  # Red armor starting to show
                    outline=(192, 192, 192, plate_alpha),  # Silver outline
                    width=int(1 * scale)
                )

        # Deployed mode (armor) - suit-up sequence
        if self.transformation_progress > 0.3:
            deploy_factor = (self.transformation_progress - 0.3) / 0.7  # 0.0 to 1.0
            body_alpha = int(255 * deploy_factor)

            # Staggered deployment - different parts appear at different times for cinematic effect
            helmet_deploy = min(1.0, deploy_factor * 1.2)  # Helmet appears first
            torso_deploy = min(1.0, deploy_factor * 1.0)  # Torso deploys
            plates_deploy = max(0.0, min(1.0, (deploy_factor - 0.2) * 1.5))  # Plates lock in after
            details_deploy = max(0.0, min(1.0, (deploy_factor - 0.4) * 1.5))  # Details last

            # Mark V design (vibrant red with silver/chrome accents and segmented plates)

            # Helmet (red dome with silver faceplate) - deploys first
            helmet_radius = int(22 * scale * helmet_deploy)
            helmet_y = center_y_scaled - int(18 * scale * helmet_deploy)
            helmet_alpha = int(255 * helmet_deploy)

            # Helmet dome (red) - appears first in suit-up
            if helmet_deploy > 0.1:
                draw.ellipse(
                    [center_x_scaled - helmet_radius, helmet_y - helmet_radius,
                     center_x_scaled + helmet_radius, helmet_y + helmet_radius],
                    fill=(220, 20, 60, helmet_alpha),  # Vibrant red
                    outline=(255, 255, 255, helmet_alpha),  # White outline
                    width=int(2 * scale)
                )

            # Silver faceplate (with white eye slits) - appears after helmet
            if helmet_deploy > 0.3:
                faceplate_y = helmet_y + int(3 * scale * helmet_deploy)
                faceplate_width = int(16 * scale * helmet_deploy)
                faceplate_height = int(10 * scale * helmet_deploy)
                draw.ellipse(
                    [center_x_scaled - faceplate_width // 2, faceplate_y - faceplate_height // 2,
                     center_x_scaled + faceplate_width // 2, faceplate_y + faceplate_height // 2],
                    fill=(192, 192, 192, int(220 * helmet_deploy))  # Silver/chrome
                )

                # White eye slits - light up when faceplate is in place
                if helmet_deploy > 0.5:
                    eye_y = faceplate_y
                    eye_width = int(12 * scale * helmet_deploy)
                    eye_height = int(3 * scale * helmet_deploy)
                    eye_glow = int(200 * helmet_deploy) + int(55 * math.sin(self.arc_reactor_pulse * 2))
                    draw.rectangle(
                        [center_x_scaled - eye_width // 2, eye_y - eye_height // 2,
                         center_x_scaled + eye_width // 2, eye_y + eye_height // 2],
                        fill=(255, 255, 255, min(255, eye_glow))  # White eyes with subtle pulse
                    )

            # Body (red torso with segmented silver plates) - deploys after helmet
            body_radius = int(28 * scale * torso_deploy)
            torso_alpha = int(255 * torso_deploy)

            # Main torso (red) - unfolds from briefcase
            if torso_deploy > 0.1:
                draw.ellipse(
                    [center_x_scaled - body_radius, center_y_scaled - body_radius,
                     center_x_scaled + body_radius, center_y_scaled + body_radius],
                    fill=(220, 20, 60, torso_alpha),  # Vibrant red
                    outline=(255, 255, 255, torso_alpha),  # White outline
                    width=int(2 * scale)
                )

            # Segmented silver plates (abdominal section - interlocking plates)
            # Plates lock into place sequentially for cinematic effect
            if plates_deploy > 0.1:
                plate_y = center_y_scaled + int(5 * scale)
                plate_width = int(14 * scale)
                plate_height = int(3 * scale)
                plate_alpha = int(200 * plates_deploy)

                # Top plate - locks in first
                top_plate_alpha = int(200 * min(1.0, plates_deploy * 1.5))
                draw.rectangle(
                    [center_x_scaled - plate_width // 2, plate_y - plate_height,
                     center_x_scaled + plate_width // 2, plate_y],
                    fill=(192, 192, 192, top_plate_alpha),  # Silver
                    outline=(255, 255, 255, int(150 * plates_deploy)),
                    width=int(1 * scale)
                )

                # Middle plate - locks in second
                if plates_deploy > 0.3:
                    middle_plate_alpha = int(200 * min(1.0, (plates_deploy - 0.2) * 1.5))
                    draw.rectangle(
                        [center_x_scaled - plate_width // 2, plate_y,
                         center_x_scaled + plate_width // 2, plate_y + plate_height],
                        fill=(192, 192, 192, middle_plate_alpha),  # Silver
                        outline=(255, 255, 255, int(150 * plates_deploy)),
                        width=int(1 * scale)
                    )

                # Bottom plate - locks in last
                if plates_deploy > 0.5:
                    bottom_plate_alpha = int(200 * min(1.0, (plates_deploy - 0.4) * 1.5))
                    draw.rectangle(
                        [center_x_scaled - plate_width // 2, plate_y + plate_height,
                         center_x_scaled + plate_width // 2, plate_y + plate_height * 2],
                        fill=(192, 192, 192, bottom_plate_alpha),  # Silver
                        outline=(255, 255, 255, int(150 * plates_deploy)),
                        width=int(1 * scale)
                    )

            # Arc Reactor (glowing white - as per image description)
            # Powers up after torso is deployed
            reactor_deploy = max(0.0, min(1.0, (torso_deploy - 0.3) * 2.0))
            reactor_radius = int(7 * scale * reactor_deploy)
            pulse_factor = 1.0 + 0.2 * math.sin(self.arc_reactor_pulse)
            reactor_radius_pulsed = int(reactor_radius * pulse_factor)

            # Arc Reactor powers up - only visible when torso is deployed
            if reactor_deploy > 0.1:
                # Outer glow (white) - intensifies as reactor powers up
                glow_alpha = int(120 * reactor_deploy)
                draw.ellipse(
                    [center_x_scaled - reactor_radius_pulsed - 3, center_y_scaled - reactor_radius_pulsed - 3,
                     center_x_scaled + reactor_radius_pulsed + 3, center_y_scaled + reactor_radius_pulsed + 3],
                    fill=(255, 255, 255, glow_alpha)  # White glow
                )

                # Main reactor (white) - brightens up
                reactor_alpha = int(255 * reactor_deploy)
                draw.ellipse(
                    [center_x_scaled - reactor_radius_pulsed, center_y_scaled - reactor_radius_pulsed,
                     center_x_scaled + reactor_radius_pulsed, center_y_scaled + reactor_radius_pulsed],
                    fill=(255, 255, 255, reactor_alpha)  # White
                )

                # Center core (bright white) - powers up last
                if reactor_deploy > 0.5:
                    core_radius = int(3 * scale * reactor_deploy)
                    core_alpha = int(255 * reactor_deploy)
                    draw.ellipse(
                        [center_x_scaled - core_radius, center_y_scaled - core_radius,
                         center_x_scaled + core_radius, center_y_scaled + core_radius],
                        fill=(255, 255, 255, core_alpha)  # Bright white center
                    )

            # Silver/chrome accents on shoulders and joints - final details lock in
            if details_deploy > 0.1:
                detail_alpha = int(180 * details_deploy)
                # Shoulder accents - lock in place
                shoulder_y = center_y_scaled - int(5 * scale)
                shoulder_size = int(6 * scale * details_deploy)
                draw.ellipse(
                    [center_x_scaled - int(18 * scale) - shoulder_size, shoulder_y - shoulder_size,
                     center_x_scaled - int(18 * scale) + shoulder_size, shoulder_y + shoulder_size],
                    fill=(192, 192, 192, detail_alpha)  # Silver
                )
                draw.ellipse(
                    [center_x_scaled + int(18 * scale) - shoulder_size, shoulder_y - shoulder_size,
                     center_x_scaled + int(18 * scale) + shoulder_size, shoulder_y + shoulder_size],
                    fill=(192, 192, 192, detail_alpha)  # Silver
                )

                # Joint details (dark grey mechanical parts) - final articulation
                if details_deploy > 0.3:
                    joint_size = int(4 * scale * details_deploy)
                    joint_y = center_y_scaled + int(15 * scale)
                    joint_alpha = int(200 * details_deploy)
                    draw.ellipse(
                        [center_x_scaled - int(12 * scale) - joint_size, joint_y - joint_size,
                         center_x_scaled - int(12 * scale) + joint_size, joint_y + joint_size],
                        fill=(47, 47, 47, joint_alpha)  # Dark grey
                    )
                    draw.ellipse(
                        [center_x_scaled + int(12 * scale) - joint_size, joint_y - joint_size,
                         center_x_scaled + int(12 * scale) + joint_size, joint_y + joint_size],
                        fill=(47, 47, 47, joint_alpha)  # Dark grey
                    )

        # Downsample with LANCZOS (high quality)
        img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_final)

        # Draw on canvas
        self.canvas.create_image(center_x, center_y, image=photo, anchor="center")
        self.canvas.image = photo  # Keep reference

    def _animate(self):
        """Animation loop"""
        while self.animation_running:
            # Update arc reactor pulse
            self.arc_reactor_pulse += 0.1
            if self.arc_reactor_pulse > 2 * math.pi:
                self.arc_reactor_pulse = 0.0

            # Redraw
            self._draw_mark_v()

            time.sleep(0.05)  # ~20 FPS

    def start(self):
        """Start the assistant"""
        self.create_window()
        self.animation_running = True

        # Start animation thread
        animation_thread = threading.Thread(target=self._animate, daemon=True)
        animation_thread.start()

        logger.info("✅ Iron Man Armor: Mark V started")
        logger.info("   Double-click to toggle between briefcase and deployed mode")
        logger.info("   Watch the cinematic suit-up sequence: briefcase opens → armor unfolds → plates lock in place")

        # Run main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the assistant"""
        self.animation_running = False
        if self.manager:
            self.manager.deactivate()
        if self.root:
            self.root.quit()
        logger.info("⏹️  Iron Man Armor: Mark V stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Iron Man Armor: Mark V Desktop Assistant - The Suitcase Suit"
    )
    parser.add_argument(
        '--briefcase',
        action='store_true',
        help='Start in briefcase mode'
    )
    args = parser.parse_args()

    try:
        assistant = MarkVDesktopAssistant()
        if args.briefcase:
            assistant.briefcase_mode = True
            assistant.transformation_progress = 0.0
        assistant.start()
    except KeyboardInterrupt:
        logger.info("⏹️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


if __name__ == "__main__":


    main()