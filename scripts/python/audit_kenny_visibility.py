import pygetwindow as gw
import psutil
import time

def audit_visibility():
    print("🔍 Auditing Kenny Visibility...")

    # 1. Check Process
    found_proc = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info.get('cmdline') or [])
            if 'kenny_imva_enhanced' in cmdline:
                print(f"✅ Process Found: PID {proc.info['pid']}")
                found_proc = True
        except: pass

    if not found_proc:
        print("❌ NO KENNY PROCESS RUNNING.")

    # 2. Check Windows
    windows = gw.getWindowsWithTitle('Kenny')
    if not windows:
        print("❌ NO KENNY WINDOW FOUND.")
    else:
        for win in windows:
            print(f"✅ Window Found: '{win.title}'")
            print(f"   - Position: ({win.left}, {win.top})")
            print(f"   - Size: {win.width}x{win.height}")
            print(f"   - Is Visible: {win.visible}")
            print(f"   - Is Minimized: {win.isMinimized}")

if __name__ == "__main__":
    audit_visibility()
