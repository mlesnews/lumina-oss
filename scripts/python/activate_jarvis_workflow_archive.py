#!/usr/bin/env python3
"""
Activate JARVIS Workflow Archive Automation

Quick activation script to start the automated archiving of finished workflows
that have been backed up to GitLens with PR.

Usage:
    python activate_jarvis_workflow_archive.py [--monitor] [--process] [--status]

Tags: #WORKFLOW #ARCHIVE #AUTOMATION #GITLENS #PR #FULLAUTO @JARVIS @DOIT
"""

import sys
import json
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_workflow_archive_automation import (
        JARVISWorkflowArchiveAutomation,
        main as archive_main
    )
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("   Make sure you're running from the correct directory")
    sys.exit(1)

logger = get_logger("ActivateJARVISWorkflowArchive")


def print_banner():
    """Print activation banner"""
    print("\n" + "="*80)
    print("🤖 JARVIS WORKFLOW ARCHIVE AUTOMATION - ACTIVATION")
    print("="*80)
    print("   Automatically archives AI agent history workflows that are:")
    print("   1. Finished/completed")
    print("   2. Backed up to GitLens with PR")
    print("="*80 + "\n")


def activate_automation(mode: str = "process"):
    """
    Activate the workflow archive automation.

    Args:
        mode: "process" (run once), "monitor" (continuous), or "status" (show status)
    """
    print_banner()

    # Initialize automation (fullauto enabled by default)
    try:
        automation = JARVISWorkflowArchiveAutomation(fullauto=True)
        logger.info("✅ JARVIS Workflow Archive Automation initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize automation: {e}")
        return False

    if mode == "status":
        # Show status
        status = automation.get_status()
        print("\n📊 AUTOMATION STATUS")
        print("-" * 80)
        print(json.dumps(status, indent=2, default=str))
        print()
        return True

    elif mode == "monitor":
        # Continuous monitoring
        print("🔄 Starting continuous monitoring mode...")
        print("   Press Ctrl+C to stop\n")
        try:
            automation.continuous_monitor(interval=3600)  # Check every hour
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        return True

    elif mode == "process":
        # Process once
        print("🔄 Processing workflows ready for archive...\n")

        # First, discover any new workflows
        discovered = automation.discover_workflows()
        if discovered:
            print(f"   📋 Discovered {len(discovered)} new workflows")

        # Process ready workflows
        results = automation.process_ready_workflows()

        print("\n" + "="*80)
        print("📊 PROCESSING RESULTS")
        print("="*80)
        print(f"   Workflows checked: {results.get('workflows_checked', 0)}")
        print(f"   Workflows ready: {results.get('workflows_ready', 0)}")
        print(f"   Workflows archived: {results.get('workflows_archived', 0)}")

        if results.get('archived'):
            print("\n   ✅ Archived workflows:")
            for wf in results['archived']:
                print(f"      - {wf.get('workflow_name')} ({wf.get('workflow_id')})")
        else:
            print("\n   ℹ️  No workflows ready for archive at this time")

        print()
        return True

    return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Activate JARVIS Workflow Archive Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process workflows once (default)
  python activate_jarvis_workflow_archive.py

  # Show status
  python activate_jarvis_workflow_archive.py --status

  # Continuous monitoring (checks every hour)
  python activate_jarvis_workflow_archive.py --monitor

  # Process workflows once explicitly
  python activate_jarvis_workflow_archive.py --process
        """
    )

    parser.add_argument("--monitor", action="store_true",
                       help="Start continuous monitoring mode")
    parser.add_argument("--process", action="store_true",
                       help="Process workflows once (default)")
    parser.add_argument("--status", action="store_true",
                       help="Show automation status")

    args = parser.parse_args()

    # Determine mode
    if args.status:
        mode = "status"
    elif args.monitor:
        mode = "monitor"
    else:
        mode = "process"  # Default

    # Activate
    success = activate_automation(mode=mode)

    if not success:
        sys.exit(1)


if __name__ == "__main__":


    main()