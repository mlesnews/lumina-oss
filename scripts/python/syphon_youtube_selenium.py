#!/usr/bin/env python3
"""
SYPHON YouTube via Selenium
Uses Edge WebDriver with existing profile for authenticated access.
"""

import json
import logging
import os
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyphonYouTubeSelenium")


def syphon_youtube(days: int = 30, max_videos: int = 300) -> Dict[str, Any]:
    """Syphon YouTube data using Selenium with Edge"""
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

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

    # Configure Edge
    options = EdgeOptions()
    options.add_argument(f"--user-data-dir={os.environ['TEMP']}\\playwright_edge_profile")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Start Edge
    logger.info("🚀 Starting Edge WebDriver...")
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    videos = []
    subscriptions = []
    recommendations = []

    try:
        # --- WATCH HISTORY ---
        logger.info("📺 Navigating to YouTube watch history...")
        driver.get("https://www.youtube.com/feed/history")
        time.sleep(5)

        # Check if logged in
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "ytd-video-renderer, ytd-compact-video-renderer, ytd-item-section-renderer",
                    )
                )
            )
            logger.info("✅ Page loaded - extracting videos...")
        except:
            # Check for login button
            if driver.find_elements(By.CSS_SELECTOR, "a[href*='accounts.google.com']"):
                logger.error("❌ Not logged in to YouTube")
                driver.quit()
                return {"error": "Not logged in"}

        # Scroll and collect videos
        last_height = 0
        scroll_attempts = 0

        while len(videos) < max_videos and scroll_attempts < 30:
            # Find all video elements
            elements = driver.find_elements(
                By.CSS_SELECTOR, "ytd-video-renderer, ytd-compact-video-renderer"
            )

            for elem in elements:
                try:
                    # Get video link
                    link_elem = elem.find_elements(
                        By.CSS_SELECTOR, "a#video-title, a#thumbnail, a[href*='watch']"
                    )
                    title_elem = elem.find_elements(By.CSS_SELECTOR, "#video-title, a#video-title")
                    channel_elem = elem.find_elements(
                        By.CSS_SELECTOR, "#channel-name a, ytd-channel-name a, .ytd-channel-name"
                    )

                    if link_elem and title_elem:
                        href = link_elem[0].get_attribute("href") or ""
                        title = (
                            title_elem[0].text.strip()
                            if title_elem[0].text
                            else title_elem[0].get_attribute("title") or ""
                        )
                        channel = channel_elem[0].text.strip() if channel_elem else "Unknown"

                        # Extract video ID
                        video_id = ""
                        if "v=" in href:
                            video_id = href.split("v=")[1].split("&")[0]
                        elif "/watch/" in href:
                            video_id = href.split("/watch/")[1].split("?")[0]

                        if (
                            video_id
                            and title
                            and not any(v.get("video_id") == video_id for v in videos)
                        ):
                            videos.append(
                                {
                                    "video_id": video_id,
                                    "title": title,
                                    "channel": channel,
                                    "url": f"https://www.youtube.com/watch?v={video_id}",
                                    "syphoned_at": datetime.now().isoformat(),
                                }
                            )
                except Exception:
                    continue

            # Scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
            last_height = new_height

            if len(videos) % 50 == 0 and len(videos) > 0:
                logger.info(f"   Extracted {len(videos)} videos...")

        logger.info(f"✅ Watch history: {len(videos)} videos")

        # --- SUBSCRIPTIONS ---
        logger.info("📋 Extracting subscriptions...")
        driver.get("https://www.youtube.com/feed/channels")
        time.sleep(5)

        # Scroll to load all
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        channel_elements = driver.find_elements(
            By.CSS_SELECTOR, "ytd-channel-renderer, ytd-grid-channel-renderer"
        )
        for elem in channel_elements:
            try:
                name_elem = elem.find_elements(By.CSS_SELECTOR, "#channel-title, #text, #main-link")
                link_elem = elem.find_elements(
                    By.CSS_SELECTOR, "a#main-link, a#avatar-link, a[href*='/@']"
                )

                if name_elem:
                    name = name_elem[0].text.strip() or name_elem[0].get_attribute("title") or ""
                    href = link_elem[0].get_attribute("href") if link_elem else ""

                    if name and not any(s.get("name") == name for s in subscriptions):
                        subscriptions.append(
                            {"name": name, "url": href, "syphoned_at": datetime.now().isoformat()}
                        )
            except:
                continue

        logger.info(f"✅ Subscriptions: {len(subscriptions)} channels")

        # --- RECOMMENDATIONS ---
        logger.info("🎯 Extracting recommendations...")
        driver.get("https://www.youtube.com")
        time.sleep(5)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        rec_elements = driver.find_elements(
            By.CSS_SELECTOR, "ytd-rich-item-renderer, ytd-video-renderer"
        )
        for elem in rec_elements[:100]:
            try:
                link_elem = elem.find_elements(
                    By.CSS_SELECTOR, "a#video-title-link, a#video-title, a#thumbnail"
                )
                title_elem = elem.find_elements(By.CSS_SELECTOR, "#video-title, a#video-title")
                channel_elem = elem.find_elements(
                    By.CSS_SELECTOR, "#channel-name a, ytd-channel-name a"
                )

                if link_elem and title_elem:
                    href = link_elem[0].get_attribute("href") or ""
                    title = (
                        title_elem[0].text.strip()
                        if title_elem[0].text
                        else title_elem[0].get_attribute("title") or ""
                    )
                    channel = channel_elem[0].text.strip() if channel_elem else "Unknown"

                    video_id = ""
                    if "v=" in href:
                        video_id = href.split("v=")[1].split("&")[0]

                    if (
                        video_id
                        and title
                        and not any(r.get("video_id") == video_id for r in recommendations)
                    ):
                        recommendations.append(
                            {
                                "video_id": video_id,
                                "title": title,
                                "channel": channel,
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
        driver.quit()

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

    print("🏆 TOP CHANNELS:")
    print("-" * 50)
    for channel, count in list(channels.most_common(10)):
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

    return analysis


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--max-videos", type=int, default=300)
    args = parser.parse_args()

    print("=" * 70)
    print(f"🎯 SYPHON: YOUTUBE (SELENIUM) - PAST {args.days} DAYS")
    print("=" * 70)
    print()

    syphon_youtube(days=args.days, max_videos=args.max_videos)
