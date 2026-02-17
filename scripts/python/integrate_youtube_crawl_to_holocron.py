#!/usr/bin/env python3
"""
YouTube Crawl to Holocron Integration Script

Integrates the YouTube Deep Crawl system with the Holocron Transformer,
creating a complete pipeline from channel discovery to knowledge power.

This script orchestrates:
1. YouTube channel crawling (if needed)
2. SME identification and mapping
3. Holocron transformation
4. Jedi Archives integration
"""

import sys
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("integrate_youtube_crawl_to_holocron")


# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from youtube_deep_crawl_sme_mapper import YouTubeDeepCrawler
    from youtube_to_holocron_transformer import YouTubeToHolocronTransformer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure both youtube_deep_crawl_sme_mapper.py and youtube_to_holocron_transformer.py are available")
    sys.exit(1)

def main():
    try:
        """Main integration pipeline"""
        print("="*80)
        print("🔮 YOUTUBE CRAWL TO HOLOCRON INTEGRATION PIPELINE")
        print("="*80)
        print()

        import argparse
        parser = argparse.ArgumentParser(description="YouTube Crawl to Holocron Integration")
        parser.add_argument("--crawl", action="store_true", help="Execute crawl cycle before transformation")
        parser.add_argument("--domains", nargs="+", help="Domains to crawl (if --crawl is used)")
        parser.add_argument("--transform-only", action="store_true", help="Only transform existing SME map (skip crawl)")
        parser.add_argument("--report", action="store_true", help="Generate transformation report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        # Step 1: Crawl (if requested)
        if args.crawl and not args.transform_only:
            print("🕷️  STEP 1: YouTube Channel Crawling")
            print("-"*80)

            crawler = YouTubeDeepCrawler(project_root=project_root)

            crawl_results = crawler.execute_crawl_cycle(
                domains=args.domains,
                max_channels_per_domain=20,
                max_videos_per_channel=50
            )

            print(f"✅ Crawl complete: {len(crawl_results['sme_profiles'])} SMEs discovered")
            print()

        # Step 2: Transform to Holocrons
        print("🔮 STEP 2: Holocron Transformation (Inception Mode)")
        print("-"*80)

        transformer = YouTubeToHolocronTransformer(project_root=project_root)

        # Transform all SMEs
        holocrons = transformer.transform_all_smes()

        print(f"✅ Transformation complete: {len(holocrons)} Holocrons created")
        print()

        # Step 3: Generate Report (if requested)
        if args.report and holocrons:
            print("📊 STEP 3: Transformation Report")
            print("-"*80)

            report = transformer.generate_transformation_report(holocrons)

            report_file = project_root / "data" / "youtube_intelligence" / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"📊 Transformation Statistics:")
            print(f"   Total Holocrons: {report['total_holocrons_created']}")
            print(f"   Total Videos: {report['total_knowledge_power']['total_videos']:,}")
            print(f"   Total Views: {report['total_knowledge_power']['total_views']:,}")
            print(f"   Total SME Score: {report['total_knowledge_power']['total_sme_score']}")
            print()
            print(f"📁 Domain Breakdown:")
            for domain, count in sorted(report['domain_breakdown'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {domain.replace('_', ' ').title()}: {count}")
            print()
            print(f"🏆 Tier Breakdown:")
            for tier, count in sorted(report['tier_breakdown'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {tier.title()}: {count}")
            print()
            print(f"✅ Report saved: {report_file.name}")
            print()

        # Final summary
        print("="*80)
        print("✅ INTEGRATION COMPLETE")
        print("="*80)
        print(f"🔮 {len(holocrons)} channels transformed into powerful Holocrons")
        print("   Knowledge power granted. Wisdom unlocked. ⚡📚")
        print("="*80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()