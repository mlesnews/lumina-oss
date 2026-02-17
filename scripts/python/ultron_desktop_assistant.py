#!/usr/bin/env python3
"""
Ultron Desktop Assistant - ACE Style

Frameless, transparent desktop assistant that walks around like ACE.
No window frame, just the animated character on the desktop.

Tags: #ULTRON #DESKTOP_ASSISTANT #ACE_STYLE @LUMINA
"""

import sys
import time
import threading
import random
import math
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

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

logger = get_logger("UltronDesktop")


class UltronDesktopAssistant:
    """
    Ultron Desktop Assistant - ACE Style
    Frameless, transparent, draggable desktop companion
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Ultron Desktop Assistant"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available - cannot create Ultron Desktop Assistant")
            raise ImportError("tkinter is required")

        # Window properties - match ACE exactly
        self.window_size = 120
        self.root = None
        self.canvas = None

        # Position - start at random location
        screen_width = 1920
        screen_height = 1080
        self.x = random.randint(100, screen_width - 220)
        self.y = random.randint(100, screen_height - 220)

        # Animation
        self.animation_running = False
        self.eye_glow = 0.0
        self.eye_dir = 1
        self.core_pulse = 0.0

        # Ultron colors (red/orange - menacing)
        self.colors = {
            "primary": "#ff3333",  # Red
            "secondary": "#ff6600",  # Orange
            "glow": "#ff0000",  # Bright red
            "outline": "#ffffff"
        }

        # Register with Iron Man Assistant Manager (singleton pattern)
        self.manager = None
        try:
            from iron_man_assistant_manager import IronManAssistantManager
            self.manager = IronManAssistantManager(project_root=project_root)
            # Check if we can activate
            can_activate, reason = self.manager.can_activate("ultron")
            if not can_activate:
                logger.warning(f"⚠️  Cannot activate: {reason}")
                # Deactivate existing and activate this one
                if self.manager.get_active_assistant():
                    self.manager.deactivate()
        except ImportError:
            logger.debug("Iron Man Assistant Manager not available")
        except Exception as e:
            logger.debug(f"Manager error: {e}")

        logger.info("✅ Ultron Desktop Assistant initialized")

    def create_window(self):
        """Create frameless transparent window - exactly like ACE"""
        self.root = tk.Tk()
        self.root.title("Ultron Desktop Assistant")

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Update position
        self.x = max(50, min(int(self.x), screen_width - self.window_size - 50))
        self.y = max(50, min(int(self.y), screen_height - self.window_size - 50))

        # Position window
        self.root.geometry(f"{self.window_size}x{self.window_size}+{self.x}+{self.y}")

        # ACE-style window properties
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # No title bar
        self.root.attributes('-topmost', True)

        # Transparent background
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
            except Exception as e:
                self.root.attributes('-transparentcolor', 'black')
        else:
            self.root.attributes('-transparentcolor', 'black')

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.window_size,
            height=self.window_size,
            bg='black',
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack()

        # Activate with manager (requires magic words "Jarvis Iron Legion")
        if self.manager:
            import os
            # Check magic words before activating
            activated = self.manager.activate("ultron", os.getpid(), bypass_magic_words=False)
            if activated:
                logger.info("✅ Registered with Iron Man Assistant Manager")
            else:
                logger.warning("⚠️  Magic words not detected - assistant will not activate")
                logger.warning("   Say 'Jarvis Iron Legion' to activate")
                # Close window if magic words not detected
                self.root.quit()
                return

        # Bind drag events
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)

        # Draw Ultron
        self._draw_ultron()

        # Start animation
        self.start_animation()

        logger.info("✅ Ultron Desktop Assistant window created")

    def _draw_ultron(self):
        """Draw Ultron character"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        center_x = self.window_size // 2
        center_y = self.window_size // 2

        # Head (more angular/robotic)
        head_radius = 35
        self.canvas.create_oval(
            center_x - head_radius,
            center_y - head_radius - 10,
            center_x + head_radius,
            center_y + head_radius - 10,
            fill=self.colors["primary"],
            outline=self.colors["outline"],
            width=2
        )

        # Eyes (red, menacing)
        eye_y = center_y - 5
        eye_size = 10 + int(self.eye_glow * 4)
        eye_color = self.colors["glow"]

        # Left eye
        self.canvas.create_oval(
            center_x - 20 - eye_size // 2,
            eye_y - eye_size // 2,
            center_x - 20 + eye_size // 2,
            eye_y + eye_size // 2,
            fill=eye_color,
            outline="#ffffff",
            width=2
        )

        # Right eye
        self.canvas.create_oval(
            center_x + 20 - eye_size // 2,
            eye_y - eye_size // 2,
            center_x + 20 + eye_size // 2,
            eye_y + eye_size // 2,
            fill=eye_color,
            outline="#ffffff",
            width=2
        )

        # Core (chest - red pulsing)
        core_y = center_y + 25
        core_radius = 14 + int(self.core_pulse * 4)
        core_color = self.colors["glow"]

        self.canvas.create_oval(
            center_x - core_radius,
            core_y - core_radius // 2,
            center_x + core_radius,
            core_y + core_radius // 2,
            fill=core_color,
            outline="#ffffff",
            width=2
        )

        # Inner core
        inner_radius = core_radius // 2
        self.canvas.create_oval(
            center_x - inner_radius,
            core_y - inner_radius // 2,
            center_x + inner_radius,
            core_y + inner_radius // 2,
            fill="#ffffff",
            outline=core_color,
            width=1
        )

    def _on_click(self, event):
        """Handle click"""
        self.eye_glow = 1.0 if self.eye_glow < 0.5 else 0.0
        self._draw_ultron()

    def _on_drag(self, event):
        """Handle drag"""
        self.root.geometry(f"+{event.x_root - self.window_size // 2}+{event.y_root - self.window_size // 2}")

    def start_animation(self):
        """Start animation loop"""
        self.animation_running = True

        def animate():
            while self.animation_running and self.root:
                try:
                    # Animate eye glow
                    self.eye_glow += 0.15 * self.eye_dir
                    if self.eye_glow >= 1.0:
                        self.eye_glow = 1.0
                        self.eye_dir = -1
                    elif self.eye_glow <= 0.0:
                        self.eye_glow = 0.0
                        self.eye_dir = 1

                    # Animate core pulse
                    self.core_pulse = (math.sin(time.time() * 3) + 1) / 2

                    self._draw_ultron()
                    self.root.update()
                    time.sleep(0.05)
                except:
                    break

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def run(self):
        """Run Ultron Desktop Assistant"""
        try:
            self.create_window()
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("🛑 Ultron Desktop Assistant stopped")
        except Exception as e:
            logger.error(f"❌ Ultron Desktop Assistant error: {e}", exc_info=True)
        finally:
            self.animation_running = False


if __name__ == "__main__":
    assistant = UltronDesktopAssistant()
    assistant.run()
