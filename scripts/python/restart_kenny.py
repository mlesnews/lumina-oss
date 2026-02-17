#!/usr/bin/env python3
"""
Restart Kenny - Kill current process and restart with new code
Wrapper script that kills existing Kenny processes and restarts him
"""

import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.kill_kenny_processes import kill_kenny_processes


def restart_kenny(*args):
    """
    Restart Kenny - kill current process and restart with new code

    Args:
        *args: Additional arguments to pass to kenny_imva_enhanced.py
               (e.g., '--match-ace', '--size', '60', etc.)
    """
    print("=" * 80)
    print("🔄 RESTARTING KENNY (@IMVA)")
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

    # Step 3: Restart Kenny with new code
    print("🚀 Step 3: Starting Kenny with new code...")

    # Check if user wants original Kenny (ironman_virtual_assistant.py) or enhanced
    # Default to original Kenny (the working one, not the Froot Loop version)
    use_original = '--original' in args or '--use-original' in args
    if use_original:
        args = [a for a in args if a not in ['--original', '--use-original']]
        kenny_script = project_root / "scripts" / "python" / "ironman_virtual_assistant.py"
        print("   Using ORIGINAL Kenny (ironman_virtual_assistant.py)")
    else:
        kenny_script = project_root / "scripts" / "python" / "kenny_imva_enhanced.py"
        print("   Using ENHANCED Kenny (kenny_imva_enhanced.py)")

    # Build command
    cmd = [sys.executable, str(kenny_script)] + list(args)

    print(f"   Command: {' '.join(cmd)}")
    print()
    print("=" * 80)
    print("✅ Kenny restart initiated")
    print("   Window should appear shortly...")
    print("   Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Start Kenny (this will block until interrupted)
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print()
        print("🛑 Kenny stopped by user")
        print("   Run this script again to restart")
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Error starting Kenny: {e}")
        sys.exit(1)


def main():
    """Main execution"""
    # Get all command-line arguments (except script name)
    args = sys.argv[1:]

    # Handle --help manually to show usage
    if '--help' in args or '-h' in args:
        print("=" * 80)
        print("🔄 RESTART KENNY - Kill current process and restart with new code")
        print("=" * 80)
        print()
        print("Usage:")
        print("  python restart_kenny.py [kenny_args...]")
        print()
        print("Arguments are passed through to kenny_imva_enhanced.py")
        print()
        print("Examples:")
        print("  python restart_kenny.py --original          # Start original Kenny (ironman_virtual_assistant.py)")
        print("  python restart_kenny.py                      # Start enhanced Kenny (kenny_imva_enhanced.py)")
        print("  python restart_kenny.py --original --start  # Original Kenny with --start flag")
        print("  python restart_kenny.py --match-ace          # Enhanced Kenny with --match-ace")
        print()
        print("=" * 80)
        sys.exit(0)

    # Start Kenny with all arguments passed through
    restart_kenny(*args)


if __name__ == "__main__":


    main()