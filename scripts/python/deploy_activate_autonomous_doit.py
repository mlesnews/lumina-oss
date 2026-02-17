#!/usr/bin/env python3
"""
Deploy & Activate Autonomous @DOIT System

DEPLOYS AND ACTIVATES JARVIS SYPHON AUTONOMOUS EXECUTOR
NO HUMAN ACTION REQUIRED - FULLY AUTONOMOUS

@DEPLOY @ACTIVATE @AUTONOMOUS @DOIT
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

from jarvis_syphon_autonomous_doit_executor import JARVISSYPHONAutonomousDOITExecutor


def deploy():
    """Deploy autonomous system"""
    print("=" * 80)
    print("🚀 DEPLOYING AUTONOMOUS @DOIT SYSTEM")
    print("=" * 80)

    # Verify components
    print("📋 Verifying components...")

    # Check SYPHON
    try:
        from ai_syphon_idm_orchestrator import AIOrchestrator
        print("   ✅ SYPHON Orchestrator: Available")
    except ImportError:
        print("   ⚠️  SYPHON Orchestrator: Not available (will use fallback)")

    # Check JARVIS Decisioning
    try:
        from jarvis_syphon_decisioning import JARVISSYPHONDecisioning
        print("   ✅ JARVIS Decisioning: Available")
    except ImportError:
        print("   ⚠️  JARVIS Decisioning: Not available (will use fallback)")

    # Check JARVIS Autonomous
    try:
        from jarvis_autonomous_extrapolation import JARVISAutonomousExtrapolation
        print("   ✅ JARVIS Autonomous: Available")
    except ImportError:
        print("   ⚠️  JARVIS Autonomous: Not available (will use fallback)")

    print("\n✅ Deployment complete")
    return True


def activate():
    """Activate autonomous system"""
    print("=" * 80)
    print("🔌 ACTIVATING AUTONOMOUS @DOIT SYSTEM")
    print("=" * 80)

    executor = JARVISSYPHONAutonomousDOITExecutor()

    print("\n🚀 Starting autonomous execution...")
    print("   Mode: UNATTENDED")
    print("   Human Action: DISABLED")
    print("   AI-Only: ENABLED")
    print("   Top-Down Decisioning: ENABLED")
    print("   Troubleshooting: AUTO")
    print("\n" + "=" * 80)

    # Start
    executor.start()

    # Keep running
    try:
        while executor.running:
            time.sleep(60)  # Check every minute
            status = executor.get_status()

            # Print status every 5 minutes
            if int(time.time()) % 300 == 0:
                print(f"\n📊 Status: {status['active_actions']} active, "
                      f"{status['queued_actions']} queued, "
                      f"{status['total_actions']} total, "
                      f"Uptime: {status['uptime_hours']:.1f}h")
    except KeyboardInterrupt:
        print("\n⏹️  Stopping...")
        executor.stop()

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy & Activate Autonomous @DOIT")
    parser.add_argument("--deploy", action="store_true", help="Deploy system")
    parser.add_argument("--activate", action="store_true", help="Activate system")
    parser.add_argument("--deploy-activate", action="store_true", help="Deploy and activate")

    args = parser.parse_args()

    if args.deploy_activate or (args.deploy and args.activate):
        deploy()
        time.sleep(2)
        activate()
    elif args.deploy:
        deploy()
    elif args.activate:
        activate()
    else:
        # Default: deploy and activate
        deploy()
        time.sleep(2)
        activate()


if __name__ == "__main__":


    main()