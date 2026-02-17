#!/usr/bin/env python3
"""
NAS Migration Progress Monitor
Outputs real-time progress to chat terminal feed
"""

import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

def get_disk_usage():
    """Get current disk usage via PowerShell"""
    cmd = [
        'powershell', '-Command',
        '$drive = Get-PSDrive C; $used = $drive.Used; $free = $drive.Free; '
        '$total = $used + $free; $percent = [math]::Round(($used/$total)*100,1); '
        'Write-Output "$percent|$([math]::Round($used/1GB,1))|$([math]::Round($free/1GB,1))"'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            parts = result.stdout.strip().split('|')
            return {
                'percent': float(parts[0]),
                'used_gb': float(parts[1]),
                'free_gb': float(parts[2])
            }
    except:
        pass
    return None

def check_move_progress(path, name):
    """Check if directory/file still exists and get size"""
    if not Path(path).exists():
        return {'exists': False, 'size_gb': 0}

    cmd = [
        'powershell', '-Command',
        f'$size = (Get-ChildItem "{path}" -Recurse -File -ErrorAction SilentlyContinue | '
        'Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum; '
        'Write-Output "$([math]::Round($size/1GB,1))"'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            size = float(result.stdout.strip())
            return {'exists': True, 'size_gb': size}
    except:
        pass
    return {'exists': True, 'size_gb': None}

def format_progress_bar(percent, width=40):
    """Create ASCII progress bar"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent:.1f}%"

def main():
    """Main monitoring loop"""
    print("=" * 60)
    print("NAS MIGRATION PROGRESS MONITOR")
    print("=" * 60)
    print()

    # Initial state
    initial_used = 3589.0  # GB
    target_used = 2956.0   # GB (< 80%)
    target_free = 630.0    # GB to free

    # Tracked directories
    tracked = {
        'Dropbox_Flattened': r'C:\Users\mlesn\Dropbox\Dropbox_Flattened_20251222_000717',
        'Docker': r'C:\Users\mlesn\AppData\Local\Docker',
        'Outlook': r'C:\Users\mlesn\AppData\Local\Microsoft\Outlook',
    }

    iteration = 0
    while True:
        iteration += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Get current disk usage
        disk = get_disk_usage()
        if not disk:
            print(f"[{timestamp}] ⚠️  Unable to get disk usage")
            time.sleep(10)
            continue

        # Calculate progress
        freed_gb = initial_used - disk['used_gb']
        progress_pct = (freed_gb / target_free) * 100 if target_free > 0 else 0
        remaining_gb = target_used - disk['used_gb']

        # Clear and print header
        print(f"\n[{timestamp}] Iteration #{iteration}")
        print("-" * 60)
        print(f"📊 DISK USAGE: {disk['percent']:.1f}%")
        print(f"   Used: {disk['used_gb']:.1f} GB | Free: {disk['free_gb']:.1f} GB")
        print()
        print(f"🎯 PROGRESS: {format_progress_bar(progress_pct)}")
        print(f"   Freed: {freed_gb:.1f} GB / {target_free:.0f} GB")
        print(f"   Remaining: {remaining_gb:.1f} GB to reach <80%")
        print()

        # Check tracked directories
        print("📁 LARGE DIRECTORY STATUS:")
        for name, path in tracked.items():
            status = check_move_progress(path, name)
            if not status['exists']:
                print(f"   ✅ {name}: MOVED")
            elif status['size_gb'] is not None:
                print(f"   🔄 {name}: {status['size_gb']:.1f} GB remaining")
            else:
                print(f"   ⚠️  {name}: Checking...")
        print()

        # Status summary
        if remaining_gb <= 0:
            print("✅ TARGET REACHED! Disk usage < 80%")
            break
        elif progress_pct >= 100:
            print("✅ TARGET REACHED! Freed 630 GB")
            break
        else:
            print(f"⏳ Continuing... Next update in 30 seconds")
            print("=" * 60)

        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")