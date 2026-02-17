#!/usr/bin/env python3
"""
Replika-Inspired VA Renderer

Beautiful, modern VA widgets inspired by Replika's design:
- Smooth animations and transitions
- Personality and emotional expressions
- Clean, modern UI
- Interactive avatars
- Status indicators with mood

Tags: #REPLIKA_INSPIRED #MODERN_UI #ANIMATIONS #PERSONALITY @JARVIS @LUMINA
"""

import sys
import math
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from va_desktop_visualization import VADesktopVisualization, VFXType, WidgetType
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
    import json
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Lazy import of VAVisibilitySystem to avoid circular import
# Import it inside functions where it's needed

logger = get_logger("ReplikaVAs")


class TransparencyHUD:
    """HUD for Model Transparency and Money Tachometer"""

    def __init__(self, root, project_root):
        self.root = root
        self.project_root = project_root
        self.status_file = project_root / "data" / "model_transparency" / "current_status.json"
        self.token_limit_percent = 98.0 # Hard-coded critical limit

        # UI Components
        self.container = None
        self.model_label = None
        self.cost_label = None
        self.tachometer_canvas = None
        self.activity_canvas = None

        # Data
        self.last_status = {}
        self.activity_history = []  # List of (is_local, timestamp)

        self.create_hud()
        self.start_monitoring()

    def create_hud(self):
        """Create the Transparency HUD"""
        # Position at top-right, near system clock area
        self.container = tk.Frame(
            self.root,
            bg="#0A0A0A",
            highlightbackground="#333333",
            highlightthickness=1,
            padx=10,
            pady=5
        )

        # Screen dimensions
        screen_width = self.root.winfo_screenwidth()
        self.container.place(x=screen_width - 450, y=10, width=400, height=80)

        # 1. Time and Activity Lines (5m green/red lines)
        left_pane = tk.Frame(self.container, bg="#0A0A0A")
        left_pane.pack(side=tk.LEFT, fill=tk.Y)

        self.time_label = tk.Label(
            left_pane,
            text="00:00:00",
            font=('Segoe UI', 14, 'bold'),
            bg="#0A0A0A",
            fg="#FFFFFF"
        )
        self.time_label.pack(anchor='w')

        self.activity_canvas = tk.Canvas(
            left_pane,
            width=100,
            height=20,
            bg="#0A0A0A",
            highlightthickness=0
        )
        self.activity_canvas.pack(anchor='w', pady=(2, 0))

        # 2. Model Name and AUTO Status
        mid_pane = tk.Frame(self.container, bg="#0A0A0A", padx=15)
        mid_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.model_label = tk.Label(
            mid_pane,
            text="AUTO/ULTRON",
            font=('Segoe UI', 10, 'bold'),
            bg="#0A0A0A",
            fg="#00D4FF"  # Local color
        )
        self.model_label.pack(anchor='w')

        self.mode_label = tk.Label(
            mid_pane,
            text="LOCAL FIRST ENFORCED",
            font=('Segoe UI', 7),
            bg="#0A0A0A",
            fg="#90a4ae"
        )
        self.mode_label.pack(anchor='w')

        # 3. Money Tachometer & Token Pool
        right_pane = tk.Frame(self.container, bg="#0A0A0A")
        right_pane.pack(side=tk.RIGHT, fill=tk.Y)

        self.token_pool_label = tk.Label(
            right_pane,
            text="TOKEN POOL: 98% (FATAL)",
            font=('Segoe UI', 7, 'bold'),
            bg="#0A0A0A",
            fg="#FF4444" # Critical Red
        )
        self.token_pool_label.pack(anchor='e')

        self.cost_label = tk.Label(
            right_pane,
            text="$0.000000",
            font=('Consolas', 12, 'bold'),
            bg="#0A0A0A",
            fg="#FFC857"
        )
        self.cost_label.pack(anchor='e')

        self.tachometer_canvas = tk.Canvas(
            right_pane,
            width=120,
            height=10,
            bg="#1A1A2E",
            highlightthickness=0
        )
        self.tachometer_canvas.pack(anchor='e', pady=2)

    def update_display(self):
        """Update HUD with live data"""
        # Update Time
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))

        # Load status
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    status = json.load(f)

                # Model Transparency
                active = status.get("active_model", {})
                display_name = active.get("display_name", "AUTO/ULTRON")
                is_local = active.get("is_local", True)

                self.model_label.config(
                    text=display_name,
                    fg="#00B894" if is_local else "#E74C3C" # Green vs Red
                )

                # Usage Stats (Money Tachometer)
                stats = status.get("usage_stats", {})
                total_cost = stats.get("total_cost_usd", 0.0)
                self.cost_label.config(text=f"${total_cost:.6f}")

                # Update Tachometer Visual (0 to $1.00 scale for visual)
                self.tachometer_canvas.delete("all")
                width = 120
                fill_width = min(width, (total_cost / 1.0) * width)
                self.tachometer_canvas.create_rectangle(0, 0, fill_width, 10, fill="#FFC857", outline="")

                # Activity Lines (Sparklines)
                self._update_activity_lines(is_local)

            except:
                pass

    def _update_activity_lines(self, is_local):
        """Render the 5m green/red activity lines"""
        self.activity_canvas.delete("all")
        # For demo, we just show a burst of lines
        for i in range(10):
            color = "#00B894" if is_local else "#E74C3C"
            h = 5 + (i % 3) * 4
            self.activity_canvas.create_line(i*10, 20, i*10, 20-h, fill=color, width=2)

    def start_monitoring(self):
        """Start background update loop"""
        def loop():
            while True:
                self.root.after(0, self.update_display)
                time.sleep(1)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()


