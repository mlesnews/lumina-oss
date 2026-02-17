#!/usr/bin/env python3
"""
LUMINA YouTube Video Search

Search for videos JARVIS can learn from, focusing on AI-generated content,
successful content creators, and high-performing videos.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
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

logger = get_logger("LuminaYouTubeVideoSearch")

from lumina_youtube_learning_analysis import LuminaYouTubeLearningAnalysis, YouTubeMetrics, LearningVideo
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class YouTubeVideoSearch:
    """
    Search YouTube for videos JARVIS can learn from

    Searches for:
    - AI-generated content
    - High-performing videos
    - Successful content creators
    - Videos with strong metrics
    """

    def __init__(self):
        self.logger = get_logger("YouTubeVideoSearch")
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        """Get YouTube API key from Azure Key Vault"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            vault = NASAzureVaultIntegration()
            client = vault.get_key_vault_client()
            if client:
                try:
                    secret = client.get_secret("youtube-api-key")
                    self.logger.info("✅ Retrieved YouTube API key from Azure Key Vault")
                    return secret.value
                except Exception:
                    pass
        except Exception as e:
            self.logger.debug(f"Could not retrieve API key: {e}")

        return None

    def search_ai_generated_content(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for AI-generated content videos

        Search terms:
        - "AI generated video"
        - "AI cinematic"
        - "AI animation"
        - "AI film"
        """
        search_queries = [
            "AI generated video",
            "AI cinematic film",
            "AI animation",
            "AI generated content",
            "artificial intelligence video",
            "AI storytelling",
            "AI generated cinematic"
        ]

        all_results = []

        for query in search_queries:
            results = self._search_youtube(query, max_results=10)
            all_results.extend(results)

        # Deduplicate by video ID
        seen = set()
        unique_results = []
        for result in all_results:
            if result.get('video_id') not in seen:
                seen.add(result['video_id'])
                unique_results.append(result)

        self.logger.info(f"  ✅ Found {len(unique_results)} unique AI-generated content videos")

        return unique_results[:max_results]

    def _search_youtube(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search YouTube using API

        Returns list of video results with metadata
        """
        if not self.api_key:
            self.logger.warning("⚠️  No YouTube API key - returning example results")
            # Return example structure
            return [{
                "video_id": f"example_{i}",
                "title": f"Example AI Video {i}",
                "channel": "Example Channel",
                "description": f"Example description for {query}",
                "url": f"https://www.youtube.com/watch?v=example_{i}",
                "published_at": datetime.now().isoformat()
            } for i in range(max_results)]

        try:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

            youtube = build('youtube', 'v3', developerKey=self.api_key)

            # Search request
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=max_results,
                order='viewCount'  # Order by view count (most popular)
            ).execute()

            results = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']

                # Get video statistics
                video_response = youtube.videos().list(
                    part='statistics,snippet,contentDetails',
                    id=video_id
                ).execute()

                stats = video_response.get('items', [{}])[0].get('statistics', {})

                results.append({
                    "video_id": video_id,
                    "title": snippet['title'],
                    "channel": snippet['channelTitle'],
                    "description": snippet['description'],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "published_at": snippet['publishedAt'],
                    "views": int(stats.get('viewCount', 0)),
                    "likes": int(stats.get('likeCount', 0)),
                    "comments": int(stats.get('commentCount', 0))
                })

            return results

        except ImportError:
            self.logger.warning("⚠️  Google API client not installed - install: pip install google-api-python-client")
            return []
        except HttpError as e:
            self.logger.error(f"❌ YouTube API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Search error: {e}")
            return []

    def analyze_search_results(
        self,
        search_results: List[Dict[str, Any]],
        analysis_system: LuminaYouTubeLearningAnalysis
    ) -> List[LearningVideo]:
        """
        Analyze search results and create learning videos with reviews
        """
        analyzed_videos = []

        for result in search_results:
            # Create metrics
            metrics = YouTubeMetrics(
                video_id=result['video_id'],
                views=result.get('views', 0),
                likes=result.get('likes', 0),
                comments=result.get('comments', 0)
            )
            metrics.calculate_engagement_rate()

            # Analyze video
            learning_video = analysis_system.analyze_video(
                video_id=result['video_id'],
                url=result['url'],
                title=result['title'],
                channel=result.get('channel', 'Unknown'),
                description=result.get('description', ''),
                metrics=metrics
            )

            analyzed_videos.append(learning_video)

        return analyzed_videos


def search_and_analyze_videos():
    """Main function to search and analyze videos"""

    print("\n" + "="*80)
    print("🔍 SEARCHING YOUTUBE FOR LEARNING VIDEOS")
    print("="*80 + "\n")

    # Initialize systems
    search_system = YouTubeVideoSearch()
    analysis_system = LuminaYouTubeLearningAnalysis()

    # Search for AI-generated content
    print("🔍 Searching for AI-generated content videos...")
    search_results = search_system.search_ai_generated_content(max_results=50)

    print(f"  ✅ Found {len(search_results)} videos")

    # Analyze results
    print("\n📊 Analyzing videos and creating 5-star reviews...")
    analyzed_videos = search_system.analyze_search_results(search_results, analysis_system)

    # Display top reviews
    print("\n" + "="*80)
    print("⭐ TOP 5-STAR REVIEWS")
    print("="*80 + "\n")

    # Sort by rating
    sorted_videos = sorted(
        analyzed_videos,
        key=lambda v: v.review.rating.value if v.review else 0,
        reverse=True
    )

    for i, video in enumerate(sorted_videos[:10], 1):
        if video.review:
            print(f"\n{i}. {video.title}")
            print(f"   ⭐ {video.review.rating.value}/5 Stars")
            print(f"   Views: {video.metrics.views:,} | Engagement: {video.metrics.engagement_rate:.2f}%")
            print(f"   {video.review.review_title}")

    # Summary statistics
    print("\n" + "="*80)
    stats = analysis_system.get_summary_statistics()
    print("📊 SUMMARY STATISTICS")
    print("="*80)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80 + "\n")

    print("KEY FINDINGS:")
    print("  • Videos analyzed for learning")
    print("  • 5-star reviews created with metrics support")
    print("  • Learnings extracted for LUMINA")
    print("  • Validation points documented")
    print("\n")


if __name__ == "__main__":
    search_and_analyze_videos()

