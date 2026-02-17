import os
import subprocess
import psutil

def aggressive_purge():
    print("🧹 Starting Aggressive Purge of all Assistant processes...")

    # 1. Kill by process name and command line
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info.get('cmdline') or [])
            name = proc.info.get('name', '').lower()

            # Target anything related to Kenny or Jarvis
            if any(term in cmdline.lower() for term in ['kenny', 'jarvis', 'assistant']):
                print(f"💀 Force killing PID {proc.info['pid']} ({cmdline[:50]}...)")
                subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])], capture_output=True)

            # Target pythonw.exe which often hides GUI windows
            if 'pythonw' in name:
                print(f"💀 Force killing background Python GUI: PID {proc.info['pid']}")
                subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])], capture_output=True)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 2. Final sweep for any window titles containing 'Kenny' or 'Jarvis'
    # (PowerShell snippet to close windows by title)
    ps_cmd = 'Get-Process | Where-Object {$_.MainWindowTitle -like "*Kenny*" -or $_.MainWindowTitle -like "*Jarvis*"} | Stop-Process -Force'
    subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)

    print("✅ Purge complete. The screen should be clear.")

if __name__ == "__main__":
    aggressive_purge()
