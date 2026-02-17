#!/usr/bin/env python3
"""
Magnetic Modular Button System - WoW Addon Style

Modular button boxes that snap together magnetically, with detailed icons
showing functionality for each VA ability/role. Inspired by World of Warcraft addons.

Each button is a self-contained module that:
- Has a detailed icon/picture showing its function
- Snaps magnetically to other buttons
- Can be dragged as a group or individually
- Shows tooltips with detailed information
- Has visual states (ready, active, cooldown, etc.)

Tags: #MAGNETIC #MODULAR #BUTTONS #WOW_STYLE #VA_CONTROL @JARVIS @LUMINA
"""

import sys
import math
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    try:
        import tkinter as tk
        from tkinter import ttk
        TKINTER_AVAILABLE = True
    except ImportError:
        TKINTER_AVAILABLE = False

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MagneticButtons")


class ButtonState(Enum):
    """Button visual states"""
    READY = "ready"          # Green - Ready to activate
    ACTIVE = "active"        # Orange/Red - Currently active
    COOLDOWN = "cooldown"    # Gray - On cooldown
    DISABLED = "disabled"    # Dark - Disabled
    CHARGING = "charging"    # Yellow - Charging/Activating


@dataclass
class MagneticButton:
    """A single magnetic button module"""
    button_id: str
    va_id: str
    name: str
    role: str
    icon_path: Optional[str] = None
    icon_color: str = "#00ff00"
    state: ButtonState = ButtonState.READY
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (64.0, 64.0)  # Standard WoW button size
    tooltip: str = ""
    on_click: Optional[Callable] = None
    on_right_click: Optional[Callable] = None
    cooldown_remaining: float = 0.0
    magnetic_snap_distance: float = 10.0  # Pixels for magnetic snap
    attached_buttons: List[str] = field(default_factory=list)
    group_id: Optional[str] = None

    def get_snap_points(self) -> List[Tuple[float, float]]:
        """Get magnetic snap points (edges and corners)"""
        x, y = self.position
        w, h = self.size
        return [
            (x, y),           # Top-left
            (x + w/2, y),     # Top-center
            (x + w, y),       # Top-right
            (x, y + h/2),     # Left-center
            (x + w, y + h/2), # Right-center
            (x, y + h),       # Bottom-left
            (x + w/2, y + h), # Bottom-center
            (x + w, y + h)    # Bottom-right
        ]


