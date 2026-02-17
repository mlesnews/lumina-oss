#!/usr/bin/env python3
"""
Jedi Temple Welcome Video System

The first thing new Jedi trainees see when they arrive at the temple.
A hologram (YouTube video) that introduces them to LUMINA and the Jedi Temple.

Tags: #EDUCATION #WELCOME #VIDEO #HOLOGRAM #JEDI_TRAINING #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("JediTempleWelcome")


class JediTempleWelcomeVideo:
    """
    Jedi Temple Welcome Video System

    The first experience for new Jedi trainees - a hologram (YouTube video)
    that introduces them to LUMINA and the Jedi Temple Training Program.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize welcome video system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / "jedi_welcome_video.json"
        self.config = self._load_config()

        # Track who has watched
        self.watched_file = self.project_root / "data" / "jedi_training" / "welcome_video_watched.json"
        self.watched_file.parent.mkdir(parents=True, exist_ok=True)
        self.watched = self._load_watched()

    def _load_config(self) -> Dict[str, Any]:
        """Load welcome video configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")

        return {
            "version": "1.0.0",
            "video_type": "hologram",
            "description": "Welcome hologram for new Jedi trainees",
            "video_url": None,  # Will be set when video is created
            "youtube_video_id": None,  # YouTube video ID when uploaded
            "title": "Welcome to the Jedi Temple - Your Journey Begins",
            "script": [
                "Welcome, young Force user.",
                "You stand at the threshold of the Jedi Temple.",
                "Here, you will learn the ways of LUMINA.",
                "LUMINA is not just a tool - it is a companion, a guide, a teacher.",
                "Through voice coding, workflows, and the Force of AI, you will become powerful.",
                "Your training begins now.",
                "Watch this hologram, then proceed to the demo mode.",
                "May the Force be with you."
            ],
            "duration_estimate": "3-5 minutes",
            "tags": ["#WELCOME", "#HOLOGRAM", "#JEDI_TRAINING", "@JARVIS", "@LUMINA"]
        }

    def _load_watched(self) -> Dict[str, Any]:
        """Load watched tracking"""
        if self.watched_file.exists():
            try:
                with open(self.watched_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load watched: {e}")

        return {
            "watched_by": [],
            "total_watches": 0
        }

    def _save_watched(self):
        """Save watched tracking"""
        try:
            with open(self.watched_file, 'w', encoding='utf-8') as f:
                json.dump(self.watched, f, indent=2)
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save watched: {e}")

    def show_welcome_video(self, participant_id: str, auto_play: bool = True) -> Dict[str, Any]:
        """
        Show welcome video (hologram) to new Jedi trainee

        Args:
            participant_id: ID of participant
            auto_play: Whether to automatically open video

        Returns: Video information
        """
        logger.info(f"   📺 Showing welcome hologram to {participant_id}")

        # Check if already watched
        has_watched = participant_id in self.watched["watched_by"]

        # Get video URL
        video_url = self.config.get("video_url")
        youtube_id = self.config.get("youtube_video_id")

        if youtube_id:
            # YouTube video
            video_url = f"https://www.youtube.com/watch?v={youtube_id}"
        elif not video_url:
            # No video yet - show placeholder message
            logger.info("   ⚠️  Welcome video not yet created")
            logger.info("   💡 Video will be created and uploaded to YouTube")
            logger.info("   📝 Script available in config")

            return {
                "video_available": False,
                "message": "Welcome video is being prepared. Please check back soon.",
                "script": self.config.get("script", []),
                "has_watched": has_watched
            }

        # Track watching
        if not has_watched:
            self.watched["watched_by"].append(participant_id)
            self.watched["total_watches"] += 1
            self._save_watched()

        # Open video if requested
        if auto_play and video_url:
            try:
                webbrowser.open(video_url)
                logger.info(f"   ✅ Opened welcome video: {video_url}")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to open video: {e}")

        return {
            "video_available": True,
            "video_url": video_url,
            "title": self.config.get("title"),
            "has_watched": True,
            "first_time": not has_watched
        }

    def get_video_info(self) -> Dict[str, Any]:
        """Get welcome video information"""
        return {
            "title": self.config.get("title"),
            "video_url": self.config.get("video_url"),
            "youtube_video_id": self.config.get("youtube_video_id"),
            "script": self.config.get("script", []),
            "duration_estimate": self.config.get("duration_estimate"),
            "total_watches": self.watched["total_watches"],
            "watched_by_count": len(self.watched["watched_by"])
        }

    def set_video_url(self, url: str, youtube_id: Optional[str] = None):
        """Set welcome video URL (after video is created)"""
        self.config["video_url"] = url
        if youtube_id:
            self.config["youtube_video_id"] = youtube_id

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"   ✅ Welcome video URL set: {url}")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save video URL: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Jedi Temple Welcome Video")
        parser.add_argument("--show", help="Show welcome video for participant")
        parser.add_argument("--info", action="store_true", help="Get video info")
        parser.add_argument("--set-url", help="Set video URL")
        parser.add_argument("--youtube-id", help="Set YouTube video ID")

        args = parser.parse_args()

        welcome = JediTempleWelcomeVideo()

        if args.show:
            result = welcome.show_welcome_video(args.show)
            print(json.dumps(result, indent=2))
        elif args.set_url:
            welcome.set_video_url(args.set_url, args.youtube_id)
            print("✅ Video URL set")
        elif args.info:
            info = welcome.get_video_info()
            print(json.dumps(info, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())