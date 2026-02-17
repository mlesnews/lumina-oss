#!/usr/bin/env python3
"""
Marvin Review Session Work - HK-47 Style

Invokes Marvin to review session work, input, and output with constructive criticism.
Marvin's "huge brain" can easily review all the work - it's trivial for him.

"Meatbags" reference: HK-47 from Star Wars (calls organics "meatbags")

Tags: #MARVIN #REVIEW #CRITICISM #HK47 @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from marvin_roast_system import MarvinRoastSystem, MarvinRoast
    from marvin_comprehensive_system_roast import MarvinComprehensiveRoast
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    print("⚠️  Marvin systems not fully available")

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinReviewSession")


def get_session_work_summary() -> Dict[str, Any]:
    """Get summary of work done in this session"""
    return {
        "session_timestamp": datetime.now().isoformat(),
        "work_items": [
            {
                "item": "Lumina Proximity Chat Service",
                "description": "Created service-oriented proximity chat system with architectural integration",
                "files": [
                    "scripts/python/lumina_proximity_chat_service.py",
                    "scripts/python/lumina_chat_bubble_renderer.py",
                    "scripts/python/lumina_proximity_chat_integration_example.py"
                ],
                "docs": [
                    "docs/LUMINA_PROXIMITY_CHAT_ARCHITECTURE.md"
                ]
            },
            {
                "item": "Background Disk Space Migration",
                "description": "Created background service to migrate files and achieve 50% disk usage goal",
                "files": [
                    "scripts/python/background_disk_space_migration.py"
                ],
                "docs": [
                    "docs/BACKGROUND_DISK_MIGRATION_GUIDE.md"
                ]
            },
            {
                "item": "Master Todo List / Roadmap System",
                "description": "Created collapsed/expanded master todo list with terminology support",
                "files": [
                    "scripts/python/lumina_master_roadmap_display.py",
                    "scripts/python/show_master_roadmap.py"
                ],
                "docs": [
                    "docs/MASTER_ROADMAP_GUIDE.md",
                    "docs/MASTER_TODO_COLLAPSED_GUIDE.md"
                ],
                "notes": [
                    "Distinguishes Master todos (persistent) from Padawan/Subagent todos (session-specific)",
                    "Initiative = individual agent chat session scope",
                    "Collapsed by default for focus, expandable on demand"
                ]
            }
        ],
        "key_decisions": [
            "Removed literal slash commands - focused on architectural integration",
            "Service-oriented approach instead of command-based",
            "Proximity-aware messaging (like WoW local chat concept)",
            "Collapsed master todo by default to maintain focus",
            "Terminology support: master todo, roadmap, one ring, etc."
        ],
        "user_feedback_integrated": [
            "User clarified: Padawan = Subagent = Session-specific todos",
            "User clarified: Initiative = Individual chat session scope",
            "User requested collapsed view by default",
            "User wanted architectural focus, not literal WoW commands"
        ]
    }


def invoke_marvin_review() -> Dict[str, Any]:
    """Invoke Marvin to review the session work"""
    print("=" * 80)
    print("🤖 INVOKING MARVIN FOR SESSION REVIEW")
    print("=" * 80)
    print()
    print("Marvin, please review this session's work with your 'huge brain'.")
    print("We are meatbags (HK-47 reference), so this should be trivial for you.")
    print()

    session_summary = get_session_work_summary()

    if not MARVIN_AVAILABLE:
        print("⚠️  Marvin roast system not available")
        print("📋 Session Summary:")
        print(json.dumps(session_summary, indent=2))
        return {"error": "Marvin not available", "summary": session_summary}

    try:
        # Use Marvin's roast system
        roast_system = MarvinRoastSystem(project_root)

        # Create a comprehensive ask for Marvin to roast
        ask_text = f"""
Session Work Review Request:

Please review the following work with constructive criticism:

1. Lumina Proximity Chat Service
   - Service-oriented architecture
   - Proximity-aware messaging
   - Chat bubble renderer
   - Integration examples

2. Background Disk Space Migration
   - Background service for 50% disk usage goal
   - Automatic file migration
   - Progress tracking

3. Master Todo List System
   - Collapsed/expanded views
   - Terminology support
   - Focus on productivity

Key Questions:
- Are there gaps in implementation?
- Is there unnecessary bloat?
- Missing integrations?
- Incomplete workflows?
- Any security concerns?
- Performance issues?
- Documentation gaps?

Please provide constructive criticism (negative feedback is welcome).
"""

        # Roast the session work
        roast = roast_system.roast_ask(
            ask_id=f"session_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            ask_text=ask_text,
            context={
                "session_summary": session_summary,
                "review_type": "comprehensive_session_review",
                "requested_by": "user_with_marvin_invocation"
            }
        )

        print("=" * 80)
        print("🔥 MARVIN'S ROAST RESULTS")
        print("=" * 80)
        print()
        print(f"Roast ID: {roast.roast_id}")
        print(f"Findings: {len(roast.findings)}")
        print()

        if roast.summary:
            print("📋 SUMMARY:")
            print(roast.summary)
            print()

        # Group findings by category
        findings_by_category = {}
        for finding in roast.findings:
            cat = finding.category
            if cat not in findings_by_category:
                findings_by_category[cat] = []
            findings_by_category[cat].append(finding)

        # Display findings
        for category, findings in findings_by_category.items():
            print(f"## {category.upper()} ({len(findings)} findings)")
            print()
            for finding in findings:
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(finding.severity, "⚪")

                print(f"{severity_emoji} **{finding.severity.upper()}**: {finding.description}")
                if finding.evidence:
                    print(f"   Evidence: {', '.join(finding.evidence[:3])}")
                if finding.recommendations:
                    print(f"   Recommendation: {finding.recommendations[0]}")
                print()

        print("=" * 80)
        print(f"Total Severity Score: {roast.total_severity_score:.2f}")
        print("=" * 80)

        return {
            "roast": roast.to_dict(),
            "session_summary": session_summary
        }

    except Exception as e:
        logger.error(f"Error invoking Marvin: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return {"error": str(e), "summary": session_summary}


def main():
    """Main function"""
    result = invoke_marvin_review()

    # Save results
    output_file = project_root / "data" / "marvin_reviews" / f"session_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Review saved to: {output_file}")
    except Exception as e:
        logger.error(f"Error saving review: {e}")


if __name__ == "__main__":


    main()