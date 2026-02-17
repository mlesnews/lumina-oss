#!/usr/bin/env python3
"""
Quick Fix for Cursor IDE Chat History Issues

Quick actions to fix common chat history and connection issues.

Usage:
    python quick_fix_cursor_chat.py --fix-all
    python quick_fix_cursor_chat.py --check-status
    python quick_fix_cursor_chat.py --clear-cache
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def check_cursor_running():
    """Check if Cursor IDE is running"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Cursor.exe"],
            capture_output=True,
            text=True
        )
        return "Cursor.exe" in result.stdout
    except Exception:
        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Quick Fix for Cursor IDE Chat Issues")
    parser.add_argument("--fix-all", action="store_true", help="Run all quick fixes")
    parser.add_argument("--check-status", action="store_true", help="Check current status")
    parser.add_argument("--clear-cache", action="store_true", help="Clear Cursor IDE cache")
    parser.add_argument("--improve-connection", action="store_true", help="Improve connection settings")

    args = parser.parse_args()

    if not any(vars(args).values()):
        # Default: show help and quick status
        parser.print_help()
        print("\n" + "=" * 80)
        print("QUICK STATUS CHECK")
        print("=" * 80)

        cursor_running = check_cursor_running()
        print(f"\nCursor IDE Running: {'✅ Yes' if cursor_running else '❌ No'}")

        if cursor_running:
            print("\n⚠️  Cursor IDE is running. Close it before clearing cache.")
            print("   Run: python quick_fix_cursor_chat.py --clear-cache")
        else:
            print("\n✅ Cursor IDE is not running. Safe to clear cache.")

        print("\nFor full troubleshooting, run:")
        print("  python scripts/python/troubleshoot_cursor_chat_history.py --full-report")
        return 0

    if args.check_status:
        print_header("CURSOR IDE STATUS CHECK")

        cursor_running = check_cursor_running()
        print(f"Cursor IDE Running: {'✅ Yes' if cursor_running else '❌ No'}")

        # Check connection health
        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor
            monitor = CursorConnectionHealthMonitor()
            health = monitor.get_health_status()

            print(f"\nConnection Health: {health['health_status']}")
            print(f"Success Rate: {health['success_rate']}%")
            print(f"Recent Success Rate: {health['recent_success_rate']}%")
            print(f"\nError Breakdown:")
            for error_type, count in health['error_breakdown'].items():
                print(f"  {error_type}: {count}")
        except Exception as e:
            print(f"⚠️  Could not check connection health: {e}")

        return 0

    if args.clear_cache:
        print_header("CLEARING CURSOR IDE CACHE")

        if check_cursor_running():
            print("❌ ERROR: Cursor IDE is currently running!")
            print("\nPlease close Cursor IDE completely before clearing cache.")
            print("Steps:")
            print("  1. Close all Cursor IDE windows")
            print("  2. Check Task Manager - ensure no Cursor.exe processes")
            print("  3. Run this command again")
            return 1

        cache_dirs = [
            Path.home() / "AppData" / "Roaming" / "Cursor" / "Cache",
            Path.home() / "AppData" / "Local" / "Cursor" / "Cache",
        ]

        cleared = 0
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    import shutil
                    # Backup first
                    backup_dir = project_root / "data" / "cursor_chat_troubleshooting" / "cache_backups"
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    backup_path = backup_dir / f"cache_backup_{cache_dir.name}"

                    print(f"📦 Backing up: {cache_dir.name}...")
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.copytree(cache_dir, backup_path, dirs_exist_ok=True)

                    # Clear cache
                    print(f"🧹 Clearing: {cache_dir.name}...")
                    for item in cache_dir.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)

                    print(f"✅ Cleared: {cache_dir.name}")
                    cleared += 1
                except Exception as e:
                    print(f"⚠️  Could not clear {cache_dir.name}: {e}")

        if cleared > 0:
            print(f"\n✅ Cache cleared successfully! ({cleared} directories)")
            print("\nNext steps:")
            print("  1. Restart Cursor IDE")
            print("  2. Wait 2-3 minutes for chat history to reload")
            print("  3. Check if chat history appears")
        else:
            print("⚠️  No cache directories found or already cleared")

        return 0

    if args.improve_connection:
        print_header("IMPROVING CONNECTION SETTINGS")

        try:
            from troubleshoot_cursor_chat_history import CursorChatHistoryTroubleshooter
            troubleshooter = CursorChatHistoryTroubleshooter()
            improvements = troubleshooter.improve_connection_resilience()

            print("✅ Connection settings improved!")
            print(f"   Max Retries: {improvements['new_config']['max_retries']}")
            print(f"   Retry Delay: {improvements['new_config']['retry_delay']}s")

        except Exception as e:
            print(f"❌ Error improving connection: {e}")
            return 1

        return 0

    if args.fix_all:
        print_header("RUNNING ALL QUICK FIXES")

        # Check status first
        cursor_running = check_cursor_running()
        if cursor_running:
            print("⚠️  Cursor IDE is running. Skipping cache clear.")
            print("   Close Cursor IDE and run --clear-cache separately")
        else:
            # Clear cache
            args.clear_cache = True
            main()

        # Improve connection
        args.improve_connection = True
        main()

        print("\n✅ All quick fixes completed!")
        print("\nNext steps:")
        print("  1. Restart Cursor IDE")
        print("  2. Wait for chat history to reload")
        print("  3. Monitor connection health")

        return 0

    return 0

if __name__ == "__main__":


    sys.exit(main())