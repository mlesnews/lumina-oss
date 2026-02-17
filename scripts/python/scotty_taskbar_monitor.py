#!/usr/bin/env python3
"""
@SCOTTY's Taskbar Usage Monitor
Monitors application launches and tracks usage for dynamic taskbar management

Tags: #SCOTTY #TASKBAR #MONITORING #USAGE_TRACKING @SCOTTY @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.python.scotty_dynamic_taskbar import DynamicTaskbarManager

def get_running_applications():
    """Get currently running applications"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object ProcessName, Path, MainWindowTitle | ConvertTo-Json'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            import json
            processes = json.loads(result.stdout)
            if not isinstance(processes, list):
                processes = [processes]

            return processes
    except Exception as e:
        print(f"Error getting processes: {e}")

    return []

def monitor_applications(manager: DynamicTaskbarManager, interval: int = 60):
    """Monitor application launches and track usage"""
    print("SCOTTY: Starting application usage monitor...")
    print(f"Monitoring every {interval} seconds")
    print("Press Ctrl+C to stop")
    print("")

    tracked_processes = set()

    try:
        while True:
            processes = get_running_applications()

            for proc in processes:
                proc_name = proc.get('ProcessName', '')
                proc_path = proc.get('Path', '')
                window_title = proc.get('MainWindowTitle', '')

                if proc_path and proc_name not in tracked_processes:
                    # Track this application
                    app_name = proc_name.replace('.exe', '').title()
                    manager.track_application_launch(app_name, proc_path)
                    tracked_processes.add(proc_name)
                    print(f"Tracked: {app_name}")

            # Clean up old tracked processes (if window closed)
            current_processes = {p.get('ProcessName', '') for p in processes}
            tracked_processes = tracked_processes.intersection(current_processes)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nSCOTTY: Monitoring stopped")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="@SCOTTY's Taskbar Usage Monitor")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")

    args = parser.parse_args()

    manager = DynamicTaskbarManager()

    if args.daemon:
        # Run in background
        monitor_applications(manager, args.interval)
    else:
        # Show current top apps
        top_apps = manager.get_top_applications(limit=10, days=7)
        print("\n🏆 Top 10 Applications (last 7 days):")
        for i, (app_name, data) in enumerate(top_apps, 1):
            print(f"  {i}. {app_name} (Score: {data['score']:.2f}, Launches: {data['recent_launches']})")

        print("\n💡 To start monitoring, run with --daemon flag")
