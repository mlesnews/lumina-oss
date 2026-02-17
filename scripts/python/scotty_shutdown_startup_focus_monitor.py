#!/usr/bin/env python3
"""
@SCOTTY Shutdown / Startup & Focus Monitor
==========================================
Chief Engineer Scotty – Windows Architect monitoring.

Logs:
- Startup: when the session started and (optionally) what ran at logon.
- Focus changes: which window stole focus (timestamp, previous window, new window, process).
  Use this to find what’s pulling focus away while you type (e.g. editor, scripts, notifications).

Usage:
  python scotty_shutdown_startup_focus_monitor.py --startup
      Log startup event only.
  python scotty_shutdown_startup_focus_monitor.py --focus 15
      Monitor focus changes for 15 minutes; log to data/scotty_monitor/.
  python scotty_shutdown_startup_focus_monitor.py --both 10
      Log startup, then monitor focus for 10 minutes.
  python scotty_shutdown_startup_focus_monitor.py --install
      Install a Task Scheduler task to run --both 10 at logon (with delay).

#automation  @SCOTTY @WINDOWS_ARCHITECT
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
    logging.basicConfig(level=logging.INFO)

logger = get_logger("ScottyFocusMonitor")

DATA_DIR = project_root / "data" / "scotty_monitor"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_foreground_window_info():
    """Return (title, process_name) for the current foreground window on Windows."""
    if sys.platform != "win32":
        return ("", "")
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ("", "")

        length = user32.GetWindowTextLengthW(hwnd) + 1
        buf = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buf, length)
        title = buf.value or ""

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return (title, "")

        try:
            import psutil
            proc = psutil.Process(pid.value)
            return (title, proc.name() or "")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return (title, "")
    except Exception as e:
        logger.debug("get_foreground_window_info: %s", e)
        return ("", "")


def log_startup_event():
    """Log a startup event (run at logon or manually)."""
    uptime_seconds = None
    try:
        import subprocess
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0 and r.stdout.strip():
            s = r.stdout.strip()
            # CIM_DATETIME e.g. 20260108135709.460000-300; use first 14 chars YYYYMMDDHHMMSS
            if len(s) >= 14:
                try:
                    boot = datetime.strptime(s[:14], "%Y%m%d%H%M%S")
                    uptime_seconds = (datetime.now() - boot).total_seconds()
                except ValueError:
                    pass
    except Exception as e:
        logger.debug("uptime check: %s", e)

    event = {
        "event": "startup",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime_seconds,
        "source": "scotty_shutdown_startup_focus_monitor",
    }
    path = DATA_DIR / f"startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(event, indent=2), encoding="utf-8")
    logger.info("Startup event logged: %s", path)
    return path


def run_focus_monitor(minutes: int):
    """Monitor foreground window changes and log each change (focus steal)."""
    interval_sec = 1.0
    prev_title, prev_process = get_foreground_window_info()
    log_path = DATA_DIR / f"focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    end_time = datetime.now().timestamp() + (minutes * 60)
    logger.info("Focus monitor started for %s minutes; log: %s", minutes, log_path)

    import time
    with open(log_path, "a", encoding="utf-8") as f:
        while datetime.now().timestamp() < end_time:
            time.sleep(interval_sec)
            title, process = get_foreground_window_info()
            if (title, process) != (prev_title, prev_process):
                line = json.dumps({
                    "ts": datetime.now().isoformat(),
                    "prev_title": prev_title or "(none)",
                    "prev_process": prev_process or "(none)",
                    "new_title": title or "(none)",
                    "new_process": process or "(none)",
                }) + "\n"
                f.write(line)
                f.flush()
                logger.info("Focus: %s [%s] -> %s [%s]", prev_title or "(none)", prev_process or "(none)", title or "(none)", process or "(none)")
            prev_title, prev_process = title, process

    logger.info("Focus monitor finished. Log: %s", log_path)
    return log_path


def install_task():
    """Install Task Scheduler task: at logon, run --both 10 (with delay)."""
    script_path = Path(__file__).resolve()
    ps = f'''
$TaskName = "SCOTTY-Startup-Focus-Monitor"
$Action = New-ScheduledTaskAction -Execute "pythonw" -Argument '"{script_path}" --both 10' -WorkingDirectory "{script_path.parent}"
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Trigger.Delay = "PT2M"
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\\$env:USERNAME" -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
Write-Output "Installed: $TaskName (runs 2 min after logon, monitors focus for 10 min)"
'''.format(script_path, project_root)
    import subprocess
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True, text=True, timeout=15
    )
    if r.returncode != 0:
        logger.error("Install failed: %s", r.stderr)
        return False
    logger.info("%s", r.stdout.strip())
    return True


def main():
    ap = argparse.ArgumentParser(description="Scotty: startup/shutdown & focus monitor")
    ap.add_argument("--startup", action="store_true", help="Log startup event only")
    ap.add_argument("--focus", type=int, metavar="MIN", help="Monitor focus changes for MIN minutes")
    ap.add_argument("--both", type=int, metavar="MIN", help="Log startup then monitor focus for MIN minutes")
    ap.add_argument("--install", action="store_true", help="Install Task Scheduler task (--both 10 at logon + 2 min delay)")
    args = ap.parse_args()

    if args.install:
        install_task()
        return

    if args.both is not None:
        log_startup_event()
        run_focus_monitor(args.both)
        return

    if args.startup:
        log_startup_event()
        return

    if args.focus is not None:
        run_focus_monitor(args.focus)
        return

    ap.print_help()
    print("\nExample: python scotty_shutdown_startup_focus_monitor.py --both 10")


if __name__ == "__main__":
    main()
