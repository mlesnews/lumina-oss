#!/usr/bin/env python3
"""
Check and Start Virtual Assistants

Checks status of VAs (JARVIS, ACE, IMVAs) and starts them if not running.
Also checks IR camera status.

Tags: #VA #STARTUP #STATUS_CHECK #IR_CAMERA @JARVIS @ACE @LUMINA
"""

import sys
import subprocess
import time
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

logger = get_logger("CheckAndStartVAs")


def check_ir_camera():
    """Check IR camera status"""
    print("=" * 80)
    print("📹 IR CAMERA STATUS CHECK")
    print("=" * 80)
    print()

    try:
        import cv2

        # Try to open IR camera (indices 1, 2, 3)
        ir_found = False
        for idx in [1, 2, 3]:
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ IR camera found at index {idx}")
                        print(f"   Frame size: {frame.shape}")
                        ir_found = True
                        cap.release()
                        break
                cap.release()
            except:
                continue

        if not ir_found:
            print("⚠️  IR camera not found at indices 1, 2, or 3")
            print("   Checking index 0 (regular camera)...")
            try:
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print("⚠️  Regular camera found at index 0 (not IR)")
                        print("   ⚠️  WARNING: Regular camera emits bright white light")
                cap.release()
            except:
                print("❌ No cameras found")

        print()
        return ir_found

    except ImportError:
        print("❌ OpenCV not available - cannot check camera")
        return False
    except Exception as e:
        print(f"❌ Error checking camera: {e}")
        return False


def check_va_processes():
    """Check if VA processes are running"""
    print("=" * 80)
    print("🤖 VIRTUAL ASSISTANT STATUS CHECK")
    print("=" * 80)
    print()

    va_processes = {
        "JARVIS": ["jarvis", "jarvis_narrator", "jarvis_avatar"],
        "ACE": ["ace", "ironman_va", "ironman_animated"],
        "IMVA": ["imva", "kenny_imva", "replika_inspired"]
    }

    running = {}

    try:
        import psutil

        for va_name, process_names in va_processes.items():
            found = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()

                    for name in process_names:
                        if name.lower() in proc_name or name.lower() in cmdline:
                            print(f"✅ {va_name} is running (PID: {proc.info['pid']})")
                            running[va_name] = True
                            found = True
                            break

                    if found:
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not found:
                print(f"❌ {va_name} is NOT running")
                running[va_name] = False

    except ImportError:
        print("⚠️  psutil not available - using basic process check")
        # Fallback to basic check
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
    return running


def start_vas():
    """Start all virtual assistants"""
    print("=" * 80)
    print("🚀 STARTING VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    # Start VA rendering system
    try:
        print("📺 Starting VA desktop widgets...")
        result = subprocess.Popen(
            ["python", str(project_root / "scripts" / "python" / "render_va_desktop_widgets.py")],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        print(f"✅ VA rendering started (PID: {result.pid})")
        time.sleep(3)  # Give it time to start
    except Exception as e:
        print(f"❌ Failed to start VA rendering: {e}")

    # Start startup script
    try:
        print("🚀 Starting VAs with startup script...")
        result = subprocess.Popen(
            ["python", str(project_root / "scripts" / "python" / "startup_vas_with_armoury_crate.py")],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        print(f"✅ VA startup script started (PID: {result.pid})")
    except Exception as e:
        print(f"❌ Failed to start VA startup script: {e}")

    print()
    print("⏳ Waiting for VAs to initialize...")
    time.sleep(5)

    # Check again
    print()
    running = check_va_processes()

    return running


def main():
    """Main function"""
    print("=" * 80)
    print("JARVIS - System Status Check & Startup")
    print("=" * 80)
    print()

    # Check IR camera
    ir_camera_on = check_ir_camera()

    # Check VA processes
    va_status = check_va_processes()

    # Start VAs if not running
    if not all(va_status.values()):
        print("=" * 80)
        print("Starting missing Virtual Assistants...")
        print("=" * 80)
        print()
        start_vas()

    # Final status
    print("=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    print()
    print(f"📹 IR Camera: {'✅ ON' if ir_camera_on else '❌ OFF'}")
    print()
    print("🤖 Virtual Assistants:")
    for va_name, is_running in va_status.items():
        status = "✅ RUNNING" if is_running else "❌ NOT RUNNING"
        print(f"   {va_name}: {status}")
    print()
    print("=" * 80)


if __name__ == "__main__":


    main()