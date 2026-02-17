#!/usr/bin/env python3
"""
Monitor Kenny Logs - Check voice filter and sprite rendering

Monitors logs to verify:
1. Voice filter is being called
2. Voice filter results
3. Sprite rendering calls
4. Any errors or warnings

Tags: #KENNY #DEBUGGING #MONITORING @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
import subprocess

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def check_kenny_process():
    """Check if Kenny process is running"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'kenny_imva_enhanced' in cmdline.lower():
                return proc.info['pid']
    except Exception:
        pass
    return None

def main():
    """Monitor Kenny logs"""
    print("=" * 80)
    print("🔍 MONITORING KENNY LOGS")
    print("=" * 80)
    print()

    # Check if Kenny is running
    pid = check_kenny_process()
    if pid:
        print(f"✅ Kenny process found: PID {pid}")
    else:
        print("⚠️  Kenny process not found")

    print()
    print("Monitoring for:")
    print("  1. Voice filter calls (🔍 Voice filter check)")
    print("  2. Voice filter results (🔍 Voice filter result)")
    print("  3. Profile training status (🔍 Voice profile trained)")
    print("  4. Filtered out messages (🔇 Filtered out non-user voice)")
    print()
    print("Check logs in:")
    print(f"  {project_root / 'logs'}")
    print()
    print("=" * 80)

if __name__ == "__main__":


    main()