#!/usr/bin/env python3
"""
Quick Start Production Script
Generates first 3 episodes to get started with production

Tags: #QUICKSTART #PRODUCTION @LUMINA @JARVIS
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from master_production_script import generate_episode_production_package

def main():
    """Generate first 3 episodes to get started"""
    output_dir = script_dir / "anime_production" / "episodes"

    print("="*80)
    print("QUICK START PRODUCTION")
    print("Generating first 3 episodes to get started")
    print("="*80)

    episodes_to_generate = [
        (1, 1),  # Season 1, Episode 1
        (1, 2),  # Season 1, Episode 2
        (1, 3),  # Season 1, Episode 3
    ]

    for season, episode in episodes_to_generate:
        try:
            generate_episode_production_package(season, episode, output_dir)
        except Exception as e:
            print(f"❌ Error S{season:02d}E{episode:02d}: {e}")

    print("\n" + "="*80)
    print("✅ QUICK START COMPLETE!")
    print("="*80)
    print("\n📁 Generated Files:")
    print(f"   Location: {output_dir}")
    print("   - Scripts: scripts/")
    print("   - Storyboards: storyboards/")
    print("   - Manifests: manifests/")
    print("   - Production Notes: production_notes/")
    print("\n🚀 Ready to start video production!")
    print("   Use the manifests with AI video generation tools (Runway, Pika, etc.)")
    print("="*80)

if __name__ == "__main__":


    main()