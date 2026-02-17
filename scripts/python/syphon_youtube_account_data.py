#!/usr/bin/env python3
"""
SYPHON YouTube Account Data

RE-SYPHON ALL OF OUR YOUTUBE ACCOUNT SUBSCRIPTIONS, RECOMMENDATIONS, HISTORY.
PAY CAREFUL ATTENTION TO WHAT WE ACTUALLY WATCH, LIKE, AND SUBSCRIBE TO,
SO WE CAN USE THIS AS A BASELINE FOR INCENTIVE-BASED AFFILIATIONS.

Extracts:
- Subscriptions (channels subscribed to)
- Watch History (what we actually watch)
- Liked Videos (what we like)
- Recommendations (what YouTube recommends)
- Watch Patterns (frequency, duration, categories)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
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

logger = get_logger("SyphonYouTubeAccountData")

from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
from syphon.models import DataSourceType, SyphonData
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class YouTubeChannel:
    """YouTube channel information"""
    channel_id: str
    title: str
    description: str
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    custom_url: Optional[str] = None
    published_at: Optional[str] = None
    thumbnail_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class YouTubeVideo:
    """YouTube video information"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: str
    duration: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    category_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    thumbnail_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class YouTubeWatchActivity:
    """YouTube watch activity data"""
    video_id: str
    video_title: str
    channel_id: str
    channel_title: str
    watched_at: str
    watch_duration_seconds: Optional[int] = None
    completion_percentage: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class YouTubeAccountData:
    """Complete YouTube account data"""
    account_id: str
    extracted_at: str
    subscriptions: List[YouTubeChannel]
    watch_history: List[YouTubeWatchActivity]
    liked_videos: List[YouTubeVideo]
    recommendations: List[YouTubeVideo]
    watch_patterns: Dict[str, Any]
    top_categories: List[Dict[str, Any]]
    top_channels: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "extracted_at": self.extracted_at,
            "subscriptions": [sub.to_dict() for sub in self.subscriptions],
            "watch_history": [watch.to_dict() for watch in self.watch_history],
            "liked_videos": [video.to_dict() for video in self.liked_videos],
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "watch_patterns": self.watch_patterns,
            "top_categories": self.top_categories,
            "top_channels": self.top_channels
        }


