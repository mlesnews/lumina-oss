#!/usr/bin/env python3
"""
JARVIS Workflow Live Monitor

Real-time monitoring of workflow progress with live updates.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWorkflowLiveMonitor")


def main():
    """Run live monitor"""
    from jarvis_workflow_transparency_system import JARVISWorkflowTransparencySystem

    project_root = Path(__file__).parent.parent.parent
    transparency = JARVISWorkflowTransparencySystem(project_root)

    print("="*80)
    print("🔄 JARVIS WORKFLOW LIVE MONITOR")
    print("="*80)
    print("Monitoring workflows... (Ctrl+C to stop)")
    print("")

    try:
        while True:
            # Update dashboard
            transparency.save_dashboard()

            # Get summary
            summary = transparency.get_workflow_summary()

            # Display status
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Active: {summary['active_workflows']}/{summary['total_workflows']} | "
                  f"Progress: {summary['average_progress']:.1%} | "
                  f"Completed: {summary['by_status'].get('completed', 0)} | "
                  f"Failed: {summary['by_status'].get('failed', 0)}", end='', flush=True)

            time.sleep(10)  # Update every 10 seconds

    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped")


if __name__ == "__main__":


    main()