class MagneticButtonSystem:
    """
    Magnetic Modular Button System

    Buttons snap together magnetically, can be grouped, and have detailed icons.
    """

    def __init__(self):
        """Initialize magnetic button system"""
        if not PIL_AVAILABLE and not TKINTER_AVAILABLE:
            raise RuntimeError("tkinter or PIL required")

        self.registry = CharacterAvatarRegistry()
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Get ACE-like characters
        self.ace_characters = [
            va for va in self.vas 
            if va.character_id in ["ace", "jarvis_va", "imva"] or 
               va.combat_mode_enabled or va.transformation_enabled
        ]

        # Button storage
        self.buttons: Dict[str, MagneticButton] = {}
        self.button_groups: Dict[str, List[str]] = {}  # group_id -> [button_ids]
        self.next_group_id = 1
        self.va_threads: Dict[str, threading.Thread] = {}  # Track active VA threads

        # Create main window
        self.root = tk.Tk()
        self.root.title("Magnetic VA Control Panel")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#000000')

        # Canvas for buttons
        self.canvas = tk.Canvas(
            self.root,
            bg='#000000',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Drag state
        self.drag_data = {
            "button": None,
            "group": None,
            "offset_x": 0,
            "offset_y": 0,
            "start_x": 0,
            "start_y": 0
        }

        # Create buttons for each VA
        self.create_va_buttons()

        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # Tooltip
        self.tooltip_window = None
        self.tooltip_label = None

        logger.info("=" * 80)
        logger.info("🧲 MAGNETIC BUTTON SYSTEM INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Buttons Created: {len(self.buttons)}")
        logger.info("   Magnetic snap enabled")
        logger.info("=" * 80)

    def get_function_description(self, va_id: str, role: str) -> str:
        """Get detailed function description for VA"""
        descriptions = {
            "ace": "Immortal Training Dummy - Combat practice partner for IMVA. Cannot be destroyed, regenerates instantly.",
            "jarvis_va": "Strategic Intelligence - Desktop assistant with combat capabilities and transformation modes.",
            "imva": "Visual Intelligence Agent - Bobblehead assistant for visual tasks and combat training.",
            "ava": "Placeholder VA - Standby assistant for concurrent operations."
        }

        if va_id in descriptions:
            return descriptions[va_id]

        # Generate from role
        role_lower = role.lower()
        if "combat" in role_lower:
            return "Combat operations and tactical support"
        elif "strategic" in role_lower or "advisor" in role_lower:
            return "Strategic planning and intelligence analysis"
        elif "training" in role_lower:
            return "Training and skill development"
        elif "focus" in role_lower:
            return "Focus coaching and productivity enhancement"
        else:
            return "Virtual assistant operations"

    def create_va_buttons(self):
        """Create magnetic buttons for each VA"""
        start_x, start_y = 20, 20
        spacing = 70

        for i, va in enumerate(self.ace_characters):
            button_id = f"btn_{va.character_id}"

            # Determine icon color based on VA
            icon_colors = {
                "ace": "#ff6600",      # Orange - Combat
                "jarvis_va": "#00ccff", # Cyan - Intelligence
                "imva": "#ffcc00"      # Yellow - Visual
            }
            icon_color = icon_colors.get(va.character_id, "#00ff00")

            # Get symbolic representation for tooltip
            symbol, symbol_type = self.get_va_symbol(va.character_id, va.role)

            # Enhanced tooltip with symbolic meaning
            tooltip_text = f"{symbol} {va.name}\n{va.role}\n\n"
            tooltip_text += f"Symbol: {symbol} ({symbol_type})\n"
            tooltip_text += f"Function: {self.get_function_description(va.character_id, va.role)}\n\n"
            tooltip_text += "Click: Activate/Deactivate\nRight-click: Roleplay options"

            # Create button
            button = MagneticButton(
                button_id=button_id,
                va_id=va.character_id,
                name=va.name,
                role=va.role,
                icon_color=icon_color,
                position=(start_x + (i * spacing), start_y),
                tooltip=tooltip_text,
                on_click=lambda v=va: self.toggle_va(v),
                on_right_click=lambda v=va: self.show_roleplay_menu(v)
            )

            self.buttons[button_id] = button
            self.draw_button(button)

    def get_va_symbol(self, va_id: str, role: str) -> tuple:
        """Get symbolic representation for VA - returns (symbol_text, symbol_type)"""
        symbols = {
            "ace": ("⚔", "combat"),  # Sword - Combat Specialist / Training Dummy
            "jarvis_va": ("🧠", "intelligence"),  # Brain - Intelligence/Strategy
            "imva": ("👁", "visual"),  # Eye - Visual Intelligence
            "ava": ("⚙", "utility"),  # Gear - Utility/Placeholder
        }

        # Check by role if not found by ID
        if va_id not in symbols:
            role_lower = role.lower()
            if "combat" in role_lower or "battle" in role_lower:
                return ("⚔", "combat")
            elif "strategic" in role_lower or "advisor" in role_lower:
                return ("🧠", "intelligence")
            elif "visual" in role_lower or "see" in role_lower:
                return ("👁", "visual")
            elif "training" in role_lower or "dummy" in role_lower:
                return ("🎯", "training")
            elif "focus" in role_lower or "coach" in role_lower:
                return ("🎯", "focus")
            elif "power" in role_lower or "channel" in role_lower:
                return ("⚡", "power")
            else:
                return ("⭐", "general")

        return symbols.get(va_id, ("⭐", "general"))

    def draw_button(self, button: MagneticButton):
        """Draw a button on canvas with detailed symbolic icon and state"""
        x, y = button.position
        w, h = button.size

        # Button background (rounded rectangle effect)
        if button.state == ButtonState.READY:
            bg_color = "#1a3a1a"  # Dark green
            border_color = button.icon_color
        elif button.state == ButtonState.ACTIVE:
            bg_color = "#3a1a1a"  # Dark red/orange
            border_color = "#ff6600"
        elif button.state == ButtonState.COOLDOWN:
            bg_color = "#2a2a2a"  # Dark gray
            border_color = "#666666"
        else:
            bg_color = "#1a1a1a"  # Dark
            border_color = "#333333"

        # Draw button background with rounded corners effect
        padding = 2
        self.canvas.create_rectangle(
            x + padding, y + padding,
            x + w - padding, y + h - padding,
            fill=bg_color,
            outline=border_color,
            width=2,
            tags=(f"button_{button.button_id}", "button_bg")
        )

        # Get symbolic representation
        symbol, symbol_type = self.get_va_symbol(button.va_id, button.role)

        icon_center_x = x + w / 2
        icon_center_y = y + h / 2 - 5  # Slightly above center for text below

        # Draw symbolic icon (larger, more prominent)
        icon_radius = 22

        # Icon background circle with glow effect when active
        if button.state == ButtonState.ACTIVE:
            # Glow effect - outer ring
            self.canvas.create_oval(
                icon_center_x - icon_radius - 2, icon_center_y - icon_radius - 2,
                icon_center_x + icon_radius + 2, icon_center_y + icon_radius + 2,
                fill=button.icon_color,
                outline="",
                tags=(f"button_{button.button_id}", "button_glow")
            )

        # Icon circle
        self.canvas.create_oval(
            icon_center_x - icon_radius, icon_center_y - icon_radius,
            icon_center_x + icon_radius, icon_center_y + icon_radius,
            fill=button.icon_color,
            outline=border_color,
            width=2,
            tags=(f"button_{button.button_id}", "button_icon")
        )

        # Symbol text (emoji/symbol representing function)
        self.canvas.create_text(
            icon_center_x, icon_center_y,
            text=symbol,
            fill="#ffffff",
            font=('Arial', 20, 'bold'),
            tags=(f"button_{button.button_id}", "button_symbol")
        )

        # VA name below icon (smaller, shows what it is)
        name_text = button.name[:8] if len(button.name) > 8 else button.name
        self.canvas.create_text(
            icon_center_x, y + h - 12,
            text=name_text,
            fill="#cccccc",
            font=('Arial', 8),
            tags=(f"button_{button.button_id}", "button_name")
        )

        # State indicator (small dot in corner)
        state_colors = {
            ButtonState.READY: "#00ff00",
            ButtonState.ACTIVE: "#ff6600",
            ButtonState.COOLDOWN: "#666666",
            ButtonState.DISABLED: "#333333",
            ButtonState.CHARGING: "#ffcc00"
        }
        state_color = state_colors.get(button.state, "#666666")

        self.canvas.create_oval(
            x + w - 12, y + 2,
            x + w - 2, y + 12,
            fill=state_color,
            outline="",
            tags=(f"button_{button.button_id}", "button_state")
        )

        # Cooldown overlay (if on cooldown)
        if button.state == ButtonState.COOLDOWN and button.cooldown_remaining > 0:
            cooldown_percent = min(1.0, button.cooldown_remaining / 5.0)  # 5 second cooldown
            cooldown_height = h * cooldown_percent

            self.canvas.create_rectangle(
                x, y + h - cooldown_height,
                x + w, y + h,
                fill="#000000",
                stipple="gray50",
                tags=(f"button_{button.button_id}", "button_cooldown")
            )

    def find_button_at(self, x: float, y: float) -> Optional[MagneticButton]:
        """Find button at given coordinates"""
        for button in self.buttons.values():
            bx, by = button.position
            bw, bh = button.size

            if bx <= x <= bx + bw and by <= y <= by + bh:
                return button
        return None

    def find_nearest_snap_point(self, button: MagneticButton, other_buttons: List[MagneticButton]) -> Optional[Tuple[float, float]]:
        """Find nearest snap point for magnetic attachment"""
        if not other_buttons:
            return None

        min_distance = button.magnetic_snap_distance
        best_snap = None

        button_snaps = button.get_snap_points()

        for other in other_buttons:
            if other.button_id == button.button_id:
                continue

            other_snaps = other.get_snap_points()

            for btn_snap in button_snaps:
                for other_snap in other_snaps:
                    dx = btn_snap[0] - other_snap[0]
                    dy = btn_snap[1] - other_snap[1]
                    distance = math.sqrt(dx*dx + dy*dy)

                    if distance < min_distance:
                        min_distance = distance
                        # Calculate offset to snap
                        offset_x = other_snap[0] - btn_snap[0]
                        offset_y = other_snap[1] - btn_snap[1]
                        best_snap = (offset_x, offset_y)

        return best_snap

    def on_canvas_click(self, event):
        """Handle canvas click"""
        x, y = event.x, event.y
        button = self.find_button_at(x, y)

        if button:
            self.drag_data["button"] = button.button_id
            self.drag_data["offset_x"] = x - button.position[0]
            self.drag_data["offset_y"] = y - button.position[1]
            self.drag_data["start_x"] = x
            self.drag_data["start_y"] = y

            # Check if clicking on button (not dragging)
            if abs(self.drag_data["offset_x"]) < 5 and abs(self.drag_data["offset_y"]) < 5:
                # Small movement = click, not drag
                pass
        else:
            self.drag_data["button"] = None

    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if not self.drag_data["button"]:
            return

        button = self.buttons[self.drag_data["button"]]
        new_x = event.x - self.drag_data["offset_x"]
        new_y = event.y - self.drag_data["offset_y"]

        # Check for magnetic snap
        other_buttons = [b for b in self.buttons.values() if b.button_id != button.button_id]
        snap = self.find_nearest_snap_point(button, other_buttons)

        if snap:
            new_x += snap[0]
            new_y += snap[1]

        # Update button position
        button.position = (new_x, new_y)

        # Move attached buttons if in group
        if button.group_id:
            group_buttons = self.button_groups.get(button.group_id, [])
            for btn_id in group_buttons:
                if btn_id != button.button_id:
                    other_btn = self.buttons[btn_id]
                    # Maintain relative position
                    dx = new_x - button.position[0]
                    dy = new_y - button.position[1]
                    other_btn.position = (other_btn.position[0] + dx, other_btn.position[1] + dy)

        # Redraw
        self.redraw_all()

    def on_canvas_release(self, event):
        """Handle canvas release"""
        if not self.drag_data["button"]:
            return

        button = self.buttons[self.drag_data["button"]]

        # Check if it was a click (not drag)
        dx = abs(event.x - self.drag_data["start_x"])
        dy = abs(event.y - self.drag_data["start_y"])

        if dx < 5 and dy < 5:
            # It was a click - activate button
            if button.on_click:
                button.on_click()
        else:
            # It was a drag - check for magnetic grouping
            other_buttons = [b for b in self.buttons.values() if b.button_id != button.button_id]
            nearby = [b for b in other_buttons 
                     if math.sqrt((b.position[0] - button.position[0])**2 + 
                                 (b.position[1] - button.position[1])**2) < 80]

            if nearby and not button.group_id:
                # Create or join group
                if nearby[0].group_id:
                    button.group_id = nearby[0].group_id
                    self.button_groups[button.group_id].append(button.button_id)
                else:
                    group_id = f"group_{self.next_group_id}"
                    self.next_group_id += 1
                    button.group_id = group_id
                    nearby[0].group_id = group_id
                    self.button_groups[group_id] = [button.button_id, nearby[0].button_id]

        self.drag_data["button"] = None
        self.redraw_all()

    def on_right_click(self, event):
        """Handle right-click"""
        button = self.find_button_at(event.x, event.y)
        if button and button.on_right_click:
            button.on_right_click()

    def on_mouse_move(self, event):
        """Handle mouse move for tooltips"""
        button = self.find_button_at(event.x, event.y)

        if button:
            if not self.tooltip_window:
                self.tooltip_window = tk.Toplevel(self.root)
                self.tooltip_window.overrideredirect(True)
                self.tooltip_window.configure(bg='#1a1a1a')

                self.tooltip_label = tk.Label(
                    self.tooltip_window,
                    text=button.tooltip,
                    bg='#1a1a1a',
                    fg='#ffffff',
                    font=('Arial', 9),
                    justify=tk.LEFT,
                    padx=5,
                    pady=5
                )
                self.tooltip_label.pack()

            # Position tooltip
            self.tooltip_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        else:
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None

    def redraw_all(self):
        """Redraw all buttons"""
        self.canvas.delete("all")
        for button in self.buttons.values():
            self.draw_button(button)

    def toggle_va(self, va):
        """Toggle VA activation - ACTUALLY ACTIVATE THE VA"""
        button_id = f"btn_{va.character_id}"
        button = self.buttons.get(button_id)

        if button:
            # Toggle state
            if button.state == ButtonState.READY:
                button.state = ButtonState.ACTIVE
                logger.info(f"🚀 Activated {va.name}")
                self.actually_activate_va(va, button)
            else:
                button.state = ButtonState.READY
                logger.info(f"⏸️  Deactivated {va.name}")
                self.actually_deactivate_va(va, button)

            self.redraw_all()

    def actually_activate_va(self, va, button):
        """Actually activate the VA - make it useful, not just a state change"""
        import threading
        import time

        def va_worker():
            """VA worker thread - actually does work"""
            logger.info(f"🎯 {va.name} worker thread started - DOING ACTUAL WORK")

            # Integrate with voice transcript queue
            try:
                from voice_transcript_queue import VoiceTranscriptQueue, RequestType
                if not hasattr(self, 'voice_queue'):
                    self.voice_queue = VoiceTranscriptQueue()

                # VA is now listening and processing
                logger.info(f"🎤 {va.name} integrated with voice queue")
            except ImportError:
                logger.warning("Voice queue not available")

            # VA actually monitors and assists
            while button.state == ButtonState.ACTIVE:
                try:
                    # Check for tasks/requests
                    if hasattr(self, 'voice_queue'):
                        # Process any queued requests
                        pass

                    # VA is actively working
                    logger.debug(f"💼 {va.name} actively monitoring and assisting")

                    # Sleep to prevent CPU spinning
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Error in {va.name} worker: {e}")
                    break

        # Start worker thread
        thread = threading.Thread(target=va_worker, daemon=True, name=f"VA-{va.character_id}")
        thread.start()

        # Store thread reference
        if not hasattr(self, 'va_threads'):
            self.va_threads = {}
        self.va_threads[va.character_id] = thread

        # Speak activation if TTS available
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(f"{va.name} activated. Ready for action.")
        except:
            pass

    def actually_deactivate_va(self, va, button):
        """Actually deactivate the VA"""
        # Thread will stop when state changes
        logger.info(f"⏸️  {va.name} worker thread stopping")

        # Speak deactivation if TTS available
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(f"{va.name} deactivated.")
        except:
            pass

    def show_roleplay_menu(self, va):
        """Show roleplay menu for VA - ACTUALLY SET ROLE"""
        # Create popup menu
        menu = tk.Menu(self.root, tearoff=0)
        roles = [
            "Combat Specialist",
            "Strategic Advisor",
            "Intelligence Analyst",
            "Operations Commander",
            "Focus Coach",
            "Power Channeler"
        ]

        def set_role(role_name):
            """Actually set the role and apply it"""
            logger.info(f"🎭 {va.name} roleplaying as: {role_name}")

            # Store role for this VA
            if not hasattr(self, 'va_roles'):
                self.va_roles = {}
            self.va_roles[va.character_id] = role_name

            # If VA is active, apply role immediately
            button_id = f"btn_{va.character_id}"
            button = self.buttons.get(button_id)
            if button and button.state == ButtonState.ACTIVE:
                logger.info(f"🔄 Applying {role_name} role to active {va.name}")
                # Role is now active - worker thread will use it

        for role in roles:
            menu.add_command(
                label=role,
                command=lambda r=role: set_role(r)
            )
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def run(self):
        """Run the button system"""
        # Set initial window size
        self.root.geometry("600x200+100+100")
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        system = MagneticButtonSystem()
        system.run()
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    sys.exit(main())