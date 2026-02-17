#!/usr/bin/env python3
"""
Ultimate Iron Man Desktop Assistant - High Fidelity (Kenny Approach)

High-quality animated desktop assistant using Kenny's 3x render scale
and component-based design. Matches Kenny's visual fidelity.

Tags: #ULTIMATE_IRON_MAN #HIGH_FIDELITY #KENNY_APPROACH @JARVIS @LUMINA
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

logger = get_logger("UltimateIronManHQ")

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


class UltimateIronManDesktopAssistant:
    """
    Ultimate Iron Man Desktop Assistant - High Fidelity

    Uses Kenny's approach:
    - 3x render scale for high quality
    - Component-based design
    - LANCZOS downsampling
    - High visual fidelity
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
                can_activate, reason = self.manager.can_activate("ultimate")
                if not can_activate:
                    logger.warning(f"⚠️  Cannot activate: {reason}")
                    # Deactivate existing and activate this one
                    if self.manager.get_active_assistant():
                        self.manager.deactivate()
            except Exception as e:
                logger.warning(f"⚠️  Manager not available: {e}")

        # Window properties
        self.size = 120  # Match Kenny/Ace window size
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

        # Ultimate Iron Man colors (silver/platinum with blue accents)
        self.colors = {
            "primary": "#C0C0C0",  # Silver
            "secondary": "#808080",  # Gray
            "accent": "#00D9FF",  # Cyan blue
            "glow": "#FFFFFF"  # White glow
        }

        logger.info("✅ Ultimate Iron Man Desktop Assistant initialized (High Fidelity)")

    def create_window(self):
        """Create frameless transparent window"""
        self.root = tk.Tk()
        self.root.title("Ultimate Iron Man")

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

        # Activate with manager (requires magic words "Jarvis Iron Legion")
        if self.manager:
            # Check magic words before activating
            activated = self.manager.activate("ultimate", os.getpid(), bypass_magic_words=False)
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

    def _draw_ultimate_iron_man(self):
        """Draw Ultimate Iron Man with 3x render scale (Kenny approach)"""
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

        # Ultimate Iron Man design (silver/platinum with blue accents)
        # Body (silver torso)
        body_radius = int(30 * scale)
        draw.ellipse(
            [center_x_scaled - body_radius, center_y_scaled - body_radius,
             center_x_scaled + body_radius, center_y_scaled + body_radius],
            fill=(192, 192, 192, 255),  # Silver
            outline=(255, 255, 255, 255),  # White outline
            width=int(2 * scale)
        )

        # Helmet (geometric, angular - Ultimate Iron Man style)
        helmet_radius = int(25 * scale)
        helmet_y = center_y_scaled - int(20 * scale)  # Above body

        # Draw hexagonal helmet (geometric)
        num_sides = 6
        hex_points = []
        for i in range(num_sides):
            angle = (2 * math.pi * i) / num_sides - math.pi / 2
            px = center_x_scaled + helmet_radius * math.cos(angle)
            py = helmet_y + helmet_radius * math.sin(angle)
            hex_points.append((px, py))

        draw.polygon(hex_points, fill=(192, 192, 192, 255), outline=(0, 217, 255, 255))  # Silver with cyan outline

        # HUD (inside helmet)
        hud_size = int(15 * scale)
        draw.rectangle(
            [center_x_scaled - hud_size, helmet_y - hud_size,
             center_x_scaled + hud_size, helmet_y + hud_size],
            fill=(0, 0, 0, 255)
        )

        # Face (inside HUD)
        face_radius = int(6 * scale)
        draw.ellipse(
            [center_x_scaled - face_radius, helmet_y - face_radius,
             center_x_scaled + face_radius, helmet_y + face_radius],
            fill=(0, 0, 0, 255)  # Solid black
        )

        # Arc Reactor (pulsing cyan)
        reactor_radius = int(8 * scale)
        pulse_factor = 1.0 + 0.2 * math.sin(self.arc_reactor_pulse)
        reactor_radius_pulsed = int(reactor_radius * pulse_factor)

        # Outer glow
        draw.ellipse(
            [center_x_scaled - reactor_radius_pulsed - 2, center_y_scaled - reactor_radius_pulsed - 2,
             center_x_scaled + reactor_radius_pulsed + 2, center_y_scaled + reactor_radius_pulsed + 2],
            fill=(0, 217, 255, 100)  # Cyan glow
        )

        # Main reactor
        draw.ellipse(
            [center_x_scaled - reactor_radius_pulsed, center_y_scaled - reactor_radius_pulsed,
             center_x_scaled + reactor_radius_pulsed, center_y_scaled + reactor_radius_pulsed],
            fill=(0, 217, 255, 255)  # Cyan
        )

        # Center core
        core_radius = int(3 * scale)
        draw.ellipse(
            [center_x_scaled - core_radius, center_y_scaled - core_radius,
             center_x_scaled + core_radius, center_y_scaled + core_radius],
            fill=(255, 255, 255, 255)  # White center
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
            self._draw_ultimate_iron_man()

            time.sleep(0.05)  # ~20 FPS

    def start(self):
        """Start the assistant"""
        self.create_window()
        self.animation_running = True

        # Start animation thread
        animation_thread = threading.Thread(target=self._animate, daemon=True)
        animation_thread.start()

        logger.info("✅ Ultimate Iron Man started (High Fidelity)")

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
        logger.info("⏹️  Ultimate Iron Man stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Ultimate Iron Man Desktop Assistant (High Fidelity)")
    args = parser.parse_args()

    try:
        assistant = UltimateIronManDesktopAssistant()
        assistant.start()
    except KeyboardInterrupt:
        logger.info("⏹️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


if __name__ == "__main__":


    main()