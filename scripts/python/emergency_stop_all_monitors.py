#!/usr/bin/env python3
"""
Emergency Stop All Monitors

Stops all JARVIS monitoring processes to prevent system freeze.
Use this when the system is freezing due to too many background processes.

Tags: #EMERGENCY #SYSTEM_STABILITY #RESOURCE_MANAGEMENT @JARVIS @LUMINA
"""

import sys
import subprocess
import psutil
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

def stop_all_monitors():
    """Stop all JARVIS monitoring processes"""
    stopped = []

    # Find all Python processes running JARVIS scripts
    monitor_scripts = [
        "jarvis_ask_processor.py",
        "jarvis_integrated_live_monitor.py",
        "jarvis_compound_log_health_monitor.py",
        "jarvis_unified_health_system.py",
        "jarvis_compound_log_admin.py",
        "jarvis_ask_live_monitor.py",
        "jarvis_auto_accept_monitor.py",
        "ironman_virtual_assistant.py",
        "process_watchdog.py",  # Don't kill the watchdog itself
        "monitoring/monitor.py",
        "monitor_ai_usage_and_enforce_local_first.py"
    ]

    # Also stop by project path
    project_path_str = str(project_root).lower()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline') or []
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    found_script = False
                    # Check for script names
                    for script in monitor_scripts:
                        if script.lower() in cmdline_str:
                            print(f"🛑 Stopping process {proc.info['pid']}: {script}")
                            proc.terminate()
                            stopped.append((proc.info['pid'], script))
                            found_script = True
                            break
                    # Also check for project path (catch any JARVIS process)
                    if not found_script and project_path_str in cmdline_str and any(keyword in cmdline_str for keyword in ['jarvis', 'lumina', 'monitor', 'health']):
                        print(f"🛑 Stopping JARVIS process {proc.info['pid']}: {cmdline[0] if cmdline else 'unknown'}")
                        proc.terminate()
                        stopped.append((proc.info['pid'], 'jarvis_related'))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Wait for processes to terminate
    import time
    time.sleep(2)

    # Force kill any remaining
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline') or []
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    found_script = False
                    for script in monitor_scripts:
                        if script.lower() in cmdline_str:
                            print(f"💀 Force killing process {proc.info['pid']}: {script}")
                            proc.kill()
                            found_script = True
                            break
                    if not found_script and project_path_str in cmdline_str and any(keyword in cmdline_str for keyword in ['jarvis', 'lumina', 'monitor', 'health']):
                        print(f"💀 Force killing JARVIS process {proc.info['pid']}")
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    print(f"\n✅ Stopped {len(stopped)} monitoring processes")
    return stopped

if __name__ == "__main__":
    print("🚨 EMERGENCY STOP: Stopping all JARVIS monitoring processes...")
    stopped = stop_all_monitors()
    print(f"\n📊 Summary: {len(stopped)} processes stopped")
