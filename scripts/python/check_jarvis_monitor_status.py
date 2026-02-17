#!/usr/bin/env python3
"""
Quick status check for JARVIS Desktop Monitor

Tags: #JARVIS #MONITORING #STATUS @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Check PID file
pid_file = project_root / "data" / "jarvis_desktop_monitor.pid"
if pid_file.exists():
    with open(pid_file) as f:
        pid = f.read().strip()
    print(f"✅ Monitor PID file exists: {pid}")
else:
    print("⚠️  Monitor PID file not found")

# Check recent screenshots
screenshot_dir = project_root / "data" / "manus_rdp_captures"
if screenshot_dir.exists():
    screenshots = sorted(screenshot_dir.glob("rdp_screenshot_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if screenshots:
        latest = screenshots[0]
        age = (datetime.now().timestamp() - latest.stat().st_mtime)
        print(f"✅ Latest screenshot: {latest.name}")
        print(f"   Age: {age:.1f} seconds ago")
        if age < 10:
            print("   ✅ Monitor is ACTIVE (capturing screenshots)")
        else:
            print(f"   ⚠️  Monitor may be inactive (last capture {age:.1f}s ago)")
    else:
        print("⚠️  No screenshots found")
else:
    print("⚠️  Screenshot directory not found")

# Check JARVIS process
import subprocess
try:
    result = subprocess.run(
        ["powershell", "-Command",
         "Get-Process python* | Where-Object {$_.MainWindowTitle -like '*JARVIS*'} | Select-Object Id, StartTime, Responding, MainWindowTitle | Format-List"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if "JARVIS" in result.stdout:
        print("✅ JARVIS process(es) found:")
        # Extract process info
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Id' in line or 'StartTime' in line or 'Responding' in line:
                print(f"   {line.strip()}")
    else:
        print("⚠️  JARVIS process not found")
        print(f"   PowerShell output: {result.stdout[:200]}")
except Exception as e:
    print(f"⚠️  Could not check JARVIS process: {e}")
