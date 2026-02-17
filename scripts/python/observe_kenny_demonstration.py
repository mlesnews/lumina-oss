#!/usr/bin/env python3
"""
Observe Kenny's Demonstration
Watch what Kenny is trying to show - visual indicators, movements, behaviors
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'scripts' / 'python'))

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced
    from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def observe_kenny():
    """Observe what Kenny is demonstrating"""
    print("=" * 80)
    print("👀 OBSERVING KENNY'S DEMONSTRATION")
    print("=" * 80)
    print()

    # Check Kenny's state
    print("📊 KENNY'S CURRENT STATE:")
    print("-" * 80)

    # Check if enhanced Kenny is running
    try:
        kenny = KennyIMVAEnhanced()

        print("✅ Enhanced Kenny initialized")
        print(f"   State: {kenny.state}")
        print(f"   Smooth Interpolation: {kenny.smooth_interpolation}")
        print(f"   Interpolation Factor: {kenny.interpolation_factor}")
        print(f"   Movement Speed: {kenny.movement_speed}")
        print(f"   Wander Enabled: {kenny.wander_enabled}")
        print(f"   Wander Target Distance: {kenny.wander_target_distance}")
        print(f"   ACES Movement Learned: {kenny.aces_movement_learned}")
        print(f"   Learning from Ace: {kenny.learning_from_ace}")
        print()

        # Visual indicators
        print("🎨 VISUAL INDICATORS:")
        print("-" * 80)
        if kenny.learning_from_ace:
            print("   🟢 Green indicator (top-right): Learning from Ace")
        if kenny.aces_movement_learned:
            print("   🔵 Cyan indicator (top-left): ACES movement learned")
        if kenny.current_notification:
            print(f"   🔴 Red notification dot: {kenny.current_notification.message}")
        print()

        # What Kenny might be demonstrating
        print("💡 WHAT KENNY MIGHT BE SHOWING:")
        print("-" * 80)

        if kenny.aces_movement_learned:
            print("   ✅ Kenny has learned ACES-like smooth movement!")
            print("      - Smooth interpolation enabled")
            print("      - Continuous wandering active")
            print("      - Professional polish applied")
            print()
            print("   🎯 DEMONSTRATION: Kenny is showing smooth, ACES-like movement")
            print("      Watch for:")
            print("      • Smooth, fluid motion (not jerky)")
            print("      • Continuous wandering (always moving)")
            print("      • Professional polish (like Ace)")
            print("      • Cyan indicator showing ACES movement learned")

        if kenny.learning_from_ace:
            print("   📚 Kenny is currently learning from Ace!")
            print("      - Green indicator should be visible")
            print("      - Learning ACES movement techniques")
            print()

        if not kenny.aces_movement_learned and not kenny.learning_from_ace:
            print("   ⚠️  Kenny hasn't learned ACES movement yet")
            print("      - Run with --learn-aces to start learning")
            print("      - Or let Kenny observe Ace's movement")
            print()

        # Movement demonstration
        print("🏃 MOVEMENT DEMONSTRATION:")
        print("-" * 80)
        print(f"   Current Position: ({kenny.x}, {kenny.y})")
        print(f"   Target Position: ({kenny.target_x}, {kenny.target_y})")
        print(f"   Border: {kenny.current_border.value}")
        print(f"   Border Position: {kenny.border_position:.2f}")
        print()

    except Exception as e:
        print(f"❌ Error observing Kenny: {e}")
        import traceback
        traceback.print_exc()

    # Check for Ace
    print("🔍 CHECKING FOR ACE:")
    print("-" * 80)
    try:
        ace = ACVAArmouryCrateIntegration()
        ace_window = ace.find_armoury_crate_va()

        if ace_window:
            print("✅ Ace (ACES) found!")
            info = ace.get_acva_window_info()
            print(f"   Window: {info.get('title', 'Unknown')}")
            print(f"   Position: {info.get('position', {})}")
            print()
            print("   💡 Kenny can learn from Ace if Ace is visible!")
        else:
            print("⚠️  Ace (ACES) not found")
            print("   - Armoury Crate Virtual Assistant not running")
            print("   - Kenny can still demonstrate learned ACES movement")
            print()
    except Exception as e:
        print(f"⚠️  Could not check for Ace: {e}")

    print("=" * 80)
    print("👀 OBSERVATION COMPLETE")
    print("=" * 80)
    print()
    print("💡 TIP: Watch Kenny's movement on screen:")
    print("   • Smooth = ACES movement learned")
    print("   • Jerky = Still learning")
    print("   • Green dot = Currently learning")
    print("   • Cyan dot = ACES movement mastered")
    print()

if __name__ == "__main__":
    observe_kenny()
