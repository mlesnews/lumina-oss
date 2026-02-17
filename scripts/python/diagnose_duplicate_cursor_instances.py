#!/usr/bin/env python3
"""
Diagnose Duplicate Cursor Instances

Identifies why multiple Cursor instances might be appearing.
Checks for:
- Multiple Cursor windows
- Startup scripts launching Cursor
- Scheduled tasks
- Multiple installations
- Warm recycle system launching instances

Tags: #DIAGNOSTICS #CURSOR @JARVIS
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorDuplicateDiagnostic")

try:
    import psutil
    import pygetwindow as gw
except ImportError:
    logger.warning("psutil or pygetwindow not available")
    psutil = None
    gw = None


def get_cursor_processes() -> List[Dict[str, Any]]:
    """Get all Cursor processes"""
    processes = []
    if not psutil:
        return processes

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info']):
            try:
                proc_info = proc.info
                if 'cursor' in proc_info['name'].lower():
                    cmdline = ' '.join(proc_info.get('cmdline', []))
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cmdline': cmdline,
                        'memory_mb': proc_info['memory_info'].rss / 1024 / 1024,
                        'create_time': datetime.fromtimestamp(proc_info['create_time']).isoformat()
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.error(f"Error getting processes: {e}")

    return processes


def get_cursor_windows() -> List[Dict[str, Any]]:
    """Get all Cursor windows"""
    windows = []
    if not gw:
        return windows

    try:
        for window in gw.getWindowsWithTitle(''):
            if 'cursor' in window.title.lower():
                windows.append({
                    'title': window.title,
                    'pid': window._hWnd if hasattr(window, '_hWnd') else None,
                    'visible': window.visible,
                    'size': (window.width, window.height) if hasattr(window, 'width') else None
                })
    except Exception as e:
        logger.error(f"Error getting windows: {e}")

    return windows


def check_startup_scripts() -> List[Dict[str, Any]]:
    """Check for scripts that might launch Cursor"""
    scripts = []
    scripts_dir = project_root / "scripts" / "python"

    # Check for scripts that launch Cursor
    cursor_launch_patterns = [
        'subprocess.*Cursor',
        'Popen.*Cursor',
        r'start.*Cursor\.exe',
        'lumina_startup_sequence_manager',
        'cursor_intelligent_warm_recycle'
    ]

    import re
    for script_file in scripts_dir.glob("*.py"):
        try:
            content = script_file.read_text(encoding='utf-8', errors='ignore')
            for pattern in cursor_launch_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    scripts.append({
                        'file': str(script_file.relative_to(project_root)),
                        'pattern': pattern
                    })
                    break
        except Exception:
            continue

    return scripts


def check_scheduled_tasks() -> List[Dict[str, Any]]:
    """Check Windows scheduled tasks that might launch Cursor"""
    tasks = []
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/fo', 'csv', '/v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'cursor' in line.lower():
                    tasks.append({'task': line.strip()})
    except Exception as e:
        logger.debug(f"Error checking scheduled tasks: {e}")

    return tasks


def check_startup_folder() -> List[Dict[str, Any]]:
    try:
        """Check Windows startup folder for Cursor shortcuts"""
        startup_items = []
        startup_paths = [
            Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
            Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp")
        ]

        for startup_path in startup_paths:
            if startup_path.exists():
                for item in startup_path.iterdir():
                    if 'cursor' in item.name.lower():
                        startup_items.append({
                            'path': str(item),
                            'name': item.name
                        })

        return startup_items


    except Exception as e:
        logger.error(f"Error in check_startup_folder: {e}", exc_info=True)
        raise
def main():
    try:
        """Run diagnostic"""
        print("=" * 80)
        print("🔍 CURSOR DUPLICATE INSTANCE DIAGNOSTIC")
        print("=" * 80)
        print()

        results = {
            'timestamp': datetime.now().isoformat(),
            'cursor_processes': get_cursor_processes(),
            'cursor_windows': get_cursor_windows(),
            'startup_scripts': check_startup_scripts(),
            'scheduled_tasks': check_scheduled_tasks(),
            'startup_folder_items': check_startup_folder()
        }

        # Print summary
        print(f"📊 Cursor Processes: {len(results['cursor_processes'])}")
        for proc in results['cursor_processes']:
            print(f"   PID {proc['pid']}: {proc['name']} ({proc['memory_mb']:.1f}MB)")
            if proc['cmdline']:
                cmdline_short = proc['cmdline'][:100] + "..." if len(proc['cmdline']) > 100 else proc['cmdline']
                print(f"      {cmdline_short}")

        print()
        print(f"🪟 Cursor Windows: {len(results['cursor_windows'])}")
        for window in results['cursor_windows']:
            print(f"   {window['title']}")

        print()
        print(f"📜 Startup Scripts (that might launch Cursor): {len(results['startup_scripts'])}")
        for script in results['startup_scripts']:
            print(f"   {script['file']} (pattern: {script['pattern']})")

        print()
        print(f"⏰ Scheduled Tasks: {len(results['scheduled_tasks'])}")
        for task in results['scheduled_tasks']:
            print(f"   {task.get('task', 'N/A')}")

        print()
        print(f"📁 Startup Folder Items: {len(results['startup_folder_items'])}")
        for item in results['startup_folder_items']:
            print(f"   {item['name']} ({item['path']})")

        print()
        print("=" * 80)

        # Save report
        report_file = project_root / "data" / "cursor_duplicate_diagnostic.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"💾 Full report saved: {report_file}")
        print("=" * 80)

        # Analysis
        print()
        print("🔍 ANALYSIS:")
        print()

        main_processes = [p for p in results['cursor_processes'] if '--type=' not in p.get('cmdline', '')]
        child_processes = [p for p in results['cursor_processes'] if '--type=' in p.get('cmdline', '')]

        print(f"   Main Cursor processes: {len(main_processes)}")
        print(f"   Child processes (renderer, utility, etc.): {len(child_processes)}")
        print(f"   Total Cursor windows: {len(results['cursor_windows'])}")

        if len(main_processes) > 1:
            print()
            print("⚠️  WARNING: Multiple main Cursor processes detected!")
            print("   This could indicate multiple Cursor instances running.")
            for proc in main_processes:
                print(f"      PID {proc['pid']} started at {proc['create_time']}")

        if len(results['startup_scripts']) > 0:
            print()
            print("⚠️  WARNING: Scripts found that might launch Cursor:")
            for script in results['startup_scripts']:
                print(f"      {script['file']}")

        if len(results['startup_folder_items']) > 0:
            print()
            print("⚠️  WARNING: Items found in startup folder:")
            for item in results['startup_folder_items']:
                print(f"      {item['name']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()