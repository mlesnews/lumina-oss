#!/usr/bin/env python3
"""
Kenny (@IMVA) - Comic-Accurate JARVIS Avatar
Restored with comic-accurate JARVIS visual design + smooth holographic behavior.
"""""
import sys
import json
import time
import threading
import random
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

try:
    from PIL import Image, ImageDraw, ImageTk, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import tkinter as tk
from tkinter import ttk

# Global Logger
try:
    from lumina_logger import get_logger
    logger = get_logger("StarkCore")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("StarkCore")

class KennyState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    WORKING = "working"
    SLEEPING = "sleeping"
    GAMING = "gaming"
    TRANSFORMING = "transforming"
    NOTIFYING = "notifying"

class KennyIMVAEnhanced:
    def __init__(self, size=120, scale=2.0):
        self.size = size
        self.size_scale = scale
        self.state = KennyState.IDLE
        self.animation_frame = 0
        self.root = None
        self.canvas = None
        self.x, self.y = 100, 100
        self.target_x, self.target_y = 100, 100
        # SLOWER MOVEMENT: Reduced from 0.05 to 0.015 for calmer, more elegant movement
        self.interpolation_factor = 0.015
        # SLOWER ANIMATION: Increased dwell time between position changes (frames)
        self.position_change_interval = 300  # Changed from 100 to 300 frames
        # SLOWER FRAME RATE: Animation update interval in ms (changed from 30 to 60)
        self.animation_interval_ms = 60  # ~17 FPS for smoother, calmer appearance

        # DRAG STATE
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Stark Specs
        self.arc_pulse = 0.0
        self.transformation_progress = 1.0 # 0.0 = Suitcase, 1.0 = Humanoid

        # Initialize
        self.create_window()

    def validate_color(self, color, default):
        if isinstance(color, (list, tuple)) and len(color) >= 3:
            return tuple(int(c) for c in color[:4])
        return default

    def draw_kenny(self):
        try:
            self.canvas.delete("all")
            if not PIL_AVAILABLE: return

            scale = 3
            img_size = int(self.size * scale)
            img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            c_x, c_y = (self.size / 2) * scale, (self.size / 2) * scale
            s_s = self.size * scale

            # --- STARK PALETTE ---
            c_red = (178, 34, 34, 255)   # Hot Rod Red
            c_gold = (255, 215, 0, 255)  # Stark Gold
            c_cyan = (0, 255, 255, 255)  # Reactor Cyan
            c_steel = (80, 85, 90, 255)  # Industrial Steel
            c_black = (10, 10, 10, 255)

            # --- TRANSFORMATION LOGIC ---
            tp = self.transformation_progress # 0 to 1

            # 1. THE CHASSIS / SUITCASE BASE
            b_r = (self.size * 0.4) * scale
            height_mod = 0.6 + (0.4 * tp)
            draw.rectangle([c_x - b_r, c_y - b_r*height_mod, c_x + b_r, c_y + b_r*height_mod], fill=c_red, outline=c_gold, width=int(2*scale))

            # 2. MECHANICAL JOINTS
            if tp > 0.2:
                n_h = (b_r * 0.4) * tp
                draw.rectangle([c_x - b_r*0.2, c_y - b_r - n_h, c_x + b_r*0.2, c_y - b_r], fill=c_steel, outline=c_gold)

            # 3. THE HELMET
            if tp > 0.4:
                hx, hy = c_x, c_y - b_r - (b_r * 0.5 * tp)
                hr = b_r * 0.7
                h_pts = [(hx + hr*math.cos(2*math.pi*i/6-math.pi/2), hy + hr*math.sin(2*math.pi*i/6-math.pi/2)) for i in range(6)]
                draw.polygon(h_pts, fill=c_red, outline=c_gold, width=int(scale))
                draw.rectangle([hx - hr*0.6, hy - hr*0.2, hx + hr*0.6, hy + hr*0.2], fill=c_black, outline=c_cyan)
                draw.rectangle([hx-hr*0.5, hy-hr*0.05, hx-hr*0.2, hy+hr*0.05], fill=c_cyan)
                draw.rectangle([hx+hr*0.2, hy-hr*0.05, hx+hr*0.5, hy+hr*0.05], fill=c_cyan)

            # 4. BEHAVIORAL OVERLAYS
            if self.state == KennyState.WORKING:
                for i in range(5):
                    k_y = c_y + b_r + (i*10)
                    draw.line([c_x - b_r, k_y, c_x + b_r, k_y], fill=(0, 255, 255, 100), width=1)

            if self.state == KennyState.SLEEPING:
                if tp > 0.4:
                    draw.rectangle([hx-hr*0.5, hy-hr*0.05, hx-hr*0.2, hy+hr*0.05], fill=(0, 50, 50, 255))
                    draw.rectangle([hx+hr*0.2, hy-hr*0.05, hx+hr*0.5, hy+hr*0.05], fill=(0, 50, 50, 255))

            # 5. RECESSED ARC REACTOR
            p = 1.0 + 0.1 * math.sin(self.animation_frame * 0.2)
            ar = (b_r * 0.3) * p
            draw.ellipse([c_x - ar, c_y - ar, c_x + ar, c_y + ar], fill=c_cyan, outline=(255,255,255,255), width=int(scale))
            for i in range(3):
                rad = math.radians(i*120 + self.animation_frame*5)
                draw.line([c_x, c_y, c_x+ar*math.cos(rad), c_y+ar*math.sin(rad)], fill=c_black, width=2)

            # Final Image
            img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if hasattr(self, 'kenny_photo'): del self.kenny_photo
            self.kenny_photo = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(self.size/2, self.size/2, image=self.kenny_photo)

        except Exception as e:
            logger.error(f"💥 STARK CORE CRASH: {e}")

    def create_window(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', '#000001')
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size, bg='#000001', highlightthickness=0)
        self.canvas.pack()

        # BINDINGS
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<Double-Button-1>", self.handle_double_click)

        self.animate()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # RECORD DRAG START FOR EYE TRACKING FINE-TUNING
        try:
            from va_movement_fine_tuning import get_va_movement_fine_tuning, MovementType
            movement_system = get_va_movement_fine_tuning()
            start_x = self.root.winfo_x()
            start_y = self.root.winfo_y()
            movement_system.record_movement(
                va_id="kenny",
                va_name="Kenny",
                movement_type=MovementType.DRAG_START,
                screen_position=(start_x, start_y),
                window_size=(self.size, self.size),
                context={"state": self.state.value}
            )
        except ImportError:
            pass  # Fine-tuning system not available

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")
        self.x, self.y = x, y
        self.target_x, self.target_y = x, y

        # RECORD MOVEMENT FOR EYE TRACKING FINE-TUNING
        # User moved Kenny - they were looking at it, valuable learning data!
        try:
            from va_movement_fine_tuning import get_va_movement_fine_tuning, MovementType
            movement_system = get_va_movement_fine_tuning()
            movement_system.record_movement(
                va_id="kenny",
                va_name="Kenny",
                movement_type=MovementType.DRAG_MOVE,
                screen_position=(x, y),
                window_size=(self.size, self.size),
                context={"state": self.state.value}
            )
        except ImportError:
            pass  # Fine-tuning system not available

    def handle_double_click(self, event):
        # RECORD DOUBLE CLICK FOR EYE TRACKING FINE-TUNING
        try:
            from va_movement_fine_tuning import get_va_movement_fine_tuning, MovementType
            movement_system = get_va_movement_fine_tuning()
            click_x = self.root.winfo_x()
            click_y = self.root.winfo_y()
            movement_system.record_movement(
                va_id="kenny",
                va_name="Kenny",
                movement_type=MovementType.DOUBLE_CLICK,
                screen_position=(click_x, click_y),
                window_size=(self.size, self.size),
                context={"action": "transform", "state": self.state.value}
            )
        except ImportError:
            pass  # Fine-tuning system not available

        # Force transformation toggle
        if self.transformation_progress > 0.5:
            self.transformation_progress = 0.0 # To Suitcase
            self.state = KennyState.IDLE
            logger.info("💼 Transformation: SUITCASE MODE")
        else:
            self.transformation_progress = 1.0 # To Armor
            self.state = KennyState.WALKING
            logger.info("🚀 Transformation: ARMOR MODE")
        self.draw_kenny()

    def animate(self):
        if not self.root: return
        self.animation_frame += 1

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.x += dx * self.interpolation_factor
        self.y += dy * self.interpolation_factor

        # SLOWER: Use configurable interval for position changes (was: every 100 frames)
        if self.animation_frame % self.position_change_interval == 0:
            self.target_x = random.randint(50, self.root.winfo_screenwidth()-150)
            self.target_y = random.randint(50, self.root.winfo_screenheight()-150)

        self.root.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")
        self.draw_kenny()
        # SLOWER: Use configurable animation interval (was: 30ms)
        self.root.after(self.animation_interval_ms, self.animate)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    kenny = KennyIMVAEnhanced()
    kenny.start()
