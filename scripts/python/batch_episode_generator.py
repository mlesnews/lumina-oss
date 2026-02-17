#!/usr/bin/env python3
"""
Batch Episode Generator
Generates all episodes for a season or entire series

Tags: #BATCHPRODUCTION #ANIMEPRODUCTION @LUMINA @JARVIS
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from anime_video_production_pipeline import AnimeVideoProductionPipeline

def generate_season(season: int, output_dir: Path) -> List[Dict[str, Any]]:
    """Generate all episodes for a season"""
    pipeline = AnimeVideoProductionPipeline()
    results = []

    print(f"\n🎬 Generating Season {season} (12 episodes)...")

    for episode in range(1, 13):
        print(f"   Episode {episode}/12...", end=" ", flush=True)
        try:
            package = pipeline.generate_production_package(season, episode, output_dir)
            results.append({
                "season": season,
                "episode": episode,
                "status": "success",
                "files": package
            })
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "season": season,
                "episode": episode,
                "status": "error",
                "error": str(e)
            })

    return results

def generate_series(output_dir: Path) -> Dict[str, Any]:
    """Generate all 12 seasons (144 episodes)"""
    pipeline = AnimeVideoProductionPipeline()
    all_results = []

    print("="*80)
    print("BATCH EPISODE GENERATOR")
    print("Generating complete 12-season series (144 episodes)")
    print("="*80)

    for season in range(1, 13):
        season_results = generate_season(season, output_dir)
        all_results.extend(season_results)

    # Summary
    successful = sum(1 for r in all_results if r["status"] == "success")
    failed = sum(1 for r in all_results if r["status"] == "error")

    print("\n" + "="*80)
    print("GENERATION COMPLETE")
    print("="*80)
    print(f"Total Episodes: {len(all_results)}")
    print(f"Successful: {successful} ✅")
    print(f"Failed: {failed} ❌")
    print(f"\nOutput Directory: {output_dir}")
    print("="*80)

    return {
        "total_episodes": len(all_results),
        "successful": successful,
        "failed": failed,
        "results": all_results
    }

if __name__ == "__main__":
    output_dir = script_dir / "anime_production" / "episodes"
    generate_series(output_dir)
