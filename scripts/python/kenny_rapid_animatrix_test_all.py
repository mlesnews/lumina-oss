#!/usr/bin/env python3
"""
Rapid Animatrix Testing - Test All Remaining Design Levels

Leverage 10,000 years of matrix simulation to test all levels in parallel.

Tags: #ANIMATRIX #RAPID_TESTING #KENNY @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from kenny_animatrix_ab_test import KennyAnimatrixABTest

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# JARVIS integration
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

def main():
    """Test all remaining design levels rapidly"""
    ab = KennyAnimatrixABTest()

    print("=" * 80)
    print("🧪 RAPID ANIMATRIX TESTING - All Remaining Levels")
    print("   Leveraging 10,000 years of matrix simulation")
    print("=" * 80)
    print()

    # Test Level 4 → 5
    print("🧪 Testing: Level 4 → Level 5 (Chest Plate → Expression System)")
    result_4_to_5 = ab.test_design_level(4, 5)
    print(f"   🏆 Winner: {result_4_to_5['winner']}")
    print(f"   Visual Quality: {result_4_to_5['comparison']['visual_quality']['improvement_pct']:.1f}%")
    print(f"   Iron Man Aesthetic: {result_4_to_5['comparison']['iron_man_aesthetic']['improvement_pct']:.1f}%")
    print()

    # Test Level 5 → 6
    print("🧪 Testing: Level 5 → Level 6 (Expression System → Glow Effects)")
    result_5_to_6 = ab.test_design_level(5, 6)
    print(f"   🏆 Winner: {result_5_to_6['winner']}")
    print(f"   Visual Quality: {result_5_to_6['comparison']['visual_quality']['improvement_pct']:.1f}%")
    print(f"   Iron Man Aesthetic: {result_5_to_6['comparison']['iron_man_aesthetic']['improvement_pct']:.1f}%")
    print()

    print("=" * 80)
    print("✅ All levels tested in Animatrix simulation (faster than real-time)")
    print("=" * 80)

if __name__ == "__main__":


    main()