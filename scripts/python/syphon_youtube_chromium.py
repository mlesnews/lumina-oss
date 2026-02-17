#!/usr/bin/env python3
"""
SYPHON YouTube via Playwright Chromium
Uses Playwright's bundled Chromium with imported cookies for authenticated access.
"""

import asyncio
import json
import logging
import os
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyphonYouTubeChromium")


async def import_edge_cookies():
    """Import cookies from Edge to Playwright format"""
    edge_cookies_db = (
        Path(os.environ["TEMP"]) / "playwright_edge_profile" / "Default" / "Network" / "Cookies"
    )

    if not edge_cookies_db.exists():
        logger.warning(f"Cookies DB not found: {edge_cookies_db}")
        return []

    cookies = []
    try:
        conn = sqlite3.connect(str(edge_cookies_db))
        cursor = conn.cursor()

        # Query YouTube cookies
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE '%youtube%' OR host_key LIKE '%google%'
        """)

        for row in cursor.fetchall():
            host, name, value, path, expires, secure, httponly, samesite = row

            # Convert Chrome timestamp to Unix timestamp
            if expires > 0:
                expires = (expires - 11644473600000000) / 1000000
            else:
                expires = -1

            cookies.append(
                {
                    "name": name,
                    "value": value,
                    "domain": host,
                    "path": path,
                    "expires": expires,
                    "httpOnly": bool(httponly),
                    "secure": bool(secure),
                    "sameSite": ["Strict", "Lax", "None"][samesite] if samesite < 3 else "None",
                }
            )

        conn.close()
        logger.info(f"Imported {len(cookies)} cookies")
        return cookies
    except Exception as e:
        logger.error(f"Error importing cookies: {e}")
        return []


async def syphon_youtube(days: int = 30, max_videos: int = 300) -> Dict[str, Any]:
    """Syphon YouTube data using Playwright Chromium with imported cookies"""
    from playwright.async_api import async_playwright

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

    # Import cookies from Edge
    cookies = await import_edge_cookies()

    videos = []
    subscriptions = []
    recommendations = []

    async with async_playwright() as p:
        # Launch Chromium (bundled, no external deps)
        logger.info("🚀 Launching Playwright Chromium...")
        browser = await p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # Add cookies
        if cookies:
            logger.info(f"Adding {len(cookies)} cookies...")
            await context.add_cookies(cookies)

        page = await context.new_page()

        try:
            # --- WATCH HISTORY ---
            logger.info("📺 Navigating to YouTube watch history...")
            await page.goto(
                "https://www.youtube.com/feed/history", wait_until="networkidle", timeout=30000
            )
            await page.wait_for_timeout(5000)

            # Check if logged in by looking for video content
            video_content = await page.query_selector_all(
                "ytd-video-renderer, ytd-compact-video-renderer, div#contents ytd-item-section-renderer"
            )

            if not video_content:
                # Check for sign-in prompt
                sign_in = await page.query_selector("a[href*='accounts.google.com']")
                if sign_in:
                    logger.warning("⚠️ Not logged in - cookies may have expired")
                    logger.info("Attempting to continue anyway...")
            else:
                logger.info(f"✅ Found {len(video_content)} content sections")

            # Scroll and extract
            last_count = 0
            scroll_attempts = 0

            while len(videos) < max_videos and scroll_attempts < 30:
                # Get all video elements on page
                elements = await page.query_selector_all(
                    "ytd-video-renderer, ytd-compact-video-renderer"
                )

                for elem in elements:
                    try:
                        title = await elem.eval_on_selector_all(
                            "#video-title, a#video-title",
                            "els => els.map(e => e.textContent || e.title).filter(Boolean)[0]",
                        )
                        href = await elem.eval_on_selector_all(
                            "a#video-title, a#thumbnail, a[href*='watch']",
                            "els => els.map(e => e.href).filter(Boolean)[0]",
                        )
                        channel = await elem.eval_on_selector_all(
                            "#channel-name a, ytd-channel-name a, .ytd-channel-name",
                            "els => els.map(e => e.textContent).filter(Boolean)[0]",
                        )

                        if title and href:
                            video_id = ""
                            if "v=" in href:
                                video_id = href.split("v=")[1].split("&")[0]

                            if video_id and not any(v.get("video_id") == video_id for v in videos):
                                videos.append(
                                    {
                                        "video_id": video_id,
                                        "title": title.strip() if title else "",
                                        "channel": channel.strip() if channel else "Unknown",
                                        "url": f"https://www.youtube.com/watch?v={video_id}",
                                        "syphoned_at": datetime.now().isoformat(),
                                    }
                                )
                    except:
                        continue

                if len(videos) == last_count:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    last_count = len(videos)

                if len(videos) % 50 == 0 and len(videos) > 0:
                    logger.info(f"   Extracted {len(videos)} videos...")

                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(1500)

            logger.info(f"✅ Watch history: {len(videos)} videos")

            # --- SUBSCRIPTIONS ---
            logger.info("📋 Extracting subscriptions...")
            await page.goto(
                "https://www.youtube.com/feed/channels", wait_until="networkidle", timeout=30000
            )
            await page.wait_for_timeout(3000)

            for _ in range(10):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(500)

            channel_elements = await page.query_selector_all(
                "ytd-channel-renderer, ytd-grid-channel-renderer"
            )
            for elem in channel_elements:
                try:
                    name = await elem.eval_on_selector_all(
                        "#channel-title, #text, #main-link",
                        "els => els.map(e => e.textContent || e.title).filter(Boolean)[0]",
                    )
                    href = await elem.eval_on_selector_all(
                        "a#main-link, a#avatar-link, a[href*='/@']",
                        "els => els.map(e => e.href).filter(Boolean)[0]",
                    )

                    if name and not any(s.get("name") == name.strip() for s in subscriptions):
                        subscriptions.append(
                            {
                                "name": name.strip(),
                                "url": href or "",
                                "syphoned_at": datetime.now().isoformat(),
                            }
                        )
                except:
                    continue

            logger.info(f"✅ Subscriptions: {len(subscriptions)} channels")

            # --- RECOMMENDATIONS ---
            logger.info("🎯 Extracting recommendations...")
            await page.goto("https://www.youtube.com", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            for _ in range(5):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(1000)

            rec_elements = await page.query_selector_all(
                "ytd-rich-item-renderer, ytd-video-renderer"
            )
            for elem in rec_elements[:100]:
                try:
                    title = await elem.eval_on_selector_all(
                        "#video-title, a#video-title",
                        "els => els.map(e => e.textContent || e.title).filter(Boolean)[0]",
                    )
                    href = await elem.eval_on_selector_all(
                        "a#video-title-link, a#video-title, a#thumbnail",
                        "els => els.map(e => e.href).filter(Boolean)[0]",
                    )
                    channel = await elem.eval_on_selector_all(
                        "#channel-name a, ytd-channel-name a",
                        "els => els.map(e => e.textContent).filter(Boolean)[0]",
                    )

                    if title and href:
                        video_id = ""
                        if "v=" in href:
                            video_id = href.split("v=")[1].split("&")[0]

                        if video_id and not any(
                            r.get("video_id") == video_id for r in recommendations
                        ):
                            recommendations.append(
                                {
                                    "video_id": video_id,
                                    "title": title.strip() if title else "",
                                    "channel": channel.strip() if channel else "Unknown",
                                    "url": f"https://www.youtube.com/watch?v={video_id}",
                                    "syphoned_at": datetime.now().isoformat(),
                                }
                            )
                except:
                    continue

            logger.info(f"✅ Recommendations: {len(recommendations)} videos")

        except Exception as e:
            logger.error(f"❌ Error: {e}")
        finally:
            await browser.close()

    # --- ANALYSIS ---
    logger.info("🔍 Analyzing data...")

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
        "ai_content": [{"title": v["title"], "channel": v["channel"]} for v in ai_videos[:20]],
        "tech_content": [{"title": v["title"], "channel": v["channel"]} for v in tech_videos[:20]],
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

    # --- SAVE ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(output_dir / f"watch_history_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"subscriptions_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(subscriptions, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"recommendations_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)

    with open(output_dir / f"analysis_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info(f"📁 Saved to: {output_dir}")

    # --- REPORT ---
    print()
    print("=" * 70)
    print(f"📺 YOUTUBE SYPHON REPORT - PAST {days} DAYS")
    print("=" * 70)
    print()
    print(f"📊 Watch History: {len(videos)} videos")
    print(f"📋 Subscriptions: {len(subscriptions)} channels")
    print(f"🎯 Recommendations: {len(recommendations)} videos")
    print(f"🤖 AI-Related: {len(ai_videos)} videos")
    print(f"💻 Tech-Related: {len(tech_videos)} videos")
    print()

    if channels:
        print("🏆 TOP CHANNELS:")
        print("-" * 50)
        for channel, count in list(channels.most_common(10)):
            bar = "█" * min(count, 20)
            print(f"   {count:3d} {bar} {channel[:40]}")
        print()

    if analysis.get("insights"):
        print("💡 INSIGHTS:")
        print("-" * 50)
        for insight in analysis["insights"]:
            print(f"   • {insight}")
        print()

    if ai_videos:
        print("🎯 AI CONTENT HIGHLIGHTS:")
        print("-" * 50)
        for item in analysis.get("ai_content", [])[:5]:
            print(f"   📹 {item.get('title', 'Unknown')[:55]}...")
            print(f"      Channel: {item.get('channel', 'Unknown')}")
        print()

    return analysis


async def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--max-videos", type=int, default=300)
    args = parser.parse_args()

    print("=" * 70)
    print(f"🎯 SYPHON: YOUTUBE (CHROMIUM) - PAST {args.days} DAYS")
    print("=" * 70)
    print()

    await syphon_youtube(days=args.days, max_videos=args.max_videos)


if __name__ == "__main__":
    asyncio.run(main())
