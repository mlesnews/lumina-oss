#!/usr/bin/env python3
"""
Work Verification using @MARVIN @PEAK @AGGRESSIVE @ADVSERIAL Protocol
Convenience script for verifying work with Marvin's comprehensive verification system.

Usage:
    python verify_work_with_marvin.py --file path/to/work.txt --type code
    python verify_work_with_marvin.py --content "work content here" --type documentation

Author: JARVIS Automation System
Date: 2025-01-27
"""

import sys
import json
import argparse
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from marvin_verification_system import verify_work_with_marvin
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    MARVIN_AVAILABLE = True
except ImportError as e:
    print(f"❌ @MARVIN verification system not available: {e}")
    MARVIN_AVAILABLE = False


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def main():
    parser = argparse.ArgumentParser(
        description="@MARVIN @PEAK @AGGRESSIVE @ADVSERIAL Work Verification"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to file containing work to verify"
    )
    parser.add_argument(
        "--content",
        type=str,
        help="Direct content to verify (alternative to --file)"
    )
    parser.add_argument(
        "--type",
        type=str,
        default="general",
        choices=["code", "documentation", "configuration", "general"],
        help="Type of work being verified"
    )
    parser.add_argument(
        "--jarvis-integration",
        action="store_true",
        help="Use full JARVIS integration (includes R5 ingestion)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output results to JSON file"
    )

    args = parser.parse_args()

    if not MARVIN_AVAILABLE:
        print("❌ @MARVIN verification system is not available")
        return 1

    # Get work content
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                work_content = f.read()
            print(f"📁 Loaded work from file: {args.file}")
        except Exception as e:
            print(f"❌ Error reading file {args.file}: {e}")
            return 1
    elif args.content:
        work_content = args.content
        print("📝 Using provided content for verification")
    else:
        print("❌ Must provide either --file or --content")
        return 1

    print(f"🔍 Verifying work of type: {args.type}")
    print(f"📏 Content length: {len(work_content)} characters")
    print("=" * 60)

    try:
        if args.jarvis_integration:
            print("🤖 Using full JARVIS integration with @MARVIN verification...")
            jarvis = JARVISHelpdeskIntegration()
            result = jarvis.verify_work_with_marvin(work_content, args.type)
        else:
            print("🤖 Using direct @MARVIN verification...")
            result = verify_work_with_marvin(work_content, args.type)

        # Display results
        print("\n🎭 MARVIN'S VERDICT")
        print("=" * 40)

        verified_status = "✅ VERIFIED" if result.get("verified", False) else "❌ REQUIRES ATTENTION"
        confidence = result.get("confidence_score", 0)

        print(f"Status: {verified_status}")
        print(".3f")
        print(f"Issues Found: {len(result.get('issues_found', []))}")

        if result.get("marvin_response"):
            print(f"\n💭 Marvin Says: {result['marvin_response']}")

        # Show issues
        issues = result.get("issues_found", [])
        if issues:
            print("\n🚨 ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(issue.get("severity"), "⚪")
                print(f"{i}. {severity_emoji} [{issue.get('category', 'unknown')}] {issue.get('issue', 'Unknown issue')}")
                if issue.get("recommendation"):
                    print(f"   💡 {issue['recommendation']}")

        # Show recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"• {rec}")

        # Show philosophical insights
        insights = result.get("philosophical_insights", [])
        if insights:
            print("\n🤔 PHILOSOPHICAL INSIGHTS:")
            for insight in insights:
                print(f"• {insight}")

        # Verification metadata
        metadata = result.get("verification_metadata", {})
        if metadata:
            print("\n📊 VERIFICATION METADATA:")
            print(f"• Protocol: {metadata.get('verification_protocol', 'unknown')}")
            print(f"• Phases Completed: {len(metadata.get('phases_completed', []))}")
            print(f"• Aggressive Checks: {metadata.get('aggressive_checks', 0)}")
            print(f"• Serial Confirmations: {metadata.get('serial_confirmations', 0)}")

        # Save results if requested
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Results saved to: {args.output}")
            except Exception as e:
                print(f"❌ Error saving results: {e}")

        print("\n" + "=" * 60)

        # Return appropriate exit code
        return 0 if result.get("verified", False) else 1

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":


    sys.exit(main())