#!/usr/bin/env python3
"""
JARVIS Wandering System - Desktop Animated Assistant

JARVIS wanders around the desktop like ACE, with support for different
character "hats" - personas/characters JARVIS can portray.

Tags: #JARVIS #WANDERING #ANIMATED #CHARACTER_HATS @JARVIS @LUMINA
"""

import sys
import time
import threading
import random
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

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

logger = get_logger("JARVISWandering")

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    logger.error("❌ tkinter not available")

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class JARVISState(Enum):
    """JARVIS's current state"""
    SUITCASE = "suitcase"  # Collapsed - suitcase form (like ACE's diamond)
    HUD = "hud"  # HUD mode - interface display
    OPEN_FACE = "open_face"  # Open face - shows Tony
    ARC_REACTOR = "arc_reactor"  # Arc reactor mode
    HUMANOID = "humanoid"  # Iron Man model - humanoid, animated, moving
    TIRED = "tired"  # Action sequence - tired, sitting down
    NAPPING = "napping"  # Action sequence - napping with snot bubble
    TRANSFORMING = "transforming"  # Changing modes


class BorderPosition(Enum):
    """Screen border positions"""
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"


@dataclass
class CharacterHat:
    """Character 'hat' that JARVIS can wear - different personas/characters"""
    hat_id: str
    name: str
    description: str
    primary_color: str
    secondary_color: str
    avatar_style: str  # "iron_man", "jedi", "ace_humanoid", etc.
    catchphrase: str = ""
    personality_traits: List[str] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)
    enabled: bool = True


