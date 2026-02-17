#!/usr/bin/env python3
"""
Force Kill IMVA - Aggressive Kill

Kills IMVA by window title, process name, and all related processes.
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def kill_by_window_title():
    """Kill processes by window title"""
    print("🔍 Searching for IMVA windows...")

    # Try using PowerShell to find windows
    ps_cmd = """
    Get-Process | Where-Object {
        $_.MainWindowTitle -like '*JARVIS*' -or
        $_.MainWindowTitle -like '*Iron*' -or
        $_.MainWindowTitle -like '*IMVA*' -or
        $_.MainWindowTitle -like '*Bobblehead*'
    } | ForEach-Object {
        Write-Host "Found: $($_.ProcessName) (PID: $($_.Id)) - Window: $($_.MainWindowTitle)"
        Stop-Process -Id $_.Id -Force
    }
    """

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
    except Exception as e:
        print(f"Window title kill error: {e}")

def kill_by_process_name():
    """Kill all Python processes that might be IMVA"""
    print("\n🔍 Killing Python processes with IMVA scripts...")

    if HAS_PSUTIL:
        killed = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue

                cmdline_str = ' '.join(str(c) for c in cmdline).lower()

                # Check for IMVA-related scripts
                imva_keywords = [
                    'ironman',
                    'bobblehead',
                    'jarvis_ironman',
                    'imva'
                ]

                if any(keyword in cmdline_str for keyword in imva_keywords):
                    pid = proc.info['pid']
                    print(f"   🛑 Killing PID {pid}: {cmdline_str[:80]}")
                    try:
                        proc.terminate()
                        time.sleep(0.5)
                        if proc.is_running():
                            proc.kill()
                        killed += 1
                        print(f"      ✅ Killed PID {pid}")
                    except Exception as e:
                        print(f"      ⚠️  Error killing PID {pid}: {e}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        print(f"\n✅ Killed {killed} IMVA processes")
    else:
        # Fallback to PowerShell
        ps_cmd = """
        Get-Process python -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like '*ironman*' -or
            $_.CommandLine -like '*bobblehead*' -or
            $_.CommandLine -like '*jarvis_ironman*'
        } | Stop-Process -Force
        """
        subprocess.run(["powershell", "-Command", ps_cmd], timeout=10)

def kill_all_python_vas():
    """Kill all Python processes that are VAs"""
    print("\n🔍 Killing all VA Python processes...")

    va_scripts = [
        'jarvis_default_va.py',
        'jarvis_va_chat_coordinator.py',
        'jarvis_ironman_bobblehead_gui.py',
        'jarvis_acva_combat_demo.py'
    ]

    if HAS_PSUTIL:
        killed = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info.get('name', '').lower() != 'python.exe':
                    continue

                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue

                cmdline_str = ' '.join(str(c) for c in cmdline).lower()

                if any(script in cmdline_str for script in va_scripts):
                    pid = proc.info['pid']
                    print(f"   🛑 Killing VA PID {pid}")
                    try:
                        proc.terminate()
                        time.sleep(0.5)
                        if proc.is_running():
                            proc.kill()
                        killed += 1
                    except Exception as e:
                        print(f"      ⚠️  Error: {e}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        print(f"\n✅ Killed {killed} VA processes")
        time.sleep(2)

if __name__ == "__main__":
    print("=" * 80)
    print("🛑 FORCE KILLING IMVA")
    print("=" * 80)
    print()

    # Method 1: Kill by window title
    kill_by_window_title()
    time.sleep(1)

    # Method 2: Kill by process name
    kill_by_process_name()
    time.sleep(1)

    # Method 3: Kill all VA processes
    kill_all_python_vas()

    print()
    print("=" * 80)
    print("✅ FORCE KILL COMPLETE")
    print("=" * 80)
