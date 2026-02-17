#!/usr/bin/env python3
"""
Notify Papa Palpatine - Report issues to the Dark Lord

Tags: #NOTIFICATION #PAPA_PALPATINE #REPORTING @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None

logger = get_logger("PapaPalpatineNotifier")

def notify_papa_palpatine(message: str, issue_type: str = "startup_failure"):
    """Notify Papa Palpatine of an issue"""

    print("=" * 80)
    print("⚡ NOTIFYING PAPA PALPATINE")
    print("=" * 80)
    print()

    # Try to find Papa Palpatine in character registry
    palpatine_found = False
    if CharacterAvatarRegistry:
        try:
            registry = CharacterAvatarRegistry()
            palpatine = registry.get_character("palpatine") or registry.get_character("papa_palpatine")
            if palpatine:
                palpatine_found = True
                print(f"📡 Contacting: {palpatine.name}")
                print(f"   Role: {palpatine.role}")
                print()
        except Exception as e:
            logger.warning(f"Could not access character registry: {e}")

    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "issue_type": issue_type,
        "message": message,
        "reported_by": "JARVIS",
        "status": "REPORTED"
    }

    # Save report to file
    reports_dir = project_root / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"palpatine_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("⚡ REPORT TO PAPA PALPATINE\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nTimestamp: {report['timestamp']}\n")
        f.write(f"Issue Type: {report['issue_type']}\n")
        f.write(f"Reported By: {report['reported_by']}\n")
        f.write(f"\nMessage:\n{message}\n")
        f.write("\n" + "=" * 80 + "\n")

    print(f"📝 Report saved: {report_file}")
    print()

    # Display report
    print("📋 REPORT:")
    print("-" * 80)
    print(f"Time: {report['timestamp']}")
    print(f"Issue: {issue_type}")
    print(f"From: {report['reported_by']}")
    print()
    print("Message:")
    print(message)
    print("-" * 80)
    print()

    if palpatine_found:
        print("✅ Papa Palpatine has been notified!")
    else:
        print("⚠️  Papa Palpatine not found in registry, but report has been saved.")

    print()
    print("=" * 80)

    return report_file

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Notify Papa Palpatine")
    parser.add_argument("message", help="Message to send")
    parser.add_argument("--type", default="startup_failure", help="Issue type")
    args = parser.parse_args()

    notify_papa_palpatine(args.message, args.type)
