#!/usr/bin/env python3
"""
Kenny (@IMVA) - Rebuilt Desktop Virtual Assistant

Rebuilt Kenny as a desktop assistant that:
- Walks around screen borders (like Armoury Crate)
- Multiple actions (interactive, responsive)
- Appears alive (animated, responsive to events)
- Real-time notifications (tells you at moment's notice)
- Freeze detection (handles stress/overload like humans/computers)
- Integration with Lumina ecosystem

"We have the technology. We can rebuild him."

Tags: #KENNY #IMVA #DESKTOP_ASSISTANT #ARMOURY_CRATE @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
import random
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

logger = get_logger("KennyIMVA")

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


class KennyState(Enum):
    """Kenny's current state"""
    IDLE = "idle"
    WALKING = "walking"
    NOTIFYING = "notifying"
    ACTING = "acting"
    FROZEN = "frozen"
    RECOVERING = "recovering"


class BorderPosition(Enum):
    """Screen border positions"""
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"


@dataclass
class Notification:
    """Real-time notification"""
    message: str
    priority: str = "normal"  # low, normal, high, critical
    timestamp: datetime = field(default_factory=datetime.now)
    action: Optional[str] = None
    dismissed: bool = False


@dataclass
class Action:
    """Kenny action"""
    action_id: str
    name: str
    description: str
    icon: str = "⚡"
    enabled: bool = True


