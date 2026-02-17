#!/usr/bin/env python3
"""
Desktop Visualization System

Visual representation of VAs on desktop with widgets, VFX, and status indicators.

Tags: #VIRTUAL_ASSISTANT #VISUALIZATION #DESKTOP #WIDGET #VFX @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VADesktopViz")


class WidgetType(Enum):
    """Widget types"""
    HUD = "hud"  # Heads-up display
    BOBBLEHEAD = "bobblehead"
    COMBAT_INTERFACE = "combat_interface"
    PLACEHOLDER = "placeholder"
    STATUS_INDICATOR = "status_indicator"
    DASHBOARD = "dashboard"
    DEFCON_STREETLIGHT = "defcon_streetlight"  # DEFCON alert system tied to WOPR


class VFXType(Enum):
    """Visual effects types"""
    TRANSFORMATION = "transformation"
    COMBAT_MODE = "combat_mode"
    ACTIVATION = "activation"
    NOTIFICATION = "notification"
    STATUS_CHANGE = "status_change"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE = "slide"
    BOUNCE = "bounce"
    PULSE = "pulse"


class WidgetTheme(Enum):
    """Widget theme styles"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    IRON_MAN = "iron_man"
    NEON = "neon"
    MINIMAL = "minimal"
    GLASS = "glass"


@dataclass
class VAWidget:
    """VA desktop widget"""
    widget_id: str
    va_id: str
    widget_type: WidgetType
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    size: Dict[str, float] = field(default_factory=lambda: {"width": 120.0, "height": 90.0})  # Smaller default size
    visible: bool = True
    z_index: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # New features
    draggable: bool = True
    resizable: bool = True
    collapsed: bool = False
    group_id: Optional[str] = None
    theme: Optional[str] = None
    animation_state: str = "idle"  # idle, animating, transition
    min_size: Dict[str, float] = field(default_factory=lambda: {"width": 80.0, "height": 60.0})  # Smaller min size
    max_size: Dict[str, float] = field(default_factory=lambda: {"width": 800.0, "height": 600.0})

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["widget_type"] = self.widget_type.value
        return data


@dataclass
class VFXEffect:
    """Visual effect"""
    effect_id: str
    va_id: str
    vfx_type: VFXType
    duration: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["vfx_type"] = self.vfx_type.value
        return data


