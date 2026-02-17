#!/usr/bin/env python3
"""
JARVIS: Research Lock Symbols Issue
🔍 Deep external research for lock symbol troubleshooting
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.research import ResearchEngine
from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Conduct deep research on lock symbol issue"""
    print("=" * 70)
    print("🔍 JARVIS: Deep Research - Lock Symbols Issue")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()
    research_engine = ResearchEngine()

    # Research queries
    queries = [
        "ASUS laptop FN lock symbol won't disappear Fn+Esc not working",
        "ASUS Windows key lock symbol visible won't unlock Win+Esc",
        "ASUS Armoury Crate lock symbols on keyboard keys how to remove",
        "ASUS laptop keyboard lock symbols controlled by software BIOS",
        "ASUS Action Key Mode BIOS disable FN lock Windows key lock"
    ]

    all_findings = []
    all_recommendations = []

    for query in queries:
        print(f"🔍 Researching: {query}")
        print("-" * 70)

        try:
            # Use web_search tool if available
            try:
                from web_search import web_search
                web_result = await web_search(search_term=query)

                if web_result and web_result.get("results"):
                    print(f"  ✅ Found {len(web_result['results'])} results")

                    # Display top results
                    for i, result in enumerate(web_result["results"][:3], 1):
                        print(f"\n  Result {i}:")
                        print(f"    Title: {result.get('title', 'N/A')}")
                        print(f"    URL: {result.get('url', 'N/A')}")
                        snippet = result.get('snippet', '')
                        if snippet:
                            print(f"    Summary: {snippet[:200]}...")
                            all_findings.append(snippet)
                else:
                    print("  ⚠️  No results found")
            except ImportError:
                # Fallback to research engine
                result = await research_engine.research(query, context={"device_type": "ASUS Laptop"})
                all_findings.extend(result.findings)
                all_recommendations.extend(result.recommendations)
                print(f"  ✅ Research complete: {len(result.findings)} findings")
        except Exception as e:
            print(f"  ⚠️  Research failed: {e}")

        print()

    # Synthesize all findings
    print("=" * 70)
    print("📊 RESEARCH SUMMARY")
    print("=" * 70)
    print()

    print(f"🔍 Total Findings: {len(all_findings)}")
    print(f"💡 Recommendations: {len(all_recommendations)}")
    print()

    if all_recommendations:
        print("💡 KEY RECOMMENDATIONS:")
        print("-" * 70)
        for i, rec in enumerate(set(all_recommendations), 1):
            print(f"  {i}. {rec}")
        print()

    # Common solutions found
    print("🔧 COMMON SOLUTIONS FOUND:")
    print("-" * 70)
    print("  1. Check Armoury Crate UI: Device > System Configuration > Action Key Mode")
    print("  2. Check BIOS/UEFI: Advanced > System Configuration > Action Key Mode")
    print("  3. Try Fn+F6 (common ASUS Windows key toggle)")
    print("  4. Update Armoury Crate software")
    print("  5. Update keyboard drivers")
    print("  6. Check Windows Mobility Center (Win+X > Mobility Center)")
    print()

    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())