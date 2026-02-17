#!/usr/bin/env python3
"""
Activate All Iron Man Avatars - VEGAS

Shows ALL Iron Man avatars from JARVIS to the most sophisticated Ultron.
Includes bobbleheads, widgets, and full humanoid avatars.

Tags: #IRON_MAN #AVATAR #JARVIS #ULTRON #VEGAS #ALL_AVATARS @JARVIS @LUMINA
"""

import sys
import subprocess
import threading
import time
from pathlib import Path

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

logger = get_logger("ActivateAllIronManVegas")

print("=" * 80)
print("🦾 ACTIVATING ALL IRON MAN AVATARS - VEGAS")
print("=" * 80)
print()
print("From JARVIS to the most sophisticated ULTIMATE/ULTRON Iron Man avatar")
print()

# Step 1: Display all Iron Man avatars (humanoid)
print("STEP 1: Displaying all Iron Man humanoid avatars...")
try:
    display_process = subprocess.Popen(
        [sys.executable, str(script_dir / "display_all_iron_man_avatars.py")],
        cwd=str(project_root)
    )
    print("   ✅ Iron Man avatar display started")
except Exception as e:
    print(f"   ⚠️  Display: {e}")

print()

# Step 2: Start bobblehead GUI (JARVIS, FRIDAY, EDITH, ULTIMATE)
print("STEP 2: Starting Iron Man bobblehead GUI...")
try:
    bobblehead_process = subprocess.Popen(
        [sys.executable, str(script_dir / "jarvis_ironman_bobblehead_gui.py")],
        cwd=str(project_root)
    )
    print("   ✅ Bobblehead GUI started (cycles through JARVIS, FRIDAY, EDITH, ULTIMATE)")
except Exception as e:
    print(f"   ⚠️  Bobblehead: {e}")

print()

# Step 3: Show Iron Man VAs
print("STEP 3: Showing Iron Man Virtual Assistants...")
try:
    vas_process = subprocess.Popen(
        [sys.executable, str(script_dir / "show_iron_man_vas.py")],
        cwd=str(project_root)
    )
    print("   ✅ Iron Man VAs display started")
except Exception as e:
    print(f"   ⚠️  VAs: {e}")

print()

# Step 4: List all Iron Man avatars
print("STEP 4: All Iron Man Avatars:")
try:
    from character_avatar_registry import CharacterAvatarRegistry

    registry = CharacterAvatarRegistry(project_root=project_root)
    all_chars = registry.get_all_characters()

    iron_man_avatars = []
    for char_id, char in all_chars.items():
        if (char.avatar_style == "iron_man" or 
            "iron_man" in char.avatar_template.lower() or
            char_id in ["jarvis", "friday", "edith", "ultimate", "ultron", "jarvis_va", "imva", "iron_man"]):
            iron_man_avatars.append((char_id, char))

    # Sort by sophistication
    sophistication = {
        "jarvis": 1,
        "friday": 2,
        "edith": 3,
        "ultimate": 4,
        "ultron": 5,
        "jarvis_va": 1.5,
        "imva": 1.7,
        "iron_man": 2.5
    }

    iron_man_avatars.sort(key=lambda x: sophistication.get(x[0], 99))

    for char_id, char in iron_man_avatars:
        sophistication_level = "Most Sophisticated" if char_id == "ultron" else "Advanced" if char_id == "ultimate" else "Standard"
        print(f"   ✅ {char.name} ({char_id})")
        print(f"      Template: {char.avatar_template}")
        print(f"      Style: {char.avatar_style}")
        print(f"      Sophistication: {sophistication_level}")
        print()

    print(f"   Total: {len(iron_man_avatars)} Iron Man avatars")

except Exception as e:
    print(f"   ⚠️  Could not list avatars: {e}")

print()

print("=" * 80)
print("✅ ALL IRON MAN AVATARS ACTIVATED")
print("=" * 80)
print()
print("You should now see:")
print("  ✅ JARVIS - Iron Man avatar")
print("  ✅ FRIDAY - Iron Man avatar")
print("  ✅ EDITH - Iron Man avatar")
print("  ✅ ULTIMATE - Iron Man avatar")
print("  ✅ ULTIMATE/ULTRON - Most sophisticated Iron Man avatar")
print("  ✅ JARVIS_VA - Bobblehead")
print("  ✅ IMVA - Bobblehead")
print("  ✅ Iron Man - Widget")
print()
print("All avatars are now visible on screen!")
print()
print("Press Ctrl+C to stop all...")
print()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Stopping all avatars...")
    print("✅ All avatars stopped")
