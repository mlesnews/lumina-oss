#!/usr/bin/env python3
"""
Import Sources Using IDM-CLI
Uses IDM-CLI as web crawler/scraper for all sources

Adapt, Improvise, Overcome - Use IDM when other tools fail

@IDM @IDM-CLI @SOURCES @WEB-CRAWLER @ADAPT-IMPROVISE-OVERCOME
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

from idm_cli_web_crawler import IDMCLIWebCrawler

def import_all_sources_with_idm():
    """Import all sources using IDM-CLI"""
    print("=" * 80)
    print("🚀 Import All Sources Using IDM-CLI")
    print("=" * 80)
    print("   Adapt, Improvise, Overcome - Using IDM for reliable web crawling")
    print("")

    crawler = IDMCLIWebCrawler()

    if not crawler.idm_available:
        print("⚠️  IDM-CLI not available")
        print("   Install IDM or configure path")
        print("   Falling back to traditional methods...")
        return 1

    # Sources to import
    sources = [
        {
            "name": "EWTN.com",
            "url": "https://www.ewtn.com",
            "type": "website"
        },
        {
            "name": "MagiCenter",
            "url": "https://www.magiscenter.com",
            "type": "website"
        }
    ]

    print(f"\n📋 Sources to Import: {len(sources)}")
    for source in sources:
        print(f"   - {source['name']}: {source['url']}")

    print("\n🚀 Starting IDM-CLI import...")

    results = []
    for source in sources:
        print(f"\n{'='*80}")
        print(f"📥 Importing: {source['name']}")
        print(f"{'='*80}\n")

        result = crawler.crawl_website(
            source['url'],
            max_pages=1000
        )

        results.append({
            "source": source['name'],
            "result": result
        })

        print(f"\n✅ {source['name']}: {result.get('pages_downloaded', 0)} pages queued")

    print("\n" + "=" * 80)
    print("📊 IMPORT SUMMARY")
    print("=" * 80)
    total_pages = sum(r['result'].get('pages_downloaded', 0) for r in results)
    print(f"Total Pages Queued: {total_pages}")
    print("\n💡 Check IDM to monitor download progress")
    print("   Downloads will be processed with SYPHON after completion")

    return 0

if __name__ == "__main__":
    sys.exit(import_all_sources_with_idm())
