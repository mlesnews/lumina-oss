#!/usr/bin/env python3
"""
Find and Kill Kenny - More aggressive version
"""

import sys
import time
import psutil

def find_all_kenny_processes():
    """Find all processes that might be Kenny"""
    kenny_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
        try:
            cmdline_list = proc.info.get('cmdline', [])
            cmdline_str = ' '.join(str(c) for c in cmdline_list) if cmdline_list else ''
            name = proc.info.get('name', '')

            # Check if it's a Kenny process
            if 'kenny' in cmdline_str.lower() or 'kenny' in name.lower():
                kenny_processes.append(proc)
            elif 'imva' in cmdline_str.lower() and ('kenny' in cmdline_str.lower() or 'enhanced' in cmdline_str.lower()):
                kenny_processes.append(proc)
            elif 'restart_kenny' in cmdline_str.lower():
                kenny_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception as e:
            print(f"   ⚠️  Error checking process: {e}", file=sys.stderr)
            continue

    return kenny_processes

def kill_all_kenny():
    """Kill all Kenny processes aggressively"""
    print("🔍 Searching for Kenny processes...")
    processes = find_all_kenny_processes()

    if not processes:
        print("✅ No Kenny processes found")
        return True

    print(f"\n🔍 Found {len(processes)} Kenny process(es):")
    for proc in processes:
        try:
            cmdline_list = proc.info.get('cmdline', [])
            cmdline_str = ' '.join(str(c) for c in cmdline_list[:3]) if cmdline_list else 'N/A'
            print(f"   PID {proc.pid}: {cmdline_str}")
        except:
            print(f"   PID {proc.pid}: (could not get command line)")

    print("\n🛑 Terminating processes...")
    killed_any = False

    for proc in processes:
        try:
            pid = proc.pid
            proc.terminate()
            print(f"   ✅ Sent terminate to PID {pid}")
            killed_any = True
        except psutil.NoSuchProcess:
            print(f"   ⚠️  PID {proc.pid} already gone")
        except Exception as e:
            print(f"   ❌ Error terminating PID {proc.pid}: {e}")

    if not killed_any:
        print("   ⚠️  No processes terminated")
        return False

    # Wait for graceful termination
    print("\n⏳ Waiting for graceful termination...")
    time.sleep(2)

    # Force kill any that are still running
    print("\n🔪 Force killing any remaining processes...")
    force_killed = False

    for proc in processes:
        try:
            if proc.is_running():
                proc.kill()
                print(f"   🔪 Force killed PID {proc.pid}")
                force_killed = True
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            print(f"   ⚠️  Error force killing PID {proc.pid}: {e}")

    if not force_killed:
        print("   ✅ All processes terminated gracefully")

    print("\n✅ Done")
    return True

if __name__ == "__main__":
    try:
        kill_all_kenny()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
