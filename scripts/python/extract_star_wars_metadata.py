#!/usr/bin/env python3
"""
Star Wars Archive Metadata Extractor
Uses yt-dlp to extract high-level metadata from key Star Wars channels.
Saves data to Δ-900.7 Jedi Archives.

Tags: #STARWARS #EXTRACTOR #HOLOCRON @JOCOSTA-NU
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("extract_star_wars_metadata")


def extract_channel_metadata(channel_url, channel_name):
    print(f"🎬 Extracting metadata for: {channel_name}...")
    try:
        # Get channel metadata (limited to top 5 videos for speed)
        cmd = [
            "yt-dlp",
            "--print-json",
            "--flat-playlist",
            "--playlist-end", "5",
            channel_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                video_data = json.loads(line)
                videos.append({
                    "title": video_data.get("title"),
                    "url": video_data.get("url"),
                    "view_count": video_data.get("view_count"),
                    "upload_date": video_data.get("upload_date")
                })

        return {
            "channel_name": channel_name,
            "channel_url": channel_url,
            "extracted_at": datetime.now().isoformat(),
            "top_videos": videos
        }
    except Exception as e:
        print(f"❌ Failed to extract {channel_name}: {e}")
        return None

def main():
    try:
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "data" / "holocron" / "archives" / "900_History_and_Docuseries"
        output_dir.mkdir(parents=True, exist_ok=True)

        channels = {
            "Star Wars Theory": "https://www.youtube.com/@StarWarsTheory",
            "The Stupendous Wave": "https://www.youtube.com/@TheStupendousWave",
            "Dash Star": "https://www.youtube.com/@DashStar",
            "Badger": "https://www.youtube.com/@BadgerStarWars"
        }

        archive_data = {"catalog": []}

        for name, url in channels.items():
            metadata = extract_channel_metadata(url, name)
            if metadata:
                archive_data["catalog"].append(metadata)

        # Save to JSON
        output_file = output_dir / "star_wars_community_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Star Wars Metadata Archive created: {output_file.name}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()