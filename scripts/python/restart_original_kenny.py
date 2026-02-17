#!/usr/bin/env python3
"""
Restart Original Kenny - Kill current process and restart original Kenny (ironman_virtual_assistant.py)

This is the working version, not the enhanced one with Froot Loop issues.
"""

import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.kill_kenny_processes import kill_kenny_processes


def restart_original_kenny(*args):
    """
    Restart Original Kenny - kill current process and restart original Kenny

    Args:
        *args: Additional arguments to pass to ironman_virtual_assistant.py
               (e.g., '--start')
    """
    print("=" * 80)
    print("🔄 RESTARTING ORIGINAL KENNY (Iron Man Virtual Assistant)")
    print("=" * 80)
    print()

    # Step 1: Kill current Kenny processes
    print("🔍 Step 1: Killing current Kenny processes...")
    kill_kenny_processes()
    print()

    # Step 2: Wait a moment for processes to fully terminate
    print("⏳ Step 2: Waiting for processes to terminate...")
    time.sleep(1.0)
    print("   ✅ Wait complete")
    print()

    # Step 3: Restart Original Kenny
    print("🚀 Step 3: Starting ORIGINAL Kenny (ironman_virtual_assistant.py)...")
    kenny_script = project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

    # Build command (add --start if not present)
    cmd = [sys.executable, str(kenny_script)]
    if '--start' not in args:
        cmd.append('--start')
    cmd.extend(list(args))

    print(f"   Command: {' '.join(cmd)}")
    print()
    print("=" * 80)
    print("✅ Original Kenny restart initiated")
    print("   Window should appear shortly...")
    print("   Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Start Original Kenny (this will block until interrupted)
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print()
        print("🛑 Original Kenny stopped by user")
        print("   Run this script again to restart")
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Error starting Original Kenny: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Get all command-line arguments (except script name)
    args = sys.argv[1:]

    # Handle --help
    if '--help' in args or '-h' in args:
        print("=" * 80)
        print("🔄 RESTART ORIGINAL KENNY - Kill and restart original Kenny")
        print("=" * 80)
        print()
        print("This starts the ORIGINAL Kenny (ironman_virtual_assistant.py)")
        print("Not the enhanced version with Froot Loop issues.")
        print()
        print("Usage:")
        print("  python restart_original_kenny.py [args...]")
        print()
        print("Arguments are passed through to ironman_virtual_assistant.py")
        print()
        print("Examples:")
        print("  python restart_original_kenny.py")
        print("  python restart_original_kenny.py --start")
        print()
        print("=" * 80)
        sys.exit(0)

    # Start Original Kenny
    restart_original_kenny(*args)
