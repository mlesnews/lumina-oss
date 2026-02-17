#!/usr/bin/env python3
"""
System Status Report

Provides comprehensive status report:
- IR Camera status
- Virtual Assistant status (JARVIS, ACE, IMVAs)
- Headless startup installation status
- Luminous system log status

Tags: #STATUS #REPORT #SYSTEM_CHECK @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SystemStatusReport")


def check_ir_camera_status():
    """Check IR camera status"""
    print("📹 IR CAMERA STATUS")
    print("-" * 80)

    try:
        import cv2

        ir_found = False
        for idx in [1, 2, 3]:
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ IR camera ON at index {idx}")
                        print(f"   Frame size: {frame.shape}")
                        ir_found = True
                        cap.release()
                        break
                cap.release()
            except:
                continue

        if not ir_found:
            print("❌ IR camera OFF (not found at indices 1, 2, or 3)")
            print("   ⚠️  Only regular camera found (emits bright white light)")

    except ImportError:
        print("❌ OpenCV not available")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def check_va_status():
    """Check Virtual Assistant status"""
    print("🤖 VIRTUAL ASSISTANT STATUS")
    print("-" * 80)

    try:
        import psutil

        vas = {
            "JARVIS": ["jarvis", "jarvis_narrator", "jarvis_avatar"],
            "ACE": ["ace", "ironman_va", "ironman_animated"],
            "IMVA": ["imva", "kenny_imva", "replika_inspired"]
        }

        for va_name, process_names in vas.items():
            found = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()

                    for name in process_names:
                        if name.lower() in proc_name or name.lower() in cmdline:
                            print(f"✅ {va_name} is RUNNING (PID: {proc.info['pid']})")
                            found = True
                            break

                    if found:
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not found:
                print(f"❌ {va_name} is NOT RUNNING")

    except ImportError:
        print("⚠️  psutil not available - using basic check")
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*jarvis*' -or $_.ProcessName -like '*ace*' -or $_.ProcessName -like '*imva*'} | Select-Object ProcessName"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                print("✅ Some VA processes found")
            else:
                print("❌ No VA processes found")
        except:
            print("❌ Could not check processes")

    print()


def check_headless_startup():
    """Check headless startup installation"""
    print("🚀 HEADLESS STARTUP STATUS")
    print("-" * 80)

    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-ScheduledTask -TaskName 'JARVISHeadlessStartup' -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            print("✅ Headless startup task is INSTALLED")
            print("   Task will run on system reboot")
        else:
            print("❌ Headless startup task is NOT INSTALLED")
            print(r"   Run: .\scripts\powershell\Install-JARVISHeadlessStartup.ps1")
    except Exception as e:
        print(f"⚠️  Could not check: {e}")

    print()


def check_luminous_log():
    """Check Luminous system log status"""
    print("💍 LUMINOUS SYSTEM LOG STATUS")
    print("-" * 80)

    try:
        from luminous_system_log_aggregator import get_luminous_log

        log = get_luminous_log()
        stats = log.get_log_statistics()

        print(f"✅ Luminous system log is ACTIVE")
        print(f"   Log file: {stats['log_file']}")
        print(f"   Active sources: {stats['active_sources']}")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   File size: {stats['log_file_size']:,} bytes")

        if stats['active_sources'] > 0:
            print(f"   Sources: {', '.join(stats['sources'][:5])}")
            if len(stats['sources']) > 5:
                print(f"   ... and {len(stats['sources']) - 5} more")

    except ImportError:
        print("❌ Luminous system log not available")
    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()


def main():
    """Main function"""
    print("=" * 80)
    print("JARVIS SYSTEM STATUS REPORT")
    print("=" * 80)
    print()

    check_ir_camera_status()
    check_va_status()
    check_headless_startup()
    check_luminous_log()

    print("=" * 80)
    print()
    print("💡 To start missing VAs:")
    print("   python scripts/python/check_and_start_vas.py")
    print()
    print("💡 To tail Luminous system log:")
    print("   python scripts/python/luminous_log_tail.py")
    print()
    print("=" * 80)


if __name__ == "__main__":


    main()