class TransparencyHUD:
    """
    Real-time Model Transparency & Money Tachometer

    Shows:
    - Current active model (AUTO detection)
    - Token usage percentage
    - Money tachometer ($USD spent)
    - Cloud vs Local activity signals
    """

    def __init__(self):
        self.transparency_data = self._load_transparency_data()
        self.token_pool_limit = 99  # Current limit percentage
        self.current_model = "ULTRON_CLUSTER"
        self.total_spend = 0.0

    def _load_transparency_data(self) -> Dict[str, Any]:
        """Load current transparency status"""
        try:
            status_file = Path("data/model_transparency/current_status.json")
            if status_file.exists():
                with open(status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load transparency data: {e}")
        return {}

    def get_transparency_status(self) -> Dict[str, Any]:
        """Get current transparency metrics"""
        return {
            "current_model": self.current_model,
            "token_usage_percent": self._get_token_usage(),
            "total_spend_usd": self.total_spend,
            "cloud_blocked": True,
            "local_active": True,
            "model_type": "LOCAL" if "ULTRON" in self.current_model else "CLOUD",
            "activity_signals": self._get_activity_signals()
        }

    def _get_token_usage(self) -> int:
        """Get current token usage percentage"""
        # Implementation would read from actual usage tracking
        return 99  # Current critical level

    def _get_activity_signals(self) -> Dict[str, Any]:
        """Get activity signal data for dashboard"""
        return {
            "green_lines": 5,  # Local activity (last 5 minutes)
            "red_lines": 0,    # Cloud activity (should be 0)
            "signal_strength": "STRONG_LOCAL"
        }

    def update_transparency(self, model_name: str, is_cloud: bool = False):
        """Update transparency with new model usage"""
        self.current_model = model_name
        if is_cloud:
            self.total_spend += 0.01  # Estimate per request

        # Save updated status
        self._save_transparency_status()

    def _save_transparency_status(self):
        """Save current transparency status"""
        status = self.get_transparency_status()
        try:
            status_file = Path("data/model_transparency/current_status.json")
            status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save transparency status: {e}")


class ReplikaInspiredWidget:
    """Replika-inspired widget with smooth animations"""

    def __init__(self, root, va, widget, viz):
        self.root = root
        self.va = va
        self.widget = widget
        self.viz = viz

        # Animation state
        self.animation_phase = 0.0
        self.idle_animation_running = True
        self.pulse_scale = 1.0
        self.fade_alpha = 1.0

        # Colors (Replika-inspired warm, modern palette)
        self.colors = self._get_replika_colors()

        # Create widget
        self.create_widget()

        # Start idle animations
        self.start_idle_animation()

    def _get_replika_colors(self) -> Dict[str, str]:
        """Get Replika-inspired color scheme for any VA"""
        # Warm, modern palette inspired by Replika
        # Use VA's own colors if available, otherwise generate from character_id
        va_colors = {
            "jarvis_va": {
                "primary": "#FF6B35",      # Warm orange-red
                "secondary": "#F7931E",    # Golden orange
                "bg": "#1A1A2E",          # Deep navy
                "accent": "#00D4FF",      # Cyan
                "text": "#FFFFFF",
                "mood": "#4ECDC4"         # Teal
            },
            "imva": {
                "primary": "#FF6B9D",     # Pink
                "secondary": "#C44569",   # Deep pink
                "bg": "#2D1B3D",          # Purple-dark
                "accent": "#FFC857",      # Yellow
                "text": "#FFFFFF",
                "mood": "#FF6B9D"
            },
            "ace": {
                "primary": "#00D4FF",     # Cyan
                "secondary": "#0099CC",  # Blue
                "bg": "#0D1B2A",          # Dark blue
                "accent": "#FF6B35",      # Orange
                "text": "#FFFFFF",
                "mood": "#00D4FF"
            },
            "ava": {
                "primary": "#9B59B6",     # Purple
                "secondary": "#8E44AD",   # Deep purple
                "bg": "#1A1A2E",          # Navy
                "accent": "#E74C3C",      # Red
                "text": "#FFFFFF",
                "mood": "#9B59B6"
            }
        }

        # Check if we have predefined colors
        if self.va.character_id in va_colors:
            return va_colors[self.va.character_id]

        # Use VA's own colors from registry if available
        if hasattr(self.va, 'primary_color') and self.va.primary_color:
            return {
                "primary": self.va.primary_color,
                "secondary": self.va.secondary_color if hasattr(self.va, 'secondary_color') else self.va.primary_color,
                "bg": "#1A1A2E",  # Deep navy background
                "accent": self.va.primary_color,
                "text": "#FFFFFF",
                "mood": self.va.primary_color
            }

        # Generate colors from character_id hash (for any VA)
        char_hash = hash(self.va.character_id)
        color_palettes = [
            {"primary": "#6C5CE7", "secondary": "#A29BFE", "accent": "#00B894", "mood": "#6C5CE7"},
            {"primary": "#00B894", "secondary": "#00CEC9", "accent": "#6C5CE7", "mood": "#00B894"},
            {"primary": "#FDCB6E", "secondary": "#E17055", "accent": "#00B894", "mood": "#FDCB6E"},
            {"primary": "#E84393", "secondary": "#FD79A8", "accent": "#FDCB6E", "mood": "#E84393"},
            {"primary": "#74B9FF", "secondary": "#0984E3", "accent": "#00B894", "mood": "#74B9FF"},
            {"primary": "#A29BFE", "secondary": "#6C5CE7", "accent": "#00B894", "mood": "#A29BFE"},
        ]

        palette = color_palettes[abs(char_hash) % len(color_palettes)]
        return {
            "primary": palette["primary"],
            "secondary": palette["secondary"],
            "bg": "#1A1A2E",
            "accent": palette["accent"],
            "text": "#FFFFFF",
            "mood": palette["mood"]
        }

    def create_widget(self):
        """Create the Replika-inspired widget"""
        # Main container with rounded corners effect
        self.container = tk.Frame(
            self.root,
            bg=self.colors["bg"],
            relief=tk.FLAT,
            borderwidth=0
        )

        # Position widget
        x = self.widget.position.get("x", 100)
        y = self.widget.position.get("y", 100)
        width = self.widget.size.get("width", 280)
        height = self.widget.size.get("height", 360)

        self.container.place(x=x, y=y, width=width, height=height)

        # Create gradient-like effect with multiple frames
        self._create_gradient_background()

        # Avatar area (top section)
        self._create_avatar_section()

        # Status/mood indicator
        self._create_mood_indicator()

        # Name and personality
        self._create_name_section()

        # Status text
        self._create_status_section()

        # Make draggable
        self._make_draggable()

    def _create_gradient_background(self):
        """Create gradient-like background effect"""
        # Top gradient frame
        top_gradient = tk.Frame(
            self.container,
            bg=self.colors["primary"],
            height=120
        )
        top_gradient.pack(fill=tk.X, side=tk.TOP)
        top_gradient.pack_propagate(False)

        # Bottom frame
        bottom_frame = tk.Frame(
            self.container,
            bg=self.colors["bg"]
        )
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = bottom_frame

    def _create_avatar_section(self):
        """Create avatar display area"""
        avatar_frame = tk.Frame(
            self.content_frame,
            bg=self.colors["bg"],
            height=100
        )
        avatar_frame.pack(fill=tk.X, pady=10)
        avatar_frame.pack_propagate(False)

        # Avatar circle (simulated with frame)
        avatar_size = 80
        self.avatar_canvas = tk.Canvas(
            avatar_frame,
            width=avatar_size,
            height=avatar_size,
            bg=self.colors["bg"],
            highlightthickness=0,
            borderwidth=0
        )
        self.avatar_canvas.pack()

        # Draw avatar circle with glow effect
        center = avatar_size // 2
        radius = avatar_size // 2 - 5

        # Outer glow
        self.avatar_canvas.create_oval(
            center - radius - 3, center - radius - 3,
            center + radius + 3, center + radius + 3,
            fill=self.colors["mood"],
            outline="",
            width=0
        )

        # Main circle
        self.avatar_canvas.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            fill=self.colors["primary"],
            outline=self.colors["accent"],
            width=2
        )

        # Avatar symbol/emoji (personality-based, works for any VA)
        avatar_symbols = {
            "jarvis_va": "⚡",
            "imva": "🤖",
            "ace": "⚔️",
            "ava": "💜"
        }

        # Get symbol from character_id or generate from name/role
        if self.va.character_id in avatar_symbols:
            symbol = avatar_symbols[self.va.character_id]
        elif hasattr(self.va, 'avatar_style') and self.va.avatar_style:
            # Use avatar style to determine symbol
            style_lower = self.va.avatar_style.lower()
            if "iron" in style_lower or "tech" in style_lower:
                symbol = "⚡"
            elif "cute" in style_lower or "playful" in style_lower:
                symbol = "🤖"
            elif "combat" in style_lower or "warrior" in style_lower:
                symbol = "⚔️"
            else:
                symbol = self.va.name[0].upper()
        else:
            # Use first letter of name
            symbol = self.va.name[0].upper()
        self.avatar_canvas.create_text(
            center, center,
            text=symbol,
            font=('Arial', 32 if len(symbol) == 1 else 20, 'bold'),
            fill=self.colors["text"]
        )

        # Pulse animation circle (hidden initially)
        self.pulse_circle = self.avatar_canvas.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            fill="",
            outline=self.colors["mood"],
            width=2
        )

    def _create_mood_indicator(self):
        """Create mood/status indicator"""
        mood_frame = tk.Frame(
            self.content_frame,
            bg=self.colors["bg"]
        )
        mood_frame.pack(fill=tk.X, padx=15, pady=5)

        # Mood dot
        self.mood_dot = tk.Canvas(
            mood_frame,
            width=12,
            height=12,
            bg=self.colors["bg"],
            highlightthickness=0
        )
        self.mood_dot.pack(side=tk.LEFT, padx=(0, 8))

        # Draw pulsing dot
        self.mood_dot.create_oval(
            2, 2, 10, 10,
            fill=self.colors["mood"],
            outline=""
        )

        # Mood text (personality-based, works for any VA)
        mood_map = {
            "jarvis_va": ["Active", "Processing", "Ready", "Assisting"],
            "imva": ["Playful", "Curious", "Engaged", "Happy"],
            "ace": ["Combat Ready", "Alert", "Focused", "Prepared"],
            "ava": ["Standby", "Ready", "Waiting", "Available"]
        }

        # Get moods from role/personality if available
        if self.va.character_id in mood_map:
            moods = mood_map[self.va.character_id]
        elif hasattr(self.va, 'role') and self.va.role:
            # Generate moods based on role
            role_lower = self.va.role.lower()
            if "combat" in role_lower or "battle" in role_lower:
                moods = ["Combat Ready", "Alert", "Focused", "Prepared"]
            elif "playful" in role_lower or "fun" in role_lower:
                moods = ["Playful", "Curious", "Engaged", "Happy"]
            elif "assistant" in role_lower or "help" in role_lower:
                moods = ["Active", "Processing", "Ready", "Assisting"]
            else:
                moods = ["Active", "Thinking", "Ready", "Listening"]
        else:
            moods = ["Active", "Thinking", "Ready", "Listening"]

        mood_text = moods[hash(self.va.character_id) % len(moods)]

        self.mood_label = tk.Label(
            mood_frame,
            text=mood_text,
            font=('Arial', 9),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            anchor='w'
        )
        self.mood_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _create_name_section(self):
        """Create name and personality section"""
        name_frame = tk.Frame(
            self.content_frame,
            bg=self.colors["bg"]
        )
        name_frame.pack(fill=tk.X, padx=15, pady=5)

        # Name
        self.name_label = tk.Label(
            name_frame,
            text=self.va.name,
            font=('Arial', 16, 'bold'),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            anchor='w'
        )
        self.name_label.pack(fill=tk.X)

        # Role/personality
        self.role_label = tk.Label(
            name_frame,
            text=self.va.role,
            font=('Arial', 10),
            bg=self.colors["bg"],
            fg=self.colors["secondary"],
            anchor='w'
        )
        self.role_label.pack(fill=tk.X, pady=(2, 0))

    def _create_status_section(self):
        """Create status section"""
        status_frame = tk.Frame(
            self.content_frame,
            bg=self.colors["bg"]
        )
        status_frame.pack(fill=tk.X, padx=15, pady=10)

        # Status text (with personality, works for any VA)
        status_texts = {
            "jarvis_va": "✨ Always here for you",
            "imva": "😊 Ready to chat!",
            "ace": "⚔️ Combat systems online",
            "ava": "💜 Standing by"
        }

        # Generate status from role/personality
        if self.va.character_id in status_texts:
            status_text = status_texts[self.va.character_id]
        elif hasattr(self.va, 'role') and self.va.role:
            role_lower = self.va.role.lower()
            if "combat" in role_lower:
                status_text = "⚔️ Combat systems online"
            elif "chat" in role_lower or "conversation" in role_lower:
                status_text = "😊 Ready to chat!"
            elif "assistant" in role_lower:
                status_text = "✨ Always here for you"
            else:
                status_text = f"✨ {self.va.role}"
        else:
            status_text = "✨ Online"

        self.status_label = tk.Label(
            status_frame,
            text=status_text,
            font=('Arial', 9),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            anchor='w'
        )
        self.status_label.pack(fill=tk.X)

        # Tasks indicator
        tasks = self.widget.properties.get("tasks", 0)
        if tasks > 0:
            tasks_label = tk.Label(
                status_frame,
                text=f"📋 {tasks} task(s)",
                font=('Arial', 8),
                bg=self.colors["bg"],
                fg=self.colors["secondary"],
                anchor='w'
            )
            tasks_label.pack(fill=tk.X, pady=(3, 0))

    def _make_draggable(self):
        """Make widget draggable"""
        def start_drag(event):
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root

        def on_drag(event):
            dx = event.x_root - self.drag_start_x
            dy = event.y_root - self.drag_start_y

            x = self.container.winfo_x() + dx
            y = self.container.winfo_y() + dy

            # Keep on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            width = self.container.winfo_width()
            height = self.container.winfo_height()

            x = max(0, min(x, screen_width - width))
            y = max(0, min(y, screen_height - height))

            self.container.place(x=x, y=y)

            # Update widget position
            self.viz.update_widget_position(
                self.widget.widget_id,
                {"x": x, "y": y}
            )

            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root

        # Make top gradient draggable
        for child in self.container.winfo_children():
            if isinstance(child, tk.Frame):
                child.bind("<Button-1>", start_drag)
                child.bind("<B1-Motion>", on_drag)
                child.configure(cursor="hand2")

    def start_idle_animation(self):
        """Start idle animation loop"""
        def animate():
            while self.idle_animation_running:
                # Pulse animation
                self.animation_phase += 0.1
                if self.animation_phase > 2 * math.pi:
                    self.animation_phase = 0.0

                # Pulse scale
                self.pulse_scale = 1.0 + 0.1 * math.sin(self.animation_phase)

                # Update avatar pulse
                if hasattr(self, 'avatar_canvas'):
                    center = 40
                    radius = 35
                    pulse_radius = radius * self.pulse_scale

                    self.avatar_canvas.coords(
                        self.pulse_circle,
                        center - pulse_radius, center - pulse_radius,
                        center + pulse_radius, center + pulse_radius
                    )

                    # Fade pulse outline
                    alpha = int(128 * (1.0 - abs(math.sin(self.animation_phase))))
                    color = self._hex_with_alpha(self.colors["mood"], alpha)
                    self.avatar_canvas.itemconfig(
                        self.pulse_circle,
                        outline=color
                    )

                time.sleep(0.05)  # ~20 FPS

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def _hex_with_alpha(self, hex_color: str, alpha: int) -> str:
        """Convert hex color with alpha (simplified)"""
        # For tkinter, we'll just return the color
        # Full alpha support would require more complex rendering
        return hex_color

    def animate_attention(self):
        """Animate attention grab (like Replika's reactions)"""
        # Scale up slightly with smooth easing
        original_width = self.container.winfo_width()
        original_height = self.container.winfo_height()
        original_x = self.container.winfo_x()
        original_y = self.container.winfo_y()

        def scale_animation():
            # Smooth scale animation
            steps = 10
            for i in range(steps):
                # Ease in-out
                t = i / steps
                ease = 0.5 - 0.5 * math.cos(t * math.pi)
                scale = 1.0 + 0.05 * (1.0 - abs(ease - 0.5) * 2)

                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                x = original_x - (new_width - original_width) // 2
                y = original_y - (new_height - original_height) // 2

                self.root.after(0, lambda w=new_width, h=new_height, x=x, y=y: 
                    self.container.place(x=x, y=y, width=w, height=h))
                time.sleep(0.02)

        thread = threading.Thread(target=scale_animation, daemon=True)
        thread.start()

    def update_mood(self, new_mood: str):
        """Update mood indicator"""
        if hasattr(self, 'mood_label'):
            self.mood_label.config(text=new_mood)

    def show_reaction(self, reaction: str):
        """Show emotional reaction (like Replika)"""
        # Create temporary reaction label
        reaction_label = tk.Label(
            self.content_frame,
            text=reaction,
            font=('Arial', 14),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        )
        reaction_label.pack(pady=5)

        # Fade out after 2 seconds
        def remove_reaction():
            time.sleep(2)
            self.root.after(0, reaction_label.destroy)

        thread = threading.Thread(target=remove_reaction, daemon=True)
        thread.start()


