#!/usr/bin/env python3
"""
SYPHON YouTube Direct - Extract data from YouTube's internal structures
Uses Edge with actual profile, extracts ytInitialData directly
"""

import asyncio
import json
import logging
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SyphonYouTubeDirect")


async def extract_yt_data(page, data_name: str = "ytInitialData") -> Dict:
    """Extract YouTube's internal data from page"""
    try:
        # Try to get ytInitialData from window object
        data = await page.evaluate(f"window.{data_name}")
        if data:
            return data
    except:
        pass

    # Try to extract from script tags
    try:
        scripts = await page.query_selector_all("script")
        for script in scripts:
            content = await script.inner_text()
            if data_name in content:
                # Find the JSON object
                match = re.search(rf"var {data_name}\s*=\s*(\{{.*?\}});", content, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
    except:
        pass

    return {}


def parse_watch_history(data: Dict) -> List[Dict]:
    """Parse watch history from ytInitialData"""
    videos = []

    try:
        # Navigate through YouTube's data structure
        contents = data.get("contents", {})
        two_column = contents.get("twoColumnBrowseResultsRenderer", {})
        tabs = two_column.get("tabs", [])

        for tab in tabs:
            tab_renderer = tab.get("tabRenderer", {})
            tab_content = tab_renderer.get("content", {})
            section_list = tab_content.get("sectionListRenderer", {})
            sections = section_list.get("contents", [])

            for section in sections:
                item_section = section.get("itemSectionRenderer", {})
                items = item_section.get("contents", [])

                for item in items:
                    # Video renderer
                    video_renderer = item.get("videoRenderer", {})
                    if video_renderer:
                        video = extract_video_info(video_renderer)
                        if video:
                            videos.append(video)

                    # Compact video renderer (alternate format)
                    compact = item.get("compactVideoRenderer", {})
                    if compact:
                        video = extract_video_info(compact)
                        if video:
                            videos.append(video)
    except Exception as e:
        logger.debug(f"Parse error: {e}")

    return videos


def extract_video_info(renderer: Dict) -> Dict:
    """Extract video info from a renderer object"""
    try:
        video_id = renderer.get("videoId", "")

        title_obj = renderer.get("title", {})
        title = ""
        if isinstance(title_obj, dict):
            runs = title_obj.get("runs", [])
            if runs:
                title = runs[0].get("text", "")
            else:
                title = title_obj.get("simpleText", "")

        channel_obj = renderer.get("ownerText", {}) or renderer.get("shortBylineText", {})
        channel = ""
        if isinstance(channel_obj, dict):
            runs = channel_obj.get("runs", [])
            if runs:
                channel = runs[0].get("text", "")

        if video_id and title:
            return {
                "video_id": video_id,
                "title": title,
                "channel": channel or "Unknown",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "syphoned_at": datetime.now().isoformat(),
            }
    except:
        pass
    return None


def parse_subscriptions(data: Dict) -> List[Dict]:
    """Parse subscriptions from ytInitialData"""
    subs = []

    try:
        contents = data.get("contents", {})
        two_column = contents.get("twoColumnBrowseResultsRenderer", {})
        tabs = two_column.get("tabs", [])

        for tab in tabs:
            tab_renderer = tab.get("tabRenderer", {})
            tab_content = tab_renderer.get("content", {})
            section_list = tab_content.get("sectionListRenderer", {})
            sections = section_list.get("contents", [])

            for section in sections:
                item_section = section.get("itemSectionRenderer", {})
                items = item_section.get("contents", [])

                for item in items:
                    # Grid renderer for subscriptions
                    grid = item.get("gridRenderer", {})
                    grid_items = grid.get("items", [])

                    for grid_item in grid_items:
                        channel_renderer = grid_item.get("gridChannelRenderer", {})
                        if channel_renderer:
                            channel_id = channel_renderer.get("channelId", "")
                            title_obj = channel_renderer.get("title", {})
                            title = (
                                title_obj.get("simpleText", "")
                                if isinstance(title_obj, dict)
                                else ""
                            )

                            if title:
                                subs.append(
                                    {
                                        "channel_id": channel_id,
                                        "name": title,
                                        "syphoned_at": datetime.now().isoformat(),
                                    }
                                )

                    # Channel renderer (alternate)
                    channel_renderer = item.get("channelRenderer", {})
                    if channel_renderer:
                        channel_id = channel_renderer.get("channelId", "")
                        title_obj = channel_renderer.get("title", {})
                        title = ""
                        if isinstance(title_obj, dict):
                            runs = title_obj.get("runs", [])
                            if runs:
                                title = runs[0].get("text", "")

                        if title:
                            subs.append(
                                {
                                    "channel_id": channel_id,
                                    "name": title,
                                    "syphoned_at": datetime.now().isoformat(),
                                }
                            )
    except Exception as e:
        logger.debug(f"Subscription parse error: {e}")

    return subs


def parse_recommendations(data: Dict) -> List[Dict]:
    """Parse home page recommendations from ytInitialData"""
    videos = []

    try:
        contents = data.get("contents", {})
        two_column = contents.get("twoColumnBrowseResultsRenderer", {})
        tabs = two_column.get("tabs", [])

        for tab in tabs:
            tab_renderer = tab.get("tabRenderer", {})
            tab_content = tab_renderer.get("content", {})

            # Rich grid for home page
            rich_grid = tab_content.get("richGridRenderer", {})
            grid_contents = rich_grid.get("contents", [])

            for grid_item in grid_contents:
                rich_item = grid_item.get("richItemRenderer", {})
                content = rich_item.get("content", {})
                video_renderer = content.get("videoRenderer", {})

                if video_renderer:
                    video = extract_video_info(video_renderer)
                    if video:
                        videos.append(video)
    except Exception as e:
        logger.debug(f"Recommendations parse error: {e}")

    return videos


async def syphon_youtube_direct(days: int = 30, max_videos: int = 300):
    """Main syphon function"""
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("🎯 SYPHON: YOUR YOUTUBE FEED (DIRECT DATA EXTRACTION)")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent.parent.parent

    # Output directory
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

    edge_profile = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Edge" / "User Data"

    videos = []
    subscriptions = []
    recommendations = []

    async with async_playwright() as p:
        logger.info("🚀 Launching Edge with your profile...")
        logger.info(f"   Profile: {edge_profile}")

        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(edge_profile),
                channel="msedge",
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                viewport={"width": 1400, "height": 900},
                timeout=60000,
            )

            page = context.pages[0] if context.pages else await context.new_page()

            # === WATCH HISTORY ===
            logger.info("📺 Getting your watch history...")
            await page.goto(
                "https://www.youtube.com/feed/history", wait_until="domcontentloaded", timeout=30000
            )
            await page.wait_for_timeout(5000)

            # Take screenshot for debugging
            screenshot_path = output_dir / "debug_history.png"
            await page.screenshot(path=str(screenshot_path))
            logger.info(f"   Screenshot saved: {screenshot_path}")

            # Extract data
            yt_data = await extract_yt_data(page)
            if yt_data:
                videos = parse_watch_history(yt_data)
                logger.info(f"   ✅ Found {len(videos)} videos in ytInitialData")

            # If no videos from internal data, try scrolling and scraping
            if len(videos) < 10:
                logger.info("   Trying DOM scraping...")

                # Scroll to load more
                for i in range(10):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)

                    # Try to extract from visible elements
                    page_videos = await page.evaluate("""
                        () => {
                            const videos = [];
                            // Try multiple selectors
                            const selectors = [
                                'ytd-video-renderer',
                                'ytd-compact-video-renderer',
                                'ytd-playlist-video-renderer'
                            ];

                            for (const sel of selectors) {
                                document.querySelectorAll(sel).forEach(el => {
                                    const titleEl = el.querySelector('#video-title, a#video-title');
                                    const channelEl = el.querySelector('#channel-name a, ytd-channel-name a, .ytd-channel-name a');
                                    const linkEl = el.querySelector('a#video-title, a#thumbnail, a[href*="watch"]');

                                    if (titleEl && linkEl) {
                                        const href = linkEl.href || '';
                                        let videoId = '';
                                        if (href.includes('v=')) {
                                            videoId = href.split('v=')[1].split('&')[0];
                                        }

                                        if (videoId) {
                                            videos.push({
                                                video_id: videoId,
                                                title: titleEl.textContent?.trim() || titleEl.title || '',
                                                channel: channelEl?.textContent?.trim() || 'Unknown'
                                            });
                                        }
                                    }
                                });
                            }

                            return videos;
                        }
                    """)

                    for v in page_videos:
                        if v["video_id"] and not any(
                            existing["video_id"] == v["video_id"] for existing in videos
                        ):
                            v["url"] = f"https://www.youtube.com/watch?v={v['video_id']}"
                            v["syphoned_at"] = datetime.now().isoformat()
                            videos.append(v)

                    if len(videos) >= max_videos:
                        break

                    logger.info(f"   Scroll {i + 1}: {len(videos)} videos total")

            logger.info(f"✅ Watch history: {len(videos)} videos")

            # === SUBSCRIPTIONS ===
            logger.info("📋 Getting your subscriptions...")
            await page.goto(
                "https://www.youtube.com/feed/channels",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await page.wait_for_timeout(5000)

            # Screenshot
            await page.screenshot(path=str(output_dir / "debug_subscriptions.png"))

            yt_data = await extract_yt_data(page)
            if yt_data:
                subscriptions = parse_subscriptions(yt_data)
                logger.info(f"   ✅ Found {len(subscriptions)} subscriptions in ytInitialData")

            # DOM fallback
            if len(subscriptions) < 5:
                logger.info("   Trying DOM scraping...")
                for _ in range(5):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1000)

                page_subs = await page.evaluate("""
                    () => {
                        const subs = [];
                        document.querySelectorAll('ytd-channel-renderer, ytd-grid-channel-renderer').forEach(el => {
                            const nameEl = el.querySelector('#channel-title, #text, #main-link');
                            const linkEl = el.querySelector('a#main-link, a#avatar-link, a[href*="/@"]');

                            const name = nameEl?.textContent?.trim() || nameEl?.title || '';
                            const href = linkEl?.href || '';

                            if (name) {
                                subs.push({ name, url: href });
                            }
                        });
                        return subs;
                    }
                """)

                for s in page_subs:
                    if s["name"] and not any(
                        existing["name"] == s["name"] for existing in subscriptions
                    ):
                        s["syphoned_at"] = datetime.now().isoformat()
                        subscriptions.append(s)

            logger.info(f"✅ Subscriptions: {len(subscriptions)} channels")

            # === RECOMMENDATIONS (Home page) ===
            logger.info("🎯 Getting your recommendations...")
            await page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)

            # Screenshot
            await page.screenshot(path=str(output_dir / "debug_home.png"))

            yt_data = await extract_yt_data(page)
            if yt_data:
                recommendations = parse_recommendations(yt_data)
                logger.info(f"   ✅ Found {len(recommendations)} recommendations in ytInitialData")

            # DOM fallback
            if len(recommendations) < 10:
                logger.info("   Trying DOM scraping...")
                for _ in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)

                page_recs = await page.evaluate("""
                    () => {
                        const videos = [];
                        document.querySelectorAll('ytd-rich-item-renderer, ytd-video-renderer').forEach(el => {
                            const titleEl = el.querySelector('#video-title, a#video-title');
                            const channelEl = el.querySelector('#channel-name a, ytd-channel-name a');
                            const linkEl = el.querySelector('a#video-title-link, a#video-title, a#thumbnail');

                            if (titleEl && linkEl) {
                                const href = linkEl.href || '';
                                let videoId = '';
                                if (href.includes('v=')) {
                                    videoId = href.split('v=')[1].split('&')[0];
                                }

                                if (videoId) {
                                    videos.push({
                                        video_id: videoId,
                                        title: titleEl.textContent?.trim() || titleEl.title || '',
                                        channel: channelEl?.textContent?.trim() || 'Unknown'
                                    });
                                }
                            }
                        });
                        return videos;
                    }
                """)

                for v in page_recs:
                    if v["video_id"] and not any(
                        existing["video_id"] == v["video_id"] for existing in recommendations
                    ):
                        v["url"] = f"https://www.youtube.com/watch?v={v['video_id']}"
                        v["syphoned_at"] = datetime.now().isoformat()
                        recommendations.append(v)

            logger.info(f"✅ Recommendations: {len(recommendations)} videos")

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await context.close()

    # === ANALYSIS ===
    logger.info("🔍 Analyzing your data...")

    channels = Counter(v.get("channel", "Unknown") for v in videos)

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
    tech_keywords = ["nvidia", "google", "microsoft", "programming", "developer", "code", "tech"]

    ai_videos = [v for v in videos if any(kw in v.get("title", "").lower() for kw in ai_keywords)]
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
            "period_days": days,
        },
        "top_channels_watched": dict(channels.most_common(20)),
        "subscriptions_list": [s["name"] for s in subscriptions[:50]],
        "ai_content": [{"title": v["title"], "channel": v["channel"]} for v in ai_videos[:20]],
        "tech_content": [{"title": v["title"], "channel": v["channel"]} for v in tech_videos[:20]],
        "recommendations_sample": [
            {"title": v["title"], "channel": v["channel"]} for v in recommendations[:20]
        ],
        "insights": [],
    }

    if channels:
        top = channels.most_common(1)[0]
        analysis["insights"].append(f"Most watched: {top[0]} ({top[1]} videos)")
    if ai_videos:
        pct = len(ai_videos) / len(videos) * 100 if videos else 0
        analysis["insights"].append(f"AI content: {len(ai_videos)} videos ({pct:.1f}%)")
    if subscriptions:
        analysis["insights"].append(f"Subscribed to {len(subscriptions)} channels")

    # === SAVE ===
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(output_dir / f"YOUR_watch_history_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"YOUR_subscriptions_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(subscriptions, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"YOUR_recommendations_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"YOUR_analysis_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info(f"📁 Saved to: {output_dir}")

    # === REPORT ===
    print()
    print("=" * 70)
    print("📺 YOUR YOUTUBE DATA - SYPHON REPORT")
    print("=" * 70)
    print()
    print(f"📊 Watch History: {len(videos)} videos")
    print(f"📋 Subscriptions: {len(subscriptions)} channels")
    print(f"🎯 Recommendations: {len(recommendations)} videos")
    print(f"🤖 AI-Related: {len(ai_videos)} videos")
    print(f"💻 Tech-Related: {len(tech_videos)} videos")
    print()

    if channels:
        print("🏆 YOUR TOP CHANNELS:")
        print("-" * 50)
        for channel, count in list(channels.most_common(10)):
            bar = "█" * min(count, 20)
            print(f"   {count:3d} {bar} {channel[:40]}")
        print()

    if subscriptions:
        print("📋 YOUR SUBSCRIPTIONS:")
        print("-" * 50)
        for s in subscriptions[:15]:
            print(f"   • {s['name']}")
        if len(subscriptions) > 15:
            print(f"   ... and {len(subscriptions) - 15} more")
        print()

    if ai_videos:
        print("🎯 AI CONTENT YOU WATCHED:")
        print("-" * 50)
        for item in ai_videos[:5]:
            print(f"   📹 {item.get('title', 'Unknown')[:55]}...")
            print(f"      Channel: {item.get('channel', 'Unknown')}")
        print()

    if recommendations:
        print("🔮 YOUR RECOMMENDATIONS:")
        print("-" * 50)
        for item in recommendations[:5]:
            print(f"   📹 {item.get('title', 'Unknown')[:55]}...")
            print(f"      Channel: {item.get('channel', 'Unknown')}")
        print()

    print("💡 INSIGHTS:")
    print("-" * 50)
    for insight in analysis.get("insights", []):
        print(f"   • {insight}")
    print()

    return analysis


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--max-videos", type=int, default=300)
    args = parser.parse_args()

    asyncio.run(syphon_youtube_direct(days=args.days, max_videos=args.max_videos))
