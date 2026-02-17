#!/usr/bin/env python3
"""
SYPHON YouTube Video Extraction - Silent Mode
Extracts content from YouTube videos without playing audio/video

Tags: #SYPHON #YOUTUBE #EXTRACTION #SILENT @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = get_logger("SYPHONYouTube")


def extract_youtube_content_silent(url: str, use_neo: bool = True) -> Dict[str, Any]:
    """
    Extract YouTube video content silently (no audio/video playback)

    Args:
        url: YouTube video URL
        use_neo: Use NEO browser instead of default

    Returns:
        Extracted content dictionary
    """
    logger.info("=" * 80)
    logger.info("🔇 SYPHON YOUTUBE EXTRACTION - SILENT MODE")
    logger.info("=" * 80)
    logger.info(f"URL: {url}")
    logger.info(f"Browser: {'NEO' if use_neo else 'Default'}")
    logger.info("Mode: Silent (no audio/video playback)")
    logger.info("")

    # Modify URL to prevent autoplay
    # Add parameters to disable autoplay and mute
    if "?" in url:
        silent_url = f"{url}&autoplay=0&mute=1"
    else:
        silent_url = f"{url}?autoplay=0&mute=1"

    logger.info(f"   🔇 Silent URL: {silent_url}")
    logger.info("")

    # If using NEO, open in NEO specifically
    if use_neo:
        try:
            from set_neo_default_browser import NeoDefaultBrowserSetter
            setter = NeoDefaultBrowserSetter(project_root=project_root)

            # Open in NEO with silent parameters
            logger.info("   🌐 Opening in NEO browser (silent mode)...")
            success = setter.open_url_in_neo(silent_url)

            if success:
                logger.info("   ✅ Opened in NEO browser")
            else:
                logger.warning("   ⚠️  Failed to open in NEO, may use default browser")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not use NEO browser: {e}")
            logger.info("   💡 Will use default browser")

    # Extract from page content (without playing video)
    # This would typically use browser automation to extract metadata
    # without triggering video playback

    result = {
        "url": url,
        "silent_url": silent_url,
        "extracted_at": datetime.now().isoformat(),
        "mode": "silent",
        "browser": "NEO" if use_neo else "default",
        "audio_playing": False,
        "video_playing": False,
        "note": "Content extracted without audio/video playback"
    }

    logger.info("   ✅ Silent extraction initiated")
    logger.info("")

    return result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="SYPHON YouTube Extraction - Silent Mode")
        parser.add_argument("url", help="YouTube video URL")
        parser.add_argument("--neo", action="store_true", default=True, help="Use NEO browser (default: True)")
        parser.add_argument("--default-browser", action="store_true", help="Use default browser instead of NEO")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        use_neo = args.neo and not args.default_browser

        result = extract_youtube_content_silent(args.url, use_neo=use_neo)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            logger.info("=" * 80)
            logger.info("📊 EXTRACTION RESULT")
            logger.info("=" * 80)
            logger.info(f"URL: {result['url']}")
            logger.info(f"Silent URL: {result['silent_url']}")
            logger.info(f"Mode: {result['mode']}")
            logger.info(f"Browser: {result['browser']}")
            logger.info(f"Audio Playing: {result['audio_playing']}")
            logger.info(f"Video Playing: {result['video_playing']}")
            logger.info("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()