class VADesktopVisualization:
    """
    Desktop Visualization System

    Features:
    - Desktop widgets per VA
    - Visual effects (VFX)
    - Status indicators
    - Multi-VA dashboard
    - Iron Man HUD integration
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize desktop visualization system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Widgets
        self.widgets: Dict[str, VAWidget] = {}
        self.widget_counter = 0

        # VFX effects
        self.vfx_effects: List[VFXEffect] = []
        self.vfx_counter = 0

        # Widget type mapping
        self.va_widget_types = self._initialize_widget_types()

        # Widget groups
        self.widget_groups: Dict[str, List[str]] = {}  # group_id -> [widget_ids]
        self.group_counter = 0

        # Themes
        self.themes = self._initialize_themes()

        # Data persistence
        self.data_dir = project_root / "data" / "va_desktop_viz"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Try to load previous state
        self._load_state()

        logger.info("=" * 80)
        logger.info("🖥️  DESKTOP VISUALIZATION SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Widget system ready")
        logger.info("=" * 80)

    def _initialize_widget_types(self) -> Dict[str, WidgetType]:
        """Initialize VA-to-widget type mapping"""
        mapping = {}

        for va in self.vas:
            if va.character_id == "jarvis_va":
                mapping[va.character_id] = WidgetType.HUD
            elif va.character_id == "imva" or va.character_id == "kenny":
                # Both IMVA and Kenny use bobblehead widgets
                mapping[va.character_id] = WidgetType.BOBBLEHEAD
            elif va.character_id == "ace":
                mapping[va.character_id] = WidgetType.COMBAT_INTERFACE
            else:
                # Check avatar_template for bobblehead
                if hasattr(va, 'avatar_template') and 'bobblehead' in va.avatar_template.lower():
                    mapping[va.character_id] = WidgetType.BOBBLEHEAD
                else:
                    mapping[va.character_id] = WidgetType.PLACEHOLDER

        return mapping

    def _initialize_themes(self) -> Dict[str, Dict[str, Any]]:
        """Initialize widget themes"""
        return {
            "default": {
                "bg": "#2d2d2d",
                "fg": "#ffffff",
                "border": "#404040",
                "accent": "#66bb6a"
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#e0e0e0",
                "border": "#333333",
                "accent": "#4a9eff"
            },
            "light": {
                "bg": "#f5f5f5",
                "fg": "#212121",
                "border": "#e0e0e0",
                "accent": "#1976d2"
            },
            "iron_man": {
                "bg": "#1a1a1a",
                "fg": "#ffd700",
                "border": "#ff6b00",
                "accent": "#ff4444"
            },
            "neon": {
                "bg": "#0a0a0a",
                "fg": "#00ffff",
                "border": "#ff00ff",
                "accent": "#ffff00"
            },
            "minimal": {
                "bg": "#ffffff",
                "fg": "#000000",
                "border": "#cccccc",
                "accent": "#666666"
            },
            "glass": {
                "bg": "rgba(255, 255, 255, 0.1)",
                "fg": "#ffffff",
                "border": "rgba(255, 255, 255, 0.2)",
                "accent": "#4fc3f7"
            }
        }

    def create_va_widget(self, va_id: str, position: Optional[Dict[str, float]] = None,
                        size: Optional[Dict[str, float]] = None) -> VAWidget:
        """Create widget for a VA"""
        va = self.registry.get_character(va_id)
        if not va or va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            raise ValueError(f"VA {va_id} not found")

        self.widget_counter += 1
        widget_id = f"widget_{self.widget_counter:06d}"

        widget_type = self.va_widget_types.get(va_id, WidgetType.PLACEHOLDER)

        # Determine position - use provided, find available, or default
        # Use smaller default sizes for better organization
        default_sizes = {
            WidgetType.HUD: {"width": 180.0, "height": 120.0},
            WidgetType.BOBBLEHEAD: {"width": 100.0, "height": 100.0},
            WidgetType.COMBAT_INTERFACE: {"width": 140.0, "height": 100.0},
            WidgetType.DEFCON_STREETLIGHT: {"width": 80.0, "height": 200.0},  # Tall and narrow for streetlight
            WidgetType.STATUS_INDICATOR: {"width": 100.0, "height": 80.0},
            WidgetType.DASHBOARD: {"width": 300.0, "height": 200.0},
            WidgetType.PLACEHOLDER: {"width": 120.0, "height": 90.0}
        }
        widget_size = size or default_sizes.get(widget_type, {"width": 120.0, "height": 90.0})
        if position is None:
            # Find available position that doesn't overlap
            position = self.find_available_position(widget_size)

        # Build widget properties
        widget_properties = {
            "va_name": va.name,
            "va_role": va.role,
            "hierarchy": va.hierarchy_level,
            "primary_color": va.primary_color,
            "secondary_color": va.secondary_color,
            "avatar_style": va.avatar_style,
            "avatar_template": va.avatar_template,
            "catchphrase": va.catchphrase
        }

        # Add training dummy properties if applicable
        if hasattr(va, 'is_training_dummy') and va.is_training_dummy:
            widget_properties["is_training_dummy"] = True
            widget_properties["immortal"] = va.immortal if hasattr(va, 'immortal') else True
            widget_properties["training_partners"] = va.training_partners if hasattr(va, 'training_partners') else []
            widget_properties["training_status"] = "Ready for training"
            if va.character_id == "ace":
                widget_properties["training_mode"] = "Immortal Demigod - Training Dummy"
                widget_properties["regeneration"] = "Instant"

        widget = VAWidget(
            widget_id=widget_id,
            va_id=va_id,
            widget_type=widget_type,
            position=position,
            size=widget_size,
            properties=widget_properties
        )

        self.widgets[widget_id] = widget

        # Auto-save state after creating widget
        self._save_state()

        logger.info(f"🖥️  Created widget: {widget_id} for {va.name} ({widget_type.value})")
        return widget

    def show_va_status(self, va_id: str, status: Dict[str, Any]):
        """Update VA widget with status"""
        va_widgets = [w for w in self.widgets.values() if w.va_id == va_id]

        if not va_widgets:
            # Create widget if doesn't exist
            self.create_va_widget(va_id)
            va_widgets = [w for w in self.widgets.values() if w.va_id == va_id]

        for widget in va_widgets:
            widget.properties.update(status)
            widget.properties["last_update"] = datetime.now().isoformat()

        logger.info(f"📊 Updated status for {va_id}")

    def display_vfx(self, va_id: str, vfx_type: VFXType,
                   duration: float = 1.0, properties: Optional[Dict[str, Any]] = None) -> VFXEffect:
        """Display visual effect for VA"""
        self.vfx_counter += 1
        effect_id = f"vfx_{self.vfx_counter:06d}"

        effect = VFXEffect(
            effect_id=effect_id,
            va_id=va_id,
            vfx_type=vfx_type,
            duration=duration,
            properties=properties or {}
        )

        self.vfx_effects.append(effect)

        # Keep only last 100 effects
        if len(self.vfx_effects) > 100:
            self.vfx_effects = self.vfx_effects[-100:]

        logger.info(f"✨ VFX: {vfx_type.value} for {va_id}")
        return effect

    def multi_va_dashboard(self) -> Dict[str, Any]:
        """Create multi-VA dashboard"""
        dashboard = {
            "dashboard_id": f"dashboard_{datetime.now().timestamp()}",
            "vas": [],
            "widgets": [],
            "timestamp": datetime.now().isoformat()
        }

        for va in self.vas:
            va_info = {
                "va_id": va.character_id,
                "name": va.name,
                "role": va.role,
                "widgets": [w.widget_id for w in self.widgets.values() if w.va_id == va.character_id],
                "visible": any(w.visible for w in self.widgets.values() if w.va_id == va.character_id)
            }
            dashboard["vas"].append(va_info)

        dashboard["widgets"] = [w.to_dict() for w in self.widgets.values()]

        logger.info(f"📊 Created multi-VA dashboard with {len(dashboard['vas'])} VAs")
        return dashboard

    def get_va_widgets(self, va_id: str) -> List[VAWidget]:
        """Get widgets for a VA"""
        return [w for w in self.widgets.values() if w.va_id == va_id]

    def set_widget_visibility(self, widget_id: str, visible: bool):
        """Set widget visibility"""
        if widget_id in self.widgets:
            self.widgets[widget_id].visible = visible
            logger.info(f"👁️  Widget {widget_id} visibility: {visible}")

    def remove_va_widgets(self, va_id: str) -> int:
        """Remove all widgets for a VA"""
        widgets_to_remove = [w for w in self.widgets.values() if w.va_id == va_id]
        count = len(widgets_to_remove)

        for widget in widgets_to_remove:
            del self.widgets[widget.widget_id]

        if count > 0:
            logger.info(f"🗑️  Removed {count} widget(s) for VA {va_id}")
            self._save_state()

        return count

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a specific widget"""
        if widget_id in self.widgets:
            va_id = self.widgets[widget_id].va_id
            del self.widgets[widget_id]
            logger.info(f"🗑️  Removed widget {widget_id} for VA {va_id}")
            self._save_state()
            return True
        return False

    def cleanup_inactive_widgets(self, active_va_ids: List[str]) -> int:
        """Remove widgets for VAs that are no longer active"""
        inactive_widgets = [
            w for w in self.widgets.values()
            if w.va_id not in active_va_ids
        ]
        count = len(inactive_widgets)

        for widget in inactive_widgets:
            del self.widgets[widget.widget_id]

        if count > 0:
            logger.info(f"🧹 Cleaned up {count} inactive widget(s)")
            self._save_state()

        return count

    def find_available_position(self, size: Dict[str, float], 
                                existing_widgets: Optional[List[VAWidget]] = None,
                                margin: float = 20.0) -> Dict[str, float]:
        """Find an available position that doesn't overlap with existing widgets"""
        if existing_widgets is None:
            existing_widgets = list(self.widgets.values())

        # Default screen bounds (can be adjusted)
        screen_width = 1920.0
        screen_height = 1080.0

        widget_width = size.get("width", 120.0)  # Smaller default
        widget_height = size.get("height", 90.0)  # Smaller default

        # Ensure widget fits on screen
        if widget_width > screen_width - 2 * margin:
            widget_width = screen_width - 2 * margin
        if widget_height > screen_height - 2 * margin:
            widget_height = screen_height - 2 * margin

        # Try positions in a grid pattern
        cols = int((screen_width - margin) / (widget_width + margin))
        rows = int((screen_height - margin) / (widget_height + margin))

        for row in range(rows):
            for col in range(cols):
                x = margin + col * (widget_width + margin)
                y = margin + row * (widget_height + margin)

                # Ensure position is on screen
                if x + widget_width > screen_width:
                    continue
                if y + widget_height > screen_height:
                    continue

                # Check for overlap
                overlaps = False
                for existing in existing_widgets:
                    if not existing.visible:
                        continue
                    ex_x = existing.position.get("x", 0)
                    ex_y = existing.position.get("y", 0)
                    ex_w = existing.size.get("width", 200.0)
                    ex_h = existing.size.get("height", 150.0)

                    if not (x + widget_width < ex_x or x > ex_x + ex_w or
                           y + widget_height < ex_y or y > ex_y + ex_h):
                        overlaps = True
                        break

                if not overlaps:
                    return {"x": x, "y": y}

        # Fallback: return a safe default position (top-left with margin)
        return {"x": margin, "y": margin}

    def _load_state(self) -> bool:
        """Load visualization state from disk"""
        state_file = self.data_dir / "visualization_state.json"

        if not state_file.exists():
            return False

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Restore widget counter
            self.widget_counter = state.get("widget_counter", 0)
            self.vfx_counter = state.get("vfx_counter", 0)
            self.group_counter = state.get("group_counter", 0)

            # Restore widget groups
            self.widget_groups = state.get("widget_groups", {})

            # Restore widgets
            widgets_data = state.get("widgets", {})
            for widget_id, widget_data in widgets_data.items():
                # Convert widget_type string back to enum
                widget_type_str = widget_data.get("widget_type", "placeholder")
                widget_type = WidgetType(widget_type_str)

                widget = VAWidget(
                    widget_id=widget_data["widget_id"],
                    va_id=widget_data["va_id"],
                    widget_type=widget_type,
                    position=widget_data.get("position", {"x": 0.0, "y": 0.0}),
                    size=widget_data.get("size", {"width": 200.0, "height": 150.0}),
                    visible=widget_data.get("visible", True),
                    z_index=widget_data.get("z_index", 0),
                    properties=widget_data.get("properties", {}),
                    created_at=widget_data.get("created_at", datetime.now().isoformat()),
                    draggable=widget_data.get("draggable", True),
                    resizable=widget_data.get("resizable", True),
                    collapsed=widget_data.get("collapsed", False),
                    group_id=widget_data.get("group_id"),
                    theme=widget_data.get("theme"),
                    animation_state=widget_data.get("animation_state", "idle"),
                    min_size=widget_data.get("min_size", {"width": 100.0, "height": 75.0}),
                    max_size=widget_data.get("max_size", {"width": 800.0, "height": 600.0})
                )

                self.widgets[widget_id] = widget

            logger.info(f"📂 Loaded visualization state: {len(self.widgets)} widget(s)")
            return True

        except Exception as e:
            logger.warning(f"⚠️  Could not load state: {e}")
            return False

    def _save_state(self):
        try:
            """Save visualization state to disk"""
            state_file = self.data_dir / "visualization_state.json"

            state = {
                "widgets": {wid: w.to_dict() for wid, w in self.widgets.items()},
                "recent_vfx": [e.to_dict() for e in self.vfx_effects[-20:]],
                "widget_counter": self.widget_counter,
                "vfx_counter": self.vfx_counter,
                "group_counter": self.group_counter,
                "widget_groups": self.widget_groups,
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved visualization state to {state_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    # Widget Grouping Methods
    def create_widget_group(self, name: str = None) -> str:
        """Create a new widget group"""
        self.group_counter += 1
        group_id = f"group_{self.group_counter:06d}"
        self.widget_groups[group_id] = []
        if name:
            self.widget_groups[group_id].append(f"_name:{name}")
        logger.info(f"📦 Created widget group: {group_id}")
        return group_id

    def add_widget_to_group(self, widget_id: str, group_id: str) -> bool:
        """Add widget to a group"""
        if widget_id not in self.widgets:
            return False
        if group_id not in self.widget_groups:
            return False

        if widget_id not in self.widget_groups[group_id]:
            self.widget_groups[group_id].append(widget_id)
            self.widgets[widget_id].group_id = group_id
            self._save_state()
            logger.info(f"📦 Added widget {widget_id} to group {group_id}")
            return True
        return False

    def remove_widget_from_group(self, widget_id: str) -> bool:
        """Remove widget from its group"""
        if widget_id not in self.widgets:
            return False

        widget = self.widgets[widget_id]
        if widget.group_id and widget.group_id in self.widget_groups:
            if widget_id in self.widget_groups[widget.group_id]:
                self.widget_groups[widget.group_id].remove(widget_id)
            widget.group_id = None
            self._save_state()
            logger.info(f"📦 Removed widget {widget_id} from group")
            return True
        return False

    def collapse_group(self, group_id: str) -> bool:
        """Collapse all widgets in a group"""
        if group_id not in self.widget_groups:
            return False

        for widget_id in self.widget_groups[group_id]:
            if widget_id.startswith("_name:"):
                continue
            if widget_id in self.widgets:
                self.widgets[widget_id].collapsed = True

        self._save_state()
        logger.info(f"📦 Collapsed group {group_id}")
        return True

    def expand_group(self, group_id: str) -> bool:
        """Expand all widgets in a group"""
        if group_id not in self.widget_groups:
            return False

        for widget_id in self.widget_groups[group_id]:
            if widget_id.startswith("_name:"):
                continue
            if widget_id in self.widgets:
                self.widgets[widget_id].collapsed = False

        self._save_state()
        logger.info(f"📦 Expanded group {group_id}")
        return True

    def get_group_widgets(self, group_id: str) -> List[VAWidget]:
        """Get all widgets in a group"""
        if group_id not in self.widget_groups:
            return []

        widgets = []
        for widget_id in self.widget_groups[group_id]:
            if widget_id.startswith("_name:"):
                continue
            if widget_id in self.widgets:
                widgets.append(self.widgets[widget_id])
        return widgets

    # Theme Methods
    def set_widget_theme(self, widget_id: str, theme: str) -> bool:
        """Set theme for a widget"""
        if widget_id not in self.widgets:
            return False
        if theme not in self.themes:
            theme = "default"

        self.widgets[widget_id].theme = theme
        self._save_state()
        logger.info(f"🎨 Set theme '{theme}' for widget {widget_id}")
        return True

    def get_theme_colors(self, theme: str = "default") -> Dict[str, Any]:
        """Get color scheme for a theme"""
        return self.themes.get(theme, self.themes["default"])

    # Animation Methods
    def animate_widget(self, widget_id: str, animation_type: VFXType, 
                      duration: float = 1.0) -> bool:
        """Animate a widget"""
        if widget_id not in self.widgets:
            return False

        widget = self.widgets[widget_id]
        widget.animation_state = "animating"

        # Create VFX effect
        effect = self.display_vfx(widget.va_id, animation_type, duration)

        # Reset animation state after duration
        def reset_animation():
            import time
            time.sleep(duration)
            widget.animation_state = "idle"

        import threading
        thread = threading.Thread(target=reset_animation, daemon=True)
        thread.start()

        logger.info(f"✨ Animating widget {widget_id} with {animation_type.value}")
        return True

    def update_widget_position(self, widget_id: str, position: Dict[str, float]) -> bool:
        """Update widget position (for drag-and-drop)"""
        if widget_id not in self.widgets:
            return False

        self.widgets[widget_id].position = position
        self._save_state()
        return True

    def update_widget_size(self, widget_id: str, size: Dict[str, float]) -> bool:
        """Update widget size (for resizing)"""
        if widget_id not in self.widgets:
            return False

        widget = self.widgets[widget_id]
        # Enforce min/max size constraints
        width = max(widget.min_size["width"], 
                   min(size["width"], widget.max_size["width"]))
        height = max(widget.min_size["height"], 
                    min(size["height"], widget.max_size["height"]))

        widget.size = {"width": width, "height": height}
        self._save_state()
        logger.info(f"📏 Resized widget {widget_id} to {width}x{height}")
        return True

    def toggle_widget_collapse(self, widget_id: str) -> bool:
        """Toggle widget collapse state"""
        if widget_id not in self.widgets:
            return False

        widget = self.widgets[widget_id]
        widget.collapsed = not widget.collapsed
        self._save_state()
        logger.info(f"📦 Widget {widget_id} {'collapsed' if widget.collapsed else 'expanded'}")
        return True

    def create_defcon_streetlight_widget(self, position: Optional[Dict[str, float]] = None) -> VAWidget:
        """Create DEFCON streetlight widget tied to WOPR and system alerts"""
        self.widget_counter += 1
        widget_id = f"widget_{self.widget_counter:06d}"

        # Default position (top-right corner for visibility)
        if position is None:
            position = {"x": 1800.0, "y": 20.0}

        widget = VAWidget(
            widget_id=widget_id,
            va_id="wopr",  # Tied to WOPR
            widget_type=WidgetType.DEFCON_STREETLIGHT,
            position=position,
            size={"width": 80.0, "height": 200.0},  # Tall and narrow like a streetlight
            properties={
                "name": "DEFCON Alert System",
                "role": "System Alert Monitor",
                "defcon_level": 5,  # 5 = Normal, 1 = Critical
                "wopr_tied": True,
                "alerts": [],
                "problems": [],
                "last_update": datetime.now().isoformat()
            },
            draggable=True,
            z_index=1000  # Always on top for visibility
        )

        self.widgets[widget_id] = widget
        self._save_state()

        logger.info(f"🚦 Created DEFCON streetlight widget: {widget_id}")
        return widget

    def update_defcon_level(self, defcon_level: int, alerts: Optional[List[Dict[str, Any]]] = None,
                           problems: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Update DEFCON streetlight widget with current alert level"""
        defcon_widgets = [
            w for w in self.widgets.values()
            if w.widget_type == WidgetType.DEFCON_STREETLIGHT
        ]

        if not defcon_widgets:
            # Create DEFCON widget if it doesn't exist
            self.create_defcon_streetlight_widget()
            defcon_widgets = [
                w for w in self.widgets.values()
                if w.widget_type == WidgetType.DEFCON_STREETLIGHT
            ]

        for widget in defcon_widgets:
            widget.properties["defcon_level"] = max(1, min(5, defcon_level))  # Clamp 1-5
            widget.properties["last_update"] = datetime.now().isoformat()

            if alerts is not None:
                widget.properties["alerts"] = alerts
            if problems is not None:
                widget.properties["problems"] = problems

            # Determine color based on DEFCON level
            defcon_colors = {
                1: "#ff0000",  # Red - Critical
                2: "#ff6600",  # Orange - High alert
                3: "#ffcc00",  # Yellow - Elevated
                4: "#00ff00",  # Green - Normal
                5: "#00ccff"   # Blue - Peaceful
            }
            widget.properties["defcon_color"] = defcon_colors.get(widget.properties["defcon_level"], "#00ccff")

        self._save_state()
        logger.info(f"🚦 Updated DEFCON level to {defcon_level}")
        return True

    def get_defcon_widgets(self) -> List[VAWidget]:
        """Get all DEFCON streetlight widgets"""
        return [w for w in self.widgets.values() if w.widget_type == WidgetType.DEFCON_STREETLIGHT]


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    viz = VADesktopVisualization(registry)

    print("=" * 80)
    print("🖥️  DESKTOP VISUALIZATION SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Create widgets
    print("Creating widgets for all VAs...")
    for va in viz.vas:
        widget = viz.create_va_widget(va.character_id)
        print(f"  ✅ Created {widget.widget_type.value} widget for {va.name}")
    print()

    # Test: Show status
    print("Updating widget status...")
    for va in viz.vas:
        viz.show_va_status(va.character_id, {
            "status": "active",
            "tasks": 2,
            "messages": 1
        })
        print(f"  ✅ Updated status for {va.name}")
    print()

    # Test: Display VFX
    print("Displaying VFX effects...")
    vfx_types = [VFXType.ACTIVATION, VFXType.COMBAT_MODE, VFXType.NOTIFICATION]
    for i, va in enumerate(viz.vas[:3]):
        if i < len(vfx_types):
            effect = viz.display_vfx(va.character_id, vfx_types[i])
            print(f"  ✅ {vfx_types[i].value} effect for {va.name}")
    print()

    # Test: Multi-VA dashboard
    print("Creating multi-VA dashboard...")
    dashboard = viz.multi_va_dashboard()
    print(f"  ✅ Dashboard created with {len(dashboard['vas'])} VAs")
    print(f"  ✅ Total widgets: {len(dashboard['widgets'])}")
    print()

    # Save state
    viz._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()