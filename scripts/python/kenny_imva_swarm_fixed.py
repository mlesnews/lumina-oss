#!/usr/bin/env python3
"""
Kenny (@IMVA) - Swarm Collaboration Fixed Version

Fixed rendering to prevent stacking/clustering.
Supports swarm collaboration - multiple avatars can coexist:
- Kenny (Iron Man Virtual Assistant)
- Iron Man Mark models
- Mace Windu
- Tony Stark
- Jarvis
- Anyone can pop into the room

Tags: #KENNY #IMVA #SWARM #COLLABORATION #FIXED @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

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

logger = get_logger("KennyIMVASwarm")

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


class AvatarType(Enum):
    """Avatar types in the swarm"""
    KENNY = "kenny"  # Iron Man Virtual Assistant (looks like Kenny)
    IRON_MAN_MARK_I = "iron_man_mark_i"
    IRON_MAN_MARK_II = "iron_man_mark_ii"
    IRON_MAN_MARK_III = "iron_man_mark_iii"
    MACE_WINDU = "mace_windu"
    TONY_STARK = "tony_stark"
    JARVIS = "jarvis"


@dataclass
class Avatar:
    """Avatar in the swarm"""
    avatar_id: str
    avatar_type: AvatarType
    name: str
    position: Tuple[int, int]
    size: int = 60
    active: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class SwarmCollaborationManager:
    """
    Manages swarm of avatars - prevents stacking, enables collaboration

    Multiple avatars can coexist:
    - Each has unique position
    - No stacking/clustering
    - Anyone can pop in
    - Swarm collaborative development
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize swarm manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "swarm_avatars"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Active avatars
        self.avatars: Dict[str, Avatar] = {}
        self.avatar_windows: Dict[str, tk.Tk] = {}

        # Positioning system (prevents stacking)
        self.min_spacing = 80  # Minimum distance between avatars
        self.used_positions: List[Tuple[int, int]] = []

        # Screen dimensions
        self.screen_width = 1920
        self.screen_height = 1080

        logger.info("=" * 80)
        logger.info("🐝 SWARM COLLABORATION MANAGER INITIALIZED")
        logger.info("   Multiple avatars can coexist - no stacking!")
        logger.info("=" * 80)

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

    def calculate_spaced_position(self, size: int) -> Tuple[int, int]:
        """Calculate position that doesn't stack with existing avatars"""
        import random

        max_attempts = 50
        for attempt in range(max_attempts):
            # Try random position
            x = random.randint(size, self.screen_width - size)
            y = random.randint(size, self.screen_height - size)

            # Check if too close to existing avatars
            too_close = False
            for pos in self.used_positions:
                distance = ((x - pos[0])**2 + (y - pos[1])**2)**0.5
                if distance < self.min_spacing:
                    too_close = True
                    break

            if not too_close:
                self.used_positions.append((x, y))
                return x, y

        # Fallback: Use grid positioning
        grid_size = int((self.screen_width * self.screen_height) ** 0.5 / 10)
        grid_x = (len(self.used_positions) % grid_size) * self.min_spacing
        grid_y = (len(self.used_positions) // grid_size) * self.min_spacing
        pos = (grid_x + size, grid_y + size)
        self.used_positions.append(pos)
        return pos

    def add_avatar(self, avatar_type: AvatarType, name: Optional[str] = None) -> str:
        """Add avatar to swarm"""
        avatar_id = f"{avatar_type.value}_{int(time.time())}"

        if name is None:
            name = avatar_type.value.replace("_", " ").title()

        position = self.calculate_spaced_position(60)

        avatar = Avatar(
            avatar_id=avatar_id,
            avatar_type=avatar_type,
            name=name,
            position=position
        )

        self.avatars[avatar_id] = avatar
        logger.info(f"✅ Added avatar: {name} ({avatar_id}) at {position}")

        return avatar_id

    def remove_avatar(self, avatar_id: str):
        """Remove avatar from swarm"""
        if avatar_id in self.avatars:
            avatar = self.avatars[avatar_id]
            # Remove position from used positions
            if avatar.position in self.used_positions:
                self.used_positions.remove(avatar.position)

            # Close window if exists
            if avatar_id in self.avatar_windows:
                try:
                    self.avatar_windows[avatar_id].quit()
                    self.avatar_windows[avatar_id].destroy()
                except:
                    pass
                del self.avatar_windows[avatar_id]

            del self.avatars[avatar_id]
            logger.info(f"🗑️  Removed avatar: {avatar_id}")

    def get_avatar_count(self) -> int:
        """Get number of active avatars"""
        return len(self.avatars)

    def list_avatars(self) -> List[Dict[str, Any]]:
        """List all active avatars"""
        return [{
            "id": av.avatar_id,
            "type": av.avatar_type.value,
            "name": av.name,
            "position": av.position,
            "active": av.active
        } for av in self.avatars.values()]


class FixedKennyWindow:
    """
    Fixed Kenny window - proper rendering, no stacking

    FIXES:
    - Proper canvas clearing (delete all before redraw)
    - Single clean sprite (no multiple overlays)
    - Proper transparency handling
    - No clustering/stacking
    """

    def __init__(self, avatar: Avatar, swarm_manager: SwarmCollaborationManager):
        """Initialize fixed Kenny window"""
        self.avatar = avatar
        self.swarm_manager = swarm_manager

        if not TKINTER_AVAILABLE:
            raise ImportError("tkinter required")

        # Window setup
        self.root = None
        self.canvas = None
        self.size = avatar.size

        # Rendering state
        self.last_draw_time = 0
        self.draw_interval = 0.1  # 10 FPS

        # Create window
        self.create_window()

    def create_window(self):
        """Create window with proper setup"""
        self.root = tk.Tk()
        self.root.title(f"{self.avatar.name} (@IMVA)")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window size and position
        window_size = self.size + 20
        x, y = self.avatar.position

        # Ensure within screen bounds
        x = max(0, min(x, screen_width - window_size))
        y = max(0, min(y, screen_height - window_size))

        self.root.geometry(f"{window_size}x{window_size}+{x}+{y}")

        # Create canvas with proper background
        self.canvas = tk.Canvas(
            self.root,
            width=window_size,
            height=window_size,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()

        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Start animation
        self.animate()

        logger.info(f"✅ Created window for {self.avatar.name} at ({x}, {y})")

    def draw_avatar(self):
        """Draw avatar with proper clearing (FIXED - no stacking)"""
        # CRITICAL FIX: Delete ALL canvas items before redrawing
        # This prevents stacking/clustering
        self.canvas.delete("all")

        center_x = (self.size + 20) // 2
        center_y = (self.size + 20) // 2

        # Draw based on avatar type
        if self.avatar.avatar_type == AvatarType.KENNY:
            self._draw_kenny(center_x, center_y)
        elif self.avatar.avatar_type == AvatarType.IRON_MAN_MARK_I:
            self._draw_iron_man_mark(center_x, center_y, "I", "#FF6B35")
        elif self.avatar.avatar_type == AvatarType.IRON_MAN_MARK_II:
            self._draw_iron_man_mark(center_x, center_y, "II", "#FFD700")
        elif self.avatar.avatar_type == AvatarType.MACE_WINDU:
            self._draw_mace_windu(center_x, center_y)
        elif self.avatar.avatar_type == AvatarType.TONY_STARK:
            self._draw_tony_stark(center_x, center_y)
        elif self.avatar.avatar_type == AvatarType.JARVIS:
            self._draw_jarvis(center_x, center_y)
        else:
            # Default: simple circle
            self._draw_default(center_x, center_y)

    def _draw_kenny(self, x: int, y: int):
        """Draw Kenny (orange parka)"""
        if PIL_AVAILABLE:
            img = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Orange parka
            draw.ellipse(
                [10, 10, self.size - 10, self.size - 10],
                fill=(255, 140, 0, 255),  # Orange
                outline=(139, 69, 19, 255),  # Brown
                width=2
            )

            # Black face (covered)
            draw.ellipse(
                [20, 20, self.size - 20, self.size - 20],
                fill=(0, 0, 0, 255),
                outline=(255, 215, 0, 255),  # Gold zipper
                width=1
            )

            photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(x, y, image=photo, anchor="center")
            self.canvas.image = photo  # Keep reference
        else:
            # Fallback
            self.canvas.create_oval(
                x - self.size // 2, y - self.size // 2,
                x + self.size // 2, y + self.size // 2,
                fill="#FF8C00",
                outline="#8B4513",
                width=2
            )

    def _draw_iron_man_mark(self, x: int, y: int, mark: str, color: str):
        """Draw Iron Man Mark"""
        self.canvas.create_oval(
            x - self.size // 2, y - self.size // 2,
            x + self.size // 2, y + self.size // 2,
            fill=color,
            outline="#FFD700",
            width=2
        )
        self.canvas.create_text(x, y, text=mark, fill="#FFFFFF", font=("Arial", 10, "bold"))

    def _draw_mace_windu(self, x: int, y: int):
        """Draw Mace Windu"""
        self.canvas.create_oval(
            x - self.size // 2, y - self.size // 2,
            x + self.size // 2, y + self.size // 2,
            fill="#4B0082",  # Indigo
            outline="#000000",
            width=2
        )
        self.canvas.create_text(x, y, text="MW", fill="#FFFFFF", font=("Arial", 8, "bold"))

    def _draw_tony_stark(self, x: int, y: int):
        """Draw Tony Stark"""
        self.canvas.create_oval(
            x - self.size // 2, y - self.size // 2,
            x + self.size // 2, y + self.size // 2,
            fill="#FFD700",  # Gold
            outline="#FF6B35",
            width=2
        )
        self.canvas.create_text(x, y, text="TS", fill="#000000", font=("Arial", 8, "bold"))

    def _draw_jarvis(self, x: int, y: int):
        """Draw Jarvis"""
        self.canvas.create_oval(
            x - self.size // 2, y - self.size // 2,
            x + self.size // 2, y + self.size // 2,
            fill="#00BFFF",  # Deep sky blue
            outline="#FFFFFF",
            width=2
        )
        self.canvas.create_text(x, y, text="J", fill="#FFFFFF", font=("Arial", 10, "bold"))

    def _draw_default(self, x: int, y: int):
        """Default avatar"""
        self.canvas.create_oval(
            x - self.size // 2, y - self.size // 2,
            x + self.size // 2, y + self.size // 2,
            fill="#808080",
            outline="#000000",
            width=2
        )

    def animate(self):
        """Animation loop"""
        current_time = time.time()

        if current_time - self.last_draw_time >= self.draw_interval:
            self.draw_avatar()
            self.last_draw_time = current_time

        self.root.after(int(self.draw_interval * 1000), self.animate)

    def on_click(self, event):
        """Handle click"""
        logger.info(f"👆 {self.avatar.name} clicked!")

    def on_drag(self, event):
        """Handle drag"""
        x = self.root.winfo_x() + event.x
        y = self.root.winfo_y() + event.y
        self.root.geometry(f"+{x}+{y}")
        self.avatar.position = (x, y)

    def on_release(self, event):
        """Handle release"""
        pass


def main():
    """Main - test swarm collaboration"""
    import argparse

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONConfig = None
    DataSourceType = None

    parser = argparse.ArgumentParser(description="Kenny Swarm - Fixed, No Stacking")
    parser.add_argument('--add', type=str, help='Add avatar (kenny, iron_man, mace_windu, tony_stark, jarvis)')
    parser.add_argument('--list', action='store_true', help='List avatars')

    args = parser.parse_args()

    swarm = SwarmCollaborationManager()

    if args.add:
        avatar_map = {
            'kenny': AvatarType.KENNY,
            'iron_man': AvatarType.IRON_MAN_MARK_I,
            'mace_windu': AvatarType.MACE_WINDU,
            'tony_stark': AvatarType.TONY_STARK,
            'jarvis': AvatarType.JARVIS
        }

        if args.add.lower() in avatar_map:
            avatar_id = swarm.add_avatar(avatar_map[args.add.lower()])
            avatar = swarm.avatars[avatar_id]
            window = FixedKennyWindow(avatar, swarm)
            swarm.avatar_windows[avatar_id] = window.root
            window.root.mainloop()
        else:
            print(f"Unknown avatar: {args.add}")
            print(f"Available: {', '.join(avatar_map.keys())}")

    elif args.list:
        avatars = swarm.list_avatars()
        print(f"\n🐝 Active Avatars: {len(avatars)}")
        for av in avatars:
            print(f"  • {av['name']} ({av['type']}) at {av['position']}")

    else:
        # Default: Start Kenny
        avatar_id = swarm.add_avatar(AvatarType.KENNY, "Kenny")
        avatar = swarm.avatars[avatar_id]
        window = FixedKennyWindow(avatar, swarm)
        swarm.avatar_windows[avatar_id] = window.root
        window.root.mainloop()


if __name__ == "__main__":


    main()