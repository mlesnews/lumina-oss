#!/usr/bin/env python3
"""
Iron Man Animated Virtual Assistant - Like Armory Crate's ACE

Actually displays an animated Iron Man character on desktop, not just text menus.
Inspired by Armory Crate's ACE virtual assistant with Replika-style interaction.

Tags: #IRON_MAN #ANIMATED #CHARACTER #ACE #REPLIKA @JARVIS @LUMINA
"""

import sys
import time
import math
import random
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

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

logger = get_logger("IronManAnimatedVA")

# Try to import GUI libraries
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    tk = None

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None
    ImageTk = None


class IronManAnimatedVA:
    """
    Iron Man Animated Virtual Assistant

    Displays an actual animated Iron Man character on desktop,
    like Armory Crate's ACE assistant.
    """

    def __init__(self):
        """Initialize animated Iron Man VA"""
        if not TKINTER_AVAILABLE:
            raise ImportError("tkinter is required for animated VA")

        self.project_root = project_root
        self.logger = logger

        # Character appearance
        self.size = 80  # Character size
        self.ironman_colors = {
            "primary": "#FF6B35",  # Orange-red
            "secondary": "#FFD700",  # Gold
            "arc_reactor": "#00FFFF",  # Cyan (arc reactor)
            "powercord": "#808080"  # Gray
        }

        # Animation state
        self.arc_reactor_pulse = 0.0
        self.animation_speed = 0.1
        self.wandering = False
        self.position_x = 100.0
        self.position_y = 100.0
        self.target_x = 100.0
        self.target_y = 100.0
        self.speed = 2.0

        # Window
        self.root = None
        self.canvas = None
        self.window_size = 120

        # Threading
        self.running = False
        self.animation_thread = None
        self.wander_thread = None

        logger.info("=" * 80)
        logger.info("🦾 IRON MAN ANIMATED VIRTUAL ASSISTANT")
        logger.info("=" * 80)

    def create_window(self):
        """Create the animated character window"""
        self.root = tk.Tk()
        self.root.title("Iron Man Virtual Assistant")
        self.root.attributes('-topmost', True)

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Position in center initially
        initial_x = (screen_width - self.window_size) // 2
        initial_y = (screen_height - self.window_size) // 2

        self.root.geometry(f"{self.window_size}x{self.window_size}+{initial_x}+{initial_y}")
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # Frameless

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

        # Set transparency (Windows)
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = self.root.winfo_id()
                try:
                    parent_hwnd = ctypes.windll.user32.GetParent(hwnd)
                    if parent_hwnd:
                        hwnd = parent_hwnd
                except:
                    pass

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
                logger.warning(f"Transparency setup failed: {e}")
                try:
                    self.root.attributes('-transparentcolor', 'black')
                except:
                    pass

        # Bind drag
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)

        # Draw character
        self._draw_ironman()

        # Start animation
        self.running = True
        self.start_animation()
        self.start_wandering()

        logger.info("✅ Iron Man animated character window created")

    def _draw_ironman(self):
        """Draw animated Iron Man character"""
        if not self.canvas:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Center of window
        x, y = self.window_size // 2, self.window_size // 2
        size = self.size

        # Use PIL for high-quality rendering if available
        if PIL_AVAILABLE:
            self._draw_ironman_pil(x, y, size)
        else:
            self._draw_ironman_canvas(x, y, size)

    def _draw_ironman_pil(self, x: float, y: float, size: float):
        """Draw Iron Man using PIL for high quality"""
        try:
            # Create image with transparency
            img = Image.new('RGBA', (self.window_size, self.window_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Draw Iron Man body (simplified but recognizable)
            # Head
            head_radius = size * 0.25
            draw.ellipse(
                [x - head_radius, y - size * 0.4, x + head_radius, y - size * 0.1],
                fill=self.ironman_colors["primary"],
                outline=self.ironman_colors["secondary"],
                width=2
            )

            # Body (chest)
            body_width = size * 0.5
            body_height = size * 0.4
            draw.rectangle(
                [x - body_width/2, y - size * 0.1, x + body_width/2, y + size * 0.3],
                fill=self.ironman_colors["primary"],
                outline=self.ironman_colors["secondary"],
                width=2
            )

            # Arc Reactor (pulsing)
            arc_size = size * 0.15 * (1.0 + 0.3 * math.sin(self.arc_reactor_pulse))
            draw.ellipse(
                [x - arc_size/2, y + size * 0.05, x + arc_size/2, y + size * 0.2],
                fill=self.ironman_colors["arc_reactor"],
                outline=self.ironman_colors["secondary"]
            )

            # Arms
            arm_width = size * 0.15
            arm_length = size * 0.3
            # Left arm
            draw.rectangle(
                [x - body_width/2 - arm_width, y, x - body_width/2, y + arm_length],
                fill=self.ironman_colors["primary"],
                outline=self.ironman_colors["secondary"],
                width=2
            )
            # Right arm
            draw.rectangle(
                [x + body_width/2, y, x + body_width/2 + arm_width, y + arm_length],
                fill=self.ironman_colors["primary"],
                outline=self.ironman_colors["secondary"],
                width=2
            )

            # Legs
            leg_width = size * 0.12
            leg_length = size * 0.35
            # Left leg
            draw.rectangle(
                [x - body_width/4 - leg_width/2, y + size * 0.3, x - body_width/4 + leg_width/2, y + size * 0.65],
                fill=self.ironman_colors["primary"],
                outline=self.ironman_colors["secondary"],
                width=2
            )
            # Right leg
            draw.rectangle(
                [x + body_width/4 - leg_width/2, y + size * 0.3, x + body_width/4 + leg_width/2, y + size * 0.65],
                fill=self.ironman_colors["primary"],
                outline=self.ironman_colors["secondary"],
                width=2
            )

            # Convert to PhotoImage and display
            self.ironman_photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.ironman_photo, tags="ironman")

        except Exception as e:
            logger.error(f"Error drawing with PIL: {e}")
            self._draw_ironman_canvas(x, y, size)

    def _draw_ironman_canvas(self, x: float, y: float, size: float):
        """Draw Iron Man using canvas (fallback)"""
        # Head
        head_radius = size * 0.25
        self.canvas.create_oval(
            x - head_radius, y - size * 0.4,
            x + head_radius, y - size * 0.1,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman"
        )

        # Body
        body_width = size * 0.5
        self.canvas.create_rectangle(
            x - body_width/2, y - size * 0.1,
            x + body_width/2, y + size * 0.3,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman"
        )

        # Arc Reactor (pulsing)
        arc_size = size * 0.15 * (1.0 + 0.3 * math.sin(self.arc_reactor_pulse))
        self.canvas.create_oval(
            x - arc_size/2, y + size * 0.05,
            x + arc_size/2, y + size * 0.2,
            fill=self.ironman_colors["arc_reactor"],
            outline=self.ironman_colors["secondary"],
            tags="ironman"
        )

        # Arms and legs (simplified)
        # Left arm
        self.canvas.create_rectangle(
            x - body_width/2 - size * 0.15, y,
            x - body_width/2, y + size * 0.3,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman"
        )
        # Right arm
        self.canvas.create_rectangle(
            x + body_width/2, y,
            x + body_width/2 + size * 0.15, y + size * 0.3,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman"
        )

        # Legs
        leg_width = size * 0.12
        # Left leg
        self.canvas.create_rectangle(
            x - body_width/4 - leg_width/2, y + size * 0.3,
            x - body_width/4 + leg_width/2, y + size * 0.65,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman"
        )
        # Right leg
        self.canvas.create_rectangle(
            x + body_width/4 - leg_width/2, y + size * 0.3,
            x + body_width/4 + leg_width/2, y + size * 0.65,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman"
        )

    def _on_click(self, event):
        """Handle click on character"""
        self.logger.info("Iron Man VA clicked!")
        # Could open interaction menu here

    def _on_drag(self, event):
        """Handle dragging the character"""
        self.root.geometry(f"+{event.x_root - self.window_size//2}+{event.y_root - self.window_size//2}")

    def start_animation(self):
        """Start animation loop using root.after() (thread-safe)"""
        def animate():
            if not self.running:
                return
            # Pulse arc reactor
            self.arc_reactor_pulse += self.animation_speed
            if self.arc_reactor_pulse > 2 * math.pi:
                self.arc_reactor_pulse = 0.0
            # Redraw
            self._draw_ironman()
            self.root.after(50, animate)  # ~20 FPS

        animate()
        logger.info("✅ Animation started")

    def start_wandering(self):
        """Start wandering behavior using root.after() (thread-safe)"""
        self.wandering = True

        # Set initial target
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.position_x = float(self.root.winfo_x())
        self.position_y = float(self.root.winfo_y())
        self.target_x = random.uniform(0, screen_width - self.window_size)
        self.target_y = random.uniform(0, screen_height - self.window_size)

        def wander():
            if not self.running or not self.wandering:
                return
            dx = self.target_x - self.position_x
            dy = self.target_y - self.position_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 1.0:
                self.position_x += (dx / distance) * self.speed
                self.position_y += (dy / distance) * self.speed
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                new_x = max(0, min(int(self.position_x), screen_width - self.window_size))
                new_y = max(0, min(int(self.position_y), screen_height - self.window_size))
                self.root.geometry(f"+{new_x}+{new_y}")
            else:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.target_x = random.uniform(0, screen_width - self.window_size)
                self.target_y = random.uniform(0, screen_height - self.window_size)

            self.root.after(100, wander)

        wander()
        logger.info("✅ Wandering started")

    def run(self):
        """Run the animated VA"""
        self.create_window()
        logger.info("✅ Iron Man Animated VA running")
        self.root.mainloop()


def main():
    """Main function"""
    print("=" * 80)
    print("🦾 IRON MAN ANIMATED VIRTUAL ASSISTANT")
    print("=" * 80)
    print()
    print("Creating animated Iron Man character...")
    print("(Like Armory Crate's ACE assistant)")
    print()

    try:
        va = IronManAnimatedVA()
        va.run()
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)