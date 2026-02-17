#!/usr/bin/env python3
"""
Direct Video Processing - Bypass Channel Timeouts

Process ULTRON channel videos directly using video URLs instead of
channel extraction to bypass YouTube rate limiting issues.
"""

import sys
from pathlib import Path
import json

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ultron_to_lumina_docuseries_pipeline import ULTRONToLuminaPipeline

# ULTRON Channel Video URLs (manually curated to bypass timeouts)
ULTRON_VIDEOS = {
    "justinjackbear": {
        "name": "Justin Jack Bear",
        "handle": "@justinjackbear",
        "videos": [
            # Add specific video URLs here when available
            # "https://www.youtube.com/watch?v=VIDEO_ID",
        ]
    },
    "natebjones": {
        "name": "Nate B Jones",
        "handle": "@NateBJones",
        "videos": [
            # Add specific video URLs here when available
        ]
    },
    "davesgarage": {
        "name": "Dave's Garage",
        "handle": "@DavesGarage",
        "videos": [
            # Add specific video URLs here when available
        ]
    }
}


def process_direct_videos():
    """Process videos directly using URLs"""
    pipeline = ULTRONToLuminaPipeline()

    print("🚀 Processing ULTRON videos directly...")
    print("="*60)

    results = {
        "processed_videos": [],
        "holocrons_created": [],
        "chapters_created": [],
        "errors": []
    }

    chapter_number = 1

    for channel_key, channel_data in ULTRON_VIDEOS.items():
        channel_name = channel_data["name"]
        videos = channel_data["videos"]

        if not videos:
            print(f"\n⚠️  No video URLs configured for {channel_name}")
            print(f"   Add video URLs to ULTRON_VIDEOS dictionary")
            continue

        print(f"\n📺 Processing {channel_name}: {len(videos)} video(s)")

        channel_info = {
            "name": channel_name,
            "handle": channel_data["handle"],
            "url": f"https://www.youtube.com/{channel_data['handle']}"
        }

        for video_url in videos:
            print(f"\n   Processing: {video_url}")

            try:
                # Process video to Holocron
                result = pipeline.process_video_to_holocron(video_url, channel_info)

                if result["status"] == "success":
                    results["processed_videos"].append(video_url)
                    holocron_path = result["steps"]["holocron"]["notebook_path"]
                    results["holocrons_created"].append(holocron_path)

                    # Transform to chapter
                    notebook_path = Path(holocron_path)
                    chapter_result = pipeline.transform_holocron_to_chapter(notebook_path, chapter_number)

                    if chapter_result["status"] == "success":
                        results["chapters_created"].append(chapter_result)
                        chapter_number += 1
                        print(f"   ✅ Chapter {chapter_number-1} created")
                    else:
                        results["errors"].append({
                            "video": video_url,
                            "error": "Chapter transformation failed",
                            "details": chapter_result.get("error")
                        })
                else:
                    results["errors"].append({
                        "video": video_url,
                        "error": result.get("error", "Processing failed")
                    })

            except Exception as e:
                print(f"   ❌ Error: {e}")
                results["errors"].append({
                    "video": video_url,
                    "error": str(e)
                })

    # Save results
    results_file = pipeline.videos_dir / f"direct_processing_results_{Path(__file__).stem}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Videos Processed: {len(results['processed_videos'])}")
    print(f"Holocrons Created: {len(results['holocrons_created'])}")
    print(f"Chapters Created: {len(results['chapters_created'])}")
    print(f"Errors: {len(results['errors'])}")
    print("="*60)
    print(f"\n📊 Results saved: {results_file.name}")

    return results


if __name__ == "__main__":
    process_direct_videos()