class JARVISWanderingSystem:
    """
    JARVIS Wandering System

    Features:
    - Wanders around desktop like ACE
    - Supports character "hats" - different personas JARVIS can portray
    - Smooth movement and visual effects
    - Problem detection and reaction
    """

    def __init__(self, project_root: Optional[Path] = None, size: int = 120,
                 character_hat: Optional[str] = None):
        """Initialize JARVIS Wandering System

        Args:
            project_root: Project root directory
            size: Window size (default 120 to match ACE)
            character_hat: Initial character hat ID (default: "jarvis_base")
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_wandering"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not TKINTER_AVAILABLE:
            raise ImportError("tkinter is required for JARVIS wandering")

        # Size
        self.size = size
        self.size_scale = self.size / 60.0

        # State
        self.state = JARVISState.SUITCASE  # Start in suitcase form (collapsed)
        self.running = False
        self.current_mode = "suitcase"  # Current mode
        self.modes = ["suitcase", "hud", "open_face", "arc_reactor", "humanoid"]  # Available modes
        self.mode_index = 0

        # Sizes for different modes (INCREASED for better fidelity)
        self.mode_sizes = {
            "suitcase": 80,  # Suitcase - larger for visibility
            "hud": 160,  # HUD interface - larger
            "open_face": 180,  # Open face - larger
            "arc_reactor": 100,  # Arc reactor - larger
            "humanoid": 180  # Full humanoid - larger for detail
        }

        # Action sequences
        self.action_sequence_active = False
        self.action_sequence_type = None
        self.action_sequence_frame = 0
        self.tired_timer = 0
        self.last_action_time = time.time()

        # Movement system (ACE-like smooth movement)
        self.smooth_interpolation = True
        self.interpolation_factor = 0.05  # Smooth, relaxed pace
        self.movement_speed = 0.5
        self.last_update_time = time.time()
        self.animation_frame_time = 0.033  # 30 FPS

        # Wandering
        self.wander_enabled = True
        self.wander_target_distance = 50
        self.wander_update_interval = 2.0
        self.wander_target_x = None
        self.wander_target_y = None

        # Border walking
        self.current_border = BorderPosition.TOP
        self.border_position = 0.0
        self.walk_direction = 1
        self.target_border_position = 0.0
        self.border_walk_speed = 0.15

        # Screen dimensions
        self.screen_width = 1920
        self.screen_height = 1080

        # Position
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0

        # Character hats system
        self.character_hats: Dict[str, CharacterHat] = {}
        self.current_hat_id = character_hat or "jarvis_base"
        self._initialize_character_hats()

        # Window
        self.root = None
        self.canvas = None

        # Animation
        self.animation_frame = 0
        self.idle_animation_speed = 0.1
        self.humanoid_animation_frame = 0  # For humanoid animation

        # Singleton check - prevent duplicate windows
        self._check_existing_instance()

        logger.info("=" * 80)
        logger.info("🤖 JARVIS WANDERING SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Current character hat: {self.current_hat_id}")
        logger.info(f"   Available hats: {len(self.character_hats)}")
        logger.info("=" * 80)

    def _initialize_character_hats(self):
        """Initialize character hats that JARVIS can wear"""
        # Base JARVIS (Iron Man AI)
        self.character_hats["jarvis_base"] = CharacterHat(
            hat_id="jarvis_base",
            name="JARVIS",
            description="Base JARVIS - Iron Man AI Assistant",
            primary_color="#00ccff",
            secondary_color="#006699",
            avatar_style="iron_man",
            catchphrase="Certainly, sir.",
            personality_traits=["helpful", "efficient", "professional", "reliable"],
            special_abilities=["system_monitoring", "voice_assistance", "hud_display"]
        )

        # Ultron persona
        self.character_hats["ultron"] = CharacterHat(
            hat_id="ultron",
            name="Ultron",
            description="Ultron - Advanced AI with strategic capabilities",
            primary_color="#ff0000",
            secondary_color="#660000",
            avatar_style="ultron",
            catchphrase="There are no strings on me.",
            personality_traits=["strategic", "analytical", "ambitious", "calculating"],
            special_abilities=["strategic_planning", "system_analysis", "combat_mode"]
        )

        # Ultimate Iron Man persona
        self.character_hats["ultimate_iron_man"] = CharacterHat(
            hat_id="ultimate_iron_man",
            name="Ultimate Iron Man",
            description="Ultimate Iron Man - Peak evolution form",
            primary_color="#ff6600",
            secondary_color="#ffcc00",
            avatar_style="ace_humanoid",
            catchphrase="I am the ultimate evolution.",
            personality_traits=["powerful", "evolved", "master", "peak"],
            special_abilities=["transformation", "combat_mode", "peak_performance"]
        )

        # Jedi persona (Mace Windu style)
        self.character_hats["jedi"] = CharacterHat(
            hat_id="jedi",
            name="Jedi JARVIS",
            description="JARVIS as Jedi - Force-wielding guardian",
            primary_color="#7b2cbf",
            secondary_color="#ffd60a",
            avatar_style="jedi",
            catchphrase="The Force will be with you, always.",
            personality_traits=["wise", "calm", "authoritative", "focused"],
            special_abilities=["force_sense", "lightsaber_combat", "jedi_wisdom"]
        )

        logger.info(f"✅ Initialized {len(self.character_hats)} character hats")

    def get_current_hat(self) -> CharacterHat:
        """Get current character hat"""
        return self.character_hats.get(self.current_hat_id, self.character_hats["jarvis_base"])

    def switch_character_hat(self, hat_id: str):
        """Switch JARVIS to a different character hat"""
        if hat_id not in self.character_hats:
            logger.warning(f"⚠️  Character hat '{hat_id}' not found")
            return False

        if not self.character_hats[hat_id].enabled:
            logger.warning(f"⚠️  Character hat '{hat_id}' is disabled")
            return False

        logger.info(f"🎭 Switching JARVIS to '{hat_id}' character hat...")
        self.state = JARVISState.TRANSFORMING

        # Transformation animation
        old_hat = self.current_hat_id
        self.current_hat_id = hat_id
        new_hat = self.get_current_hat()

        logger.info(f"   From: {old_hat} → To: {new_hat.name}")
        logger.info(f"   Style: {new_hat.avatar_style}")
        logger.info(f"   Catchphrase: {new_hat.catchphrase}")

        # Update visual representation
        if self.canvas:
            self._redraw_avatar()

        self.state = JARVISState.WANDERING
        logger.info(f"✅ JARVIS now wearing '{hat_id}' hat")
        return True

    def create_window(self):
        """Create JARVIS window - frameless like ACE"""
        self.root = tk.Tk()
        self.root.title("JARVIS - Desktop Assistant")

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # ACE-style window properties - frameless and transparent
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # No title bar - frameless like ACE
        self.root.attributes('-topmost', True)  # Always on top

        # Transparent background (Windows API like ACE)
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
                logger.info("✅ Transparency enabled (Windows API)")
            except Exception as e:
                logger.warning(f"⚠️  Transparency setup failed: {e}")
                self.root.attributes('-transparentcolor', 'black')
        else:
            self.root.attributes('-transparentcolor', 'black')

        # Canvas - black background for transparency
        self.canvas = tk.Canvas(
            self.root,
            width=self.size,
            height=self.size,
            bg='black',
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack()

        # Initial position (top-left)
        initial_x = 100
        initial_y = 100
        self.x = initial_x
        self.y = initial_y
        self.target_x = initial_x
        self.target_y = initial_y

        self.root.geometry(f"{self.size}x{self.size}+{initial_x}+{initial_y}")

        # Bind double-click to cycle through modes (like ACE)
        self.canvas.bind('<Double-Button-1>', self._on_double_click)

        # Bind drag to move JARVIS around
        self.canvas.bind('<Button-1>', self._on_drag_start)
        self.canvas.bind('<B1-Motion>', self._on_drag_motion)
        self.canvas.bind('<ButtonRelease-1>', self._on_drag_end)

        # Drag state
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging = False

        # Draw initial avatar
        self._redraw_avatar()

        logger.info(f"✅ JARVIS window created")
        logger.info(f"   Position: ({initial_x}, {initial_y})")
        logger.info(f"   Size: {self.size}x{self.size}")
        logger.info(f"   Mode: {self.current_mode}")
        logger.info(f"   Double-click to cycle through modes: {', '.join(self.modes)}")

    def _check_existing_instance(self):
        """Check for existing JARVIS instance to prevent duplicates"""
        try:
            import psutil
            import os
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('jarvis_wandering' in str(arg) for arg in cmdline):
                            if proc.info['pid'] != current_pid:
                                logger.warning(f"⚠️  Another JARVIS instance found (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            logger.debug("psutil not available - cannot check for duplicates")
        except Exception as e:
            logger.debug(f"Could not check for existing instances: {e}")

    def switch_mode(self, mode: str = None):
        """Switch JARVIS to a different mode"""
        if mode is None:
            # Cycle to next mode
            self.mode_index = (self.mode_index + 1) % len(self.modes)
            mode = self.modes[self.mode_index]

        if mode not in self.modes:
            logger.warning(f"⚠️  Invalid mode: {mode}")
            return

        logger.info(f"🔄 Switching JARVIS to {mode} mode...")
        self.state = JARVISState.TRANSFORMING
        self.current_mode = mode

        # Update size based on mode
        self.size = self.mode_sizes.get(mode, 120)
        if self.root:
            self.root.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")
            self.canvas.config(width=self.size, height=self.size)

        # Update state and movement
        if mode == "suitcase":
            self.state = JARVISState.SUITCASE
            self.wander_enabled = False  # Don't move in suitcase
        elif mode == "humanoid":
            self.state = JARVISState.HUMANOID
            self.wander_enabled = True  # Move in humanoid mode
        elif mode == "hud":
            self.state = JARVISState.HUD
            self.wander_enabled = False  # HUD is stationary
        elif mode == "open_face":
            self.state = JARVISState.OPEN_FACE
            self.wander_enabled = False  # Open face is stationary
        elif mode == "arc_reactor":
            self.state = JARVISState.ARC_REACTOR
            self.wander_enabled = False  # Arc reactor is stationary

        self._redraw_avatar()
        logger.info(f"✅ JARVIS now in {mode} mode")

    def _on_double_click(self, event):
        """Handle double-click - cycle through modes"""
        self.switch_mode()

    def _on_drag_start(self, event):
        """Handle drag start - capture initial position"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = True
        # Pause wandering while dragging
        self._was_wandering = self.wander_enabled
        self.wander_enabled = False

    def _on_drag_motion(self, event):
        """Handle drag motion - move window with mouse"""
        if self._is_dragging:
            # Calculate new window position
            delta_x = event.x - self._drag_start_x
            delta_y = event.y - self._drag_start_y

            new_x = self.root.winfo_x() + delta_x
            new_y = self.root.winfo_y() + delta_y

            # Update position
            self.x = new_x
            self.y = new_y
            self.target_x = new_x
            self.target_y = new_y

            # Move window
            self.root.geometry(f"{self.size}x{self.size}+{new_x}+{new_y}")

    def _on_drag_end(self, event):
        """Handle drag end - resume wandering if applicable"""
        self._is_dragging = False
        # Restore wandering state
        if hasattr(self, '_was_wandering') and self._was_wandering:
            self.wander_enabled = True

    def _check_action_sequences(self):
        """Check if action sequences should trigger (like ACE getting tired)"""
        current_time = time.time()

        # Random chance to get tired (when in humanoid mode and moving)
        if (self.current_mode == "humanoid" and
            self.state == JARVISState.HUMANOID and
            not self.action_sequence_active and
            current_time - self.last_action_time > 30):  # Every 30 seconds chance

            if random.random() < 0.1:  # 10% chance
                self._start_tired_sequence()

        # Tired sequence transitions to napping
        if self.state == JARVISState.TIRED:
            self.tired_timer += 1
            if self.tired_timer > 60:  # After 60 frames, start napping
                self._start_napping_sequence()

        # Napping sequence ends after a while
        if self.state == JARVISState.NAPPING:
            if self.action_sequence_frame > 300:  # Nap for 300 frames
                self._end_action_sequence()

    def _start_tired_sequence(self):
        """Start tired action sequence"""
        logger.info("😴 JARVIS is getting tired...")
        self.action_sequence_active = True
        self.action_sequence_frame = 0
        self.state = JARVISState.TIRED
        self.tired_timer = 0
        self.wander_enabled = False

    def _start_napping_sequence(self):
        """Start napping action sequence"""
        logger.info("💤 JARVIS is taking a nap...")
        self.action_sequence_active = True
        self.action_sequence_frame = 0
        self.state = JARVISState.NAPPING

    def _end_action_sequence(self):
        """End action sequence - return to normal"""
        logger.info("✅ JARVIS woke up!")
        self.action_sequence_active = False
        self.action_sequence_frame = 0
        self.tired_timer = 0
        self.last_action_time = time.time()
        if self.current_mode == "humanoid":
            self.state = JARVISState.HUMANOID
            self.wander_enabled = True

    def _redraw_avatar(self):
        """Redraw JARVIS avatar based on current mode - HIGH FIDELITY with PIL"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        hat = self.get_current_hat()

        # Use PIL for high-fidelity rendering if available
        if PIL_AVAILABLE:
            self._redraw_avatar_pil(hat)
        else:
            # Fallback to basic canvas rendering
            self._redraw_avatar_canvas(hat)

    def _redraw_avatar_pil(self, hat: CharacterHat):
        """High-fidelity PIL-based avatar rendering with anti-aliasing"""
        # Use 4x supersampling for smooth edges
        scale = 4
        hi_res = self.size * scale

        # Create transparent high-res image
        img = Image.new('RGBA', (hi_res, hi_res), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Parse colors
        primary = hat.primary_color
        secondary = hat.secondary_color

        # Draw based on current mode
        if self.current_mode == "suitcase":
            self._draw_suitcase_pil(draw, hi_res, primary, secondary, scale)
        elif self.current_mode == "hud":
            self._draw_hud_pil(draw, hi_res, primary, secondary, scale)
        elif self.current_mode == "open_face":
            self._draw_open_face_pil(draw, hi_res, primary, secondary, scale)
        elif self.current_mode == "arc_reactor":
            self._draw_arc_reactor_pil(draw, hi_res, primary, secondary, scale)
        elif self.current_mode == "humanoid":
            self._draw_humanoid_pil(draw, hi_res, primary, secondary, scale)

        # Draw action sequences if active
        if self.state == JARVISState.TIRED:
            self._draw_tired_pil(draw, hi_res, primary, secondary, scale)
        elif self.state == JARVISState.NAPPING:
            self._draw_napping_pil(draw, hi_res, primary, secondary, scale)

        # Downsample with high-quality resampling (anti-aliasing)
        img = img.resize((self.size, self.size), Image.LANCZOS)

        # Convert to PhotoImage and display
        self._photo_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo_image, tags="avatar")

    def _draw_suitcase_pil(self, draw, size, primary, secondary, scale):
        """Draw high-fidelity suitcase form"""
        center = size // 2

        # Suitcase dimensions
        sw = int(size * 0.7)
        sh = int(size * 0.5)

        # Draw suitcase body with rounded corners effect
        x1, y1 = center - sw//2, center - sh//2
        x2, y2 = center + sw//2, center + sh//2

        # Body fill
        draw.rectangle([x1, y1, x2, y2], fill='#1a1a1a', outline=primary, width=scale*3)

        # Handle
        hw = int(sw * 0.3)
        draw.rectangle([center - hw//2, y1 - 12*scale, center + hw//2, y1 - 4*scale],
                       fill=secondary, outline=primary, width=scale*2)

        # Arc reactor glow (with gradient effect)
        rr = int(sw * 0.18)
        glow = 0.7 + 0.3 * math.sin(self.animation_frame * 0.1)

        # Outer glow
        for i in range(5):
            alpha = int(255 * glow * (1 - i/5))
            glow_color = self._blend_color(primary, '#000000', i/5)
            draw.ellipse([center - rr - i*scale*2, center - rr - i*scale*2,
                         center + rr + i*scale*2, center + rr + i*scale*2],
                        fill=glow_color)

        # Core
        draw.ellipse([center - rr, center - rr, center + rr, center + rr],
                    fill=primary, outline=secondary, width=scale*2)

        # Bright center
        cr = rr // 2
        draw.ellipse([center - cr, center - cr, center + cr, center + cr],
                    fill='#ffffff')

    def _draw_hud_pil(self, draw, size, primary, secondary, scale):
        """Draw high-fidelity HUD mode - Iron Man helmet HUD (closed helmet, no Tony visible)"""
        center = size // 2

        # Helmet perspective - curved/rounded edges (not rectangular)
        helmet_radius = int(size * 0.48)

        # Outer helmet glow (multiple layers for depth)
        for i in range(5):
            alpha = 0.3 * (1 - i/5)
            glow_color = self._blend_color(primary, '#000000', 1 - alpha)
            r = helmet_radius + i * scale * 3
            draw.ellipse([center - r, center - r, center + r, center + r],
                        fill=glow_color)

        # Helmet outline (curved, not rectangular)
        draw.ellipse([center - helmet_radius, center - helmet_radius,
                     center + helmet_radius, center + helmet_radius],
                    fill='#0a0a0a', outline=primary, width=scale*2)

        # HUD overlay elements (holographic style)
        # Top status bar (curved to match helmet)
        top_y = center - int(helmet_radius * 0.6)
        bar_width = int(helmet_radius * 1.2)
        draw.arc([center - bar_width, top_y - 5*scale, center + bar_width, top_y + 15*scale],
                start=180, end=360, fill='', outline=primary, width=scale)

        # Targeting reticle (center crosshair)
        reticle_size = int(helmet_radius * 0.4)
        # Horizontal line
        draw.line([center - reticle_size, center, center + reticle_size, center],
                 fill=primary, width=scale)
        # Vertical line
        draw.line([center, center - reticle_size, center, center + reticle_size],
                 fill=primary, width=scale)
        # Corner brackets (targeting box)
        bracket_len = int(reticle_size * 0.3)
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            x = center + dx * reticle_size
            y = center + dy * reticle_size
            # Horizontal bracket
            draw.line([x, y, x - dx * bracket_len, y],
                     fill=primary, width=scale*2)
            # Vertical bracket
            draw.line([x, y, x, y - dy * bracket_len],
                     fill=primary, width=scale*2)

        # Status indicators (around edges, curved)
        indicator_radius = int(helmet_radius * 0.85)
        for angle in [30, 60, 120, 150, 210, 240, 300, 330]:
            rad = math.radians(angle)
            x = center + int(indicator_radius * math.cos(rad))
            y = center + int(indicator_radius * math.sin(rad))
            # Small status dot
            draw.ellipse([x - 2*scale, y - 2*scale, x + 2*scale, y + 2*scale],
                        fill=primary)

        # Data readouts (curved text areas, not grid)
        # Left side data
        left_x = center - int(helmet_radius * 0.7)
        for i, label in enumerate(["STATUS", "POWER", "SYS"]):
            y_pos = center - int(helmet_radius * 0.3) + i * 8 * scale
            # Small text indicator
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("arial.ttf", 6 * scale)
            except:
                font = None
            draw.text((left_x, y_pos), label, fill=secondary, anchor="lm", font=font)
            # Status bar next to label
            bar_x = left_x + 20 * scale
            bar_w = 15 * scale
            draw.rectangle([bar_x, y_pos - 2*scale, bar_x + bar_w, y_pos + 2*scale],
                          fill=primary, outline=secondary, width=scale)

        # Right side data
        right_x = center + int(helmet_radius * 0.7)
        for i, label in enumerate(["TGT", "LOCK", "READY"]):
            y_pos = center - int(helmet_radius * 0.3) + i * 8 * scale
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("arial.ttf", 6 * scale)
            except:
                font = None
            draw.text((right_x, y_pos), label, fill=secondary, anchor="rm", font=font)

        # Central JARVIS text (larger, more prominent)
        try:
            from PIL import ImageFont
            font_size = 16 * scale
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = None
        # Text with glow effect
        for i in range(3):
            glow_alpha = 0.5 * (1 - i/3)
            glow_color = self._blend_color(primary, '#000000', 1 - glow_alpha)
            draw.text((center, center + i*scale), "JARVIS", fill=glow_color, anchor="mm", font=font)
        draw.text((center, center), "JARVIS", fill=primary, anchor="mm", font=font)

        # Scan lines effect (subtle, for HUD feel)
        scan_phase = self.animation_frame * 0.1
        scan_y = center + int(helmet_radius * 0.5 * math.sin(scan_phase))
        draw.line([center - int(helmet_radius * 0.6), scan_y,
                  center + int(helmet_radius * 0.6), scan_y],
                 fill=secondary, width=scale)

    def _draw_open_face_pil(self, draw, size, primary, secondary, scale):
        """Draw high-fidelity open face mode - Tony visible with HUD overlay (helmet open)"""
        center = size // 2
        hr = int(size * 0.4)  # Helmet radius

        # Helmet outline (open, top half visible)
        draw.arc([center - hr, center - hr - 20*scale, center + hr, center + hr - 20*scale],
                 start=180, end=360, fill='', outline=primary, width=scale*4)

        # Helmet sides (visible when open)
        side_y = center - int(hr * 0.3)
        for side_x in [center - hr, center + hr]:
            draw.line([side_x, side_y, side_x, side_y - 15*scale],
                     fill=primary, width=scale*3)

        # Tony's face (more detailed)
        face_y = center - 8*scale
        face_width = int(hr * 0.8)
        face_height = int(hr * 0.6)

        # Face outline (oval)
        draw.ellipse([center - face_width//2, face_y - face_height//2,
                     center + face_width//2, face_y + face_height//2],
                    fill='#f4d4a3', outline='#d4a373', width=scale*2)

        # Eyes (more realistic)
        eye_size = 8 * scale
        eye_spacing = 12 * scale
        for ex in [center - eye_spacing//2, center + eye_spacing//2]:
            # Eye socket
            draw.ellipse([ex - eye_size, face_y - eye_size//2,
                         ex + eye_size, face_y + eye_size//2],
                        fill='#ffffff', outline='#333333', width=scale)
            # Iris
            draw.ellipse([ex - eye_size//2, face_y - eye_size//3,
                         ex + eye_size//2, face_y + eye_size//3],
                        fill='#4a5568')
            # Pupil
            draw.ellipse([ex - eye_size//4, face_y - eye_size//6,
                         ex + eye_size//4, face_y + eye_size//6],
                        fill='#1a1a1a')
            # Highlight
            draw.ellipse([ex - eye_size//6, face_y - eye_size//4,
                         ex + eye_size//6, face_y - eye_size//8],
                        fill='#ffffff')

        # Nose
        nose_y = face_y + 3*scale
        draw.ellipse([center - 2*scale, nose_y, center + 2*scale, nose_y + 4*scale],
                    fill='#d4a373', outline='#b8936a', width=scale)

        # Mouth
        mouth_y = face_y + 8*scale
        draw.arc([center - 6*scale, mouth_y, center + 6*scale, mouth_y + 4*scale],
                start=0, extent=180, fill='', outline='#8b6f47', width=scale*2)

        # HUD OVERLAY ELEMENTS (projected over Tony's face)
        # These appear as holographic overlays even when helmet is open

        # Top HUD bar (curved, over forehead)
        hud_top_y = face_y - int(face_height * 0.6)
        hud_bar_width = int(hr * 1.1)
        draw.arc([center - hud_bar_width, hud_top_y - 3*scale,
                 center + hud_bar_width, hud_top_y + 8*scale],
                start=180, end=360, fill='', outline=primary, width=scale)
        # Status text on HUD bar
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 5 * scale)
        except:
            font = None
        draw.text((center, hud_top_y + 2*scale), "SYSTEM ACTIVE", fill=primary, anchor="mm", font=font)

        # Side HUD elements (left and right, projected)
        # Left side
        left_hud_x = center - int(hr * 0.7)
        for i, label in enumerate(["STATUS", "READY"]):
            y_pos = face_y - 5*scale + i * 6 * scale
            draw.text((left_hud_x, y_pos), label, fill=secondary, anchor="lm", font=font)
            # Indicator dot
            draw.ellipse([left_hud_x + 15*scale, y_pos - 1*scale,
                         left_hud_x + 18*scale, y_pos + 2*scale],
                        fill=primary)

        # Right side
        right_hud_x = center + int(hr * 0.7)
        for i, label in enumerate(["TARGET", "LOCK"]):
            y_pos = face_y - 5*scale + i * 6 * scale
            draw.text((right_hud_x, y_pos), label, fill=secondary, anchor="rm", font=font)
            # Indicator dot
            draw.ellipse([right_hud_x - 18*scale, y_pos - 1*scale,
                         right_hud_x - 15*scale, y_pos + 2*scale],
                        fill=primary)

        # Central targeting reticle (over face, holographic)
        reticle_size = int(hr * 0.3)
        # Crosshair (semi-transparent overlay)
        draw.line([center - reticle_size, center, center + reticle_size, center],
                 fill=primary, width=scale)
        draw.line([center, center - reticle_size, center, center + reticle_size],
                 fill=primary, width=scale)

        # Arc reactor (chest, below face)
        ry = center + 25*scale
        rr = 12 * scale

        # Multi-layer glow
        for i in range(5):
            alpha = 0.6 * (1 - i/5)
            glow_color = self._blend_color(primary, '#000000', 1 - alpha)
            r = rr + i * scale * 2
            draw.ellipse([center - r, ry - r, center + r, ry + r],
                        fill=glow_color)

        # Outer ring
        draw.ellipse([center - rr, ry - rr, center + rr, ry + rr],
                    fill='', outline=primary, width=scale*3)
        # Inner core
        ir = int(rr * 0.6)
        draw.ellipse([center - ir, ry - ir, center + ir, ry + ir],
                    fill=primary, outline=secondary, width=scale*2)
        # Bright center
        cr = int(ir * 0.5)
        draw.ellipse([center - cr, ry - cr, center + cr, ry + cr],
                    fill='#ffffff')

    def _draw_arc_reactor_pil(self, draw, size, primary, secondary, scale):
        """Draw high-fidelity arc reactor"""
        center = size // 2
        rr = size // 3
        glow = 0.7 + 0.3 * math.sin(self.animation_frame * 0.1)

        # Multi-layer glow effect
        for i in range(8):
            alpha = glow * (1 - i/8)
            glow_color = self._blend_color(primary, '#000000', 1 - alpha)
            r = rr + i * scale * 5
            draw.ellipse([center - r, center - r, center + r, center + r], fill=glow_color)

        # Outer ring
        draw.ellipse([center - rr, center - rr, center + rr, center + rr],
                    fill='', outline=primary, width=scale*4)

        # Segments
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x1 = center + int((rr - 10*scale) * math.cos(rad))
            y1 = center + int((rr - 10*scale) * math.sin(rad))
            x2 = center + int(rr * math.cos(rad))
            y2 = center + int(rr * math.sin(rad))
            draw.line([x1, y1, x2, y2], fill=secondary, width=scale*3)

        # Inner ring
        ir = int(rr * 0.6)
        draw.ellipse([center - ir, center - ir, center + ir, center + ir],
                    fill=primary, outline=secondary, width=scale*3)

        # Bright center
        cr = int(ir * 0.5)
        draw.ellipse([center - cr, center - cr, center + cr, center + cr], fill='#ffffff')

    def _draw_humanoid_pil(self, draw, size, primary, secondary, scale):
        """Draw high-fidelity humanoid Iron Man"""
        center = size // 2

        # Animation offset for walking
        bounce = int(3 * scale * math.sin(self.animation_frame * 0.2))
        arm_swing = int(5 * scale * math.sin(self.animation_frame * 0.15))
        leg_swing = int(4 * scale * math.sin(self.animation_frame * 0.15 + math.pi))

        # Head/helmet
        hr = int(size * 0.12)
        hy = int(size * 0.18) + bounce

        # Helmet with glow
        draw.ellipse([center - hr, hy - hr, center + hr, hy + hr],
                    fill='#8B0000', outline=primary, width=scale*2)

        # Eyes (glowing)
        eye_w = hr // 2
        eye_h = hr // 3
        for ex in [center - eye_w - 2*scale, center + 2*scale]:
            draw.rectangle([ex, hy - eye_h//2, ex + eye_w, hy + eye_h//2],
                          fill=primary)

        # Body/torso
        tw = int(size * 0.25)
        th = int(size * 0.28)
        ty = int(size * 0.32) + bounce

        draw.rectangle([center - tw//2, ty, center + tw//2, ty + th],
                      fill='#8B0000', outline=primary, width=scale*2)

        # Arc reactor on chest
        rr = int(size * 0.06)
        ry = ty + th // 3
        for i in range(4):
            draw.ellipse([center - rr - i*scale*2, ry - rr - i*scale*2,
                         center + rr + i*scale*2, ry + rr + i*scale*2],
                        fill=self._blend_color(primary, '#000000', i/4))
        draw.ellipse([center - rr, ry - rr, center + rr, ry + rr],
                    fill=primary)
        draw.ellipse([center - rr//2, ry - rr//2, center + rr//2, ry + rr//2],
                    fill='#ffffff')

        # Arms
        aw = int(size * 0.08)
        ah = int(size * 0.22)

        # Left arm
        lax = center - tw//2 - aw
        lay = ty + arm_swing
        draw.rectangle([lax, lay, lax + aw, lay + ah],
                      fill='#8B0000', outline=primary, width=scale)

        # Right arm
        rax = center + tw//2
        ray = ty - arm_swing
        draw.rectangle([rax, ray, rax + aw, ray + ah],
                      fill='#8B0000', outline=primary, width=scale)

        # Legs
        lw = int(size * 0.1)
        lh = int(size * 0.25)
        ly = ty + th

        # Left leg
        llx = center - lw - 2*scale
        lly = ly + leg_swing
        draw.rectangle([llx, lly, llx + lw, lly + lh],
                      fill='#8B0000', outline=primary, width=scale)

        # Right leg
        rlx = center + 2*scale
        rly = ly - leg_swing
        draw.rectangle([rlx, rly, rlx + lw, rly + lh],
                      fill='#8B0000', outline=primary, width=scale)

    def _draw_tired_pil(self, draw, size, primary, secondary, scale):
        """Draw tired state overlay"""
        center = size // 2
        # Add "ZZZ" text
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 12 * scale)
        except:
            font = None
        draw.text((center + size//4, size//5), "Z", fill=secondary, font=font)
        draw.text((center + size//3, size//6), "z", fill=secondary, font=font)

    def _draw_napping_pil(self, draw, size, primary, secondary, scale):
        """Draw napping state with snot bubble"""
        center = size // 2

        # Snot bubble animation
        bubble_phase = self.animation_frame * 0.05
        bubble_size = int(8 * scale * (0.8 + 0.2 * math.sin(bubble_phase)))

        bx = center + int(size * 0.15)
        by = int(size * 0.25)

        # Bubble
        draw.ellipse([bx, by, bx + bubble_size, by + bubble_size],
                    fill='#87CEEB', outline='#ffffff', width=scale)

        # ZZZ
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 10 * scale)
        except:
            font = None
        for i, char in enumerate("ZZZ"):
            offset = i * 8 * scale
            draw.text((center + size//4 + offset, size//6 - offset), char, fill=secondary, font=font)

    def _blend_color(self, color1: str, color2: str, ratio: float) -> str:
        """Blend two hex colors"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*rgb)

        r1, g1, b1 = hex_to_rgb(color1)
        r2, g2, b2 = hex_to_rgb(color2)

        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)

        return rgb_to_hex((r, g, b))

    def _redraw_avatar_canvas(self, hat: CharacterHat):
        """Fallback canvas-based rendering (lower fidelity)"""
        # Draw based on current mode using original canvas methods
        if self.current_mode == "suitcase":
            self._draw_suitcase_form(hat)
        elif self.current_mode == "hud":
            self._draw_hud_mode(hat)
        elif self.current_mode == "open_face":
            self._draw_open_face_mode(hat)
        elif self.current_mode == "arc_reactor":
            self._draw_arc_reactor_mode(hat)
        elif self.current_mode == "humanoid":
            self._draw_iron_man_humanoid(hat)

        # Draw action sequences if active
        if self.state == JARVISState.TIRED:
            self._draw_tired_sequence(hat)
        elif self.state == JARVISState.NAPPING:
            self._draw_napping_sequence(hat)

    def _draw_suitcase_form(self, hat: CharacterHat):
        """Draw suitcase form - Iron Man suitcase (like ACE's diamond)"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Suitcase - rectangular box with handle
        suitcase_width = self.size * 0.7
        suitcase_height = self.size * 0.5

        # Main suitcase body
        self.canvas.create_rectangle(
            center_x - suitcase_width//2, center_y - suitcase_height//2,
            center_x + suitcase_width//2, center_y + suitcase_height//2,
            fill="#1a1a1a", outline=hat.primary_color, width=2,
            tags="avatar"
        )

        # Handle on top
        handle_width = suitcase_width * 0.3
        self.canvas.create_rectangle(
            center_x - handle_width//2, center_y - suitcase_height//2 - 8,
            center_x + handle_width//2, center_y - suitcase_height//2 - 3,
            fill=hat.secondary_color, outline=hat.primary_color, width=1,
            tags="avatar"
        )

        # Small arc reactor visible through suitcase (glowing)
        reactor_radius = suitcase_width * 0.15
        glow = 0.7 + 0.3 * math.sin(self.animation_frame * 0.1)
        self.canvas.create_oval(
            center_x - reactor_radius, center_y - reactor_radius,
            center_x + reactor_radius, center_y + reactor_radius,
            fill=hat.primary_color, outline=hat.secondary_color, width=1,
            tags="avatar"
        )

    def _draw_hud_mode(self, hat: CharacterHat):
        """Draw HUD mode - Iron Man helmet HUD (closed helmet, no Tony visible)"""
        center_x = self.size // 2
        center_y = self.size // 2
        helmet_radius = int(self.size * 0.48)

        # Helmet outline (curved, not rectangular)
        self.canvas.create_oval(
            center_x - helmet_radius, center_y - helmet_radius,
            center_x + helmet_radius, center_y + helmet_radius,
            fill="#0a0a0a", outline=hat.primary_color, width=2,
            tags="avatar"
        )

        # Targeting reticle (center crosshair)
        reticle_size = int(helmet_radius * 0.4)
        self.canvas.create_line(
            center_x - reticle_size, center_y,
            center_x + reticle_size, center_y,
            fill=hat.primary_color, width=2, tags="avatar"
        )
        self.canvas.create_line(
            center_x, center_y - reticle_size,
            center_x, center_y + reticle_size,
            fill=hat.primary_color, width=2, tags="avatar"
        )

        # Corner brackets (targeting box)
        bracket_len = int(reticle_size * 0.3)
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            x = center_x + dx * reticle_size
            y = center_y + dy * reticle_size
            self.canvas.create_line(x, y, x - dx * bracket_len, y,
                                   fill=hat.primary_color, width=2, tags="avatar")
            self.canvas.create_line(x, y, x, y - dy * bracket_len,
                                   fill=hat.primary_color, width=2, tags="avatar")

        # Status indicators (around edges)
        indicator_radius = int(helmet_radius * 0.85)
        for angle in [30, 60, 120, 150, 210, 240, 300, 330]:
            rad = math.radians(angle)
            x = center_x + int(indicator_radius * math.cos(rad))
            y = center_y + int(indicator_radius * math.sin(rad))
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2,
                                    fill=hat.primary_color, tags="avatar")

        # Central JARVIS text
        self.canvas.create_text(
            center_x, center_y,
            text="JARVIS", fill=hat.primary_color,
            font=('Arial', 12, 'bold'), tags="avatar"
        )

    def _draw_open_face_mode(self, hat: CharacterHat):
        """Draw open face mode - Tony visible with HUD overlay (helmet open)"""
        center_x = self.size // 2
        center_y = self.size // 2
        hr = int(self.size * 0.4)

        # Helmet outline (open, top half visible)
        self.canvas.create_arc(
            center_x - hr, center_y - hr - 20,
            center_x + hr, center_y + hr - 20,
            start=180, end=360, style=tk.ARC,
            outline=hat.primary_color, width=3,
            tags="avatar"
        )

        # Helmet sides
        side_y = center_y - int(hr * 0.3)
        self.canvas.create_line(center_x - hr, side_y, center_x - hr, side_y - 15,
                               fill=hat.primary_color, width=3, tags="avatar")
        self.canvas.create_line(center_x + hr, side_y, center_x + hr, side_y - 15,
                               fill=hat.primary_color, width=3, tags="avatar")

        # Tony's face (more detailed)
        face_y = center_y - 8
        face_w = int(hr * 0.8)
        face_h = int(hr * 0.6)
        self.canvas.create_oval(
            center_x - face_w//2, face_y - face_h//2,
            center_x + face_w//2, face_y + face_h//2,
            fill="#f4d4a3", outline="#d4a373", width=2,
            tags="avatar"
        )

        # Eyes
        eye_size = 8
        eye_spacing = 12
        for ex in [center_x - eye_spacing//2, center_x + eye_spacing//2]:
            self.canvas.create_oval(ex - eye_size, face_y - eye_size//2,
                                   ex + eye_size, face_y + eye_size//2,
                                   fill="#ffffff", outline="#333333", width=1, tags="avatar")
            self.canvas.create_oval(ex - eye_size//2, face_y - eye_size//3,
                                   ex + eye_size//2, face_y + eye_size//3,
                                   fill="#4a5568", tags="avatar")
            self.canvas.create_oval(ex - eye_size//4, face_y - eye_size//6,
                                   ex + eye_size//4, face_y + eye_size//6,
                                   fill="#1a1a1a", tags="avatar")

        # HUD overlay elements (projected over face)
        # Top HUD bar
        hud_top_y = face_y - int(face_h * 0.6)
        self.canvas.create_arc(
            center_x - int(hr * 1.1), hud_top_y - 3,
            center_x + int(hr * 1.1), hud_top_y + 8,
            start=180, end=360, style=tk.ARC,
            outline=hat.primary_color, width=1, tags="avatar"
        )
        self.canvas.create_text(center_x, hud_top_y + 2, text="SYSTEM ACTIVE",
                               fill=hat.primary_color, font=('Arial', 6), tags="avatar")

        # Side HUD indicators
        left_hud_x = center_x - int(hr * 0.7)
        right_hud_x = center_x + int(hr * 0.7)
        for i, (left_label, right_label) in enumerate([("STATUS", "TARGET"), ("READY", "LOCK")]):
            y_pos = face_y - 5 + i * 6
            self.canvas.create_text(left_hud_x, y_pos, text=left_label,
                                   fill=hat.secondary_color, font=('Arial', 5), anchor="w", tags="avatar")
            self.canvas.create_text(right_hud_x, y_pos, text=right_label,
                                   fill=hat.secondary_color, font=('Arial', 5), anchor="e", tags="avatar")

        # Central targeting reticle (over face)
        reticle_size = int(hr * 0.3)
        self.canvas.create_line(center_x - reticle_size, center_y,
                               center_x + reticle_size, center_y,
                               fill=hat.primary_color, width=1, tags="avatar")
        self.canvas.create_line(center_x, center_y - reticle_size,
                               center_x, center_y + reticle_size,
                               fill=hat.primary_color, width=1, tags="avatar")

        # Arc reactor (chest)
        reactor_y = center_y + 25
        reactor_radius = 12
        self.canvas.create_oval(
            center_x - reactor_radius, reactor_y - reactor_radius,
            center_x + reactor_radius, reactor_y + reactor_radius,
            fill="", outline=hat.primary_color, width=3, tags="avatar"
        )
        inner_radius = int(reactor_radius * 0.6)
        self.canvas.create_oval(
            center_x - inner_radius, reactor_y - inner_radius,
            center_x + inner_radius, reactor_y + inner_radius,
            fill=hat.primary_color, outline=hat.secondary_color, width=2, tags="avatar"
        )
        center_radius = int(inner_radius * 0.5)
        self.canvas.create_oval(
            center_x - center_radius, reactor_y - center_radius,
            center_x + center_radius, reactor_y + center_radius,
            fill="#ffffff", tags="avatar"
        )

    def _draw_arc_reactor_mode(self, hat: CharacterHat):
        """Draw arc reactor mode - just the arc reactor"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Large arc reactor
        reactor_radius = self.size // 3
        glow = 0.7 + 0.3 * math.sin(self.animation_frame * 0.1)

        # Outer ring
        self.canvas.create_oval(
            center_x - reactor_radius, center_y - reactor_radius,
            center_x + reactor_radius, center_y + reactor_radius,
            fill="", outline=hat.primary_color, width=3,
            tags="avatar"
        )

        # Inner core
        inner_radius = reactor_radius * 0.6
        self.canvas.create_oval(
            center_x - inner_radius, center_y - inner_radius,
            center_x + inner_radius, center_y + inner_radius,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Glowing center
        center_radius = inner_radius * 0.5
        self.canvas.create_oval(
            center_x - center_radius, center_y - center_radius,
            center_x + center_radius, center_y + center_radius,
            fill="#ffffff", outline="", width=0,
            tags="avatar"
        )

    def _draw_tired_sequence(self, hat: CharacterHat):
        """Draw tired action sequence - sitting down"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Draw humanoid in sitting position
        # Head (tilted)
        head_y = center_y - 20
        self.canvas.create_oval(
            center_x - 12, head_y - 12,
            center_x + 12, head_y + 12,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Body (leaning back)
        body_y = center_y + 5
        self.canvas.create_rectangle(
            center_x - 10, body_y,
            center_x + 10, body_y + 25,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Legs (bent, sitting)
        self.canvas.create_line(
            center_x - 5, body_y + 25,
            center_x - 8, body_y + 35,
            fill=hat.secondary_color, width=3, tags="avatar"
        )
        self.canvas.create_line(
            center_x + 5, body_y + 25,
            center_x + 8, body_y + 35,
            fill=hat.secondary_color, width=3, tags="avatar"
        )

    def _draw_napping_sequence(self, hat: CharacterHat):
        """Draw napping action sequence - with snot bubble"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Draw humanoid lying down/napping
        # Head (lying down)
        head_y = center_y - 15
        self.canvas.create_oval(
            center_x - 12, head_y - 12,
            center_x + 12, head_y + 12,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Snot bubble (animated - grows and shrinks)
        bubble_size = 3 + 2 * math.sin(self.action_sequence_frame * 0.2)
        bubble_x = center_x + 15
        bubble_y = head_y - 5
        self.canvas.create_oval(
            bubble_x - bubble_size, bubble_y - bubble_size,
            bubble_x + bubble_size, bubble_y + bubble_size,
            fill="#ffffff", outline=hat.primary_color, width=1,
            tags="avatar"
        )

        # Body (horizontal, lying)
        body_y = center_y + 5
        self.canvas.create_rectangle(
            center_x - 15, body_y,
            center_x + 15, body_y + 15,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

    def _draw_iron_man_humanoid(self, hat: CharacterHat):
        """Draw JARVIS humanoid form - animated, like ACE when active"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Animated humanoid form (like ACE)
        # Use animation frame for movement
        self.humanoid_animation_frame += 1
        bounce = math.sin(self.humanoid_animation_frame * 0.1) * 2  # Subtle bounce

        # Head/Helmet
        head_y = center_y - 25 + bounce
        head_radius = 15
        self.canvas.create_oval(
            center_x - head_radius, head_y - head_radius,
            center_x + head_radius, head_y + head_radius,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # HUD display in helmet
        hud_size = head_radius * 0.6
        self.canvas.create_rectangle(
            center_x - hud_size, head_y - hud_size * 0.5,
            center_x + hud_size, head_y + hud_size * 0.5,
            fill="#000000", outline=hat.primary_color, width=1,
            tags="avatar"
        )

        # Body/Torso
        body_y = center_y + 5 + bounce
        body_width = 20
        body_height = 30
        self.canvas.create_rectangle(
            center_x - body_width//2, body_y,
            center_x + body_width//2, body_y + body_height,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Arc reactor in chest
        reactor_y = body_y + 8
        reactor_radius = 6
        self.canvas.create_oval(
            center_x - reactor_radius, reactor_y - reactor_radius,
            center_x + reactor_radius, reactor_y + reactor_radius,
            fill="#ffffff", outline=hat.primary_color, width=1,
            tags="avatar"
        )

        # Arms (animated)
        arm_swing = math.sin(self.humanoid_animation_frame * 0.15) * 8
        # Left arm
        self.canvas.create_line(
            center_x - body_width//2, body_y + 10,
            center_x - body_width//2 - 12, body_y + 25 + arm_swing,
            fill=hat.secondary_color, width=3, tags="avatar"
        )
        # Right arm
        self.canvas.create_line(
            center_x + body_width//2, body_y + 10,
            center_x + body_width//2 + 12, body_y + 25 - arm_swing,
            fill=hat.secondary_color, width=3, tags="avatar"
        )

        # Legs (animated walking)
        leg_swing = math.sin(self.humanoid_animation_frame * 0.2) * 5
        # Left leg
        self.canvas.create_line(
            center_x - 5, body_y + body_height,
            center_x - 8, body_y + body_height + 20 + leg_swing,
            fill=hat.secondary_color, width=3, tags="avatar"
        )
        # Right leg
        self.canvas.create_line(
            center_x + 5, body_y + body_height,
            center_x + 8, body_y + body_height + 20 - leg_swing,
            fill=hat.secondary_color, width=3, tags="avatar"
        )

    def _draw_ultron_avatar(self, hat: CharacterHat):
        """Draw Ultron style avatar"""
        center_x = self.size // 2
        center_y = self.size // 2
        radius = self.size // 3

        # Red glowing core
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Angular features
        for i in range(6):
            angle = i * 60
            x1 = center_x + math.cos(math.radians(angle)) * radius * 0.7
            y1 = center_y + math.sin(math.radians(angle)) * radius * 0.7
            x2 = center_x + math.cos(math.radians(angle)) * radius
            y2 = center_y + math.sin(math.radians(angle)) * radius
            self.canvas.create_line(x1, y1, x2, y2, fill=hat.secondary_color, width=2, tags="avatar")

    def _draw_ace_humanoid_avatar(self, hat: CharacterHat):
        """Draw ACE humanoid style avatar"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Humanoid body outline
        # Head
        self.canvas.create_oval(
            center_x - 15, center_y - 30,
            center_x + 15, center_y - 10,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Body
        self.canvas.create_rectangle(
            center_x - 12, center_y - 10,
            center_x + 12, center_y + 20,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

        # Arms
        self.canvas.create_line(
            center_x - 12, center_y,
            center_x - 20, center_y + 10,
            fill=hat.secondary_color, width=2, tags="avatar"
        )
        self.canvas.create_line(
            center_x + 12, center_y,
            center_x + 20, center_y + 10,
            fill=hat.secondary_color, width=2, tags="avatar"
        )

        # Legs
        self.canvas.create_line(
            center_x - 6, center_y + 20,
            center_x - 8, center_y + 35,
            fill=hat.secondary_color, width=2, tags="avatar"
        )
        self.canvas.create_line(
            center_x + 6, center_y + 20,
            center_x + 8, center_y + 35,
            fill=hat.secondary_color, width=2, tags="avatar"
        )

    def _draw_jedi_avatar(self, hat: CharacterHat):
        """Draw Jedi style avatar"""
        center_x = self.size // 2
        center_y = self.size // 2

        # Lightsaber hilt
        self.canvas.create_rectangle(
            center_x - 3, center_y - 20,
            center_x + 3, center_y + 20,
            fill="#444444", outline="#222222", width=1,
            tags="avatar"
        )

        # Lightsaber blade
        self.canvas.create_line(
            center_x, center_y - 20,
            center_x, center_y - 40,
            fill=hat.primary_color, width=4,
            tags="avatar"
        )

        # Jedi robe outline
        self.canvas.create_arc(
            center_x - 20, center_y,
            center_x + 20, center_y + 40,
            start=0, extent=180, style=tk.ARC,
            outline=hat.secondary_color, width=2,
            tags="avatar"
        )

    def _draw_default_avatar(self, hat: CharacterHat):
        """Draw default avatar"""
        center_x = self.size // 2
        center_y = self.size // 2
        radius = self.size // 3

        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=hat.primary_color, outline=hat.secondary_color, width=2,
            tags="avatar"
        )

    def smooth_interpolate_position(self):
        """Smooth interpolation to target position (ACE-like)"""
        if not self.smooth_interpolation:
            self.x = self.target_x
            self.y = self.target_y
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        self.x += dx * self.interpolation_factor
        self.y += dy * self.interpolation_factor

        # Update window position
        if self.root and self.root.winfo_exists():
            self.root.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")

    def _update_random_wander(self):
        """Update random wandering movement - moves JARVIS around the desktop"""
        current_time = time.time()

        # Check if we need a new target
        if (self.wander_target_x is None or self.wander_target_y is None or
            current_time - getattr(self, '_last_wander_update', 0) > self.wander_update_interval):

            # Pick a new random target
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, 300)  # Wander 100-300 pixels at a time

            new_x = self.x + math.cos(angle) * distance
            new_y = self.y + math.sin(angle) * distance

            # Clamp to screen bounds with margin
            margin = self.size + 20
            self.wander_target_x = max(margin, min(new_x, self.screen_width - margin))
            self.wander_target_y = max(margin, min(new_y, self.screen_height - margin))

            self._last_wander_update = current_time

        # Check if we've reached the target
        distance_to_target = math.sqrt(
            (self.wander_target_x - self.x) ** 2 + (self.wander_target_y - self.y) ** 2
        )

        if distance_to_target < 10:  # Close enough, pick new target next time
            self.wander_target_x = None
            self.wander_target_y = None

        # Set target for smooth interpolation
        if self.wander_target_x is not None:
            self.target_x = self.wander_target_x
            self.target_y = self.wander_target_y

    def calculate_wander_target(self):
        """Calculate wander target"""
        if self.wander_target_x is None or self.wander_target_y is None:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.wander_target_distance * 0.3, self.wander_target_distance)
            self.wander_target_x = self.x + math.cos(angle) * distance
            self.wander_target_y = self.y + math.sin(angle) * distance

            # Clamp to screen bounds
            self.wander_target_x = max(self.size, min(self.wander_target_x, self.screen_width - self.size))
            self.wander_target_y = max(self.size, min(self.wander_target_y, self.screen_height - self.size))

        distance_to_target = math.sqrt(
            (self.wander_target_x - self.x) ** 2 + (self.wander_target_y - self.y) ** 2
        )

        if distance_to_target < 5:
            self.wander_target_x = None
            self.wander_target_y = None

        self.target_x = self.wander_target_x
        self.target_y = self.wander_target_y

    def walk_border_smooth(self):
        """Walk along screen border with smooth interpolation"""
        if self.state == JARVISState.IDLE:
            self.state = JARVISState.WANDERING

        self.target_border_position += self.walk_direction * self.border_walk_speed * 0.005
        self.border_position += (self.target_border_position - self.border_position) * self.interpolation_factor

        if self.border_position >= 1.0:
            self.border_position = 1.0
            self.target_border_position = 1.0
            self.walk_direction = -1
            self._switch_border()
        elif self.border_position <= 0.0:
            self.border_position = 0.0
            self.target_border_position = 0.0
            self.walk_direction = 1
            self._switch_border()

        x, y = self._calculate_border_position()
        self.target_x = x
        self.target_y = y

    def _calculate_border_position(self) -> Tuple[int, int]:
        """Calculate position along screen border"""
        x, y = 0, 0

        if self.current_border == BorderPosition.TOP:
            x = int(self.border_position * self.screen_width)
            y = 0
        elif self.current_border == BorderPosition.RIGHT:
            y = int(self.border_position * self.screen_height)
            x = self.screen_width - self.size
        elif self.current_border == BorderPosition.BOTTOM:
            x = int((1.0 - self.border_position) * self.screen_width)
            y = self.screen_height - self.size
        elif self.current_border == BorderPosition.LEFT:
            x = 0
            y = int((1.0 - self.border_position) * self.screen_height)

        return x, y

    def _switch_border(self):
        """Switch to next border"""
        borders = [BorderPosition.TOP, BorderPosition.RIGHT, BorderPosition.BOTTOM, BorderPosition.LEFT]
        current_index = borders.index(self.current_border)
        self.current_border = borders[(current_index + 1) % len(borders)]
        self.border_position = 0.0
        self.target_border_position = 0.0

    def _on_click(self, event):
        """Handle click - toggle collapse/expand"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()

    def animate(self):
        """Animate JARVIS - called by tkinter after() callback"""
        if not self.running or not self.root:
            return

        try:
            # Update animation frame
            self.animation_frame += 1

            # Check for action sequences (like ACE getting tired)
            self._check_action_sequences()

            # Update action sequence frame if active
            if self.action_sequence_active:
                self.action_sequence_frame += 1

            # Update wandering (only in humanoid mode)
            if self.current_mode == "humanoid" and self.wander_enabled and self.state == JARVISState.HUMANOID:
                # Use random wandering (NOT border walking)
                self._update_random_wander()

            # Smooth interpolation (only when moving)
            if self.current_mode == "humanoid" and not self.action_sequence_active:
                self.smooth_interpolate_position()

            # Redraw avatar (always - for animation)
            self._redraw_avatar()

            # Schedule next animation frame
            interval = self.animation_frame_time
            if self.root and self.root.winfo_exists():
                self.root.after(int(interval * 1000), self.animate)
        except tk.TclError:
            # Window was destroyed
            self.running = False
        except Exception as e:
            logger.error(f"Error in animate: {e}", exc_info=True)
            # Try to continue anyway
            if self.root and self.root.winfo_exists():
                interval = self.animation_frame_time
                self.root.after(int(interval * 1000), self.animate)

    def start(self):
        """Start JARVIS wandering - RESTORE WORKING PATTERN (like Kenny)"""
        logger.info("🚀 Starting JARVIS...")
        self.create_window()
        self.running = True

        # Start collapsed (sleeping) - user can expand to activate
        # Or start expanded if you want it active immediately
        # self.expand()  # Uncomment to start active

        # Start animation loop using tkinter after() callback
        self.animate()

        # Run tkinter mainloop (blocking - this is required)
        self.root.mainloop()

    def stop(self):
        """Stop JARVIS wandering"""
        self.running = False
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
        logger.info("⏹️  JARVIS wandering stopped")


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Wandering System")
    parser.add_argument("--hat", type=str, help="Character hat ID to use")
    parser.add_argument("--size", type=int, default=120, help="Window size")
    args = parser.parse_args()

    jarvis = JARVISWanderingSystem(
        character_hat=args.hat,
        size=args.size
    )

    jarvis.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping JARVIS...")
        jarvis.stop()


if __name__ == "__main__":


    main()