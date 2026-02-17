#!/usr/bin/env python3
"""Check what Python processes are running"""

import psutil

print("Checking all Python processes...\n")

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'python' in proc.info.get('name', '').lower():
            cmdline = proc.info.get('cmdline', [])
            cmdline_str = ' '.join(str(c) for c in cmdline[:5]) if cmdline else 'N/A'
            print(f"PID {proc.pid}: {cmdline_str}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except Exception as e:
        print(f"Error checking process: {e}")

print("\nChecking specifically for Kenny processes...\n")

kenny_found = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline_list = proc.info.get('cmdline', [])
        cmdline_str = ' '.join(str(c) for c in cmdline_list) if cmdline_list else ''

        if 'kenny_imva_enhanced' in cmdline_str.lower():
            print(f"✅ Found Kenny process: PID {proc.pid}")
            print(f"   Command: {cmdline_str[:200]}")
            kenny_found = True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if not kenny_found:
    print("❌ No Kenny processes found")
