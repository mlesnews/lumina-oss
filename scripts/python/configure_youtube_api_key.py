#!/usr/bin/env python3
"""
Configure YouTube API Key

Helper script to configure the Google API key for YouTube in LUMINA systems.
"""

import sys
import json
import os
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("configure_youtube_api_key")


script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

project_root = script_dir.parent.parent
data_dir = project_root / "data" / "lumina_youtube_channel"
channel_file = data_dir / "channel.json"


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def configure_api_key(api_key: str):
    try:
        """Configure API key in channel.json"""
        data_dir.mkdir(parents=True, exist_ok=True)

        if channel_file.exists():
            with open(channel_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "channel_id": "lumina_youtube_channel",
                "channel_name": "LUMINA",
                "api_credentials": {}
            }

        if 'api_credentials' not in data:
            data['api_credentials'] = {}

        data['api_credentials']['api_key'] = api_key

        with open(channel_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"✅ API key configured in {channel_file}")
        print(f"   Channel: {data.get('channel_name', 'LUMINA')}")

    except Exception as e:
        logger.error(f"Error in configure_api_key: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        configure_api_key(api_key)
    else:
        # Check if API key is in environment
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('YOUTUBE_API_KEY')
        if api_key:
            print(f"✅ Found API key in environment variable")
            configure_api_key(api_key)
        else:
            print("Usage: python configure_youtube_api_key.py <API_KEY>")
            print("Or set GOOGLE_API_KEY or YOUTUBE_API_KEY environment variable")