class KennyIMVA:
    """
    Kenny (@IMVA) - Rebuilt Desktop Virtual Assistant

    Walks around screen borders, provides real-time notifications,
    handles multiple actions, appears alive, detects freezes.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Kenny"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "kenny_imva"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not TKINTER_AVAILABLE:
            raise ImportError("tkinter is required for Kenny")

        # State
        self.state = KennyState.IDLE
        self.frozen = False
        self.freeze_count = 0
        self.last_activity = time.time()
        self.stress_level = 0.0  # 0.0 to 1.0

        # Screen borders walking
        self.current_border = BorderPosition.TOP
        self.border_position = 0.0  # 0.0 to 1.0 along border
        self.walk_speed = 0.5  # pixels per frame
        self.walk_direction = 1  # 1 or -1

        # Window setup
        self.root = None
        self.canvas = None
        self.kenny_sprite = None
        self.size = 60  # Kenny size

        # Screen dimensions
        self.screen_width = 1920
        self.screen_height = 1080

        # Notifications
        self.notifications: List[Notification] = []
        self.max_notifications = 5
        self.current_notification = None

        # Actions
        self.actions: List[Action] = [
            Action("status", "System Status", "Check system status", "📊"),
            Action("alerts", "View Alerts", "View all alerts", "🔔"),
            Action("help", "Help", "Get help", "❓"),
            Action("settings", "Settings", "Open settings", "⚙️"),
        ]

        # Freeze detection
        self.freeze_threshold = 5.0  # seconds of no activity = freeze
        self.last_update_time = time.time()
        self.update_interval = 0.1  # 10 FPS

        # Animation
        self.animation_frame = 0
        self.idle_animation_speed = 0.1

        # Integration
        self.jarvis_integration = None
        self.adaptive_collab = None

        # Load integrations
        self._load_integrations()

        logger.info("=" * 80)
        logger.info("🔧 KENNY (@IMVA) - REBUILT")
        logger.info("   'We have the technology. We can rebuild him.'")
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

    def _load_integrations(self):
        """Load Lumina ecosystem integrations"""
        # JARVIS integration
        try:
            from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
            self.jarvis_integration = JARVISHelpdeskIntegration(self.project_root)
            logger.info("✅ JARVIS integration loaded")
        except Exception as e:
            logger.debug(f"JARVIS integration not available: {e}")

        # Adaptive collaboration system
        try:
            from adaptive_collaboration_system import AdaptiveCollaborationSystem
            self.adaptive_collab = AdaptiveCollaborationSystem(self.project_root)
            logger.info("✅ Adaptive collaboration system loaded")
        except Exception as e:
            logger.debug(f"Adaptive collaboration not available: {e}")

    def create_window(self):
        """Create Kenny's window"""
        self.root = tk.Tk()
        self.root.title("Kenny (@IMVA) - Desktop Assistant")
        self.root.overrideredirect(True)  # No window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-transparentcolor', 'black')  # Transparent background

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Set window size
        window_size = self.size + 20  # Add padding
        self.root.geometry(f"{window_size}x{window_size}+0+0")

        # Create canvas
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

        # Start animation loop
        self.animate()

        logger.info(f"✅ Kenny window created ({self.screen_width}x{self.screen_height})")

    def calculate_border_position(self) -> Tuple[int, int]:
        """Calculate position along screen border"""
        border_length = 0
        x, y = 0, 0

        if self.current_border == BorderPosition.TOP:
            border_length = self.screen_width
            x = int(self.border_position * border_length)
            y = 0
        elif self.current_border == BorderPosition.RIGHT:
            border_length = self.screen_height
            x = self.screen_width - self.size
            y = int(self.border_position * border_length)
        elif self.current_border == BorderPosition.BOTTOM:
            border_length = self.screen_width
            x = int((1.0 - self.border_position) * border_length)
            y = self.screen_height - self.size
        elif self.current_border == BorderPosition.LEFT:
            border_length = self.screen_height
            x = 0
            y = int((1.0 - self.border_position) * border_length)

        return x, y

    def walk_border(self):
        """Walk along screen border"""
        if self.state == KennyState.FROZEN:
            return

        # Update border position
        self.border_position += self.walk_direction * self.walk_speed * 0.01

        # Check if reached end of border
        if self.border_position >= 1.0:
            self.border_position = 1.0
            self.walk_direction = -1
            self._switch_border()
        elif self.border_position <= 0.0:
            self.border_position = 0.0
            self.walk_direction = 1
            self._switch_border()

        # Update position
        x, y = self.calculate_border_position()
        self.root.geometry(f"{self.size + 20}x{self.size + 20}+{x}+{y}")

    def _switch_border(self):
        """Switch to next border"""
        borders = list(BorderPosition)
        current_index = borders.index(self.current_border)
        next_index = (current_index + 1) % len(borders)
        self.current_border = borders[next_index]
        self.border_position = 0.0 if self.walk_direction == 1 else 1.0
        logger.debug(f"Switched to {self.current_border.value} border")

    def draw_kenny(self):
        """Draw Kenny sprite"""
        self.canvas.delete("all")

        center_x = (self.size + 20) // 2
        center_y = (self.size + 20) // 2

        # Draw Kenny (simple circle for now, can be enhanced with image)
        if PIL_AVAILABLE:
            # Use PIL for better rendering
            img = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Draw Kenny body (orange parka)
            draw.ellipse(
                [10, 10, self.size - 10, self.size - 10],
                fill=(255, 140, 0, 255),  # Orange
                outline=(139, 69, 19, 255),  # Brown outline
                width=2
            )

            # Draw face (covered by hood - black)
            draw.ellipse(
                [20, 20, self.size - 20, self.size - 20],
                fill=(0, 0, 0, 255),  # Black
                outline=(255, 215, 0, 255),  # Gold zipper
                width=1
            )

            # Convert to PhotoImage
            self.kenny_photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(center_x, center_y, image=self.kenny_photo)
        else:
            # Fallback to tkinter drawing
            self.canvas.create_oval(
                center_x - self.size // 2,
                center_y - self.size // 2,
                center_x + self.size // 2,
                center_y + self.size // 2,
                fill="#FF8C00",  # Orange
                outline="#8B4513",  # Brown
                width=2
            )
            # Face (covered)
            self.canvas.create_oval(
                center_x - self.size // 3,
                center_y - self.size // 3,
                center_x + self.size // 3,
                center_y + self.size // 3,
                fill="#000000",  # Black
                outline="#FFD700",  # Gold
                width=1
            )

        # Draw notification indicator if active
        if self.current_notification:
            self.canvas.create_oval(
                center_x + self.size // 3,
                center_y - self.size // 3,
                center_x + self.size // 3 + 10,
                center_y - self.size // 3 + 10,
                fill="#FF0000",  # Red dot
                outline="#FFFFFF",
                width=1
            )

        # Draw freeze indicator if frozen
        if self.frozen:
            self.canvas.create_text(
                center_x,
                center_y + self.size // 2 + 15,
                text="❄️ FROZEN",
                fill="#00BFFF",
                font=("Arial", 8)
            )

    def check_freeze(self):
        """Check if Kenny is frozen"""
        current_time = time.time()
        time_since_update = current_time - self.last_update_time

        if time_since_update > self.freeze_threshold:
            if not self.frozen:
                self.frozen = True
                self.freeze_count += 1
                self.state = KennyState.FROZEN
                logger.warning(f"⚠️  Kenny frozen! (freeze #{self.freeze_count})")
                self.add_notification("Kenny detected a freeze. Recovering...", "high")
                # Start recovery
                threading.Timer(2.0, self.recover_from_freeze).start()
        else:
            if self.frozen and self.state == KennyState.RECOVERING:
                # Recovery in progress
                pass
            elif self.frozen:
                # Should be recovering
                self.state = KennyState.RECOVERING

    def recover_from_freeze(self):
        """Recover from freeze"""
        logger.info("🔄 Kenny recovering from freeze...")
        self.frozen = False
        self.state = KennyState.IDLE
        self.last_update_time = time.time()
        self.stress_level = max(0.0, self.stress_level - 0.2)
        self.add_notification("Kenny recovered from freeze!", "normal")

    def add_notification(self, message: str, priority: str = "normal"):
        """Add a real-time notification"""
        notification = Notification(
            message=message,
            priority=priority,
            timestamp=datetime.now()
        )
        self.notifications.append(notification)

        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)

        # Set as current if high priority
        if priority in ["high", "critical"]:
            self.current_notification = notification
            self.state = KennyState.NOTIFYING

        logger.info(f"📢 Notification: {message} (priority: {priority})")

        # Auto-dismiss after delay
        if priority == "normal":
            threading.Timer(5.0, lambda: self.dismiss_notification(notification)).start()

    def dismiss_notification(self, notification: Notification):
        """Dismiss a notification"""
        notification.dismissed = True
        if self.current_notification == notification:
            self.current_notification = None
            if self.state == KennyState.NOTIFYING:
                self.state = KennyState.IDLE

    def on_click(self, event):
        """Handle click on Kenny"""
        # Show actions menu or perform action
        logger.info("👆 Kenny clicked!")
        self.add_notification("Kenny is here! What can I help with?", "normal")

    def on_drag(self, event):
        """Handle drag"""
        # Allow manual repositioning
        x = self.root.winfo_x() + event.x
        y = self.root.winfo_y() + event.y
        self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        """Handle release"""
        pass

    def animate(self):
        """Main animation loop"""
        current_time = time.time()

        # Check for freeze
        self.check_freeze()

        if not self.frozen:
            # Update last activity
            self.last_update_time = current_time

            # Walk border
            if self.state in [KennyState.IDLE, KennyState.WALKING]:
                self.walk_border()
                self.state = KennyState.WALKING

            # Update animation frame
            self.animation_frame += self.idle_animation_speed

        # Draw Kenny
        self.draw_kenny()

        # Schedule next frame
        self.root.after(int(self.update_interval * 1000), self.animate)

    def start(self):
        """Start Kenny"""
        logger.info("🚀 Starting Kenny...")
        self.create_window()
        self.root.mainloop()

    def stop(self):
        """Stop Kenny"""
        logger.info("🛑 Stopping Kenny...")
        if self.root:
            self.root.quit()


def main():
    """Main execution"""
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

    parser = argparse.ArgumentParser(description="Kenny (@IMVA) - Rebuilt Desktop Assistant")
    parser.add_argument('--test', action='store_true', help='Test mode')

    args = parser.parse_args()

    kenny = KennyIMVA()

    if args.test:
        print("🧪 Test mode - Kenny will start and run for 10 seconds")
        threading.Timer(10.0, kenny.stop).start()

    try:
        kenny.start()
    except KeyboardInterrupt:
        kenny.stop()


if __name__ == "__main__":


    main()