class YouTubeAccountSyphon:
    """
    SYPHON YouTube Account Data

    Extracts subscriptions, watch history, likes, and recommendations
    for affiliate program baseline analysis
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("YouTubeAccountSyphon")

        # Initialize SYPHON system
        config = SYPHONConfig(
            project_root=self.project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            enable_self_healing=True
        )
        self.syphon = SYPHONSystem(config)

        # Data storage
        self.data_dir = self.project_root / "data" / "youtube_account_syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # YouTube API setup
        self.api_key = self._get_youtube_api_key()

        self.logger.info("📺 YouTube Account SYPHON initialized")
        self.logger.info("   Extracting: Subscriptions, History, Likes, Recommendations")

    def _get_youtube_api_key(self) -> Optional[str]:
        """Get YouTube API key from various sources"""
        import os

        # 1. Try environment variable
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('YOUTUBE_API_KEY')
        if api_key and api_key not in ["SET_API_KEY", "TO_BE_SET", ""]:
            self.logger.info("✅ YouTube API key found in environment")
            return api_key

        # 2. Try YouTube channel config
        try:
            youtube_channel_file = self.project_root / "data" / "lumina_youtube_channel" / "channel.json"
            if youtube_channel_file.exists():
                with open(youtube_channel_file, 'r', encoding='utf-8') as f:
                    channel_data = json.load(f)
                    key_from_config = channel_data.get('api_credentials', {}).get('api_key')
                    if key_from_config and key_from_config not in ["SET_API_KEY", "TO_BE_SET", ""]:
                        self.logger.info("✅ YouTube API key found in channel config")
                        return key_from_config
        except Exception as e:
            self.logger.debug(f"  Could not load API key from channel config: {e}")

        # 3. Try config/secrets directory
        try:
            secrets_file = self.project_root / "config" / "secrets" / "google_api_key.json"
            if secrets_file.exists():
                with open(secrets_file, 'r', encoding='utf-8') as f:
                    secrets_data = json.load(f)
                    key_from_file = secrets_data.get('api_key') or secrets_data.get('GOOGLE_API_KEY')
                    if key_from_file and key_from_file not in ["SET_API_KEY", "TO_BE_SET", ""]:
                        self.logger.info("✅ YouTube API key found in secrets file")
                        return key_from_file
        except Exception as e:
            self.logger.debug(f"  Could not load API key from secrets: {e}")

        # 4. Try Azure Key Vault
        try:
            import importlib.util
            azure_module_path = self.project_root / "scripts" / "python" / "azure_service_bus_integration.py"
            if azure_module_path.exists():
                spec = importlib.util.spec_from_file_location("azure_service_bus_integration", azure_module_path)
                azure_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(azure_module)
                AzureKeyVaultClient = azure_module.AzureKeyVaultClient

                vault_url = "https://jarvis-lumina.vault.azure.net/"

                try:
                    key_vault = AzureKeyVaultClient(vault_url)

                    # List all secrets first to find the actual name
                    try:
                        secrets_list = key_vault.list_secrets()
                        self.logger.debug(f"  Available secrets: {[s.name for s in secrets_list]}")
                    except:
                        pass

                    # Try common secret names
                    for secret_name in ["youtube-api-key", "youtube_api_key", "google-api-key", "google_api_key"]:
                        try:
                            secret = key_vault.get_secret(secret_name)
                            if secret and secret not in ["SET_API_KEY", "TO_BE_SET", ""]:
                                self.logger.info(f"✅ YouTube API key retrieved from Azure Key Vault: {secret_name}")
                                return secret
                        except:
                            continue
                except Exception as e:
                    self.logger.debug(f"  Azure Key Vault error: {e}")
        except Exception as e:
            self.logger.debug(f"  Could not access Azure Key Vault: {e}")

        self.logger.warning("⚠️  No YouTube API key found - OAuth required for account data")
        self.logger.info("   Note: Account data (subscriptions, history, likes) requires OAuth authentication")
        return None

    def _call_youtube_api(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call YouTube Data API v3"""
        if not self.api_key:
            self.logger.error("❌ No YouTube API key available")
            return None

        try:
            import requests

            base_url = "https://www.googleapis.com/youtube/v3"
            params["key"] = self.api_key

            response = requests.get(f"{base_url}/{endpoint}", params=params, timeout=30)
            response.raise_for_status()

            return response.json()
        except ImportError:
            self.logger.error("❌ requests library not installed: pip install requests")
            return None
        except Exception as e:
            self.logger.error(f"❌ YouTube API error: {e}")
            return None

    def extract_subscriptions(self, max_results: int = 50) -> List[YouTubeChannel]:
        """Extract subscribed channels"""
        self.logger.info(f"📋 Extracting subscriptions (max: {max_results})...")

        if not self.api_key:
            self.logger.warning("⚠️  No API key - OAuth required for account data")
            self.logger.info("   Note: Subscriptions require OAuth authentication (mine=true)")
            return []

        subscriptions = []
        next_page_token = None

        try:
            while len(subscriptions) < max_results:
                params = {
                    "part": "snippet,contentDetails,statistics",
                    "mine": "true",
                    "maxResults": min(50, max_results - len(subscriptions))
                }

                if next_page_token:
                    params["pageToken"] = next_page_token

                # Note: This requires OAuth, not just API key
                # For now, we'll document the requirement
                self.logger.warning("⚠️  Subscriptions endpoint requires OAuth authentication")
                self.logger.info("   To extract account data, you need:")
                self.logger.info("   1. OAuth 2.0 credentials from Google Cloud Console")
                self.logger.info("   2. User authorization to access account data")
                self.logger.info("   3. Access token with appropriate scopes")

                # Try API call anyway (will fail without OAuth)
                data = self._call_youtube_api("subscriptions", params)

                if not data or "items" not in data:
                    break

                for item in data["items"]:
                    snippet = item.get("snippet", {})
                    channel_id = snippet.get("resourceId", {}).get("channelId", "")

                    channel = YouTubeChannel(
                        channel_id=channel_id,
                        title=snippet.get("title", ""),
                        description=snippet.get("description", ""),
                        custom_url=snippet.get("customUrl"),
                        published_at=snippet.get("publishedAt"),
                        thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url")
                    )

                    # Get channel statistics
                    stats_params = {
                        "part": "statistics",
                        "id": channel_id
                    }
                    stats_data = self._call_youtube_api("channels", stats_params)
                    if stats_data and "items" in stats_data and stats_data["items"]:
                        stats = stats_data["items"][0].get("statistics", {})
                        channel.subscriber_count = int(stats.get("subscriberCount", 0))
                        channel.video_count = int(stats.get("videoCount", 0))
                        channel.view_count = int(stats.get("viewCount", 0))

                    subscriptions.append(channel)

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

            self.logger.info(f"✅ Extracted {len(subscriptions)} subscriptions")
            return subscriptions

        except Exception as e:
            self.logger.error(f"❌ Error extracting subscriptions: {e}")
            return []

    def extract_watch_history(self, max_results: int = 200) -> List[YouTubeWatchActivity]:
        """Extract watch history"""
        self.logger.info(f"📋 Extracting watch history (max: {max_results})...")

        if not self.api_key:
            self.logger.warning("⚠️  No API key - returning empty list")
            return []

        watch_history = []
        next_page_token = None

        try:
            while len(watch_history) < max_results:
                params = {
                    "part": "snippet,contentDetails",
                    "mine": "true",
                    "maxResults": min(50, max_results - len(watch_history))
                }

                if next_page_token:
                    params["pageToken"] = next_page_token

                data = self._call_youtube_api("activities", params)

                if not data or "items" not in data:
                    break

                for item in data["items"]:
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})

                    # Only process watch activities
                    if "watch" not in content_details:
                        continue

                    video_id = content_details.get("watch", {}).get("videoId", "")
                    if not video_id:
                        continue

                    # Get video details
                    video_params = {
                        "part": "snippet,contentDetails,statistics",
                        "id": video_id
                    }
                    video_data = self._call_youtube_api("videos", video_params)

                    video_title = ""
                    channel_id = ""
                    channel_title = ""

                    if video_data and "items" in video_data and video_data["items"]:
                        video_snippet = video_data["items"][0].get("snippet", {})
                        video_title = video_snippet.get("title", "")
                        channel_id = video_snippet.get("channelId", "")
                        channel_title = video_snippet.get("channelTitle", "")

                    activity = YouTubeWatchActivity(
                        video_id=video_id,
                        video_title=video_title,
                        channel_id=channel_id,
                        channel_title=channel_title,
                        watched_at=snippet.get("publishedAt", datetime.now().isoformat())
                    )

                    watch_history.append(activity)

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

            self.logger.info(f"✅ Extracted {len(watch_history)} watch history items")
            return watch_history

        except Exception as e:
            self.logger.error(f"❌ Error extracting watch history: {e}")
            return []

    def extract_liked_videos(self, max_results: int = 50) -> List[YouTubeVideo]:
        """Extract liked videos"""
        self.logger.info(f"📋 Extracting liked videos (max: {max_results})...")

        if not self.api_key:
            self.logger.warning("⚠️  No API key - returning empty list")
            return []

        liked_videos = []
        next_page_token = None

        try:
            while len(liked_videos) < max_results:
                params = {
                    "part": "snippet,contentDetails",
                    "myRating": "like",
                    "maxResults": min(50, max_results - len(liked_videos))
                }

                if next_page_token:
                    params["pageToken"] = next_page_token

                data = self._call_youtube_api("videos", params)

                if not data or "items" not in data:
                    break

                for item in data["items"]:
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})
                    statistics = item.get("statistics", {})

                    video = YouTubeVideo(
                        video_id=item.get("id", ""),
                        title=snippet.get("title", ""),
                        description=snippet.get("description", ""),
                        channel_id=snippet.get("channelId", ""),
                        channel_title=snippet.get("channelTitle", ""),
                        published_at=snippet.get("publishedAt", ""),
                        duration=content_details.get("duration"),
                        view_count=int(statistics.get("viewCount", 0)),
                        like_count=int(statistics.get("likeCount", 0)),
                        comment_count=int(statistics.get("commentCount", 0)),
                        category_id=snippet.get("categoryId"),
                        tags=snippet.get("tags", []),
                        thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url")
                    )

                    liked_videos.append(video)

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

            self.logger.info(f"✅ Extracted {len(liked_videos)} liked videos")
            return liked_videos

        except Exception as e:
            self.logger.error(f"❌ Error extracting liked videos: {e}")
            return []

    def extract_recommendations(self, max_results: int = 50) -> List[YouTubeVideo]:
        """Extract recommended videos"""
        self.logger.info(f"📋 Extracting recommendations (max: {max_results})...")

        # Note: YouTube API doesn't have a direct "recommendations" endpoint
        # We'll use the "search" endpoint with default parameters to get trending/popular
        # In a real implementation, you'd need OAuth to get personalized recommendations

        if not self.api_key:
            self.logger.warning("⚠️  No API key - returning empty list")
            return []

        recommendations = []

        try:
            params = {
                "part": "snippet",
                "type": "video",
                "order": "relevance",
                "maxResults": min(50, max_results)
            }

            data = self._call_youtube_api("search", params)

            if data and "items" in data:
                video_ids = [item["id"]["videoId"] for item in data["items"] if "videoId" in item.get("id", {})]

                if video_ids:
                    # Get full video details
                    video_params = {
                        "part": "snippet,contentDetails,statistics",
                        "id": ",".join(video_ids)
                    }
                    video_data = self._call_youtube_api("videos", video_params)

                    if video_data and "items" in video_data:
                        for item in video_data["items"]:
                            snippet = item.get("snippet", {})
                            content_details = item.get("contentDetails", {})
                            statistics = item.get("statistics", {})

                            video = YouTubeVideo(
                                video_id=item.get("id", ""),
                                title=snippet.get("title", ""),
                                description=snippet.get("description", ""),
                                channel_id=snippet.get("channelId", ""),
                                channel_title=snippet.get("channelTitle", ""),
                                published_at=snippet.get("publishedAt", ""),
                                duration=content_details.get("duration"),
                                view_count=int(statistics.get("viewCount", 0)),
                                like_count=int(statistics.get("likeCount", 0)),
                                comment_count=int(statistics.get("commentCount", 0)),
                                category_id=snippet.get("categoryId"),
                                tags=snippet.get("tags", []),
                                thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url")
                            )

                            recommendations.append(video)

            self.logger.info(f"✅ Extracted {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            self.logger.error(f"❌ Error extracting recommendations: {e}")
            return []

    def analyze_watch_patterns(self, watch_history: List[YouTubeWatchActivity]) -> Dict[str, Any]:
        """Analyze watch patterns from history"""
        self.logger.info("📊 Analyzing watch patterns...")

        patterns = {
            "total_watches": len(watch_history),
            "unique_channels": len(set(w.activity.channel_id for w in watch_history if hasattr(w, 'activity'))),
            "watch_frequency": {},
            "top_categories": {},
            "watch_times": []
        }

        # Count watches per channel
        channel_counts = {}
        for activity in watch_history:
            channel_id = activity.channel_id
            if channel_id:
                channel_counts[channel_id] = channel_counts.get(channel_id, 0) + 1

        patterns["top_channels_by_watches"] = sorted(
            channel_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Analyze watch times
        from collections import Counter
        watch_times = []
        for activity in watch_history:
            try:
                watched_at = datetime.fromisoformat(activity.watched_at.replace('Z', '+00:00'))
                watch_times.append(watched_at.hour)
            except:
                pass

        if watch_times:
            patterns["peak_watch_hours"] = Counter(watch_times).most_common(5)

        self.logger.info("✅ Watch patterns analyzed")
        return patterns

    def generate_affiliate_baseline(self, account_data: YouTubeAccountData) -> Dict[str, Any]:
        """Generate affiliate program baseline from account data"""
        self.logger.info("💰 Generating affiliate program baseline...")

        baseline = {
            "extracted_at": account_data.extracted_at,
            "subscriptions": {
                "total": len(account_data.subscriptions),
                "channels": [
                    {
                        "channel_id": sub.channel_id,
                        "title": sub.title,
                        "subscriber_count": sub.subscriber_count,
                        "affiliate_potential": "high" if (sub.subscriber_count or 0) > 1000000 else "medium" if (sub.subscriber_count or 0) > 100000 else "low"
                    }
                    for sub in account_data.subscriptions
                ]
            },
            "watch_history": {
                "total": len(account_data.watch_history),
                "top_channels": account_data.watch_patterns.get("top_channels_by_watches", [])[:10]
            },
            "liked_videos": {
                "total": len(account_data.liked_videos),
                "top_channels": self._get_top_channels_from_videos(account_data.liked_videos)
            },
            "affiliate_opportunities": self._identify_affiliate_opportunities(account_data)
        }

        self.logger.info("✅ Affiliate baseline generated")
        return baseline

    def _get_top_channels_from_videos(self, videos: List[YouTubeVideo]) -> List[Dict[str, Any]]:
        """Get top channels from video list"""
        from collections import Counter
        channel_counts = Counter(video.channel_id for video in videos if video.channel_id)
        return [
            {"channel_id": channel_id, "count": count}
            for channel_id, count in channel_counts.most_common(10)
        ]

    def _identify_affiliate_opportunities(self, account_data: YouTubeAccountData) -> List[Dict[str, Any]]:
        """Identify affiliate opportunities based on watch patterns"""
        opportunities = []

        # Channels we subscribe to
        for sub in account_data.subscriptions:
            if (sub.subscriber_count or 0) > 100000:
                opportunities.append({
                    "type": "subscription",
                    "channel_id": sub.channel_id,
                    "channel_title": sub.title,
                    "subscriber_count": sub.subscriber_count,
                    "reason": "Subscribed channel with significant following",
                    "affiliate_potential": "high"
                })

        # Channels we watch frequently
        top_watched = account_data.watch_patterns.get("top_channels_by_watches", [])
        for channel_id, count in top_watched[:10]:
            opportunities.append({
                "type": "frequent_watch",
                "channel_id": channel_id,
                "watch_count": count,
                "reason": f"Watched {count} times",
                "affiliate_potential": "medium"
            })

        # Channels we like
        liked_channels = self._get_top_channels_from_videos(account_data.liked_videos)
        for channel_info in liked_channels[:10]:
            opportunities.append({
                "type": "liked_content",
                "channel_id": channel_info["channel_id"],
                "like_count": channel_info["count"],
                "reason": f"Liked {channel_info['count']} videos",
                "affiliate_potential": "medium"
            })

        return opportunities

    def syphon_all_account_data(self) -> YouTubeAccountData:
        """SYPHON all YouTube account data"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🔄 SYPHONING ALL YOUTUBE ACCOUNT DATA")
        self.logger.info("="*80 + "\n")

        # Extract all data
        subscriptions = self.extract_subscriptions(max_results=200)
        watch_history = self.extract_watch_history(max_results=500)
        liked_videos = self.extract_liked_videos(max_results=200)
        recommendations = self.extract_recommendations(max_results=100)

        # Analyze patterns
        watch_patterns = self.analyze_watch_patterns(watch_history)

        # Get top categories and channels
        top_categories = self._analyze_categories(watch_history, liked_videos)
        top_channels = self._analyze_top_channels(subscriptions, watch_history, liked_videos)

        # Create account data object
        account_data = YouTubeAccountData(
            account_id="primary_account",
            extracted_at=datetime.now().isoformat(),
            subscriptions=subscriptions,
            watch_history=watch_history,
            liked_videos=liked_videos,
            recommendations=recommendations,
            watch_patterns=watch_patterns,
            top_categories=top_categories,
            top_channels=top_channels
        )

        # Generate affiliate baseline
        affiliate_baseline = self.generate_affiliate_baseline(account_data)

        # Save data
        self._save_account_data(account_data, affiliate_baseline)

        # SYPHON through SYPHON system
        self._syphon_to_system(account_data, affiliate_baseline)

        self.logger.info("\n" + "="*80)
        self.logger.info("✅ YOUTUBE ACCOUNT DATA SYPHONED")
        self.logger.info("="*80 + "\n")

        return account_data

    def _analyze_categories(self, watch_history: List[YouTubeWatchActivity], liked_videos: List[YouTubeVideo]) -> List[Dict[str, Any]]:
        """Analyze top categories"""
        # This would require category mapping from video data
        # For now, return placeholder
        return []

    def _analyze_top_channels(self, subscriptions: List[YouTubeChannel], 
                             watch_history: List[YouTubeWatchActivity],
                             liked_videos: List[YouTubeVideo]) -> List[Dict[str, Any]]:
        """Analyze top channels across all data sources"""
        from collections import Counter

        channel_scores = Counter()

        # Subscriptions get highest weight
        for sub in subscriptions:
            channel_scores[sub.channel_id] += 10

        # Watch history gets medium weight
        for activity in watch_history:
            if activity.channel_id:
                channel_scores[activity.channel_id] += 1

        # Liked videos get high weight
        for video in liked_videos:
            if video.channel_id:
                channel_scores[video.channel_id] += 5

        return [
            {"channel_id": channel_id, "score": score}
            for channel_id, score in channel_scores.most_common(20)
        ]

    def _save_account_data(self, account_data: YouTubeAccountData, affiliate_baseline: Dict[str, Any]):
        try:
            """Save account data to files"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save full account data
            account_file = self.data_dir / f"youtube_account_data_{timestamp}.json"
            with open(account_file, 'w', encoding='utf-8') as f:
                json.dump(account_data.to_dict(), f, indent=2, ensure_ascii=False)

            # Save affiliate baseline
            baseline_file = self.data_dir / f"affiliate_baseline_{timestamp}.json"
            with open(baseline_file, 'w', encoding='utf-8') as f:
                json.dump(affiliate_baseline, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Data saved:")
            self.logger.info(f"   Account data: {account_file}")
            self.logger.info(f"   Affiliate baseline: {baseline_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_account_data: {e}", exc_info=True)
            raise
    def _syphon_to_system(self, account_data: YouTubeAccountData, affiliate_baseline: Dict[str, Any]):
        try:
            """SYPHON data through SYPHON system"""
            self.logger.info("🔄 SYPHONing data through SYPHON system...")

            # Create SYPHON data object
            content = json.dumps({
                "account_data": account_data.to_dict(),
                "affiliate_baseline": affiliate_baseline
            }, indent=2)

            metadata = {
                "source": "youtube_account",
                "extracted_at": account_data.extracted_at,
                "subscriptions_count": len(account_data.subscriptions),
                "watch_history_count": len(account_data.watch_history),
                "liked_videos_count": len(account_data.liked_videos),
                "recommendations_count": len(account_data.recommendations)
            }

            # Extract actionable items
            actionable_items = []
            for opp in affiliate_baseline.get("affiliate_opportunities", []):
                actionable_items.append({
                    "type": "affiliate_opportunity",
                    "channel_id": opp.get("channel_id"),
                    "channel_title": opp.get("channel_title", ""),
                    "potential": opp.get("affiliate_potential"),
                    "reason": opp.get("reason")
                })

            # Create SyphonData
            syphon_data = SyphonData(
                data_id=f"youtube_account_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.SOCIAL,
                source_id="youtube_account",
                content=content,
                metadata=metadata,
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=[],
                decisions=[],
                intelligence=[]
            )

            # Save to SYPHON system
            self.syphon.storage.save(syphon_data)

            self.logger.info(f"✅ SYPHONed {len(actionable_items)} affiliate opportunities")


        except Exception as e:
            self.logger.error(f"Error in _syphon_to_system: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution function"""
        print("\n" + "="*80)
        print("🔄 SYPHON YOUTUBE ACCOUNT DATA")
        print("="*80 + "\n")

        project_root = Path(".").resolve()
        syphon = YouTubeAccountSyphon(project_root)

        # SYPHON all account data
        account_data = syphon.syphon_all_account_data()

        # Display summary
        print("\n" + "="*80)
        print("📊 EXTRACTION SUMMARY")
        print("="*80 + "\n")
        print(f"Subscriptions: {len(account_data.subscriptions)}")
        print(f"Watch History: {len(account_data.watch_history)}")
        print(f"Liked Videos: {len(account_data.liked_videos)}")
        print(f"Recommendations: {len(account_data.recommendations)}")
        print(f"Top Channels: {len(account_data.top_channels)}")
        print("\n" + "="*80 + "\n")

        return account_data


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()