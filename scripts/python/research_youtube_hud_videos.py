#!/usr/bin/env python3
"""
Research JARVIS/Iron Man HUD Videos from YouTube Account

Searches the user's YouTube channel for:
1. JARVIS/Iron Man HUD Android demo videos
2. Behind-the-scenes design videos for the Iron Man HUD

Tags: #RESEARCH #YOUTUBE #HUD #JARVIS #IRONMAN #ANDROID @JARVIS @MARVIN @RR
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ResearchYouTubeHUDVideos")


def get_youtube_service():
    """Get authenticated YouTube Data API service"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

        # Check for credentials
        project_root = Path(__file__).parent.parent.parent
        creds_file = project_root / "config" / "youtube_credentials.json"
        token_file = project_root / "config" / "youtube_token.json"

        if not creds_file.exists():
            logger.warning("⚠️  YouTube credentials not found")
            logger.info(f"   Expected location: {creds_file}")
            logger.info("   Run: python scripts/python/manus_youtube_oauth_setup.py")
            return None

        creds = None
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed credentials
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            else:
                logger.warning("⚠️  YouTube authentication required")
                logger.info("   Run: python scripts/python/manus_youtube_oauth_setup.py")
                return None

        youtube = build('youtube', 'v3', credentials=creds)
        logger.info("✅ YouTube Data API authenticated")
        return youtube

    except ImportError:
        logger.warning("⚠️  Google API libraries not installed")
        logger.info("   Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return None
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return None


def get_my_channel_id(youtube) -> Optional[str]:
    """Get the authenticated user's channel ID"""
    try:
        # Get channel for authenticated user
        response = youtube.channels().list(
            part='id,snippet',
            mine=True
        ).execute()

        if response.get('items'):
            channel_id = response['items'][0]['id']
            channel_title = response['items'][0]['snippet']['title']
            logger.info(f"✅ Found channel: {channel_title} ({channel_id})")
            return channel_id

        logger.warning("⚠️  No channel found for authenticated user")
        return None

    except Exception as e:
        logger.error(f"❌ Error getting channel ID: {e}")
        return None


def search_channel_videos(youtube, channel_id: str, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """Search for videos in a specific channel"""
    try:
        # Search for videos in the channel
        search_response = youtube.search().list(
            q=query,
            channelId=channel_id,
            part='id,snippet',
            type='video',
            maxResults=max_results,
            order='relevance'
        ).execute()

        videos = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']

            # Get detailed video information
            video_response = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            if video_response.get('items'):
                video_item = video_response['items'][0]
                video_snippet = video_item['snippet']
                video_stats = video_item.get('statistics', {})

                videos.append({
                    "video_id": video_id,
                    "title": video_snippet['title'],
                    "description": video_snippet['description'],
                    "published_at": video_snippet['publishedAt'],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": video_snippet['thumbnails'].get('high', {}).get('url', ''),
                    "views": int(video_stats.get('viewCount', 0)),
                    "likes": int(video_stats.get('likeCount', 0)),
                    "comments": int(video_stats.get('commentCount', 0)),
                    "duration": video_item.get('contentDetails', {}).get('duration', ''),
                    "tags": video_snippet.get('tags', [])
                })

        return videos

    except Exception as e:
        logger.error(f"❌ Error searching channel videos: {e}")
        return []


def list_all_channel_videos(youtube, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """List all videos from a channel (alternative method)"""
    try:
        # Get uploads playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        if not channel_response.get('items'):
            return []

        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Get videos from uploads playlist
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            playlist_items_response = youtube.playlistItems().list(
                playlistId=uploads_playlist_id,
                part='snippet,contentDetails',
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            ).execute()

            video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response.get('items', [])]

            if not video_ids:
                break

            # Get detailed video information
            video_response = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()

            for video_item in video_response.get('items', []):
                video_snippet = video_item['snippet']
                video_stats = video_item.get('statistics', {})

                videos.append({
                    "video_id": video_item['id'],
                    "title": video_snippet['title'],
                    "description": video_snippet['description'],
                    "published_at": video_snippet['publishedAt'],
                    "url": f"https://www.youtube.com/watch?v={video_item['id']}",
                    "thumbnail": video_snippet['thumbnails'].get('high', {}).get('url', ''),
                    "views": int(video_stats.get('viewCount', 0)),
                    "likes": int(video_stats.get('likeCount', 0)),
                    "comments": int(video_stats.get('commentCount', 0)),
                    "duration": video_item.get('contentDetails', {}).get('duration', ''),
                    "tags": video_snippet.get('tags', [])
                })

            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    except Exception as e:
        logger.error(f"❌ Error listing channel videos: {e}")
        return []


def filter_hud_videos(videos: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filter videos into categories: HUD demos and behind-the-scenes"""
    hud_keywords = ['hud', 'jarvis', 'iron man', 'ironman', 'android', 'demo', 'interface', 'overlay']
    behind_scenes_keywords = ['behind', 'scene', 'design', 'making', 'how', 'created', 'development', 'process']

    hud_demos = []
    behind_scenes = []
    other = []

    for video in videos:
        title_lower = video['title'].lower()
        description_lower = video.get('description', '').lower()
        tags_lower = ' '.join([tag.lower() for tag in video.get('tags', [])])
        combined_text = f"{title_lower} {description_lower} {tags_lower}"

        # Check for HUD-related keywords
        has_hud_keywords = any(keyword in combined_text for keyword in hud_keywords)
        has_behind_scenes = any(keyword in combined_text for keyword in behind_scenes_keywords)

        if has_hud_keywords and has_behind_scenes:
            behind_scenes.append(video)
        elif has_hud_keywords:
            hud_demos.append(video)
        elif has_behind_scenes:
            behind_scenes.append(video)
        else:
            other.append(video)

    return {
        "hud_demos": hud_demos,
        "behind_scenes": behind_scenes,
        "other": other
    }


def display_results(categorized_videos: Dict[str, List[Dict[str, Any]]]):
    """Display categorized video results"""
    print("\n" + "="*80)
    print("🎬 JARVIS/IRON MAN HUD VIDEO RESEARCH RESULTS")
    print("="*80 + "\n")

    # HUD Demos
    hud_demos = categorized_videos.get("hud_demos", [])
    print(f"📱 HUD DEMO VIDEOS ({len(hud_demos)} found):")
    print("-"*80)
    if hud_demos:
        for i, video in enumerate(hud_demos, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   URL: {video['url']}")
            print(f"   Published: {video['published_at']}")
            print(f"   Views: {video['views']:,} | Likes: {video['likes']:,} | Comments: {video['comments']:,}")
            if video.get('description'):
                desc_preview = video['description'][:200].replace('\n', ' ')
                print(f"   Description: {desc_preview}...")
    else:
        print("   No HUD demo videos found.")

    # Behind-the-Scenes
    behind_scenes = categorized_videos.get("behind_scenes", [])
    print(f"\n\n🎨 BEHIND-THE-SCENES / DESIGN VIDEOS ({len(behind_scenes)} found):")
    print("-"*80)
    if behind_scenes:
        for i, video in enumerate(behind_scenes, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   URL: {video['url']}")
            print(f"   Published: {video['published_at']}")
            print(f"   Views: {video['views']:,} | Likes: {video['likes']:,} | Comments: {video['comments']:,}")
            if video.get('description'):
                desc_preview = video['description'][:200].replace('\n', ' ')
                print(f"   Description: {desc_preview}...")
    else:
        print("   No behind-the-scenes videos found.")

    # Other (for reference)
    other = categorized_videos.get("other", [])
    if other:
        print(f"\n\n📋 OTHER VIDEOS ({len(other)} found - not categorized):")
        print("-"*80)
        for i, video in enumerate(other[:10], 1):  # Show first 10
            print(f"{i}. {video['title']} - {video['url']}")
        if len(other) > 10:
            print(f"   ... and {len(other) - 10} more")

    print("\n" + "="*80)
    print("✅ RESEARCH COMPLETE")
    print("="*80 + "\n")


def save_results(categorized_videos: Dict[str, List[Dict[str, Any]]], output_file: Path):
    try:
        """Save results to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(categorized_videos, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Results saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in save_results: {e}", exc_info=True)
        raise
def main():
    try:
        """Main research function"""
        logger.info("🔍 Starting YouTube HUD video research...")

        # Get YouTube service
        youtube = get_youtube_service()
        if not youtube:
            logger.error("❌ Cannot proceed without YouTube API access")
            return

        # Get channel ID
        channel_id = get_my_channel_id(youtube)
        if not channel_id:
            logger.error("❌ Cannot proceed without channel ID")
            return

        # Strategy 1: Search for specific keywords
        logger.info("🔍 Searching channel for HUD-related videos...")
        search_queries = [
            "jarvis hud",
            "iron man hud",
            "android hud",
            "hud demo",
            "behind the scenes hud",
            "hud design",
            "iron man interface"
        ]

        all_search_videos = []
        for query in search_queries:
            logger.info(f"   Searching: '{query}'")
            videos = search_channel_videos(youtube, channel_id, query, max_results=20)
            all_search_videos.extend(videos)

        # Deduplicate by video_id
        seen_ids = set()
        unique_search_videos = []
        for video in all_search_videos:
            if video['video_id'] not in seen_ids:
                seen_ids.add(video['video_id'])
                unique_search_videos.append(video)

        logger.info(f"✅ Found {len(unique_search_videos)} unique videos via search")

        # Strategy 2: List all recent videos (as backup/complement)
        logger.info("🔍 Listing recent channel videos...")
        all_channel_videos = list_all_channel_videos(youtube, channel_id, max_results=100)
        logger.info(f"✅ Found {len(all_channel_videos)} total channel videos")

        # Combine and deduplicate
        all_videos = unique_search_videos.copy()
        for video in all_channel_videos:
            if video['video_id'] not in seen_ids:
                all_videos.append(video)
                seen_ids.add(video['video_id'])

        logger.info(f"✅ Total unique videos to analyze: {len(all_videos)}")

        # Categorize videos
        categorized_videos = filter_hud_videos(all_videos)

        # Display results
        display_results(categorized_videos)

        # Save results
        project_root = Path(__file__).parent.parent.parent
        output_file = project_root / "docs" / "research" / "youtube_hud_videos.json"
        save_results(categorized_videos, output_file)

        # Also update research document
        research_doc = project_root / "docs" / "research" / "JARVIS_IRON_MAN_HUD_ANDROID_RESEARCH.md"
        if research_doc.exists():
            update_research_doc(research_doc, categorized_videos)

        logger.info("✅ Research complete!")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
def update_research_doc(doc_path: Path, categorized_videos: Dict[str, List[Dict[str, Any]]]):
    """Update the research document with YouTube video findings"""
    try:
        content = doc_path.read_text(encoding='utf-8')

        # Add YouTube video findings section
        youtube_section = "\n## YouTube Channel Videos Found\n\n"

        hud_demos = categorized_videos.get("hud_demos", [])
        if hud_demos:
            youtube_section += "### HUD Demo Videos\n\n"
            for video in hud_demos:
                youtube_section += f"- **{video['title']}**\n"
                youtube_section += f"  - URL: {video['url']}\n"
                youtube_section += f"  - Published: {video['published_at']}\n"
                youtube_section += f"  - Views: {video['views']:,} | Likes: {video['likes']:,}\n\n"

        behind_scenes = categorized_videos.get("behind_scenes", [])
        if behind_scenes:
            youtube_section += "### Behind-the-Scenes / Design Videos\n\n"
            for video in behind_scenes:
                youtube_section += f"- **{video['title']}**\n"
                youtube_section += f"  - URL: {video['url']}\n"
                youtube_section += f"  - Published: {video['published_at']}\n"
                youtube_section += f"  - Views: {video['views']:,} | Likes: {video['likes']:,}\n\n"

        # Append to document
        if "## YouTube Channel Videos Found" not in content:
            content += youtube_section
            doc_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Updated research document: {doc_path}")
        else:
            logger.debug("Research document already contains YouTube section")

    except Exception as e:
        logger.warning(f"⚠️  Could not update research document: {e}")


if __name__ == "__main__":


    main()