#!/usr/bin/env python3
"""
Process Star Wars Theory Video and Generate Advice

Processes the specific Star Wars Theory video:
https://www.youtube.com/live/qPUPmz6Zh4g?si=lI47tTGeiIrjra9A
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ProcessSWTVideo")

from lumina_star_wars_theory_advice import LuminaStarWarsTheoryAdvice
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def extract_video_id_from_url(url: str) -> str:
    """Extract video ID from YouTube URL"""
    # Handle various YouTube URL formats
    if 'youtube.com/live/' in url:
        video_id = url.split('youtube.com/live/')[1].split('?')[0]
    elif 'youtube.com/watch?v=' in url:
        video_id = url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
    else:
        video_id = url
    return video_id


def get_video_transcript(video_id: str) -> Optional[str]:
    """
    Get transcript from YouTube video

    Tries multiple methods:
    1. youtube-transcript-api library
    2. YouTube Data API
    3. Manual input
    """
    transcript_text = None

    # Try youtube-transcript-api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        logger.info(f"Attempting to fetch transcript for video: {video_id}")
        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        fetched_transcript = api.fetch(video_id, languages=['en'])
        # Get the transcript snippets (FetchedTranscriptSnippet objects with .text attribute)
        transcript_snippets = fetched_transcript.snippets
        transcript_text = ' '.join([snippet.text for snippet in transcript_snippets])
        logger.info(f"✅ Successfully fetched transcript ({len(transcript_text)} characters)")
        return transcript_text
    except ImportError:
        logger.warning("youtube-transcript-api not installed. Install: pip install youtube-transcript-api")
    except Exception as e:
        logger.warning(f"Could not fetch transcript via youtube-transcript-api: {e}")

    # Try YouTube Data API (would need video description/closed captions)
    # This is a placeholder - would need API setup

    # If no transcript available, return None
    logger.warning("⚠️  No transcript available. Please provide transcript manually or install youtube-transcript-api")
    return None


def process_swt_video(video_url: str, transcript: Optional[str] = None) -> Dict[str, Any]:
    """
    Process Star Wars Theory video and generate advice

    Args:
        video_url: YouTube video URL
        transcript: Optional transcript text (if not provided, will try to fetch)
    """
    logger.info("⭐ Processing Star Wars Theory Video")
    logger.info(f"   URL: {video_url}")

    # Extract video ID
    video_id = extract_video_id_from_url(video_url)
    logger.info(f"   Video ID: {video_id}")

    # Get transcript if not provided
    if transcript is None:
        transcript = get_video_transcript(video_id)

    if transcript is None:
        logger.error("❌ No transcript available. Cannot process video.")
        logger.info("   Please provide transcript manually or install youtube-transcript-api:")
        logger.info("   pip install youtube-transcript-api")
        return {
            "error": "No transcript available",
            "video_url": video_url,
            "video_id": video_id,
            "instructions": "Install youtube-transcript-api or provide transcript manually"
        }

    # Process with advice system
    advisor = LuminaStarWarsTheoryAdvice()
    result = advisor.process_video(transcript, video_url)

    # Display results
    print("\n" + "="*80)
    print("⭐ STAR WARS THEORY VIDEO PROCESSED")
    print("="*80 + "\n")
    print(f"Video URL: {video_url}")
    print(f"Video ID: {video_id}")
    print(f"Questions Found: {result['questions_found']}\n")

    # Display advice for each question
    advisor.display_advice([
        advisor.generate_advice(
            advisor.extract_questions(transcript)[i]
        ) for i in range(min(5, len(advisor.extract_questions(transcript))))
    ])

    return result


def main():
    """Main function"""
    video_url = "https://www.youtube.com/live/qPUPmz6Zh4g?si=lI47tTGeiIrjra9A"

    print("\n" + "="*80)
    print("⭐ PROCESSING STAR WARS THEORY VIDEO")
    print("="*80 + "\n")

    result = process_swt_video(video_url)

    if "error" in result:
        print("\n" + "="*80)
        print("⚠️  TRANSCRIPT REQUIRED")
        print("="*80 + "\n")
        print("To process this video, we need the transcript.")
        print("Options:")
        print("1. Install youtube-transcript-api: pip install youtube-transcript-api")
        print("2. Provide transcript manually via command line argument")
        print("3. Use YouTube's auto-generated captions")
        print("\n" + "="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("✅ VIDEO PROCESSED SUCCESSFULLY")
        print("="*80 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process Star Wars Theory Video")
    parser.add_argument("--url", default="https://www.youtube.com/live/qPUPmz6Zh4g?si=lI47tTGeiIrjra9A",
                       help="YouTube video URL")
    parser.add_argument("--transcript", type=Path, help="Path to transcript file")

    args = parser.parse_args()

    transcript_text = None
    if args.transcript:
        with open(args.transcript, 'r', encoding='utf-8') as f:
            transcript_text = f.read()

    process_swt_video(args.url, transcript_text)

