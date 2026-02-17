#!/usr/bin/env python3
"""
Kenny Attribute Comparison System

Quantitative comparison between Original Kenny and Enhanced Kenny.
One-for-one attribute comparison to identify desirable traits and remove undesirable ones.
Creates merged version with best of both.

Tags: #KENNY #COMPARISON #MERGE #QUANTITATIVE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

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
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KennyAttributeComparison")


class AttributeCategory(Enum):
    """Attribute categories"""
    VISUAL = "visual"  # Sprite rendering, appearance
    MOVEMENT = "movement"  # Animation, speed, interpolation
    COLLABORATION = "collaboration"  # Ace integration, messaging
    BEHAVIOR = "behavior"  # State management, reactions
    INTEGRATION = "integration"  # Ecosystem integration
    PERFORMANCE = "performance"  # Speed, efficiency


class AttributeStatus(Enum):
    """Attribute status"""
    DESIRABLE = "desirable"  # Keep this attribute
    UNDESIRABLE = "undesirable"  # Remove this attribute
    NEEDS_IMPROVEMENT = "needs_improvement"  # Fix/improve
    UNKNOWN = "unknown"  # Not yet evaluated


@dataclass
class KennyAttribute:
    """Single attribute for comparison"""
    name: str
    category: AttributeCategory
    original_value: Any
    enhanced_value: Any
    status: AttributeStatus = AttributeStatus.UNKNOWN
    is_desirable: Optional[bool] = None
    notes: str = ""
    merged_value: Optional[Any] = None  # Best value after comparison

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['category'] = self.category.value
        result['status'] = self.status.value
        return result


class KennyAttributeComparison:
    """
    Quantitative comparison system for Kenny attributes.

    Compares Original Kenny vs Enhanced Kenny one-for-one.
    Identifies desirable traits and removes undesirable ones.
    Creates merged version.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize comparison system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "kenny_comparison"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.attributes: List[KennyAttribute] = []
        self.comparison_file = self.data_dir / "kenny_attribute_comparison.json"

        # Load existing comparison
        self._load_comparison()

        # If no comparison exists, create initial comparison
        if not self.attributes:
            self._create_initial_comparison()

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

    def _load_comparison(self):
        """Load existing comparison from file"""
        if self.comparison_file.exists():
            try:
                with open(self.comparison_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.attributes = [
                        KennyAttribute(
                            name=attr['name'],
                            category=AttributeCategory(attr['category']),
                            original_value=attr['original_value'],
                            enhanced_value=attr['enhanced_value'],
                            status=AttributeStatus(attr['status']),
                            is_desirable=attr.get('is_desirable'),
                            notes=attr.get('notes', ''),
                            merged_value=attr.get('merged_value')
                        )
                        for attr in data.get('attributes', [])
                    ]
                logger.info(f"✅ Loaded {len(self.attributes)} attributes from comparison file")
            except Exception as e:
                logger.warning(f"Could not load comparison: {e}")

    def _save_comparison(self):
        """Save comparison to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "attributes": [attr.to_dict() for attr in self.attributes]
            }
            with open(self.comparison_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Saved {len(self.attributes)} attributes to comparison file")
        except Exception as e:
            logger.error(f"❌ Error saving comparison: {e}")

    def _create_initial_comparison(self):
        """Create initial attribute comparison"""
        logger.info("📋 Creating initial Kenny attribute comparison...")

        # VISUAL ATTRIBUTES
        self.attributes.append(KennyAttribute(
            name="sprite_rendering",
            category=AttributeCategory.VISUAL,
            original_value="Working filled circles (not rings)",
            enhanced_value="Froot Loop rings (broken)",
            status=AttributeStatus.UNDESIRABLE,
            is_desirable=False,
            notes="Original has correct filled circles, enhanced has ring issue",
            merged_value="Use original: filled circles"
        ))

        self.attributes.append(KennyAttribute(
            name="sprite_size",
            category=AttributeCategory.VISUAL,
            original_value="Default size (working)",
            enhanced_value="Scalable size system",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has better scaling, but needs original rendering",
            merged_value="Use enhanced: scalable, but with original rendering"
        ))

        # MOVEMENT ATTRIBUTES
        self.attributes.append(KennyAttribute(
            name="movement_speed",
            category=AttributeCategory.MOVEMENT,
            original_value="Balanced speed (working)",
            enhanced_value="Balanced speed (0.5 border_walk_speed)",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Both have balanced speed - keep",
            merged_value="Use enhanced: explicit 0.5 speed"
        ))

        self.attributes.append(KennyAttribute(
            name="position_interpolation",
            category=AttributeCategory.MOVEMENT,
            original_value="Working interpolation",
            enhanced_value="smooth_interpolate_position() (fixed)",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has explicit interpolation call - keep",
            merged_value="Use enhanced: explicit interpolation"
        ))

        self.attributes.append(KennyAttribute(
            name="startup_position",
            category=AttributeCategory.MOVEMENT,
            original_value="Default position",
            enhanced_value="Top-left quadrant (fixed)",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has top-left positioning - keep",
            merged_value="Use enhanced: top-left positioning"
        ))

        self.attributes.append(KennyAttribute(
            name="zipping_off_bug",
            category=AttributeCategory.MOVEMENT,
            original_value="No zipping (working)",
            enhanced_value="Zipping off on startup (fixed)",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has fix for zipping - keep",
            merged_value="Use enhanced: position init after screen dimensions"
        ))

        # COLLABORATION ATTRIBUTES
        self.attributes.append(KennyAttribute(
            name="ace_collaboration",
            category=AttributeCategory.COLLABORATION,
            original_value="Unknown",
            enhanced_value="Collaboration system integrated",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has collaboration - keep",
            merged_value="Use enhanced: collaboration system"
        ))

        self.attributes.append(KennyAttribute(
            name="collision_avoidance",
            category=AttributeCategory.COLLABORATION,
            original_value="Unknown",
            enhanced_value="Collision avoidance with position validation",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has collision avoidance - keep",
            merged_value="Use enhanced: collision avoidance"
        ))

        # BEHAVIOR ATTRIBUTES
        self.attributes.append(KennyAttribute(
            name="error_handling",
            category=AttributeCategory.BEHAVIOR,
            original_value="Unknown",
            enhanced_value="Error handling in animation loop",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has error handling - keep",
            merged_value="Use enhanced: error handling"
        ))

        self.attributes.append(KennyAttribute(
            name="crash_detection",
            category=AttributeCategory.BEHAVIOR,
            original_value="Unknown",
            enhanced_value="Crash detection system",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Enhanced has crash detection - keep",
            merged_value="Use enhanced: crash detection"
        ))

        # INTEGRATION ATTRIBUTES
        self.attributes.append(KennyAttribute(
            name="ecosystem_integration",
            category=AttributeCategory.INTEGRATION,
            original_value="Full ecosystem (JARVIS, etc.)",
            enhanced_value="Optional ecosystem integration",
            status=AttributeStatus.DESIRABLE,
            is_desirable=True,
            notes="Original has full integration, enhanced has optional - merge both",
            merged_value="Use enhanced: optional (more flexible)"
        ))

        # Save initial comparison
        self._save_comparison()
        logger.info(f"✅ Created initial comparison with {len(self.attributes)} attributes")

    def get_desirable_attributes(self) -> List[KennyAttribute]:
        """Get all desirable attributes"""
        return [attr for attr in self.attributes if attr.is_desirable is True]

    def get_undesirable_attributes(self) -> List[KennyAttribute]:
        """Get all undesirable attributes"""
        return [attr for attr in self.attributes if attr.is_desirable is False]

    def get_merged_attributes(self) -> Dict[str, Any]:
        """Get merged attribute values (best of both)"""
        merged = {}
        for attr in self.attributes:
            if attr.merged_value is not None:
                merged[attr.name] = attr.merged_value
        return merged

    def print_comparison_report(self):
        """Print comparison report"""
        print("\n" + "=" * 80)
        print("📊 KENNY ATTRIBUTE COMPARISON REPORT")
        print("=" * 80)
        print()

        # Group by category
        by_category = {}
        for attr in self.attributes:
            cat = attr.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(attr)

        for category, attrs in sorted(by_category.items()):
            print(f"\n{category.upper()} ATTRIBUTES:")
            print("-" * 80)
            for attr in attrs:
                status_icon = "✅" if attr.is_desirable else "❌" if attr.is_desirable is False else "❓"
                print(f"{status_icon} {attr.name}")
                print(f"   Original: {attr.original_value}")
                print(f"   Enhanced: {attr.enhanced_value}")
                if attr.merged_value:
                    print(f"   Merged: {attr.merged_value}")
                if attr.notes:
                    print(f"   Notes: {attr.notes}")
                print()

        # Summary
        desirable = len(self.get_desirable_attributes())
        undesirable = len(self.get_undesirable_attributes())
        total = len(self.attributes)

        print("=" * 80)
        print("SUMMARY:")
        print(f"  Total Attributes: {total}")
        print(f"  Desirable: {desirable} ✅")
        print(f"  Undesirable: {undesirable} ❌")
        print(f"  Unknown: {total - desirable - undesirable} ❓")
        print("=" * 80)
        print()


if __name__ == "__main__":
    comparison = KennyAttributeComparison()
    comparison.print_comparison_report()

    # Show merged attributes
    print("\n" + "=" * 80)
    print("🔀 MERGED ATTRIBUTES (Best of Both)")
    print("=" * 80)
    merged = comparison.get_merged_attributes()
    for name, value in merged.items():
        print(f"  {name}: {value}")
    print("=" * 80)
