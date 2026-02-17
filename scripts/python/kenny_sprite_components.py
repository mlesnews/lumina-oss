#!/usr/bin/env python3
"""
Kenny Sprite Components - Component-Based Design with Dynamic Scaling

Each design element is a separate component that can be adjusted dynamically:
- Body (Hot Rod Red circle - torso) - Iron Man Mark 5
- Helmet/Head (above body) - Hot Rod Red with Gold accents
- HUD (inside helmet)
- Arc Reactor (in chest/torso)

Components use dynamic scaling and can be adjusted without restarting.

Tags: #KENNY #COMPONENTS #DYNAMIC_SCALING @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

@dataclass
class SpriteComponent:
    """Base component with dynamic scaling"""
    name: str
    size_scale: float = 1.0
    position_offset: Tuple[float, float] = (0.0, 0.0)  # Relative to center (x, y)
    enabled: bool = True
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)

    def get_scaled_size(self, base_size: int) -> int:
        """Get scaled size based on base size"""
        return int(base_size * self.size_scale)

    def get_position(self, center_x: float, center_y: float, base_size: int) -> Tuple[float, float]:
        """Get absolute position with offset"""
        offset_x = self.position_offset[0] * base_size
        offset_y = self.position_offset[1] * base_size
        return (center_x + offset_x, center_y + offset_y)

@dataclass
class BodyComponent(SpriteComponent):
    """Hot Rod Red circle - represents TORSO/BODY (not head) - Iron Man Mark 5 proportions"""
    name: str = "body"
    size_scale: float = 1.0  # Full size
    color: Tuple[int, int, int, int] = (220, 20, 60, 255)  # Hot Rod Red (Iron Man Mark 5)
    radius_ratio: float = 0.50  # 50% of base size (larger to fill window like Ace)

@dataclass
class HelmetComponent(SpriteComponent):
    """Helmet/Head - JARVIS-like geometric/angular (hexagonal) - Hot Rod Red with Gold accents (Mark 5)"""
    name: str = "helmet"
    size_scale: float = 1.0  # 100% of base size (larger to match Ace's visual size)
    position_offset: Tuple[float, float] = (0.0, -0.50)  # Higher up (negative Y - clearly above body)
    color: Tuple[int, int, int, int] = (220, 20, 60, 255)  # Hot Rod Red (Iron Man Mark 5)
    width_ratio: float = 0.90  # Geometric helmet width (larger, fills window better)
    height_ratio: float = 0.85  # Geometric helmet height (larger, fills window better)

@dataclass
class HUDComponent(SpriteComponent):
    """HUD rectangle - INSIDE the helmet/head"""
    name: str = "hud"
    size_scale: float = 0.50  # 50% of base size (larger, more visible)
    position_offset: Tuple[float, float] = (0.0, -0.50)  # Same as helmet (inside it)
    color: Tuple[int, int, int, int] = (0, 0, 0, 255)  # Black
    width_ratio: float = 0.50
    height_ratio: float = 0.40

@dataclass
class FaceComponent(SpriteComponent):
    """Face circle - INSIDE the HUD"""
    name: str = "face"
    size_scale: float = 0.18  # 18% of base size (larger, more visible)
    position_offset: Tuple[float, float] = (0.0, -0.50)  # Same as HUD (inside it)
    color: Tuple[int, int, int, int] = (0, 0, 0, 255)  # Black (solid, not transparent)
    radius_ratio: float = 0.18

@dataclass
class ArcReactorComponent(SpriteComponent):
    """Arc Reactor - in CHEST/TORSO area (the orange body circle) - slightly smaller"""
    name: str = "arc_reactor"
    size_scale: float = 0.10  # 10% of base size (slightly smaller)
    position_offset: Tuple[float, float] = (0.0, -0.05)  # Slightly above center (chest area)
    color: Tuple[int, int, int, int] = (0, 217, 255, 255)  # Cyan (#00D9FF)
    radius_ratio: float = 0.10

class KennySpriteComponents:
    """Component manager for Kenny's sprite - allows dynamic adjustment"""

    def __init__(self, base_size: int = 60):
        self.base_size = base_size

        # Initialize components with corrected positions (based on analysis)
        # Helmet: Needs to be in head area (< 40% from top) - use -0.50 offset (higher up)
        # Arc Reactor: Needs to be in chest area (33-66% from top) - use 0.0 offset (center)
        self.body = BodyComponent()
        self.helmet = HelmetComponent()  # Uses default position_offset=(0.0, -0.50) - clearly above body
        self.hud = HUDComponent()  # Uses default position_offset=(0.0, -0.50) - inside helmet
        self.face = FaceComponent()  # Uses default position_offset=(0.0, -0.50) - inside HUD
        self.arc_reactor = ArcReactorComponent()  # Uses default position_offset=(0.0, -0.05) - chest area

        # Component registry for easy access
        self.components = {
            "body": self.body,
            "helmet": self.helmet,
            "hud": self.hud,
            "face": self.face,
            "arc_reactor": self.arc_reactor
        }

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []

        # Logger setup
        try:
            from lumina_logger import get_logger
            self.logger = get_logger("KennySpriteComponents")
        except ImportError:
            import logging
            self.logger = logging.getLogger("KennySpriteComponents")

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

    def adjust_component(self, component_name: str, **kwargs):
        """Dynamically adjust a component without restart"""
        if component_name not in self.components:
            raise ValueError(f"Unknown component: {component_name}")

        component = self.components[component_name]

        # Update component properties
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)
                print(f"✅ Adjusted {component_name}.{key} = {value}")
            else:
                print(f"⚠️  {component_name} has no attribute: {key}")

    def get_component_config(self, component_name: str) -> Dict:
        """Get current configuration of a component"""
        if component_name not in self.components:
            return {}

        component = self.components[component_name]
        return {
            "name": component.name,
            "size_scale": component.size_scale,
            "position_offset": component.position_offset,
            "enabled": component.enabled,
            "color": component.color
        }

    def get_all_configs(self) -> Dict:
        """Get all component configurations"""
        return {name: self.get_component_config(name) for name in self.components.keys()}