def render_replika_inspired(visibility_system=None):
    """Render ALL VAs with Replika-inspired design"""
    if not TKINTER_AVAILABLE:
        logger.error("tkinter not available")
        return False

    # Initialize visibility system (lazy import to avoid circular dependency)
    from va_visibility_system import VAVisibilitySystem

    if visibility_system is None:
        visibility = VAVisibilitySystem()
        visibility.show_all_vas()
    else:
        visibility = visibility_system
        existing_widgets = sum(len(visibility.viz.get_va_widgets(va.character_id)) 
                              for va in visibility.vas)
        if existing_widgets == 0:
            visibility.show_all_vas()

    # Create main window
    root = tk.Tk()
    root.title("LUMINA Virtual Assistants - Replika Inspired ✨")
    root.geometry("1400x900")
    root.configure(bg='#0A0A0A')  # Deep black background

    # Create widgets for ALL virtual assistants
    widgets = []
    viz = visibility.viz

    # Add Transparency HUD
    hud = TransparencyHUD(root, project_root)

    # Get all VAs (ensure we have widgets for all)
    all_vas = visibility.vas

    print("=" * 80)
    print("✨ REPLIKA-INSPIRED RENDERING FOR ALL VIRTUAL ASSISTANTS")
    print("=" * 80)
    print(f"Rendering {len(all_vas)} virtual assistant(s)...")
    print()

    for i, va in enumerate(all_vas):
        va_widgets = viz.get_va_widgets(va.character_id)

        if not va_widgets:
            print(f"  Creating widget for {va.name}...")
            widget = viz.create_va_widget(va.character_id)
            va_widgets = [widget]
        else:
            print(f"  Using existing widget for {va.name}...")

        for widget in va_widgets:
            if not widget.visible:
                widget.visible = True  # Ensure visible
                print(f"    ✅ Made {va.name} visible")

            # Position widgets in a responsive grid
            cols = max(2, int(len(all_vas) ** 0.5) + 1)  # Dynamic columns
            row = i // cols
            col = i % cols

            x = 50 + col * 320
            y = 50 + row * 400

            # Update widget position
            widget.position = {"x": x, "y": y}
            widget.size = {"width": 280, "height": 360}
            viz.update_widget_position(widget.widget_id, {"x": x, "y": y})

            # Create Replika-inspired widget
            print(f"    🎨 Creating Replika widget for {va.name}...")
            replika_widget = ReplikaInspiredWidget(root, va, widget, viz)
            widgets.append(replika_widget)
            print(f"    ✅ {va.name} rendered with Replika design!")

    print()
    print(f"✅ Successfully rendered {len(widgets)} virtual assistant(s) with Replika-inspired design!")
    print()

    # Add fade-in animation
    def fade_in():
        for widget in widgets:
            widget.container.configure(bg=widget.colors["bg"])
        root.update()

    fade_in()

    print("=" * 80)
    print("✨ REPLIKA-INSPIRED VA WIDGETS")
    print("=" * 80)
    print()
    print("Features:")
    print("  🎨 Modern, warm color palette")
    print("  ✨ Smooth idle animations")
    print("  💫 Pulsing avatar indicators")
    print("  🎭 Personality and mood display")
    print("  🖱️  Drag to reposition")
    print()
    print("Close window when done.")
    print()

    root.mainloop()

    return True


def main():
    """Main entry point"""
    print("=" * 80)
    print("🎨 REPLIKA-INSPIRED VA RENDERER")
    print("=" * 80)
    print()

    try:
        render_replika_inspired()
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":

    sys.exit(main())