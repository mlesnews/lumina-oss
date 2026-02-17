#!/usr/bin/env python3
"""
Ciao Session Resumer - IDE Startup Integration
Automatically runs on IDE startup with resource balancing
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ciao_session_resumer import CiaoSessionResumer

def main():
    """Run Ciao session resumer on IDE startup with log parsing"""
    project_root = Path(__file__).parent.parent.parent

    # Initialize log parser for startup logs
    try:
        from centralized_log_parser import CentralizedLogParser, LogSource
        log_parser = CentralizedLogParser(project_root=project_root)
        print("📋 Centralized log parser initialized")

        # Parse startup logs in background (non-blocking)
        import threading
        def parse_startup_logs():
            try:
                startup_logs = log_parser.get_startup_logs(LogSource.IDE_STARTUP)
                if startup_logs:
                    print(f"   Found {len(startup_logs)} IDE startup log entries")
                    # Aggregate patterns
                    aggregation = log_parser.aggregate_by_patterns(startup_logs)
                    if aggregation.get('patterns_matched', 0) > 0:
                        print(f"   Detected {aggregation['patterns_matched']} log patterns")
            except Exception as e:
                print(f"   ⚠️  Log parsing error: {e}")

        # Start log parsing in background
        log_thread = threading.Thread(target=parse_startup_logs, daemon=True)
        log_thread.start()
    except ImportError:
        print("   ⚠️  Centralized log parser not available")

    resumer = CiaoSessionResumer(project_root=project_root)

    # Setup auto-startup flag
    resumer.setup_auto_startup()

    # Wait for IDE to fully initialize
    print(f"⏳ Waiting {resumer.startup_delay}s for IDE initialization...")
    time.sleep(resumer.startup_delay)

    # Get initial resource stats
    initial_stats = resumer.get_resource_stats()
    print(f"📊 System state: CPU {initial_stats.cpu_percent:.1f}%, Memory {initial_stats.memory_percent:.1f}%")

    # Check if system is ready (not overloaded)
    if initial_stats.cpu_percent > 90 or initial_stats.memory_percent > 90:
        print("⚠️  System resources high, deferring session resume")
        print(f"   Will retry when CPU < 90% and Memory < 90%")
        return

    # Resume sessions
    print("🚀 Starting Ciao session resume...")
    summary = resumer.resume_sessions()

    print(f"\n✅ Completed: {summary.get('sessions_resumed', 0)} sessions resumed")

if __name__ == "__main__":



    main()