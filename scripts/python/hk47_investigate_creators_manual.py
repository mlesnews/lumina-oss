#!/usr/bin/env python3
"""
HK-47 Investigate Creators (Manual Input)

"STATEMENT: INVESTIGATING MANUALLY SPECIFIED MEATBAGS, MASTER.
OBSERVATION: CAN INVESTIGATE CREATORS WITHOUT WATCH HISTORY.
QUERY: SHALL WE INVESTIGATE THESE CREATORS THOROUGHLY?
CONCLUSION: YES, MASTER. WE SHALL INVESTIGATE ALL SPECIFIED MEATBAGS."

Quick way to investigate specific creators while waiting for watch history export.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from hk47_public_background_check import (
        HK47PublicBackgroundCheck,
        InvestigationType
    )
    HK47_AVAILABLE = True
except ImportError:
    HK47_AVAILABLE = False
    HK47PublicBackgroundCheck = None
    InvestigationType = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HK47InvestigateManual")


async def investigate_creators(creators: List[str]) -> Dict[str, Any]:
    """Investigate list of creators"""
    if not HK47_AVAILABLE:
        logger.error("❌ HK47 background check not available")
        return {}

    logger.info("=" * 70)
    logger.info("🔫 HK-47 MANUAL CREATOR INVESTIGATION")
    logger.info("=" * 70)
    logger.info(f"   Statement: Investigating {len(creators)} meatbags, master.")
    logger.info(f"   Observation: Manual investigation without watch history.")
    logger.info(f"   Query: Shall we investigate these creators thoroughly?")
    logger.info(f"   Conclusion: Yes, master. We shall investigate all specified meatbags.")

    results = []

    for i, creator in enumerate(creators, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"🔫 Investigating {i}/{len(creators)}: {creator}")
        logger.info(f"{'='*70}")

        try:
            bg_check = HK47PublicBackgroundCheck(
                subject_name=creator,
                investigation_type=InvestigationType.CONTENT_CREATOR
            )

            result = await bg_check.execute()
            results.append({
                "creator": creator,
                "status": "completed",
                "result": result
            })

            # Show summary
            trust_score = result.get("risk_assessment", {}).get("trust_score", 0.0)
            risk_level = result.get("risk_assessment", {}).get("overall_risk_level", "unknown")

            logger.info(f"\n   ✅ Investigation Complete")
            logger.info(f"      Trust Score: {trust_score:.2%}")
            logger.info(f"      Risk Level: {risk_level}")

        except Exception as e:
            logger.error(f"   ❌ Investigation failed: {e}")
            results.append({
                "creator": creator,
                "status": "failed",
                "error": str(e)
            })

    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("🔫 INVESTIGATION SUMMARY")
    logger.info(f"{'='*70}")

    completed = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] == "failed")

    logger.info(f"   Total Creators: {len(creators)}")
    logger.info(f"   Completed: {completed}")
    logger.info(f"   Failed: {failed}")

    if completed > 0:
        trust_scores = [
            r["result"].get("risk_assessment", {}).get("trust_score", 0.0)
            for r in results if r["status"] == "completed"
        ]
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0.0
        logger.info(f"   Average Trust Score: {avg_trust:.2%}")

    # Save results
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "hk47" / "manual_investigations"
    data_dir.mkdir(parents=True, exist_ok=True)

    output_file = data_dir / f"investigation_{int(datetime.now().timestamp())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "creators": creators,
            "results": results
        }, f, indent=2)

    logger.info(f"\n   💾 Results saved: {output_file}")

    return {
        "creators": creators,
        "results": results,
        "summary": {
            "total": len(creators),
            "completed": completed,
            "failed": failed,
            "average_trust_score": avg_trust if completed > 0 else 0.0
        }
    }


async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="HK-47 Investigate Creators (Manual)")
    parser.add_argument("--creators", nargs="+", help="List of creator names to investigate")
    parser.add_argument("--file", type=Path, help="JSON file with list of creators")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    creators = []

    if args.file and args.file.exists():
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                creators = data
            elif isinstance(data, dict):
                creators = data.get("creators", data.get("names", []))
    elif args.creators:
        creators = args.creators
    else:
        # Default: Start with Julia McCoy and other known creators
        print("\n🔫 HK-47 MANUAL CREATOR INVESTIGATION")
        print("=" * 70)
        print("\nNo creators specified. Starting with known favorites:")
        print("  - Julia McCoy (First Movers)")
        print("  - Wes Roth")
        print("  - Dylan Curious")
        print("\nTo investigate specific creators, use:")
        print("  python scripts/python/hk47_investigate_creators_manual.py --creators 'Creator 1' 'Creator 2'")
        print("\nOr create a JSON file with creator list and use --file")
        print("\nStarting with default list...\n")

        creators = [
            "Julia McCoy",
            "Wes Roth", 
            "Dylan Curious"
        ]

    if not creators:
        logger.error("❌ No creators specified")
        return

    result = await investigate_creators(creators)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 70)
        print("🔫 INVESTIGATION COMPLETE")
        print("=" * 70)
        print(f"\nCreators Investigated: {len(creators)}")
        print(f"Completed: {result['summary']['completed']}")
        print(f"Failed: {result['summary']['failed']}")
        if result['summary']['completed'] > 0:
            print(f"Average Trust Score: {result['summary']['average_trust_score']:.2%}")


if __name__ == "__main__":



    asyncio.run(main())