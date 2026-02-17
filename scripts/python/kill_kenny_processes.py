#!/usr/bin/env python3
"""
Kill All Kenny Processes
Finds and terminates all running Kenny/IMVA processes
"""

import sys
import psutil
from pathlib import Path

def find_kenny_processes():
    """Find all Kenny/IMVA processes"""
    import os
    current_pid = os.getpid()
    kenny_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip ourselves
            if proc.pid == current_pid:
                continue

            cmdline_list = proc.info.get('cmdline', [])
            cmdline = ' '.join(str(c) for c in cmdline_list) if cmdline_list else ''
            name = proc.info.get('name', '').lower()

            # Skip kill scripts (they contain 'kenny' but we don't want to kill them)
            if 'kill_kenny' in cmdline.lower() or 'find_and_kill_kenny' in cmdline.lower():
                continue

            # Check if it's a Kenny/Iron Man VA process
            # Kenny = Iron Man Virtual Assistant (ironman_virtual_assistant.py) - shows "Mark 7"
            # Enhanced Kenny = kenny_imva_enhanced.py - the enhanced version
            if 'kenny_imva_enhanced' in cmdline.lower():
                kenny_processes.append(proc)
            elif 'ironman_virtual_assistant' in cmdline.lower():
                kenny_processes.append(proc)  # Original Kenny (Mark 7)
            elif 'kenny' in cmdline.lower() and ('enhanced' in cmdline.lower() or 'imva' in cmdline.lower()):
                kenny_processes.append(proc)
            elif 'imva' in cmdline.lower() and 'kenny' in cmdline.lower():
                kenny_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return kenny_processes

def kill_kenny_processes():
    """Kill all Kenny processes"""
    processes = find_kenny_processes()

    if not processes:
        print("✅ No Kenny processes found")
        return

    print(f"🔍 Found {len(processes)} Kenny process(es):")
    for proc in processes:
        try:
            cmdline_list = proc.info.get('cmdline', [])
            cmdline_str = ' '.join(str(c) for c in cmdline_list) if cmdline_list else 'N/A'
            print(f"   PID {proc.pid}: {proc.info.get('name', 'Unknown')}")
            print(f"      Command: {cmdline_str[:100]}")
        except:
            pass

    print("\n🛑 Terminating Kenny processes...")
    for proc in processes:
        try:
            proc.terminate()
            print(f"   ✅ Terminated PID {proc.pid}")
        except Exception as e:
            print(f"   ❌ Error terminating PID {proc.pid}: {e}")

    # Wait a moment, then force kill if needed
    import time
    time.sleep(1)

    for proc in processes:
        try:
            if proc.is_running():
                proc.kill()
                print(f"   🔪 Force killed PID {proc.pid}")
        except:
            pass

    print("\n✅ All Kenny processes terminated")

if __name__ == "__main__":
    kill_kenny_processes()
