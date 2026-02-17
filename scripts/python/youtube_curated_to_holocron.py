#!/usr/bin/env python3
"""
YouTube Curated Videos to Holocron
Defines flow for curated AI news videos and Lumina Education videos to Holocron

Flow:
1. YouTube Curated AI News Videos → Holocron
2. Lumina Education Videos → Holocron
3. Lumina YouTube Account → Holocron

Tags: #YOUTUBE #HOLOCRON #CURATED #AI_NEWS #LUMINA_EDUCATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("YouTubeCuratedToHolocron")


class YouTubeCuratedToHolocron:
    """
    YouTube Curated Videos to Holocron Flow

    Handles:
    - Curated AI news videos
    - Lumina Education videos
    - Lumina YouTube account videos
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize YouTube curated to Holocron flow"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.holocron_dir = self.project_root / "data" / "holocron"
        self.youtube_dir = self.project_root / "data" / "lumina_youtube_learning"
        self.curated_dir = self.holocron_dir / "youtube_curated"
        self.curated_dir.mkdir(parents=True, exist_ok=True)

        # Video categories
        self.categories = {
            "ai_news": {
                "name": "Curated AI News Videos",
                "description": "AI news videos curated for intelligence gathering",
                "holocron_path": self.curated_dir / "ai_news"
            },
            "lumina_education": {
                "name": "Lumina Education Videos",
                "description": "Educational videos from Lumina Education",
                "holocron_path": self.curated_dir / "lumina_education"
            },
            "lumina_youtube_account": {
                "name": "Lumina YouTube Account",
                "description": "Videos from Lumina's own YouTube account",
                "holocron_path": self.curated_dir / "lumina_account"
            }
        }

        logger.info("✅ YouTube Curated to Holocron initialized")
        logger.info("   Categories: AI News, Lumina Education, Lumina YouTube Account")

    def process_curated_video(self, video_data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Process a curated video and create Holocron entry

        Args:
            video_data: Video data (from YouTube learning analysis)
            category: Video category (ai_news, lumina_education, lumina_youtube_account)

        Returns:
            Holocron entry
        """
        if category not in self.categories:
            logger.warning(f"⚠️  Unknown category: {category}")
            return {}

        category_info = self.categories[category]
        holocron_path = category_info["holocron_path"]
        holocron_path.mkdir(parents=True, exist_ok=True)

        # Extract video information
        video_id = video_data.get('video_id', 'unknown')
        title = video_data.get('title', 'Unknown Title')
        learnings = video_data.get('learnings_for_lumina', [])
        rating = video_data.get('rating', 0)

        # Create Holocron entry
        holocron_entry = {
            "entry_id": f"HOLOCRON-YT-CURATED-{video_id}",
            "title": title,
            "type": "curated_youtube_video",
            "category": category,
            "category_name": category_info["name"],
            "created": datetime.now().isoformat(),
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "rating": rating,
            "learnings": learnings,
            "source": "youtube_curated",
            "holocron_path": str(holocron_path.relative_to(self.project_root))
        }

        # Save Holocron entry
        entry_file = holocron_path / f"{video_id}.json"
        with open(entry_file, 'w', encoding='utf-8') as f:
            json.dump(holocron_entry, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created Holocron entry: {holocron_entry['entry_id']}")

        return holocron_entry

    def process_all_curated_videos(self) -> Dict[str, Any]:
        """
        Process all curated videos from YouTube learning data

        Returns:
            Processing results
        """
        logger.info("=" * 80)
        logger.info("🔮 Processing YouTube Curated Videos to Holocron")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "categories": {
                "ai_news": {"processed": 0, "entries": []},
                "lumina_education": {"processed": 0, "entries": []},
                "lumina_youtube_account": {"processed": 0, "entries": []}
            },
            "total_processed": 0
        }

        # Load YouTube learning data
        if not self.youtube_dir.exists():
            logger.warning(f"⚠️  YouTube learning directory not found: {self.youtube_dir}")
            return results

        # Process each video JSON file
        for video_file in self.youtube_dir.glob("*.json"):
            try:
                with open(video_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)

                # Determine category based on video data
                category = self._determine_category(video_data)

                if category:
                    holocron_entry = self.process_curated_video(video_data, category)
                    results["categories"][category]["processed"] += 1
                    results["categories"][category]["entries"].append(holocron_entry)
                    results["total_processed"] += 1

            except Exception as e:
                logger.warning(f"⚠️  Error processing {video_file}: {e}")

        # Print summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Videos Processed: {results['total_processed']}")
        logger.info("")
        logger.info("By Category:")
        for category, info in results["categories"].items():
            logger.info(f"   {category}: {info['processed']} videos")
        logger.info("")
        logger.info("=" * 80)

        return results

    def _determine_category(self, video_data: Dict[str, Any]) -> Optional[str]:
        """
        Determine video category based on video data

        Returns:
            Category name or None
        """
        title = video_data.get('title', '').lower()
        description = video_data.get('description', '').lower()
        text = f"{title} {description}"

        # Check for AI news keywords
        ai_news_keywords = ['ai news', 'artificial intelligence news', 'ai update', 'ai breakthrough', 'ai development']
        if any(kw in text for kw in ai_news_keywords):
            return "ai_news"

        # Check for Lumina Education
        lumina_keywords = ['lumina', 'education', 'tutorial', 'course', 'learning']
        if any(kw in text for kw in lumina_keywords):
            return "lumina_education"

        # Check for Lumina YouTube account (could be based on channel ID or other metadata)
        channel_id = video_data.get('channel_id', '')
        if 'lumina' in channel_id.lower():
            return "lumina_youtube_account"

        # Default: AI news if it has learnings
        if video_data.get('learnings_for_lumina'):
            return "ai_news"

        return None


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Curated Videos to Holocron")
    parser.add_argument("--process-all", action="store_true", help="Process all curated videos")

    args = parser.parse_args()

    processor = YouTubeCuratedToHolocron()

    if args.process_all:
        results = processor.process_all_curated_videos()
        logger.info("")
        logger.info("✅ Processing complete")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()