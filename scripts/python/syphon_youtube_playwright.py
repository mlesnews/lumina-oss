#!/usr/bin/env python3
"""
SYPHON YouTube via Playwright
Uses existing Edge profile (authenticated session) to extract watch history.
No manual steps required - fully automated.
"""

import asyncio
import json
import logging
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyphonYouTubePlaywright")


class PlaywrightYouTubeSyphon:
    """Syphon YouTube data using Playwright with authenticated Edge profile"""

    def __init__(self, project_root: Path = None, days: int = 30):
        self.days = days
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Load storage policy
        policy_file = self.project_root / "config" / "storage_policy.json"
        storage_policy = {"zero_local_storage_enforced": False}
        if policy_file.exists():
            with open(policy_file, encoding="utf-8") as f:
                storage_policy = json.load(f)

        if storage_policy.get("zero_local_storage_enforced"):
            self.output_dir = Path(storage_policy["nas_paths"]["youtube_history"])
        else:
            self.output_dir = self.project_root / "data" / "syphon" / "youtube_history"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Use actual Edge profile (requires Edge to be closed)
        self.edge_user_data = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Edge" / "User Data"

        self.videos = []

    async def syphon_watch_history(self, max_videos: int = 500) -> List[Dict[str, Any]]:
        """Extract watch history using Playwright with Edge profile"""
        from playwright.async_api import async_playwright

        logger.info(f"🎯 Starting Playwright YouTube syphon (past {self.days} days)")
        logger.info(f"   Using Edge profile: {self.edge_user_data}")

        videos = []

        async with async_playwright() as p:
            # Launch Edge with persistent context (uses existing login)
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.edge_user_data),
                channel="msedge",
                headless=False,  # Need visible browser for auth
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 800},
            )

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # Navigate to watch history
                logger.info("📺 Navigating to YouTube watch history...")
                await page.goto(
                    "https://www.youtube.com/feed/history", wait_until="networkidle", timeout=30000
                )

                # Wait for content to load
                await page.wait_for_timeout(3000)

                # Check if we're logged in
                logged_in = await page.query_selector(
                    "ytd-watch-history-renderer, ytd-item-section-renderer"
                )
                if not logged_in:
                    logger.warning("⚠️ May not be logged in - checking for login button")
                    login_btn = await page.query_selector('a[href*="accounts.google.com"]')
                    if login_btn:
                        logger.error("❌ Not logged into YouTube. Please log in via Edge first.")
                        await context.close()
                        return []

                logger.info("✅ Logged into YouTube - extracting history...")

                # Scroll and collect videos
                last_count = 0
                scroll_attempts = 0
                max_scroll_attempts = 50

                while len(videos) < max_videos and scroll_attempts < max_scroll_attempts:
                    # Extract visible videos
                    video_elements = await page.query_selector_all(
                        "ytd-video-renderer, ytd-compact-video-renderer"
                    )

                    for elem in video_elements:
                        try:
                            # Extract video data
                            title_elem = await elem.query_selector("#video-title, a#video-title")
                            channel_elem = await elem.query_selector(
                                "#channel-name a, .ytd-channel-name a, ytd-channel-name a"
                            )
                            link_elem = await elem.query_selector("a#video-title, a#thumbnail")
                            time_elem = await elem.query_selector(
                                "#metadata-line span, .ytd-video-meta-block span"
                            )

                            if title_elem and link_elem:
                                title = await title_elem.inner_text()
                                href = await link_elem.get_attribute("href")
                                channel = (
                                    await channel_elem.inner_text() if channel_elem else "Unknown"
                                )
                                time_text = await time_elem.inner_text() if time_elem else ""

                                # Extract video ID
                                video_id = ""
                                if href and "v=" in href:
                                    video_id = href.split("v=")[1].split("&")[0]
                                elif href and "/watch/" in href:
                                    video_id = href.split("/watch/")[1].split("?")[0]

                                if video_id and not any(
                                    v.get("video_id") == video_id for v in videos
                                ):
                                    video = {
                                        "video_id": video_id,
                                        "title": title.strip(),
                                        "channel": channel.strip(),
                                        "url": f"https://www.youtube.com/watch?v={video_id}",
                                        "time_text": time_text.strip(),
                                        "syphoned_at": datetime.now().isoformat(),
                                    }
                                    videos.append(video)

                                    if len(videos) % 50 == 0:
                                        logger.info(f"   Extracted {len(videos)} videos...")
                        except Exception:
                            continue

                    # Check if we got new videos
                    if len(videos) == last_count:
                        scroll_attempts += 1
                    else:
                        scroll_attempts = 0
                        last_count = len(videos)

                    # Scroll down
                    await page.evaluate("window.scrollBy(0, 1000)")
                    await page.wait_for_timeout(1000)

                logger.info(f"✅ Extracted {len(videos)} videos from watch history")

            except Exception as e:
                logger.error(f"❌ Error: {e}")
            finally:
                await context.close()

        return videos

    async def syphon_subscriptions(self) -> List[Dict[str, Any]]:
        """Extract subscriptions using Playwright"""
        from playwright.async_api import async_playwright

        logger.info("📋 Extracting subscriptions...")
        subscriptions = []

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.edge_user_data),
                channel="msedge",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 800},
            )

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                await page.goto(
                    "https://www.youtube.com/feed/channels", wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(3000)

                # Scroll to load all subscriptions
                for _ in range(10):
                    await page.evaluate("window.scrollBy(0, 1000)")
                    await page.wait_for_timeout(500)

                # Extract channel data
                channel_elements = await page.query_selector_all(
                    "ytd-channel-renderer, ytd-grid-channel-renderer"
                )

                for elem in channel_elements:
                    try:
                        name_elem = await elem.query_selector("#channel-title, #text")
                        link_elem = await elem.query_selector("a#main-link, a#avatar-link")
                        subs_elem = await elem.query_selector("#subscribers, #video-count")

                        if name_elem:
                            name = await name_elem.inner_text()
                            href = await link_elem.get_attribute("href") if link_elem else ""
                            subs = await subs_elem.inner_text() if subs_elem else ""

                            channel_id = ""
                            if href:
                                if "/channel/" in href:
                                    channel_id = href.split("/channel/")[1].split("/")[0]
                                elif "/@" in href:
                                    channel_id = href.split("/@")[1].split("/")[0]

                            subscriptions.append(
                                {
                                    "channel_id": channel_id,
                                    "name": name.strip(),
                                    "url": f"https://www.youtube.com{href}" if href else "",
                                    "subscribers": subs.strip(),
                                    "syphoned_at": datetime.now().isoformat(),
                                }
                            )
                    except:
                        continue

                logger.info(f"✅ Extracted {len(subscriptions)} subscriptions")

            except Exception as e:
                logger.error(f"❌ Error extracting subscriptions: {e}")
            finally:
                await context.close()

        return subscriptions

    async def syphon_recommendations(self) -> List[Dict[str, Any]]:
        """Extract homepage recommendations"""
        from playwright.async_api import async_playwright

        logger.info("🎯 Extracting recommendations...")
        recommendations = []

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.edge_user_data),
                channel="msedge",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 800},
            )

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                await page.goto("https://www.youtube.com", wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)

                # Scroll to load more recommendations
                for _ in range(5):
                    await page.evaluate("window.scrollBy(0, 1000)")
                    await page.wait_for_timeout(1000)

                # Extract recommended videos
                video_elements = await page.query_selector_all(
                    "ytd-rich-item-renderer, ytd-video-renderer"
                )

                for elem in video_elements[:100]:  # Limit to 100
                    try:
                        title_elem = await elem.query_selector("#video-title, a#video-title")
                        channel_elem = await elem.query_selector(
                            "#channel-name a, ytd-channel-name a"
                        )
                        link_elem = await elem.query_selector("a#video-title-link, a#thumbnail")
                        views_elem = await elem.query_selector("#metadata-line span")

                        if title_elem:
                            title = await title_elem.inner_text()
                            href = await link_elem.get_attribute("href") if link_elem else ""
                            channel = await channel_elem.inner_text() if channel_elem else "Unknown"
                            views = await views_elem.inner_text() if views_elem else ""

                            video_id = ""
                            if href and "v=" in href:
                                video_id = href.split("v=")[1].split("&")[0]

                            if video_id and not any(
                                r.get("video_id") == video_id for r in recommendations
                            ):
                                recommendations.append(
                                    {
                                        "video_id": video_id,
                                        "title": title.strip(),
                                        "channel": channel.strip(),
                                        "views": views.strip(),
                                        "url": f"https://www.youtube.com/watch?v={video_id}",
                                        "syphoned_at": datetime.now().isoformat(),
                                    }
                                )
                    except:
                        continue

                logger.info(f"✅ Extracted {len(recommendations)} recommendations")

            except Exception as e:
                logger.error(f"❌ Error: {e}")
            finally:
                await context.close()

        return recommendations

    def analyze_data(
        self, videos: List[Dict], subscriptions: List[Dict], recommendations: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze all syphoned data"""
        logger.info("🔍 Analyzing syphoned data...")

        # Channel frequency from watch history
        channels = Counter(v.get("channel", "Unknown") for v in videos)

        # AI/Tech keywords
        ai_keywords = [
            "ai",
            "artificial intelligence",
            "gpt",
            "claude",
            "llm",
            "machine learning",
            "openai",
            "anthropic",
            "deepmind",
            "neural",
            "chatgpt",
            "cursor",
            "coding",
        ]
        tech_keywords = [
            "nvidia",
            "google",
            "microsoft",
            "apple",
            "programming",
            "developer",
            "code",
        ]

        ai_videos = [
            v for v in videos if any(kw in v.get("title", "").lower() for kw in ai_keywords)
        ]
        tech_videos = [
            v for v in videos if any(kw in v.get("title", "").lower() for kw in tech_keywords)
        ]

        analysis = {
            "summary": {
                "total_watch_history": len(videos),
                "total_subscriptions": len(subscriptions),
                "total_recommendations": len(recommendations),
                "ai_related_videos": len(ai_videos),
                "tech_related_videos": len(tech_videos),
                "analysis_date": datetime.now().isoformat(),
                "period_days": self.days,
            },
            "top_channels_watched": dict(channels.most_common(20)),
            "ai_content": [{"title": v["title"], "channel": v["channel"]} for v in ai_videos[:20]],
            "tech_content": [
                {"title": v["title"], "channel": v["channel"]} for v in tech_videos[:20]
            ],
            "insights": [],
        }

        # Generate insights
        if channels:
            top = channels.most_common(1)[0]
            analysis["insights"].append(f"Most watched: {top[0]} ({top[1]} videos)")

        if ai_videos:
            pct = len(ai_videos) / len(videos) * 100 if videos else 0
            analysis["insights"].append(f"AI content: {len(ai_videos)} videos ({pct:.1f}%)")

        if subscriptions:
            analysis["insights"].append(f"Subscribed to {len(subscriptions)} channels")

        return analysis

    def save_results(
        self,
        videos: List[Dict],
        subscriptions: List[Dict],
        recommendations: List[Dict],
        analysis: Dict[str, Any],
    ):
        """Save all syphoned data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save watch history
        history_file = self.output_dir / f"watch_history_{timestamp}.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        logger.info(f"📁 Watch history: {history_file}")

        # Save subscriptions
        subs_file = self.output_dir / f"subscriptions_{timestamp}.json"
        with open(subs_file, "w", encoding="utf-8") as f:
            json.dump(subscriptions, f, indent=2, ensure_ascii=False)
        logger.info(f"📁 Subscriptions: {subs_file}")

        # Save recommendations
        recs_file = self.output_dir / f"recommendations_{timestamp}.json"
        with open(recs_file, "w", encoding="utf-8") as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        logger.info(f"📁 Recommendations: {recs_file}")

        # Save analysis
        analysis_file = self.output_dir / f"analysis_{timestamp}.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        logger.info(f"📁 Analysis: {analysis_file}")

        return history_file, subs_file, recs_file, analysis_file

    def print_report(self, analysis: Dict[str, Any]):
        """Print summary report"""
        print()
        print("=" * 70)
        print(f"📺 YOUTUBE SYPHON REPORT - PAST {self.days} DAYS")
        print("=" * 70)
        print()

        summary = analysis.get("summary", {})
        print(f"📊 Watch History: {summary.get('total_watch_history', 0)} videos")
        print(f"📋 Subscriptions: {summary.get('total_subscriptions', 0)} channels")
        print(f"🎯 Recommendations: {summary.get('total_recommendations', 0)} videos")
        print(f"🤖 AI-Related: {summary.get('ai_related_videos', 0)} videos")
        print(f"💻 Tech-Related: {summary.get('tech_related_videos', 0)} videos")
        print()

        print("🏆 TOP CHANNELS:")
        print("-" * 50)
        for channel, count in list(analysis.get("top_channels_watched", {}).items())[:10]:
            bar = "█" * min(count, 20)
            print(f"   {count:3d} {bar} {channel[:40]}")
        print()

        print("💡 INSIGHTS:")
        print("-" * 50)
        for insight in analysis.get("insights", []):
            print(f"   • {insight}")
        print()

        print("🎯 AI CONTENT HIGHLIGHTS:")
        print("-" * 50)
        for item in analysis.get("ai_content", [])[:5]:
            print(f"   📹 {item.get('title', 'Unknown')[:55]}...")
            print(f"      Channel: {item.get('channel', 'Unknown')}")
        print()

    async def run(self, max_videos: int = 500):
        """Run full syphon process"""
        print("=" * 70)
        print(f"🎯 SYPHON: YOUTUBE (PLAYWRIGHT) - PAST {self.days} DAYS")
        print("=" * 70)
        print()

        # Syphon all data
        videos = await self.syphon_watch_history(max_videos)
        subscriptions = await self.syphon_subscriptions()
        recommendations = await self.syphon_recommendations()

        if not videos and not subscriptions and not recommendations:
            print("❌ No data syphoned. Ensure you're logged into YouTube in Edge.")
            return None

        # Analyze
        analysis = self.analyze_data(videos, subscriptions, recommendations)

        # Save
        self.save_results(videos, subscriptions, recommendations, analysis)

        # Report
        self.print_report(analysis)

        return analysis


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="SYPHON YouTube via Playwright")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--max-videos", type=int, default=500, help="Max videos to extract")

    args = parser.parse_args()

    syphon = PlaywrightYouTubeSyphon(days=args.days)
    await syphon.run(max_videos=args.max_videos)


if __name__ == "__main__":
    asyncio.run(main())
