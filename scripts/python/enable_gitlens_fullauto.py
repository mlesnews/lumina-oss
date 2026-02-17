#!/usr/bin/env python3
"""
Enable Full Automation for GitLens Follow-ups

Enables complete automation of all GitLens operations:
- Auto-commit on changes
- Auto-push after commit
- Auto-pull before operations
- Auto-resolve conflicts

Tags: #GITLENS #FULLAUTO #AUTOMATION @JARVIS @DOIT
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from jarvis_gitlens_automation import JARVISGitLensAutomation
from jarvis_helpdesk_integration import JARVISHelpdeskIntegration

def main():
    """Enable full automation for GitLens"""
    print("\n" + "=" * 80)
    print("🚀 ENABLING FULL AUTOMATION FOR GITLENS FOLLOW-UPS")
    print("=" * 80 + "\n")

    # Initialize GitLens automation with fullauto
    print("📦 Initializing GitLens automation (fullauto mode)...")
    gitlens = JARVISGitLensAutomation(fullauto=True)
    print("✅ GitLens automation initialized with fullauto enabled\n")

    # Handle follow-ups (will use fullauto)
    print("🔄 Handling all GitLens follow-ups automatically...")
    results = gitlens.handle_follow_ups()

    print("\n📋 Results:")
    print("-" * 80)
    for action in results.get("actions_taken", []):
        status = "✅" if action.get("success") else "❌"
        print(f"{status} {action.get('action')}: {action.get('message', '')}")

    print("\n" + "=" * 80)
    print("✅ FULL AUTOMATION ENABLED FOR GITLENS")
    print("=" * 80)
    print("\nAll GitLens follow-ups will now be handled automatically:")
    print("  • Auto-commit on changes")
    print("  • Auto-push after commit")
    print("  • Auto-pull before operations")
    print("  • Auto-resolve conflicts (using 'ours' strategy)")
    print("\nTo use in code:")
    print("  from jarvis_helpdesk_integration import JARVISHelpdeskIntegration")
    print("  jarvis = JARVISHelpdeskIntegration()")
    print("  jarvis.handle_gitlens_follow_ups(fullauto=True)\n")

    return 0

if __name__ == "__main__":


    sys.exit(main())