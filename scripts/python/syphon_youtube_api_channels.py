#!/usr/bin/env python3
"""
SYPHON YouTube via API
Gets recent content from AI/tech channels and trending topics.
Uses YouTube Data API v3 with our API key.
"""

import json
import logging
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import requests

# Add script directory to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyphonYouTubeAPI")


# Key AI/Tech channels to monitor
CHANNELS_OF_INTEREST = [
    {"name": "Wes Roth", "id": "UCnSvjCLTXvCX4v7cNZvhS4Q"},
    {"name": "Fireship", "id": "UCsBjURrPoezykLs9EqgamOA"},
    {"name": "Two Minute Papers", "id": "UCbfYPyITQ-7l4upoX8nvctg"},
    {"name": "Matthew Berman", "id": "UCRI7hLzMfX1BLmGj5S-zR1w"},
    {"name": "AI Explained", "id": "UCNJ1Ymd5yFuUPtn21xtRbbw"},
    {"name": "David Shapiro", "id": "UCPw2cfzG5sTkS5lXZ2RXm8g"},
    {"name": "NetworkChuck", "id": "UC9x0AN7BWHpCDHSm9NiJFJQ"},
    {"name": "ThePrimeagen", "id": "UC8ENHE5xdFSwx71u3fDH5Xw"},
    {"name": "Lex Fridman", "id": "UCSHZKyawb77ixDdsGog4iWA"},
    {"name": "Andrej Karpathy", "id": "UCXUPKJO5MZQN11PqgIvyuvQ"},
    {"name": "3Blue1Brown", "id": "UCYO_jab_esuFRV4b17AJtAw"},
    {"name": "Computerphile", "id": "UC9-y-6csu5WGm29I7JiwpnA"},
    {"name": "Yannic Kilcher", "id": "UCZHmQk67mSJgfCCTn7xBfew"},
    {"name": "sentdex", "id": "UCfzlCWGWYyIQ0aLC5w48gBQ"},
    {"name": "Tech With Tim", "id": "UC4JX40jDee_tINbkjycV4Sg"},
]

# Topics to search for
TOPICS_OF_INTEREST = [
    "GPT-5 news 2026",
    "Claude AI update 2026",
    "local LLM Ollama",
    "AI agents autonomous",
    "Cursor AI coding",
    "BitNet 1-bit LLM",
    "OpenAI news January 2026",
    "Anthropic Claude news",
    "NVIDIA AI 2026",
    "AI homelab self-hosted",
]


def get_api_key() -> str:
    """Get YouTube API key from Azure Key Vault"""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        vault_url = "https://jarvis-lumina.vault.azure.net/"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)

        secret = client.get_secret("youtube-api-key")
        return secret.value
    except Exception as e:
        logger.error(f"Could not get API key: {e}")
        return None


def youtube_api_request(endpoint: str, params: Dict, api_key: str) -> Dict:
    """Make a YouTube API request"""
    base_url = "https://www.googleapis.com/youtube/v3"
    params["key"] = api_key

    try:
        response = requests.get(f"{base_url}/{endpoint}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API error: {e}")
        return {}


def get_channel_videos(
    channel_id: str, api_key: str, max_results: int = 10, days_back: int = 30
) -> List[Dict]:
    """Get recent videos from a channel"""
    # First get the uploads playlist
    params = {"part": "contentDetails", "id": channel_id}
    channel_data = youtube_api_request("channels", params, api_key)

    if not channel_data.get("items"):
        return []

    uploads_playlist = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Get videos from uploads playlist
    params = {"part": "snippet", "playlistId": uploads_playlist, "maxResults": max_results}
    playlist_data = youtube_api_request("playlistItems", params, api_key)

    videos = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    for item in playlist_data.get("items", []):
        snippet = item.get("snippet", {})
        published = snippet.get("publishedAt", "")

        try:
            pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if pub_date.replace(tzinfo=None) < cutoff_date:
                continue
        except:
            pass

        videos.append(
            {
                "video_id": snippet.get("resourceId", {}).get("videoId", ""),
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published": published,
                "description": snippet.get("description", "")[:200],
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            }
        )

    return videos


def search_videos(
    query: str, api_key: str, max_results: int = 10, days_back: int = 30
) -> List[Dict]:
    """Search for videos by query"""
    published_after = (datetime.now() - timedelta(days=days_back)).isoformat() + "Z"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "relevance",
        "publishedAfter": published_after,
        "maxResults": max_results,
    }

    search_data = youtube_api_request("search", params, api_key)

    videos = []
    for item in search_data.get("items", []):
        snippet = item.get("snippet", {})
        videos.append(
            {
                "video_id": item.get("id", {}).get("videoId", ""),
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published": snippet.get("publishedAt", ""),
                "description": snippet.get("description", "")[:200],
            }
        )

    return videos


