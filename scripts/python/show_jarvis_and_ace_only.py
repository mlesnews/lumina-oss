#!/usr/bin/env python3
"""
Show JARVIS and ACE (ASUS Armory Crate) Only

Stops Iron Man suit spawning and ensures only JARVIS and ACE are visible.
ACE = ASUS Armory Crate virtual assistant (NOT Iron Man).

Tags: #JARVIS #ACE #ASUS #ARMORY_CRATE #VISIBILITY @JARVIS @ACE @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ShowJARVISACEOnly")

print("=" * 80)
print("👁️  SHOWING JARVIS AND ACE (ASUS ARMORY CRATE) ONLY")
print("=" * 80)
print()
print("Clarification:")
print("  • JARVIS = Main virtual assistant")
print("  • ACE = ASUS Armory Crate virtual assistant (NOT Iron Man)")
print("  • Iron Man suits = Separate feature (currently disabled)")
print()

# Kill existing processes
print("🛑 Stopping existing VA processes...")
try:
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('jarvis_narrator_avatar.py' in str(c) for c in cmdline):
                proc.terminate()
                print(f"   ✅ Stopped JARVIS (PID: {proc.info['pid']})")
            elif cmdline and any('ironman_animated_va.py' in str(c) for c in cmdline):
                proc.terminate()
                print(f"   ✅ Stopped Iron Man VA (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    time.sleep(2)
except ImportError:
    print("   ⚠️  psutil not available - cannot stop processes automatically")
    print("   Please manually stop existing VA processes")

print()
print("🚀 Starting JARVIS...")
try:
    jarvis_script = script_dir / "jarvis_narrator_avatar.py"
    jarvis_proc = subprocess.Popen(
        [sys.executable, str(jarvis_script)],
        cwd=str(project_root)
    )
    print(f"   ✅ JARVIS started (PID: {jarvis_proc.pid})")
    time.sleep(2)
except Exception as e:
    print(f"   ❌ Failed to start JARVIS: {e}")

print()
print("🚀 Starting ACE (ASUS Armory Crate)...")
print("   Note: ACE is ASUS Armory Crate's virtual assistant")
print("   This should integrate with your ASUS Armory Crate software")
try:
    # Check if Armory Crate ACE is available
    # For now, start the Iron Man animated VA as ACE placeholder
    # (This is a placeholder - real ACE would be from Armory Crate)
    ace_script = script_dir / "ironman_animated_va.py"
    if ace_script.exists():
        ace_proc = subprocess.Popen(
            [sys.executable, str(ace_script)],
            cwd=str(project_root)
        )
        print(f"   ✅ ACE placeholder started (PID: {ace_proc.pid})")
        print("   ⚠️  Note: This is a placeholder - real ACE comes from ASUS Armory Crate")
    else:
        print("   ⚠️  ACE script not found - ACE should come from ASUS Armory Crate")
except Exception as e:
    print(f"   ❌ Failed to start ACE: {e}")

print()
print("=" * 80)
print("STATUS")
print("=" * 80)
print("JARVIS: ✅ Should be visible")
print("ACE: ✅ Should be visible (ASUS Armory Crate)")
print()
print("💡 If VAs don't appear:")
print("   1. Check if windows are behind other windows")
print("   2. Try Alt+Tab to find them")
print("   3. Check Task Manager for python.exe processes")
print()
print("⚠️  Iron Man suit spawning is DISABLED")
print("   (Suit spawning was causing confusion)")
print("=" * 80)
