#!/usr/bin/env python3
"""
Kill ALL NEO Browser Processes - Emergency Cleanup
#JARVIS #NEO #CLEANUP
"""

import subprocess
import sys
import time

def kill_all_neo():
    """Kill ALL NEO processes aggressively"""
    print("🔪 KILLING ALL NEO PROCESSES...")

    # Method 1: taskkill with /T (kill tree)
    try:
        result = subprocess.run(
            ['taskkill', '/F', '/IM', 'neo.exe', '/T'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )
        print(f"taskkill result: {result.stdout}")
        if result.stderr:
            print(f"taskkill errors: {result.stderr}")
    except Exception as e:
        print(f"taskkill error: {e}")

    # Method 2: psutil if available
    try:
        import psutil
        killed = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                if 'neo' in name:
                    print(f"Killing: PID {proc.info['pid']} ({proc.info['name']})")
                    proc.kill()
                    killed += 1
            except:
                pass
        print(f"Killed {killed} processes via psutil")
    except ImportError:
        print("psutil not available")
    except Exception as e:
        print(f"psutil error: {e}")

    time.sleep(3)

    # Verify
    try:
        import psutil
        remaining = [p.info['pid'] for p in psutil.process_iter(['pid', 'name']) if 'neo' in p.info['name'].lower()]
        if remaining:
            print(f"⚠️  {len(remaining)} processes still running: {remaining}")
        else:
            print("✅ All NEO processes killed")
    except:
        pass

if __name__ == "__main__":
    kill_all_neo()
