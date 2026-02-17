#!/usr/bin/env python3
"""
JARVIS Desktop Assistant - ACE Style

Frameless, transparent desktop assistant that walks around like ACE.
No window frame, just the animated character on the desktop.

Tags: #JARVIS #DESKTOP_ASSISTANT #ACE_STYLE @LUMINA
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

logger = get_logger("JARVISDesktop")


class JARVISDesktopAssistant:
    """
    JARVIS Desktop Assistant - ACE Style
    Frameless, transparent, draggable desktop companion
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Desktop Assistant"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available - cannot create JARVIS Desktop Assistant")
            raise ImportError("tkinter is required")

        # Window properties - match ACE exactly
        self.window_size = 120
        self.root = None
        self.canvas = None

        # Position - start at random location
        screen_width = 1920  # Will be updated from actual screen
        screen_height = 1080
        self.x = random.randint(100, screen_width - 220)
        self.y = random.randint(100, screen_height - 220)

        # Animation
        self.animation_running = False
        self.eye_glow = 0.0
        self.eye_dir = 1
        self.arc_reactor_pulse = 0.0

        # JARVIS colors (Iron Man blue/cyan)
        self.colors = {
            "primary": "#00ccff",  # JARVIS blue
            "secondary": "#006699",
            "glow": "#00ffff",
            "outline": "#ffffff"
        }

        # Register with Iron Man Assistant Manager (singleton pattern)
        self.manager = None
        try:
            from iron_man_assistant_manager import IronManAssistantManager
            self.manager = IronManAssistantManager(project_root=project_root)
            # Check if we can activate
            can_activate, reason = self.manager.can_activate("jarvis")
            if not can_activate:
                logger.warning(f"⚠️  Cannot activate: {reason}")
                # Deactivate existing and activate this one
                if self.manager.get_active_assistant():
                    self.manager.deactivate()
        except ImportError:
            logger.debug("Iron Man Assistant Manager not available")
        except Exception as e:
            logger.debug(f"Manager error: {e}")

        logger.info("✅ JARVIS Desktop Assistant initialized")

    def create_window(self):
        """Create frameless transparent window - exactly like ACE"""
        self.root = tk.Tk()
        self.root.title("JARVIS Desktop Assistant")

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Update position to be within screen bounds
        self.x = max(50, min(int(self.x), screen_width - self.window_size - 50))
        self.y = max(50, min(int(self.y), screen_height - self.window_size - 50))

        # Position window
        self.root.geometry(f"{self.window_size}x{self.window_size}+{self.x}+{self.y}")

        # ACE-style window properties
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # No title bar - frameless
        self.root.attributes('-topmost', True)  # Always on top

        # Transparent background (Windows)
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
                logger.info("✅ Transparency enabled")
            except Exception as e:
                logger.warning(f"⚠️  Transparency setup failed: {e}")
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
            activated = self.manager.activate("jarvis", os.getpid(), bypass_magic_words=False)
            if activated:
                logger.info("✅ Registered with Iron Man Assistant Manager")
            else:
                logger.warning("⚠️  Magic words not detected - assistant will not activate")
                logger.warning("   Say 'Jarvis Iron Legion' to activate")
                # Close window if magic words not detected
                self.root.quit()
                return

        # Bind drag events (like ACE)
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)

        # Draw JARVIS
        self._draw_jarvis()

        # Start animation
        self.start_animation()

        logger.info("✅ JARVIS Desktop Assistant window created")

    def _draw_jarvis(self):
        """Draw JARVIS Iron Man character"""
        if not self.canvas:
            return

        # Clear canvas
        self.canvas.delete("all")

        center_x = self.window_size // 2
        center_y = self.window_size // 2

        # Helmet/Head (circular)
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

        # Eyes (glowing)
        eye_y = center_y - 5
        eye_size = 8 + int(self.eye_glow * 3)
        eye_color = self.colors["glow"] if self.eye_glow > 0.5 else self.colors["primary"]

        # Left eye
        self.canvas.create_oval(
            center_x - 20 - eye_size // 2,
            eye_y - eye_size // 2,
            center_x - 20 + eye_size // 2,
            eye_y + eye_size // 2,
            fill=eye_color,
            outline=self.colors["outline"],
            width=1
        )

        # Right eye
        self.canvas.create_oval(
            center_x + 20 - eye_size // 2,
            eye_y - eye_size // 2,
            center_x + 20 + eye_size // 2,
            eye_y + eye_size // 2,
            fill=eye_color,
            outline=self.colors["outline"],
            width=1
        )

        # Arc Reactor (chest)
        reactor_y = center_y + 25
        reactor_radius = 12 + int(self.arc_reactor_pulse * 3)
        reactor_color = self.colors["glow"] if self.arc_reactor_pulse > 0.5 else self.colors["primary"]

        self.canvas.create_oval(
            center_x - reactor_radius,
            reactor_y - reactor_radius // 2,
            center_x + reactor_radius,
            reactor_y + reactor_radius // 2,
            fill=reactor_color,
            outline=self.colors["outline"],
            width=2
        )

        # Inner reactor core
        inner_radius = reactor_radius // 2
        self.canvas.create_oval(
            center_x - inner_radius,
            reactor_y - inner_radius // 2,
            center_x + inner_radius,
            reactor_y + inner_radius // 2,
            fill="#ffffff",
            outline=reactor_color,
            width=1
        )

    def _on_click(self, event):
        """Handle click - toggle eye glow"""
        self.eye_glow = 1.0 if self.eye_glow < 0.5 else 0.0
        self._draw_jarvis()

    def _on_drag(self, event):
        """Handle drag - move window"""
        self.root.geometry(f"+{event.x_root - self.window_size // 2}+{event.y_root - self.window_size // 2}")

    def start_animation(self):
        """Start animation loop"""
        self.animation_running = True

        def animate():
            while self.animation_running and self.root:
                try:
                    # Animate eye glow
                    self.eye_glow += 0.1 * self.eye_dir
                    if self.eye_glow >= 1.0:
                        self.eye_glow = 1.0
                        self.eye_dir = -1
                    elif self.eye_glow <= 0.0:
                        self.eye_glow = 0.0
                        self.eye_dir = 1

                    # Animate arc reactor pulse
                    self.arc_reactor_pulse = (math.sin(time.time() * 2) + 1) / 2

                    # Redraw
                    self._draw_jarvis()
                    self.root.update()
                    time.sleep(0.05)
                except:
                    break

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def run(self):
        """Run JARVIS Desktop Assistant"""
        try:
            self.create_window()
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("🛑 JARVIS Desktop Assistant stopped")
        except Exception as e:
            logger.error(f"❌ JARVIS Desktop Assistant error: {e}", exc_info=True)
        finally:
            self.animation_running = False


if __name__ == "__main__":
    assistant = JARVISDesktopAssistant()
    assistant.run()