def syphon_youtube_api(days: int = 30, max_per_channel: int = 10) -> Dict[str, Any]:
    """Main syphon function using YouTube API"""
    logger.info("=" * 70)
    logger.info("🎯 SYPHON: YOUTUBE API - CHANNEL & TOPIC INTELLIGENCE")
    logger.info("=" * 70)

    api_key = get_api_key()
    if not api_key:
        logger.error("❌ No API key available")
        return {"error": "No API key"}

    logger.info("✅ API key loaded")

    project_root = Path(__file__).parent.parent.parent

    # Load storage policy
    policy_file = project_root / "config" / "storage_policy.json"
    if policy_file.exists():
        with open(policy_file, encoding="utf-8") as f:
            storage_policy = json.load(f)
        if storage_policy.get("zero_local_storage_enforced"):
            output_dir = Path(storage_policy["nas_paths"]["youtube_history"])
        else:
            output_dir = project_root / "data" / "syphon" / "youtube_history"
    else:
        output_dir = project_root / "data" / "syphon" / "youtube_history"

    output_dir.mkdir(parents=True, exist_ok=True)

    all_videos = []
    channel_videos = {}
    topic_videos = {}

    # Syphon from channels of interest
    logger.info(f"\n📺 Syphoning from {len(CHANNELS_OF_INTEREST)} channels...")
    for channel in CHANNELS_OF_INTEREST:
        try:
            videos = get_channel_videos(channel["id"], api_key, max_per_channel, days)
            if videos:
                channel_videos[channel["name"]] = videos
                all_videos.extend(videos)
                logger.info(f"   ✅ {channel['name']}: {len(videos)} videos")
            else:
                logger.info(f"   ⚪ {channel['name']}: no recent videos")
        except Exception as e:
            logger.warning(f"   ❌ {channel['name']}: {e}")

    # Search for topics
    logger.info(f"\n🔍 Searching {len(TOPICS_OF_INTEREST)} topics...")
    for topic in TOPICS_OF_INTEREST:
        try:
            videos = search_videos(topic, api_key, 5, days)
            if videos:
                topic_videos[topic] = videos
                # Only add unique videos
                for v in videos:
                    if not any(av["video_id"] == v["video_id"] for av in all_videos):
                        all_videos.append(v)
                logger.info(f"   ✅ '{topic}': {len(videos)} videos")
        except Exception as e:
            logger.warning(f"   ❌ '{topic}': {e}")

    # Analyze
    logger.info("\n🔍 Analyzing collected videos...")

    channels = Counter(v.get("channel", "Unknown") for v in all_videos)

    ai_keywords = [
        "ai",
        "artificial intelligence",
        "gpt",
        "claude",
        "llm",
        "machine learning",
        "openai",
        "anthropic",
        "cursor",
        "coding",
        "neural",
        "chatgpt",
        "agent",
    ]

    ai_videos = [
        v for v in all_videos if any(kw in v.get("title", "").lower() for kw in ai_keywords)
    ]

    analysis = {
        "summary": {
            "total_videos_collected": len(all_videos),
            "channels_monitored": len(CHANNELS_OF_INTEREST),
            "topics_searched": len(TOPICS_OF_INTEREST),
            "ai_related_videos": len(ai_videos),
            "analysis_date": datetime.now().isoformat(),
            "period_days": days,
        },
        "top_channels": dict(channels.most_common(20)),
        "channel_breakdown": {name: len(vids) for name, vids in channel_videos.items()},
        "topic_breakdown": {topic: len(vids) for topic, vids in topic_videos.items()},
        "ai_content_highlights": [
            {"title": v["title"], "channel": v["channel"], "video_id": v["video_id"]}
            for v in ai_videos[:30]
        ],
        "insights": [],
    }

    # Generate insights
    if channels:
        top = channels.most_common(3)
        analysis["insights"].append(f"Most active: {', '.join([f'{c[0]} ({c[1]})' for c in top])}")

    if ai_videos:
        analysis["insights"].append(
            f"AI-focused content: {len(ai_videos)} / {len(all_videos)} videos ({len(ai_videos) / len(all_videos) * 100:.1f}%)"
        )

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(output_dir / f"api_channel_videos_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(
            {"channels": channel_videos, "all_videos": all_videos}, f, indent=2, ensure_ascii=False
        )

    with open(output_dir / f"api_topic_search_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(topic_videos, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"api_analysis_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info(f"📁 Saved to: {output_dir}")

    # Report
    print()
    print("=" * 70)
    print(f"📺 YOUTUBE API SYPHON REPORT - PAST {days} DAYS")
    print("=" * 70)
    print()
    print(f"📊 Total Videos: {len(all_videos)}")
    print(f"📺 Channels Monitored: {len(CHANNELS_OF_INTEREST)}")
    print(f"🔍 Topics Searched: {len(TOPICS_OF_INTEREST)}")
    print(f"🤖 AI-Related: {len(ai_videos)}")
    print()

    print("🏆 CHANNEL ACTIVITY (Past 30 Days):")
    print("-" * 50)
    for name, count in sorted(
        analysis["channel_breakdown"].items(), key=lambda x: x[1], reverse=True
    )[:10]:
        bar = "█" * min(count, 10)
        print(f"   {count:2d} {bar} {name}")
    print()

    print("🔥 TOP AI CONTENT:")
    print("-" * 50)
    for item in analysis["ai_content_highlights"][:10]:
        print(f"   📹 {item['title'][:55]}...")
        print(f"      Channel: {item['channel']}")
    print()

    print("💡 INSIGHTS:")
    print("-" * 50)
    for insight in analysis["insights"]:
        print(f"   • {insight}")
    print()

    return analysis


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--max-per-channel", type=int, default=10)
    args = parser.parse_args()

    syphon_youtube_api(days=args.days, max_per_channel=args.max_per_channel)
