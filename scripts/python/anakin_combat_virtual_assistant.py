#!/usr/bin/env python3
"""
Anakin/Vader Combat Virtual Assistant (ACVA) - Desktop GUI

Desktop companion VA for Anakin/Vader with lightsaber and combat abilities.
Similar to IMVA but with Star Wars theme and combat focus.

Tags: #ACVA #ANAKIN #VADER #COMBAT #LIGHTSABER #VIRTUAL_ASSISTANT @JARVIS @TEAM
"""

import sys
import time
import threading
import random
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
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
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from va_positioning_combat_system import VAPositioningCombatSystem

logger = get_logger("AnakinCombatVA")


class AnakinCombatVirtualAssistant:
    """
    Anakin/Vader Combat Virtual Assistant (ACVA)

    Desktop GUI companion with lightsaber and combat abilities.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ACVA"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available - cannot create ACVA")
            raise ImportError("tkinter is required for ACVA")

        # Window properties
        self.window_size = 120
        self.root = None
        self.canvas = None

        # Position
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0

        # Positioning system
        try:
            self.positioning_system = VAPositioningCombatSystem(project_root=self.project_root)
            logger.info("✅ VA Positioning System initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize positioning system: {e}")
            self.positioning_system = None

        # Initialize position
        if self.positioning_system:
            try:
                pos_x, pos_y = self.positioning_system.calculate_spaced_position("acva", self.window_size)
                self.x = pos_x
                self.y = pos_y
                logger.info(f"✅ Initialized position: ({self.x}, {self.y})")
            except Exception as e:
                logger.warning(f"⚠️  Could not use positioning system: {e}")
                import random
                screen_width = 1920
                screen_height = 1080
                self.x = screen_width // 2 + random.randint(-200, 200)
                self.y = screen_height // 2 + random.randint(-200, 200)
        else:
            import random
            screen_width = 1920
            screen_height = 1080
            self.x = screen_width // 2 + random.randint(-200, 200)
            self.y = screen_height // 2 + random.randint(-200, 200)

        self.target_x = self.x
        self.target_y = self.y

        # Animation
        self.animation_running = False
        self.lightsaber_active = False

        logger.info("✅ Anakin Combat Virtual Assistant initialized")

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON integration failed: {e}")

        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  R5 integration failed: {e}")

    def create_window(self):
        """Create ACVA window"""
        self.root = tk.Tk()
        self.root.title("Anakin/Vader Combat VA - LUMINA")
        self.root.attributes('-topmost', True)

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Position window
        initial_x = max(50, min(int(self.x), screen_width - self.window_size))
        initial_y = max(50, min(int(self.y), screen_height - self.window_size))
        self.root.geometry(f"{self.window_size}x{self.window_size}+{initial_x}+{initial_y}")

        # Transparent background
        self.root.configure(bg='black')
        self.root.overrideredirect(True)

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
            except ImportError:
                pass  # ctypes not available

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = SYPHONConfig = DataSourceType = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None

    def _draw_acva(self):
        """Draw Anakin/Vader figure"""
        if not self.canvas:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Draw simple Anakin/Vader figure (red/blue lightsaber)
        center_x = self.window_size // 2
        center_y = self.window_size // 2

        # Body (simple circle for now)
        body_size = 40
        self.canvas.create_oval(
            center_x - body_size // 2,
            center_y - body_size // 2,
            center_x + body_size // 2,
            center_y + body_size // 2,
            fill="#2C2C2C",  # Dark gray/black
            outline="#1A1A1A",
            width=2
        )

        # Lightsaber (blue for Anakin, red for Vader)
        if self.lightsaber_active:
            saber_color = "#00FFFF"  # Blue (Anakin)
            saber_length = 60
            saber_x = center_x + body_size // 2
            saber_y = center_y
            self.canvas.create_line(
                saber_x, saber_y,
                saber_x + saber_length, saber_y,
                fill=saber_color,
                width=4
            )
            # Glow effect
            self.canvas.create_line(
                saber_x, saber_y,
                saber_x + saber_length, saber_y,
                fill=saber_color,
                width=2
            )

    def _on_click(self, event):
        """Handle click"""
        self.lightsaber_active = not self.lightsaber_active
        self._draw_acva()

    def _on_drag(self, event):
        """Handle drag"""
        self.root.geometry(f"+{event.x_root - self.window_size // 2}+{event.y_root - self.window_size // 2}")

    def start_animation(self):
        """Start animation loop"""
        self.animation_running = True

        def animate():
            while self.animation_running and self.root:
                try:
                    # Toggle lightsaber occasionally
                    if random.random() < 0.1:
                        self.lightsaber_active = not self.lightsaber_active
                        self._draw_acva()

                    self.root.update()
                    time.sleep(0.1)
                except:
                    break

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def run(self):
        """Run ACVA"""
        try:
            self.create_window()
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("🛑 ACVA stopped")
        except Exception as e:
            logger.error(f"❌ ACVA error: {e}", exc_info=True)
        finally:
            self.animation_running = False


if __name__ == "__main__":
    assistant = AnakinCombatVirtualAssistant()
    assistant.run()
